# geant4pymp

geant4pymp written by Adam Glick at MD Anderson Cancer Center for dose calculations on DICOM datasets. Geant4 framework written in python using BOOST bindings. Current support is for python3.8 (with a provided anaconda environment) on Ubuntu 16. Tested with Geant4.10.7. Based on geant4py code written by Dan Hellfeld with contributions from the Applied Nuclear Physics group at Lawrence Berkeley National Laboratory and BeARING group at UC Berkeley.


## Installation

#### Anaconda environment

- If you don't already have Anaconda installed
    ```
    bash installs/installConda4Boost.sh
    ```

- Setup the conda environment
    ```
    conda activate
    python --version
    ```

- Python version should be 3.x. Initial problems with `multiprocessing` of simulation as been solved.

#### Geant4 Dependencies

- Before installing Geant4, install necessary dependencies
    ```
    $ sh installs/installXercesC.sh
    ```
    - ***First run will download data files. Enter `n` when prompted. Then go into `/src/xercesc/dom/impl/DOMNodeIDMap.cpp` and replace `static const XMLSize_t gPrimes[] = {997, 9973, 99991, 999983, 0 };` with `static const XMLSize_t gPrimes[] = {997, 9973, 99991, 999983, 999999991, 9999999989, 0 };`***
    - ***This allows for large GDML datasets to be loaded***

#### Geant4
- If Geant4 is not installed, run the following:
    ```
    $ sh installs/install_geant4.sh
    ```
    ***There is a chance that lines 27--29 need to be changed depending on your system. It should be fine for debian systems.***

- Source Geant4 (add these to your .bashrc)
    ```
    $ . <path/to/G4install/Geant4.10.version.patch/geant4-install/share/Geant4-10.5.0/geant4make/geant4make.sh>
    $ . <path/to/G4install/Geant4.10.version.patch/geant4-install/bin/geant4.sh>
    ```

#### Geant4 python environment

- G4Py installs as part of the GEANT4 install now. It should have installed to `~/anaconda3/lib/python3.x/site-packages/Geant4`.

- G4Py does not automatically import GDML formatting, so you must edit the `~/anaconda3/lib/python3.x/site-packages/Geant4/__init__.py` to include the following under `import submodules`:
  ```
  from .G4gdml import *
  ```

- Test install
    ```
    $ python -c "import Geant4"
    ```

#### geant4pymp

- Run the setup script
    ```
    $ python setup.py install
    ```

- Test install
    ```
    $ python scripts/simBeam.py
    ```

## Multiprocessing

- Simulations can be locally multiprocessed across certain parameters.
- For example, for a simulation of a single energy and single direction, the simulation can be multiprocessed across the number of particles
    ```
    $ python scripts/simBeam.py -mp
    ```

- The multiprocessed output data will be written to separates files and then merged together into one file. Therefore this is some additional processing that needs to happen when reading in the data. An example notebook is provided to show this.

## Code Structure

# Core

  - `main.py`: initializes all necessary parameters for simulations
  - `detectorconstruction.py`: constructs world and sets sensitive detectors
  - `sensitivedetector.py`: defines what types of processes to track and what information to extract from those interactions. passes data to `runaction.py`.
  - `runaction.py`: initializes data arrays and saves data as HDF5 files at end of simulation.
  - `eventaction.py`: prints to screen how many events have been simulated every 1e5 events.
  - `stackingaction.py`: classifies new track after each interaction. can kill particles that are not of interest to speed up simulation.
  - `physicslist.py`: empty
  - `steppingaction.py`: empty
  - `visualization.py`: inputs commands to visualize simulation based on user input.
  - `argparser.py`: parses command line inputs and passes to `main.py`

# Geo
  .
  .
  .

# Source
  .
  .
  .

# Scripts
  .
  .
  .

## Geometry, Sources, Physics

  - GDML output appears to be the format that GEANT likes. PyG4ometry is a highly useful package for generating GDML data from STL data:
  http://www.pp.rhul.ac.uk/bdsim/pyg4ometry/pythonscripting.html#registry-and-gdml-output
    ***For PyG4ometry questions, please contact Stewart Boogert (stewart.boogert@rhul.ac.uk). Special thanks to him for all of his help in developing out the implementation of PyG4ometry in Geant4PyMP!!!***

  - To generate a GDML file from a STL file using PyG4ometry the STL file must be in ASCII format. To get it in ASCII format install `pip install numpy-stl` and run:
    ```
    stl2ascii your_binary_stl_file.stl new_ascii_stl_file.stl
    ```
  - You can then 
  - Loading a GDML requires material definitions to be loaded *prior* to loading the GDML file.
    ```
    G4_Galactic = g4py.geo.material.Vacuum()
    gdmlParser = g4.G4GDMLParser()
    gdmlParser.Read('/path/to/gdml/file')
    geo = gdmlParser.GetWorldVolume()
    ```



## Output Data

  - All data is saved as HDF5. Look at `runaction.py` to see `keys()` structure.

## Examples

..
