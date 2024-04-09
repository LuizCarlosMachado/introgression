#!/bin/bash

# Define constant parameters
N_main=10000     # Main population size
mu=2e-8          # Mutation rate
rho=1e-8         # Recombination rate
chrlen=1e4       # Chromosome length
samples_size=10  # Number of samples

# Loop to execute the Python script for 100 unique simulation IDs
for sim_id in {1..100}; do
    python 3_sim_no_mig.py $N_main $mu $rho $chrlen $samples_size $sim_id
done

# Make the Script Executable
# chmod +x 4_run_sim_no_mig.sh
# Usage
# ./4_run_sim_no_mig.sh