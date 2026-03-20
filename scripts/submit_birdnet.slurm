#!/bin/bash

# Copy/paste this job script into a text file and submit with the command:
#    sbatch thefilename
# Job standard output will go to the file slurm-%j.out (where %j is the job ID)

#SBATCH --job-name=birdnet_analysis
#SBATCH --partition=instruction    # Use the instruction partition
#SBATCH --nodes=1   # Number of nodes to use
#SBATCH --ntasks-per-node=48   # Use 48 processor cores per node 
#SBATCH --time=2-0:0:0   # Walltime limit (DD-HH:MM:SS)
#SBATCH --mem=200G   # Maximum memory per node
#SBATCH --account=s2026.ds.4010.01   # Slurm account to use for the job
#SBATCH --qos=instruction   # Quality of service
#SBATCH --mail-user=devonk@iastate.edu   # Email address
#SBATCH --mail-type=BEGIN,END,FAIL

# LOAD MODULES, INSERT CODE, AND RUN YOUR PROGRAMS HERE

# Load required modules
module load python/3.9
module load cuda/11.8

# Change to the scripts directory
cd DS4020-Birds/scripts

# Run the BirdNET script
python birdnetlib_basics.py