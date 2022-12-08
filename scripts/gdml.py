import geant4py as g4py
import numpy as np
import Geant4 as g4
import os

world = g4py.geo.prebuilt.world('sphere', g4py.material.Air(), extent=[5, 'm'])

"""
Get Mobetron head
*** must set `parent=None` or else duplicate volumes created ***
"""
gdmlParser = G4GDMLParser()
gdmlParser.Read('geant4py/geo/gdml/temptest.gdml')
mob = gdmlParser.GetWorldVolume()
mobetron = g4py.geo.gdml.GDML(name='Mobetron',
                         physical=mob,
                         color=[0,0,1,1],
                         parent=None,
                         sensitive=False)
"""
Place the object inside the world
*** must set `parent=world` to generate physical volume ***
"""
mobetron.placeit(parent=world,
                    translation=[0,0,100],
                    rotation=None)

"""
Create or load dicom geometry from .dcm or .gdml file.

Dicom Handler based on DICOM examples in GEANT4 folder.

def dicomHandler(dicomFolder,name='dicomCT',coarseness=1,gdmlName=None)

If gdmlName == None ---> create dicom geometry and save a .gdml file

If gdmlName != None ---> load dicom geometry from .gdml file


Notes: DICOM ***must*** be calibrated from -1000 (air) to +3200 (steel)
"""

"""
mouse = g4py.geo.dicomHandler.dicom()
print(mouse)
mouse = mouse.dicomHandler(dicomFolder='{}/geant4py38/geant4py/geo/Mouse for MC/CT'.format(os.path.expanduser('~')),
                                            name='mouseCTCuts',coarseness=1)#,
                                            #gdmlName="{}/geant4py38/geant4py/geo/gdml/dicomCT.gdml".format(os.path.expanduser('~')))
"""
mouse = g4py.geo.dicomHandler2.dicomHandler(dicomFolder='{}/geant4py38/geant4py/geo/Mouse for MC/CT'.format(os.path.expanduser('~')),
                                            name='mouseCTCuts',coarseness=1,
                                            gdmlName="{}/geant4py38/geant4py/geo/gdml/mouseCTCuts.gdml".format(os.path.expanduser('~')))

"""
Place the object inside the world
*** must set `parent=world` to generate physical volume ***
"""
mouse.placeit(parent=world,
              translation=[0,0,-100],
              rotation=None)
# Setup source
source = g4py.Source(field='near',
                     particle='e-',
                     energyDist = 'gauss',
                     energy=10,#[0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10],
                     minE=0.5,
                     maxE=15,
                     energy_unit='MeV',
                     direction=[0,0], #should be nside if direction_type is healpix
                     direction_type='angle',
                     num_particles=int(4e6),
                     source_rad=5,
                     source_dist=100,
                     length_unit='cm',
                     random_seed=13,
                     outputfile='output/mouse',
                     sourcedatafile='src/mouse')

# Send to sim
run = g4py.Run(world=world,
               source=source,
               check_overlaps=False,
               track_secondaries=True, #doesn't track protons/neutrons if False
               vis_driver=None,#'oglsx',#'heprep',#None,#
               physics_list=['FTFP_BERT_LIV'],
               process_tracking = ['ioni', 'elastic'])
