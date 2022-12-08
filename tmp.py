#!/usr/bin/env python
import numpy as np
#from multiprocessing import Pool, cpu_count, Array
from pathos.threading import cpu_count, ThreadPool
import geant4py as g4py
import pydicom as dm
import glob
import os
import pyg4ometry as g4o

global dummy,x,y,z

def fillArray(i):
    global dummy, PixelSpacing,x,y,z
    print('in func')

    print('dummy daughters = ', dummy.logical.GetNoDaughters())
    voxDim = {"x": [PixelSpacing[0] , 'mm'],
     "y": [PixelSpacing[1], 'mm'],
     "z": [PixelSpacing[2], 'mm']}
    voxPrimitive = g4py.geo.primitive.BoxSolid('voxDummy', voxDim)
    voxColor = np.array([0.2, 0.2, 0.2, 0.2])
    lab = i*PixelDims[0]*PixelDims[1] + PixelDims[1]*(i+200) + i
    voxel = g4py.geo.volume.Volume(name="voxel"+"_" + str(lab),
                                    primitive=voxPrimitive,
                                    material=g4py.geo.material.Air(lab),
                                    sensitive=True,
                                    color=voxColor,
                                    parent=dummy,
                                    translation=[x[i],y[i],z[i]],
                                    rotation=None)
    print('dummy daughters = ', dummy.logical.GetNoDaughters())
    return
dicomFolder='{}/geant4py38/geant4py/geo/Mouse for MC/CT'.format(os.path.expanduser('~'))
dcmFils = sorted(glob.glob('{}*.dcm'.format(dicomFolder)))

# Get ref file
RefDs = dm.read_file(dcmFils[0])
# Load dimensions based on the number of rows, columns, and slices (along the Z axis)
PixelDims = [int(RefDs.Rows), int(RefDs.Columns), len(dcmFils)]
#PixelDims = (int(RefDs.Rows), int(RefDs.Columns), 1)
# Load spacing values (in mm)
PixelSpacing = [float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]), float(RefDs.SliceThickness)]

# can aribitrarily set ArrayDicom[0] as positive or negative, so we instead
# set origin at center of DICOM in mm
z = np.linspace(-len(dcmFils)/2.*PixelSpacing[2],len(dcmFils)/2.*PixelSpacing[2],len(dcmFils))
y = np.linspace(-len(dcmFils)/2.*PixelSpacing[1],len(dcmFils)/2.*PixelSpacing[1],len(dcmFils))
x = np.linspace(-len(dcmFils)/2.*PixelSpacing[0],len(dcmFils)/2.*PixelSpacing[0],len(dcmFils))

dummyDim = {"x": [PixelSpacing[0]*PixelDims[0]+1*PixelSpacing[0]*PixelDims[0] , 'mm'],
 "y": [PixelSpacing[1]*PixelDims[1]+0.05*PixelSpacing[1]*PixelDims[1], 'mm'],
 "z": [PixelSpacing[2]*PixelDims[2]+0.05*PixelSpacing[2]*PixelDims[2], 'mm']}
dummyPrimitive = g4py.geo.primitive.BoxSolid('boxDummy', dummyDim)
dummyMaterial = g4py.geo.material.Vacuum('dummy')
dummyColor = g4py.geo.colors.red()
dummy = g4py.geo.volume.Volume(name='dummy',
                               primitive=dummyPrimitive,
                               material=dummyMaterial,
                               sensitive=False,
                               color=dummyColor,
                               parent=None,
                               translation=None,
                               rotation=None)
'''
Convert dummy class to GDML
'''

dummy = g4py.geo.gdml.GDML(name='dummy',
                           physical=dummy.physical,
                           color=dummyColor,
                           parent=None,
                           translation=None,
                           rotation=None)
arr = np.array([])
pool = ThreadPool(1)#Pool(cpu_count())
print('cpus = ',cpu_count())
print('pool = ',pool)
res = pool.map(fillArray,np.arange(0,100,1))
print('dummy = ',dummy)
print(dummy.logical.GetNoDaughters())
#pool.close()
