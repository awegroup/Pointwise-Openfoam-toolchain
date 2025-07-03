"""Main file to run to create the polar plot and cp plots"""
import LEI_Parametric
import Pointwise_LEI
import runOpenFoam_pointiwse
import subprocess
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams

# Change directory to your pc setup
font_path = "dir/.local/share/fonts/ARIAL.TTF"
fm.fontManager.addfont(font_path)
arial_font = fm.FontProperties(fname=font_path)
arial_name = arial_font.get_name()
rcParams['font.family'] = arial_name

def fond_size(width_overleaf, width_figure):
    windth_fig_page = 21*width_overleaf*0.9
    ratio = width_figure*2.54/windth_fig_page
    overleaf_font = 10
    return overleaf_font * ratio



## file directory
# Change the following 2 directories to your pc setup
root_path = r"<dir>/"
pointwise_exe = r"/<dir>/Pointwise.exe"

polar_data_file_path = Path(root_path) / 'results' / 'polar.dat'
glyph_script_path = Path(root_path) / 'scripts' / 'mesh_pointwise.glf'
polar_plot_residuals_file_path = Path(root_path) / 'results' / 'polar.png'
mesh_file_path = Path(root_path) / 'scripts' / 'openfoam_runs_pointwise' / 'Base_AOA' / 'polyMesh'
fig_file_path = Path(root_path) / 'results' / 'profile.png'
profile_p_file_path = Path(root_path) / 'results' / 'profile.dat'


######  Study case inputs ######
# Reynolds number
Re = 5e6

# LEI_airfoil instance
tube_size = 0.08
c_x = 0.15
c_y = 0.08
LE_tension = 0.65
TE_angle = 0
TE_cam_tension = 0.2
TE_tension = 0.2
e = 0.0005
LE_fillet = 0.08

# Defines profile geometry
LE_tube_points, P1, P11, P12, LE_points, TE_points, P2, P21, P22, P3, round_TE_points, P4, P5, P51, P52, TE_lower_points, P6, P61, P62, P63, fillet_points, Origin_LE_tube, round_TE_mid, seam_a, LE_dyu_dx, LE_d2yu_dx2, circ_dyu_dx, circ_d2yu_dx2, both_array = \
    LEI_Parametric.LEI_airfoil(tube_size=tube_size, c_x=c_x, c_y=c_y, LE_config=3, LE_tension=LE_tension, e=e, TE_angle=TE_angle, TE_cam_tension=TE_cam_tension, TE_tension=TE_tension, LE_fillet=LE_fillet)

# Profile name
profile_name = f'tube_size: {tube_size}, c_x: {c_x}, c_y: {c_y}, seam_a: {int(np.rad2deg(seam_a))}, LE_tension: {LE_tension}, TE_angle: {TE_angle}, TE_cam_tension: {TE_cam_tension}, TE_tension: {TE_tension}, e: {e}'

# Save profile shape in results
LEI_Parametric.plot_airfoil(fig_file_path, profile_name, LE_tube_points, P1, P11, P12, LE_points, TE_points, P2, P21, P22, P3, round_TE_points, P4, P5, P51, P52, TE_lower_points, P6, P61, P62, P63, fillet_points, seam_a)

# Combine all points into a single array
all_points = np.vstack((LE_points, TE_points[1:], round_TE_points[1:-1], TE_lower_points[::-1], fillet_points[:-1][::-1], LE_tube_points[::-1]))
points = np.column_stack((all_points, np.zeros(all_points.shape[0])))
fillet_loc = len(np.vstack((LE_points, TE_points[1:], round_TE_points[1:-1], TE_lower_points[::-1])))


#  Write profile points to dat file
with open(profile_p_file_path, "w") as f:
    f.write(f"# {profile_name}\n")
    f.write("# x y z\n")
    for point in points:
        f.write(" ".join(map(str, point)) + "\n")


# Generate Pointwise mesh
Pointwise_LEI.mesh_generation_pointiwse(glyph_script_path, mesh_file_path, Re, points)
subprocess.run([pointwise_exe, glyph_script_path], check=True)

# Remove AOA directories if exist
subprocess.run("rm -rf openfoam_runs_pointwise/AOA_*", shell=True)


# Empty polar file
open(polar_data_file_path, 'w').close()

# Execute openfoam for each AOA
range_AOA = np.array([5, 10])
for i, alpha in enumerate(range_AOA):
    print(i, alpha)
    if i == 0:
        previous_alpha = range_AOA[0]
    else:
        previous_alpha = range_AOA[i - 1]

    # Run openfoam and post-processing
    runOpenFoam_pointiwse.compute_alpha_pointwise(Re, alpha, previous_alpha, root_path, profile_name)



# plot polars with iterations
try:
    with open(polar_data_file_path, "r") as file:
        lines = file.readlines()
    # Initialise lists for alpha, force coefficients and iteration number
    alpha = []
    cd = []
    cl = []
    cmpitch = []
    iter_n = []
    xcp = []

    # Skip the header line and process data
    for line in lines[1:]:
        parts = line.split()
        alpha.append(float(parts[0]))        # Alpha
        cd.append(float(parts[1]))           # Cd
        cl.append(float(parts[3]))           # Cl
        cmpitch.append(float(parts[5]))      # CmPitch
        xcp.append(float(parts[13]))
        iter_n.append(int(parts[-1]))


    plt.figure(figsize=(15, 10))
    # Plot 1: Cl vs Alpha
    plt.subplot(3, 2, 1)
    plt.plot(alpha, cl, marker='o', label='Cl')
    plt.plot(alpha, xcp, marker='o', label='xcp')
    plt.xlabel('Alpha')
    plt.ylabel('Cl')
    plt.title('Cl vs Alpha')
    plt.grid(True)

    # Plot 2: Cd vs Alpha
    plt.subplot(3, 2, 2)
    plt.plot(alpha, cd, marker='o', label='Cd')
    plt.xlabel('Alpha')
    plt.ylabel('Cd')
    plt.title('Cd vs Alpha')
    plt.grid(True)

    # Plot 3: CmPitch vs Alpha
    plt.subplot(3, 2, 3)
    plt.plot(alpha, cmpitch, marker='o', label='CmPitch')
    plt.xlabel('Alpha')
    plt.ylabel('CmPitch')
    plt.title('CmPitch vs Alpha')
    plt.grid(True)

    # Plot 4: Cl vs Cd
    plt.subplot(3, 2, 4)
    plt.plot(cd, cl, marker='o', label='Cl vs Cd')
    plt.xlabel('Cd')
    plt.ylabel('Cl')
    plt.title('Cl vs Cd')
    plt.grid(True)

    # Plot 5: iterations vs Alpha
    plt.subplot(3, 1, 3)
    plt.plot(alpha, iter_n, marker='o')
    plt.xlabel(r'$\alpha$ [$^\circ$]')
    plt.ylabel('Iteration number [-]')
    plt.grid(True)

    # Figure title
    plt.title(profile_name, fontsize=8, fontweight='bold')

    # Save figure
    plt.tight_layout()
    plt.savefig(polar_plot_residuals_file_path, format='png', dpi=300)
    plt.close()

except Exception as e:
    print(f"An error occurred while processing the file: {e}")