#!/bin/bash
set -x

# FFMS
mkdir ffms
pushd ffms
#wget -O ffms.tar.gz https://github.com/FFMS/ffms2/archive/2.23.1.tar.gz
#tar xf ffms.tar.gz --strip-components 1
git clone https://github.com/FFMS/ffms2.git .
bash autogen.sh #--prefix=/usr
make -j "$CPU_CORES"
make install
popd
rm -rf ffms

# OTR tool
git clone https://github.com/craeckie/otrtool.git otrtool
cd otrtool
make -j "$CPU_CORES"
make install
cd .. && rm -r otrtool
