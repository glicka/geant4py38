from Geant4 import gApplyUICommand
import numpy as np
import os
import geant4py as g4py

PATH = os.getenv('HOME') + '/repos/geant4py/'
vis_path = os.getcwd()
def setup_vis(vis_driver):
    '''Configure visualization'''

    if vis_driver is not None:

        if np.char.lower(vis_driver) == 'oglsx':
            gApplyUICommand('/tracking/verbose 0')
            gApplyUICommand('/vis/verbose 0')
            gApplyUICommand('/vis/open OGLSX 1000x1000-0+50')
            gApplyUICommand('/vis/drawVolume')
            gApplyUICommand('/vis/scene/add/axes 0 0 0 20 cm')
            gApplyUICommand('/vis/viewer/set/viewpointThetaPhi 90 0')
            gApplyUICommand('/vis/viewer/zoom 0.5')
            gApplyUICommand('/vis/viewer/set/hiddenEdge 0')
            gApplyUICommand('/vis/scene/add/trajectories')
            gApplyUICommand('/vis/scene/endOfEventAction accumulate')

        elif np.char.lower(vis_driver) == 'raytracer':

            if not os.path.exists('raytrace'):
                os.makedirs('raytrace')

            gApplyUICommand('/vis/open RayTracer')
            gApplyUICommand('/vis/viewer/set/upVector 0 0 1')
            gApplyUICommand('/vis/rayTracer/headAngle 0')
            gApplyUICommand('/vis/rayTracer/eyePosition 100 0 0 cm')
            gApplyUICommand('/vis/rayTracer/trace raytrace/world_x.jpg')
            gApplyUICommand('/vis/rayTracer/headAngle 0')
            gApplyUICommand('/vis/rayTracer/eyePosition 0 100 0 cm')
            gApplyUICommand('/vis/rayTracer/trace raytrace/world_y.jpg')
            gApplyUICommand('/vis/rayTracer/headAngle 0')
            gApplyUICommand('/vis/rayTracer/eyePosition 0 0 100  cm')
            gApplyUICommand('/vis/rayTracer/trace raytrace/world_z.jpg')

        elif np.char.lower(vis_driver) == 'heprep':

            if not os.path.exists('visualization'):
                os.makedirs('visualization')

            gApplyUICommand('/vis/open HepRepFile')
            gApplyUICommand('/vis/scene/create')
            gApplyUICommand('/vis/scene/add/volume')
            gApplyUICommand('/vis/sceneHandler/attach')
            gApplyUICommand('/vis/viewer/flush')
            gApplyUICommand('/vis/scene/add/trajectories')
            gApplyUICommand('/vis/scene/add/hits')
            gApplyUICommand('/tracking/storeTrajectory 1')
            gApplyUICommand('/vis/scene/endOfEventAction accumulate')
            gApplyUICommand('/run/beamOn 50')
            gApplyUICommand('/vis/viewer/update')

            heprep_file = g4py.core.Fix_heprep('G4Data0.heprep',
                                       'geant4py/core/header_file.heprep',
                                     'geometry.heprep')
            heprep_file.cleaned_heprep_file()
            '''
            The below line deletes the raw heprep file. Comment this line out
            if you want the original heprep file.
            The file is then renamed and moved into the visualization folder
            '''
            os.remove("G4Data0.heprep")
            os.rename("geometry.heprep",
                      vis_path+"/visualization/geometry.heprep")

            event_files = g4py.core.Event_heprep('G4Data1.heprep',
                                       'geant4py/core/header_file.heprep',
                                       'event_data.heprep')
            event_files.cleaned_heprep_file()

            # Removes all the generated heprep files
            # Move the event_data into visualization
            os.remove('G4Data1.heprep')
            os.remove('G4Data2.heprep')
            os.rename("event_data.heprep",
                      vis_path+"/visualization/event_data.heprep")

        elif np.char.lower(vis_driver) == 'vrml':
            gApplyUICommand('/tracking/verbose 0')
            gApplyUICommand('/vis/verbose 0')
            gApplyUICommand('/vis/open VRML2FILE')
            gApplyUICommand('/vis/drawVolume')
            gApplyUICommand('/vis/scene/add/axes 0 0 0 20 cm')
            gApplyUICommand('/vis/viewer/set/viewpointThetaPhi 45 45')
            gApplyUICommand('/vis/viewer/zoom 1')
            gApplyUICommand('/vis/viewer/set/hiddenEdge 1')
            gApplyUICommand('/vis/scene/add/trajectories')
            gApplyUICommand('/vis/scene/endOfEventAction accumulate')

        else:
            raise Exception("Visualization driver unrecognized")
