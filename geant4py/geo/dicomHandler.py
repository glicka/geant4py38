import numpy as np
import Geant4 as g4
import glob
import geant4py as g4py
import pydicom as dm
from multiprocessing import Pool, cpu_count
#import pyg4ometry as g4o
import os
import itertools
from multiprocessing import sharedctypes
from concurrent.futures import ThreadPoolExecutor as tpe

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

class dicom():
    def __init__(self):
        dummyDim = {"x": [0.1 , 'm'],
         "y": [0.1, 'm'],
         "z": [0.1, 'm']}
        #print('Dummy Dim: ',dummyDim)
        dummyPrimitive = g4py.geo.primitive.BoxSolid('boxDummy', dummyDim)
        dummyMaterial = g4py.geo.material.Vacuum()#.Bone(1.3,1513)
        #dummyMaterial = g4py.geo.material.SoftTissue(1.0,0)
        dummyColor = np.array([2, -1, -0.2, 0.8])#*10
        self.dummy = g4py.geo.volume.Volume(name='init',
                                       primitive=dummyPrimitive,
                                       material=dummyMaterial,
                                       sensitive=False,
                                       color=dummyColor,
                                       parent=None,
                                       translation=None,
                                       rotation=None)





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

    def generateSlice(self,slice,sliceNum,PixelDims,PixelSpacing):
        print('in slice')
        print('slice = ',sliceNum)

        xPos = np.linspace(-PixelSpacing[0]/2.*PixelDims[0],PixelSpacing[0]/2.*PixelDims[0],PixelDims[0])
        yPos = np.linspace(-PixelSpacing[1]/2.*PixelDims[1],PixelSpacing[1]/2.*PixelDims[1],PixelDims[1])
        zPos = np.linspace(-PixelSpacing[2]/2.*PixelDims[2],PixelSpacing[2]/2.*PixelDims[2],PixelDims[2])
        dummyDim = {"x": [PixelSpacing[0]*PixelDims[0] , 'mm'],
         "y": [PixelSpacing[1]*PixelDims[1], 'mm'],
         "z": [PixelSpacing[2], 'mm']}
        print('Dummy Dim: ',dummyDim)

        dummyPrimitive = g4py.geo.primitive.BoxSolid('boxDummy', dummyDim)
        dummyMaterial = g4py.geo.material.Vacuum()#.Bone(1.3,1513)
        #dummyMaterial = g4py.geo.material.SoftTissue(1.0,0)
        dummyColor = np.array([2, -1, -0.2, 0.8])#*10
        sliceName = 'slice' + '_' + str(sliceNum)
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
        print('voxDim = ', voxDim)

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
                                                parent=None,
                                                translation=[x,y,zPos[sliceNum]],
                                                rotation=None)

        print('saving slice {}...'.format(sliceNum))
        gdml_parser = g4.G4GDMLParser()
        gdmlName="{}/geant4py38/geant4py/geo/gdml/{}.gdml".format(os.path.expanduser('~'),sliceName)
        gdml_parser.Write("{}".format(gdmlName), patientGeo.get_physical())
        print('slice {} saved!')

    def convertToG4Voxels(self,dicomArray,PixelSpacing,PixelDims,name,coarseness):
        print('in convertToG4Voxels')

        '''
        Define x,y,z coordinates for DICOM
        '''
        xPos = np.linspace(-PixelSpacing[0]/2.*PixelDims[0],PixelSpacing[0]/2.*PixelDims[0],PixelDims[0])
        yPos = np.linspace(-PixelSpacing[1]/2.*PixelDims[1],PixelSpacing[1]/2.*PixelDims[1],PixelDims[1])
        zPos = np.linspace(-PixelSpacing[2]/2.*PixelDims[2],PixelSpacing[2]/2.*PixelDims[2],PixelDims[2])
        '''
        Include hard-coded cuts to DICOM file to simplify geometry
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

        #print('xPos = ',xPos[PixelDims[0]/2])
        '''
        Set up parents for DICOM as vacuum w/ size of whole slice
        '''
        """
        print('total dims x: ',PixelSpacing[0]*PixelDims[0]+0.05*PixelSpacing[0]*PixelDims[0])
        dummyDim = {"x": [PixelSpacing[0]*PixelDims[0]+1*PixelSpacing[0]*PixelDims[0] , 'mm'],
         "y": [PixelSpacing[1]*PixelDims[1]+0.05*PixelSpacing[1]*PixelDims[1], 'mm'],
         "z": [PixelSpacing[2]*PixelDims[2]+0.05*PixelSpacing[2]*PixelDims[2], 'mm']}
        print('Dummy Dim: ',dummyDim)
        """
        print(x1)
        print(x2)
        print('x2-x1 = ',x2-x1)
        print('PixelDims = ', PixelDims)
        print('PixelDims[0] = ', PixelDims[0])
        PixelDims[0] = x2-x1
        PixelDims[1] = y2-y1
        PixelDims[2] = zRange[1] - zRange[0]
        print('total dims x: ',PixelSpacing[0]*PixelDims[0]+0.05*PixelSpacing[0]*PixelDims[0])
        dummyDim = {"x": [PixelSpacing[0]*PixelDims[0]+1*PixelSpacing[0]*PixelDims[0] , 'mm'],
         "y": [PixelSpacing[1]*PixelDims[1]+0.05*PixelSpacing[1]*PixelDims[1], 'mm'],
         "z": [PixelSpacing[2]*PixelDims[2]+0.05*PixelSpacing[2]*PixelDims[2], 'mm']}
        #print('Dummy Dim: ',dummyDim)
        dummyPrimitive = g4py.geo.primitive.BoxSolid('boxDummy', dummyDim)
        dummyMaterial = g4py.geo.material.Vacuum()#.Bone(1.3,1513)
        #dummyMaterial = g4py.geo.material.SoftTissue(1.0,0)
        dummyColor = np.array([2, -1, -0.2, 0.8])#*10
        """
        dummy = g4py.geo.volume.Volume(name=name+'_0',
                                       primitive=dummyPrimitive,
                                       material=dummyMaterial,
                                       sensitive=False,
                                       color=dummyColor,
                                       parent=None,
                                       translation=None,
                                       rotation=None)
        """
        self.dummy.solid = dummyPrimitive
        self.dummy.name = name
        self.dummy.material = dummyMaterial
        print('dummy material = ', g4.G4String(self.dummy.name))

        #sdummy = sharedctypes.RawArray(dummy._type_, dummy)

        '''
        Set up voxel dimensions
        '''
        voxDim = {"x": [PixelSpacing[0]*coarseness , 'mm'],
         "y": [PixelSpacing[1]*coarseness, 'mm'],
         "z": [PixelSpacing[2]*coarseness, 'mm']}
        #print('voxDim = ', voxDim)

        voxPrimitive = g4py.geo.primitive.BoxSolid('voxDummy', voxDim)
        voxColor = np.array([0.2, 0.2, 0.2, 0.2])


        '''
        Define and place voxels
        '''
        '''
        To do: parallelize this process...
        '''
        """
        for i in range(0,PixelDims[2],coarseness):
            for k in range(0,50,coarseness):
                for j in range(0,50,coarseness):
        """
        """
        dsLab = 0

        #for i in range(0,PixelDims[2],coarseness):
        #    for k in range(0,PixelDims[0],coarseness):
        #        for j in range(0,PixelDims[1],coarseness):
        for i in range(zRange[0],zRange[1],coarseness):
            for k in range(xRange[0],xRange[1],coarseness):
                for j in range(yRange[0],yRange[1],coarseness):
                    slice = dicomArray[i:(i+coarseness),k:(k+coarseness),j:(j+coarseness)]
                    if coarseness > 1:
                        try:
                            x = xPos[k] + PixelSpacing[0]*coarseness/2 #- PixelSpacing[0]/2.
                        except:
                            differential = (xPos[-1] - xPos[k])/2.
                            x = xPos[k] + differential
                        #print('xPos = ',x)
                        try:
                            y = yPos[j] + PixelSpacing[1]*coarseness/2#+coarseness/2] #- PixelSpacing[1]/2.
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
                        #tot = (PixelDims[1]*1./coarseness)*(PixelDims[0]*1./coarseness)*(PixelDims[2]*1./coarseness)
                        tot = ((yRange[1]-yRange[0])*1./coarseness)*((xRange[1]-xRange[0])*1./coarseness)*((zRange[1]-zRange[0])*1./coarseness)
                        num = dsLab#PixelDims[1]*k + j
                        percent = num * 100./tot
                        print('{}% Done'.format(percent))
                #if (j+1)%100 == 0:
                #    break
            #if (k+1)%100 == 0:
            #    break

            #if i == 1:
                #break


        """
        '''
        Current attempt at parallelizing:
        '''
        """
        i = 0
        for slice in dicomArray:
            '''
            sliceNum = i
            with tpe(max_workers=cpu_count()) as executor:
                executor.submit(placeVoxels, [[slice,sliceNum,rowNum,PixelDims] for rowNum in range(PixelDims[0])])
            '''
            pool = Pool(processes = cpu_count())

            pool.apply_async(placeVoxels, [[slice,sliceNum,rowNum,PixelDims] for rowNum in range(PixelDims[0])])
            pool.close()

            sliceNum += 1

        """
        """
        print('dummy = ',self.dummy)
        print('')
        p = []
        pool = Pool(processes = cpu_count())
        for i in range(0,PixelDims[2],1):
            p += [pool.apply_async(self.generateSlice, [dicomArray[i],i,PixelDims,PixelSpacing])]# for i in range(0,PixelDims[2],1)]
        results = [res.get() for res in p]
        pool.close()
        for tmp in range(len(p)):
            print(tmp)

        """
        i = np.array(np.arange(0,PixelDims[2],1),dtype='int')
        pool = Pool(processes = cpu_count())
        pool.map(self.generateSlice, [dicomArray,i,PixelDims,PixelSpacing])


        return self.dummy

    def dicomHandler(self,dicomFolder,name='dicomCT',coarseness=1,gdmlName=None):
        dcmFils = sorted(glob.glob('{}*.dcm'.format(dicomFolder)))
        #print(dcmFils)

        # Get ref file
        RefDs = dm.read_file(dcmFils[0])
        print(RefDs)
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

            This method only down samples in x and y. Need to somehow incorporate the z
            dimension (slice number) without overloading memory with multiple CT slices
            at once.
            '''
            patientGeo = self.convertToG4Voxels(ArrayDicom,PixelSpacing,PixelDims,name,coarseness)
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
