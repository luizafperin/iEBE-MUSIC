#!/bin/bash

base_seed=12345
base_dir="/home/luizaperin/iEBE-MUSIC"

for n in {0..3}
do
    workdir="hrg_s0_run${n}"
    full_path="${base_dir}/${workdir}"
    seed=$((base_seed + n))

    echo "=== Running job $n with seed $seed in $workdir ==="

    # Generate events/jobs
    python3 generate_jobs.py \
        -w "$workdir" \
        -par config/parameters_dict_user_TRENTo.py \
        -seed "$seed" \
        --isobar_seed_file nucleon-seeds.hdf

    # Go through each event folder and submit
    for event_dir in "$full_path"/event_*
    do
        if [ -d "$event_dir" ]; then
            echo "Submitting job in $event_dir"
            (
                cd "$event_dir" || exit
                bash ./submit_job.script
            )
        fi
    done

done
