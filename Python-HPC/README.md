# Python HPC toolchain
The toolchain outlines the use of the high-performance computing (HPC) cluster at the Aerospace Engineering Faculty of TU Delft for simulating parametrised 2D Leading Edge Inflatable (LEI) kite profiles.

It consists of a local machine stage involving the automated meshing of LEI kite profiles and the creation of the required directory structure for CFD simulations with OpenFOAM.

The 2D meshes are created in Pointwise using an O-grid topology.

Both the meshes and the OpenFOAM run files are uploaded to the HPC, where a task description file is used to enable parallel processing across multiple nodes and cores.

This document first explains how to run CFD simulations in parallel on the HPC, followed by instructions for configuring the setup to specific use cases.


## Prerequisites

1. Ubuntu
2. Python
3. OpenFOAM v2006


## HPC simulation Process

The OF_Setup/ directory contains all the Python scripts and Pointwise files required to create the OpenFOAM directory structure and generate meshes.
These files are executed locally on a user’s machine. 
Additionally, the directory includes a Python script for clearing the contents of the results subfolders.

The OF_Ref/ directory contains the Python scripts required for post-processing CFD results on the HPC system.

The OF_Uploads/ folder stores the Pointwise meshes for each profile, along with their corresponding profile figure.

DescriptionFile.PBS contains the bash commands to quide the HPC the run the processes in parallel, allocate the cores and nodes, link the directories, performa CFD simualtion and post-processing

The results/ directory stores CFD output in the CFD_profile_results_sorted.dat file, which includes the Re, profile configuration, AoA, aerodynamic coefficients, residuals, Y+ values, and the number of iterations.
Additionally, the directory contains pressure and skin friction data files, as well as VTK files organised into designated subfolders.

Note: More in detail information of linking the profile parametric model and Pointwise automatic mesher can be found in Pointwise-Openfoam-toolchain/Python/


## Step 1:

Install Cadence Pointwise by following the steps outlined in the installation guide, starting from page 14: Installing the License Manager, Windows Installation.
The server and port number can be found in the license_instructions file.

Once the installation is complete, you can execute the Windows application from within the Ubuntu directory structure.

A connection to the TU Delft network is required, either through Eduroam or a VPN connection.


## Step 2:

Change <dir> and <person> in the following files:

    -> OF_Setup/OF_Dir_structure*.py
    -> OF_Setup/LEI_Parametric.py
    -> OF_Setup/ProfileWriter.py


## Step 3:

The desired configurations such as AoA and Re for the CFD simulations can be set in OF_Setup/Profile_Writer.py. The script prints the number of desired simulations, the number of simulations to be executed(some configurations are filtered out), and the number of required meshes.
It writes the final configuration list to OF_Setup/profile_configs.dat and generates the corresponding OpenFOAM directory files in the OF_Ref/ folder.

## Step 4:

The Pointwise meshes can be run locally either in parallel or individually. A test run can be performed by setting process_all = False in the OF_Dir_Structure*.py scripts.
The LEI_Mesh*.glf files are input scripts used by Pointwise for the meshing process.
To run the meshing process in parallel, use the following command in the terminal:

    mpirun -np 1 python3 OF_Dir_Structure.py : -np 1 python3 OF_Dir_Structure2.py : -np 1 python3 OF_Dir_Structure3.py : -np 1 python3 OF_Dir_Structure4.py

The meshes are stored in the OF_Uploads directory along with their corresponding profile figures. This output can be disabled in OF_Setup/Profile_Writer.py.


## Step 5:

The post-processing tasks are defined in OF_Ref/PostProcess.py, 
where the VTK output can be switch on or off.


## Step 6:

Clean_Results.py can be run to empty the OF_Results sub-directories.


## Step 7:

Toggle the DecriptionFile.pbs to the desired nodes and cores.
Change the amount of allocated maximum cores!


## Step 8:

Enter the HPC of the Tudelft with the SSH key.

    ssh -X <person>@hpc12.tudelft.net


## Step 9:

Push the setup folder to the HPC.

    scp -r /<dir>/Python-HPC/ <person>@hpc12.tudelft.net:/home/scratch/<person>/


## Step 10:

Run the Description file on the HPC to start the HPC process.

    qsub DescriptionFile.pbs


## Step 11:

Pull Results folder off the HPC to your local device.

    scp -r <person>@hpc12.tudelft.net:/home/scratch/<person>/Python-HPC/OF_Results/ /<dir>/Python-HPC/
