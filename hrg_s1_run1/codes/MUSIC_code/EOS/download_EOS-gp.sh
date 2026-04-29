#!/usr/bin/env bash

L=400
S=15
EOS_TYPES=("hrg" "pwr" "w") #select the type to download, where "hrg" is where extrapolate as hrg below 150 MeV, "pwr" is where extrap as power law below 120 MeV, and "w" where interpolate linearly from 110-120 MeV, and use hrg below 110 MeV
SAMPLES=("s0" "s1") #which samples to download, e.g. s0, s1, s2, s3, s4

BASE_URL="https://raw.githubusercontent.com/luizafperin/MUSIC-EOS-data/refs/heads/main/EOS-gp/constrained/l400_s15"  # GitHub raw / server / etc

TARGET_DIR="/home/luizaperin/MUSIC/EOS/EOS-gp/constrained/l${L}_s${S}"
mkdir -p "${TARGET_DIR}"

for eos in "${EOS_TYPES[@]}"; do
  for sample in "${SAMPLES[@]}"; do

    FILE="eos_${eos}_${sample}_l${L}_s${S}.dat"
    URL="${BASE_URL}/${FILE}"

    if [ -f "${TARGET_DIR}/${FILE}" ]; then
      echo "Skipping ${FILE} (already exists)"
      continue
    fi

    echo "Downloading ${FILE}..."

    curl -L -o "${TARGET_DIR}/${FILE}" "${URL}"

  done
done