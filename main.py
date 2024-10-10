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

def process_point_name(X):
    """Process point name according to the specified rules."""
    import re
    
    # Remove specific characters and apply rules in order
    if X.isalnum():
        return X
    
    # Remove underscores
    X = X.replace('_', '')
    
    # Remove curly brackets
    X = X.replace('{', '').replace('}', '')
    
    # Handle prime notation
    if "'" in X:
        X = X.replace("'", '') + 'p'
    
    # Remove any remaining non-alphanumeric characters
    X = re.sub(r'[^a-zA-Z0-9]', '', X)
    
    return X

def process_point_definitions(lines):
    """Process dot/label pairs and create point definitions."""
    import re
    
    # Dictionary to keep track of point name occurrences
    point_names = {}
    
    # List to store new point definitions and processed lines
    point_definitions = []
    processed_lines = []
    
    # Regular expressions for matching dot and label lines
    dot_pattern = r'dot\(\(([-\d.]+),([-\d.]+)\),dotstyle\);'
    label_pattern = r'label\("\$(.+?)\$", \(([-\d.]+),([-\d.]+)\), NE\);'
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if i < len(lines) - 1:
            dot_match = re.match(dot_pattern, line)
            label_match = re.match(label_pattern, lines[i + 1].strip())
            
            if dot_match and label_match:
                # Get coordinates and label text
                A, B = dot_match.groups()
                X = label_match.group(1)
                C, D = label_match.groups()[1:]
                
                # Process the point name
                base_name = process_point_name(X)
                
                # Handle duplicate names
                if base_name in point_names:
                    point_names[base_name] += 1
                    point_name = f"{base_name}{point_names[base_name]}"
                else:
                    point_names[base_name] = 1
                    point_name = base_name
                
                # Create point definition with original coordinates
                point_def = f"pair {point_name}=({A},{B});\n"
                point_definitions.append(point_def)
                
                # Add modified dot and label lines
                processed_lines.append(f"dot({point_name});\n")
                processed_lines.append(f'label("${X}$", {point_name}, NE);\n')
                
                i += 2  # Skip the next line since we've processed it
                continue
        
        # For all other lines, keep them as is
        processed_lines.append(lines[i])
        i += 1
    
    # Combine everything: original lines up to line 3, point definitions, then processed lines
    return lines[:3] + point_definitions + processed_lines[3:]

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

    # Process point definitions and replacements
    lines = process_point_definitions(lines)

    # Write the modified content to the output file
    with open(output_filename, 'w') as file:
        file.writelines(lines)

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

# Example usage
input_file = "geogebra-export.txt"
output_file = "geogebra-export-modified.txt"
decimal_precision = 3  # Default value, can be changed

try:
    modify_file(input_file, output_file, decimal_precision)
    print(f"Successfully modified the file. Output saved to {output_file}")
except Exception as e:
    print(f"An error occurred: {e}")
