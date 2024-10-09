class NumberTruncator:
    def __init__(self, precision):
        self.precision = precision
    
    def truncate_number(self, match):
        number_str = match.group(0)
        try:
            # Handle negative numbers
            sign = '-' if number_str[0] == '-' else ''
            if sign:
                number_str = number_str[1:]
                
            # Split into integer and decimal parts
            parts = number_str.split('.')
            if len(parts) == 2:  # If there's a decimal point
                integer, decimal = parts
                return f"{sign}{integer}.{decimal[:self.precision]}"
            return number_str
        except:
            return number_str

def modify_file(input_filename, output_filename, decimal_precision=3):
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

    # Add blank lines after first and second lines
    if len(lines) >= 2:
        lines.insert(1, '\n')
        lines.insert(3, '\n')

    # Add blank line before "/* dots and labels */"
    for i, line in enumerate(lines):
        if line.strip().startswith('/* dots and labels */'):
            lines.insert(i, '\n')
            break

    # Truncate decimal numbers
    import re
    truncator = NumberTruncator(decimal_precision)
    processed_lines = []
    for line in lines:
        # Find numbers with decimal points and more than decimal_precision digits after
        processed_line = re.sub(
            r'-?\d*\.\d{' + str(decimal_precision + 1) + ',}',
            truncator.truncate_number,
            line
        )
        processed_lines.append(processed_line)

    # Write the modified content to the output file
    with open(output_filename, 'w') as file:
        file.writelines(processed_lines)

# Example usage
input_file = "geogebra-export.txt"
output_file = "geogebra-export-modified.txt"
decimal_precision = 3  # Default value, can be changed

try:
    modify_file(input_file, output_file, decimal_precision)
    print(f"Successfully modified the file. Output saved to {output_file}")
except Exception as e:
    print(f"An error occurred: {e}")
