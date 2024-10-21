python
Copiar código
import msprime
import tskit
from IPython.display import SVG, display

# Define simple parameters
N = 1000  # Population size
tau2 = 5000  # Divergence time between A and B
tau1 = 10000  # Divergence time between AB and C (older)
mu = 1e-7  # Mutation rate
rho = 1e-7  # Recombination rate
chrom_length = 1e4  # Small chromosome length
mig_rate = 0.05  # Migration rate from B to A

# Define the demographic model with populations and splits
demography = msprime.Demography()
demography.add_population(name="A", initial_size=N)
demography.add_population(name="B", initial_size=N)
demography.add_population(name="C", initial_size=N)
demography.add_population(name="AB", initial_size=N)
demography.add_population(name="ABC", initial_size=N)

# Population splits
demography.add_population_split(time=tau2, derived=["A", "B"], ancestral="AB")
demography.add_population_split(time=tau1, derived=["AB", "C"], ancestral="ABC")

# Recent migration from B to A
demography.set_migration_rate(source="B", dest="A", rate=mig_rate)

# Define the number of individuals in each population
num_individuos_A = 5
num_individuos_B = 5
num_individuos_C = 1

# Automatically create samples
samples = ([msprime.SampleSet(1, population="A", ploidy=1) for _ in range(num_individuos_A)] +
           [msprime.SampleSet(1, population="B", ploidy=1) for _ in range(num_individuos_B)] +
           [msprime.SampleSet(1, population="C", ploidy=1) for _ in range(num_individuos_C)])

# Continue with the simulation
ts = msprime.sim_ancestry(
    samples=samples,
    demography=demography,
    sequence_length=chrom_length,
    recombination_rate=rho,
    random_seed=42
)

