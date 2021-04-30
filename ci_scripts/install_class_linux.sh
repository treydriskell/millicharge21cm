#!/bin/bash

git clone -b dmb https://github.com/veragluscevic/class_public.git
cd class_public
make -j4

# at this point the make file leaves you in the python dir
cd ..
