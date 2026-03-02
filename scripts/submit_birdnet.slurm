#SBATCH --job-name=birdnet_analysis
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16GB
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --output=birdnet_%j.out
#SBATCH --error=birdnet_%j.err

# Load required modules
module load python/3.9
module load cuda/11.8

# Activate your Python environment (adjust path as needed)
source /path/to/your/venv/bin/activate

# Change to the scripts directory
cd /path/to/DS4020-Birds/scripts

# Run the BirdNET script
python run_asynchronous_processing.py