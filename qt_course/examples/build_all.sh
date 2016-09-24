#!/bin/bash
builddir=$(dirname ${0})/_build

mkdir -p ${builddir}
cd ${builddir}
qmake ../examples.pro
make -j 2
