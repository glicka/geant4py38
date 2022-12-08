import Geant4 as g4

class MyDetectorConstruction(g4.G4VUserDetectorConstruction):
    "My Detector Construction"

    def __init__(self, world):

        g4.G4VUserDetectorConstruction.__init__(self)

        self.world = world

    def Construct(self):
        return self.world.physical

    def SetSensitives(self, SD):
        if self.world.grade() == 'GDML':
            sensitives = self.world.get_sensitives(self.world.get_physical())
        else:
            sensitives = self.world.get_sensitives()
        for sensitive in sensitives:
            sensitive.logical.SetSensitiveDetector(SD)
        
