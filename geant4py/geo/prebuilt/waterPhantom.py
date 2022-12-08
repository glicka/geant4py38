import geant4py as g4py
import numpy as np
import math as m
import os

_HERE = os.path.dirname(os.path.abspath(__file__))

def waterPhantom(name, icDepth=0, copies=1, indices=[""]):



    '''
    500 cm water phantom
    '''

    assert copies >= 1

    dummyDim = {"x": [500 + 6 , 'cm'], "y": [500 + 6, 'cm'], "z": [500, 'cm']}
    dummyPrimitive = g4py.geo.primitive.BoxSolid('boxDummy', dummyDim)
    dummyMaterial = g4py.geo.material.Vacuum()
    dummyColor = None#np.array([0.2, 0.2, 0.2, 0.2])#*10

    # Setting up aluminum casing
    waterDim = {"x": [500 , 'cm'], "y": [500, 'cm'], "z": [500, 'cm']}
    waterPrimitive = g4py.geo.primitive.BoxSolid('waterBox', waterDim)
    waterMaterial = g4py.geo.material.Water()
    waterColor = g4py.geo.colors.red()

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

        water = g4py.geo.volume.Volume(name="waterPhantom"+"_"+str(i),
                                        primitive=waterPrimitive,
                                        material=waterMaterial,
                                        sensitive=False,
                                        color=waterColor,
                                        parent=dummy,
                                        translation=[0,0,0],
                                        rotation=None)
        vol[i] = dummy


    if copies > 1: return vol
    else: return vol[0]
