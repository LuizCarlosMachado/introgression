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
num_individuals_A = 500
num_individuals_B = 500
num_individuals_C = 1

# List of migration rates to test
mig_rates = [0, 0.0001, 0.0005, 0.001, 0.005, 0.01]

# Define migration type and migration times (can be a list for multiple pulses)
migration_type = "continuous"  # or "massive"
# migration_type = "massive"  # or "continuous"
time_massive = [4000, 3000, 2000, 1000]  # Use a list for n pulses or a single value for one pulse

# Create a list to store data from all simulations
all_data = []

# Loop through each migration rate
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

    # Check migration type
    if migration_type == "massive":
        if isinstance(time_massive, list):  # If it's a list of times (multiple pulses)
            for t in time_massive:
                demography.add_mass_migration(time=t, source="B", dest="A", proportion=mig_rate)
        else:  # If it's just a single pulse
            demography.add_mass_migration(time=time_massive, source="B", dest="A", proportion=mig_rate)
        mig_time = time_massive  # Store migration time for record
        output_suffix = "massive_migration"
    elif migration_type == "continuous":
        demography.set_migration_rate(source="B", dest="A", rate=mig_rate)
        mig_time = "cont_since_tau2"  # Store "cont_since_tau2" for record
        output_suffix = "continuous_migration"

    # Sort demographic events
    demography.sort_events()

    # Automatically create the samples
    samples = ([msprime.SampleSet(1, population="A", ploidy=1) for _ in range(num_individuals_A)] +
               [msprime.SampleSet(1, population="B", ploidy=1) for _ in range(num_individuals_B)] +
               [msprime.SampleSet(1, population="C", ploidy=1) for _ in range(num_individuals_C)])

    # Simulate the sequence
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
    for tree_id in range(1, 100):  # IDs from 1 to 100
        # Choose a random position in the genome
        pos = np.random.uniform(0, ts.sequence_length)
        
        # Get the tree at the chosen position
        tree = ts.at(pos)
        
        # Define the samples from A and B (population A and B)
        pop_A = list(range(num_individuals_A))
        pop_B = list(range(num_individuals_A, num_individuals_A + num_individuals_B))
        
        # Calculate TMRCA between populations A and B (X)
        tmrca_X = tree.tmrca(pop_A[0], pop_B[0])
        
        # Calculate TMRCA between AB and C (X + Y)
        pop_C = [num_individuals_A + num_individuals_B]  # Population C
        tmrca_XY = tree.tmrca(pop_A[0], pop_C[0])  # Or pop_B[0] is also equivalent
        
        # Calculate the value of Y (difference between X+Y and X)
        tmrca_Y = tmrca_XY - tmrca_X

        # Calculate the ratios X/(X+Y) and Y/(X+Y)
        if tmrca_XY > 0:  # Avoid division by zero
            tmrca_XtoXY = tmrca_X / tmrca_XY
            tmrca_YtoXY = tmrca_Y / tmrca_XY
        else:
            tmrca_XtoXY = np.nan  # If X+Y is zero, set NaN (can adjust as needed)
            tmrca_YtoXY = np.nan

        # Store the results in the data list
        data.append({
            'migration_type': migration_type,
            'time': ', '.join(map(str, mig_time)) if isinstance(mig_time, list) else mig_time,  # Store times without brackets
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

# Create a DataFrame with the results of all simulations
df = pd.DataFrame(all_data)

# Define the path to save the CSV file in the current directory
output_dir = os.getcwd()  # Get the current working directory
output_file = os.path.join(output_dir, f'tmrca_data_{output_suffix}.csv')

# Save the DataFrame as a CSV
df.to_csv(output_file, index=False)

# Display a confirmation message
print(f"DataFrame saved as 'tmrca_data_{output_suffix}.csv' in {output_dir}")

