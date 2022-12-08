from __future__ import print_function
import Geant4 as g4
import numpy as np
import os
import tables
import datetime

class MyRunAction(g4.G4UserRunAction):
    "My Run Action"

    def __init__(self):

        g4.G4UserRunAction.__init__(self)

        self.process_mapping = {"phot":0, "compt":1, "rayl":2, "transportation":3, "conv":4,
                                "eioni":5, "annihil":6, "msc":7, "ebrem":8, "ionioni":9, "hadelastic":10,
                                "hioni":11, "neutroninelastic":12, "ncapture":13, "nkiller":14}
        self.particle_mapping =  {"gamma":0, "neutron":1, "alpha":2, "e+":3, "e-":4, "C12":5,
                                "C13":6, "C14":7, "proton":8, "Be9":9, "Be10":10, "deuteron":11,
                                "Al27":12, "O16":13, "O17":14, "O18":15, "N14":16, "Pb208":17}

    def BeginOfRunAction(self, run):


        self.allGenInitE = []
        self.allGenEvtID = []

        # Time
        self.beginruntime = str(datetime.datetime.now())

        self.trackID = []
        self.eventID = []
        self.subeventID = []
        self.time = []
        self.particle = []
        self.detID = []
        self.interaction = []
        self.initE = []
        self.E = []
        self.dose = []
        self.cumDose = 0
        self.gx = []
        self.gy = []
        self.gz = []
        self.dx = []
        self.dy = []
        self.dz = []

    def EndOfRunAction(self, run):

        # Time
        self.endruntime = str(datetime.datetime.now())

        # Get ID of last event simulated
        ea = g4.gRunManager.GetUserEventAction()
        lasteventID = ea.lasteventID

        print("*** End of Run")
        print(" - Number of events: %i" % (lasteventID+1))
        print(" - Number of hits: %i" % len(self.E))
        print(" - Total dose: {}".format(sum(self.dose)))
        '''

        self.data_dtype = np.dtype([('eventID', np.uint32), ('subeventID', np.uint8),
                                  ('time', np.float32),('trackID', np.uint8),
                                  ("detID", np.uint16),("interaction", np.uint8),
                                  ('particle', np.uint8), ("E", np.float32),
                                  ("initE", np.float32),
                                  ("gx", np.float32), ("gy", np.float32),
                                  ("gz", np.float32), ("dx", np.float32),
                                  ("dy", np.float32), ("dz", np.float32)])

        # Put data into array
        self.data = np.empty(len(self.E), dtype=self.data_dtype)
        self.data['trackID'] = np.array(self.trackID)
        self.data['eventID'] = np.array(self.eventID)
        self.data['subeventID'] = np.array(self.subeventID)
        self.data['time'] = np.array(self.time)
        self.data['particle'] = np.array(self.particle)
        self.data['detID'] = np.array(self.detID)
        self.data['interaction'] = np.array(self.interaction)
        self.data['initE'] = np.array(self.initE)
        self.data['E'] = np.array(self.E)
        self.data['gx'] = np.array(self.gx)
        self.data['gy'] = np.array(self.gy)
        self.data['gz'] = np.array(self.gz)
        self.data['dx'] = np.array(self.dx)
        self.data['dy'] = np.array(self.dy)
        self.data['dz'] = np.array(self.dz)
        '''

        self.alldata_dtype = np.dtype([('eventID', np.uint32),
                                  ("initE", np.float32)])
        # Put data into array
        self.alldata = np.empty(len(self.allGenInitE), dtype=self.alldata_dtype)
        self.alldata['eventID'] = np.array(self.allGenEvtID)
        self.alldata['initE'] = np.array(self.allGenInitE)


        self.data_dtype = np.dtype([('eventID', np.uint32), ('time', np.float32),
                                  ("detID", np.uint16),("interaction", np.uint8),
                                  ('particle', np.uint8), ("E", np.float32),
                                  ("initE", np.float32), ("dx", np.float32),
                                  ("dy", np.float32), ("dz", np.float32),
                                  ("dose", np.float32)])

        # Put data into array
        self.data = np.empty(len(self.E), dtype=self.data_dtype)
        self.data['eventID'] = np.array(self.eventID)
        self.data['particle'] = np.array(self.particle)
        self.data['detID'] = np.array(self.detID)
        self.data['time'] = np.array(self.time)
        self.data['interaction'] = np.array(self.interaction)
        self.data['initE'] = np.array(self.initE)
        self.data['E'] = np.array(self.E)
        self.data['dose'] = np.array(self.dose)
        self.data['dx'] = np.array(self.dx)
        self.data['dy'] = np.array(self.dy)
        self.data['dz'] = np.array(self.dz)

        # Write to disk
        self.write2h5()
        self.writeInitE2h5()

    def write2h5(self):

        # Grab source term from primarygeneratoraction
        pga = g4.gRunManager.GetUserPrimaryGeneratorAction()
        source = pga.get_source()

        # Set up output file
        output_dir = os.path.dirname(source.outputfile)
        if output_dir:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

        # Save (to HDF5)
        h5file = tables.open_file(source.outputfile + ".h5",
                                  mode="w",
                                  title="Geant4 simulation output")
        raw = h5file.create_group("/", 'raw', 'Simulation data')
        h5file.create_table(raw, 'data', self.data, 'Simulation output')

        # Metadata
        h5file.root.raw.data._v_attrs.random_seed = source.random_seed
        h5file.root.raw.data._v_attrs.sim_start_time = self.beginruntime
        h5file.root.raw.data._v_attrs.sim_finish_time = self.endruntime
        h5file.root.raw.data._v_attrs.process_mapping = self.process_mapping
        srcattrs = [a for a in dir(source) if not a.startswith('_')]
        for srcattr in srcattrs:
            setattr(h5file.root.raw.data._v_attrs, srcattr, getattr(source, srcattr))

        # Close
        del self.data
        h5file.close()

    def writeInitE2h5(self):

        # Grab source term from primarygeneratoraction
        pga = g4.gRunManager.GetUserPrimaryGeneratorAction()
        source = pga.get_source()

        # Set up output file
        output_dir = os.path.dirname(source.sourcedatafile)
        if output_dir:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

        # Save (to HDF5)
        h5file = tables.open_file(source.sourcedatafile + ".h5",
                                  mode="w",
                                  title="Geant4 initial E output")
        raw = h5file.create_group("/", 'raw', 'Simulation data')
        h5file.create_table(raw, 'data', self.alldata, 'Simulation output')

        srcattrs = [a for a in dir(source) if not a.startswith('_')]
        for srcattr in srcattrs:
            setattr(h5file.root.raw.data._v_attrs, srcattr, getattr(source, srcattr))

        # Close
        del self.alldata
        h5file.close()
