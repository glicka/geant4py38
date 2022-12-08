import Geant4 as g4
import numpy as np
from geant4py.source.source import Source
from scipy.stats import poisson
import math

class MyPrimaryGeneratorAction(g4.G4VUserPrimaryGeneratorAction):
    "My Primary Generator Action"

    def __init__(self, source=Source()):

        g4.G4VUserPrimaryGeneratorAction.__init__(self)

        # Initialize source term
        self.set_source(source)
        #print(self.source.energy)

        #x=np.linspace(self.source.minE,self.source.maxE,1000)
        self.enrg = np.linspace(self.source.minE,self.source.maxE,1000)
        j1 = 1.006e-6*np.exp(-0.35*(np.log(self.enrg))**2 + 2.1451*np.log(self.enrg))
        j2 = 1.011e-3*np.exp(-0.4106*(np.log(self.enrg))**2 - 0.6670*np.log(self.enrg))
        M = (j1 + j2) #cm^-2 s^-1

        pdf = M/sum(M)
        self.cdfBono = np.cumsum(pdf)
        self.cdfBono /= max(self.cdfBono)

        enfwhm = 0.05
        self.gaussEnrg = np.random.normal(loc=self.source.energy, scale=(enfwhm*self.source.energy)/2.355,size=1000)
        self.cdfGauss = np.cumsum(self.gaussEnrg)
        self.cdfGauss /= max(self.cdfGauss)
        # Get particle
        particle_table = g4.G4ParticleTable.GetParticleTable()
        particle = particle_table.FindParticle(g4.G4String(self.source.particle))

        # Setup beam
        beam = g4.G4ParticleGun()
        beam.SetParticleEnergy(self.source.energy * getattr(g4, self.source.energy_unit))
        beam.SetParticleMomentumDirection(g4.G4ThreeVector(0,0,-1))
        beam.SetParticleDefinition(particle)
        beam.SetParticlePosition(g4.G4ThreeVector(0,0,1*g4.m))

        self.particleGun = beam


    def GeneratePrimaries(self, event):

        # Far field
        if self.source.field == 'far':
            pos, direc = self.farField()
            #print('xdir = ',direc.z)
            _x = direc
            _y = pos
        # Near field
        elif self.source.field == 'near':
            pos, direc = self.nearField()
            _x = g4.G4ThreeVector(direc.x, direc.y, direc.z)
            _y = g4.G4ThreeVector(pos.x, pos.y, pos.z)

        elif self.source.field == 'isotropic':
            pos, direc = self.isotropic()
            _x = direc
            _y = pos
        elif self.source.field == 'isotropicResp':
            pos, direc = self.isotropicResp()
            _x = direc
            _y = pos
        elif self.source.field == 'isotropicPos':
            pos, direc = self.isotropicPos()
            _x = direc
            _y = pos
        elif self.source.field == 'isotropicNeg':
            pos, direc = self.isotropicNeg()
            _x = direc
            _y = pos
        elif self.source.field == 'square':
            pos, direc = self.squareField()
            #_x = direc
            #_y = pos
            _x = g4.G4ThreeVector(direc.x, direc.y, direc.z)
            _y = g4.G4ThreeVector(pos.x, pos.y, pos.z)

        else:
            raise Exception("Unrecognized source type")



        # Calculate energy for particle
        if self.source.energyDist == 'neutronBackground':
            rndm = g4.G4UniformRand()
            energy = np.interp(rndm,self.cdfBono[:],self.enrg)
        elif self.source.energyDist == 'mono':
            energy = self.source.energy
        elif self.source.energyDist == 'gauss':
            rndm = g4.G4UniformRand()
            energy = np.interp(rndm,self.cdfGauss[:],self.gaussEnrg)
        elif self.source.energyDist is None:
            energy = self.source.energy
        self.source.energy = energy

        #print('energy = ', self.source.energy)
        # Get particle
        particle_table = g4.G4ParticleTable.GetParticleTable()
        particle = particle_table.FindParticle(g4.G4String(self.source.particle))

        self.particleGun.SetParticleDefinition(particle)
        self.particleGun.SetParticleEnergy(self.source.energy * getattr(g4, self.source.energy_unit))
        self.particleGun.SetParticleMomentumDirection(_x)
        self.particleGun.SetParticlePosition(_y)
        self.particleGun.GeneratePrimaryVertex(event)

    def squareField(self,):
        # Set the direction of the rays, given theta and phi (calculate position, take all negative values)
        z = self.source.source_dist * getattr(g4, self.source.length_unit)
        theta = self.source.theta * getattr(g4, self.source.angle_unit)
        phi = self.source.phi * getattr(g4, self.source.angle_unit)
        direc = g4.G4ThreeVector(-z * np.cos(phi) * np.sin(theta),
	                             -z * np.sin(phi) * np.sin(theta),
	                             -z * np.cos(theta))
        # Uniformly sample a square defined as rad=[x1,x2,y1,y2] (start at z-axis (0,0,1) and then rotate)
        x1,x2,y1,y2 = self.source.source_rad
        randX = ( (x2-x1) * g4.G4UniformRand() + x1 ) * getattr(g4, self.source.length_unit)
        randY = ( (y2-y1) * g4.G4UniformRand() + y1 ) * getattr(g4, self.source.length_unit)
        source_pos = g4.G4ThreeVector(randX,
                                      randY,
                                      z)
        # Get position by rotating the z-oriented square
        pos = source_pos.rotateY(theta).rotateZ(phi)

        return pos, direc

    def farField(self,):
        # Set the direction of the rays, given theta and phi (calculate position, take all negative values)
        r = self.source.source_dist * getattr(g4, self.source.length_unit)
        theta = self.source.theta * getattr(g4, self.source.angle_unit)
        phi = self.source.phi * getattr(g4, self.source.angle_unit)
        direc = g4.G4ThreeVector(-r * np.cos(phi) * np.sin(theta),
	                             -r * np.sin(phi) * np.sin(theta),
	                             -r * np.cos(theta))

	    # Uniformly sample a disk that just covers the entire detector (start at z-axis (0,0,1) and then rotate)
        rand_r = g4.G4UniformRand()
        rand_theta = 2. * np.pi * g4.G4UniformRand()
        rad = self.source.source_rad * getattr(g4, self.source.length_unit)
        source_pos = g4.G4ThreeVector(rad * np.sqrt(rand_r) * np.cos(rand_theta),
                                    rad * np.sqrt(rand_r) * np.sin(rand_theta),
                                    r)

        # Get position by rotating the z-oriented disk
        pos = source_pos.rotateY(theta).rotateZ(phi)

        return pos, direc

    def nearField(self,):

        r = self.source.source_dist * getattr(g4, self.source.length_unit)
        theta = self.source.theta * getattr(g4, self.source.angle_unit)
        phi = self.source.phi * getattr(g4, self.source.angle_unit)

        # Source position (cone vertex)
        pos = g4.G4ThreeVector(r * np.cos(phi) * np.sin(theta),
                               r * np.sin(phi) * np.sin(theta),
                               r * np.cos(theta))

        # Cone beam with vertex at (0, 0)
        cone_rad = self.source.source_rad*getattr(g4, self.source.length_unit)
        opening_angle = np.arctan(cone_rad/r)
        # open a cone of degree theta centered on positive z-axis
        z = 1 - (1-np.cos(opening_angle)) * g4.G4UniformRand()
        cone_phi = 2. * np.pi * g4.G4UniformRand()
        initial_direction = g4.G4ThreeVector(np.sqrt(1-z*z) * np.cos(cone_phi),
                                             np.sqrt(1-z*z) * np.sin(cone_phi),
                                             -z)

        # Rotate direction to  source location
        direction = initial_direction.rotateY(theta).rotateZ(phi)
        #print('direction = ',direction)

        return pos, direction

    def isotropic(self,):

        r = self.source.source_dist * getattr(g4, self.source.length_unit)
        theta = self.source.theta * getattr(g4, self.source.angle_unit)
        phi = self.source.phi * getattr(g4, self.source.angle_unit)

        pos = g4.G4ThreeVector(r * np.cos(phi) * np.sin(theta),
                               r * np.sin(phi) * np.sin(theta),
                               r * np.cos(theta))

        dir_phi = 2. * np.pi * g4.G4UniformRand()
        dir_theta = np.arccos((2. * g4.G4UniformRand()) - 1.)

        direction = g4.G4ThreeVector(np.cos(dir_phi) * np.sin(dir_theta),
                                     np.sin(dir_phi) * np.sin(dir_theta),
                                     np.cos(dir_theta))

        return pos, direction

    def isotropicPos(self,):

        # Uniformly sample a disk that just covers the entire detector (start at z-axis (0,0,1) and then rotate)
        # Set the direction of the rays, given theta and phi (calculate position, take all negative values)
        r = self.source.source_dist * getattr(g4, self.source.length_unit)
        theta = self.source.theta * getattr(g4, self.source.angle_unit)
        phi = self.source.phi * getattr(g4, self.source.angle_unit)
        rand_r = g4.G4UniformRand()
        rand_theta = 2. * np.pi * g4.G4UniformRand()
        rad = self.source.source_rad * getattr(g4, self.source.length_unit)
        source_pos = g4.G4ThreeVector(rad * np.sqrt(rand_r) * np.cos(rand_theta),
                             rad * np.sqrt(rand_r) * np.sin(rand_theta),
                             r)

        # Get position by rotating the z-oriented disk
        pos = source_pos.rotateY(theta).rotateZ(phi)

        dir_phi = 2. * np.pi * g4.G4UniformRand()
        dir_theta = np.arccos((2. * g4.G4UniformRand()) - 1.)

        initial_direction = g4.G4ThreeVector(np.cos(dir_phi) * np.sin(dir_theta),
                                     np.sin(dir_phi) * np.sin(dir_theta),
                                     -abs(np.cos(dir_theta)))

        # Rotate direction to  source location
        direction = initial_direction.rotateY(theta).rotateZ(phi)
        direction /= np.sqrt(direction.x**2 + direction.y**2 + direction.z**2)

        return pos, direction




    def set_source(self, source):
        self.source = source

        # Set random seed
        if self.source.random_seed is not None:
            g4.HepRandom.setTheSeed(self.source.random_seed)

    def get_source(self):
        return self.source
    '''
    def set_det(self, detectorConstruction):
        self.detectorConstruction = detectorConstruction
    '''
