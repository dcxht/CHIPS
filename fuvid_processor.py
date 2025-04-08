import csv
import re
from utils import str_to_float, POSSIBLE_DEXA_FILE_COLUMNS, REGION_MAP

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
        "Total %RegionFat",       
        "Total Fat kg",           
        "Total Lean kg",          
        "Total BMC kg",           
        "DEXA Weight kg",         
        "Total FFM kg",           
        
        "Trunk Fat %RegionFat",   
        "Trunk Fat kg",           
        "Trunk Lean kg",          
        "Total Trunk Mass kg",    
        "Trunk FFM kg",           
        "Trunk Fat %BodyFat",     
        
        "Android Fat %RegionFat", 
        "Android Fat kg",         
        "Android Lean kg",        
        "Total Android Mass kg",  
        "Android FFM kg",         
        "Android Fat %BodyFat",   
        
        "Gynoid Fat %RegionFat",  
        "Gynoid Fat kg",          
        "Gynoid Lean kg",         
        "Total Gynoid Mass kg",   
        "Gynoid FFM kg",          
        "Gynoid Fat %BodyFat",    
        
        "ROI Rib Fat %RegionFat", 
        "ROI Rib Fat kg",         
        "ROI Rib Lean kg",        
        "ROI Total Rib Mass kg",  
        "ROI Rib FFM kg",         
        "ROI Rib Fat %BodyFat",   
        
        "ROI Abdomen Fat %RegionFat",
        "ROI Abdomen Fat kg",      
        "ROI Abdomen Lean kg",     
        "ROI Total Abdomen Mass kg",
        "ROI Abdomen FFM kg",      
        "ROI Abdomen Fat %BodyFat",
        
        "Visceral Fat Of Android Region kg",
        "Calc Subcutaneous Fat of Android Region kg",
    ]

    output_data = {col: "" for col in output_columns}  # Initialize all fields as blank

    # Process standard regions first
    for region, values in data.items():
        if region == "Total":
            output_data["Total %RegionFat"] = f"{float(values['Region (%Fat)']):.1f}"
            output_data["Total Fat kg"] = str(round(str_to_float(values["Fat (g)"]) / 1000, 3))
            output_data["Total Lean kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
            output_data["Total BMC kg"] = str(round(str_to_float(values["BMC (g)"]) / 1000, 3))
            output_data["DEXA Weight kg"] = values["Total Mass (kg)"]
            output_data["Total FFM kg"] = str(round(str_to_float(values["Fat Free (g)"]) / 1000, 3))
            
        elif region == "Trunk":
            output_data["Trunk Fat %RegionFat"] = f"{float(values['Region (%Fat)']):.1f}"
            output_data["Trunk Fat kg"] = str(round(str_to_float(values["Fat (g)"]) / 1000, 3))
            output_data["Trunk Lean kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
            output_data["Total Trunk Mass kg"] = values["Total Mass (kg)"]
            output_data["Trunk FFM kg"] = str(round(str_to_float(values["Fat Free (g)"]) / 1000, 3))
            
        elif region == "Android":
            output_data["Android Fat %RegionFat"] = f"{float(values['Region (%Fat)']):.1f}"
            output_data["Android Fat kg"] = str(round(str_to_float(values["Fat (g)"]) / 1000, 3))
            output_data["Android Lean kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
            output_data["Total Android Mass kg"] = values["Total Mass (kg)"]
            output_data["Android FFM kg"] = str(round(str_to_float(values["Fat Free (g)"]) / 1000, 3))
            
        elif region == "Gynoid":
            output_data["Gynoid Fat %RegionFat"] = f"{float(values['Region (%Fat)']):.1f}"
            output_data["Gynoid Fat kg"] = str(round(str_to_float(values["Fat (g)"]) / 1000, 3))
            output_data["Gynoid Lean kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
            output_data["Total Gynoid Mass kg"] = values["Total Mass (kg)"]
            output_data["Gynoid FFM kg"] = str(round(str_to_float(values["Fat Free (g)"]) / 1000, 3))

    # Process ROI regions
    for region, values in data.items():
        if region == "ROI Rib":
            output_data["ROI Rib Fat %RegionFat"] = f"{float(values['Region (%Fat)']):.1f}"
            output_data["ROI Rib Fat kg"] = str(round(str_to_float(values["Fat (g)"]) / 1000, 3))
            output_data["ROI Rib Lean kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
            output_data["ROI Total Rib Mass kg"] = values["Total Mass (kg)"]
            output_data["ROI Rib FFM kg"] = str(round(str_to_float(values["Fat Free (g)"]) / 1000, 3))
            
        elif region == "ROI Abdomen":
            output_data["ROI Abdomen Fat %RegionFat"] = f"{float(values['Region (%Fat)']):.1f}"
            output_data["ROI Abdomen Fat kg"] = str(round(str_to_float(values["Fat (g)"]) / 1000, 3))
            output_data["ROI Abdomen Lean kg"] = str(round(str_to_float(values["Lean (g)"]) / 1000, 3))
            output_data["ROI Total Abdomen Mass kg"] = values["Total Mass (kg)"]
            output_data["ROI Abdomen FFM kg"] = str(round(str_to_float(values["Fat Free (g)"]) / 1000, 3))

    # Process Visceral Fat if present
    if "Visceral Fat" in data:
        vat_kg = str(round(str_to_float(data["Visceral Fat"]["Mass (g)"]) / 1000, 3))
        output_data["Visceral Fat Of Android Region kg"] = vat_kg
        
        # Calculate subcutaneous fat
        if output_data["Android Fat kg"]:
            subcut_fat = float(output_data["Android Fat kg"]) - float(vat_kg)
            output_data["Calc Subcutaneous Fat of Android Region kg"] = f"{subcut_fat:.3f}"

    # Calculate all percentages of total fat
    total_fat = float(output_data["Total Fat kg"])
    if total_fat > 0:
        # Trunk Fat %BodyFat
        if output_data["Trunk Fat kg"]:
            trunk_fat = float(output_data["Trunk Fat kg"])
            output_data["Trunk Fat %BodyFat"] = f"{(trunk_fat / total_fat * 100):.1f}"
            
        # Android Fat %BodyFat
        if output_data["Android Fat kg"]:
            android_fat = float(output_data["Android Fat kg"])
            output_data["Android Fat %BodyFat"] = f"{(android_fat / total_fat * 100):.1f}"
            
        # Gynoid Fat %BodyFat
        if output_data["Gynoid Fat kg"]:
            gynoid_fat = float(output_data["Gynoid Fat kg"])
            output_data["Gynoid Fat %BodyFat"] = f"{(gynoid_fat / total_fat * 100):.1f}"
            
        # ROI Rib Fat %BodyFat
        if output_data["ROI Rib Fat kg"]:
            rib_fat = float(output_data["ROI Rib Fat kg"])
            output_data["ROI Rib Fat %BodyFat"] = f"{(rib_fat / total_fat * 100):.1f}"
            
        # ROI Abdomen Fat %BodyFat
        if output_data["ROI Abdomen Fat kg"]:
            abdomen_fat = float(output_data["ROI Abdomen Fat kg"])
            output_data["ROI Abdomen Fat %BodyFat"] = f"{(abdomen_fat / total_fat * 100):.1f}"

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=output_columns)
        writer.writeheader()
        writer.writerow(output_data)

    print("Generated output data:", output_data)