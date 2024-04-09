#!/bin/bash

# Define constant parameters
N_main=10000     # Main population size
mu=2e-8          # Mutation rate
rho=1e-8         # Recombination rate
chrlen=1e5       # Chromosome length

# Loop to execute the Python script for 100 unique simulation IDs
for sim_id in {1..100}; do
    python 3_sim_no_mig.py $N_main $mu $rho $chrlen 100 $sim_id
done

# Make the Script Executable
# chmod +x 3_sin_no_mig.sh
# Usage
# ./3_sin_no_mig.sh
