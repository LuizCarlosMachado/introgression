#!/bin/bash

# USage example with no CHR WINSTART WINEND info : ./2.summarie_ARG.sh intro_tracts_sim_SP_B2A_1mb outputs/intro_tracts_sim_SP_B2A_1mb_hapmig.txt outputs/summary
# USage example with CHR WINSTART WINEND info : ./2.summarie_ARG.sh intro_tracts_sim_SP_B2A_1mb outputs/intro_tracts_sim_SP_B2A_1mb_hapmig.txt outputs/summary 1 50 999889
# RUNAME: Prefix for input files
# HAPMIGF: Hap-mig file generated in previous step
# OUTPREF: Prefix for output files
# CHR, WINSTART, WINEND (optional): Define the genomic region to analyze

# Ensure at least 3 arguments are provided
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 RUNAME HAPMIGF OUTPREF [CHR WINSTART WINEND]"
    exit 1
fi

# Assign input parameters
RUNAME=$1
HAPMIGF=$2
OUTPREF=$3

# Optional arguments for region filtering
USE_REGION=false
if [ "$#" -eq 6 ]; then
    USE_REGION=true
    CHR=$4
    WINSTART=$5
    WINEND=$6
    echo "Using genomic region: CHR=$CHR, START=$WINSTART, END=$WINEND"
fi

# Output logging
LOG_FILE="${OUTPREF}_pipeline.log"
echo "Starting ARG processing pipeline: $(date)" | tee -a $LOG_FILE

# Ensure required files exist
if [ ! -f "outputs/${RUNAME}.10.smc.gz" ]; then
    echo "ERROR: Missing SMC file outputs/${RUNAME}.10.smc.gz" | tee -a $LOG_FILE
    exit 1
fi

if [ ! -f "$HAPMIGF" ]; then
    echo "ERROR: Missing hap-mig file $HAPMIGF" | tee -a $LOG_FILE
    exit 1
fi

# Step 1: Convert ARG to BED format 
echo "Running smc2bed-all..." | tee -a $LOG_FILE
smc2bed-all outputs/${RUNAME}
echo "Completed smc2bed-all." | tee -a $LOG_FILE

# Step 2: Summarize migration events 

echo "Running arg-summarize without region filtering..." | tee -a $LOG_FILE
arg-summarize --log-file outputs/${RUNAME}.log \
              -a outputs/${RUNAME}.bed.gz \
              --burnin 4500 \
              --mean \
              --hap-mig-file $HAPMIGF | bgzip > ${OUTPREF}.migStatsHap.bed.gz
ARG_STATUS=$?

if [ $ARG_STATUS -ne 0 ]; then
    echo "ERROR: arg-summarize failed with exit status $ARG_STATUS" | tee -a $LOG_FILE
    exit 1
fi
echo "Completed basic arg-summarize." | tee -a $LOG_FILE

# Step 3: Summarize migration events with region filtering 

if [ "$USE_REGION" = true ]; then
    echo "Running arg-summarize with region filtering..." | tee -a $LOG_FILE
    arg-summarize --log-file outputs/${RUNAME}.log \
                  -a outputs/${RUNAME}.bed.gz \
                  --burnin 4500 \
                  -r ${CHR}:${WINSTART}-${WINEND} \
                  --mean \
                  --hap-mig-file $HAPMIGF | bgzip > ${OUTPREF}.migStatsHap_region.bed.gz

    if [ $? -ne 0 ]; then
        echo "ERROR: arg-summarize with region filtering failed." | tee -a $LOG_FILE
    else
        echo "Completed arg-summarize with region filtering." | tee -a $LOG_FILE
    fi
fi

# Finalize
echo "Pipeline completed successfully at $(date)." | tee -a $LOG_FILE
exit 0
