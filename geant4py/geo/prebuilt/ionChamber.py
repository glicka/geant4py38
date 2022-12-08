import geant4py as g4py
import numpy as np

def ionChamber(name, copies=1, indices=[""]):
    '''
    500 cm water phantom
    '''

    assert copies >= 1

    dummyDim = {"inner_rad": [0, 'mm'], "outer_rad": [100+0.1, 'mm'], "height": [100+0.1, 'mm'],'sPhi':[0,'deg'],'dPhi':[360,'deg']}
    dummyPrimitive = g4py.geo.primitive.Cylinder('boxDummy', dummyDim)
    dummyMaterial = g4py.geo.material.Vacuum()
    dummyColor = None#np.array([0.2, 0.2, 0.2, 0.2])#*10

    # Setting up aluminum casing
    icDim = {"inner_rad": [0, 'mm'], "outer_rad": [100, 'mm'], "height": [100, 'mm'],'sPhi':[0,'deg'],'dPhi':[360,'deg']}
    icPrimitive = g4py.geo.primitive.Cylinder('ionChamber', icDim)
    icMaterial = g4py.geo.material.Air()
    icColor = [-1, 4, 1, 1]


    # Creating and placing volumes
    vol = np.empty(copies, dtype=object)
    for i in range(copies):
        dummy = g4py.geo.volume.Volume(name=name+"_"+str(i),
                                       primitive=dummyPrimitive,
                                       material=dummyMaterial,
                                       sensitive=False,
                                       color=dummyColor,
                                       parent=None,
                                       translation=None,
                                       rotation=None)

        ic = g4py.geo.volume.Volume(name="ic"+"_"+str(i),
                                        primitive=icPrimitive,
                                        material=icMaterial,
                                        sensitive=True,
                                        color=icColor,
                                        parent=dummy,
                                        translation=None,
                                        rotation=None)
        vol[i] = dummy


    if copies > 1: return vol
    else: return vol[0]
