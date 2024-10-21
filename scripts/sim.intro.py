import msprime
import tskit
import pandas as pd
import numpy as np
import os

# Define simple parameters
N = 1000  # Population size
tau2 = 5000  # Divergence time between A and B
tau1 = 10000  # Divergence time between AB and C (older)
mu = 1e-7  # Mutation rate
rho = 1e-7  # Recombination rate
chrom_length = 1e4  # Small chromosome

# Define the number of individuals in each population
num_individuals_A = 5
num_individuals_B = 5
num_individuals_C = 1

# List of migration rates to test
mig_rates = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]

# Create a list to store data from all simulations
all_data = []

# Loop over different migration rates
for mig_rate in mig_rates:
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

    # Create the samples automatically
    samples = ([msprime.SampleSet(1, population="A", ploidy=1) for _ in range(num_individuals_A)] +
               [msprime.SampleSet(1, population="B", ploidy=1) for _ in range(num_individuals_B)] +
               [msprime.SampleSet(1, population="C", ploidy=1) for _ in range(num_individuals_C)])

    # Continue with the simulation
    ts = msprime.sim_ancestry(
        samples=samples,
        demography=demography,
        sequence_length=chrom_length,
        recombination_rate=rho,
        random_seed=42
    )

    # Create a list to store data from 100 trees for the current mig_rate
    data = []

    # Loop to generate 100 trees
    for tree_id in range(1, 101):  # IDs from 1 to 100
        # Choose a random position on the genome
        pos = np.random.uniform(0, ts.sequence_length)
        
        # Get the tree at the chosen position
        tree = ts.at(pos)
        
        # Define samples from A and B (population A and B)
        pop_A = list(range(num_individuals_A))
        pop_B = list(range(num_individuals_A, num_individuals_A + num_individuals_B))
        
        # Calculate TMRCA between populations A and B (X)
        tmrca_X = tree.tmrca(pop_A[0], pop_B[0])
        
        # Calculate TMRCA between AB and C (X + Y)
        pop_C = [num_individuals_A + num_individuals_B]  # Population C
        tmrca_XY = tree.tmrca(pop_A[0], pop_C[0])  # Or pop_B[0] is also equivalent
        
        # Calculate the Y value (difference between X+Y and X)
        tmrca_Y = tmrca_XY - tmrca_X

        # Calculate proportions X/(X+Y) and Y/(X+Y)
        if tmrca_XY > 0:  # Avoid division by zero
            tmrca_XtoXY = tmrca_X / tmrca_XY
            tmrca_YtoXY = tmrca_Y / tmrca_XY
        else:
            tmrca_XtoXY = np.nan  # If X+Y is zero, set NaN (can adjust as needed)
            tmrca_YtoXY = np.nan

        # Store the results in the data list
        data.append({
            'id': tree_id,
            'mig_rate': mig_rate,
            'tmrca_X': tmrca_X,
            'tmrca_Y': tmrca_Y,
            'tmrca_XY': tmrca_XY,
            'tmrca_XtoXY': tmrca_XtoXY,
            'tmrca_YtoXY': tmrca_YtoXY
        })

    # Add the data from this simulation to the main list
    all_data.extend(data)

# Create a DataFrame with the results from all simulations
df = pd.DataFrame(all_data)

# Define the path to save the CSV file in the current directory
output_dir = os.getcwd()  # Get the current working directory
output_file = os.path.join(output_dir, 'tmrca_data.csv')

# Save the DataFrame as CSV
df.to_csv(output_file, index=False)

# Display a confirmation message
print(f"DataFrame saved as 'tmrca_data.csv' in {output_dir}")

