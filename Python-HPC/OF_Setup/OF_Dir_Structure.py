"""Sets up the directory structure for the profiles and creates the AOA cases in OF_Ref"""
import LEI_Parametric
import Pointwise_LEI
import os
import re
import numpy as np
import subprocess
from Profile_Writer import range_Re, process_configs_from_bottom


### Run this script in the HPC/OF_Setup directory ###
# 0. Make sure Profile_configs.dat contains all configurations, written by Profile_Writer.py
# 1. Addapt Re
# 2. Change root_path
# 3. Run test case for one config by switching to --> process_all=False

### Parallel mesh generation ###
# mpirun -np 1 python3 OF_Dir_Structure.py : -np 1 python3 OF_Dir_Structure2.py : -np 1 python3 OF_Dir_Structure3.py : -np 1 python3 OF_Dir_Structure4.py

### Enter HPC ###
# ssh -X <person>@hpc12.tudelft.net

### push command
# scp -r /<dir>/Python-HPC/ <person>@hpc12.tudelft.net:/home/scratch/<person>/

### run command###
# qsub DescriptionFile.pbs

### pull command
# scp -r <person>@hpc12.tudelft.net:/home/scratch/<person>/Python-HPC/OF_Results/ /<dir>/Python-HPC/


# Directories
root_path = r"/<dir>/"
profile_configs_dat = root_path + "OF_Setup/profile_configs.dat"
pointwise_exe = r"/<dir>/Pointwise.exe"
glyph_script_path = root_path + "OF_Setup/LEI_Mesh.glf"

# Mesh based on max Re from Profile_Writer
Re = max(range_Re)


"""Call config directory writer"""
# For testing process_all can be switched to False, to only process the last line
process_configs_from_bottom(Re, process_all=True, pointwise_exe=pointwise_exe, glyph_script_path=glyph_script_path)