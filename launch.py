# File: launch.py
"""
Ultimate Animation Picker Launcher
Main entry point for the Ultimate Animation Picker tool

Usage in Maya:
    import UltimatePicker.launch
    UltimatePicker.launch.launch_ultimate_picker()
"""

import sys
import os

def launch_ultimate_picker():
    """Launch the Ultimate Animation Picker"""
    
    # Check if we're running in Maya
    try:
        import maya.cmds as cmds
        print("Ultimate Animation Picker - Starting in Maya environment")
    except ImportError:
        print("Warning: Maya not detected. Some features may not work.")
        return None
    
    try:
        # Add current directory to path if not already there
        current_dir = os.path.dirname(__file__)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Import and launch the main application
        from core.app import launch_ultimate_picker as launch_app
        
        # Launch the application
        picker_window = launch_app()
        
        print("Ultimate Animation Picker launched successfully!")
        print("Features available:")
        print("- Unlimited canvas with pan/zoom navigation")
        print("- Multiple picker item types (buttons, sliders, checkboxes, etc.)")
        print("- Edit mode with property panel")
        print("- Animation toolbar with pose operations")
        print("- Tab management system")
        print("- Context menus and advanced tools")
        
        return picker_window
        
    except Exception as e:
        print(f"Error launching Ultimate Animation Picker: {e}")
        import traceback
        traceback.print_exc()
        return None


# For backward compatibility and alternative launch methods
def main():
    """Alternative main function"""
    return launch_ultimate_picker()


if __name__ == "__main__":
    # Direct execution (for testing outside Maya)
    print("Ultimate Animation Picker")
    print("This tool is designed to run within Autodesk Maya.")
    print("Please run from within Maya using:")
    print("import UltimatePicker.launch")
    print("UltimatePicker.launch.launch_ultimate_picker()")