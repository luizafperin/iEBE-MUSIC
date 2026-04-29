#!/bin/bash

(
    cd hadronic_afterburner_toolkit
   ./hadronic_afterburner_tools.e analyze_HBT=0 2>&1  >> run.log
)
