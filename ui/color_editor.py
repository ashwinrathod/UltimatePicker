# File: ui/color_editor.py
"""
Color Editor Widget for Ultimate Animation Picker
Provides color selection with preview and advanced options
"""

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal

class ColorEditor(QtWidgets.QWidget):
    """Color selection widget with preview and advanced options"""
    
    # Signals
    color_changed = Signal(QtGui.QColor)
    
    def __init__(self, initial_color=QtCore.Qt.white, parent=None):
        super(ColorEditor, self).__init__(parent)
        self._current_color = QtGui.QColor(initial_color)
        self._alpha_enabled = True
        self._show_name = False
        self.setup_ui()
        
    def setup_ui(self):
        """Setup color editor UI"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Color preview button
        self.color_button = QtWidgets.QPushButton()
        self.color_button.setMaximumSize(30, 20)
        self.color_button.setMinimumSize(30, 20)
        self.color_button.clicked.connect(self.show_color_dialog)
        layout.addWidget(self.color_button)
        
        # Color name label (optional)
        self.color_label = QtWidgets.QLabel()
        self.color_label.setVisible(self._show_name)
        layout.addWidget(self.color_label)
        
        # Alpha slider (optional)
        self.alpha_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.alpha_slider.setRange(0, 255)
        self.alpha_slider.setValue(255)
        self.alpha_slider.setMaximumWidth(60)
        self.alpha_slider.valueChanged.connect(self.on_alpha_changed)
        self.alpha_slider.setVisible(self._alpha_enabled)
        layout.addWidget(self.alpha_slider)
        
        # Alpha value label
        self.alpha_label = QtWidgets.QLabel("100%")
        self.alpha_label.setMinimumWidth(30)
        self.alpha_label.setVisible(self._alpha_enabled)
        layout.addWidget(self.alpha_label)
        
        layout.addStretch()
        
        # Update UI
        self.update_color_display()
        
    def set_color(self, color):
        """Set current color"""
        self._current_color = QtGui.QColor(color)
        self.alpha_slider.setValue(self._current_color.alpha())
        self.update_color_display()
        
    def get_color(self):
        """Get current color"""
        return self._current_color
        
    def set_alpha_enabled(self, enabled):
        """Enable/disable alpha channel editing"""
        self._alpha_enabled = enabled
        self.alpha_slider.setVisible(enabled)
        self.alpha_label.setVisible(enabled)
        
    def set_show_name(self, show):
        """Show/hide color name"""
        self._show_name = show
        self.color_label.setVisible(show)
        if show:
            self.update_color_display()
            
    def show_color_dialog(self):
        """Show color selection dialog"""
        color_dialog = QtWidgets.QColorDialog(self._current_color, self)
        
        if self._alpha_enabled:
            color_dialog.setOption(QtWidgets.QColorDialog.ShowAlphaChannel, True)
            
        if color_dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_color = color_dialog.selectedColor()
            if new_color != self._current_color:
                self._current_color = new_color
                self.alpha_slider.setValue(self._current_color.alpha())
                self.update_color_display()
                self.color_changed.emit(self._current_color)
                
    def on_alpha_changed(self, value):
        """Handle alpha slider change"""
        self._current_color.setAlpha(value)
        self.update_color_display()
        self.color_changed.emit(self._current_color)
        
    def update_color_display(self):
        """Update color preview and labels"""
        # Update button background
        color_style = f"""
            QPushButton {{
                background-color: rgba({self._current_color.red()}, {self._current_color.green()}, 
                                     {self._current_color.blue()}, {self._current_color.alpha()});
                border: 1px solid #888888;
            }}
            QPushButton:hover {{
                border: 2px solid #4A90E2;
            }}
        """
        self.color_button.setStyleSheet(color_style)
        
        # Update alpha label
        alpha_percent = int((self._current_color.alpha() / 255.0) * 100)
        self.alpha_label.setText(f"{alpha_percent}%")
        
        # Update color name if shown
        if self._show_name:
            self.color_label.setText(self._current_color.name())


class ColorPalette(QtWidgets.QWidget):
    """Color palette widget with predefined colors"""
    
    # Signals
    color_selected = Signal(QtGui.QColor)
    
    def __init__(self, parent=None):
        super(ColorPalette, self).__init__(parent)
        self._colors = self.create_default_palette()
        self._button_size = 24
        self._columns = 8
        self.setup_ui()
        
    def setup_ui(self):
        """Setup palette UI"""
        grid_layout = QtWidgets.QGridLayout(self)
        grid_layout.setSpacing(2)
        
        self._color_buttons = []
        
        for i, color in enumerate(self._colors):
            row = i // self._columns
            col = i % self._columns
            
            button = QtWidgets.QPushButton()
            button.setMaximumSize(self._button_size, self._button_size)
            button.setMinimumSize(self._button_size, self._button_size)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color.name()};
                    border: 1px solid #666666;
                }}
                QPushButton:hover {{
                    border: 2px solid #4A90E2;
                }}
                QPushButton:pressed {{
                    border: 2px solid #2171b5;
                }}
            """)
            
            button.clicked.connect(lambda checked, c=color: self.color_selected.emit(c))
            grid_layout.addWidget(button, row, col)
            self._color_buttons.append(button)
            
    def create_default_palette(self):
        """Create default color palette"""
        colors = []
        
        # Basic colors
        basic_colors = [
            "#FFFFFF", "#000000", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
            "#C0C0C0", "#808080", "#800000", "#008000", "#000080", "#808000", "#800080", "#008080",
            "#FFE4E1", "#F0F8FF", "#FAEBD7", "#F0FFFF", "#F5F5DC", "#FFE4C4", "#FFEBCD", "#0000CD",
            "#8FBC8F", "#483D8B", "#2F4F4F", "#00CED1", "#9400D3", "#FF1493", "#00BFFF", "#696969"
        ]
        
        for color_str in basic_colors:
            colors.append(QtGui.QColor(color_str))
            
        # Generate gradient colors
        for hue in range(0, 360, 30):
            for sat in [128, 255]:
                for val in [128, 255]:
                    color = QtGui.QColor()
                    color.setHsv(hue, sat, val)
                    colors.append(color)
                    
        return colors
        
    def add_color(self, color):
        """Add custom color to palette"""
        # Implementation for adding custom colors
        pass
        
    def remove_color(self, color):
        """Remove color from palette"""
        # Implementation for removing colors
        pass


class ColorThemeManager(QtCore.QObject):
    """Manages color themes for the picker"""
    
    # Signals
    theme_changed = Signal(str)
    
    def __init__(self, parent=None):
        super(ColorThemeManager, self).__init__(parent)
        self._themes = self.create_default_themes()
        self._current_theme = "Default"
        
    def create_default_themes(self):
        """Create default color themes"""
        themes = {}
        
        # Default theme
        themes["Default"] = {
            "background": "#3E3E3E",
            "button_normal": "#5A5A5A",
            "button_hover": "#6A6A6A",
            "button_pressed": "#4A4A4A",
            "text": "#FFFFFF",
            "accent": "#4A90E2"
        }
        
        # Dark theme
        themes["Dark"] = {
            "background": "#2B2B2B",
            "button_normal": "#404040",
            "button_hover": "#505050",
            "button_pressed": "#353535",
            "text": "#E0E0E0",
            "accent": "#0E7DB8"
        }
        
        # Light theme
        themes["Light"] = {
            "background": "#F0F0F0",
            "button_normal": "#E0E0E0",
            "button_hover": "#D0D0D0",
            "button_pressed": "#C0C0C0",
            "text": "#333333",
            "accent": "#0078D4"
        }
        
        # Maya theme
        themes["Maya"] = {
            "background": "#393939",
            "button_normal": "#4F4F4F",
            "button_hover": "#5F5F5F",
            "button_pressed": "#3F3F3F",
            "text": "#CCCCCC",
            "accent": "#FF9500"
        }
        
        return themes
        
    def get_themes(self):
        """Get available themes"""
        return list(self._themes.keys())
        
    def get_current_theme(self):
        """Get current theme name"""
        return self._current_theme
        
    def set_theme(self, theme_name):
        """Set current theme"""
        if theme_name in self._themes:
            self._current_theme = theme_name
            self.theme_changed.emit(theme_name)
            return True
        return False
        
    def get_theme_colors(self, theme_name=None):
        """Get colors for specified theme"""
        if theme_name is None:
            theme_name = self._current_theme
        return self._themes.get(theme_name, {})
        
    def add_theme(self, name, colors):
        """Add custom theme"""
        self._themes[name] = colors
        
    def remove_theme(self, name):
        """Remove theme"""
        if name != "Default" and name in self._themes:
            del self._themes[name]
            if self._current_theme == name:
                self.set_theme("Default")
                
    def export_theme(self, theme_name, file_path):
        """Export theme to file"""
        import json
        if theme_name in self._themes:
            try:
                with open(file_path, 'w') as f:
                    json.dump({theme_name: self._themes[theme_name]}, f, indent=2)
                return True
            except Exception as e:
                print(f"Error exporting theme: {e}")
        return False
        
    def import_theme(self, file_path):
        """Import theme from file"""
        import json
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                for theme_name, colors in data.items():
                    self._themes[theme_name] = colors
                return True
        except Exception as e:
            print(f"Error importing theme: {e}")
        return False


class ColorSchemeWidget(QtWidgets.QWidget):
    """Widget for managing color schemes"""
    
    def __init__(self, parent=None):
        super(ColorSchemeWidget, self).__init__(parent)
        self.theme_manager = ColorThemeManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup color scheme UI"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Theme selection
        theme_layout = QtWidgets.QHBoxLayout()
        theme_layout.addWidget(QtWidgets.QLabel("Theme:"))
        
        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(self.theme_manager.get_themes())
        self.theme_combo.currentTextChanged.connect(self.theme_manager.set_theme)
        theme_layout.addWidget(self.theme_combo)
        
        theme_layout.addStretch()
        layout.addLayout(theme_layout)
        
        # Color palette
        self.color_palette = ColorPalette()
        layout.addWidget(self.color_palette)
        
        # Theme management buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        save_theme_btn = QtWidgets.QPushButton("Save Theme")
        save_theme_btn.clicked.connect(self.save_current_theme)
        button_layout.addWidget(save_theme_btn)
        
        load_theme_btn = QtWidgets.QPushButton("Load Theme")
        load_theme_btn.clicked.connect(self.load_theme)
        button_layout.addWidget(load_theme_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
    def save_current_theme(self):
        """Save current theme to file"""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Color Theme", "", "JSON Files (*.json)"
        )
        if file_path:
            self.theme_manager.export_theme(self.theme_manager.get_current_theme(), file_path)
            
    def load_theme(self):
        """Load theme from file"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load Color Theme", "", "JSON Files (*.json)"
        )
        if file_path:
            if self.theme_manager.import_theme(file_path):
                # Update combo box
                self.theme_combo.clear()
                self.theme_combo.addItems(self.theme_manager.get_themes())
