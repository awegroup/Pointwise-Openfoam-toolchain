import subprocess
import numpy as np
import os
import matplotlib.pyplot as plt
from rdp import rdp
import matplotlib.font_manager as fm
from matplotlib import rcParams

# Define font path
font_path = "/<dir>/.local/share/fonts/ARIAL.TTF"
fm.fontManager.addfont(font_path)
arial_font = fm.FontProperties(fname=font_path)
arial_name = arial_font.get_name()  # Typically returns "Arial"
rcParams['font.family'] = arial_name

def fond_size(width_overleaf, width_figure):
    windth_fig_page = 21*width_overleaf*0.9
    ratio = width_figure*2.54/windth_fig_page
    overleaf_font = 10
    return overleaf_font * ratio

def compute_alpha_pointwise(Re, alpha, previous_alpha, root_path, profile_name):
    parallel_comp = True
    cp_plot = True
    cf_plot = True
    force_plot = True
    residuals_plot = True  # keep on otherwise cp_plot does not work without last iteration value
    steady = True
    unsteady = False
    initialise_sim = False
    VTK_paraview = True
    transition_model = False

    if steady:
        ### Create the working directory ###
        subprocess.run(["mkdir", "-p", "openfoam_runs_pointwise/AOA_" + str(alpha)])   # Create a AOA directory

        ### With transition model ###
        if transition_model:
            subprocess.run(["cp", "-r", "openfoam_runs_pointwise/Base_AOA_trans/0", "openfoam_runs_pointwise/Base_AOA_trans/constant", "openfoam_runs_pointwise/Base_AOA_trans/system", "openfoam_runs_pointwise/AOA_" + str(alpha)])    # Copying Base_AOA folders
            subprocess.run(["cp", "-r", "openfoam_runs_pointwise/Base_AOA/polyMesh", "openfoam_runs_pointwise/AOA_" + str(alpha) + "/constant"]) # Copies mesh

        ### Fully turbulent model ###
        else:
            subprocess.run(["cp", "-r", "openfoam_runs_pointwise/Base_AOA/0", "openfoam_runs_pointwise/Base_AOA/constant", "openfoam_runs_pointwise/Base_AOA/system", "openfoam_runs_pointwise/AOA_" + str(alpha)])    # Copying Base_AOA folders
            subprocess.run(["cp", "-r", "openfoam_runs_pointwise/Base_AOA/polyMesh", "openfoam_runs_pointwise/AOA_" + str(alpha) + "/constant"]) # Copies mesh


        ### Change AOA in includeDict  ###
        file_path = 'openfoam_runs_pointwise/AOA_' + str(alpha) + '/system/includeDict'
        with open(file_path, 'r') as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            if 'alpha' in line.split():
                new_lines = np.append(new_lines, 'alpha               ' + str(alpha) + ';\n')
            elif 'Re' in line.split():
                new_lines = np.append(new_lines, 'Re                  ' + str(Re) + ';\n')
            else:
                new_lines = np.append(new_lines, line)

        with open(file_path, 'w') as f:
            f.writelines(new_lines)


        ### Renumber Pointwise mesh to Openfoam mesh ###
        case_dir = "openfoam_runs_pointwise/AOA_" + str(alpha)
        env = os.environ.copy()
        env["PWD"] = os.path.abspath(case_dir)
        subprocess.run(["renumberMesh"], cwd=case_dir, env=env, check=True)


        # Initialises next sim with previous converged simulation field
        if initialise_sim and alpha != previous_alpha:
            subprocess.run(f'mapFields ../AOA_{previous_alpha} -sourceTime latestTime', shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))


        ### Run simpleFoam ###
        if parallel_comp:
            subprocess.run(['decomposePar'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))
            subprocess.run(['mpirun -np 4 simpleFoam -parallel > log'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))
            subprocess.run(['reconstructPar'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))
        else:
            subprocess.run(['simpleFoam > log'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))

        ### Output surfaces postProcess ###
        subprocess.run(['postProcess -func surfaces -latestTime'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))

        ### Output yPlus postProcess ###
        subprocess.run(['simpleFoam -postProcess -func yPlus'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))

        ### Output VTK paraview field ###
        if VTK_paraview:
            subprocess.run(['foamToVTK -latestTime'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))


    ### Unsteady sim ###
    if unsteady:
        ### Create the working directory ###
        subprocess.run(["mkdir", "-p", "openfoam_runs_pointwise/AOA_" + str(alpha) + "_U"])   # Create a AOA directory
        subprocess.run(["cp", "-r", "openfoam_runs_pointwise/Base_AOA_unsteady/0", "openfoam_runs_pointwise/Base_AOA_unsteady/constant", "openfoam_runs_pointwise/Base_AOA_unsteady/system", "openfoam_runs_pointwise/AOA_" + str(alpha) + "_U"])    # Copying Base_AOA_unsteady folders
        subprocess.run(["cp", "-r", "openfoam_runs_pointwise/Base_AOA/polyMesh", "openfoam_runs_pointwise/AOA_" + str(alpha) + "_U" + "/constant"]) # Copies mesh


        ### Change AOA in includeDict  ###
        file_path = 'openfoam_runs_pointwise/AOA_' + str(alpha) + '_U' + '/system/includeDict'
        with open(file_path, 'r') as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            if 'alpha' in line.split():
                new_lines = np.append(new_lines, 'alpha               ' + str(alpha) + ';\n')
            elif 'Re' in line.split():
                new_lines = np.append(new_lines, 'Re                  ' + str(Re) + ';\n')
            else:
                new_lines = np.append(new_lines, line)

        with open(file_path, 'w') as f:
            f.writelines(new_lines)


        ### Renumber Pointwise mesh to Openfoam mesh ###
        case_dir = "openfoam_runs_pointwise/AOA_" + str(alpha) + "_U"
        env = os.environ.copy()
        env["PWD"] = os.path.abspath(case_dir)
        subprocess.run(["renumberMesh"], cwd=case_dir, env=env, check=True)

        subprocess.run(f'mapFields ../AOA_{alpha} -sourceTime latestTime', shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha) + "_U")


        ### Run pimpleFoam ###
        if parallel_comp:
            subprocess.run(['decomposePar'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha) + "_U")
            subprocess.run(['mpirun -np 4 pimpleFoam -parallel > log'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha) + "_U")
            subprocess.run(['reconstructPar'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha) + "_U")
        else:
            subprocess.run(['pimpleFoam > log'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha) + "_U")


        alpha = str(alpha) + "_U"
        ### Output surfaces postProcess ###
        subprocess.run(['pimpleFoam -postProcess -func wallShearStress'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))
        subprocess.run(['postProcess -func surfaces -latestTime'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))

        subprocess.run(['pimpleFoam -postProcess -latestTime'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))
        subprocess.run(['postProcess -latestTime -func CourantNo'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))

        ### Output yPlus postProcess ###
        subprocess.run(['pimpleFoam -postProcess -func yPlus'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))


        ### Output VTK paraview field ###
        if VTK_paraview:
            subprocess.run(['foamToVTK -latestTime'], shell=True, cwd="openfoam_runs_pointwise/AOA_" + str(alpha))




    ### Residual convergence plot ###
    if residuals_plot:
        residual_file_path = "openfoam_runs_pointwise/AOA_" + str(alpha) + "/postProcessing/solverInfo/1/solverInfo.dat"

        # Check if the file exists
        if not os.path.isfile(residual_file_path):
            raise FileNotFoundError(f"The file '{residual_file_path}' does not exist. Please check the file path.")

        # Initialize variables
        iteration = []
        Ux_final = []
        Uy_final = []
        k_final = []
        omega_final = []
        p_final = []

        with open(residual_file_path, "r") as file:
            lines = file.readlines()[2:]

            for line in lines:
                line = line.strip()
                # Split the line into parts
                parts = line.split()

                # Extract relevant columns
                iteration.append(float(parts[0]))
                Ux_final.append(float(parts[3]))
                Uy_final.append(float(parts[6]))
                k_final.append(float(parts[11]))
                p_final.append(float(parts[16]))
                omega_final.append(float(parts[21]))

        min_y = min(
            min(Ux_final), min(Uy_final), min(k_final),
            min(omega_final), min(p_final))

        # Plot residual values
        plt.figure(figsize=(10, 8))
        plt.plot(iteration, Ux_final, label=r'$U_x$', lw=2)
        plt.plot(iteration, Uy_final, label=r'$U_y$', lw=2)
        plt.plot(iteration, k_final, label=r'$k$', lw=2)
        plt.plot(iteration, omega_final, label=r'$\omega$', lw=2)
        plt.plot(iteration, p_final, label=r'$p$', lw=2)
        plt.plot([0, iteration[-1]], [8e-7, 8e-7], "--", color='k', lw=1.5)

        font = fond_size(width_overleaf=0.5, width_figure=10)
        plt.xlabel('Iteration Number [-]', fontsize=font)
        plt.ylabel('Residual Value [-]', fontsize=font)
        plt.yscale('log')
        plt.ylim(bottom=min_y, top=0.1)
        plt.yticks([10**i for i in range(-1, -11, -1)], fontsize=font)
        plt.xticks(fontsize=font)
        plt.legend(fontsize=font)

        plt.grid(True, linestyle='--')
        plt.tight_layout()
        plt.savefig("openfoam_runs_pointwise/AOA_" + str(alpha) + "/postProcessing/solverInfo/1/residuals" + str(alpha) + ".pdf", dpi=300)  # Saving figure to results
        plt.close()

    ### Force coefficient residual plot ###
    if force_plot:
        force_file_path = "openfoam_runs_pointwise/AOA_" + str(alpha) + "/postProcessing/forceCoeffs/1/coefficient.dat"

        # Check if the file exists
        if not os.path.isfile(force_file_path):
            raise FileNotFoundError(f"The file '{force_file_path}' does not exist. Please check the file path.")

        # Initialize variables
        iteration = []
        residual_Cd = []
        residual_Cl = []
        residual_CmPitch = []

        with open(force_file_path, "r") as file:
            lines = file.readlines()[13:]

            # Initial values for residuals
            previous_Cd = 0.0
            previous_Cl = 0.0
            previous_CmPitch = 0.0

            for line in lines:
                # Split the line into parts
                parts = line.split()

                # Extract columns
                iteration.append(float(parts[0]))
                Cd_value = float(parts[1])
                Cl_value = float(parts[3])
                CmPitch_value = float(parts[5])


                # Calculate residuals
                if len(iteration) > 1:
                    residual_Cd.append(abs(Cd_value - previous_Cd))  # Absolute difference for Cd residual
                    residual_Cl.append(abs(Cl_value - previous_Cl))  # Absolute difference for Cl residual
                    residual_CmPitch.append(abs(CmPitch_value - previous_CmPitch))  # Absolute difference for CmPitch residual
                else:
                    residual_Cd.append(0.0)  # First iteration, no residual
                    residual_Cl.append(0.0)  # First iteration, no residual
                    residual_CmPitch.append(0.0)  # First iteration, no residual

                # Update previous values for the next iteration
                previous_Cd = Cd_value
                previous_Cl = Cl_value
                previous_CmPitch = CmPitch_value


        # Plot force residual plot
        plt.figure(figsize=(10, 8))
        plt.plot(iteration, residual_Cd, label='$C_d$', lw=2)
        plt.plot(iteration, residual_Cl, label='$C_l$', lw=2)
        plt.plot(iteration, residual_CmPitch, label='$C_m$', lw=2)
        plt.plot([0, iteration[-1]], [10**-4, 10**-4], "--", color='k', lw=1.5)

        font = fond_size(width_overleaf=0.5, width_figure=10)
        plt.xlabel('Iteration Number [-]', fontsize=font)
        plt.ylabel('Residual Value [-]', fontsize=font)
        plt.yticks([10**i for i in range(-1, -11, -1)], fontsize=font)
        plt.yscale('log')
        plt.xticks(fontsize=font)
        plt.legend(fontsize=font)

        plt.grid(True, linestyle='--')
        plt.tight_layout()
        plt.savefig("openfoam_runs_pointwise/AOA_" + str(alpha) + "/postProcessing/forceCoeffs/1/force_residuals" + str(alpha) + ".pdf", dpi=300)
        plt.close()


    ### Pressure coefficient plot ###
    if cp_plot:
        # File path
        pressure_file_path = "openfoam_runs_pointwise/AOA_" + str(alpha) + "/postProcessing/surfaces/" + str(int(iteration[-1])) + "/p_airfoilSurface.raw"
        cp_output_file_path = "openfoam_runs_pointwise/AOA_" + str(alpha) + "/postProcessing/surfaces/" + str(int(iteration[-1])) + "/cp_AOA_" + str(alpha) + ".dat"

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

        # Add Y value to reduced data
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

        x_vals = data[:, 0]
        y_vals = data[:, 1]
        Cp_vals = data[:, 2]
        x_vals_reduced = reduced_data[:, 0]
        Cp_vals_reduced = reduced_data[:, 2]

        # Plot Cp plot
        plt.figure(figsize=(10, 8))
        plt.plot([-1, 2], [0, 0], color='k', linestyle='--', linewidth=1)
        plt.plot(x_vals, Cp_vals, marker='o', markersize=1.5, linestyle='-', linewidth=3, label="Raw data")
        plt.plot(x_vals_reduced, Cp_vals_reduced, marker='o', markersize=5, linestyle='-', linewidth=1.5, label="Reduced data")

        font = fond_size(width_overleaf=0.5, width_figure=10)
        plt.xlabel(r'x/c [-]', fontsize=font)
        plt.ylabel(r'$C_p$ [-]', fontsize=font)
        plt.xlim([-0.1, 1.1])
        plt.xticks(np.arange(0, 1.1, 0.1), fontsize=font)
        plt.yticks(np.arange(np.ceil(1.2 * np.min(Cp_vals) / 0.5) * 0.5, np.ceil(1.2 * np.max(Cp_vals) / 0.5) * 0.5, 0.5), fontsize=font)
        plt.gca().invert_yaxis()

        plt.legend(fontsize=font)
        plt.grid(True, linestyle='--', lw=0.5)
        plt.tight_layout()
        plt.savefig("openfoam_runs_pointwise/AOA_" + str(alpha) + "/postProcessing/surfaces/" + str(int(iteration[-1])) + "/cp_AOA_" + str(alpha) + ".pdf", dpi=500)  # Saving figure to results
        plt.close()


    ### Friction coefficient plot ###
    if cf_plot:
        # File path
        wallshear_file_path = "openfoam_runs_pointwise/AOA_" + str(alpha) + "/postProcessing/surfaces/" + str(int(iteration[-1])) + "/wallShearStress_airfoilSurface.raw"
        cf_output_file_path = "openfoam_runs_pointwise/AOA_" + str(alpha) + "/postProcessing/surfaces/" + str(int(iteration[-1])) + "/cf_AOA_" + str(alpha) + ".dat"

        data = []
        with open(wallshear_file_path, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue

                # Split each line into its components
                parts = line.split()

                # Check if the line has at least 6 columns
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

        # Add Y value to reduced data again
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

        x_vals = data[:, 0]
        y_vals = data[:, 1]
        Cf_vals = 100*data[:, 2]
        x_vals_reduced = reduced_data[:, 0]
        Cf_vals_reduced = 100*reduced_data[:, 2]

        # Plot Cf plot
        plt.figure(figsize=(10, 8))
        plt.plot([-1, 2], [0, 0], color='k', linestyle='--', linewidth=1)
        plt.plot(x_vals, Cf_vals, marker='o', markersize=2, linestyle='-', linewidth=3, label="Raw data")
        plt.plot(x_vals_reduced, Cf_vals_reduced, marker='o', markersize=5, linestyle='-', linewidth=1.5, label="Reduced data")

        font = fond_size(width_overleaf=0.5, width_figure=10)
        plt.xlabel('x/c [-]', fontsize=font)
        plt.ylabel(r'$C_{f} \times 100 \, [-]$', fontsize=font)
        plt.xlim([-0.1, 1.1])
        plt.xticks(np.arange(0, 1.1, 0.1), fontsize=font)
        plt.yticks(np.arange(np.floor(1.2 * np.min(Cf_vals) / 0.2) * 0.2, np.ceil(1.2 * np.max(Cf_vals) / 0.2) * 0.2, 0.2), fontsize=font)

        plt.grid(True, linestyle='--', lw=0.5)
        plt.legend(fontsize=font)
        plt.tight_layout()
        plt.savefig("openfoam_runs_pointwise/AOA_" + str(alpha) + "/postProcessing/surfaces/" + str(int(iteration[-1])) + "/cf_AOA_" + str(alpha) + ".pdf", dpi=300)  # Saving figure to results
        plt.close()

    ### Write last line of forceCoeffs.dat and residuals (solverInfo.dat) into polar_pointwise.dat ###
    force_coeffs_path = "openfoam_runs_pointwise/AOA_" + str(alpha) + "/postProcessing/forceCoeffs/1/coefficient.dat"
    residuals_path = "openfoam_runs_pointwise/AOA_" + str(alpha) + "/postProcessing/solverInfo/1/solverInfo.dat"
    yplus_path = "openfoam_runs_pointwise/AOA_" + str(alpha) + "/postProcessing/yPlus/" + str(int(iteration[-1])) + "/yPlus.dat"
    output_file = root_path + "/results/polar.dat"

    # Define the header row
    header = "# Alpha Cd Cs Cl CmRoll CmPitch CmYaw Cd(f) Cd(r) Cs(f) Cs(r) Cl(f) Cl(r) xcp Ux_final Uy_final k_final p_final omega_final Cl_res Cd_res Cm_res yplus iter_n"

    # Check if the output file already exists and has content
    try:
        with open(output_file, 'r') as datfile:
            file_content = datfile.read()
            file_has_header = header in file_content
    except FileNotFoundError:
        file_has_header = False  # File does not exist, so no header yet

    # If the file is new or doesn't have a header, write the header
    if not file_has_header:
        with open(output_file, 'w') as datfile:
            datfile.write(header + "\n")


    # Try Force coefficients
    try:
        with open(force_coeffs_path, 'r') as f:
            force_lines = f.readlines()
            last_force_line = force_lines[-1].strip().split()
            secondlast_force_line = force_lines[-2].strip().split()
            last_iteration = str(int(last_force_line[0]))

            # Replace the first value with alpha
            last_force_line[0] = str(alpha)

            # COP location
            x_ca = 0.25
            CL = float(last_force_line[3])
            CD = float(last_force_line[1])
            CM = float(last_force_line[5])

            theta = np.arctan(CL / CD)
            phi = theta + np.radians(alpha)
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

    except FileNotFoundError:
            last_iteration = "N/A"
            last_force_line = ["N/A"] * 13
            force_residuals_data = ["N/A"] * 3

    # Try residual/solverInfo
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
            residuals_data = f"{Ux_final} {Uy_final} {k_final} {p_final} {omega_final}"

    except FileNotFoundError:
        residuals_data = "N/A N/A N/A N/A N/A"

    # Try yplus
    try:
        with open(yplus_path, 'r') as f:
            yplus_lines = f.readlines()
            last_yplus_line = yplus_lines[-1].strip().split()
            yplus_max = last_yplus_line[3]
            yplus_data = f"{yplus_max}"

    except FileNotFoundError:
        yplus_data = "N/A"

    # Combine forces, residuals, force residuals and yplus max
    combined_line = " ".join(last_force_line) + " " + residuals_data + " " + force_residuals_data + " " + yplus_data + " " + last_iteration

    # Append the combined data to the polar output file
    with open(output_file, 'a') as datfile:
        datfile.write(combined_line + "\n")

    return ()
