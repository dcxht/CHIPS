import csv
import re
from utils import str_to_float, POSSIBLE_DEXA_FILE_COLUMNS, REGION_MAP

COLUMN_FORMULAS = {
    "ASMM kg": lambda data: str(round(float(data["Total Lean Arms kg"]) + float(data["Total Lean Legs kg"]), 3)),
    "Trunk Fat Perc BodyFat": lambda data: str(round(100 * float(data["Trunk Fat kg"]) / float(data["Total Fat kg"]), 2)),
    "Android Fat Perc BodyFat": lambda data: str(round(100 * float(data["Android Fat kg"]) / float(data["Total Fat kg"]), 2)),
    "Gynoid Fat Perc BodyFat": lambda data: str(round(100 * float(data["Gynoid Fat kg"]) / float(data["Total Fat kg"]), 2)),
    "ROI Rib Fat Perc BodyFat": lambda data: str(round(100 * float(data["ROI Rib Fat kg"]) / float(data["Total Fat kg"]), 2)),
    "ROI Abdomen Fat Perc BodyFat": lambda data: str(round(100 * float(data["ROI Abdomen Fat kg"]) / float(data["Total Fat kg"]), 1)),
    "Calc Subcutaneous Fat of Android Region kg": lambda data: str(round(float(data["Android Fat kg"]) - float(data["Visceral Fat Of Android Region kg"]), 3)),
    "ROI Chest Wall Fat Perc RegionFat": lambda data: str(round(100 * (float(data["ROI Rib Fat kg"]) + float(data["ROI Abdomen Fat kg"])) / (float(data["ROI Total Rib Mass kg"]) + float(data["ROI Total Abdomen Mass kg"])), 1)),
    "ROI Chest Wall Fat kg": lambda data: str(round(float(data["ROI Rib Fat kg"]) + float(data["ROI Abdomen Fat kg"]), 3)),
    "ROI Chest Wall Lean kg": lambda data: str(round(float(data["ROI Rib Lean kg"]) + float(data["ROI Abdomen Lean kg"]), 3)),
    "ROI Chest Wall Total Mass kg": lambda data: str(round(float(data["ROI Total Rib Mass kg"]) + float(data["ROI Total Abdomen Mass kg"]), 3)),
    "ROI Chest Wall FFM kg": lambda data: str(round(float(data["ROI Rib FFM kg"]) + float(data["ROI Abdomen FFM kg"]), 3)),
    "ROI Chest Wall Fat Perc BodyFat": lambda data: str(round(100 * float(data["ROI Chest Wall Fat kg"]) / float(data["Total Fat kg"]), 2)),
}

def parse_body_composition(content):
    print("Starting to parse the file content...")
    
    # Check for both possible starting points
    standard_start = content.find("BODY COMPOSITION: Total Body (Enhanced Analysis)")
    numeric_start = content.find("Total Body Custom Results")
    
    if standard_start != -1:
        content = content[standard_start:]
        print("Found standard format starting point")
    elif numeric_start != -1:
        content = content[numeric_start:]
        print("Found numeric format starting point")
    else:
        print("Error: Could not find either starting point in the file.")
        return None
    
    def find_column_index(col):
        # Remove whitespace and newlines for comparison
        clean_content = ''.join(content.split())
        clean_col = ''.join(col.split())
        return clean_content.index(clean_col) if clean_col in clean_content else float('inf')
    
    # Reorder columns based on their appearance in the content
    columns = sorted(POSSIBLE_DEXA_FILE_COLUMNS, key=find_column_index)
    
    data = {}
    lines = content.split('\n')
    current_region = None
    current_values = []
    using_numeric = numeric_start != -1
    
    print(f"\nParsing lines (Format: {'Numeric' if using_numeric else 'Descriptive'}):")
    for line in lines[1:]:  # Skip the header line
        line = line.strip()
        if not line or line.startswith("Fat Mass Ratios:"):
            continue
        
        print(f"Processing line: {line}")
        
        # Check if this line is a new region
        if not any(char.isdigit() for char in line) or (using_numeric and line in REGION_MAP.keys()):
            if current_region and len(current_values) == 8:
                region_key = current_region
                if using_numeric and current_region in REGION_MAP:
                    region_key = REGION_MAP[current_region]
                data[region_key] = dict(zip(columns, current_values))
                print(f"Stored data for region: {region_key}")
                print(f"Data: {data[region_key]}")
            current_region = line.replace('(e)', '').strip()
            current_values = []
        else:
            # This line contains numeric data
            values = re.findall(r'[-\d,.]+', line)
            current_values.extend(values)
    
    # Store the last region if it's complete
    if current_region and len(current_values) == len(columns):
        region_key = current_region
        if using_numeric and current_region in REGION_MAP:
            region_key = REGION_MAP[current_region]
        data[region_key] = dict(zip(columns, current_values))
        print(f"Stored final data for region: {region_key}")
        print(f"Data: {data[region_key]}")
    
    # Extract Visceral Adipose Tissue Mass if present
    vat_match = re.search(r"Estimated Visceral Adipose Tissue\s+Volume\s+Mass\s+Area\s+\d+ cm³\s+(\d+) g", content)
    if vat_match:
        data["Visceral Fat"] = {"Mass (g)": vat_match.group(1)}
        print(f"Extracted Visceral Fat Mass: {data['Visceral Fat']['Mass (g)']} g")
    
    if not data:
        print("Error: No data was parsed from the file.")
        return None

    print(f"\nParsed data structure: {data}")
    for region, values in data.items():
        print(f"{region}:")
        for key, value in values.items():
            print(f"  {key}: {value}")

    data["_format"] = "numeric" if using_numeric else "standard"
    return data

def generate_output_csv(data, output_file):
    output_columns = [
        "Total Fat PercBodyWeight", "Total Fat kg", "Total Lean kg", "Total BMC kg", "DEXA Weight kg",
        "Total FFM kg", "Total Lean Arms kg", "Total Lean Legs kg", "ASMM kg", "Trunk Fat Perc RegionFat",
        "Trunk Fat kg", "Trunk Lean kg", "Total Trunk Mass kg", "Trunk FFM kg", "Trunk Fat Perc BodyFat",
        "Android Fat Perc RegionFat", "Android Fat kg", "Android Lean kg", "Total Android Mass kg",
        "Android FFM kg", "Android Fat Perc BodyFat", "Gynoid Fat Perc RegionFat", "Gynoid Fat kg",
        "Gynoid Lean kg", "Total Gynoid Mass kg", "Gynoid FFM kg", "Gynoid Fat Perc BodyFat",
        "ROI Rib Fat Perc RegionFat", "ROI Rib Fat kg", "ROI Rib Lean kg", "ROI Total Rib Mass kg",
        "ROI Rib FFM kg", "ROI Rib Fat Perc BodyFat", "ROI Abdomen Fat Perc RegionFat",
        "ROI Abdomen Fat kg", "ROI Abdomen Lean kg", "ROI Total Abdomen Mass kg", "ROI Abdomen FFM kg",
        "ROI Abdomen Fat Perc BodyFat", "ROI Chest Wall Fat Perc RegionFat", "ROI Chest Wall Fat kg",
        "ROI Chest Wall Lean kg", "ROI Chest Wall Total Mass kg", "ROI Chest Wall FFM kg",
        "ROI Chest Wall Fat Perc BodyFat", "Visceral Fat Of Android Region kg",
        "Calc Subcutaneous Fat of Android Region kg", "FMI (kg/m2)", "FFMI (kg/m2)", "LMI (kg/m2)",
        "ASMI (kg/m2)", "ASM-to-Wt Ratio", "FMI / LMI", "LMI / FMI", "LMI / BMI"
    ]

    output_data = {col: "" for col in output_columns}  # Initialize all fields as blank

    # Process standard regions first
    for region, values in data.items():
        if region == "Total":
            output_data["Total Fat PercBodyWeight"] = f"{float(values['Region (%Fat)']):.2f}"
            output_data["Total Fat kg"] = str(round(str_to_float(values["Fat (g)"]) / 1000, 3))
            output_data["Total Lean kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
            output_data["Total BMC kg"] = str(round(str_to_float(values["BMC (g)"]) / 1000, 3))
            output_data["DEXA Weight kg"] = values["Total Mass (kg)"]
            output_data["Total FFM kg"] = str(round(str_to_float(values["Fat Free (g)"]) / 1000, 3))
        elif region == "Arms":
            output_data["Total Lean Arms kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
        elif region == "Legs":
            output_data["Total Lean Legs kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
        elif region == "Trunk":
            output_data["Trunk Fat Perc RegionFat"] = f"{float(values['Region (%Fat)']):.2f}"
            output_data["Trunk Fat kg"] = str(round(str_to_float(values["Fat (g)"]) / 1000, 3))
            output_data["Trunk Lean kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
            output_data["Total Trunk Mass kg"] = values["Total Mass (kg)"]
            output_data["Trunk FFM kg"] = str(round(str_to_float(values["Fat Free (g)"]) / 1000, 3))
        elif region == "Android":
            output_data["Android Fat Perc RegionFat"] = f"{float(values['Region (%Fat)']):.2f}"
            output_data["Android Fat kg"] = str(round(str_to_float(values["Fat (g)"]) / 1000, 3))
            output_data["Android Lean kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
            output_data["Total Android Mass kg"] = values["Total Mass (kg)"]
            output_data["Android FFM kg"] = str(round(str_to_float(values["Fat Free (g)"]) / 1000, 3))
        elif region == "Gynoid":
            output_data["Gynoid Fat Perc RegionFat"] = f"{float(values['Region (%Fat)']):.2f}"
            output_data["Gynoid Fat kg"] = str(round(str_to_float(values["Fat (g)"]) / 1000, 3))
            output_data["Gynoid Lean kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
            output_data["Total Gynoid Mass kg"] = values["Total Mass (kg)"]
            output_data["Gynoid FFM kg"] = str(round(str_to_float(values["Fat Free (g)"]) / 1000, 3))

    # Process ROI regions
    for region, values in data.items():
        if region == "ROI Rib":
            output_data["ROI Rib Fat Perc RegionFat"] = f"{float(values['Region (%Fat)']):.2f}"
            output_data["ROI Rib Fat kg"] = str(round(str_to_float(values["Fat (g)"]) / 1000, 3))
            output_data["ROI Rib Lean kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
            output_data["ROI Total Rib Mass kg"] = values["Total Mass (kg)"]
            output_data["ROI Rib FFM kg"] = str(round(str_to_float(values["Fat Free (g)"]) / 1000, 3))
        elif region == "ROI Abdomen":
            output_data["ROI Abdomen Fat Perc RegionFat"] = f"{float(values['Region (%Fat)']):.2f}"
            output_data["ROI Abdomen Fat kg"] = str(round(str_to_float(values["Fat (g)"]) / 1000, 3))
            output_data["ROI Abdomen Lean kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
            output_data["ROI Total Abdomen Mass kg"] = values["Total Mass (kg)"]
            output_data["ROI Abdomen FFM kg"] = str(round(str_to_float(values["Fat Free (g)"]) / 1000, 3))

    # Process Visceral Fat if present
    if "Visceral Fat" in data:
        output_data["Visceral Fat Of Android Region kg"] = str(round(str_to_float(data["Visceral Fat"]["Mass (g)"]) / 1000, 3))

    # Apply formulas after populating the initial data
    for column, formula in COLUMN_FORMULAS.items():
        try:
            output_data[column] = formula(output_data)
        except Exception as e:
            print(f"Error calculating {column}: {repr(e)}")
            output_data[column] = "ERROR"

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=output_columns)
        writer.writeheader()
        writer.writerow(output_data)

    print("Generated output data:", output_data)