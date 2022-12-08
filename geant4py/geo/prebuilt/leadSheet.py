import geant4py as g4py
import numpy as np
#import pyg4ometry as g4o
def photonAbsorber(name, copies=1, indices=[""]):
    '''
    Lead Sheet for absorbing photons
    '''

    assert copies >= 1

    dummyDim = {"x": [5000 + 6 , 'cm'], "y": [5000 + 6, 'cm'], "z": [50, 'cm']}
    dummyPrimitive = g4py.geo.primitive.BoxSolid('boxDummy', dummyDim)
    dummyMaterial = g4py.geo.material.Vacuum()
    dummyColor = None#np.array([0.2, 0.2, 0.2, 0.2])#*10

    # Setting up aluminum casing
    leadDim = {"x": [5000 , 'cm'], "y": [5000, 'cm'], "z": [50, 'cm']}
    leadPrim = g4py.geo.primitive.BoxSolid('leadBox', leadDim)
    leadMaterial = g4py.geo.material.element('Pb')
    leadColor = g4py.geo.colors.blue()

    airHoleDim = {"inner_rad": [0, 'cm'], "outer_rad": [10, 'cm'], "height": [50, 'cm'],'sPhi':[0,'deg'],'dPhi':[360,'deg']}
    airHolePrimitive = g4py.geo.primitive.Cylinder('airHole', airHoleDim)
    airHoleMaterial = g4py.geo.material.Air()
    airHoleColor = g4py.geo.colors.white()
    # Creating and placing volumes
    vol = np.empty(copies, dtype=object)
    for i in range(copies):
        dummy = g4py.geo.volume.Volume(name=name+"_"+str(i),
                                       primitive=dummyPrimitive,
                                       material=dummyMaterial,
                                       sensitive=False,
                                       color=dummyColor,
                                       parent=None,
                                       translation=[0,0,0],
                                       rotation=None)

        lead = g4py.geo.volume.Volume(name="photonAbsorber"+"_"+str(i),
                                        primitive=leadPrim,
                                        material=leadMaterial,
                                        sensitive=True,
                                        color=leadColor,
                                        parent=dummy,
                                        translation=[0,0,0],
                                        rotation=None)

        airHole = g4py.geo.volume.Volume(name="photonAbsorber"+"_"+str(i),
                                        primitive=airHolePrimitive,
                                        material=airHoleMaterial,
                                        sensitive=True,
                                        color=airHoleColor,
                                        parent=lead,
                                        translation=[0,0,0],
                                        rotation=None)



        vol[i] = dummy


    if copies > 1: return vol
    else: return vol[0]
