#!/bin/bash
# This script is only for exploratory analysis to see how much SINGER is affected by sample size variation

# Defines the log file to store the results of the times
LOGFILE="runtime_log.txt"

# Clears the old log file
echo "" > $LOGFILE

# Function to run the command and record the time
run_and_log() {
    VCF_FILE=$1
    SAMPLE_SIZE=$(echo $VCF_FILE | grep -oP 'samples_size_\K\d+')

    # Builds the command
    CMD="SINGER/releases/singer-0.1.7-beta-linux-x86_64/singer_master -Ne 1e4 -m 2e-8 -vcf singer_time/vcf/${VCF_FILE} -output singer_time/inferred/${VCF_FILE}/${VCF_FILE} -start 0 -end 1e4 -n 1000 -thin 10"

    # Executes the command and measures the time
    START_TIME=$SECONDS
    $CMD
    ELAPSED_TIME=$(($SECONDS - $START_TIME))

    # Saves the execution time in the logfile with details
    echo "Sample size ${SAMPLE_SIZE}, VCF file ${VCF_FILE}, Time: ${ELAPSED_TIME} seconds" >> $LOGFILE
}

# List of all VCF files for which the commands will be executed
vcf_files=(   
    # VCF directories and files list
    # "msprime_NoMig_ID_10_samples_size_10_chrlen_10000000.0_N_main_10000_mu_2e-08_rho_1e-08"
    # "msprime_NoMig_ID_10_samples_size_150_chrlen_10000000.0_N_main_10000_mu_2e-08_rho_1e-08"
)

# Executes the function for each VCF file
for vcf in "${vcf_files[@]}"
do
    run_and_log $vcf
done

