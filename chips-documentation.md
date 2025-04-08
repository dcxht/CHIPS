# CHIPS - DEXA Scan Processing Application
## User Documentation

### What is CHIPS?
CHIPS is a user-friendly application that processes DEXA (Dual-energy X-ray Absorptiometry) scan files. It takes scan files and converts them into organized spreadsheets (CSV files) that are easier to analyze and work with.

### Getting Started

#### System Requirements
- A computer running Windows, Mac, or Linux
- Enough disk space to store your scan files and processed results
- The CHIPS application installed on your computer

#### Main Window Layout
When you open CHIPS, you'll see:
- A large "CHIPS" title at the top
- A dropdown menu to select your study type (Cuirass or FUVID)
- A box showing your selected files
- Several buttons for different actions
- A progress bar (only visible during processing)

### Step-by-Step Usage Guide

1. **Select Your Study Type**
   - Click the dropdown menu under "Study"
   - Choose either "Cuirass" or "FUVID" depending on your study type
   - If unsure, check with your research coordinator

2. **Adding Files**
   - Click the "Add Files" button
   - In the file browser that opens:
     - Navigate to where your scan files are stored
     - Select one or more files to process
     - Click "Open"
   - The files you selected will appear in the list box
   - You can add more files at any time by clicking "Add Files" again

3. **Selecting Output Location**
   - Click "Select Output Directory"
   - Choose where you want the processed files to be saved
   - The selected location will be shown below the button

4. **Processing Files**
   - Once you've added files and selected an output location, the "Convert Files" button will become active
   - Click "Convert Files" to start processing
   - A progress bar will show the status
   - Wait for processing to complete

5. **Viewing Results**
   - When processing is finished, a message will show the results
   - Your processed files will be in your chosen output directory
   - Each file will be named based on the original scan file
   - For paired files, you'll see a "_merged_output.csv" file

### Special Features

#### Handling Paired Files
- If you have related scan files (usually with the same number at the start of the filename), CHIPS will automatically:
  - Recognize them as a pair
  - Process them together
  - Create a single merged output file

#### File Types
CHIPS can process:
- XPS files (usually from the DEXA scanner)
- Text files (TXT)

### Troubleshooting

#### Common Issues and Solutions

1. **Files Not Appearing in List**
   - Make sure you're selecting the correct file type
   - Try clearing the selection and adding files again

2. **Convert Button Not Active**
   - Check that you have:
     - Added at least one file
     - Selected an output directory

3. **Processing Errors**
   - Make sure your files are valid DEXA scan files
   - Check that you selected the correct study type
   - Ensure you have enough disk space

4. **Output Files Not Found**
   - Double-check your selected output directory
   - Make sure processing completed successfully
   - Look for files with "_output.csv" or "_merged_output.csv" endings

### Understanding Output Files

Your processed files will be spreadsheets (CSV files) containing:
- Body composition measurements
- Regional analysis (arms, legs, trunk, etc.)
- Calculated ratios and percentages
- Fat and lean mass measurements

The exact measurements included will depend on your selected study type (Cuirass or FUVID).

### Getting Help
If you encounter problems:
1. Double-check all steps in this guide
2. Consult with your research coordinator
3. Make note of any error messages you see
4. Take screenshots if possible

### Best Practices
1. Keep your files organized in folders
2. Use a clear naming system for your output directories
3. Process files in small batches if you have many
4. Regularly back up your original scan files
5. Check processed files after conversion to ensure data looks correct

Remember: CHIPS is designed to be user-friendly, but always double-check your results and consult with your research team if you're unsure about anything.
