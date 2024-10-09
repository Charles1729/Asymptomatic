def truncate_all_numbers(line, decimal_precision):
    """Truncate all numbers in a line to specified decimal precision."""
    import re
    
    def truncate_match(match):
        num_str = match.group(0)
        if '.' not in num_str:
            return num_str
            
        # Handle negative numbers
        is_negative = num_str.startswith('-')
        if is_negative:
            num_str = num_str[1:]
            
        # Split into integer and decimal parts
        integer_part, decimal_part = num_str.split('.')
        
        # Truncate decimal part if it's longer than precision
        if len(decimal_part) > decimal_precision:
            decimal_part = decimal_part[:decimal_precision]
            
        # Reconstruct number
        result = f"{'-' if is_negative else ''}{integer_part}.{decimal_part}"
        return result
    
    # Match any number (including negative) with a decimal point
    pattern = r'-?\d+\.\d+'
    return re.sub(pattern, truncate_match, line)

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

    # Remove lines matching label("$[lowercase_letter]")
    filtered_lines = []
    for line in lines:
        line_strip = line.strip()
        if not (line_strip.startswith('label("$') and 
                len(line_strip) > 8 and 
                line_strip[8].islower()):
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

    # Truncate all numbers in all lines
    processed_lines = []
    for line in lines:
        processed_line = truncate_all_numbers(line, decimal_precision)
        processed_lines.append(processed_line)
    lines = processed_lines

    # Now process the dot lines after number truncation
    lines = process_dot_lines(lines)

    # Write the modified content to the output file
    with open(output_filename, 'w') as file:
        file.writelines(lines)

# Rest of the helper functions remain the same
def extract_pen_names(line):
    """Extract all 6-letter lowercase pen names from a pen definition line."""
    import re
    pattern = r'pen ([a-z]{6})\s*='
    return re.findall(pattern, line)

def remove_pen_references(lines, pen_name):
    """Remove all instances of a pen name and its variations from all lines."""
    modified_lines = []
    for line in lines:
        line = line.replace(f" + {pen_name}", "")
        line = line.replace(f",{pen_name}", "")
        line = line.replace(pen_name, "")
        modified_lines.append(line)
    return modified_lines

def extract_dot_coordinates(line):
    """Extract coordinates from a dot line."""
    import re
    match = re.search(r'dot\(\(([-\d.]+),([-\d.]+)\)', line)
    if match:
        return f"({match.group(1)},{match.group(2)})"
    return None

def process_dot_lines(lines):
    """Process dot lines according to the new rules."""
    # First, collect all coordinates from dot lines
    dot_coords = []
    for line in lines:
        if line.strip().startswith('dot('):
            coords = extract_dot_coordinates(line)
            if coords:
                dot_coords.append(coords)

    # Now process all lines
    processed_lines = []
    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith('dot('):
            # Remove ,dotstyle from the line
            line = line.replace(',dotstyle', '')
            coords = extract_dot_coordinates(line)
            # Only add the line if its coordinates don't appear in any draw line
            should_keep = True
            if coords:
                for draw_line in lines:
                    if draw_line.strip().startswith('draw(') and coords in draw_line:
                        should_keep = False
                        break
            if should_keep:
                processed_lines.append(line)
        else:
            processed_lines.append(line)
    
    return processed_lines

# Example usage
input_file = "geogebra-export.txt"
output_file = "geogebra-export-modified.txt"
decimal_precision = 3  # Default value, can be changed

try:
    modify_file(input_file, output_file, decimal_precision)
    print(f"Successfully modified the file. Output saved to {output_file}")
except Exception as e:
    print(f"An error occurred: {e}")
