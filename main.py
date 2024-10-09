def modify_file(input_filename, output_filename):
    # Read the entire file
    with open(input_filename, 'r') as file:
        lines = file.readlines()

    # Find the indices of the lines we want to remove between
    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('real labelscalefactor = 0.5'):
            start_idx = i
        elif line.strip().startswith('/* draw figures */'):
            end_idx = i
            break

    # Remove the lines between (and including) start_idx and end_idx
    if start_idx != -1 and end_idx != -1:
        lines = lines[:start_idx] + lines[end_idx + 1:]

    # Remove ", linewidth(2)" from all lines
    lines = [line.replace(', linewidth(2)', '') for line in lines]

    # Remove lines starting with "dot("
    lines = [line for line in lines if not line.strip().startswith('dot(')]

    # Check and remove last two lines if they match the criteria
    if len(lines) >= 2:
        if lines[-2].strip().startswith('clip') and lines[-1].strip().startswith('/*'):
            lines = lines[:-2]

    # Remove " * labelscalefactor" from all lines
    lines = [line.replace(' * labelscalefactor', '') for line in lines]

    # Write the modified content to the output file
    with open(output_filename, 'w') as file:
        file.writelines(lines)

# Example usage
input_file = "geogebra-export.txt"
output_file = "geogebra-export-modified.txt"

try:
    modify_file(input_file, output_file)
    print(f"Successfully modified the file. Output saved to {output_file}")
except Exception as e:
    print(f"An error occurred: {e}")