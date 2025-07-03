import os

# Set your input and output file paths
input_file = "CFD_profile_results.dat"
output_file = "CFD_profile_results_sorted.dat"

# Read header and data lines
with open(input_file, 'r') as f:
    header = f.readline()  # read header (e.g., "#Re Config_a")
    lines = f.readlines()  # read the rest of the file

def sort_key(line):
    parts = line.split()
    if not parts:
        return (float('inf'), "", 0)

    # First column: Reynolds number (Re)
    try:
        re_value = int(parts[0])
    except ValueError:
        re_value = 0  # default if conversion fails

    # Second column: Config_a
    config_str = parts[1] if len(parts) > 1 else ""
    if '_a' in config_str:
        config_base, angle_str = config_str.rsplit('_a', 1)
        try:
            angle_val = float(angle_str)
        except ValueError:
            angle_val = 0
    else:
        config_base = config_str
        angle_val = 0

    return (re_value, config_base, angle_val)

# Sort the data lines using the sort_key function
sorted_lines = sorted(lines, key=sort_key)

# Write the header and sorted lines to the new output file
with open(output_file, 'w') as f:
    f.write(header)
    f.writelines(sorted_lines)
