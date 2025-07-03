"""Post processing VTK, CFD data and CP data"""
import subprocess
import numpy as np
import os
from rdp import rdp


# VTK switch
VTK_paraview = False

### Output surfaces postProcess ###
subprocess.run(['postProcess -func surfaces -latestTime'], shell=True)

### Output yPlus postProcess ###
subprocess.run(['simpleFoam -postProcess -func yPlus'], shell=True)

### Output VTK paraview field ###
if VTK_paraview:
    subprocess.run(['foamToVTK -latestTime'], shell=True)


### Directories for result data ###
config_abs_path = os.path.abspath("../../")
config_output_file = os.path.join(config_abs_path, "config_data.dat")   # Path for config results

# Get the alpha and Re value out
AOA_dir = os.getcwd()
alpha = os.path.basename(AOA_dir).split("_")[-1]

Re_dir = os.path.dirname(AOA_dir)
Re = str(os.path.basename(Re_dir).split("_")[-1])

# config name
config_a_name = str(os.path.basename(config_abs_path) + "_a" + str(alpha))

# Create destination VTK folder if not present
results_vtk_dir = os.path.join("../../../../", "OF_Results", "OF_VTK")
os.makedirs(results_vtk_dir, exist_ok=True)

# Define target folder
target_dir = os.path.join(results_vtk_dir, f"VTK_Re{Re}_{config_a_name}")

# Copy the VTK folder from current AOA directory, if it exists
source_vtk = os.path.join(AOA_dir, "VTK")
if os.path.exists(source_vtk):
    subprocess.run(["cp", "-r", source_vtk, target_dir])
else:
    print(source_vtk, "not found for", target_dir)


# Force and Residual paths
force_coeffs_path = "postProcessing/forceCoeffs/1/coefficient.dat"
residuals_path = "postProcessing/solverInfo/1/solverInfo.dat"


### Write results data ###
# Define the header row
header = "#Re Config_a Cd Cs Cl CmRoll CmPitch CmYaw Cd(f) Cd(r) Cs(f) Cs(r) Cl(f) Cl(r) xcp Ux_final Uy_final k_final p_final omega_final Cl_res Cd_res Cm_res Iter yplus_max"

# Try config results output file exists and has content
try:
    with open(config_output_file, 'r') as datfile:
        file_content = datfile.read()
        file_has_header = header in file_content
except FileNotFoundError:
    file_has_header = False  # File does not exist, so no header yet

# Write the header if new or no header
if not file_has_header:
    with open(config_output_file, 'w') as datfile:
        datfile.write(header + "\n")


# Try Force coefficients
try:
    with open(force_coeffs_path, 'r') as f:
        force_lines = f.readlines()
        last_force_line = force_lines[-1].strip().split()
        last_iteration = str(int(last_force_line[0]))
        secondlast_force_line = force_lines[-2].strip().split()

        # COP location
        x_ca = 0.25
        CL = float(last_force_line[3])
        CD = float(last_force_line[1])
        CM = float(last_force_line[5])

        theta = np.arctan(CL / CD)
        phi = theta + np.radians(float(alpha))
        C_R = np.sqrt(CL**2 + CD**2)
        x_cop = x_ca - (CM / (C_R * np.sin(phi)))
        last_force_line.append(str(x_cop))

        # Last force residual
        CL2 = float(secondlast_force_line[3])
        CD2 = float(secondlast_force_line[1])
        CM2 = float(secondlast_force_line[5])
        Cl_residual = abs(CL - CL2)
        Cd_residual = abs(CD - CD2)
        Cm_residual = abs(CM - CM2)

        # Combine the residuals into a string
        force_residuals_data = f"{Cl_residual} {Cd_residual} {Cm_residual}"

        # Exclude the iteration number
        last_force_line = last_force_line[1:]

except FileNotFoundError:
    last_iteration = "N/A"
    last_force_line = ["N/A"] * 13    # Placeholder if coefficient.dat is missing
    force_residuals_data = ["N/A"] * 3


# Try Residuals
try:
    with open(residuals_path, 'r') as f:
        residuals_lines = f.readlines()
        last_residuals_line = residuals_lines[-1].strip().split()

        # Extract residual values
        Ux_final = last_residuals_line[3]
        Uy_final = last_residuals_line[6]
        k_final = last_residuals_line[11]
        p_final = last_residuals_line[16]
        omega_final = last_residuals_line[21]

        # Combine the residuals into a string
        residuals_data = f'{Ux_final} {Uy_final} {k_final} {p_final} {omega_final}'

except FileNotFoundError:
    residuals_data = "N/A N/A N/A N/A N/A"  # Placeholder if solverInfo.dat is missing


# Try yplus
yplus_path = "postProcessing/yPlus/" + last_iteration + "/yPlus.dat"
try:
    with open(yplus_path, 'r') as f:
        yplus_lines = f.readlines()
        last_yplus_line = yplus_lines[-1].strip().split()
        yplus_max = last_yplus_line[3]
        yplus_data = f"{yplus_max}"

except FileNotFoundError:
    yplus_data = "N/A"  # Placeholder if yPlus.dat is missing


# Combine: configuration, Forces, Residuals and yplus max
combined_line = Re + " " + config_a_name + " " + " ".join(last_force_line) + " " + residuals_data + " " + force_residuals_data + " " + last_iteration + " " + yplus_data

# Append the combined data to the polar output file
with open(config_output_file, 'a') as datfile:
    datfile.write(combined_line + "\n")


### Cp data ###
# File path
pressure_file_path = "postProcessing/surfaces/" + last_iteration + "/p_airfoilSurface.raw"
cp_output_file_path = f"../../../../OF_Results/OF_Cp/cp_Re{Re}_{config_a_name}.dat"

data = []
with open(pressure_file_path, 'r') as f:
    for line in f:
        if line.startswith('#'):
            continue

        # Split each line into its components (x, y, z, Cp)
        parts = line.split()

        # Check if the line has at least 4 columns (x, y, z, Cp)
        if len(parts) >= 4:
            x = float(parts[0])
            y = float(parts[1])
            z = float(parts[2])
            Cp = float(parts[3])*2

            # Only include the data where z is not equal to 1
            if z != 1:
                data.append((x, y, Cp))

data = np.array(data)


# Apply RDP to x and Cp only
reduced_points = rdp(data[:, [0, 2]], epsilon=0.004)  # Get reduced indices, modify eps to desired data resolution, smaller equals more resolution

# Add Y value to reduced data again to plot the according airfoil shape with it
reduced_data = []
for point in reduced_points:
    # Find indices where x and Cp match the reduced point
    indices = np.where((np.isclose(data[:, 0], point[0])) & (np.isclose(data[:, 2], point[1])))[0]

    # Check if at least one match is found
    if len(indices) > 0:
        # Use the first match (in case there are duplicates)
        idx = indices[0]
        reduced_data.append(data[idx])

reduced_data = np.array(reduced_data)

# Write reduced data to dat file
with open(cp_output_file_path, 'w') as f:
    f.write('# x y Cp\n')  # Header
    for x, y, Cp in reduced_data:
        f.write(f"{x} {y} {Cp}\n")



### Cf data ###
# File path
wallshear_file_path = "postProcessing/surfaces/" + last_iteration + "/wallShearStress_airfoilSurface.raw"
cf_output_file_path = f"../../../../OF_Results/OF_Cf/cf_Re{Re}_{config_a_name}.dat"

data = []
with open(wallshear_file_path, 'r') as f:
    for line in f:
        if line.startswith('#'):
            continue

        # Split each line into its components (x, y, z, tau_x, tau_y, tau_z)
        parts = line.split()

        # Check if the line has at least 6 columns (x, y, z, tau_x, tau_y, tau_z)
        if len(parts) >= 6:
            x = float(parts[0])
            y = float(parts[1])
            z = float(parts[2])
            Cf = -float(parts[3])*2

            # Only include the data where z is not equal to 1
            if z != 1:
                data.append((x, y, Cf))

data = np.array(data)


# Apply RDP to x and Cf only
reduced_points = rdp(data[:, [0, 2]], epsilon=0.0001)  # Get reduced indices, modify eps to desired data resolution, smaller equals more resolution

# Add Y value to reduced data again to plot the according airfoil shape with it
reduced_data = []
for point in reduced_points:
    # Find indices where x and Cf match the reduced point
    indices = np.where((np.isclose(data[:, 0], point[0])) & (np.isclose(data[:, 2], point[1])))[0]

    # Check if at least one match is found
    if len(indices) > 0:
        # Use the first match (in case there are duplicates)
        idx = indices[0]
        reduced_data.append(data[idx])

reduced_data = np.array(reduced_data)

# Write reduced data to dat file
with open(cf_output_file_path, 'w') as f:
    f.write('# x y Cf\n')  # Header
    for x, y, Cf in reduced_data:
        f.write(f"{x} {y} {Cf}\n")