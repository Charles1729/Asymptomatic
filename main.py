import re
import sys
from decimal import Decimal, ROUND_DOWN

def truncate_decimal(match):
    """Truncate decimal places to the specified precision."""
    num = match.group(0)
    if '.' not in num:
        return num
    
    # Handle negative numbers
    sign = ''
    if num.startswith('-'):
        sign = '-'
        num = num[1:]
    
    parts = num.split('.')
    if len(parts[1]) <= decimal_precision:
        return sign + num
    
    return sign + parts[0] + '.' + parts[1][:decimal_precision]

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
    
    # Truncate decimal places
    decimal_pattern = r'-?\d+\.\d+'
    content = re.sub(decimal_pattern, truncate_decimal, content)
    
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
        elif line.strip().startswith('real xmin'):
            xmin_line = line
    
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
    # Replace all ", linewidth(X)" where X is any number
    content = re.sub(r', linewidth\(\d+(?:\.\d+)?(pt)?\)', '', content)
    content = re.sub(r' \* labelscalefactor', '', content)
    # Remove the line with dots and labels
    content = re.sub(r'^\s*\/\* dots and labels \*\/\s*$', '', content, flags=re.MULTILINE)
    # Remove all "label("$x" lines where x is a lowercase letter
    content = re.sub(r'label\("\$[a-z].*$\n', '', content, flags=re.MULTILINE)
    
    # Process dot and label pairs using a more flexible approach
    lines = content.split('\n')
    processed_lines = []
    pairs = []
    preserved_labels = []
    
    i = 0
    while i < len(lines):
        # Try to match a label line followed by a dot line
        label_match = None
        dot_match = None
        label_line = None
        
        # Check if current line is a label line
        if i < len(lines) and lines[i].strip().startswith('label("$'):
            label_match = re.search(r'label\("\$([^$]+)\$", \(([^)]+)\)', lines[i])
            label_line = lines[i]
        
        # Check if next line is a dot line
        if i+1 < len(lines) and lines[i+1].strip().startswith('dot('):
            dot_match = re.search(r'dot\(\(([^)]+)\)', lines[i+1])
        
        # Also check in reverse order: dot line followed by label line
        if not (label_match and dot_match):
            if i < len(lines) and lines[i].strip().startswith('dot('):
                dot_match = re.search(r'dot\(\(([^)]+)\)', lines[i])
                
            if i+1 < len(lines) and lines[i+1].strip().startswith('label("$'):
                label_match = re.search(r'label\("\$([^$]+)\$", \(([^)]+)\)', lines[i+1])
                label_line = lines[i+1]
        
        if label_match and dot_match:
            label_name = label_match.group(1)
            label_coords = label_match.group(2)
            dot_coords = dot_match.group(1)
            
            # Format point name according to rules
            formatted_name = format_point_name(label_name)
            
            # Add to pairs and preserve the label
            pairs.append((formatted_name, label_coords, dot_coords))
            if label_line:
                preserved_labels.append(label_line)
            # Skip these two lines
            i += 2
        else:
            processed_lines.append(lines[i])
            i += 1
    
    # Construct the new content structure
    # First line
    structured_content = ["/* something something */"]
    
    # Add import and size
    for line in processed_lines:
        if line.strip().startswith('import graph'):
            structured_content.append(line)
            break
    
    # Add xmin line
    for line in processed_lines:
        if line.strip().startswith('real xmin'):
            structured_content.append(line)
            break
    
    # Add Point Definitions header and point definitions
    structured_content.append("\n/* Point Definitions */")
    point_definitions = []
    for name, label_coords, dot_coords in pairs:
        point_definitions.append(f"pair {name}=({dot_coords});")
    structured_content.extend(point_definitions)
    
    # Add Drawings header and drawing commands
    structured_content.append("\n/* Drawings */")
    draw_lines = [line for line in processed_lines if line.strip().startswith('draw')]
    structured_content.extend(draw_lines)
    
    # Add Labels header and preserved labels
    structured_content.append("\n/* Labels */")
    structured_content.extend(preserved_labels)
    
    # Replace all coordinates with point names in draw commands and labels
    new_content = '\n'.join(structured_content)
    
    for name, label_coords, dot_coords in pairs:
        # Replace coordinates in the drawing and label sections
        for section_start in ["/* Drawings */", "/* Labels */"]:
            section_start_idx = new_content.find(section_start)
            if section_start_idx >= 0:
                before = new_content[:section_start_idx]
                after = new_content[section_start_idx:]
                after = after.replace(f"({dot_coords})", f"{name}")
                after = after.replace(f"({label_coords})", f"{name}")
                new_content = before + after
    
    # Remove ,dotstyle
    new_content = new_content.replace(",dotstyle", "")
        
    # Add Dots header and dot commands for all defined points
    structured_content.append("\n/* Dots */")
    dot_commands = []
    for name, _, _ in pairs:
        dot_commands.append(f"dot({name});")
    structured_content.extend(dot_commands)

    # Rebuild the content with the new dot section
    new_content = '\n'.join(structured_content)
    
    # Replace all coordinate pairs with their corresponding point label
    # Slight spaghetti
    for name, x, y in pairs:
        while f"({x})" in new_content:
            new_content = new_content.replace(f"({x})", f"{name}")
        while f"({y})" in new_content:
            new_content = new_content.replace(f"({y})", f"{name}")
        new_content = new_content.replace(f"{name}={name}",f"{name}=({y})")
    
    # Write the result to the output file
    if output_file:
        with open(output_file, 'w') as f:
            f.write(new_content)
    else:
        print(new_content)
    
    return new_content

if __name__ == "__main__":
    decimal_precision = 3  # Default decimal precision
    
    if len(sys.argv) < 2:
        print("Usage: python asymptote.py input_file [output_file] [decimal_precision]")
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
