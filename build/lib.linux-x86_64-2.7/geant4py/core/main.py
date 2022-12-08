# Imports
## Geant4
from Geant4 import gRunManager, HepRandom, G4String, G4physicslists, G4UImanager
## Python
import numpy as np
from multiprocessing import cpu_count, Pool, Process, Queue
import copy
import time
import tables
import numpy.lib.recfunctions as rfn
import os
#from torch.multiprocessing import Pool
from contextlib import closing
#import ray
## geant4py
import geant4py.core.detectorconstruction as g4DC
import geant4py.core.primarygeneratoraction as g4PGA
import geant4py.core.runaction as g4RA
import geant4py.core.eventaction as g4EA
import geant4py.core.sensitivedetector as g4SD
import geant4py.core.stackingaction as g4StackA
import geant4py.core.physicslist as g4PL
import geant4py.core.steppingaction as g4StepA
import geant4py.core.visualization as visualization
from geant4py.geo.volume import get_all_children
from geant4py.core.argparser import argparser

import logging
import os
import multiprocessing
from threading import Semaphore
from time import sleep


def BeamOn(source):#,detector=None):

    # Set source in primarygeneratoraction
    pga = gRunManager.GetUserPrimaryGeneratorAction()
    pga.set_source(source)
    '''
    if detector is not None:
        pga.set_det(detector)
    '''


    # Beam on!
    print('Beam On!')
    print('num particles = ', source.num_particles)
    print('particle type = ', source.particle)
    print('polar dir = ', 90-source.theta)
    gRunManager.BeamOn(source.num_particles)



class Run():
    '''
    Initialize simulation and run
    '''

    def __init__(self, world, source, check_overlaps=False, track_secondaries=False,
                       vis_driver=None, multiprocess=False, physics_list="FTFP_BERT_LIV",
                       process_tracking=None):

        self.world = world
        self.source = source
        self.check_overlaps = check_overlaps
        self.track_secondaries= track_secondaries
        self.vis_driver = vis_driver
        if hasattr(physics_list,'lower'):
            self.physics_list = G4String(physics_list)
        else:
            self.physics_list = [G4String(physics_list[i]) for i in range(len(physics_list))]
        self.multiprocess = multiprocess
        self.process_tracking = process_tracking

        # Override some of these attributes if passed through the command line
        self.parse_command_line()

        # Check overlaps
        if self.check_overlaps:
            vols = get_all_children(self.world)
            for vol in vols:
                vol.check_overlaps()
        # Start sim
        self.execute()

    def parse_command_line(self):
        argument = argparser()

        # Override source type if command line argument passed
        if argument.field:
            self.source.field = argument.field

        # Dont run any particles if visualizing, unless specified below...
        if argument.vis:
            self.vis_driver = argument.vis

        # Override overlap checking if command line argument passed
        if argument.check_overlaps:
            self.check_overlaps = argument.check_overlaps

        # Override track secondaries if command line argument passed
        if argument.track_secondaries:
            self.track_secondaries = argument.track_secondaries

        # Override multiprocessing if command line argument passed
        if argument.multiprocess:
            self.multiprocess = argument.multiprocess

        ### Build out source term

        # Assume just one source to begin with
        num_sources = 1

        # If multiple sources are passed in the script. ignore command line
        if isinstance(self.source, list):
            print("Ignoring source-related command line arguments b/c multiple sources were passed to Run()")
            return

        # Override number of particles if command line argument passed
        num_particles = argument.num_particles if argument.num_particles else self.source.num_particles

        # Override outputfile name if command line argument passed
        outputfile = argument.output if argument.output else self.source.outputfile

        # Override random seed if command line argument passed
        random_seed = argument.random_seed if argument.random_seed else self.source.random_seed

        # Override energy if command line argument passed
        if argument.energy:
            energy = argument.energy
            energy_unit = 'keV'
            num_sources = len(energy)
            if num_sources == 1:
                energy = energy[0]
        else:
             energy, energy_unit = (self.source.energy, self.source.energy_unit)
             if isinstance(energy, list):
                 num_sources = len(energy)
        # Override angle if command line argument passed
        if argument.angle:
            direc = argument.angle
            direc_type = 'angle'
            direc_unit = 'rad'
        else:
            direc_type = self.source.direction_type
            direc_unit = self.source.angle_unit
            if direc_type == 'angle':
                if np.array(self.source.theta).shape != ():
                    direc = [[self.source.theta[k], self.source.phi[k]] for k in range(len(self.source.theta))]
                    if len(self.source.theta) > 1:
                        num_sources = len(self.source.theta)
                else:
                    direc = [self.source.theta,self.source.phi]
                #print(direc)

            else:
                direc = (self.source.nside, self.source.hpi)

        # Override healpix direction if command line argument passed
        if argument.healpix:
            nside = int(argument.healpix[0])
            if len(argument.healpix) > 2:
                if num_sources > 1:
                    raise Exception("Currently can only construct multiple sources over one variable in command line")
                else:
                    direc = zip([nside] * (len(argument.healpix) - 1), argument.healpix[1:])
                    print(direc)
                    num_sources = len(argument.healpix[1:])
            elif argument.healpix[1] == -1:
                if num_sources > 1:
                    raise Exception("Currently can only construct multiple sources over one variable in command line")
                else:
                    direc = zip([nside] * (nside*nside*12), range(nside*nside*12))
                    num_sources = nside*nside*12
            else:
                direc = argument.healpix
            direc_type = 'healpix'

        # If there are multiple sources, create source list
        #nums = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 18, 19, 24, 25, 30, 31, 36, 37, 42, 43])#[0, 36, 18, 12, 24, 30, 42, 6, 1, 37, 19, 13, 25, 31, 43, 7])
        #print('number of sources = ', num_sources)
        if num_sources > 1:
            self.particle = self.source.particle
            source_list = []
            for i in range(num_sources):
                #if all(i != ki for ki in nums) and i < 2000:
                # Copy source
                s = copy.deepcopy(self.source)
                #print('deepcopy = ', s)
                # Update
                s.num_particles = num_particles
                s.outputfile = outputfile + "_" + str(i)
                s.sourcedatafile = self.source.sourcedatafile + "_" + str(i)
                s.random_seed = random_seed + i
                s.energy_unit = energy_unit
                s.energy = energy[i] if isinstance(energy, list) else energy
                d = direc[i] if len(np.shape(direc)) > 1 else direc
                s._setDirection(d, direc_type)
                # Append to list
                source_list.append(s)
            # Set as source
            self.source = source_list
            print('number of sources = ', len(source_list))
            #ncpus = cpu_count()
            #pool = Pool(processes = ncpus, maxtasksperchild=1)


        # Otherwise, update current source
        else:
            # Update
            self.particle = self.source.particle
            self.source.num_particles = num_particles
            self.source.outputfile = outputfile
            self.source.energy = energy
            self.source.energy_unit = energy_unit
            self.source._setDirection(direc, direc_type, direc_unit)

    def execute(self):

        # Time
        start_time = time.time()

        # Setup geometry
        detector_construction = g4DC.MyDetectorConstruction(self.world)
        gRunManager.SetUserInitialization(detector_construction)
        self.det = detector_construction

        # Set physics list
        physfactory = G4physicslists.G4PhysListFactory()
        if hasattr(self.physics_list,'lower'):
            physlist = physfactory.GetReferencePhysList(self.physics_list)
            gRunManager.SetUserInitialization(physlist)
        else:
            for i in range(len(self.physics_list)):
                physlist = physfactory.GetReferencePhysList(self.physics_list[i])
                gRunManager.SetUserInitialization(physlist)
        #physlist = g4PL.MyPhysicsList()


        # Set up beam
        primary_generator_action = g4PGA.MyPrimaryGeneratorAction()
        gRunManager.SetUserAction(primary_generator_action)

        # Run action
        run_action = g4RA.MyRunAction()
        gRunManager.SetUserAction(run_action)

        # Event action
        event_action= g4EA.MyEventAction()
        gRunManager.SetUserAction(event_action)

        # Stacking action
        stacking_action= g4StackA.MyStackingAction(self.track_secondaries)
        gRunManager.SetUserAction(stacking_action)

        # Stepping action
        stepping_action= g4StepA.MySteppingAction()
        gRunManager.SetUserAction(stepping_action)

        # Set range cuts (HACK!)
        if self.track_secondaries:
            if self.particle == "gamma":
                G4UImanager.GetUIpointer().ApplyCommand("/run/setCutForAGivenParticle gamma 1 um")
            elif self.particle == "neutron":
                G4UImanager.GetUIpointer().ApplyCommand("/run/setCutForAGivenParticle neutron 1 um")
                G4UImanager.GetUIpointer().ApplyCommand("/run/setCutForAGivenParticle proton 1 um")
            elif self.particle == "e-":
                G4UImanager.GetUIpointer().ApplyCommand("/run/setCutForAGivenParticle e- 1 um")
                G4UImanager.GetUIpointer().ApplyCommand("/run/setCutForAGivenParticle gamma 1 um")
            # G4UImanager.GetUIpointer().ApplyCommand("/run/setCut 10 nm")
            # G4UImanager.GetUIpointer().ApplyCommand("/process/em/deexcitationIgnoreCut true")
            # G4UImanager.GetUIpointer().ApplyCommand("/process/em/pixeElecXSmodel Livermore")
            # G4UImanager.GetUIpointer().ApplyCommand("/process/em/fluo true")
            # G4UImanager.GetUIpointer().ApplyCommand("/process/em/auger true")
            # G4UImanager.GetUIpointer().ApplyCommand("/process/em/pixe true")

        # Initialize run
        gRunManager.Initialize()

        # Setup visualization
        visualization.setup_vis(self.vis_driver)

        # Setup sensitive detector
        sd = g4SD.MySensitiveDetector(G4String("sd"), self.process_tracking)
        #print('sensitivedetector = ', sd)
        detector_construction.SetSensitives(sd)

        # Time
        print("\nTime to initialize simultation: %0.2f s" % (time.time() - start_time))

        # Run sim in multiprocessing mode
        if self.multiprocess:

            # Setup pool with max CPU
            ncpus = cpu_count()
            #pool = Pool(processes = ncpus)#, maxtasksperchild=1)


            # If source is not list, distribute single sim over particles
            if not isinstance(self.source, list):
                chunk = 1
                # Set up beam


                # Chunk particles
                particles = [self.source.num_particles / ncpus] * ncpus
                if np.sum(particles) != self.source.num_particles:
                    particles.append(self.source.num_particles - np.sum(particles))

                # Build separate source terms
                source_list = []
                sourceTest = []
                for i, j in enumerate(particles):
                    # Copy
                    s = copy.deepcopy(self.source)
                    # Change particles
                    s.num_particles = j
                    # Change random seed
                    s.random_seed = self.source.random_seed + i
                    # Change filename
                    s.outputfile = self.source.outputfile + "_" + str(i)
                    s.sourcedatafile = self.source.sourcedatafile + "_" + str(i)
                    # Append to list
                    source_list.append(s)
                    #sourceTest += [s]

                # Set as source

                print('source list[i] = ', source_list)
                self.source = source_list
            else:
                chunk = int(1.*len(self.source)/ncpus)


            # Beam on!
            start_time = time.time()
            iterableInt = int(1*ncpus)
            iterable = int(len(self.source)*1./(iterableInt))+1
            print('iterables = ', iterable)
            print('ncpus = ', ncpus)
            for i in range(iterable):
                k1 = i*iterableInt
                k2 = (i+1)*iterableInt
                if k2 > int(len(self.source)+1):
                    s = self.source[k1:]
                else:
                    s = self.source[k1:k2]
                chunk = int(len(s)*1./ncpus)
                pool = Pool(processes = ncpus)
                pool.map(BeamOn, s, chunksize=1)
                pool.close()

            #print(self.source)
            #ray.init()

            print('chunksize = ',chunk)
            #ray.get([BeamOn.remote(self.source[i]) for i in range(ncpus)])
            #pool.map(BeamOn, self.source,ncores=ncpus)

            '''
            with closing(Pool(ncpus)) as p:
                p.map(BeamOn, self.source)
                p.close()
            '''

            '''
            processes = []
            for i in range(len(self.source)):
                s = self.source[i]
                p = Process(target=BeamOn, args=(s,))
                p.start()
                processes.append(p)
                while True:
                    if all([p.exitcode != None for p in processes]):
                        print('process finished')
                        p
            '''



            #print(ncpus)
            #print(len(self.source))


            print("\nSimulation time = %0.2f s" % (time.time() - start_time))

            # Merge output files
            self.merge_hdf5(self.source)
            self.merge_alldata_hdf5(self.source)

        # Run serialized
        else:

            # Beam on!
            if isinstance(self.source, list):
                start_time = time.time()

                for s in self.source:
                    print('running multiple sources serialized = ',s)

                    BeamOn(s)
                print("\nSimulation time = %0.2f s" % (time.time() - start_time))

            else:
                print('running serialized')
                start_time = time.time()
                # Set up beam
                primary_generator_action = g4PGA.MyPrimaryGeneratorAction(self.source)
                gRunManager.SetUserAction(primary_generator_action)
                BeamOn(self.source)
                print("\nSimulation time = %0.2f s" % (time.time() - start_time))

                # Hold visualization open if OGL
                if self.vis_driver is not None:
                    if np.char.lower(self.vis_driver) == 'oglsx':
                        raw_input("Enter to quit:")

    def merge_hdf5(self, source_list):

        # Filename
        fname = os.path.dirname(source_list[0].outputfile) + '/' + os.path.basename(source_list[0].outputfile).split("_")[0]
        print(fname)
        # Create one file
        h5file = tables.open_file(fname + ".h5", "w",
                                title="Geant4 simulation output")
        raw = h5file.create_group("/", 'raw', 'Simulation data')
        # Loop over individual and grab data
        filnum = int(os.path.basename(source_list[-1].outputfile).split('_')[1]) + 1
        for i in range(filnum):#, s in enumerate(source_list):
            # Filename
            filname = fname + "_" + str(i) + ".h5"
            # Get data
            f = tables.open_file(filname, "r")
            dat = f.root.raw.data[:]

            # Create new data table
            h5file.create_table(raw, 'data_' + str(i), dat, 'Simulation output')
            # Transfer metadata
            x = getattr(h5file.root.raw, 'data_' + str(i))
            for attr in f.root.raw.data._v_attrs._f_list():
                setattr(x._v_attrs, attr, getattr(f.root.raw.data._v_attrs, attr))
            # Close
            f.close()
            # Remove
            os.remove(filname)

        # Close
        h5file.close()

    def merge_alldata_hdf5(self, source_list):

        # Filename
        fname = fname = os.path.dirname(source_list[0].sourcedatafile) + '/' + os.path.basename(source_list[0].sourcedatafile).split("_")[0]
        print(fname)
        # Create one file
        h5file = tables.open_file(fname + ".h5", "w",
                                title="Geant4 simulation output")
        raw = h5file.create_group("/", 'raw', 'Simulation data')
        # Loop over individual and grab data
        filnum = int(os.path.basename(source_list[-1].sourcedatafile).split('_')[1]) + 1
        for i in range(filnum):#, s in enumerate(source_list):
            # Filename
            filname = fname + "_" + str(i) + ".h5"
            # Get data
            f = tables.open_file(filname, "r")
            dat = f.root.raw.data[:]

            # Create new data table
            h5file.create_table(raw, 'data_' + str(i), dat, 'Simulation output')
            # Transfer metadata
            x = getattr(h5file.root.raw, 'data_' + str(i))
            for attr in f.root.raw.data._v_attrs._f_list():
                setattr(x._v_attrs, attr, getattr(f.root.raw.data._v_attrs, attr))
            # Close
            f.close()
            # Remove
            os.remove(filname)

        # Close
        h5file.close()
