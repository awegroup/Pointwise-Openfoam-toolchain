"""Sets up the directory structure for the profiles and creates the AOA cases in OF_Ref"""
import LEI_Parametric
import Pointwise_LEI
import os
import re
import numpy as np
import subprocess
from Profile_Writer import range_Re, process_configs_from_bottom


# Directories
root_path = r"/<dir>/"
profile_configs_dat = root_path + "OF_Setup/profile_configs.dat"
pointwise_exe = r"/<dir>/Pointwise.exe"
glyph_script_path = root_path + "OF_Setup/LEI_Mesh3.glf"

# Mesh based on max Re from Profile_Writer
Re = max(range_Re)


"""Call config directory writer"""
# For testing process_all can be switched to False, to only process the last line
process_configs_from_bottom(Re, process_all=True, pointwise_exe=pointwise_exe, glyph_script_path=glyph_script_path)