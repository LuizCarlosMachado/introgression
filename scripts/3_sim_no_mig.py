import msprime
import sys

# This script is designed to run from the command line, taking 7 arguments
# Usage: python 3_sim_no_mig.py 10000 2e-8 1e-8 1e5 100 1
# Parameters examples from: https://popsim-consortium.github.io/stdpopsim-docs/stable/catalog.html

# Check if the correct number of arguments was provided
if len(sys.argv) < 7:
    print("Usage: python 3_sim_no_mig.py N_main mu rho chrlen samples_size sim_id")
    sys.exit(1)

# Assign each argument to a variable, converting to the appropriate type
N_main = int(sys.argv[1])  # Main population size
mu = float(sys.argv[2])  # Mutation rate
rho = float(sys.argv[3])  # Recombination rate
chrlen = float(sys.argv[4]) # Chromosome length, converted to float
samples_size = int(sys.argv[5]) # Number of samples, converted to int
sim_id = sys.argv[6]  # Simulation identifier, kept as string

# Print the input parameters for verification
print(f"Parameters: N_main={N_main}, mu={mu}, rho={rho}, chrlen={chrlen}, samples_size={samples_size}, sim_id={sim_id}")

# Configure the demography for the simulation
demography = msprime.Demography()
demography.add_population(name="Main", initial_size=N_main)

# Simulate ancestry and mutations
ts_sim = msprime.sim_ancestry(samples=samples_size, demography=demography, sequence_length=chrlen, recombination_rate=rho, ploidy=2)
ts_sim = msprime.sim_mutations(ts_sim, rate=mu, model="jc69")

# Save simulation results in VCF and tskit format, with names according to the input parameters and simulation ID
filename_prefix = f"msprime_NoMig_ID_{sim_id}_samples_size_{samples_size}_chrlen_{chrlen}_N_main_{N_main}_mu_{mu}_rho_{rho}"
ts_sim.dump(f"{filename_prefix}.trees")
with open(f"{filename_prefix}.vcf", "w") as vcf_file:
    ts_sim.write_vcf(vcf_file)
