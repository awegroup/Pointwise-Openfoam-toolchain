# Pointwise OpenFOAM Toolchain

The toolchain automatically meshes parametrized 2D Leading-Edge Inflatable (LEI) kite profiles and creates the required directory infrastructure for subsequent CFD simulations.

https://github.com/user-attachments/assets/2253ec46-c116-45fd-906c-d18838bf960f

The 2D meshes are generated in Pointwise with O-grid topology. The directory infrastructure is set up for OpenFOAM cases with different angles of attack (AoA).


## Directories

1. **Matlab:** The Matlab Pointwise OpenFoam toolchain, developed by John Watchorn, uses **Matlab** to generate parameterized 2D LEI kite profiles and AOA directories for CFD simulations. It can be run locally but also has the capability to execute on **HPC** (High-Performance Computing) systems.

2. **Python-HPC:** The Python Pointwise OpenFoam HPC toolchain, developed by Kasper Masure, utilizes **Python** to create parameterized 2D LEI kite profiles and AOA directories for CFD. It is specifically designed for execution on **HPC** systems.

3. **Python:** The Python Pointwise OpenFoam local PC toolchain, also developed by Kasper Masure, uses **Python** to generate parameterized 2D LEI kite profiles and AOA directories for CFD. Designed for local execution, it includes mesh decomposition capabilities and the ability to initialize subsequent AOAs, optimizing the simulation process on a **local machine**.



## Author

**John Watchorn**

**Kasper Masure**
