import Geant4 as g4

def get_all_children(node):
    children = []
    if node.children:
        for child in node.children:
            print('child = ',child.name)
            children += [child]
            children += get_all_children(child)
    return children

class Volume():
    '''
    General volume object

    A volume is a primitive with a material, placed in some parent volume.
    self.solid = primitive
    self.logical = primitive + material
    self.physical = placed logical in parent

    ...

    '''

    def __init__(self, name, primitive, material, sensitive, color,
                       parent=None, userinfo=None, translation=None, rotation=None, rotationName=None):

        self.name = g4.G4String(name)
        self.solid = primitive
        self.material = material
        self.sensitive = sensitive
        self.color = color
        self.children = []
        self.userinfo = userinfo

        # Build logical
        self._build_logical()
        # Build physical
        self._build_physical(parent, translation, rotation, rotationName)

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

        return g4.G4Transform3D(rot, trans)

    def _build_physical(self, parent=None, translation=None, rotation=None, rotationName='HEP'):
        self.placeit(parent, translation, rotation, rotationName)

    def placeit(self, parent, translation, rotation, rotationName='HEP', check_overlap=True):

        self.translation = translation
        self.rotation = rotation
        self.parent = parent
        self.update_parent()
        self.transform = self.build_transform(translation, rotation, rotationName)

        parentphys = self.parent.physical if self.parent is not None else None
        self.physical = g4.G4PVPlacement(self.transform,
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

    def get_sensitives(self):
        sensitives = []
        children = get_all_children(self)
        for child in children:
            if child.sensitive:
                sensitives.append(child)
        return sensitives

    def get_logical(self):
        return self.logical
    def get_physical(self):
        return self.physical
    def grade(self):
        return 'vol'
