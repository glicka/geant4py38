import geant4py as g4py
import numpy as np
from Geant4 import G4GDMLParser
import os
# Get prebuilt world volume
'''
world = g4py.geo.prebuilt.world(primitive='sphere',
                                material=g4py.geo.material.Vacuum())
'''
world_primitive = g4py.geo.primitive.Sphere('world', dim={'inner_rad':[0,'m'],
                                                 'outer_rad':[50, 'm'],
                                                 'sPhi':[0,'deg'],
                                                 'dPhi':[360,'deg'],
                                                 'sTheta':[0,'deg'],
                                                 'dTheta':[180,'deg']})
world = g4py.geo.volume.Volume(name='world',
                              primitive=world_primitive,
                              material=g4py.geo.material.Vacuum(),
                              sensitive=False,
                              color=None,
                              parent=None,
                              translation=None,
                              rotation=None)
# Get prebuilt water phantom
# Set depth in mm
waterPhantom = g4py.geo.prebuilt.waterBox('phantom',icDepth=0.5)
waterPhantom.placeit(parent=world,
             translation=[0,0,-2500],
             rotation=[np.deg2rad(0),np.deg2rad(0)],
             rotationName='rotAx')

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
                     source_rad=50,
                     source_dist=100,
                     length_unit='cm',
                     random_seed=13,
                     outputfile='output/mouse2',
                     sourcedatafile='src/mouse2')

# Send to sim
run = g4py.Run(world=world,
               source=source,
               check_overlaps=False,
               track_secondaries=True, #doesn't track protons/neutrons if False
               vis_driver=None,#'oglsx',#'heprep',#None,#
               physics_list=['FTFP_BERT_LIV'],
               process_tracking = ['ioni', 'elastic'])
