import fitz
import re
import os

def str_to_float(s):
    return float(s.replace(',', ''))

def xps_to_text(xps_file):
    try:
        doc = fitz.open(xps_file)
        text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text() + "\n\n"
        return text
    except Exception as e:
        raise Exception(f"Error converting XPS to text: {str(e)}")

def get_file_prefix(filename):
    """Extract the numeric prefix from a filename."""
    base_name = os.path.basename(filename)
    match = re.match(r'(\d+)', base_name)
    return match.group(1) if match else None

def group_related_files(files):
    """Group files by their numeric prefix."""
    file_groups = {}
    for file in files:
        prefix = get_file_prefix(file)
        if prefix:
            if prefix not in file_groups:
                file_groups[prefix] = []
            file_groups[prefix].append(file)
    return file_groups

def merge_data(standard_data, numeric_data):
    """Merge data from standard and numeric format files."""
    if not standard_data or not numeric_data:
        return None
        
    merged_data = standard_data.copy()
    
    # Replace ROI data from numeric format
    for region_num, region_name in REGION_MAP.items():
        if region_name in numeric_data:
            merged_data[region_name] = numeric_data[region_name]
    
    return merged_data

# Constants
REGION_MAP = {
    "1": "ROI Rib",
    "2": "ROI Abdomen",
    "3": "ROI Hip",
    "4": "ROI Femur"
}

POSSIBLE_DEXA_FILE_COLUMNS = [
    "Region Tissue (%Fat)",
    "Region (%Fat)",
    "Tissue (g)",
    "Fat (g)",
    "Lean (g)",
    "BMC (g)",
    "Fat Free (g)",
    "Total Mass (kg)"
]