import msprime
import numpy as np
from IPython.display import SVG
import tskit
import pandas as pd
import os

# Define populations involved in migration
POP_source_migration = "B"  # Donor population
POP_dest_migration = "A"  # Recipient population

def run_simulation(sequence_length, random_seed=None):
    # Divergence time between populations
    tau_AB = 5000  # Divergence time between A and B (in generations)
    tau_ABC = 10000  # Divergence time between AB and C (older, in generations)

    # Define population size for all populations
    N = 10000  # Effective population size

    # Set up demographic model
    demography = msprime.Demography()
    demography.add_population(name="A", initial_size=N)
    demography.add_population(name="B", initial_size=N)
    demography.add_population(name="C", initial_size=N)

    # Add partial introgression from C to B with 2% migration
    #demography.add_mass_migration(
    #    time=500, source="B", dest="A", proportion=0.05)  # Partial introgression event

    demography.set_migration_rate(source="B", dest="A", rate=0.05)

    # A and B fully merge into AB at time tau_AB
    demography.add_mass_migration(
        time=tau_AB, source="B", dest="A", proportion=1)  # A and B merge

    # Older divergence event between AB and C (equivalent to 10000 generations)
    demography.add_mass_migration(
        time=tau_ABC, source="C", dest="A", proportion=1)  # AB diverges from C

    # Simulate the coalescent process and record migrations
    ts = msprime.sim_ancestry(
        recombination_rate=1e-8,  # Recombination rate
        sequence_length=sequence_length,  # Chromosome length
        samples=[
            msprime.SampleSet(1, ploidy=1, population="A"),  # A sample from population A
            msprime.SampleSet(1, ploidy=1, population="B"),  # A sample from population B
            msprime.SampleSet(1, ploidy=1, population="C"),  # A sample from population C
        ],
        demography=demography,
        record_migrations=True,  # Record migration events
        random_seed=random_seed,  # Random seed for reproducibility
    )

    # Print basic simulation information
    print(f"Simulation of {sequence_length / 10**6}Mb run, using record_migrations=True")
    print(
        "Divergence time A and B:",
        f"{tau_AB} generations",
        f"Divergence time AB and C: {tau_ABC} generations"
    )

    return ts

# Run the simulation with the above settings
ts = run_simulation(20 * 10**6, 1)

# Display the tree
#SVG(ts.draw_svg(size=(800, 300)))

import numpy as np

# Add arguments with explicit populations in functions
def get_migrating_tracts(ts, target_population_name=POP_dest_migration):
    """
    Identifies tracts that migrated to a specific population.
    """
    target_id = [p.id for p in ts.populations() if p.metadata['name'] == target_population_name][0]
    migrating_tracts = []
    for migration in ts.migrations():
        if migration.dest == target_id:
            migrating_tracts.append((migration.left, migration.right))
    return np.array(migrating_tracts)


def get_coalescing_tracts(ts, pop_name_1=POP_dest_migration, pop_name_2=POP_source_migration):
    """
    Finds segments where coalescence occurs within a specific population.
    """
    pop_1_id = [p.id for p in ts.populations() if p.metadata['name'] == pop_name_1][0]
    coalescing_tracts = []
    tract_left = None
    for tree in ts.trees():
        # Considering specific sample nodes in the tree
        mrca_pop = ts.node(tree.mrca(0, 1)).population  # Adjust IDs as needed
        left = tree.interval[0]
        if mrca_pop == pop_1_id and tract_left is None:
            tract_left = left      
        elif mrca_pop != pop_1_id and tract_left is not None:
            coalescing_tracts.append((tract_left, left))
            tract_left = None
    if tract_left is not None:
        coalescing_tracts.append((tract_left, ts.sequence_length))
    return np.array(coalescing_tracts)


def get_pairwise_tracts(ts, sample_1=0, sample_2=1):
    """
    Finds segments between two populations, such as A and B, where coalescence occurs before reaching the root.
    """
    tracts = []
    tract_left = None
    for tree in ts.trees():
        mrca = tree.mrca(sample_1, sample_2)
        left = tree.interval[0]
        if mrca != tree.root and tract_left is None:
            tract_left = left      
        elif mrca == tree.root and tract_left is not None:
            tracts.append((tract_left, left))
            tract_left = None
    if tract_left is not None:
        tracts.append((tract_left, ts.sequence_length))
    return np.array(tracts)


# Apply functions to your TreeSequence `ts`
migrating_tracts = get_migrating_tracts(ts)  # Using POP_dest_migration
within_ab = get_coalescing_tracts(ts)  # Coalescence between POP_dest_migration and POP_source_migration
ab_c_tracts = get_pairwise_tracts(ts, sample_1=0, sample_2=1)  # Adjust `sample_1` and `sample_2` as needed for simulation samples

#migrating_tracts: Segments that migrated to the target population.
#within_ab: Segments where samples from "A" and "B" coalesce within population "A".
#ab_c_tracts: Segments where samples from "A" and "B" share a common ancestor before reaching the root (excluding "C").

# Example output:
print("Migrating Tracts:", migrating_tracts)
print("Coalescing Tracts (A and B):", within_ab)
print("Tracts between A and B with common ancestor before C:", ab_c_tracts)

