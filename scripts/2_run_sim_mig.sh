#!/bin/bash

# Parâmetros constantes
N_anc=10000
N_main=10000
N_ghost=10000
tau=5000
m=0.029
mu=2e-8
rho=1e-8
chrlen=1e7
samples_size=10

# Executa o script Python 100 vezes com IDs de simulação únicos
for sim_id in {1..100}; do
    python 1_sim_mig.py $N_anc $N_main $N_ghost $tau $m $mu $rho $chrlen $samples_size $sim_id
done

# Make the Script Executable
# chmod +x 2_run_sim_mig.sh
# Usage
# ./2_run_sim_mig.sh