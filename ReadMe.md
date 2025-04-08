# CHIPS (Chet Helps Integrate Perfect Spreadsheets)
## Technical Documentation

### Application Overview
CHIPS is a Python-based application designed to process and convert DEXA (Dual-energy X-ray Absorptiometry) scan files into standardized CSV formats. The application supports two different study types: Cuirass and FUVID, each with their own specific processing requirements and output formats.

### Code Structure

#### 1. Main Components (main.py)
```
ModernDEXAConverter (QMainWindow)
├── UI Components
│   ├── Study Type Selector (QComboBox)
│   ├── File List (QListWidget)
│   ├── Progress Bar (QProgressBar)
│   └── Action Buttons (QPushButton)
└── ProcessingThread (QThread)
    ├── Process Management
    └── File Handling
```

Key Classes:
- `ModernDEXAConverter`: Main GUI window inheriting from QMainWindow
- `ProcessingThread`: Handles asynchronous file processing to prevent UI freezing

#### 2. Processors (cuirass_processor.py & fuvid_processor.py)

Both processors share similar structure but different calculations:

```
├── parse_body_composition()
│   ├── Detects format (standard/numeric)
│   ├── Extracts measurements
│   └── Returns structured data dictionary
└── generate_output_csv()
    ├── Processes measurements
    ├── Calculates derived values
    └── Creates standardized CSV output
```

##### Key Differences:
- Cuirass includes additional metrics (ASMM, FMI, etc.)
- FUVID focuses on regional fat percentages
- Different output column structures
- Unique calculation formulas

#### 3. Utilities (utils.py)
```
├── File Operations
│   ├── xps_to_text(): Converts XPS to text
│   └── str_to_float(): Handles numeric conversion
├── File Management
│   ├── get_file_prefix(): Extracts numeric prefixes
│   └── group_related_files(): Groups paired files
└── Data Processing
    └── merge_data(): Combines standard/numeric formats
```

### Data Flow

1. **Input Processing**
```
Raw Files (XPS/TXT) → Text Conversion → Data Parsing → Structured Dictionary
```

2. **Data Analysis**
```
Structured Dictionary → Measurements → Calculations → Derived Values
```

3. **Output Generation**
```
Processed Data → CSV Formatting → Final Output File
```

### Key Algorithms

#### 1. File Pairing Algorithm
```python
def group_related_files(files):
    """
    1. Extract numeric prefix from filename
    2. Group files with matching prefixes
    3. Return dictionary of grouped files
    """
```

#### 2. Data Merging Algorithm
```python
def merge_data(standard_data, numeric_data):
    """
    1. Copy standard format data
    2. Replace ROI data with numeric format data
    3. Return merged dataset
    """
```

### Constants and Data Structures

#### Region Mapping
```python
REGION_MAP = {
    "1": "ROI Rib",
    "2": "ROI Abdomen",
    "3": "ROI Hip",
    "4": "ROI Femur"
}
```

#### DEXA File Columns
```python
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
```

### Error Handling

1. **File Processing**
   - Invalid file format handling
   - Missing data management
   - Conversion error catching

2. **Data Validation**
   - Numeric value verification
   - Required field checking
   - Format consistency validation

### Performance Considerations

1. **Threading**
   - File processing runs in separate thread
   - UI remains responsive during processing
   - Progress updates via signals

2. **Memory Management**
   - Processes files individually
   - Cleans up temporary data
   - Efficient string handling

### Development Guidelines

1. **Adding New Features**
   - Create new processor if needed
   - Update UI in main.py
   - Add utility functions in utils.py

2. **Modifying Calculations**
   - Update COLUMN_FORMULAS in processor
   - Adjust output columns list
   - Update data validation

3. **Adding Study Types**
   - Create new processor file
   - Add to study type selector
   - Implement required calculations

### Testing Recommendations

1. **Input Testing**
   - Various file formats
   - Different data structures
   - Edge cases

2. **Processing Testing**
   - Calculation accuracy
   - Error handling
   - Memory usage

3. **Output Testing**
   - CSV format verification
   - Data consistency
   - Derived value accuracy

### Future Enhancements Considerations

1. **Potential Features**
   - Additional study types
   - Batch processing improvements
   - Enhanced error reporting
   - Data visualization

2. **Code Optimization**
   - Calculation efficiency
   - Memory usage
   - Processing speed

### Dependencies
- PyQt6: GUI framework
- fitz: PDF/XPS processing
- csv: File output handling
- re: Text parsing
