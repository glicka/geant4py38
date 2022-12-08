from Geant4 import gApplyUICommand
import numpy as np
import os

def setup_vis(vis_driver):
    '''Configure visualization'''

    if vis_driver is not None:

        if np.char.lower(vis_driver) == 'oglsx':
            gApplyUICommand('/tracking/verbose 0')
            gApplyUICommand('/vis/verbose 0')
            gApplyUICommand('/vis/open OGLSX 1600x1600')#-0+50)
            gApplyUICommand('/vis/drawVolume')
            gApplyUICommand('/vis/scene/add/axes 0 0 0 20 cm')
            gApplyUICommand('/vis/viewer/set/viewpointThetaPhi 0 0')
            gApplyUICommand('/vis/viewer/zoom 0.5')
            gApplyUICommand('/vis/viewer/set/hiddenEdge 1')
            gApplyUICommand('/vis/scene/add/trajectories')
            gApplyUICommand('/vis/scene/endOfEventAction accumulate')
            gApplyUICommand('/vis/ogl/set/displayListLimit 500000.')

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

            gApplyUICommand('/vis/open HepRepFile')
            gApplyUICommand('/vis/scene/create')
            gApplyUICommand('/vis/scene/add/volume')
            gApplyUICommand('/vis/sceneHandler/attach')
            gApplyUICommand('/vis/viewer/flush')
            gApplyUICommand('/vis/scene/add/trajectories')
            gApplyUICommand('/vis/scene/add/hits')
            gApplyUICommand('/tracking/storeTrajectory 1')

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
