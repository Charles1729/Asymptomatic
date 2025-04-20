import re
import sys
from decimal import Decimal, ROUND_DOWN

def truncate_to_precision(value, precision=3):
    """Truncate a numeric value to specified precision."""
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return value
    
    # Format with specified precision, removing trailing zeros
    formatted = f"{value:.{precision}f}".rstrip('0').rstrip('.')
    return formatted

def format_point_name(name):
    """Format point names according to specified rules."""
    # Handle names with underscores and curly braces like I_{C}
    if '_{' in name and '}' in name:
        base = name.split('_{')[0]
        subscript = name.split('_{')[1].split('}')[0]
        return base + subscript.lower()
    
    # Handle prime symbols
    prime_count = name.count("'") + name.count("`")
    if prime_count > 0:
        # Remove all prime symbols
        base = name.replace("'", "").replace("`", "")
        return base + "prime" * prime_count
    
    return name

def process_file(input_file, output_file=None):
    # Read the file
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Process decimal numbers
    def truncate_decimal_match(match):
        return truncate_to_precision(match.group(0), decimal_precision)
    
    decimal_pattern = r'-?\d+\.\d+'
    content = re.sub(decimal_pattern, truncate_decimal_match, content)
    
    # Find the pen definitions before deleting any lines
    lines = content.split('\n')
    pen_names = []
    for line in lines:
        if 'pen ' in line and ' = rgb(' in line:
            # Extract all pen definitions from the line
            pen_defs = re.findall(r'pen (\w+) = rgb\([^;]+\);', line)
            pen_names.extend(pen_defs)
    
    # Find the start and end lines for deletion
    start_index = None
    end_index = None
    xmin_line = None
    
    for i, line in enumerate(lines):
        if line.strip().startswith('real labelscalefactor'):
            start_index = i
        elif line.strip().startswith('/* draw figures */'):
            end_index = i
        if 'real xmin' in line:
            xmin_line = line[line.index('real xmin'):]
            # Truncate decimal values in xmin line
            xmin_values = re.findall(decimal_pattern, xmin_line)
            for value in xmin_values:
                truncated = truncate_to_precision(value, decimal_precision)
                xmin_line = xmin_line.replace(value, truncated)

    # Remove lines between labelscalefactor and draw figures, except xmin line
    if start_index is not None and end_index is not None:
        new_lines = lines[:start_index]
        if xmin_line:
            new_lines.append(xmin_line)
        new_lines.extend(lines[end_index+1:])
        lines = new_lines
        content = '\n'.join(lines)
    
    # Process pen references
    for pen in pen_names:
        # Remove " + pen" occurrences
        content = re.sub(r' \+ ' + re.escape(pen), '', content)
        # Remove ",pen" occurrences
        content = re.sub(r',' + re.escape(pen), '', content)
        # Remove standalone "pen" occurrences (as a whole word)
        content = re.sub(r'\b' + re.escape(pen) + r'\b', '', content)
    
    # Miscellaneous deletions
    content = re.sub(r', linewidth\(\d+(?:\.\d+)?(pt)?\)', '', content)
    content = re.sub(r' \* labelscalefactor', '', content)
    content = re.sub(r'^\s*\/\* dots and labels \*\/\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'label\("\$[a-z].*$\n', '', content, flags=re.MULTILINE)
    
    # Extract drawing coordinates and process labels
    lines = content.split('\n')
    all_drawing_coords = []
    
    # First gather all coordinates
    coord_pattern = r'\((-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)'
    for line in lines:
        if line.strip().startswith('draw('):
            coords_matches = re.findall(coord_pattern, line)
            for x_str, y_str in coords_matches:
                x = truncate_to_precision(x_str, decimal_precision)
                y = truncate_to_precision(y_str, decimal_precision)
                all_drawing_coords.append((x, y))
    
    # Remove duplicates
    all_drawing_coords = list(set(all_drawing_coords))
    
    # Extract all labels
    label_info = []
    for line in lines:
        if line.strip().startswith('label("$'):
            label_match = re.search(r'label\("\$([A-Z][^$]*)\$", \(([^,]+),([^)]+)\)', line)
            if label_match:
                label_name = label_match.group(1)
                label_x = truncate_to_precision(label_match.group(2), decimal_precision)
                label_y = truncate_to_precision(label_match.group(3), decimal_precision)
                label_info.append((label_name, label_x, label_y))
    
    # Associate labels with points
    pairs = []
    preserved_labels = []
    used_coords = set()
    
    for label_name, label_x, label_y in label_info:
        # Calculate distance to all drawing coordinates
        distances = []
        for coord_x, coord_y in all_drawing_coords:
            if (coord_x, coord_y) in used_coords:
                continue
            
            # Calculate Euclidean distance
            try:
                distance = ((float(label_x) - float(coord_x)) ** 2 + (float(label_y) - float(coord_y)) ** 2) ** 0.5
                distances.append((distance, (coord_x, coord_y)))
            except ValueError:
                continue
        
        # If valid coordinates found, use the closest one
        if distances:
            distances.sort()
            closest_distance, (closest_x, closest_y) = distances[0]
            
            # Use points that are reasonably close
            if closest_distance < 15.0:
                formatted_name = format_point_name(label_name)
                pairs.append((formatted_name, label_x, label_y, closest_x, closest_y))
                preserved_labels.append(f'label("${label_name}$", {formatted_name}, NE);')
                used_coords.add((closest_x, closest_y))
            else:
                # Fall back to offset method
                formatted_name = format_point_name(label_name)
                offset_x = truncate_to_precision(float(label_x) - 0.08, decimal_precision)
                offset_y = truncate_to_precision(float(label_y) - 0.2, decimal_precision)
                pairs.append((formatted_name, label_x, label_y, offset_x, offset_y))
                preserved_labels.append(f'label("${label_name}$", {formatted_name}, NE);')
        else:
            # Fall back to offset method
            formatted_name = format_point_name(label_name)
            offset_x = truncate_to_precision(float(label_x) - 0.08, decimal_precision)
            offset_y = truncate_to_precision(float(label_y) - 0.2, decimal_precision)
            pairs.append((formatted_name, label_x, label_y, offset_x, offset_y))
            preserved_labels.append(f'label("${label_name}$", {formatted_name}, NE);')
    
    # Create a lookup dictionary for point names
    point_lookup = {}
    for name, _, _, x, y in pairs:
        coord_key = f"({x},{y})"
        point_lookup[coord_key] = name
    
    # Extract draw commands
    draw_commands = []
    for line in lines:
        if line.strip().startswith('draw('):
            draw_commands.append(line)
    
    # Build the output content
    structured_content = [
        "/* Geogebra to Asymptote conversion, documentation at artofproblemsolving.com/Wiki go to User:Azjps/geogebra */", 
        "/* Asymptomatic by Charles Zhang, documentation at https://github.com/Charles1729/Asymptomatic/ */"
    ]
    
    # Add import statement
    for line in lines:
        if line.strip().startswith('import graph'):
            size_match = re.search(r'size\(([^)]+)\)', line)
            if size_match:
                size_value = truncate_to_precision(size_match.group(1).replace('cm', ''), decimal_precision)
                structured_content.append(f"import graph; size({size_value}cm);")
            else:
                structured_content.append(line)
            break
    
    # Add xmin line
    if xmin_line:
        structured_content.append(xmin_line)
    
    # Add Point Definitions
    structured_content.append("\n/* Point Definitions */")
    point_definitions = []
    seen_points = set()
    
    for name, _, _, x, y in pairs:
        if name not in seen_points:
            point_definitions.append(f"pair {name}=({x},{y});")
            seen_points.add(name)
    
    structured_content.extend(point_definitions)
    
    # Add Drawings
    structured_content.append("\n/* Drawings */")
    processed_draws = []
    
    for line in draw_commands:
        new_line = line
        # Replace coordinates with point names
        for (name, _, _, x, y) in pairs:
            coord = f"({x},{y})"
            if coord in new_line:
                new_line = new_line.replace(coord, name)
        processed_draws.append(new_line)
    
    structured_content.extend(processed_draws)
    
    # Add Labels
    structured_content.append("\n/* Labels */")
    structured_content.extend(preserved_labels)
    
    # Add Dots
    structured_content.append("\n/* Dots */")
    dot_commands = []
    seen_dots = set()
    
    for name, _, _, _, _ in pairs:
        if name not in seen_dots:
            dot_commands.append(f"dot({name});")
            seen_dots.add(name)
    
    structured_content.extend(dot_commands)
    
    # Join all lines
    new_content = '\n'.join(structured_content)
    
    # Replace any remaining coordinates with point names
    for name, _, _, x, y in pairs:
        coord = f"({x},{y})"
        if coord in new_content:
            new_content = new_content.replace(coord, name)
        new_content = new_content.replace(f"{name}={name}",f"{name}={coord}")
    
    # Clean up any remaining formatting issues
    new_content = new_content.replace(",dotstyle", "")
    
    # Write the result
    if output_file:
        with open(output_file, 'w') as f:
            f.write(new_content)
    else:
        print(new_content)
    
    return new_content

if __name__ == "__main__":
    decimal_precision = 3  # Default decimal precision
    
    if len(sys.argv) < 2:
        print("Usage: python remake.py input_file [output_file] [decimal_precision]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if len(sys.argv) > 3:
        try:
            decimal_precision = int(sys.argv[3])
            if decimal_precision < 0:
                raise ValueError("Decimal precision must be a positive integer")
        except ValueError:
            print("Error: decimal_precision must be a positive integer")
            sys.exit(1)
    
    process_file(input_file, output_file)
