import Geant4 as g4
import numpy as np

class MyStackingAction(g4.G4UserStackingAction):
    "My Stacking Action"

    def __init__(self, track_secondaries):

        g4.G4UserStackingAction.__init__(self)
        self.track_secondaries = track_secondaries
        self.step = g4.G4UserSteppingAction

    def UserSteppingAction(self, step):
        pass


    def ClassifyNewTrack(self, track):
        cl = g4.G4ClassificationOfNewTrack(0)
        #if (track.GetDefinition().GetParticleName() != "neutron"):# and (track.GetDefinition().GetParticleName() != "proton"):
        #    cl = g4.G4ClassificationOfNewTrack(-9)
        # Kill secondaries (here this means everything except gammas/xrays. Xrays are killed with
        # production cut set in main.py)
        if not self.track_secondaries:
            if (track.GetDefinition().GetParticleName() != "gamma"):
                cl = g4.G4ClassificationOfNewTrack(-9)
        #kBefore = track.GetKineticEnergy()
        '''
        if self.track_secondaries:
            try:
                touchable = track.GetTouchable()
                vol = str(touchable.GetVolume().GetName())
                if vol.find('floor') != -1:

                    momentum = track.GetMomentumDirection()
                    print('momentum = ', momentum.z)
                    print('energy = ',kBefore)
                    if momentum.x > 0:
                        cl = g4.G4ClassificationOfNewTrack(-9)
            except:
                cl = g4.G4ClassificationOfNewTrack(0)
        '''




        '''
        if self.track_secondaries:
            try:
                touchable = track.GetTouchable()
                vol = str(touchable.GetVolume().GetName())
                if vol.find('floor') != -1:
                    ra = g4.gRunManager.GetUserRunAction()
                    evtID = g4.gRunManager.GetCurrentEvent().GetEventID()
                    ind = np.where(ra.allGenEvtID == evtID)[0]
                    if len(ind) > 500:
                        cl = g4.G4ClassificationOfNewTrack(-9)
            except:
                cl = g4.G4ClassificationOfNewTrack(0)
        '''


        return cl
