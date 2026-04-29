#!/bin/bash

results_folder=hydro_results

(
cd MUSIC

rm -fr *.dat
rm -fr $results_folder


export OMP_NUM_THREADS=1

# hydro evolution
./MUSIChydro music_input_mode_2 > run.log
./sweeper.sh $results_folder
cp run.log $results_folder/run.log
)
