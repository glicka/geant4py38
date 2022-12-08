import geant4py as g4py
import numpy as np
import Geant4 as g4
import math as m
import os
import pydicom as dm
import glob

_HERE = os.path.dirname(os.path.abspath(__file__))

def voxel(name):

    # Setup dummy
    dummyDim = {"x": [PixelSpacing[0]*scaler , 'mm'],
     "y": [PixelSpacing[1]*scaler, 'mm'],
     "z": [PixelSpacing[2]*scaler, 'mm']}
    dummyColor = [2, 2, 2, 2]
    dummyPrimitive = g4py.geo.primitive.Sphere('dummySphere', dummyDim)
    dummyMaterial = g4py.geo.material.Vacuum()

    dummy = g4py.geo.volume.Volume(name=name,
                                   primitive=dummyPrimitive,
                                   material=dummyMaterial,
                                   color=None,
                                   sensitive=False,
                                   parent=None,
                                   translation=None,
                                   rotation=None)



    voxDim = {"x": [PixelSpacing[0]*scaler , 'mm'],
     "y": [PixelSpacing[1]*scaler, 'mm'],
     "z": [PixelSpacing[2]*scaler, 'mm']}
    print('voxDim = ', voxDim)

    voxPrimitive = g4py.geo.primitive.BoxSolid('voxDummy', voxDim)
    voxColor = np.array([0.2, 0.2, 0.2, 0.2])
    # Define voxel
    voxel = g4py.geo.volume.Volume(name="voxel"+"_" + str(lab),
                                    primitive=voxPrimitive,
                                    material=materialLookup(HU,voxNum),
                                    sensitive=True,
                                    color=voxColor,
                                    parent=dummy,
                                    translation=[x,y,z],
                                    rotation=None)




    return dummy
