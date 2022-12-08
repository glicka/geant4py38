import Geant4 as g4
import numpy as np
import geant4py.core.primarygeneratoraction as g4PGA

class MySensitiveDetector(g4.G4VSensitiveDetector):
    "Sensitive detector"

    def __init__(self, name, process_tracking):
        g4.G4VSensitiveDetector.__init__(self, name)

        self.track_secondaries = g4.gRunManager.GetUserStackingAction().track_secondaries
        self.particle_map =  {"gamma":0, "neutron":1, "alpha":2, "e+":3, "e-":4, "C12":5, "C13":6, "C14":7, "proton":8, "Be9":9, "Be10":10, "deuteron":11, "Al27":12}
        self.process_tracking = process_tracking

    def ProcessHits(self, step, touch):

        track = step.GetTrack()
        touchable = track.GetTouchable()



        # Get interaction process name
        process = str(step.GetPostStepPoint().GetProcessDefinedStep().GetProcessName()).lower()
        #print('Process = ', process)





        # Dont track transportation process
        if process != 'transportation':
            #if process.find("ioni") != -1 or process.find("elastic") != -1:
            if (self.process_tracking is None or any(process.find(self.process_tracking[i]) != -1 for i in range(len(self.process_tracking)))):
                #int PDGcode = aStep->GetTrack()->GetDefinition()->GetPDGEncoding();
                pdgCode = step.GetTrack().GetDefinition().GetPDGEncoding()
                particle = str(step.GetTrack().GetDefinition().GetParticleName())
                #if (particle == 'neutron'):
                #try:

                pga = g4.gRunManager.GetUserPrimaryGeneratorAction()
                initialEnergy = pga.get_source().energy
                # Grab runmanager, where data is stored
                ra = g4.gRunManager.GetUserRunAction()
                self.particle_map[particle]


                # Get event ID
                evtID = g4.gRunManager.GetCurrentEvent().GetEventID()
                ea = g4.gRunManager.GetUserEventAction()

                # Get name of volume
                detID = int(str(touchable.GetVolume().GetName()).split("_")[-1])
                #print('det = ',str(touchable.GetVolume().GetName()))
                #print('event ID: ', evtID)
                material = track.GetMaterial();
                density = material.GetDensity();
                cavityVolume = (step.GetTrack().GetVolume().GetLogicalVolume().GetSolid().GetCubicVolume());
                massOfCavity = cavityVolume * density;

                mass = track.GetVolume().GetLogicalVolume().GetMass() / g4.kg




                # Energy deposition
                # If secondaries are on, use total energy deposit
                #SetKBefore(aStep->GetPreStepPoint()->GetKineticEnergy()
                kBefore = step.GetPreStepPoint().GetKineticEnergy()
                #print('kBefore = ',kBefore)
                kAfter = step.GetPostStepPoint().GetKineticEnergy()
                depE = (kBefore - kAfter) / g4.keV
                dose = depE * 1.6022e-16 / mass
                #print('dose deposited: ', dose)
                ra.cumDose += (100*dose)
                #print('cumulative dose: {} cGy'.format(ra.cumDose))
                # Get time when interaction occured
                time = step.GetPostStepPoint().GetGlobalTime() #ns




                # Get position of interaction (in world coord)
                posworld = step.GetPostStepPoint().GetPosition()




                # Get position of interaction (in local coord) (not able to get matrix when defining geometry...)
                trans = touchable.GetTranslation()
                rot = touchable.GetRotation()
                poslocal = step.GetPostStepPoint().GetPosition()
                poslocal = poslocal.transform(rot) - trans.transform(rot)



                '''
                # Append...
                ra.interaction.append(ra.process_mapping[process])
                ra.particle.append(ra.particle_mapping[particle])
                ra.eventID.append(evtID)
                ra.subeventID.append(subevtID)
                ra.time.append(time)
                ra.trackID.append(trackID)
                ra.detID.append(detID)
                ra.gx.append(posworld.x)
                ra.gy.append(posworld.y)
                ra.gz.append(posworld.z)
                ra.dx.append(poslocal.x)
                ra.dy.append(poslocal.y)
                ra.dz.append(poslocal.z)
                ra.E.append(depE)
                ra.initE.append(initialEnergy)
                '''

                # Append...

                ra.interaction.append(ra.process_mapping[process])
                ra.particle.append(ra.particle_mapping[particle])
                ra.eventID.append(evtID)
                ra.detID.append(detID)
                ra.E.append(depE)
                ra.time.append(time)
                ra.initE.append(initialEnergy)
                ra.dose.append(dose)
                ra.dx.append(poslocal.x)
                ra.dy.append(poslocal.y)
                ra.dz.append(poslocal.z)




                '''
                except:
                    print('particle not accounted for')
                    print('particle = ', particle)
                    print('process = ', process)
                '''
