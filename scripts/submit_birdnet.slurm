#!/bin/bash

#SBATCH --job-name=birdnet_analysis
#SBATCH --partition=instruction
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=50
#SBATCH --mem=200GB
#SBATCH --time=2-00:00:00
#SBATCH --output=birdnet_%j.out
#SBATCH --error=birdnet_%j.err
#SBATCH --mail-user=devonk@iastate.edu   # Email address
#SBATCH --mail-type=BEGIN,END,FAIL

# Load required modules
module load python/3.9
module load cuda/11.8

# Activate your Python environment (adjust path as needed)
# source /path/to/your/venv/bin/activate

# Change to the scripts directory
cd DS4020-Birds/scripts

# Run the BirdNET script
python birdnetlib_basics.py