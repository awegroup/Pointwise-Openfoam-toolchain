# Python local-pc toolchain

The toolchain automatically meshes parametrised 2D Leading-Edge Inflatable (LEI) kite profiles and creates the required directory infrastructure for subsequent CFD simulations.

The 2D meshes are generated in Pointwise with O-grid topology. The directory infrastructure is set up for OpenFOAM cases with different angles of attack (AoA).

This directory is set up to run on a local PC, with or without parallel computing, depending on the availability of multiple processors.

This document first explains the process of the file structure and links. followed by instructions for configuring the setup to specific use cases.


## Prerequisites

1. Ubuntu
2. Python
3. OpenFOAM v2006


## Simulation Process

All python files are located in the scripts/ directory.

The main script to run is polars_pointwise.py, where you specify the airfoil parameters, Reynolds number, and AOA values.

The script first calls LEI_Parametric.py, which generates splines based on the input parameters and returns the geometry coordinates.

Pointwise_LEI.py then creates a structured mesh with an O-grid topology in Pointwise.
It uses the wall_height function from LEI_Parametric.py to determine the initial cell height.
Surface and normal node distributions are defined in this file and generate the input script: mesh_pointwise.glf.
Pointwise is automatically launched to generate the mesh, and then closed automatically or manually.
The volume conditions are automatically converted from Pointwise to OpenFOAM format and exported to the scripts/openfoam_runs_pointwise/Base_AOA/polyMesh sub-directory.

Since an O-grid topology is used, remeshing is not required when changing the AOA. Instead, the inlet velocity vector direction is adjusted by specifying the AOA range.
Each AOA is then simulated with the pre and post-processing settings entailed in runOpenFoam_pointwise.py.
This file copies the necessary directories from scripts/openfoam_runs_pointwise/Base_AOA for each AOA, ensuring that all simulations have the same setup, except for the unique flow direction specified for each AOA.

The results/ directory stores the polar data, plots, airfoil geometry data, and figure.
In scripts/openfoam_runs_pointwise/AOA_*, the flow field residuals, force coefficient residuals, pressure and skin friction coefficient plots can be found.


## Step 1:

Install Cadence Pointwise by following the steps outlined in the installation guide, starting from page 14: Installing the License Manager, Windows Installation.
The server and port number can be found in the license_instructions file.

Once the installation is complete, you can execute the Windows application from within the Ubuntu directory structure.

A connection to the TU Delft network is required, either through Eduroam or a VPN connection.


## Step 2:

Modify the root directory in both polars_pointwise.py and LEI_Parametric.py.

Additionally, update the installation directory of Pointwise in polars_pointwise.py.


## Step 3:

In the main file polars_pointwise.py, the Reynolds number and airfoil parameters are defined.

The desired AOA range can be specified at the line: "# Execute openfoam for each AOA"


## Step 4:

The openfoam setup can be tweaked slightly if required.

    -> Numbre of max iterations: Base_AOA/system/controlDict, "endTime"
    -> Convergence parameter for the initial residual values: Base_AOA/system/fvSolution, "residualControl"
    -> RelaxationFactors: Base_AOA/system/fvSolution, "relaxationFactors"


## Step 5:

Pre and post-processing can be configured in runOpenFoam_pointwise.py.

It contains multiple switches that trigger conditional (if) statements throughout the script, enabling specific pre-processing and post-processing actions.

    -> parallel_comp: If multiple processors are available,
    the default setting uses 4 processors, decomposing the mesh accordingly.
    If a different number of processors is required, update the number in:
    --> parts.subprocess.run(['mpirun -np 4 simpleFoam -parallel > log'])
    --> Base_AOA/system/decomposeParDict
    -> cp_plot: Outputs reduced Cp data and plots it alongside the airfoil geometry.
    -> force_plot: Outputs a force residual plot.
    -> residuals_plot: Outputs a final residual value plot with the following variables:
    Ux_final, Uy_final, k_final, p_final, omega_final.
    -> steady: Executes a steady RANS k-omega SST simulation.
    -> unsteady: Executes an unsteady RANS k-omega SST simulation ### not working!!! ###
    -> initialise_sim: After running the first simulation,
    the previous converged simulation field is used to map the first iteration of the following simulation.
    -> VTK_paraview: Outputs all field data for the last iteration.
    -> transition_model: Chenges the fully turbulent boundary layer RANS simulation to one with a transition model.


## Step 6:

Run the script polars_pointwise.py


## Step 5:

Polar data, plots, and parametric airfoil geometry can be retrieved in the results/ directory.
Cp, Cf, VTK files, residual plots can be found in the openfoam_runs_pointwise/AOA_* directories.


## Author

**Kasper Masure**