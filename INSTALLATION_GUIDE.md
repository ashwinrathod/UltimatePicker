# Ultimate Animation Picker - Installation Guide

This guide provides step-by-step instructions for installing and setting up the Ultimate Animation Picker in Autodesk Maya.

## System Requirements

### Supported Maya Versions
- Maya 2020 and later
- Maya 2022 (recommended)
- Maya 2023
- Maya 2024+

### Operating Systems
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+, CentOS 7+)

### Technical Requirements
- Python 3.7+ (included with Maya)
- PySide2/Qt5 (included with Maya)
- Minimum 4GB RAM
- Graphics card with OpenGL 3.0+ support

## Installation Methods

### Method 1: Maya Scripts Directory (Recommended for Users)

This method installs the picker globally for your Maya installation.

#### Windows
1. Navigate to your Maya scripts directory:
   ```
   C:\Users\[YourUsername]\Documents\maya\scripts\
   ```

2. Download and extract the UltimatePicker folder into this directory
   ```
   C:\Users\[YourUsername]\Documents\maya\scripts\UltimatePicker\
   ```

3. Restart Maya

#### macOS  
1. Navigate to your Maya scripts directory:
   ```
   ~/Library/Preferences/Autodesk/maya/scripts/
   ```

2. Download and extract the UltimatePicker folder:
   ```
   ~/Library/Preferences/Autodesk/maya/scripts/UltimatePicker/
   ```

3. Restart Maya

#### Linux
1. Navigate to your Maya scripts directory:
   ```
   ~/maya/scripts/
   ```

2. Extract the UltimatePicker folder:
   ```
   ~/maya/scripts/UltimatePicker/
   ```

3. Restart Maya

### Method 2: Custom Location (Recommended for Developers)

This method allows you to install the picker in any location and is useful for development or testing.

1. **Download the Tool**
   - Clone the repository: `git clone https://github.com/ashwinrathod/UltimatePicker.git`
   - Or download and extract the ZIP file to your desired location

2. **Add to Maya's Python Path**
   - Open Maya
   - Open the Script Editor (Windows > General Editors > Script Editor)
   - Switch to the Python tab
   - Run this code (adjust the path to match your installation):

   ```python
   import sys
   import os

   # Add UltimatePicker to Python path
   picker_path = "C:/path/to/your/UltimatePicker"  # Adjust this path
   if picker_path not in sys.path:
       sys.path.append(picker_path)

   # Launch the picker
   import UltimatePicker.launch
   UltimatePicker.launch.launch_ultimate_picker()
   ```

### Method 3: Maya Module File (Advanced Users)

Create a Maya module file for professional pipeline integration.

1. **Create Module File**
   Create a file named `UltimatePicker.mod` in your Maya modules directory:
   - Windows: `C:\Users\[Username]\Documents\maya\modules\`
   - macOS: `~/Library/Preferences/Autodesk/maya/modules/`
   - Linux: `~/maya/modules/`

2. **Module File Content**
   ```
   + UltimatePicker 1.0 /path/to/UltimatePicker
   PYTHONPATH+:=scripts
   ```

3. **Launch**
   ```python
   import UltimatePicker.launch
   UltimatePicker.launch.launch_ultimate_picker()
   ```

## Post-Installation Setup

### 1. Verify Installation

Run this code in Maya's Script Editor to test the installation:

```python
try:
    import UltimatePicker.launch
    print("✓ UltimatePicker successfully imported")
    
    # Test launch
    UltimatePicker.launch.launch_ultimate_picker()
    print("✓ UltimatePicker launched successfully")
    
except ImportError as e:
    print("✗ Import Error:", e)
    print("Check your installation path and Python path settings")
    
except Exception as e:
    print("✗ Launch Error:", e)
    print("Check Maya's Script Editor for detailed error messages")
