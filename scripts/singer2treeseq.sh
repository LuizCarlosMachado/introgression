#!/bin/bash

: '
Conversion Attempt History

1. Initial Attempt:
   - Method: Execution via bash script using the convert_to_tskit command directly.
   - Issue: Encountered difficulties with direct command execution, including permission issues.
   - Bash Command Example:
     #!/bin/bash
     SINGER_CONVERTER="PATH/convert_to_tskit"
     if [ ! -x "$SINGER_CONVERTER" ]; then
         echo "convert_to_tskit not found or not executable."
         exit 1
     fi
     for i in {0..214}; do
         echo "Converting files for index $i..."
         $SINGER_CONVERTER -input "output_file_${i}" -output "converted_tskit_${i}" -start 0 -end 10000
         echo "Conversion attempt for index $i completed."
     done
     - The convert_to_tskit command seems expects explicit full names for each of the four input files per index {i}, not just a common prefix and index.

2. Strategy Change:
   - Reason: The initial attempt was unsuccessful due to issues locating the convert_to_tskit command or permission problems.
   - Action: Modified the conversion file extension to `.py` and executed through Python3 for improved control and debugging.
   - Outcome: This adjustment allowed the script to run.

Additional Observations:
- Ensure all paths are correct and execution permissions are set for the involved scripts.
- While the SINGER documentation suggests command-line execution, adapting to a Python script provided more flexibility for debugging.
'

# Difine variable and paths
SCRIPT_PATH="../SINGER/releases/singer-0.1.7-beta-linux-x86_64/convert_to_tskit.py" 
INPUT_PREFIX="../tmp/output_file"
OUTPUT_PREFIX="../tmp/converted_tskit"
START=0
END=214
STEP=1

# excute the python script with the defined parameters
python3 $SCRIPT_PATH -input $INPUT_PREFIX -output $OUTPUT_PREFIX -start $START -end $END -step $STEP

# Make the Script Executable
# chmod +x singer2treeseq.sh
# Usage
# ./singer2treeseq.sh
