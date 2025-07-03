# scripts/openfoam_runs_pointwise/ directory

This directory contains reference sub-directories which are individual OpenFOAM cases. 

Each case considers a different angle-of-attack (AoA). The remaining flow conditions
and simulation set-up are the same. 

Base_AOA contains the steady RANS k-omega SST base configuration.
Base_AOA_unsteady contains the unsteady RANS k-omega SST base configuration.
Note: This unsteady is not fully functional yet!!!

The reference sub-directories are created by allocating the desired AOA in polars_pointwise.py.
Then runOpenFoam_pointwise.py copies the directories in Base_AOA to the allocated AOA directory.

To change the flow direction according to the AOA of an OpenFOAM case, runOpenFoam_pointwise.py modifies the AOA_*/system/includeDict file.

Tip: You can delete one specific AOA directory or all of them by writing in the command line:

    -> delete AOA 5: rm -rf AOA_5
    -> delete all: rm -rf AOA_*
    