#!/bin/bash

results_folder=trento_results
evid=$1

 (
cd TRENTo

mkdir -p $results_folder
rm -fr $results_folder/*

export OMP_NUM_THREADS=1

    # Run Isobar-Sampler ...

(
cd Isobar-Sampler_target
./build_isobars.py isobars-conf_target.yaml > run.log
mv nuclei_target ..
)
(
cd Isobar-Sampler_projectile
./build_isobars.py isobars-conf_projectile.yaml  > run.log
mv nuclei_projectile ..
)
# Run TRENTo...
./trento -c input > run.log
mv test_path.dat $results_folder/
 )
