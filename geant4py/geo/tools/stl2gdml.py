import stl
import pyg4ometry as g4o
from geant4py.geo.tools.stlGdmlTest import main
import os

def _get_name(args):
    names = [
        args.name,
        getattr(args.outfile, 'name', None),
        getattr(args.infile, 'name', None),
        'numpy-stl-%06d' % random.randint(0, 1e6),
    ]

    for name in names:  # pragma: no branch
        if name and isinstance(name, str) and not name.startswith('<'):
            return name

def stl2gdml(inputFile,outputFile):
    '''
    Easy way to convert from an STL to a GDML geometry for placement in simulation
    inputFile: geometry in .stl binary or ASCII format
    outputFile: name of geometry in a .gdml format
    '''

    '''
    Automatically convert from binary to ASCII
    Checks if input file is ASCII and if it is then this is redundant
    '''
    #cadData = stl.stl.read_binary_(inputFile)

    asciiName = '{}ASCII_Vacuum.stl'.format(outputFile.split('.')[0])
    #stl.stl.BaseStl.save(cadData,asciiName,mode=stl.stl.ASCII)
    os.system('stl2ascii {} {}'.format(inputFile,asciiName))
    name = _get_name()
    stl_file = stl.stl.StlMesh(filename=inputFile, fh=args.infile,
                           calculate_normals=False,
                           remove_empty_areas=args.remove_empty_areas,
                           speedups=not args.disable_speedups)
    stl_file.save(name, args.outfile, mode=stl.ASCII,
                  update_normals=not args.use_file_normals)
    '''
    Convert from stl to gdml using PyG4ometry:
    '''
    #cad4gdml = g4o.stl.Reader(asciiName)
    #cad4gdml.writeDefaultGDML(outputfile)
    os.system('python stl_gdml.py {} {}'.format(outputFile,asciiName))
    return outputFile
