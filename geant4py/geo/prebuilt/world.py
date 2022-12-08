import geant4py as g4py
import numpy as np

def world(primitive, material, extent=[5, 'm']):
    '''
    Base world volume
    '''

    if np.char.lower(primitive) == 'sphere':
        world_primitive = g4py.geo.primitive.Sphere('world',
                                                    dim={'inner_rad':[0,'m'],
                                                         'outer_rad':extent,
                                                         'sPhi':[0,'deg'],
                                                         'dPhi':[360,'deg'],
                                                         'sTheta':[0,'deg'],
                                                         'dTheta':[180,'deg']})

    elif np.char.lower(primitive) == 'box':
        world_primitive = g4py.geo.primitive.BoxSolid('world',
                                                      dim={'x':[extent,'m'],
                                                           'y':[extent,'m'],
                                                           'z':[extent,'m']})

    return g4py.geo.volume.Volume(name='world',
                                  primitive=world_primitive,
                                  material=material,
                                  sensitive=False,
                                  color=None,
                                  parent=None,
                                  translation=None,
                                  rotation=None)
