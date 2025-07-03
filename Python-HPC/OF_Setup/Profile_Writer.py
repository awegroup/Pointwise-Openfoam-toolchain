"""Writes the desired configurations to Profile_Configs.dat and provides functions to read the file and generate meshes in parallel."""
import numpy as np
import itertools
import subprocess
from collections import defaultdict
import LEI_Parametric
import Pointwise_LEI
import os
import re
from pathlib import Path
import time
import random


# Define file directory
root_path = r"/<dir>/"
profile_configs_dat = "profile_configs.dat"
AOA_file_path = root_path + "OF_Ref"

# Switch
save_png_dat = True

### Study case inputs ###
range_Re = np.array([5e6])                              # Reynolds number
range_AOA = np.array([0, 2, 4, 6, 8, 10])               # AOA range
range_Re = range_Re.astype(int)
all_cases = itertools.product(range_Re, range_AOA)      # Re and AoA cases
all_cases_list = list(all_cases)

# Define parameter ranges
range_cx = np.array([0.2, 0.25])
range_cy = np.array([0.08, 0.1])
range_t = np.array([0.08, 0.1])
range_reflex = np.array([-8, -5, -2, 0])
range_LE = np.array([0.65])
range_camTE = np.array([0.1, 0.2])


# Generate all possible profile combinations
all_configs = itertools.product(range_t, range_cx, range_cy, range_reflex, range_LE, range_camTE)
all_configs_list = list(all_configs)


# Functions
def process_configs_from_bottom(Re, process_all=False, pointwise_exe="nan", glyph_script_path="nan"):
    sleep_time = round(random.uniform(0, 1), 5)
    time.sleep(sleep_time)
    while True:  # Loop until done or error occurs
        # If .dat file not found
        if not os.path.isfile(profile_configs_dat):
            print(f'{profile_configs_dat} not found.')
            return

        # Read lines
        with open(profile_configs_dat, "r") as f:
            lines = f.readlines()

        # Find all non-blank lines and their indices
        nonblank = [(i, ln.strip()) for i, ln in enumerate(lines) if ln.strip()]

        if not nonblank:
            print("No configurations left to process.")
            return

        # Pick the last non-blank line and remove
        last_idx, last_line = nonblank[-1]
        del lines[last_idx]

        # write other configs
        with open(profile_configs_dat, "w") as f:
            f.writelines(lines)

        # Split the line at underscores to separate each parameter
        tokens = last_line.split('_')

        # Create a dictionary to store the values
        params = {}

        # Process each token: separate the alphabetic key from the numeric value.
        for token in tokens:
            # Splits into a key (letters) and a value (numbers, dot, or minus sign)
            m = re.match(r"([A-Za-z]+)([-0-9.]+)", token)
            if m:
                key = m.group(1)
                value = m.group(2)
                params[key] = value

        # Convert matches to integers
        t_val      = params.get("t")
        cx_val     = params.get("cx")
        cy_val     = params.get("cy")
        reflex_val = params.get("r")
        LE_val     = params.get("LE")
        camTE_val  = params.get("camTE")

        # Create upload directory for this config
        success = create_upload_dir(Re, t_val, cx_val, cy_val, reflex_val, LE_val, camTE_val, pointwise_exe, glyph_script_path)

        # If successful, remove this config line and rewrite the file
        if success:
            # If successful print (debug)
            print(f"Succes: {last_line}")
        else:
            # If not successful print (debug)
            print(f"ERROR: {last_line}")
            break

        # TEST, If only one config should be processed, break here
        if not process_all:
            break

def create_upload_dir(Re, t_val, cx_val, cy_val, reflex_val, LE_val, camTE_val, pointwise_exe, glyph_script_path):
    try:
        # Create profile directory
        subprocess.run(["mkdir", "-p", f"../OF_Uploads/t{t_val}_cx{cx_val}_cy{cy_val}_r{reflex_val}_LE{LE_val}_camTE{camTE_val}"])

        # Create the Polymesh directorie and profile png path
        polymesh_dir_location = f"../OF_Uploads/t{t_val}_cx{cx_val}_cy{cy_val}_r{reflex_val}_LE{LE_val}_camTE{camTE_val}/polyMesh"
        subprocess.run(["mkdir", "-p", polymesh_dir_location])
        fig_file_path = f"../OF_Uploads/t{t_val}_cx{cx_val}_cy{cy_val}_r{reflex_val}_LE{LE_val}_camTE{camTE_val}/profile.png"

        # Dir for point file
        profile_p_file_path = Path("../OF_Uploads") / f"t{t_val}_cx{cx_val}_cy{cy_val}_r{reflex_val}_LE{LE_val}_camTE{camTE_val}" / "profile.dat"
        profile_p_file_path.parent.mkdir(parents=True, exist_ok=True)


        # Convert matches to floats
        t_val      = float(t_val)
        cx_val     = float(cx_val)
        cy_val     = float(cy_val)
        reflex_val = float(reflex_val)
        LE_val     = float(LE_val)
        camTE_val  = float(camTE_val)

        # LEI profile instance
        tube_size = t_val
        c_x = cx_val
        c_y = cy_val
        LE_tension = LE_val
        TE_angle = reflex_val
        TE_cam_tension = camTE_val
        TE_tension = 0.2
        e = 0.0005
        LE_fillet = 0.06

        # Create Spline points for profile config
        LE_tube_points, P1, P11, P12, LE_points, TE_points, P2, P21, P22, P3, round_TE_points, P4, P5, P51, P52, TE_lower_points, P6, P61, P62, P63, fillet_points, Origin_LE_tube, round_TE_mid, seam_a, LE_dyu_dx, LE_d2yu_dx2, circ_dyu_dx, circ_d2yu_dx2, both_array = \
            LEI_Parametric.LEI_airfoil(tube_size=tube_size, c_x=c_x, c_y=c_y, LE_config=3, LE_tension=LE_tension, e=e, TE_angle=TE_angle, TE_cam_tension=TE_cam_tension, TE_tension=TE_tension, LE_fillet=LE_fillet)

        profile_name = f'tube_size: {tube_size}, c_x: {c_x}, c_y: {c_y}, seam_a: {int(np.rad2deg(seam_a))}, LE_tension: {LE_tension}, TE_angle: {TE_angle}, TE_cam_tension: {TE_cam_tension}, TE_tension: {TE_tension}, e: {e}, dimTotal: {575}, NumLayers: {201}'

        # Combine all points into a single array
        all_points = np.vstack((LE_points, TE_points[1:], round_TE_points[1:-1], TE_lower_points[::-1], fillet_points[:-1][::-1], LE_tube_points[::-1]))
        points = np.column_stack((all_points, np.zeros(all_points.shape[0])))

        if save_png_dat:
            # Save profile PNG in results
            LEI_Parametric.plot_airfoil(fig_file_path, profile_name, LE_tube_points, P1, P11, P12, LE_points, TE_points, P2, P21, P22, P3, round_TE_points, P4, P5, P51, P52, TE_lower_points, P6, P61, P62, P63, fillet_points, seam_a)

            # Write profile points to a dat file
            with open(profile_p_file_path, "w") as f:
                f.write(f"# {profile_name}\n")
                for point in all_points:
                    f.write(" ".join(map(str, point)) + "\n")

        # Generate Pointwise mesh
        Pointwise_LEI.mesh_generation_pointiwse(glyph_script_path, polymesh_dir_location, Re, points)
        subprocess.run([pointwise_exe, glyph_script_path], check=True)
        return True

    except Exception as e:
        print(f"Error while processing config (t={t_val}, cx={cx_val}, cy={cy_val}, r={reflex_val}, LE={LE_val}), camTE_val={camTE_val}:", e)
        return False





if __name__ == '__main__':
    # Collect unique profiles
    unique_profiles = set()
    profile_lines = []

    for t, cx, cy, r, LE, camTE in all_configs_list:
        # Condition 1:
        if camTE + cx > 0.8:
            continue

        # Condition 2: if cy < t/2
        if cy < (t / 2):
            cx = 0.0
            cy = 0.0
            LE = 0.0
            camTE = 0.0

        # 4) Condition 3:
        if cy > (2.5 * t):
            continue

        line = f"t{t}_cx{cx}_cy{cy}_r{r}_LE{LE}_camTE{camTE}\n"
        if line not in unique_profiles:
            unique_profiles.add(line)
            profile_lines.append(line)

    # Write to file
    with open(profile_configs_dat, "w") as file:
        file.writelines(profile_lines)


    # Remove AOA directories
    subprocess.run("rm -rf ../OF_Ref/Re_*", shell=True)

    # Create Re and AOA directories in OF_Ref
    for Re, alpha in all_cases_list:
        # Create a AOA directories in OF_Setup
        subprocess.run(["mkdir", "-p", f"../OF_Ref/Re_{Re}/AOA_{alpha}"])
        # Copying Base_AOA folders and content to AOA directory in OF_Ref
        subprocess.run(["cp", "-r", "../OF_Setup/Base_AOA/0", "../OF_Setup/Base_AOA/constant", "../OF_Setup/Base_AOA/system", f"../OF_Ref/Re_{Re}/AOA_{alpha}"])

        # Change AOA in includeDict
        f = open(f"../OF_Ref/Re_{Re}/AOA_" + str(alpha) + '/system/includeDict', 'r+')
        t = f.readlines()
        new_lines = []
        for line in t:
            if 'alpha' in line.split():
                new_lines = np.append(new_lines, 'alpha               ' + str(alpha) + ';\n')
            elif 'Re' in line.split():
                new_lines = np.append(new_lines, 'Re                  ' + str(Re) + ';\n')
            else:
                new_lines = np.append(new_lines, line)

        f.close()
        f = open(f"../OF_Ref/Re_{Re}/AOA_" + str(alpha) + '/system/includeDict', 'w')
        f.writelines(new_lines)
        f.close()


    print("Total flow cases:", len(all_cases_list), " Re cases:", len(range_Re), " AOA cases:", len(range_AOA))
    print("Total configs desired:", len(all_configs_list), "Total outcome:", len(profile_lines))
    print("Total of sims:", len(profile_lines)*len(all_cases_list), "\n")

    # Configs per tube size
    tube_counts = defaultdict(int)
    for line in profile_lines:
        tube_str = line.split('_')[0]
        tube_thickness = float(tube_str[1:])
        tube_counts[tube_thickness] += 1

    for tube in sorted(tube_counts.keys()):
        print(f"tube: {tube} has {tube_counts[tube]} configurations")

    print(f"\nConfigurations written to {profile_configs_dat}")
    print(f"Cases have been writtin in /OF_Ref")