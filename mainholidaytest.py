import sys
import os
import base64
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QListWidget, QProgressBar, QMessageBox, QFrame,
                            QComboBox, QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent, QIcon, QPalette, QColor
from datetime import datetime

from utils import xps_to_text, group_related_files, get_file_prefix, merge_data
from cuirass_processor import parse_body_composition as cuirass_parse
from cuirass_processor import generate_output_csv as cuirass_generate
from fuvid_processor import parse_body_composition as fuvid_parse
from fuvid_processor import generate_output_csv as fuvid_generate

# Holiday Detection
HOLIDAY_TITLES = {
    "New Year": "CHIPS 🎉 Happy New Year!",
    "Valentine's Day": "CHIPS 💝 Happy Valentine's Day!",
    "Independence Day": "CHIPS 🇺🇸 Happy Independence Day!",
    "Halloween": "CHIPS 🎃 Spooky Halloween!",
    "Thanksgiving": "CHIPS 🦃 Happy Thanksgiving!",
    "Christmas": "CHIPS 🎄 Merry Christmas!"
}

def get_current_holiday():
    """Determine current holiday based on date, including the week before."""
    today = datetime.now()
    month = today.month
    day = today.day
    
    def is_within_week_before(target_month, target_day):
        """Check if current date is within a week before the target date"""
        target_date = datetime(today.year, target_month, target_day)
        date_diff = target_date - today
        return 0 <= date_diff.days <= 7

    # New Year (Dec 25 - Jan 1)
    if (month == 12 and day >= 25) or (month == 1 and day == 1):
        return "New Year"
        
    # Valentine's Day (Feb 7-14)
    if month == 2 and (is_within_week_before(2, 14) or day == 14):
        return "Valentine's Day"
        
    # Independence Day (June 27 - July 4)
    if (month == 6 and day >= 27) or (month == 7 and day <= 4):
        return "Independence Day"
        
    # Halloween (Oct 24-31)
    if month == 10 and (is_within_week_before(10, 31) or day == 31):
        return "Halloween"
        
    # Thanksgiving (Week before 4th Thursday of November)
    if month == 11:
        first_day = datetime(today.year, 11, 1)
        thursday_offset = (3 - first_day.weekday()) % 7
        thanksgiving_day = 1 + thursday_offset + (3 * 7)
        if is_within_week_before(11, thanksgiving_day) or day == thanksgiving_day:
            return "Thanksgiving"
            
    # Christmas (Dec 18-25)
    if month == 12 and (is_within_week_before(12, 25) or day == 25):
        return "Christmas"
        
    return None

def get_holiday_background_pattern(holiday):
    """Return SVG pattern for holiday background with improved icons."""
    patterns = {
        "New Year": """
            <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <pattern id="new-year" width="200" height="200" patternUnits="userSpaceOnUse">
                        <path d="M50 50L53 65L60 55L65 70L70 55L77 65L80 50L83 65L90 55L85 70L80 75L95 80L80 83L85 90L70 85L75 100L70 85L65 100L60 85L55 100L50 85L45 100L40 85L35 90L40 83L25 80L40 75L35 70L30 55L37 65L40 50L43 65L50 50Z" 
                              fill="#FFD700" opacity="0.15"/>
                        <path d="M150 120L160 180L140 180L150 120M145 180L155 180L155 190L145 190Z" 
                              fill="#FFD700" opacity="0.15"/>
                        <path d="M130 120C130 90 170 90 170 120L150 150Z" 
                              fill="#FFD700" opacity="0.15"/>
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#new-year)"/>
            </svg>
        """,
        "Valentine's Day": """
            <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <pattern id="valentines" width="200" height="200" patternUnits="userSpaceOnUse">
                        <path d="M100 60C120 40 150 40 150 70C150 100 100 130 100 130C100 130 50 100 50 70C50 40 80 40 100 60Z" 
                              fill="#FF69B4" opacity="0.12"/>
                        <path d="M40 60L160 60M150 50L160 60L150 70" 
                              fill="#FF69B4" opacity="0.12"/>
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#valentines)"/>
            </svg>
        """,
        "Independence Day": """
            <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <pattern id="patriotic" width="200" height="200" patternUnits="userSpaceOnUse">
                        <rect width="200" height="40" y="0" fill="#B71C1C" opacity="0.08"/>
                        <rect width="200" height="40" y="80" fill="#B71C1C" opacity="0.08"/>
                        <rect width="200" height="40" y="160" fill="#B71C1C" opacity="0.08"/>
                        <path d="M50 50L55 65L70 70L55 75L50 90L45 75L30 70L45 65L50 50Z" 
                              fill="#0D47A1" opacity="0.12"/>
                        <path d="M150 110L155 125L170 130L155 135L150 150L145 135L130 130L145 125L150 110Z" 
                              fill="#0D47A1" opacity="0.12"/>
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#patriotic)"/>
            </svg>
        """,
        "Halloween": """
            <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <pattern id="halloween" width="200" height="200" patternUnits="userSpaceOnUse">
                        <!-- Jack O'Lantern -->
                        <path d="M100 50 C140 50 160 90 160 130 C160 170 40 170 40 130 C40 90 60 50 100 50Z" 
                              fill="black" opacity="0.12"/>
                        <path d="M90 90L70 100L90 110ZM110 90L130 100L110 110Z" 
                              fill="black" opacity="0.12"/>
                        <path d="M80 120Q100 140 120 120" 
                              fill="black" opacity="0.12"/>
                        <path d="M95 40L105 40L105 60L95 60Z" 
                              fill="black" opacity="0.12"/>
                        <!-- Stem and Leaf -->
                        <path d="M95 30Q100 20 105 30L100 40Z" 
                              fill="black" opacity="0.12"/>
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#halloween)"/>
            </svg>
        """,
        "Thanksgiving": """
            <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <pattern id="thanksgiving" width="200" height="200" patternUnits="userSpaceOnUse">
                        <!-- Turkey Body -->
                        <path d="M100 100C130 100 150 120 150 150C150 180 50 180 50 150C50 120 70 100 100 100Z" 
                              fill="#8B4513" opacity="0.12"/>
                        <!-- Turkey Head -->
                        <path d="M100 90C110 90 120 95 120 105C120 115 80 115 80 105C80 95 90 90 100 90Z" 
                              fill="#8B4513" opacity="0.12"/>
                        <!-- Feathers -->
                        <path d="M60 80C80 60 120 60 140 80L100 100Z" 
                              fill="#8B4513" opacity="0.12"/>
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#thanksgiving)"/>
            </svg>
        """,
        "Christmas": """
            <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <pattern id="christmas" width="200" height="200" patternUnits="userSpaceOnUse">
                        <!-- Christmas Tree -->
                        <path d="M100 20L130 60L120 60L150 100L110 100L140 140L60 140L90 100L50 100L80 60L70 60L100 20Z" 
                              fill="#228B22" opacity="0.12"/>
                        <!-- Tree Trunk -->
                        <path d="M90 140L110 140L110 160L90 160Z" 
                              fill="#8B4513" opacity="0.12"/>
                        <!-- Ornaments -->
                        <circle cx="90" cy="50" r="5" fill="#FF0000" opacity="0.12"/>
                        <circle cx="110" cy="80" r="5" fill="#FFD700" opacity="0.12"/>
                        <circle cx="85" cy="110" r="5" fill="#FF0000" opacity="0.12"/>
                        <circle cx="120" cy="120" r="5" fill="#FFD700" opacity="0.12"/>
                        <!-- Star -->
                        <path d="M100 10L105 20L115 20L107 27L110 37L100 32L90 37L93 27L85 20L95 20Z" 
                              fill="#FFD700" opacity="0.15"/>
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#christmas)"/>
            </svg>
        """
    }
    return patterns.get(holiday, "")
def apply_holiday_theme(window):
    """Apply holiday-specific theme to the window."""
    # Get holiday from theme selector if available, otherwise use current date
    if hasattr(window, 'theme_selector'):
        holiday = window.theme_selector.currentText()
        if holiday == "Default":
            return
    else:
        holiday = get_current_holiday()
        
    if not holiday:
        return
        
    palette = window.palette()
    background_pattern = get_holiday_background_pattern(holiday)
    if background_pattern:
        base64_pattern = base64.b64encode(background_pattern.encode()).decode()
        background_image = f"url(data:image/svg+xml;base64,{base64_pattern})"
    else:
        background_image = "none"
    
    theme_styles = {
        "New Year": {
            "bg_color": "#F8F9FA",
            "button_color": "#DAA520",
            "button_hover": "#B8860B",
            "accent_color": "#FFD700",
            "text_color": "#212529"
        },
        "Valentine's Day": {
            "bg_color": "#FFF0F5",
            "button_color": "#DB7093",
            "button_hover": "#C71585",
            "accent_color": "#FF69B4",
            "text_color": "#212529"
        },
        "Independence Day": {
            "bg_color": "#FFFFFF",
            "button_color": "#3D5A80",
            "button_hover": "#2B4162",
            "accent_color": "#B71C1C",
            "text_color": "#212529"
        },
        "Halloween": {
            "bg_color": "#FFF8DC",
            "button_color": "#FF7518",
            "button_hover": "#E65C00",
            "accent_color": "#000000",
            "text_color": "#212529"
        },
        "Thanksgiving": {
            "bg_color": "#FFF8E7",
            "button_color": "#B87745",
            "button_hover": "#946038",
            "accent_color": "#8B4513",
            "text_color": "#212529"
        },
        "Christmas": {
            "bg_color": "#FFF8F8",
            "button_color": "#2D5A27",
            "button_hover": "#1B4720",
            "accent_color": "#B22222",
            "text_color": "#212529"
        },
        "Easter": {
            "bg_color": "#FFF5F5",
            "button_color": "#DDA0DD",
            "button_hover": "#BA55D3",
            "accent_color": "#FFB6C1",
            "text_color": "#212529"
        },
        "Cinco de Mayo": {
            "bg_color": "#FFFFFF",
            "button_color": "#FF6B6B",
            "button_hover": "#E84855",
            "accent_color": "#4ECDC4",
            "text_color": "#212529"
        },
        "Start of Summer": {
            "bg_color": "#F0F8FF",
            "button_color": "#4169E1",
            "button_hover": "#1E90FF",
            "accent_color": "#FFD700",
            "text_color": "#212529"
        },
        "Flag Day": {
            "bg_color": "#FFFFFF",
            "button_color": "#0D47A1",
            "button_hover": "#1565C0",
            "accent_color": "#B71C1C",
            "text_color": "#212529"
        },
        "Labor Day": {
            "bg_color": "#F5F5F5",
            "button_color": "#696969",
            "button_hover": "#4A4A4A",
            "accent_color": "#FFD700",
            "text_color": "#212529"
        },
        "St. Patrick's Day": {
            "bg_color": "#E0F8E0",
            "button_color": "#4CAF50",
            "button_hover": "#388E3C",
            "accent_color": "#8BC34A",
            "text_color": "#212529"
        }
    }
    
    style = theme_styles[holiday]
    palette.setColor(QPalette.ColorRole.Window, QColor(style["bg_color"]))
    
    window.setStyleSheet(f"""
        QMainWindow {{
            background-color: {style["bg_color"]};
            background-image: {background_image};
            background-repeat: repeat;
        }}
        QPushButton {{
            background-color: {style["button_color"]};
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {style["button_hover"]};
        }}
        QPushButton:disabled {{
            background-color: #E9ECEF;
            color: #6C757D;
        }}
        QLabel {{
            color: {style["text_color"]};
        }}
        QComboBox {{
            background-color: white;
            color: {style["text_color"]};
            border: 1px solid {style["button_color"]};
            border-radius: 5px;
            padding: 5px;
        }}
        QListWidget {{
            background-color: white;
            border: 1px solid {style["button_color"]};
            border-radius: 5px;
            padding: 5px;
        }}
        QListWidget::item {{
            padding: 3px;
            border-bottom: 1px solid #ECF0F1;
        }}
        QProgressBar {{
            border: 1px solid {style["button_color"]};
            border-radius: 3px;
            text-align: center;
            height: 20px;
        }}
        QProgressBar::chunk {{
            background-color: {style["button_color"]};
        }}
    """)
    
    window.setWindowTitle(HOLIDAY_TITLES.get(holiday, "CHIPS"))
    window.setPalette(palette)

class ProcessingThread(QThread):
    """Thread for handling file processing"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    
    def __init__(self, files, output_dir, processing_type):
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self.processing_type = processing_type
        
    def run(self):
        try:
            success_count = 0
            error_count = 0
            merged_count = 0
            total_files = len(self.files)
            processed_count = 0
            
            parse_function = cuirass_parse if self.processing_type == "Cuirass" else fuvid_parse
            generate_function = cuirass_generate if self.processing_type == "Cuirass" else fuvid_generate
            
            file_groups = group_related_files(self.files)
            standalone_files = [f for f in self.files if get_file_prefix(f) is None]
            
            for prefix, files in file_groups.items():
                try:
                    if len(files) == 2:
                        data1 = parse_function(xps_to_text(files[0]) if files[0].lower().endswith('.xps') 
                                            else open(files[0], 'r').read())
                        data2 = parse_function(xps_to_text(files[1]) if files[1].lower().endswith('.xps') 
                                            else open(files[1], 'r').read())
                        
                        standard_data = data1 if data1["_format"] == "standard" else data2
                        numeric_data = data1 if data1["_format"] == "numeric" else data2
                        
                        merged_data = merge_data(standard_data, numeric_data)
                        
                        if merged_data:
                            output_file = os.path.join(self.output_dir, f"{prefix}_merged_output.csv")
                            generate_function(merged_data, output_file)
                            merged_count += 1
                            success_count += 2
                            processed_count += 2
                    else:
                        if self.process_single_file(files[0]):
                            success_count += 1
                        else:
                            error_count += 1
                        processed_count += 1
                        
                except Exception as e:
                    error_count += 1
                    processed_count += len(files)
                    print(f"Error processing files with prefix {prefix}: {str(e)}")
                
                self.progress.emit(int(processed_count / total_files * 100))
            
            for file in standalone_files:
                if self.process_single_file(file):
                    success_count += 1
                else:
                    error_count += 1
                processed_count += 1
                self.progress.emit(int(processed_count / total_files * 100))
            
            results = {
                'success': success_count,
                'errors': error_count,
                'merged': merged_count
            }
            self.finished.emit(results)
            
        except Exception as e:
            self.finished.emit({'error': str(e)})
    
    def process_single_file(self, file):
        try:
            content = xps_to_text(file) if file.lower().endswith('.xps') else open(file, 'r').read()
            parse_function = cuirass_parse if self.processing_type == "Cuirass" else fuvid_parse
            generate_function = cuirass_generate if self.processing_type == "Cuirass" else fuvid_generate
            
            parsed_data = parse_function(content)
            if parsed_data:
                base_name = os.path.splitext(os.path.basename(file))[0]
                output_file = os.path.join(self.output_dir, f"{base_name}_output.csv")
                generate_function(parsed_data, output_file)
                return True
            return False
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
            return False
class ModernDEXAConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CHIPS")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.files = []
        self.output_dir = None
        self.init_ui()
        apply_holiday_theme(self)
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Title Container with Holiday Greeting
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main Title
        header = QLabel("CHIPS")
        header.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setStyleSheet("color: #2C3E50; margin: 10px 0;")
        title_layout.addWidget(header)
        
        # Holiday Greeting (will be populated if holiday is active)
        self.holiday_label = QLabel("")
        self.holiday_label.setFont(QFont("Arial", 24))
        self.holiday_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.holiday_label.setStyleSheet("color: #2C3E50; margin: 10px 0;")
        title_layout.addWidget(self.holiday_label)
        
        layout.addWidget(title_container)
        
        # Processing Type and Theme Selection
        selection_container = QWidget()
        selection_layout = QHBoxLayout(selection_container)
        selection_layout.setContentsMargins(0, 0, 0, 10)
        
        type_label = QLabel("Study: ")
        type_label.setFont(QFont("Arial", 11))
        type_label.setStyleSheet("color: #2C3E50;")
        selection_layout.addWidget(type_label)
        
        self.processing_type = QComboBox()
        self.processing_type.addItems(["Cuirass", "FUVID"])
        self.processing_type.setMinimumWidth(150)
        selection_layout.addWidget(self.processing_type)
        
        # Add spacing between dropdowns
        selection_layout.addSpacing(20)
        
        # Add Theme Selection
        theme_label = QLabel("Theme: ")
        theme_label.setFont(QFont("Arial", 11))
        theme_label.setStyleSheet("color: #2C3E50;")
        selection_layout.addWidget(theme_label)
        
        self.theme_selector = QComboBox()
        self.theme_selector.addItems([
            "Default",
            "New Year",
            "Valentine's Day",
            "Easter",
            "Cinco de Mayo",
            "Start of Summer",
            "Flag Day",
            "Independence Day",
            "Labor Day",
            "Halloween",
            "Thanksgiving",
            "Christmas",
            "St. Patrick's Day"
        ])
        self.theme_selector.setMinimumWidth(150)
        self.theme_selector.currentTextChanged.connect(self.change_theme)
        selection_layout.addWidget(self.theme_selector)
        
        selection_layout.addStretch()
        layout.addWidget(selection_container)
        
        # File List
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        layout.addWidget(self.file_list)
        
        # Buttons Container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.add_button = QPushButton("Add Files")
        self.add_button.setMinimumWidth(120)
        self.add_button.clicked.connect(self.select_files)
        button_layout.addWidget(self.add_button)
        
        self.clear_button = QPushButton("Clear Selection")
        self.clear_button.setMinimumWidth(120)
        self.clear_button.clicked.connect(self.clear_selection)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        layout.addWidget(button_container)
        
        # Output Directory
        self.output_button = QPushButton("Select Output Directory")
        self.output_button.clicked.connect(self.select_output_directory)
        layout.addWidget(self.output_button)
        
        self.output_label = QLabel("No output directory selected")
        self.output_label.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        layout.addWidget(self.output_label)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Convert Button
        self.convert_button = QPushButton("Convert Files")
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setEnabled(False)
        layout.addWidget(self.convert_button)
        
        # Status Label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        # Update holiday greeting if applicable
        self.update_holiday_greeting()
        
    def update_holiday_greeting(self):
        """Update the holiday greeting label based on current holiday."""
        holiday = get_current_holiday()
        if holiday:
            greeting_map = {
                "New Year": "✨ Happy New Year!",
                "Valentine's Day": "💝 Happy Valentine's Day!",
                "Independence Day": "🇺🇸 Happy Fourth of July!",
                "Halloween": "🎃 Spooky Season!",
                "Thanksgiving": "🦃 Happy Thanksgiving!",
                "Christmas": "🎄 Merry Christmas!",
                "St. Patrick's Day": "🍀 Happy St. Patrick's Day! 🍀"
            }
            self.holiday_label.setText(greeting_map.get(holiday, ""))
        else:
            self.holiday_label.setText("")
    
    def add_files(self, file_paths):
        for file_path in file_paths:
            if file_path not in self.files:
                self.files.append(file_path)
                self.file_list.addItem(os.path.basename(file_path))
        self.update_convert_button()
        
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "XPS Files (*.xps);;Text Files (*.txt);;All Files (*.*)"
        )
        self.add_files(files)
        
    def clear_selection(self):
        self.files.clear()
        self.file_list.clear()
        self.update_convert_button()
        
    def select_output_directory(self):
        self.output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory"
        )
        if self.output_dir:
            self.output_label.setText(f"Output Directory: ...{self.output_dir[-30:]}")
            self.update_convert_button()
            
    def update_convert_button(self):
        self.convert_button.setEnabled(bool(self.files and self.output_dir))
        
    def start_conversion(self):
        self.progress_bar.setVisible(True)
        self.convert_button.setEnabled(False)
        self.status_label.setText("Processing files...")
        
        processing_type = self.processing_type.currentText()
        self.processing_thread = ProcessingThread(self.files, self.output_dir, processing_type)
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.finished.connect(self.conversion_finished)
        self.processing_thread.start()
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def conversion_finished(self, results):
        self.progress_bar.setVisible(False)
        self.convert_button.setEnabled(True)
        
        if 'error' in results:
            QMessageBox.critical(self, "Error", f"An error occurred: {results['error']}")
            return
            
        message = f"🎊 Conversion complete! 🎊\n\n"
        if results['merged'] > 0:
            message += f"Successfully merged: {results['merged']} pairs ({results['merged'] * 2} files)\n"
        message += f"Successfully processed: {results['success']} files\n"
        if results['errors'] > 0:
            message += f"Errors encountered: {results['errors']} files"
            
        QMessageBox.information(self, "Success", message)
        self.status_label.setText("Ready")

    def change_theme(self, theme):
        """Change the theme based on combo box selection."""
        if theme == "Default":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: white;
                }
                QPushButton {
                    background-color: #0D6EFD;
                    color: white;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0B5ED7;
                }
                QPushButton:disabled {
                    background-color: #E9ECEF;
                    color: #6C757D;
                }
                QListWidget, QComboBox {
                    border: 1px solid #DEE2E6;
                    border-radius: 5px;
                    padding: 5px;
                }
                QComboBox {
                    background-color: white;
                    min-height: 30px;
                }
                QLabel {
                    color: #212529;
                }
                QProgressBar {
                    border: 1px solid #DEE2E6;
                    border-radius: 3px;
                    text-align: center;
                    height: 20px;
                }
                QProgressBar::chunk {
                    background-color: #0D6EFD;
                }
            """)
            self.setWindowTitle("CHIPS")
            self.holiday_label.setText("")
        else:
            # Update both theme and titles
            self.setWindowTitle(HOLIDAY_TITLES.get(theme, "CHIPS"))
            greeting_map = {
                "New Year": "✨ Happy New Year!",
                "Valentine's Day": "💝 Happy Valentine's Day!",
                "Easter": "🐰 Happy Easter! 🥚",
                "Cinco de Mayo": "🌮 ¡Feliz Cinco de Mayo! 🎊",
                "Start of Summer": "🌞 Hello Summer! 🏖️",
                "Flag Day": "🚩 Happy Flag Day! 🚩",
                "Independence Day": "🦅 Happy 4th of July! 🗽",
                "Labor Day": "👷 Happy Labor Day! 🛠️",
                "Halloween": "👺🕷️🕸️🎃💀🦇🪓BOO!🩸🕯️👻🐺⚰️🧟‍♂️🤡",
                "Thanksgiving": "🦃 Happy Thanksgiving!",
                "Christmas": "🎄🎁🤶⛄ Merry Christmas!❄️🦌🛷🎅",
                "St. Patrick's Day": "🍀 Happy St. Patrick's Day! 🍀"
            }
            self.holiday_label.setText(greeting_map.get(theme, ""))
            apply_holiday_theme(self)

def main():
    app = QApplication(sys.argv)
    window = ModernDEXAConverter()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()