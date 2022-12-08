#/!bin/bash

### TO RUN
# $ sh install_geant4.py <path/to/install_directory>

#sudo apt-get install libxaw7-dev

# Choose version (each must be two digits!) -- eventually put this into command line argument
export MAJOR="10"
export MINOR="07"
export g4dir="Geant4.$((MAJOR)).$((MINOR))"

pyMajor=$(python -c 'import sys; print(str(sys.version_info[0]))')
pyMinor=$(python -c 'import sys; print(str(sys.version_info[1]))')
# Move to home directory and creat geant4 dir
cd

# Choose build options
export OPENGL_X11="ON"
export RAYTRACER_X11="ON"
export USE_QT="OFF"
export MULTITHREADED="ON"
export INSTALL_DATA="ON"
export USE_SYSTEM_EXPAT="OFF"
export STATIC_LIBS="OFF"
export G4PYINSTALL="ON"
export XERCESCPATH=~/opt/xerces-c/
export XercesIncludeDir=/usr/local/include/xercesc/
export XercesRootDir=/usr/local/lib

echo "Organizing directories..."
if [ ! -d "$g4dir" ]; then
    mkdir $g4dir
    mkdir $g4dir/geant4-build
    mkdir $g4dir/geant4-source
    mkdir $g4dir/geant4-install
    mkdir $g4dir/geant4-data
fi

echo "Downloading source..."

git clone https://github.com/Geant4/geant4.git


echo "Moving to build directory..."
cd $g4dir/geant4-build
export install_dir=$PWD/../geant4-install
export data_dir=$PWD/../geant4-data
export source_dir=$PWD/../geant4-source
export pyinstallDir=${CONDA_PREFIX}/lib/python${pyMajor}.${pyMinor}/site-packages/

cd $source_dir/geant4/environments/g4py

echo \
'''
#include <boost/python.hpp>
#include "G4PhysListFactory.hh"

using namespace boost::python;

// ====================================================================
// module definition
// ====================================================================
void export_G4PhysListFactory()
{
  class_<G4PhysListFactory, G4PhysListFactory*>
    ("G4PhysListFactory", "phys list factory")
    // ---
    .def("GetReferencePhysList", &G4PhysListFactory::GetReferencePhysList,
         return_internal_reference<>())
    ;
}

// ====================================================================
// module definition
// ====================================================================
void export_PhysicsLists();
void export_G4PhysListFactory();

BOOST_PYTHON_MODULE(G4physicslists)
{
  export_PhysicsLists();
  export_G4PhysListFactory();
}
''' \
> source/physics_lists/pymodG4physicslists.cc

cd ~/$g4dir/geant4-build

echo "Starting build with cmake..."
cmake  -DGEANT4_USE_OPENGL_X11=$OPENGL_X11        \
      -DGEANT4_USE_RAYTRACER_X11=$RAYTRACER_X11   \
      -DGEANT4_USE_QT=$USE_QT                     \
      -DBUILD_STATIC_LIBS=$STATIC_LIBS            \
      -DGEANT4_BUILD_MULTITHREADED=$MULTITHREADED \
      -DGEANT4_USE_SYSTEM_EXPAT=$USE_SYSTEM_EXPAT \
      -DGEANT4_INSTALL_DATADIR=$data_dir          \
      -DGEANT4_INSTALL_DATA=$INSTALL_DATA         \
      -DCMAKE_INSTALL_PREFIX=$install_dir         \
      -DCMAKE_INSTALL_PYTHONDIR=$pyinstallDir     \
      -DGEANT4_USE_PYTHON=$G4PYINSTALL            \
      -DGEANT4_BUILD_TLS_MODEL=global-dynamic     \
      -DCMAKE_PREFIX_PATH=$XERCESCPATH            \
      -XercesC_INCLUDE_DIR=$XercesIncludeDir \
      -XERCESC_ROOT_DIR=$XercesRootDir            \
      -DGEANT4_USE_GDML=ON                        \
      ../geant4-source/geant4


ncores=$(python -c "import multiprocessing as mp; print(mp.cpu_count())")
echo "Starting make and make install..."
make "-j${ncores}" ### must build Geant4 on a single thread.
#make
make install


echo "Writing selected build options to file and placing in $g4dir/geant4-build..."
cd geant4-build
cat <<EOT>> BUILDOPTIONS.txt
OPENGL_X11=$OPENGL_X11
RAYTRACER_X11=$RAYTRACER_X11
USE_QT=$USE_QT
MULTITHREADED=$MULTITHREADED
INSTALL_DATA=$INSTALL_DATA
USE_SYSTEM_EXPAT=$USE_SYSTEM_EXPAT
CXXSTD=$CXXSTD
STATIC_LIBS=$STATIC_LIBS
EOT

echo "Done!"
# Print bashrc advice to screen
echo "Add the following to your bashrc:"
echo "# Source Geant4"
echo "source ~/$g4dir/geant4-install/share/Geant4-11.0.0/geant4make/geant4make.sh"
echo "source ~/$g4dir/geant4-install/bin/geant4.sh"
echo "export G4WORKDIR=."

ln -sf "${g4dir}/geant4-build/BuildProducts/lib/python${pyMajor}.${pyMinor}/site-packages/Geant4/" "${CONDA_PREFIX}/lib/python${pyMajor}.${pyMinor}/site-packages/Geant4/"
