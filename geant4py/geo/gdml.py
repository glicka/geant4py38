import Geant4 as g4

def get_all_children(node):
    children = []
    print('parent = ',g4.G4String(node.GetName()))
    print('num child = ',node.GetLogicalVolume().GetNoDaughters())
    for i in range(node.GetLogicalVolume().GetNoDaughters()):
        if node.GetLogicalVolume().GetDaughter(i):
            child = node.GetLogicalVolume().GetDaughter(i)
            child = GDML(name=child.GetName(), physical=child, color=g4py.geo.colors.red(), sensitive=True, parent=node)
            children += [child]
            children += get_all_children(child.get_physical())
    return children

class GDML():
    '''
    Create a general volume object from GDML loaded geo.

    ...
    Steps:

    1. Load the GDML with parent = None
    2. Place the GDML object inside the world volume by setting parent = world
    ...

    '''

    def __init__(self, name, physical, color, sensitive=False,
                       parent=None, userinfo=None, translation=None, rotation=None, rotationName=None):

        self.name = g4.G4String(name)
        self.logical = physical.GetLogicalVolume()
        self.material = self.logical.GetMaterial()
        self.color = color
        self.children = []
        self.userinfo = userinfo
        self.sensitive = sensitive
        self.parent = parent
        self.physical = physical
        del physical

        if self.parent is not None:
            try:
                parentName = self.physical.GetMotherLogical().GetName()
            except:
                parentName = None
            if parentName is None or parentName != self.parent.GetLogicalVolume().GetName():
                self.solid = self.logical.GetSolid()
                self.material = self.logical.GetMaterial()
                if not self.logical:
                    # Build logical
                    self._build_logical()
                # Build physical
                self._build_physical(self.parent, translation, rotation, rotationName)


    def _build_logical(self):

        self.logical = g4.G4LogicalVolume(self.solid,
                                          self.material,
                                          self.name)
        # Visual attributes
        vis = g4.G4VisAttributes()
        if self.color is not None:
            vis.SetColor(g4.G4Color(*self.color))
        else:
            vis.SetVisibility(False)
        self.logical.SetVisAttributes(vis)

    def build_transform(self, translation, rotation, rotationName = None):
        trans = g4.G4ThreeVector() if translation is None else g4.G4ThreeVector(*translation)
        rot = g4.G4RotationMatrix()
        if rotation is not None:
            if rotationName == 'HEP':
                rot.setTheta(rotation[0])
                rot.setPhi(rotation[1])
                rot.setPsi(rotation[2])
            elif rotationName == 'rotAx':
                rot.rotateY(rotation[0])
                rot.rotateZ(rotation[1])
        return trans, rot

    def _build_physical(self, parent=None, translation=None, rotation=None, rotationName='HEP'):
        self.placeit(parent, translation, rotation, rotationName)

    def placeit(self, parent, translation, rotation, rotationName='HEP', check_overlap=True):

        self.translation = translation
        self.rotation = rotation
        self.parent = parent
        self.update_parent()
        trans,rot = self.build_transform(translation, rotation, rotationName)
        try:
            parentphys = self.parent.physical if self.parent is not None else None
        except:
            parentphys = self.parent if self.parent is not None else None

        self.physical = g4.G4PVPlacement(g4.G4Transform3D(rot,trans),
                                         self.name,
                                         self.logical,
                                         parentphys,
                                         False,
                                         0)

    def check_overlaps(self):
        if self.physical.CheckOverlaps(1000, 0., True):
            raise Exception("Overlap detected for volume %s" % self.name)

    def update_parent(self):
        if self.parent is not None:
            if self not in self.parent.children:
                self.parent.children.append(self)


    def get_sensitives(self,parentphys):
        sensitives = []
        children = get_all_children(parentphys)
        for child in children:
            if child.sensitive:
                sensitives.append(child)
        return sensitives

    def get_logical(self):
        return self.logical

    def get_physical(self):
        return self.physical

    def grade(self):
        return 'GDML'
