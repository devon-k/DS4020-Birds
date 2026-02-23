# DS4020-Birds

## Pipeline Rough Draft Outline
1. Copy audio files from lss to inputs directory
2. Run audio files through bird net
    * Store outputs in output directory
    * Delete audio file from inputs
    * Clean audio file, if time allows
3. Compile output files into one large csv
    * make visualizations/dashboards from this csv
    * other analyzations of data

## Set up Intructions
1. Clone GitHub
3. Rename "config.py.template" as "config.py"
5. Install Libraries
   * librosa
   * tesorflow
   * resampy
   * birdnetlib
   * pandas
6. Run copy_inputs.py, birdnetlib_basics.py, then consolidate_outputs.py
