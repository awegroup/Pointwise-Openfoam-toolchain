"""Append config.dat to CFD_profile_results"""
import os

# Define file paths
config_abs_path = os.getcwd()
config_file = os.path.join(config_abs_path, "config_data.dat")  # Source file with config data
config_output_file = os.path.join(config_abs_path, "../../OF_Results/CFD_profile_results.dat")  # Target file

# Define your header line
header = "#Re Config_a Cd Cs Cl CmRoll CmPitch CmYaw Cd(f) Cd(r) Cs(f) Cs(r) Cl(f) Cl(r) xcp Ux_final Uy_final k_final p_final omega_final Cl_res Cd_res Cm_res Iter yplus_max"

# Ensure the target directory exists
os.makedirs(os.path.dirname(config_output_file), exist_ok=True)

# Check if the output file exists and already contains the header
def file_contains_header(file_path, header_line):
    try:
        with open(file_path, 'r') as f:
            return header_line in f.read()
    except FileNotFoundError:
        return False

if not file_contains_header(config_output_file, header):
    with open(config_output_file, 'w') as datfile:
        datfile.write(header + "\n")

# Append the contents of config_data.dat to the config_output_file
# writing only lines that do NOT start with "#"
with open(config_file, 'r') as infile, open(config_output_file, 'a') as outfile:
    for line in infile:
        if not line.startswith("#"):
            outfile.write(line)