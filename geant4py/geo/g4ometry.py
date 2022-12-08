import pyg4ometry as g4o

def get_all_children(node):
    children = []
    if node.children:
        for child in node.children:
            print('child = ',child.name)
            children += [child]
            children += get_all_children(child)
    return children

class G4ometry():
    '''
    Create a general volume object from pyg4ometry package.


    A volume is a primitive with a material, placed in some parent volume.
    self.solid = solid
    self.logical = solid + material
    self.physical = placed logical in register

    ...

    '''

    def __init__(self, name, solid, material, sensitive, color,
                       reg=None, userinfo=None, translation=None, rotation=None, rotationName=None):

        self.name = str(name)
        self.solid = solid
        self.material = material
        self.sensitive = sensitive
        self.color = color
        self.children = []
        self.userinfo = userinfo

        # Build logical
        self._build_logical()
        # Build physical
        self._build_physical(reg, translation, rotation, rotationName)

    def _build_logical(self):

        self.logical = g4o.geant4.LogicalVolume(  self.solid,
                                                  self.material,
                                                  self.name,
                                                  reg)
        # Visual attributes
        vis = g4.G4VisAttributes()
        if self.color is not None:
            vis.SetColor(g4.G4Color(*self.color))
        else:
            vis.SetVisibility(False)
        self.logical.SetVisAttributes(vis)

    def _build_physical(self, parent=None, translation=None, rotation=None, rotationName='HEP'):
        self.placeit(parent, translation, rotation, rotationName)

    def placeit(self, registry, translation, rotation, rotationName='HEP', check_overlap=True):

        self.translation = translation
        self.rotation = rotation
        self.parent = parent
        self.update_parent()
        #self.transform = self.build_transform(translation, rotation, rotationName)

        parentlog = self.parent.logical if self.parent is not None else None
        self.physical = g4o.geant4.PhysicalVolume(self.rotation,
                                                  self.translation,
                                                  self.logical,
                                                  self.name,
                                                  parentlog,
                                                  registry)

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
