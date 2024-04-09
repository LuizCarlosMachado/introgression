import msprime
import sys

# This script is now designed to run from the command line, taking 10 arguments
# Usage: python 1_sim_mig.py 10000 10000 10000 5000 0.029 2e-8 1e-8 1e4 10 1
# Parameters examples from: https://popsim-consortium.github.io/stdpopsim-docs/stable/catalog.html#sec_catalog_homsap_models_outofafrica_3g09

# Check if the correct number of arguments was provided
if len(sys.argv) < 11:
    print("Usage: python 1_sim_mig.py N_anc N_main N_ghost tau m mu rho chrlen samples_size sim_id")
    sys.exit(1)

# Assign each argument to a variable, converting to the appropriate type
N_anc = int(sys.argv[1])  # Ancestral population size, 10000
N_main = int(sys.argv[2])  # Main population size, 10000
N_ghost = int(sys.argv[3])  # Ghost population size, 10000
tau = int(sys.argv[4])  # Split time, 5000
m = float(sys.argv[5])  # Migration rate,  0.029 
mu = float(sys.argv[6])  # Mutation rate, 2e-8
rho = float(sys.argv[7])  # Recombination rate, 1e-8 
chrlen = float(sys.argv[8]) # Chromosome length, converted to float, 1e4
samples_size = int(sys.argv[9]) # Number of samples, converted to int, 10
sim_id = sys.argv[10]  # Simulation identifier, kept as string, 1

# Print the input parameters for verification
print(f"Parameters: N_anc={N_anc}, N_main={N_main}, N_ghost={N_ghost}, tau={tau}, m={m}, mu={mu}, rho={rho}, chrlen={chrlen}, samples_size={samples_size}, sim_id={sim_id}")

# Configure the demography for the simulation
demography = msprime.Demography()
demography.add_population(name="Main", initial_size=N_main)
demography.add_population(name="Ghost", initial_size=N_ghost)
demography.add_population(name="Anc", initial_size=N_anc)
demography.add_population_split(time=tau, derived=["Main", "Ghost"], ancestral="Anc")
demography.set_migration_rate(source="Main", dest="Ghost", rate=m)

# Simulate ancestry and mutations
ts_sim = msprime.sim_ancestry(samples={"Main":samples_size}, demography=demography, sequence_length=chrlen, recombination_rate=rho, ploidy=2)
ts_sim = msprime.sim_mutations(ts_sim, rate=mu, model="jc69")

# Save simulation results in VCF and tskit format, with names according to the input parameters and simulation ID
filename_prefix = f"msprime_Mig_ID_{sim_id}_samples_size_{samples_size}_chrlen_{chrlen}_N_anc_{N_anc}_N_main_{N_main}_N_ghost_{N_ghost}_tau_{tau}_m_{m}_mu_{mu}_rho_{rho}"
ts_sim.dump(f"{filename_prefix}.trees")
with open(f"{filename_prefix}.vcf", "w") as vcf_file:
    ts_sim.write_vcf(vcf_file)

