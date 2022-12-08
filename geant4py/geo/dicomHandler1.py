import numpy as np
import Geant4 as g4
import glob
import geant4py as g4py
import pydicom as dm
from multiprocessing import Pool, cpu_count
#import pyg4ometry as g4o
import os
import itertools



'''
Import DICOM data and create Geant4 Voxels based on macro data
'''

def materialLookup(HU,voxNum):
    '''
    Take HU value for a voxel and returns the material
    '''
    if HU < -974:
        y = [0.001,0.044]
        x = [-1024,-974]
        m,b = np.polyfit(x,y,1)
        density = m*HU + b
        return g4py.geo.material.AirCavity(density,voxNum)
    elif HU >= -974 and HU < -100:
        y = [0.044,0.302]
        x = [-974,-100]
        m,b = np.polyfit(x,y,1)
        density = m*HU + b
        return g4py.geo.material.Lung(density,voxNum)
    elif HU >= -100 and HU < 180:
        y = [0.302,1.101]
        x = [-100,180]
        m,b = np.polyfit(x,y,1)
        density = m*HU + b
        return g4py.geo.material.SoftTissue(density,voxNum)
    elif HU >= 180 and HU < 2488:
        y = [1.101,2.088]
        x = [180,1976]
        m,b = np.polyfit(x,y,1)
        density = m*HU + b
        return g4py.geo.material.Bone(density,voxNum)
    elif HU >= 2488 and HU < 3050:
        return g4py.geo.material.PMMA(voxNum)
    elif HU >= 3050 and HU < 3150:
        return g4py.geo.material.element('Al')
    elif HU >= 3150:
        return g4py.geo.material.Steel(voxNum)

def loadScan(slices):
    slices.sort(key = lambda x: int(x.InstanceNumber))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    for s in slices:
        s.SliceThickness = slice_thickness
    return slices

def getPixelHU(scans):
    image = np.stack([s.pixel_array for s in scans])
    image = image.astype(np.int16)
    # Set outside-of-scan pixels to 0
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0

    # Convert to Hounsfield units (HU)
    intercept = scans[0].RescaleIntercept
    slope = scans[0].RescaleSlope
    print('slope = ', slope)
    print('intercept = ',intercept)
    if slope != 1:
        image = slope * image.astype(np.float64)
        image = image.astype(np.int16)

    image += np.int16(intercept)
    image = image #* m + b
    return np.array(image, dtype=np.int16)



def placeVoxels(slice,sliceNum,rowNum,PixelDims):
    for pixNum in range(PixelDims[1]):
        '''
        To do: parallelize this process...
        '''
        x = xPos[rowNum]
        y = yPos[pixNum]
        z = zPos[sliceNum]
        lab = sliceNum*PixelDims[0]*PixelDims[1] + PixelDims[1]*rowNum + pixNum
        voxel = g4py.geo.volume.Volume(name="voxel"+"_" + str(lab),
                                        primitive=voxPrimitive,
                                        material=materialLookup(slice[rowNum,pixNum],lab),
                                        sensitive=True,
                                        color=voxColor,
                                        parent=dummy,
                                        translation=[x,y,z],
                                        rotation=None)
        if lab%int(5e3) == 0:
            tot = PixelDims[1]*PixelDims[0]
            num = PixelDims[1]*k + j
            percent = num * 100./tot
            print('{}% Done'.format(percent))

def generateSlice(slice,sliceNum,PixelDims,PixelSpacing):
    sliceName = 'slice' + '_' + str(sliceNum)
    try:
        '''
        Check if slice has already been generated
        '''
        gdmlName="{}/geant4py38/geant4py/geo/gdml/{}.gdml".format(os.path.expanduser('~'),sliceName)

        '''
        If slice does not exist, create it
        '''
        if not os.path.isfile(gdmlName):

            xPos = np.linspace(-PixelSpacing[0]/2.*PixelDims[0],PixelSpacing[0]/2.*PixelDims[0],PixelDims[0])
            yPos = np.linspace(-PixelSpacing[1]/2.*PixelDims[1],PixelSpacing[1]/2.*PixelDims[1],PixelDims[1])
            zPos = np.linspace(-PixelSpacing[2]/2.*PixelDims[2],PixelSpacing[2]/2.*PixelDims[2],PixelDims[2])
            dummyDim = {"x": [PixelSpacing[0]*PixelDims[0] , 'mm'],
             "y": [PixelSpacing[1]*PixelDims[1], 'mm'],
             "z": [PixelSpacing[2], 'mm']}


            dummyPrimitive = g4py.geo.primitive.BoxSolid('boxDummy', dummyDim)
            dummyMaterial = g4py.geo.material.Vacuum(sliceName)
            dummyColor = np.array([2, -1, -0.2, 0.8])

            sliceVoxelized = g4py.geo.volume.Volume(name=sliceName,
                                           primitive=dummyPrimitive,
                                           material=dummyMaterial,
                                           sensitive=False,
                                           color=dummyColor,
                                           parent=None,
                                           translation=[0,0,zPos[sliceNum]],
                                           rotation=None)

            '''
            Set up voxel dimensions
            '''
            voxDim = {"x": [PixelSpacing[0] , 'mm'],
             "y": [PixelSpacing[1], 'mm'],
             "z": [PixelSpacing[2], 'mm']}

            voxPrimitive = g4py.geo.primitive.BoxSolid('voxDummy', voxDim)
            voxColor = np.array([0.2, 0.2, 0.2, 0.2])
            for k in range(0,PixelDims[0],1):
                for j in range(0,PixelDims[1],1):
                    lab = sliceNum*PixelDims[0]*PixelDims[1] + PixelDims[1]*k + j

                    x = xPos[k]
                    y = yPos[j]




                    #lab = (i+coarseness/2)*PixelDims[0]*PixelDims[1] + PixelDims[1]*(k+coarseness/2) + (j+coarseness/2)
                    #dsLab += 1
                    HU = slice[k,j]
                    voxel = g4py.geo.volume.Volume(name="voxel"+"_" + str(lab),
                                                    primitive=voxPrimitive,
                                                    material=materialLookup(HU,lab),#materialLookup(slice[k,j],lab),
                                                    sensitive=True,
                                                    color=voxColor,
                                                    parent=sliceVoxelized,
                                                    translation=[x,y,zPos[sliceNum]],
                                                    rotation=None)

            #print('saving slice {}...'.format(sliceNum))
            gdml_parser = g4.G4GDMLParser()
            gdml_parser.Write("{}".format(gdmlName), sliceVoxelized.get_physical())
        '''
        If slice exists or is generated, return 0
        '''
        return 0
    except:
        '''
        If slice cannot be loaded/generated, return 1
        '''
        return 1
    #print('slice {} saved!')


def convertToG4Voxels(dicomArray,PixelSpacing,PixelDims,name,coarseness):

    '''
    Define x,y,z coordinates for DICOM
    '''
    xPos = np.linspace(-PixelSpacing[0]/2.*PixelDims[0],PixelSpacing[0]/2.*PixelDims[0],PixelDims[0])
    yPos = np.linspace(-PixelSpacing[1]/2.*PixelDims[1],PixelSpacing[1]/2.*PixelDims[1],PixelDims[1])
    zPos = np.linspace(-PixelSpacing[2]/2.*PixelDims[2],PixelSpacing[2]/2.*PixelDims[2],PixelDims[2])

    '''
    Include hard-coded cuts to DICOM file to simplify geometry.
    Cuts created by observing where the object of interest is
    in the image.
    '''
    idx = (abs(xPos+14)).argmin()
    x1 = idx
    idx = (abs(xPos-14)).argmin()
    x2 = idx
    idx = (abs(yPos+10)).argmin()
    y1 = idx
    idx = (abs(yPos-10)).argmin()
    y2 = idx

    xRange = [x1,x2]
    yRange = [y1,y2]
    zRange = [30,230]
    zSlice = [zPos[30],zPos[230]]

    PixelDims[0] = x2-x1
    PixelDims[1] = y2-y1
    PixelDims[2] = zRange[1] - zRange[0]
    #print('xPos = ',xPos[PixelDims[0]/2])
    '''
    Set up parent for DICOM as vacuum w/ size of whole patient DICOM
    '''
    dummyDim = {"x": [PixelSpacing[0]*PixelDims[0]+1*PixelSpacing[0]*PixelDims[0] , 'mm'],
     "y": [PixelSpacing[1]*PixelDims[1]+0.05*PixelSpacing[1]*PixelDims[1], 'mm'],
     "z": [PixelSpacing[2]*PixelDims[2]+0.05*PixelSpacing[2]*PixelDims[2], 'mm']}
    #print('Dummy Dim: ',dummyDim)
    dummyPrimitive = g4py.geo.primitive.BoxSolid('boxDummy', dummyDim)
    dummyMaterial = g4py.geo.material.Vacuum(name)
    dummyColor = g4py.geo.colors.red(),
    dummy = g4py.geo.volume.Volume(name=name,
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
    dummy = g4py.geo.gdml.GDML(name=name,
                               physical=dummy.physical,
                               color=dummyColor,
                               parent=None,
                               translation=None,
                               rotation=None)
    '''
    ...
    Parallelize creation of individual 3D slices
    ...
    Slices are the parent geometry of individual voxels which are generated and
    placed in `generateSlice`. Cannot pass Geant4 objects through pool, so
    intermediate step of saving as GDML files is done instead.
    '''
    p = []
    pool = Pool(processes = cpu_count())
    for i in range(0,PixelDims[2],1):
        p += [pool.apply_async(generateSlice, [dicomArray[i],i,PixelDims,PixelSpacing])]# for i in range(0,PixelDims[2],1)]
    results = np.array([res.get() for res in p])
    pool.close()
    '''
    Check that all slices return 0 as a result
    '''
    if not np.any(results):
        print('success!')
        for i in range(PixelDims[2]):
            '''
            Open up slice files one at a time. Add to parent geometry. Remove
            slice file.
            '''
            sliceName = 'slice' + '_' + str(i)
            sliceGDML = "{}/geant4py38/geant4py/geo/gdml/{}.gdml".format(os.path.expanduser('~'),sliceName)
            gdml_parser = g4.G4GDMLParser()
            gdml_parser.Read(sliceGDML)
            world = gdml_parser.GetWorldVolume()
            patientGeo = g4py.geo.gdml.GDML(name=sliceName, physical=world, color=g4py.geo.colors.blue(),
                               parent=dummy, sensitive=True, userinfo=None, translation=None, rotation=None, rotationName=None)
            os.remove(sliceGDML)

    '''
    Return parent geometry
    '''
    return dummy

def dicomHandler(dicomFolder,name='dicomCT',coarseness=1,gdmlName=None):
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
    zPos = np.linspace(-len(dcmFils)/2.*PixelSpacing[2],len(dcmFils)/2.*PixelSpacing[2],len(dcmFils))
    yPos = np.linspace(-len(dcmFils)/2.*PixelSpacing[1],len(dcmFils)/2.*PixelSpacing[1],len(dcmFils))
    xPos = np.linspace(-len(dcmFils)/2.*PixelSpacing[0],len(dcmFils)/2.*PixelSpacing[0],len(dcmFils))

    if gdmlName is None:
        # The array is sized based on 'PixelDims'
        ArrayDicom = np.zeros(PixelDims, dtype=RefDs.pixel_array.dtype)
        slices = []

        # loop through all the DICOM files and convert to HU
        for filenameDCM in dcmFils:
            # read the file
            ds = dm.read_file(filenameDCM)
            # store the file
            slices.append(ds)

        # unpack all slices
        ArrayDicom = getPixelHU(loadScan(slices))


        '''
        To do:

        Down sample the CT data by creating larger regions that average the CT
        data HU values. Must be something that evenly divides 255 x 255.

        Current thought process:

        Input a down sampling value (i.e. 5) and pass it to `convertToG4Voxels`. In
        this function, make k = np.arange(0,PixelDims[0],downSampleVal) and
        j = np.arange(0,PixelDims[0],downSampleVal).

        Problem:

        This method only seems to work with certain values of the downSampleVal
        parameter. May require further investigation into the placement of the
        new voxel.
        '''
        patientGeo = convertToG4Voxels(ArrayDicom,PixelSpacing,PixelDims,name,coarseness)
        '''
        w = g4o.gdml.Writer()
        w.addDetector(patientGeo)
        w.write('~/geant4py38/geant4py/geo/gdml/{}.gdml'.format(name))
        '''
        gdml_parser = g4.G4GDMLParser()
        gdmlName="{}/geant4py38/geant4py/geo/gdml/{}.gdml".format(os.path.expanduser('~'),name)
        gdml_parser.Write("{}".format(gdmlName), patientGeo.get_physical())
    else:
        gdml_parser = g4.G4GDMLParser()
        gdml_parser.Read(gdmlName)
        world = gdml_parser.GetWorldVolume()
        print('world = ',g4.G4String(world.GetLogicalVolume().GetName()))
        print('num child = ', world.GetLogicalVolume().GetNoDaughters())
        patientGeo = g4py.geo.gdml.GDML(name=name, physical=world, color=[0,0,0,1],
                           parent=None, userinfo=None, translation=None, rotation=None, rotationName=None)
    #w.writeGmadTester('{}.gmad'.format(name),'{}.gdml'.format(name))
        print('num child = ', patientGeo.get_logical().GetNoDaughters())
    return patientGeo
