from __future__ import print_function
import Geant4 as g4
import numpy as np

class MyEventAction(g4.G4UserEventAction):
    "My Event Action"

    def __init__(self):
        g4.G4UserEventAction.__init__(self)
        self.lasteventID = 0
        self.initialEnergy = 0

    def BeginOfEventAction(self, event):

        pga = g4.gRunManager.GetUserPrimaryGeneratorAction()
        initialEnergy = pga.get_source().energy

        evt = event.GetEventID()
        # Grab runmanager, where data is stored
        ra = g4.gRunManager.GetUserRunAction()
        ra.allGenInitE.append(initialEnergy)
        ra.allGenEvtID.append(evt)


        if evt%int(1e5) == 0:
            #if evt != 0:
            dose = np.array(ra.dose).sum()
            print('{} particles simulated'.format(evt))
            print('{} Gy deposited'.format(dose))

    def EndOfEventAction(self, event):
        # Store event ID
        self.lasteventID = event.GetEventID()
