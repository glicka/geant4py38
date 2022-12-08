import geant4py as g4py
import numpy as np
#import pyg4ometry as g4o
def waterBox(name, icDepth=0, copies=1, indices=[""]):
    '''
    500 cm water phantom
    '''

    assert copies >= 1

    dummyDim = {"x": [500 + 6 , 'cm'], "y": [500 + 6, 'cm'], "z": [500 + 6, 'cm']}
    dummyPrimitive = g4py.geo.primitive.BoxSolid('boxDummy', dummyDim)
    dummyMaterial = g4py.geo.material.Vacuum()
    dummyColor = None#np.array([0.2, 0.2, 0.2, 0.2])#*10

    # Setting up aluminum casing
    waterDim = {"x": [500 , 'cm'], "y": [500, 'cm'], "z": [500, 'cm']}
    waterPrimitive = g4py.geo.primitive.BoxSolid('waterBox', waterDim)
    waterMaterial = g4py.geo.material.Water()
    waterColor = np.array([0.2, 0.2, 0.2, 0.2])

    icDim = {"inner_rad": [0, 'cm'], "outer_rad": [5, 'cm'], "height": [5, 'cm'],'sPhi':[0,'deg'],'dPhi':[360,'deg']}
    icPrimitive = g4py.geo.primitive.Cylinder('ionChamber', icDim)
    icMaterial = g4py.geo.material.Air()
    icColor = [-1, 4, 1, 1]
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

        water = g4py.geo.volume.Volume(name="waterBox"+"_"+str(i),
                                        primitive=waterPrimitive,
                                        material=waterMaterial,
                                        sensitive=False,
                                        color=waterColor,
                                        parent=dummy,
                                        translation=[0,0,0],
                                        rotation=None)

        ic = g4py.geo.volume.Volume(name="ic"+"_"+str(i),
                                        primitive=icPrimitive,
                                        material=icMaterial,
                                        sensitive=True,
                                        color=icColor,
                                        parent=water,
                                        translation=[0,0,2475-icDepth],
                                        rotation=[np.rad2deg(0),np.rad2deg(0)],
                                        rotationName='rotAx')

        vol[i] = dummy


    if copies > 1: return vol
    else: return vol[0]
