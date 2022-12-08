#/!bin/bash
### GLVND
sudo apt install libglvnd-core-dev
### OpenGL
sudo apt-get update
sudo apt-get install libglu1-mesa-dev freeglut3-dev mesa-common-dev
#### VTK
cd
git clone https://gitlab.kitware.com/vtk/vtk.git
cd vtk
cmake -DCMAKE_INSTALL_PREFIX=$HOME/vtk-inst \
    -DCMAKE_INSTALL_RPATH=$HOME/vtk-inst \
    -DVTK_Group_Qt=ON \
    -DVTK_QT_VERSION=5 \
    -DVTK_Group_Imaging=ON \
    -DVTK_Group_Views=ON \
    -DModule_vtkRenderingFreeTypeFontConfig=ON \
    -DVTK_WRAP_PYTHON=ON \
    -DVTK_PYTHON_VERSION=3 \
    -DPYTHON_EXECUTABLE=/usr/bin/python3 \
    -DPYTHON_INCLUDE_DIR=/usr/include/python3.6 \
    -DPYTHON_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.6m.so \
    -DBUILD_TESTING=OFF \
    -DVTK_USE_SYSTEM_LIBRARIES=ON \
    -DVTK_USE_SYSTEM_LIBPROJ4=OFF \
    -DVTK_USE_SYSTEM_GL2PS=OFF \
    -DVTK_USE_SYSTEM_LIBHARU=OFF \
    -DVTK_USE_SYSTEM_PUGIXML=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    ..
make -j$(($(nproc) - 1))
make install

### MEDC
sudo apt install libmedc-dev

### SWIG
sudo apt install swig

### Eigen3
sudo apt install libeigen3-dev

### Coin
pip install ruamel-yaml
pip install pycosat
pip install coin
git clone --recurse-submodules https://github.com/coin3d/coin coin
cmake -Hcoin -Bcoin_build -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX=/usr/local -DCMAKE_BUILD_TYPE=Release -DCOIN_BUILD_DOCUMENTATION=OFF
cd coin_build && make -j$(($(nproc) - 1))
make install
cd ~/coin/cpack.d
cpack --config debian.cmake

### Pivy
sudo apt-get install -y python3-pivy

### SPNAV
pip install spnav

### Shiboken
pip install utils
pip install shiboken2
### PySide
pip install pyside2

### FreeCAD
pyMajor=$(python -c 'import sys; print(str(sys.version_info[0]))')
pyMinor=$(python -c 'import sys; print(str(sys.version_info[1]))')
export pyinstallDir=${CONDA_PREFIX}/lib/python${pyMajor}.${pyMinor}/site-packages/
export vtkRoot=~/vtk/build
export vtkInclude=~/vtk-inst/include/vtk-9.0
git clone https://github.com/FreeCAD/FreeCAD
cd FreeCAD
sudo apt-get install --no-install-recommends --yes build-essential cmake doxygen git \
    libboost-date-time-dev libboost-dev libboost-filesystem-dev \
    libboost-graph-dev libboost-iostreams-dev libboost-program-options-dev \
    libboost-python-dev libboost-regex-dev libboost-serialization-dev \
    libboost-thread-dev libcoin-dev libeigen3-dev libgtkglext1-dev \
    libgts-dev libkdtree++-dev libkml-dev libmedc-dev libocct-data-exchange-dev \
    libocct-draw-dev libocct-foundation-dev libocct-modeling-algorithms-dev \
    libocct-modeling-data-dev libocct-ocaf-dev libocct-visualization-dev \
    libopencv-dev libproj-dev libpyside2-dev libqt5svg5-dev libqt5webkit5-dev \
    libqt5xmlpatterns5-dev libshiboken2-dev libvtk-dicom-dev libx11-dev libxerces-c-dev libxmu-dev libxmuu-dev \
    libzipios++-dev netgen netgen-headers pyside2-tools python3-dev \
    python3-matplotlib python3-pivy python3-ply python3-pyside2.qtsvg \
    python3-pyside2.qtuitools qtchooser qttools5-dev shiboken2 swig -y

#mkdir build && cd build
cmake -DVTK_DIR=$vtkRoot                \
      -DCMAKE_INSTALL_PREFIX=../install \
      -DBUILD_FEM=0 \
      -DBUILD_MATERIAL=0 -DBUILD_SHIP=0 -DBUILD_DRAFT=0 -DBUILD_TUX=0 -DBUILD_ARCH=0 -DBUILD_PLOT=0 \
      -DBUILD_OPENSCAD=0                \
      -DCMAKE_INSTALL_PYTHONDIR=$pyinstallDir     \
      ..
sudo apt-get install freecad
conda config --add channels conda-forge
conda config --add channels freecad
conda create --name freecad_py3 python=3.6 freecad

source activate freecad_py3
FreeCAD
### TO RUN
# $ sh installPyg4ometry.sh
pyMajor=$(python -c 'import sys; print(str(sys.version_info[0]))')
pyMinor=$(python -c 'import sys; print(str(sys.version_info[1]))')
cd ~
mkdir pyg4ometry
git clone http://bitbucket.org/jairhul/pyg4ometry
git checkout develop
ln -sf "~/pyg4ometry/jairhul-pyg4ometry-0257988a56ad/pyg4ometry" "~/${CONDA_PREFIX}/lib/python${pyMajor}.${pyMinor}/site-packages/"

#make install

#pip install pybind11
#make build_ext

#http://www.pp.rhul.ac.uk/bdsim/pyg4ometry/installation.html#requirements

### Specifically interested in: ###

### import pyg4ometry
### w = p4gometry.gdml.Writer()
### w.addDetector(reg)
### w.write('file.gdml')
### # make a quick bdsim job for the one component in a beam line
### w.writeGmadTester('file.gmad', 'file.gdml')
