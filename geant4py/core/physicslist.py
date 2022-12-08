import Geant4 as g4

class MyPhysicsList(g4.G4VUserPhysicsList):
    "My Physics list"

    def ConstructParticle(self):
        pass

    def ConstructProcess(self):
        pass

    def SetCuts(self):
        pass
