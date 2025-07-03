import subprocess

subprocess.run("rm -rf ../OF_Results/OF_Cp/*", shell=True)
subprocess.run("rm -rf ../OF_Results/OF_Cf/*", shell=True)
subprocess.run("rm -rf ../OF_Results/OF_VTK/*", shell=True)

subprocess.run("> ../OF_Results/CFD_profile_results.dat", shell=True)
subprocess.run("> ../OF_Results/CFD_profile_results_sorted.dat", shell=True)



