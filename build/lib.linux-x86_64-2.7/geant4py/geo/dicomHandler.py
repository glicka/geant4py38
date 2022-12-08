import numpy as np
import Geant4 as g4
import glob
import geant4py as g4py
import pydicom as dm
from multiprocessing import Pool, cpu_count

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

def placeVoxels(sliceNum,rowNum,PixelDims,parent):
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

def convertToG4Voxels(dicomArray,PixelSpacing,PixelDims,name,coarseness):
    '''
    Define x,y,z coordinates for DICOM
    '''
    xPos = np.linspace(-PixelSpacing[0]/2.*PixelDims[0],PixelSpacing[0]/2.*PixelDims[0],PixelDims[0])
    yPos = np.linspace(-PixelSpacing[1]/2.*PixelDims[1],PixelSpacing[1]/2.*PixelDims[1],PixelDims[1])
    zPos = np.linspace(-PixelSpacing[2]/2.*PixelDims[2],PixelSpacing[2]/2.*PixelDims[2],PixelDims[2])
    print('xPos = ',xPos[PixelDims[0]/2])
    '''
    Set up parents for DICOM as vacuum w/ size of whole slice
    '''
    print('total dims x: ',PixelSpacing[0]*PixelDims[0]+0.05*PixelSpacing[0]*PixelDims[0])
    print('x0 = ',xPos[0])
    dummyDim = {"x": [PixelSpacing[0]*PixelDims[0]+1*PixelSpacing[0]*PixelDims[0] , 'mm'],
     "y": [PixelSpacing[1]*PixelDims[1]+0.05*PixelSpacing[1]*PixelDims[1], 'mm'],
     "z": [PixelSpacing[2]*PixelDims[2]+0.05*PixelSpacing[2]*PixelDims[2], 'mm']}
    print('Dummy Dim: ',dummyDim)
    dummyPrimitive = g4py.geo.primitive.BoxSolid('boxDummy', dummyDim)
    dummyMaterial = g4py.geo.material.Vacuum()#.Bone(1.3,1513)
    #dummyMaterial = g4py.geo.material.SoftTissue(1.0,0)
    dummyColor = np.array([2, -1, -0.2, 0.8])#*10
    dummy = g4py.geo.volume.Volume(name=name+'_0',
                                   primitive=dummyPrimitive,
                                   material=dummyMaterial,
                                   sensitive=True,
                                   color=dummyColor,
                                   parent=None,
                                   translation=None,
                                   rotation=None)
    '''
    Set up voxel dimensions
    '''
    voxDim = {"x": [PixelSpacing[0]*coarseness , 'mm'],
     "y": [PixelSpacing[1]*coarseness, 'mm'],
     "z": [PixelSpacing[2]*coarseness, 'mm']}
    print('voxDim = ', voxDim)

    voxPrimitive = g4py.geo.primitive.BoxSolid('voxDummy', voxDim)
    voxColor = np.array([0.2, 0.2, 0.2, 0.2])


    '''
    Define and place voxels
    '''
    '''
    To do: parallelize this process...
    '''

    dsLab = 0
    for i in range(0,PixelDims[2],coarseness):
        for k in range(0,PixelDims[0],coarseness):
            for j in range(0,PixelDims[1],coarseness):
                slice = dicomArray[i:(i+coarseness),k:(k+coarseness),j:(j+coarseness)]
                if coarseness > 1:
                    try:
                        x = xPos[k] + PixelSpacing[0]*coarseness/2 #- PixelSpacing[0]/2.
                    except:
                        differential = (xPos[-1] - xPos[k])/2.
                        x = xPos[k] + differential
                    #print('xPos = ',x)
                    try:
                        y = yPos[j] + PixelSpacing[2]*coarseness/2#+coarseness/2] #- PixelSpacing[1]/2.
                    except:
                        differential = (yPos[-1] - yPos[j])/2.
                        y = yPos[j] + differential
                    #print('yPos = ',y)
                    try:
                        z = zPos[i] + PixelSpacing[2]*coarseness/2#+coarseness/2] #- PixelSpacing[2]/2.
                    except:
                        differential = (zPos[-1] - zPos[i])/2.
                        z = zPos[i] + differential
                    #print('zPos = ',z)
                else:
                    x = xPos[k]
                    y = yPos[j]
                    z = zPos[i]
                '''
                try:
                    slice = dicomArray[i:(i+coarseness),k:(k+coarseness),j:(j+coarseness)]
                    x = xPos[k+coarseness/2] #- PixelSpacing[0]/2.
                    #print('xPos = ',x)
                    y = yPos[j+coarseness/2] #- PixelSpacing[1]/2.
                    #print('yPos = ',y)
                    z = zPos[i+coarseness/2] #- PixelSpacing[2]/2.
                    #print('zPos = ',z)
                except:
                    slice = dicomArray[i:,k:,j:]


                    differential = (xPos[-1] - xPos[k])/2.
                    x = xPos[k] + differential
                    #print('xPos = ',x)
                    y = yPos[j] + differential
                    #print('yPos = ',y)
                    z = zPos[i] + differential
                '''


                #lab = (i+coarseness/2)*PixelDims[0]*PixelDims[1] + PixelDims[1]*(k+coarseness/2) + (j+coarseness/2)
                dsLab += 1
                HU = np.mean(slice)
                voxel = g4py.geo.volume.Volume(name="voxel"+"_" + str(dsLab),
                                                primitive=voxPrimitive,
                                                material=materialLookup(HU,dsLab),#materialLookup(slice[k,j],lab),
                                                sensitive=True,
                                                color=voxColor,
                                                parent=dummy,
                                                translation=[x,y,z],
                                                rotation=None)
                if dsLab%int(1e4) == 0:
                    tot = (PixelDims[1]*1./coarseness)*(PixelDims[0]*1./coarseness)*(PixelDims[2]*1./coarseness)
                    num = dsLab#PixelDims[1]*k + j
                    percent = num * 100./tot
                    print('{}% Done'.format(percent))
            #if (j+1)%100 == 0:
            #    break
        #if (k+1)%100 == 0:
        #    break

        #if i == 1:
            #break



    '''
    Current attempt at parallelizing:
    '''
    '''
    for slice in dicomArray:
        sliceNum = i
        pool = Pool(processes = ncpus)
        pool.apply_async(placeVoxels, [[sliceNum,rowNum,PixelDims] for rowNum in range(PixelDims[0])])
        pool.close()
    '''


    return dummy

def dicomHandler(dicomFolder,name='dicomCT',coarseness=1):
    dcmFils = sorted(glob.glob('{}*.dcm'.format(dicomFolder)))
    #print(dcmFils)

    # Get ref file
    RefDs = dm.read_file(dcmFils[0])
    print(RefDs)
    # Load dimensions based on the number of rows, columns, and slices (along the Z axis)
    ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), len(dcmFils))

    # Load spacing values (in mm)
    ConstPixelSpacing = (float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]), float(RefDs.SliceThickness))

    # can aribitrarily set ArrayDicom[0] as positive or negative, so we instead
    # set origin at center of DICOM in mm
    zPos = np.linspace(-len(dcmFils)/2.*ConstPixelSpacing[2],len(dcmFils)/2.*ConstPixelSpacing[2],len(dcmFils))
    yPos = np.linspace(-len(dcmFils)/2.*ConstPixelSpacing[1],len(dcmFils)/2.*ConstPixelSpacing[1],len(dcmFils))
    xPos = np.linspace(-len(dcmFils)/2.*ConstPixelSpacing[0],len(dcmFils)/2.*ConstPixelSpacing[0],len(dcmFils))

    # The array is sized based on 'ConstPixelDims'
    ArrayDicom = np.zeros(ConstPixelDims, dtype=RefDs.pixel_array.dtype)
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

    This method only down samples in x and y. Need to somehow incorporate the z
    dimension (slice number) without overloading memory with multiple CT slices
    at once.
    '''
    patientGeo = convertToG4Voxels(ArrayDicom,ConstPixelSpacing,ConstPixelDims,name,coarseness)
    return patientGeo
