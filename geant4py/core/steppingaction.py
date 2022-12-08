import Geant4 as g4

class MySteppingAction(g4.G4UserSteppingAction):
    "My Stepping Action"

    def UserSteppingAction(self, step):
        #kBefore = step.GetPreStepPoint().GetKineticEnergy()
        #print('kBefore = ',kBefore)
        pass
