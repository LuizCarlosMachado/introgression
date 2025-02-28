import os

# Parameters
event_base = "B2A_mig"  # Migration event name
recipient_pop = 1  # Population receiving migrants
source_pop = 0  # Population donating migrants
migration_time = 1000  # Migration time in generations
output_dir = "outputs"
output_file = f"{output_dir}/intro_tracts_sim_SP_B2A_1mb_hapmig.txt"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# List of haplotypes extracted from the .smc file
haplotypes_smc = [
    "A_1_2", "B_1_1", "C_0_2", "A_2_2", "B_4_1", "B_9_1", "B_0_2", "B_9_2", "A_7_1", "A_5_1", "A_5_2",
    "B_3_2", "A_7_2", "C_0_1", "A_9_2", "A_3_1", "B_2_2", "A_2_1", "B_1_2", "B_0_1", "B_5_1", "A_1_1",
    "B_8_1", "B_2_1", "B_5_2", "B_4_2", "B_6_1", "B_8_2", "A_4_1", "B_6_2", "A_0_2", "A_6_1", "A_6_2",
    "A_8_2", "B_3_1", "A_3_2", "A_0_1", "B_7_1", "A_4_2", "A_9_1", "B_7_2", "A_8_1"
]

# Generate hapmig file content
hapmig_lines = [
    f"{event_base}_{hap}\t{recipient_pop}\t{source_pop}\t{migration_time}\t{hap}"
    for hap in haplotypes_smc
]

# Write to file
with open(output_file, "w") as f:
    f.write("\n".join(hapmig_lines) + "\n")

# Confirmation message
print(f"Hapmig file created: {output_file}")
print("First 5 lines preview:")
print("\n".join(hapmig_lines[:5]))


