#!/bin/bash

git clone https://github.com/veragluscevic/class_public.git
cd class_public
git checkout -b dmb
git pull origin dmb
make -j4

# at this point the make file leaves you in the python dir
cd ..
