# Ultimate Animation Picker - Troubleshooting Guide

This guide helps resolve common issues when running the Ultimate Animation Picker in Maya.

## Common Import Errors

### Error: "No module named 'UltimatePicker'"

**Solution:**
```python
import sys
import os

# Add the UltimatePicker directory to Python path
picker_path = r"C:\Users\Ashwin\Documents\maya\scripts"
if picker_path not in sys.path:
    sys.path.append(picker_path)

# Now try importing
import UltimatePicker.launch
picker = UltimatePicker.launch.launch_ultimate_picker()
```

### Error: "No module named 'core'"

This means the package structure is incorrect or files are missing.

**Check:**
1. Ensure all `__init__.py` files exist:
   - `UltimatePicker/__init__.py` (create if missing)
   - `UltimatePicker/core/__init__.py`
   - `UltimatePicker/items/__init__.py`
   - `UltimatePicker/ui/__init__.py`
   - `UltimatePicker/utils/__init__.py`
   - `UltimatePicker/widgets/__init__.py`

2. Create missing `__init__.py` files:
```python
# Create an empty file or basic content:
# File: __init__.py
"""
Ultimate Animation Picker Package
"""
```

### Error: "Cannot import MenuBarManager" or similar component errors

**Solution:**
This indicates missing files in the core components. Check that all these files exist:
- `core/app.py`
- `core/menu_bar.py`
- `core/animation_toolbar.py`
- `core/tab_manager.py`

## Runtime Errors

### Error: "PySide2 not found"

**Cause:** Wrong Maya version or PySide2 not installed.

**Solutions:**
1. **Maya 2020+:** Should have PySide2 built-in
2. **Maya 2018-2019:** May need PySide2 installation:
   ```python
   # In Maya Script Editor:
   import sys
   print(sys.version)  # Check Python version
   
   # For Maya 2018/2019, you may need to install PySide2
   ```

### Error: "Main window not responding"

**Cause:** UI components not loading properly.

**Solution:**
```python
# Try launching with debug information:
import UltimatePicker.launch
import traceback

try:
    picker = UltimatePicker.launch.launch_ultimate_picker()
    print("Picker launched successfully:", picker)
except Exception as e:
    print("Error:", e)
    traceback.print_exc()
```

### Error: "Canvas not working" or "Right-click menus not appearing"

**Cause:** Missing widget files or import errors.

**Check files exist:**
- `widgets/enhanced_canvas.py`
- `widgets/context_menu.py`
- `ui/property_panel.py`

## UI Issues

### Property Panel Not Visible

**Solution:**
1. Enter Edit Mode (press 'E' or use Edit menu)
2. Property panel should appear on the right side
3. If still not visible, check Window menu for docked panels

### Items Not Creating

**Cause:** Missing item classes.

**Check files exist:**
- `items/base_item.py`
- `items/rectangle.py`
- `items/button.py`
- All other item files

**Test individual item creation:**
```python
# Test creating items directly:
from UltimatePicker.items.rectangle import RectangleItem
item = RectangleItem()
print("Item created:", item)
```

### Canvas Navigation Not Working

**Expected behavior:**
- Middle mouse button: Pan
- Mouse wheel: Zoom
- Left mouse: Select items
- Right mouse: Context menu

**If not working:**
1. Check Maya viewport navigation isn't interfering
2. Ensure canvas has focus (click on it first)
3. Try different mouse/tablet settings

## Performance Issues

### Slow Performance

**Solutions:**
1. Check number of items on canvas (very large numbers may slow performance)
2. Ensure high-quality rendering is appropriate for your system:
   ```python
   # In canvas settings, disable high-quality rendering if needed
   canvas._high_quality_rendering = False
   ```

### Memory Issues

**Solutions:**
1. Close other heavy Maya plugins
2. Restart Maya if tool has been reloaded multiple times
3. Check for memory leaks in custom commands

## File Operations Issues

### Cannot Save/Load Picker Files

**Check:**
1. File permissions in save directory
2. JSON format validity:
   ```python
   import json
   
   # Test JSON file loading:
   with open('your_picker_file.json', 'r') as f:
       data = json.load(f)
   print("JSON valid:", data)
   ```

### Picker Files Not Loading Correctly

**Common causes:**
1. File path contains special characters
2. File was saved in different version
3. Manual file editing broke JSON structure

## Debug Commands

### Enable Debug Mode

```python
# Add at beginning of launch script:
import logging
logging.basicConfig(level=logging.DEBUG)

# Then launch normally:
import UltimatePicker.launch
picker = UltimatePicker.launch.launch_ultimate_picker()
```

### Check Component Status

```python
# After launching, check components:
print("Main window:", picker)
print("Tab manager:", hasattr(picker, 'tab_manager'))
print("Canvas:", picker.tab_manager.get_current_canvas() if hasattr(picker, 'tab_manager') else None)
print("Property panel:", hasattr(picker, 'property_panel'))
```

### Test Individual Components

```python
# Test canvas creation:
from PySide2 import QtWidgets
from UltimatePicker.widgets.enhanced_canvas import EnhancedCanvas

app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
canvas = EnhancedCanvas()
canvas.show()
```

## Getting Help

### Report Issues

When reporting issues, include:

1. **Maya Version:** (e.g., Maya 2023)
2. **Operating System:** (e.g., Windows 11)
3. **Error Message:** Complete error text
4. **Steps to Reproduce:** What you were doing when error occurred
5. **Console Output:** Any additional messages in Maya Script Editor

### Diagnostic Information

Run this to gather system info:
```python
import sys
import maya.cmds as cmds

print("=== DIAGNOSTIC INFO ===")
print("Maya Version:", cmds.about(version=True))
print("Python Version:", sys.version)
print("Operating System:", cmds.about(os=True))
print("Python Path:")
for path in sys.path[:5]:  # First 5 paths
    print(f"  {path}")
print("UltimatePicker Path:")
try:
    import UltimatePicker
    print(f"  Found at: {UltimatePicker.__file__}")
except ImportError as e:
    print(f"  Not found: {e}")
```

## Recovery Procedures

### Reset to Default State

If the tool becomes unresponsive:

1. **Close Maya completely**
2. **Restart Maya**
3. **Clear Python cache:**
   ```python
   import sys
   # Remove UltimatePicker from module cache
   modules_to_remove = [m for m in sys.modules.keys() if m.startswith('UltimatePicker')]
   for module in modules_to_remove:
       del sys.modules[module]
   ```
4. **Re-import and launch**

### Clean Installation

If persistent issues occur:

1. Remove old UltimatePicker folder completely
2. Download/copy fresh version
3. Ensure correct folder structure
4. Test with minimal Maya scene (new scene)

## Advanced Debugging

### Memory Tracking

```python
import gc
import sys

# Before launching:
initial_objects = len(gc.get_objects())
print(f"Initial objects: {initial_objects}")

# Launch picker
import UltimatePicker.launch
picker = UltimatePicker.launch.launch_ultimate_picker()

# After launching:
final_objects = len(gc.get_objects())
print(f"Final objects: {final_objects}")
print(f"New objects created: {final_objects - initial_objects}")
```

### Component Testing

```python
# Test each major component individually:

# 1. Test imports
try:
    from UltimatePicker.core.app import UltimateAnimationPicker
    print("✓ Core app import successful")
except Exception as e:
    print("✗ Core app import failed:", e)

# 2. Test UI components
try:
    from UltimatePicker.ui.property_panel import PropertyPanel
    print("✓ Property panel import successful")
except Exception as e:
    print("✗ Property panel import failed:", e)

# 3. Test item creation
try:
    from UltimatePicker.items.rectangle import RectangleItem
    item = RectangleItem()
    print("✓ Rectangle item creation successful")
except Exception as e:
    print("✗ Rectangle item creation failed:", e)
```