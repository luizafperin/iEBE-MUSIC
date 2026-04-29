#!/bin/bash

unalias ls 2>/dev/null

SubEventId=$1

(
cd UrQMDev_$SubEventId

mkdir -p UrQMD_results
rm -fr UrQMD_results/*

surfaceFile=`ls hydro_event | grep "surface"`
for iev in {0..9}
do
    export OMP_NUM_THREADS=1
    cd iSS
    export OMP_NUM_THREADS=1
    RANDOMSEED=`cat iSS_parameters.dat | grep "randomSeed" | cut -f 3 -d " "`
    if [ $RANDOMSEED != "-1" ]; then
        RANDOMSEED=$((RANDOMSEED + iev))
    fi
    mkdir -p results
    rm -fr results/*
    ln -s ../../hydro_event/${surfaceFile} results/surface.dat
    cp ../hydro_event/music_input results/music_input
    cp ../hydro_event/spectators.dat results/spectators.dat 2>/dev/null
    if [ $SubEventId = "0" ] && [ $iev -eq "0" ]; then
        ./iSS.e randomSeed=$RANDOMSEED 2>&1  >> run.log
    else
        ./iSS.e randomSeed=$RANDOMSEED 2>&1 > run.log
    fi
    
    cd ../osc2u
    ./osc2u.e < ../iSS/OSCAR.DAT > run.log
    mv fort.14 ../urqmd/OSCAR.input
    rm -fr ../iSS/OSCAR.DAT
    cd ../urqmd
    ./runqmd.sh > run.log
    mv particle_list.dat ../UrQMD_results/particle_list_${iev}.dat
    rm -fr OSCAR.input
    cd ..
    ../hadronic_afterburner_toolkit/convert_to_binary.e UrQMD_results/particle_list_${iev}.dat binary
    rm -fr UrQMD_results/particle_list_${iev}.dat
    cat UrQMD_results/particle_list_${iev}.bin >> UrQMD_results/particle_list.bin
    rm -fr UrQMD_results/particle_list_${iev}.bin
done

    rm -fr hydro_event
)
