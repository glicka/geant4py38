from __future__ import print_function
import numpy as np
import healpy as hp

class Source(object):

    def __init__(self, field='far', particle='neutron', energyDist = None, energy=3, minE=0.25, maxE=15,
                       direction=[0,0], direction_type='angle',
                       num_particles=100, source_rad=20, source_dist=100,
                       energy_unit='MeV', angle_unit='deg', length_unit='cm',
                       random_seed=42, outputfile='output', sourcedatafile='srcoutput'):
        self.field = field
        self.particle = particle
        self.energyDist = energyDist
        self.energy = energy
        self.minE = minE
        self.maxE = maxE
        self.num_particles = num_particles
        self.source_rad = source_rad
        self.source_dist = source_dist
        self.energy_unit = energy_unit
        self.length_unit = length_unit
        self.random_seed = random_seed
        self.outputfile = outputfile
        self._setDirection(direction, direction_type, angle_unit)
        self.random_seed = random_seed
        self.outputfile = outputfile
        self.sourcedatafile = sourcedatafile

    def _setDirection(self, direction, direction_type, angle_unit='deg'):

        self.direction_type = direction_type

        if self.direction_type == 'angle':
            if np.array(direction).shape != (2,):
                theta = []
                phi = []
                for i in range(len(direction)):
                    row = direction[i]
                    theta += [row[0]]
                    phi += [row[1]]
                self.theta = theta
                self.phi = phi
            else:
                self.theta, self.phi = direction
            self.angle_unit = angle_unit

        elif self.direction_type == 'healpix':
            self.nside, self.hpi = direction
            self.theta, self.phi = hp.pix2ang(self.nside, self.hpi)
            self.angle_unit = 'rad'
        else:
            raise Exception("Acceptable direction types are angle (theta, phi) and healpix (nside, index)")

    def _printInfo(self):

        print("\nPRINTING USER PARAMETERS:")
        print("Field: " + str(self.field))
        print("Particle: " + str(self.particle))
        print("Energy: " + str(self.energy))
        print("Energy unit: " + str(self.energy_unit))
        print("Direction Theta: " + str(self.theta))
        print("Direction Phi: " + str(self.phi))
        print("Direction type: " + str(self.direction_type))
        print("Angle unit: " + str(self.angle_unit))
        print("Nevents: " + str(self.num_particles))
        print("source rad: " + str(self.source_rad))
        print("source dist: " + str(self.source_dist))
        print("length_unit: " + str(self.length_unit))
        print("random_seed: " + str(self.random_seed))
        print("outputfile: " + str(self.outputfile))
