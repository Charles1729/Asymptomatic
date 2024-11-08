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

def fix_latex_commands(line):
    """Fix common LaTeX command errors."""
    latex_fixes = {
        '\\\\': '\\',  # Double backslash to single backslash
        # Add more LaTeX fixes here if needed
    }
    for old, new in latex_fixes.items():
        line = line.replace(old, new)
    return line

def process_point_name(X):
    """Process point name according to the specified rules."""
    import re
    
    # Store original name before processing
    original_name = X
    
    # Remove specific characters and apply rules in order
    if X.isalnum():
        return X, X
    
    # Remove underscores
    X = X.replace('_', '')
    
    # Remove curly brackets
    X = X.replace('{', '').replace('}', '')
    
    # Handle prime notation
    if "'" in X:
        X = X.replace("'", '') + 'p'
    
    # Remove any remaining non-alphanumeric characters for the programmatic name
    X = re.sub(r'[^a-zA-Z0-9]', '', X)
    
    return X, original_name

def process_point_definitions(lines):
    """Process dot/label pairs and create point definitions."""
    import re
    
    # Dictionary to keep track of point name occurrences
    point_names = {}
    
    # Dictionary to map coordinates to point names (both programmatic and display versions)
    coord_to_point = {}
    coord_to_display_name = {}
    
    # Lists to store different types of lines
    header_lines = lines[:3]
    point_definitions = []
    dot_lines = []
    label_lines = []
    other_lines = []
    
    # Regular expressions for matching dot and label lines
    dot_pattern = r'dot\(\(([-\d.]+),([-\d.]+)\)(?:,dotstyle)?\);'
    label_pattern = r'label\("\$(.+?)\$", \(([-\d.]+),([-\d.]+)\), NE\);'
    
    # Function to replace coordinates with point name
    def replace_coordinates(line):
        coord_pattern = r'\(([-\d.]+),([-\d.]+)\)'
        result = line[:]
        
        matches = list(re.finditer(coord_pattern, line))
        for match in reversed(matches):
            coord_str = match.group(0)
            if coord_str in coord_to_point:
                prefix = line[max(0, match.start()-3):match.start()]
                if not prefix.strip().endswith('.'):
                    replacement = coord_to_point[coord_str]
                    start, end = match.span()
                    if line[max(0, start-4):start].rstrip().endswith('('):
                        replacement = f"{replacement}"
                    result = result[:start] + replacement + result[end:]
        return result
    
    i = 3  # Start after header lines
    while i < len(lines):
        line = lines[i].strip()
        
        if i < len(lines) - 1:
            dot_match = re.match(dot_pattern, line)
            next_line = lines[i + 1].strip()
            label_match = re.match(label_pattern, next_line)
            
            if dot_match and label_match:
                # Get coordinates and label text
                A, B = dot_match.groups()[:2]
                X = label_match.group(1)
                
                # Create coordinate string
                coord_str = f"({A},{B})"
                
                # Fix any LaTeX command errors in X
                X = fix_latex_commands(X)
                
                # Process the point name - now getting both programmatic and display versions
                prog_name, display_name = process_point_name(X)
                
                # Handle duplicate names
                if prog_name in point_names:
                    point_names[prog_name] += 1
                    prog_name = f"{prog_name}{point_names[prog_name]}"
                    display_name = f"{display_name}{point_names[prog_name]}"
                else:
                    point_names[prog_name] = 1
                
                # Create point definition with original coordinates
                point_def = f"pair {prog_name}={coord_str};\n"
                point_definitions.append(point_def)
                
                # Store both programmatic and display names
                coord_to_point[coord_str] = prog_name
                coord_to_display_name[coord_str] = display_name
                
                # Add dot line without dotstyle and modified label line
                dot_lines.append(f"dot({coord_str});\n")
                # Use the display name in the label
                label_lines.append(f'label("${display_name}$", {coord_str}, NE);\n')
                
                i += 2
                continue
        
        # For all other lines
        if line.startswith('dot('):
            line = re.sub(r',dotstyle', '', line)
            dot_lines.append(line + '\n')
        elif line.startswith('label('):
            label_lines.append(fix_latex_commands(line) + '\n')
        else:
            if '$' in line:
                other_lines.append(fix_latex_commands(line) + '\n')
            else:
                other_lines.append(line + '\n')
        i += 1
    
    # Find the marker for dots and labels section
    marker_index = -1
    for i, line in enumerate(other_lines):
        if '/* dots and labels */' in line:
            marker_index = i
            break
    
    # Construct final output
    final_lines = []
    final_lines.extend(header_lines)
    final_lines.extend(point_definitions)
    
    if marker_index != -1:
        final_lines.extend(other_lines[:marker_index])
        final_lines.append(other_lines[marker_index])
        final_lines.extend(dot_lines)
        final_lines.append('\n')
        final_lines.extend(label_lines)
        final_lines.extend(other_lines[marker_index + 1:])
    else:
        final_lines.extend(other_lines)
        final_lines.extend(dot_lines)
        final_lines.append('\n')
        final_lines.extend(label_lines)
    
    # Now perform coordinate replacements on all lines except point definitions
    processed_lines = []
    for line in final_lines:
        if not line.strip().startswith('pair '):
            line = replace_coordinates(line)
        processed_lines.append(line)
    
    return processed_lines

def modify_file(input_filename, output_filename, decimal_precision=3):
    """Main function to modify the file."""
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

    # Extract and save the xmin line and pen definitions if they exist
    if start_idx != -1 and end_idx != -1:
        for i in range(start_idx, end_idx + 1):
            line = lines[i]
            if line.strip().startswith('real xmin'):
                xmin_line = line
            elif 'pen ' in line and '= rgb(' in line:
                pen_definitions_line = line
                # Extract pen names and remove their references
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

    # Check and remove last line if it starts with /*
    if len(lines) >= 1 and lines[-1].strip().startswith('/*'):
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
    
    # Process point definitions and replacements
    final_lines = process_point_definitions(processed_lines)

    # Write the modified content to the output file
    with open(output_filename, 'w') as file:
        file.writelines(final_lines)

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
if __name__ == "__main__":
    input_file = "geogebra-export.txt"
    output_file = "geogebra-export-modified.txt"
    decimal_precision = 3  # Default value, can be changed

    try:
        modify_file(input_file, output_file, decimal_precision)
        print(f"Successfully modified the file. Output saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
