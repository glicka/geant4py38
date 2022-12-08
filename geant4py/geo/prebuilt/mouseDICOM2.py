import geant4py as g4py
import numpy as np
import math as m
import os
import pydicom as dm
import glob

_HERE = os.path.dirname(os.path.abspath(__file__))

def mouseDICOM():


    dcmFils = sorted(glob.glob('C:/Users/aeglick/Documents/Python Scripts/Mouse for MC/CT*.dcm'))
    #print(dcmFils)

    # Get ref file
    RefDs = dm.read_file(dcmFils[0])
    print(RefDs)
    # Load dimensions based on the number of rows, columns, and slices (along the Z axis)
    ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), len(dcmFils))

    # Load spacing values (in mm)
    ConstPixelSpacing = (float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]), float(RefDs.SliceThickness))

    x = np.arange(0.0, (ConstPixelDims[0]+1)*ConstPixelSpacing[0], ConstPixelSpacing[0])
    y = np.arange(0.0, (ConstPixelDims[1]+1)*ConstPixelSpacing[1], ConstPixelSpacing[1])
    z = np.arange(0.0, (ConstPixelDims[2]+1)*ConstPixelSpacing[2], ConstPixelSpacing[2])

    # The array is sized based on 'ConstPixelDims'
    ArrayDicom = np.zeros(ConstPixelDims, dtype=RefDs.pixel_array.dtype)

    # loop through all the DICOM files
    for filenameDCM in dcmFils:
        # read the file
        ds = dm.read_file(filenameDCM)
        print(filenameDCM)
        # store the raw image data
        ArrayDicom[:, :, dcmFils.index(filenameDCM)] = ds.pixel_array
    # Setup dummy
    dummyDim = {'inner_rad':[0,'mm'],
                                   'outer_rad':[5,'m'],
                                   'sPhi':[0,'deg'],
                                   'dPhi':[360,'deg'],
                                   'sTheta':[0,'deg'],
                                   'dTheta':[180,'deg']}
    dummyColor = [2, 2, 2, 2]
    dummyPrimitive = g4py.geo.primitive.Sphere('dummySphere', dummyDim)
    dummyMaterial = g4py.geo.material.Vacuum()

    dummy = g4py.geo.volume.Volume(name='dummy',
                                   primitive=dummyPrimitive,
                                   material=dummyMaterial,
                                   color=None,
                                   sensitive=False,
                                   parent=None,
                                   translation=None,
                                   rotation=None)




    # Get prebuilt Water Box
    mouse = g4py.geo.volume.Volume(name='dummy',
                                   primitive=ArrayDicom,
                                   material=dummyMaterial,
                                   color=None,
                                   sensitive=False,
                                   parent=None,
                                   translation=None,
                                   rotation=None)


    return dummy
