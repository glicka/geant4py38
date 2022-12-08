import Geant4 as g4
#import pyg4ometry as g4o

def Sphere(name='sphere', dim={'inner_rad':[0,'mm'],
                               'outer_rad':[1,'mm'],
                               'sPhi':[0,'deg'],
                               'dPhi':[360,'deg'],
                               'sTheta':[0,'deg'],
                               'dTheta':[180,'deg']}):
    '''
    Geant4 primitive solid - sphere

    Inputs:
    ------------------
    name [string] = name of solid
    dim [dictionary] = array full lengths (float) and units (string) along each
                       named axis
        - dim['inner_rad'] = [value, unit] -- inner radius
        - dim['outer_rad'] = [value, unit] -- outer radius
        - dim['sPhi'] = [value, unit] -- start of azimuthal angle
        - dim['dPhi'] = [value, unit] -- delta of azimuthal angle
        - dim['sTheta'] = [value, unit] -- start of polar angle
        - dim['dTheta'] = [value, unit] -- delta of polar angle

    Returns
    ------------------
    G4Solid object
    '''

    return g4.G4Sphere(g4.G4String(name),
                       dim['inner_rad'][0] * getattr(g4, dim['inner_rad'][1]),
                       dim['outer_rad'][0] * getattr(g4, dim['outer_rad'][1]),
                       dim['sPhi'][0] * getattr(g4, dim['sPhi'][1]),
                       dim['dPhi'][0] * getattr(g4, dim['dPhi'][1]),
                       dim['sTheta'][0] * getattr(g4, dim['sTheta'][1]),
                       dim['dTheta'][0] * getattr(g4, dim['dTheta'][1]))


def BoxSolid(name='boxsolid', dim={'x':[1,'mm'],
                                   'y':[1,'mm'],
                                   'z':[1,'mm']}):
    '''
    Geant4 primitive solid - solid box

    Inputs:
    ------------------
    name [string] = name of solid
    dim [dictionary] = array full lengths (float) and units (string) along each
                       named axis
        - dim['x'] = [value, unit] -- full x length
        - dim['y'] = [value, unit] -- full y length
        - dim['z'] = [value, unit] -- full z length

    Returns
    ------------------
    G4Solid object
    '''

    return g4.G4Box(g4.G4String(name),
                    dim['x'][0] / 2. * getattr(g4, dim['x'][1]),
                    dim['y'][0] / 2. * getattr(g4, dim['y'][1]),
                    dim['z'][0] / 2. * getattr(g4, dim['z'][1]))
"""
def boxG4o(name='boxsolid', dim={'x':[1,'mm'],
                                   'y':[1,'mm'],
                                   'z':[1,'mm']}, registry=None):
    '''
    Geant4 primitive solid - solid box

    Inputs:
    ------------------
    name [string] = name of solid
    dim [dictionary] = array full lengths (float) and units (string) along each
                       named axis
        - dim['x'] = [value, unit] -- full x length
        - dim['y'] = [value, unit] -- full y length
        - dim['z'] = [value, unit] -- full z length

    Returns
    ------------------
    G4Solid object
    '''

    return g4o.geant4.solid.Box(str(name),
                    dim['x'][0] / 2. ,
                    dim['y'][0] / 2. ,
                    dim['z'][0] / 2. ,
                    registry         ,
                    lunit = x[1]     )
"""
def BoxHollow(name='boxhollow', dim={'x_start':[1,'mm'],
                               'x_end':[2,'mm'],
                               'y_start':[1,'mm'],
                               'y_end':[2,'mm'],
                               'z_start':[1,'mm'],
                               'z_end':[2,'mm']}):
    '''
    Geant4 primitive solid - hollow box

    Inputs:
    ------------------
    name [string] = name of solid
    dim [dictionary] = array full lengths (float) and units (string) along each
                       named axis
        - dim['x_start'] = [value, unit] -- start of x extent
        - dim['x_end'] = [value, unit] -- end of x extent
        - dim['y_start'] = [value, unit] -- start of y extent
        - dim['y_end'] = [value, unit] -- end of y extent
        - dim['z_start'] = [value, unit] -- start of z extent
        - dim['z_end'] = [value, unit] -- end of z extent

    Returns
    ------------------
    G4Solid object
    '''

    outer_box = g4.G4Box(g4.G4String("outer_box"),
                         dim['x_end'][0] / 2. * getattr(g4, dim['x_end'][1]),
                         dim['y_end'][0] / 2. * getattr(g4, dim['y_end'][1]),
                         dim['z_end'][0] / 2. * getattr(g4, dim['z_end'][1]))

    inner_box = g4.G4Box(g4.G4String("inner_box"),
                         dim['x_start'][0] / 2. * getattr(g4, dim['x_start'][1]),
                         dim['y_start'][0] / 2. * getattr(g4, dim['y_start'][1]),
                         dim['z_start'][0] / 2. * getattr(g4, dim['z_start'][1]))

    return Subtraction(g4.G4String(name), outer_box, inner_box)


def Cylinder(name='cylinder', dim={'inner_rad':[0,'mm'],
                                   'outer_rad':[1,'mm'],
                                   'height':[1,'mm'],
                                   'sPhi':[0,'deg'],
                                   'dPhi':[360,'deg']}):
    '''
    Geant4 primitive solid - cylinder

    Inputs:
    ------------------
    name [string] = name of solid
    dim [dictionary] = array full lengths (float) and units (string) along each
                       named axis
        - dim['inner_rad'] = [value, unit] -- inner radius
        - dim['outer_rad'] = [value, unit] -- outer radius
        - dim['height'] = [value, unit] -- full height
        - dim['sPhi'] = [value, unit] -- start of azimuthal angle
        - dim['dPhi'] = [value, unit] -- delta of azimuthal angle

    Returns
    ------------------
    G4Solid object
    '''

    return g4.G4Tubs(g4.G4String(name),
                     dim['inner_rad'][0] * getattr(g4, dim['inner_rad'][1]),
                     dim['outer_rad'][0] * getattr(g4, dim['outer_rad'][1]),
                     dim['height'][0] / 2. * getattr(g4, dim['height'][1]),
                     dim['sPhi'][0] * getattr(g4, dim['sPhi'][1]),
                     dim['dPhi'][0] * getattr(g4, dim['dPhi'][1]))

def Cone(name = 'cone', dim={'inner_rad1':[0,'mm'],
                                   'outer_rad1':[1,'mm'],
                                   'inner_rad2':[0,'mm'],
                                   'outer_rad2':[2,'mm'],
                                   'height':[1,'mm'],
                                   'sPhi':[0,'deg'],
                                   'dPhi':[360,'deg']}):

    '''
    Geant4 primitive solid - cone

    Inputs:
    ------------------
    name [string] = name of solid
    dim [dictionary] = array full lengths (float) and units (string) along each
                       named axis
        - dim['inner_rad1'] = [value, unit] -- inner radius of top
        - dim['outer_rad1'] = [value, unit] -- outer radius of top
        - dim['inner_rad2'] = [value, unit] -- inner radius of bottom
        - dim['outer_rad2'] = [value, unit] -- outer radius of bottom
        - dim['height'] = [value, unit] -- full height
        - dim['sPhi'] = [value, unit] -- start of azimuthal angle
        - dim['dPhi'] = [value, unit] -- delta of azimuthal angle

    Returns
    ------------------
    G4Solid object
    '''
    return g4.G4Cons(g4.G4String(name),
                     dim['inner_rad1'][0] * getattr(g4, dim['inner_rad1'][1]),
                     dim['outer_rad1'][0] * getattr(g4, dim['outer_rad1'][1]),
                     dim['inner_rad2'][0] * getattr(g4, dim['inner_rad2'][1]),
                     dim['outer_rad2'][0] * getattr(g4, dim['outer_rad2'][1]),
                     dim['height'][0] / 2. * getattr(g4, dim['height'][1]),
                     dim['sPhi'][0] * getattr(g4, dim['sPhi'][1]),
                     dim['dPhi'][0] * getattr(g4, dim['dPhi'][1]))


def Subtraction(name, solidA, solidB, rotation=None, translation=None):
    '''
    Subtract one solid from another

    Document...

    '''
    if (solidA is None) and (solidB is None):
        return g4.G4SubtractionSolid()

    return g4.G4SubtractionSolid(g4.G4String(name), solidA, solidB, Transform(rotation, translation))


def Union(name, solidA, solidB, rotation=None, translation=None):
    '''
    Union two solids

    Document...

    '''
    if (solidA is None) and (solidB is None):
        return g4.G4UnionSolid()

    return g4.G4UnionSolid(g4.G4String(name), solidA, solidB, Transform(rotation, translation))


def Transform(rotation=None, translation=None):
    '''
    Build Geant4 transform

    Document...

    '''

    trans = g4.G4ThreeVector() if translation is None else g4.G4ThreeVector(*translation)
    rot = g4.G4RotationMatrix()
    if rotation is not None:
        rot.setTheta(rotation[0])
        rot.setPhi(rotation[1])
        rot.setPsi(rotation[2])
    transform = g4.G4Transform3D(rot, trans)

    return transform
