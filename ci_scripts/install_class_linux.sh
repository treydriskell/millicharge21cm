#!/bin/bash

git clone https://github.com/veragluscevic/class_public.git
cd class_public
git fetch
git checkout dmb
make -j4

# at this point the make file leaves you in the python dir
cd ..
