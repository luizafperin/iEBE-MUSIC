#!/usr/bin/env python3
"""This script generates the job submission script for a generic HTCondor cluster
with Singularity/Apptainer support."""

import subprocess
import re
import sys
from os import path, makedirs
import argparse

FILENAME = "singularity.submit"


def detect_afterburner(param_file):
    """Return afterburner_type string read from the parameter file."""
    try:
        with open(param_file, 'r') as f:
            content = f.read()

        m = re.search(
            r"['\"]afterburner_type['\"]\s*:\s*['\"](\w+)['\"]",
            content
        )

        if m:
            return m.group(1)

    except Exception:
        pass

    return "UrQMD"


# --------------------------------------------------------------
# URQMD
# --------------------------------------------------------------

def write_submission_script_urqmd(para_dict_):

    jobName = "iEBEMUSIC_{}".format(para_dict_["job_name"])

    random_seed = para_dict_["random_seed"]
    seed_file = para_dict_.get("seed_file", "")
    has_seed = seed_file != ""

    sif = para_dict_["singularity_image_path"]

    script = open(FILENAME, "w")

    # ----------------------------------------------------------
    # Build arguments dynamically
    # ----------------------------------------------------------

    if para_dict_["bayesFlag"]:

        args = [
            para_dict_["param_file"],
            "$(Process)",
            str(para_dict_["n_hydro_per_job"]),
            str(para_dict_["n_threads"]),
            str(random_seed),
            para_dict_["bayes_file"]
        ]

    else:

        args = [
            para_dict_["param_file"],
            "$(Process)",
            str(para_dict_["n_hydro_per_job"]),
            str(para_dict_["n_threads"]),
            str(random_seed)
        ]

        args.append(sif)

    script.write(f"""universe = vanilla
executable = run_singularity.sh
arguments = {" ".join(args)}

JobBatchName = {jobName}

should_transfer_files = YES
WhenToTransferOutput = ON_EXIT
requirements = (Machine != "gpusphydro")
""")

    # ----------------------------------------------------------
    # Transfer input files dynamically
    # ----------------------------------------------------------

    inputs = [para_dict_["param_file"]]

    if para_dict_["bayesFlag"]:
        inputs.append(para_dict_["bayes_file"])

    inputs.append("shared_seeds")

    inputs.append(sif)

    script.write(
        "\ntransfer_input_files = {}\n".format(
            ", ".join(inputs)
        )
    )

    script.write(
        "transfer_checkpoint_files = "
        "playground/event_0/EVENT_RESULTS_$(Process).tar.gz\n"
    )

    script.write("""
transfer_output_files = \
playground/event_0/EVENT_RESULTS_$(Process)/spvn_results_$(Process).h5, \
playground/model_parameters

transfer_output_remaps = "model_parameters=model_parameters_$(Process)"

error = log/job.$(Cluster).$(Process).error
output = log/job.$(Cluster).$(Process).output
log = log/job.$(Cluster).$(Process).log

max_idle = 1000

periodic_remove = (ExitCode == 73)

periodic_release = ((HoldReasonCode == 13 || HoldReasonCode == 26) && \
(time() - EnteredCurrentStatus) > 1200 )

checkpoint_exit_code = 85

on_exit_hold = (ExitBySignal == True) || \
(ExitCode != 0 && ExitCode != 73)

request_cpus = {0:d}
request_memory = {1:d} GB
request_disk = 8 GB

queue {2:d}
""".format(
        para_dict_["n_threads"],
        para_dict_["memory_per_job"],
        para_dict_["n_jobs"]
    ))

    script.close()


# ─────────────────────────────────────────────────────────────────────
# RUN SCRIPT
# ─────────────────────────────────────────────────────────────────────

def write_job_running_script_urqmd(para_dict_):

    has_seed = para_dict_.get("seed_file", "") != ""

    with open("run_singularity.sh", "w") as script:

        script.write(r"""#!/usr/bin/env bash

set -euo pipefail

parafile=$1
processId=$2
nHydroEvents=$3
nthreads=$4
randomSeed=$5

""")

        # ----------------------------------------------------------
        # Argument parsing
        # ----------------------------------------------------------

        if para_dict_["bayesFlag"]:
            script.write(r"""
bayesFile=$6

if [ $# -eq 8 ]; then
    seed_file=$7
    SINGULARITY_IMAGE=$8
else
    seed_file=""
    SINGULARITY_IMAGE=$7
fi

""")

        else:
            script.write(r"""
if [ $# -eq 7 ]; then
    seed_file=$6
    SINGULARITY_IMAGE=$7
else
    seed_file=""
    SINGULARITY_IMAGE=$6
fi

""")

        script.write(r'''
export PYTHONIOENCODING=utf-8

export PATH="${PATH:-}:/usr/lib64/openmpi/bin:/usr/local/gsl/2.5/x86_64/bin"

export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:/usr/local/lib:/usr/local/gsl/2.5/x86_64/lib64"

SCRATCH_DIR="$(pwd)"
JOBDIR="${SCRATCH_DIR}"

echo "======================================="
echo "Start time : $(date)"
echo "Hostname   : $(hostname)"
echo "Scratch    : ${SCRATCH_DIR}"
echo "======================================="

echo "Arguments received: $#"
echo "$@"

SIF="${SCRATCH_DIR}/$(basename "${SINGULARITY_IMAGE}")"

echo "Resolved SIF: ${SIF}"

if [ ! -f "${SIF}" ]; then
    echo "ERROR: SIF file not found"
    ls -lh
    exit 1
fi


# --------------------------------------------------------------
# Writable dirs
# --------------------------------------------------------------

export TMPDIR="${JOBDIR}/tmp"
export XDG_DATA_HOME="${JOBDIR}/.local/share"
export XDG_CACHE_HOME="${JOBDIR}/.cache"
export TRENTO_CACHE="${JOBDIR}/.trento"

mkdir -p "${TMPDIR}"
mkdir -p "${XDG_DATA_HOME}"
mkdir -p "${XDG_CACHE_HOME}"
mkdir -p "${TRENTO_CACHE}"
mkdir -p "${XDG_DATA_HOME}/trento"


# --------------------------------------------------------------
# Forward env into container
# --------------------------------------------------------------

export APPTAINERENV_TMPDIR="${TMPDIR}"
export APPTAINERENV_XDG_DATA_HOME="${XDG_DATA_HOME}"
export APPTAINERENV_XDG_CACHE_HOME="${XDG_CACHE_HOME}"
export APPTAINERENV_TRENTO_CACHE="${TRENTO_CACHE}"

echo "Running generate_jobs.py ..."
''')

        # ----------------------------------------------------------
        # generate_jobs.py
        # ----------------------------------------------------------

        seed_argument = (
            '        --isobar_seed_file "${seed_file}" \\\n'
            if has_seed else ""
        )

        if para_dict_["bayesFlag"]:

            script.write(fr'''
apptainer exec \
    --bind "${{SCRATCH_DIR}}:${{SCRATCH_DIR}}" \
    "${{SIF}}" \
    python3 /opt/iEBE-MUSIC/generate_jobs.py \
        -w playground \
        -c {para_dict_["cluster_name"]} \
        --node_type {para_dict_["node_type"]} \
        -par "${{parafile}}" \
        -id "${{processId}}" \
        -n_th "${{nthreads}}" \
        -n_urqmd {para_dict_["n_urqmd_per_hydro"]} \
        -n_hydro {para_dict_["n_hydro_per_job"]} \
{seed_argument}        -seed "${{randomSeed}}" \
        -b "${{bayesFile}}" \
        {"--nocopy" if para_dict_["nocopy"] else ""} \
        {"--continueFlag" if para_dict_["continueFlag"] else ""}
''')

        else:
            script.write(fr'''
apptainer exec \
    --bind "${{SCRATCH_DIR}}:${{SCRATCH_DIR}}" \
    "${{SIF}}" \
    python3 /opt/iEBE-MUSIC/generate_jobs.py \
        -w playground \
        -c {para_dict_["cluster_name"]} \
        --node_type {para_dict_["node_type"]} \
        -par "${{parafile}}" \
        -id "${{processId}}" \
        -n_th "${{nthreads}}" \
        -n_urqmd {para_dict_["n_urqmd_per_hydro"]} \
        -n_hydro {para_dict_["n_hydro_per_job"]} \
{seed_argument}        -seed "${{randomSeed}}" \
        {"--nocopy" if para_dict_["nocopy"] else ""} \
        {"--continueFlag" if para_dict_["continueFlag"] else ""}
''')

            script.write(r'''

gen_status=$?

echo "generate_jobs.py exit code: ${gen_status}"

if [ ${gen_status} -ne 0 ]; then
    echo "ERROR: generate_jobs.py failed"
    exit ${gen_status}
fi

echo "Generated files:"
find playground -maxdepth 2 | head -50

if [ ! -d "playground/event_0" ]; then
    echo "ERROR: playground/event_0 missing"
    exit 1
fi

cd playground/event_0

echo "Current dir:"
pwd

ls -lh

if [ ! -f "submit_job.script" ]; then
    echo "ERROR: submit_job.script missing"
    find . -maxdepth 2
    exit 1
fi

chmod +x submit_job.script

echo "Running submit_job.script ..."

apptainer exec \
    --bind "${SCRATCH_DIR}:${SCRATCH_DIR}" \
    "${SIF}" \
    bash submit_job.script

status=$?

echo "submit_job.script exit code: ${status}"

if [ ${status} -ne 0 ]; then
    echo "ERROR: submit_job.script failed"
    exit ${status}
fi

echo "Job finished successfully at $(date)"
''')

    subprocess.call("chmod +x run_singularity.sh", shell=True)


# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────

def main(para_dict_):

    afterburner = detect_afterburner(para_dict_["param_file"])

    print("Detected afterburner: {}".format(afterburner))

    write_submission_script_urqmd(para_dict_)
    write_job_running_script_urqmd(para_dict_)

    logFolderName = "log"

    if not path.exists(logFolderName):
        makedirs(logFolderName)


# ─────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='HTCondor + Apptainer submission script for iEBE-MUSIC',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # --------------------------------------------------------------
    # Core job settings
    # --------------------------------------------------------------

    parser.add_argument(
        '-n',
        '--n_jobs',
        metavar='',
        type=int,
        default=1,
        help='number of jobs'
    )

    parser.add_argument(
        '-n_hydro',
        '--n_hydro_per_job',
        metavar='',
        type=int,
        default=1,
        help='number of hydro events per job'
    )

    parser.add_argument(
        '-n_urqmd',
        '--n_urqmd_per_hydro',
        metavar='',
        type=int,
        default=1,
        help='number of oversampled UrQMD events per hydro'
    )

    parser.add_argument(
        '-nth',
        '--n_threads',
        metavar='',
        type=int,
        default=1,
        help='number of threads per job'
    )

    # --------------------------------------------------------------
    # Cluster settings
    # --------------------------------------------------------------

    parser.add_argument(
        '-c',
        '--cluster_name',
        metavar='',
        type=str,
        default='OSG',
        help='cluster name'
    )

    parser.add_argument(
        '--node_type',
        metavar='',
        type=str,
        default='CPU',
        help='node type'
    )

    # --------------------------------------------------------------
    # Files
    # --------------------------------------------------------------

    parser.add_argument(
        '-singularity',
        '--singularity_image_path',
        metavar='',
        type=str,
        default="",
        help='path to .sif image'
    )

    parser.add_argument(
        '-param',
        '--param_file',
        metavar='',
        type=str,
        default="",
        help='parameter file'
    )

    parser.add_argument(
        '-jobid',
        '--job_name',
        metavar='',
        type=str,
        default="test",
        help='job name'
    )

    parser.add_argument(
        '-bayes',
        '--bayes_file',
        metavar='',
        type=str,
        default="",
        help='bayes file'
    )

    parser.add_argument(
        '-mem',
        '--memory_per_job',
        metavar='',
        type=int,
        default=2,
        help='memory per job (GB)'
    )

    parser.add_argument(
        '-seed_file',
        '--seed_file',
        metavar='',
        type=str,
        default="",
        help='isobar nucleon seed HDF5 file'
    )

    parser.add_argument(
        '-random_seed',
        metavar='',
        type=int,
        default=-1,
        help='random seed passed to generate_jobs.py'
    )

    # --------------------------------------------------------------
    # Optional flags
    # --------------------------------------------------------------

    parser.add_argument(
        '--nocopy',
        action='store_true',
        help='pass nocopy flag to generate_jobs.py'
    )

    parser.add_argument(
        '--continueFlag',
        action='store_true',
        help='continue unfinished events'
    )

    if len(sys.argv) < 2:
        parser.print_help()
        exit(0)

    para_dict = vars(parser.parse_args())

    para_dict["bayesFlag"] = para_dict["bayes_file"] != ""

    main(para_dict)
