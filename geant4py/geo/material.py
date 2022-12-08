import Geant4 as g4
import numpy as np
import os

'''
Define materials here. GEANT materials can be included as:

def geantPrebuiltMaterial():
    Define air
    return g4.gNistManager.FindOrBuildMaterial(g4.G4String("G4_PREBUILT_MATERIAL_NAME"))

Custom materials follows this format:

def customMaterial():
    Define ultra-high molecular weight pe: (CH2)n
    # Setup
    name = "CustomName"
    components = {"Atom1": relativeAbundance1, "Atom2": relativeAbundance2} 
    density = newDensity*g/cm3
    # Build and return
    return build(name, components, density)

'''

_HERE = os.path.dirname(os.path.abspath(__file__))
_ELEMENTSFILE = os.path.join(_HERE, "elements.txt")

g = g4.g
mole = g4.mole
cm3 = g4.cm3

def build(name, components, density):
    # Read in element data
    el = np.genfromtxt(_ELEMENTSFILE, delimiter=', ', dtype=[('Z','i8'),('symbol','S3'),('name','S15'),('mass','f8')], encoding=None)

    # Initialize material
    mat = g4.G4Material(g4.G4String(name), density, len(components))

    # Add elements either by molecular formula or mass fraction
    # Component values should sum to 1 if mass fraction
    if (sum(components.values()) == 1.):

        # Add elements to material
        for sym, mf in components.items():
            x = el[np.char.lower(el['symbol']) == np.char.lower(sym.encode('utf-8'))][0]
            try:
                mat.AddElement(g4.G4Element(g4.G4String(x['name'].decode('utf-8')), g4.G4String(x['symbol'].decode('utf-8')), np.double(x['Z']), np.double(x['mass'])*g/mole), mf)
            except:
                mat.AddElement(g4.G4Element(g4.G4String(x['name']), g4.G4String(x['symbol']), np.double(x['Z']), np.double(x['mass'])*g/mole), mf)

    # Otherwise its a molecular formula
    else:
        # Compute total mass
        total_mass = 0.
        for sym, natoms in components.items():
            x = el[np.char.lower(el['symbol']) == np.char.lower(sym.encode('utf-8'))][0]
            total_mass += natoms * x['mass']*g/mole

        # Add elements to material
        for sym, natoms in components.items():
            x = el[np.char.lower(el['symbol']) == np.char.lower(sym.encode('utf-8'))][0]
            mf = natoms * x['mass']*g/mole / total_mass
            try:
                mat.AddElement(g4.G4Element(g4.G4String(x['name'].decode('utf-8')), g4.G4String(x['symbol'].decode('utf-8')), np.double(x['Z']), np.double(x['mass'])*g/mole), mf)
            except:
                mat.AddElement(g4.G4Element(g4.G4String(x['name']), g4.G4String(x['symbol']), np.double(x['Z']), np.double(x['mass'])*g/mole), mf)
    return mat

def buildElemental(name, components, ratios, density):
    # Initialize material
    mat = g4.G4Material(g4.G4String(name), density, len(components))

    # Add elements either by molecular formula or mass fraction
    # Component values should sum to 1 if mass fraction
    if (sum(ratios) == 1.):
        # Add elements to material
        for m in range(len(components)):
            x = components[m]
            mf = ratios[m]
            #print('x = ', x)
            mat.AddElement(g4.G4Element(g4.G4String(x['name']), g4.G4String(x['symbol']), np.double(x['Z']), np.double(x['mass'])*g/mole), mf)

    # Otherwise its a molecular formula
    else:
        # Compute total mass
        total_mass = 0.
        for m in range(len(components)):
            natoms = ratios[m]
            sym = components[m]
            total_mass += natoms * sym['mass']*g/mole

        # Add elements to material
        for m in range(len(components)):
            natoms = ratios[m]
            x = components[m]
            mf = natoms * x['mass']*g/mole / total_mass
            #print('x = ', x)
            mat.AddElement(g4.G4Element(g4.G4String(x['name']), g4.G4String(x['symbol']), np.double(x['Z']), np.double(x['mass'])*g/mole), mf)
    #print('mat = ',mat)
    return mat

def element(name,voxNum=0):
    '''
    Return base Geant4 element material
    Currently requires correct capitalization and using only the symbol
    i.e. Ge
    '''
    mat = g4.gNistManager.FindOrBuildMaterial(g4.G4String("G4_" + name))
    mat.SetName(g4.G4String("G4_{}_{}".format(name,voxNum)))
    return mat

'''
Elemental materials with correct atomic densities
'''
elH = {'name':'Hydrogen', 'symbol':'H', 'Z':1.0, 'mass':1.0080}

elC = {'name':'Carbon', 'symbol':'C', 'Z': 6.0, 'mass':12.011}

elN = {'name':'Nitrogen', 'symbol':'N', 'Z':7.0, 'mass':14.007}

elO = {'name':'Oxygen', 'symbol':'O', 'Z':8.0, 'mass':15.999}

elNa = {'name':'Sodium', 'symbol':'Na', 'Z':11.0, 'mass':22.9897693}

elMg = {'name':'Magnesium', 'symbol':'Mg', 'Z':12.0, 'mass':24.3050}

elP = {'name':'Phosphorus', 'symbol':'P', 'Z':15.0, 'mass':30.973762}

elS = {'name':'Sulfur', 'symbol':'S', 'Z':16.0, 'mass':32.07}

elCl = {'name':'Chlorine', 'symbol':'Cl', 'Z':17.0, 'mass':35.453}

elK = {'name':'Potassium', 'symbol':'K', 'Z':19.0, 'mass':39.098}

elFe = {'name':'Iron', 'symbol':'Fe', 'Z':26.0, 'mass':55.84}

elCa = {'name':'Calcium', 'symbol':'Ca', 'Z':20.0, 'mass':40.08}

elZn = {'name':'Zinc', 'symbol':'Zn', 'Z':30.0, 'mass':65.4}

elAr = {'name':'Argon', 'symbol':'Ar', 'Z': 18.0, 'mass':39.948}

def Vacuum(voxNum=0):
    '''Define vacuum'''
    mat = g4.gNistManager.FindOrBuildMaterial(g4.G4String("G4_Galactic"))
    mat.SetName(g4.G4String("G4_Galactic_{}".format(voxNum)))
    return mat

def Air(voxNum=0):
    '''Define air'''
    mat = g4.gNistManager.FindOrBuildMaterial(g4.G4String("G4_AIR"))
    mat.SetName(g4.G4String("G4_AIR_{}".format(voxNum)))
    return mat

def Water(voxNum=0):
    '''Define water'''
    mat = g4.gNistManager.FindOrBuildMaterial(g4.G4String("G4_WATER"))
    mat.SetName(g4.G4String("G4_WATER_{}".format(voxNum)))
    return mat

def NaI(voxNum=0):
    '''Define NaI material'''
    mat = g4.gNistManager.FindOrBuildMaterial(g4.G4String("G4_SODIUM_IODIDE"))
    mat.SetName(g4.G4String("G4_SODIUM_IODIDE_{}".format(voxNum)))
    return mat

def CsI(voxNum=0):
    '''Define CsI material'''
    mat = g4.gNistManager.FindOrBuildMaterial(g4.G4String("G4_CESIUM_IODIDE"))
    mat.SetName(g4.G4String("G4_CESIUM_IODIDE_{}".format(voxNum)))
    return mat

def Concrete(voxNum=0):
    '''Define Concrete material'''
    mat = g4.gNistManager.FindOrBuildMaterial(g4.G4String("G4_CONCRETE"))
    mat.SetName(g4.G4String("G4_CONCRETE_{}".format(voxNum)))
    return mat

def Steel(voxNum=0):
    '''Define 304 stainless steel: 0.07% C, 0.75% Si, 2% Mn, 0.045% P, 0.03% S, 17.5% Cr, 8% Ni, 0.1% N'''
    # Setup
    name = "Steel_{}".format(voxNum)
    components = {"C": .0007, "Si": 0.0075, "Mn": 0.02, "P": 0.00045, "S": 0.0003, "Cr": 0.175, "Ni": 0.08, "N": 0.001, "Fe": 0.71505} #*1e22
    density = 7.9*g/cm3
    # Build and return
    return build(name, components, density)

def SoftTissue(density,voxNum=0):
    '''Define soft tissue: https://physics.nist.gov/cgi-bin/Star/compos.pl?matno=261'''
    name = "SoftTissue_{}".format(voxNum)
    components = [elH, elC, elN, elO, elNa, elMg, elP, elS, elCl, elK, elCa, elFe, elZn]
    ratios = [0.104472,0.232190,0.024880,0.630238,0.001130,0.000130,0.001330,0.001990,0.001340,0.001990,0.000230,0.000050,0.000030]
    #density range from 0.302 - 1.01
    #density = 1.0*g/cm3
    return buildElemental(name, components, ratios, density*g/cm3)


def AirCavity(density,voxNum=0):
    '''Define air: https://www.eo.ucar.edu/basics/wx_1_b_1.html, https://forces.si.edu/Atmosphere/02_01_02.html'''
    name = "Air_{}".format(voxNum)
    components = [elO,elN,elAr]
    ratios = [0.21,0.78,0.01]
    #density range 0.001-0.044
    return buildElemental(name, components, ratios, density*g/cm3)

def Lung(density,voxNum=0):
    '''Define lung tissue'''
    name = "Lung_{}".format(voxNum)
    components = [elH, elC, elN, elO, elNa, elP, elS, elCl, elK]
    ratios = [0.103, 0.105, 0.031, 0.749, 0.002, 0.002, 0.003, 0.002, 0.003]
    #density range 0.044-0.302
    return buildElemental(name, components, ratios, density*g/cm3)

def Bone(density,voxNum=0):
    '''Define bone'''
    #density range 1.101 - 2.088
    name = "Bone_{}".format(voxNum)
    if density <= 1.1695:
        #trabecular bone
        components = [elH, elC, elN, elO, elNa, elMg, elP, elS, elCl, elK, elCa, elFe]
        ratios = [0.085,0.404,0.058,0.367,0.001,0.001,0.034,0.002,0.002,0.001,0.044,0.001]
    elif density > 1.1695 and density <= 1.3775:
        #dense trabecular bone
        components = [elH, elC, elN, elO, elNa, elMg, elP, elS, elCl, elK, elCa, elFe]
        ratios = [0.085,0.4040,0.028,0.3670,0.001,0.001,0.034,0.002,0.002,0.001,0.074,0.001]
    elif density > 1.3775 and density <= 1.7125:
        #dense bone
        components = [elH, elC, elN, elO, elNa, elMg, elP, elS, elCl, elK, elCa]
        ratios = [0.056,0.235,0.050,0.434,0.001,0.001,0.072,0.003,0.001,0.001,0.146]
    elif density > 1.7125:
        #cortical bone
        components = [elH, elC, elN, elO, elMg, elP, elS, elCa, elZn]
        ratios = [0.047234,0.144330,0.04199,0.446096,0.0022,0.10497,0.00315,0.20993,0.0001]
    return buildElemental(name, components, ratios, density*g/cm3)

def PMMA(voxNum=0):
    '''Define pmma: https://physics.nist.gov/cgi-bin/Star/compos.pl?matno=223'''
    name = "PolymethylMethacralate_LucidePlexiglass_{}".format(voxNum)
    components = [elH, elC, elO]
    ratios = [0.080538, 0.599848, 0.319614]
    #density range from 0.302 - 1.01
    density = 1.19*g/cm3
    return buildElemental(name, components, ratios, density)

def UHMWPE(voxNum=0):
    '''Define ultra-high molecular weight pe: (CH2)n'''
    # Setup
    name = "UHMWPE"
    #weightRatio = (7.9*1.008)/(7.9*1.008+4.35*12.001) #No.of H Getoms/cm3, 5.43E22
    components = {"H": .1438, "C": 0.8562} #*1e22
    density = 0.97*g/cm3
    # Build and return
    return build(name, components, density)
