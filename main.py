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

def extract_pen_names(line):
    """Extract all 6-letter lowercase pen names from a pen definition line."""
    import re
    # Match "pen" followed by exactly 6 lowercase letters
    pattern = r'pen ([a-z]{6})\s*='
    return re.findall(pattern, line)

def remove_pen_references(lines, pen_name):
    """Remove all instances of a pen name and its variations from all lines."""
    modified_lines = []
    for line in lines:
        # Remove " + pen_name" first
        line = line.replace(f" + {pen_name}", "")
        # Remove ",pen_name" next
        line = line.replace(f",{pen_name}", "")
        # Remove the pen_name itself
        line = line.replace(pen_name, "")
        modified_lines.append(line)
    return modified_lines

def modify_file(input_filename, output_filename, decimal_precision=3):
    # Read the entire file
    with open(input_filename, 'r') as file:
        lines = file.readlines()

    # Find the indices of the lines we want to process between
    start_idx = -1
    end_idx = -1
    xmin_line = None
    pen_definitions_line = None
    for i, line in enumerate(lines):
        if line.strip().startswith('real labelscalefactor = 0.5'):
            start_idx = i
        elif line.strip().startswith('/* draw figures */'):
            end_idx = i
            break

    # Extract and save the xmin line and pen definitions if they exist between start_idx and end_idx
    if start_idx != -1 and end_idx != -1:
        for i in range(start_idx, end_idx + 1):
            line = lines[i]
            if line.strip().startswith('real xmin'):
                xmin_line = line
            elif 'pen ' in line and '= rgb(' in line:
                pen_definitions_line = line
                # Extract pen names and remove their references from all lines
                pen_names = extract_pen_names(line)
                for pen_name in pen_names:
                    lines = remove_pen_references(lines, pen_name)
        
        # Remove the lines between (and including) start_idx and end_idx,
        # then insert back the xmin line if it was found
        lines = lines[:start_idx] + ([xmin_line] if xmin_line else []) + lines[end_idx + 1:]

    # Remove ", linewidth(2)" from all lines
    lines = [line.replace(', linewidth(2)', '') for line in lines]

    # Remove lines starting with "dot(" or matching label("$[lowercase_letter]")
    filtered_lines = []
    for line in lines:
        line_strip = line.strip()
        if (not line_strip.startswith('dot(') and 
            not (line_strip.startswith('label("$') and 
                 len(line_strip) > 8 and 
                 line_strip[8].islower())):
            filtered_lines.append(line)
    lines = filtered_lines

    # Check and remove last two lines if they match the criteria
    if len(lines) >= 1:
        if lines[-1].strip().startswith('/*'):
            lines = lines[:-1]

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
