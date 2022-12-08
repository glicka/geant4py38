#/!bin/bash

wget https://dlcdn.apache.org//xerces/c/3/sources/xerces-c-3.2.3.zip
unzip xerces-c-3.2.3.zip
rm xerces-c-3.2.3.zip
cd xerces-c-3.2.3/src/xercesc/dom/impl/
### Doesn't work. Must verify this part works or manually change /src/xercesc/dom/impl/DOMNodeIDMap.cpp!!! ###
sed -i "s|static\ const\ XMLSize_t\ gPrimes[]\ =\ {997, 9973, 99991, 999983, 0 };|static\ const\ XMLSize_t\ gPrimes[]\ =\ {997, 9973, 99991, 999983, 999999991, 9999999989, 0 }; // To do - add a few more.|g" DOMNodeIDMap.cpp
echo "Did you alter /src/xercesc/dom/impl/DOMNodeIDMap.cpp? (y/n)"
read -p yn
if [[ "$yn" == "y" ]]; then
  cd ~/xerces-c-3.2.3
  mkdir build && cd build
  cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX=/opt/xerces-c -DCMAKE_BUILD_TYPE=Debug -Dmessage-loader=icu ..
  ncores=$(python -c "import multiprocessing as mp; print(mp.cpu_count())")
  make "-j${ncores}"
  make test
  sudo make install
else
  echo "You must alter /src/xercesc/dom/impl/DOMNodeIDMap.cpp before proceeding"
  echo "cd /src/xercesc/dom/impl"
  echo "nano DOMNodeIDMap.cpp"
  echo "replace  static const XMLSize_t gPrimes[] = {997, 9973, 99991, 999983, 0 };"
  echo "with static const XMLSize_t gPrimes[] = {997, 9973, 99991, 999983, 999999991, 9999999989, 0 };"
  echo "then rerun `sh installXercesC.sh`"
fi
