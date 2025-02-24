import tskit
import msprime
import numpy as np
import matplotlib.pyplot as plt
import random

# Demographic Parameters
N_anc = 5000   # Ancestral root population size
N_ABC = 5000   # Intermediate population before the separation of C
N_AB = 5000    # Intermediate population before the separation of A and B
N_A = 5000     # Current population size of A
N_B = 5000     # Current population size of B
N_C = 5000        # Outgroup population size (C)

# Divergence Times (in generations)
tau_AB = 10000   # Time of separation between populations A and B
tau_ABC = 50000  # Time of separation between ABC and outgroup C

# Genomic Parameters
mu = 2e-8       # Mutation rate per base pair per generation
rho = 1e-8      # Recombination rate per base pair per generation
chrlen = 2e6    # Length of the simulated chromosome (2 Mb)

# Migration Pulse Parameters
T_mig = 1000    # Time of pulse migration (generations ago)
prop_mig = 0.1  # Proportion of migrants from B to A

# Demography Configuration
demography = msprime.Demography()

# Defining populations
demography.add_population(name="Anc", initial_size=N_anc)
demography.add_population(name="A", initial_size=N_A)
demography.add_population(name="B", initial_size=N_B)
demography.add_population(name="C", initial_size=N_C)

# Defining population splits
demography.add_population_split(time=tau_ABC, derived=["C"], ancestral="Anc")
demography.add_population_split(time=tau_AB, derived=["A", "B"], ancestral="Anc")

# Defining migration pulse from B to A
demography.add_mass_migration(time=T_mig, source="B", dest="A", proportion=prop_mig)

# Sorting events to ensure chronological order
demography.sort_events()

# Running ancestry simulation with migration events
# Simulating 10 diploid samples from A and B, and 1 diploid sample from outgroup C
ts_sim = msprime.sim_ancestry(
    samples={"A": 20, "B": 20, "C": 1},
    demography=demography,
    sequence_length=chrlen,
    recombination_rate=rho,
    ploidy=2,
    record_migrations=True
)

# Function to extract migration tracts between specified populations
def get_migration_tracts(ts, source_pop, dest_pop):
    source_id = [p.id for p in ts.populations() if p.metadata["name"] == source_pop][0]
    dest_id = [p.id for p in ts.populations() if p.metadata["name"] == dest_pop][0]

    migration_tracts = []
    for migration in ts.migrations():
        # Filter migrations based on source, destination, and migration time
        if migration.source == source_id and migration.dest == dest_id and migration.time == T_mig:
            migration_tracts.append((migration.left, migration.right))

    return np.array(migration_tracts)

# Extracting migration tracts from B to A
migration_tracts = get_migration_tracts(ts_sim, source_pop="B", dest_pop="A")

# Checking if migration tracts were found and calculating statistics
if migration_tracts.size == 0:
    print("No migrated tracts were found.")
else:
    tot_mig_tract_len = np.sum(migration_tracts[:, 1] - migration_tracts[:, 0])
    print(f"Total introgression tract length: {tot_mig_tract_len} bp")
    print(f"Proportion of introgressed tracts on the chromosome: {tot_mig_tract_len / ts_sim.sequence_length:.2%}")

# Adding mutations to the simulated ancestry tree
ts_sim = msprime.sim_mutations(ts_sim, rate=mu, random_seed=42)
print(f"Total number of mutations: {ts_sim.num_mutations}")

# Identifying mutations within introgressed tracts
mut_positions = [site.position for site in ts_sim.sites()]
mut_in_migration = sum(
    any(left <= pos < right for left, right in migration_tracts)
    for pos in mut_positions
)
print(f"Mutations within migrated tracts: {mut_in_migration}")

# Output VCF file name
vcf_filename = "output_renamed.vcf"

# Creating custom sample labels
sample_names = []
pop_counts = {"A": 0, "B": 0, "C": 0}  # Counters for sample naming

# Assigning names based on population
for individual in ts_sim.individuals():
    pop_id = ts_sim.node(individual.nodes[0]).population
    pop_name = {1: "A", 2: "B", 3: "C"}.get(pop_id, f"Pop{pop_id}")
    new_label = f"{pop_name}_{pop_counts[pop_name]}"
    pop_counts[pop_name] += 1
    sample_names.append(new_label)

# Exporting VCF file with custom sample names
with open(vcf_filename, "w") as vcf_file:
    ts_sim.write_vcf(vcf_file, individual_names=sample_names)

print(f"VCF saved with custom labels at: {vcf_filename}")