# File: utils/style_manager.py
"""
Style Manager for Ultimate Animation Picker
Manages themes, styles, and visual consistency across the application
"""

import json
import os
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Signal

class StyleTheme:
    """Style theme container"""
    
    def __init__(self, name, colors=None, fonts=None, sizes=None):
        self.name = name
        self.colors = colors or {}
        self.fonts = fonts or {}
        self.sizes = sizes or {}
        self.metadata = {}
        
    def get_color(self, color_name, default=None):
        """Get color by name"""
        return self.colors.get(color_name, default or QtCore.Qt.gray)
        
    def get_font(self, font_name, default_size=10):
        """Get font by name"""
        font_info = self.fonts.get(font_name, {})
        family = font_info.get('family', 'Arial')
        size = font_info.get('size', default_size)
        bold = font_info.get('bold', False)
        italic = font_info.get('italic', False)
        
        font = QtGui.QFont(family, size)
        font.setBold(bold)
        font.setItalic(italic)
        return font
        
    def get_size(self, size_name, default=10):
        """Get size by name"""
        return self.sizes.get(size_name, default)
        
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'name': self.name,
            'colors': {name: color.name() if hasattr(color, 'name') else str(color) 
                      for name, color in self.colors.items()},
            'fonts': self.fonts,
            'sizes': self.sizes,
            'metadata': self.metadata
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        theme = cls(data.get('name', 'Unnamed'))
        
        # Convert color strings back to QColor
        colors = {}
        for name, color_str in data.get('colors', {}).items():
            colors[name] = QtGui.QColor(color_str)
        theme.colors = colors
        
        theme.fonts = data.get('fonts', {})
        theme.sizes = data.get('sizes', {})
        theme.metadata = data.get('metadata', {})
        
        return theme


class StyleManager(QtCore.QObject):
    """Manages application styles and themes"""
    
    # Signals
    theme_changed = Signal(str)  # theme_name
    style_updated = Signal()
    
    def __init__(self, parent=None):
        super(StyleManager, self).__init__(parent)
        self._themes = {}
        self._current_theme = None
        self._custom_styles = {}
        self._style_cache = {}
        
        # Initialize default themes
        self.create_default_themes()
        self.set_theme('Default')
        
    def create_default_themes(self):
        """Create default application themes"""
        # Default theme
        default_theme = StyleTheme('Default')
        default_theme.colors = {
            'background': QtGui.QColor('#3E3E3E'),
            'canvas_background': QtGui.QColor('#2D2D2D'),
            'button_normal': QtGui.QColor('#5A5A5A'),
            'button_hover': QtGui.QColor('#6A6A6A'),
            'button_pressed': QtGui.QColor('#4A4A4A'),
            'button_selected': QtGui.QColor('#4A90E2'),
            'text_normal': QtGui.QColor('#FFFFFF'),
            'text_disabled': QtGui.QColor('#888888'),
            'border_normal': QtGui.QColor('#666666'),
            'border_selected': QtGui.QColor('#4A90E2'),
            'grid_lines': QtGui.QColor('#444444'),
            'selection_box': QtGui.QColor('#4A90E2'),
            'accent': QtGui.QColor('#FF9500'),
            'success': QtGui.QColor('#4CAF50'),
            'warning': QtGui.QColor('#FF9800'),
            'error': QtGui.QColor('#F44336')
        }
        default_theme.fonts = {
            'default': {'family': 'Arial', 'size': 9},
            'small': {'family': 'Arial', 'size': 8},
            'large': {'family': 'Arial', 'size': 12},
            'title': {'family': 'Arial', 'size': 14, 'bold': True},
            'code': {'family': 'Consolas', 'size': 9}
        }
        default_theme.sizes = {
            'button_height': 24,
            'toolbar_height': 32,
            'splitter_width': 4,
            'margin_small': 4,
            'margin_medium': 8,
            'margin_large': 16,
            'border_radius': 4,
            'selection_border_width': 2
        }
        self._themes['Default'] = default_theme
        
        # Dark theme
        dark_theme = StyleTheme('Dark')
        dark_theme.colors = {
            'background': QtGui.QColor('#1E1E1E'),
            'canvas_background': QtGui.QColor('#0D1117'),
            'button_normal': QtGui.QColor('#2D2D2D'),
            'button_hover': QtGui.QColor('#404040'),
            'button_pressed': QtGui.QColor('#1A1A1A'),
            'button_selected': QtGui.QColor('#0E7DB8'),
            'text_normal': QtGui.QColor('#E6E6E6'),
            'text_disabled': QtGui.QColor('#6E6E6E'),
            'border_normal': QtGui.QColor('#444444'),
            'border_selected': QtGui.QColor('#0E7DB8'),
            'grid_lines': QtGui.QColor('#333333'),
            'selection_box': QtGui.QColor('#0E7DB8'),
            'accent': QtGui.QColor('#FF6B35'),
            'success': QtGui.QColor('#28A745'),
            'warning': QtGui.QColor('#FFC107'),
            'error': QtGui.QColor('#DC3545')
        }
        dark_theme.fonts = default_theme.fonts.copy()
        dark_theme.sizes = default_theme.sizes.copy()
        self._themes['Dark'] = dark_theme
        
        # Light theme
        light_theme = StyleTheme('Light')
        light_theme.colors = {
            'background': QtGui.QColor('#F5F5F5'),
            'canvas_background': QtGui.QColor('#FFFFFF'),
            'button_normal': QtGui.QColor('#E0E0E0'),
            'button_hover': QtGui.QColor('#D0D0D0'),
            'button_pressed': QtGui.QColor('#C0C0C0'),
            'button_selected': QtGui.QColor('#0078D4'),
            'text_normal': QtGui.QColor('#333333'),
            'text_disabled': QtGui.QColor('#999999'),
            'border_normal': QtGui.QColor('#CCCCCC'),
            'border_selected': QtGui.QColor('#0078D4'),
            'grid_lines': QtGui.QColor('#E0E0E0'),
            'selection_box': QtGui.QColor('#0078D4'),
            'accent': QtGui.QColor('#FF8C00'),
            'success': QtGui.QColor('#5CB85C'),
            'warning': QtGui.QColor('#F0AD4E'),
            'error': QtGui.QColor('#D9534F')
        }
        light_theme.fonts = default_theme.fonts.copy()
        light_theme.sizes = default_theme.sizes.copy()
        self._themes['Light'] = light_theme
        
        # Maya theme
        maya_theme = StyleTheme('Maya')
        maya_theme.colors = {
            'background': QtGui.QColor('#393939'),
            'canvas_background': QtGui.QColor('#2E2E2E'),
            'button_normal': QtGui.QColor('#4F4F4F'),
            'button_hover': QtGui.QColor('#5F5F5F'),
            'button_pressed': QtGui.QColor('#3F3F3F'),
            'button_selected': QtGui.QColor('#FF9500'),
            'text_normal': QtGui.QColor('#CCCCCC'),
            'text_disabled': QtGui.QColor('#888888'),
            'border_normal': QtGui.QColor('#666666'),
            'border_selected': QtGui.QColor('#FF9500'),
            'grid_lines': QtGui.QColor('#4A4A4A'),
            'selection_box': QtGui.QColor('#FF9500'),
            'accent': QtGui.QColor('#00BFFF'),
            'success': QtGui.QColor('#90EE90'),
            'warning': QtGui.QColor('#FFD700'),
            'error': QtGui.QColor('#FF6B6B')
        }
        maya_theme.fonts = default_theme.fonts.copy()
        maya_theme.sizes = default_theme.sizes.copy()
        self._themes['Maya'] = maya_theme
        
    def get_themes(self):
        """Get list of available themes"""
        return list(self._themes.keys())
        
    def get_current_theme(self):
        """Get current theme"""
        return self._current_theme
        
    def set_theme(self, theme_name):
        """Set current theme"""
        if theme_name in self._themes:
            old_theme = self._current_theme
            self._current_theme = self._themes[theme_name]
            
            # Clear style cache
            self._style_cache.clear()
            
            # Emit signals
            self.theme_changed.emit(theme_name)
            self.style_updated.emit()
            
            return True
        return False
        
    def get_color(self, color_name, default=None):
        """Get color from current theme"""
        if self._current_theme:
            return self._current_theme.get_color(color_name, default)
        return default or QtCore.Qt.gray
        
    def get_font(self, font_name, default_size=10):
        """Get font from current theme"""
        if self._current_theme:
            return self._current_theme.get_font(font_name, default_size)
        return QtGui.QFont('Arial', default_size)
        
    def get_size(self, size_name, default=10):
        """Get size from current theme"""
        if self._current_theme:
            return self._current_theme.get_size(size_name, default)
        return default
        
    def create_stylesheet(self, widget_type):
        """Create stylesheet for widget type"""
        cache_key = f"{self._current_theme.name}_{widget_type}"
        if cache_key in self._style_cache:
            return self._style_cache[cache_key]
            
        stylesheet = ""
        
        if widget_type == 'QPushButton':
            stylesheet = f"""
                QPushButton {{
                    background-color: {self.get_color('button_normal').name()};
                    color: {self.get_color('text_normal').name()};
                    border: 1px solid {self.get_color('border_normal').name()};
                    border-radius: {self.get_size('border_radius')}px;
                    padding: 4px 8px;
                    min-height: {self.get_size('button_height') - 8}px;
                }}
                QPushButton:hover {{
                    background-color: {self.get_color('button_hover').name()};
                }}
                QPushButton:pressed {{
                    background-color: {self.get_color('button_pressed').name()};
                }}
                QPushButton:checked {{
                    background-color: {self.get_color('button_selected').name()};
                    border-color: {self.get_color('border_selected').name()};
                }}
                QPushButton:disabled {{
                    color: {self.get_color('text_disabled').name()};
                    background-color: {self.get_color('button_normal').name()};
                    opacity: 0.5;
                }}
            """
            
        elif widget_type == 'QTabBar':
            stylesheet = f"""
                QTabBar::tab {{
                    background-color: {self.get_color('button_normal').name()};
                    color: {self.get_color('text_normal').name()};
                    border: 1px solid {self.get_color('border_normal').name()};
                    border-bottom: none;
                    padding: 4px 12px;
                    margin-right: 2px;
                }}
                QTabBar::tab:selected {{
                    background-color: {self.get_color('button_selected').name()};
                    border-color: {self.get_color('border_selected').name()};
                }}
                QTabBar::tab:hover {{
                    background-color: {self.get_color('button_hover').name()};
                }}
            """
            
        elif widget_type == 'QGroupBox':
            stylesheet = f"""
                QGroupBox {{
                    font-weight: bold;
                    border: 1px solid {self.get_color('border_normal').name()};
                    border-radius: {self.get_size('border_radius')}px;
                    margin: 8px 0px;
                    padding-top: 8px;
                    color: {self.get_color('text_normal').name()};
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 8px;
                    padding: 0 4px 0 4px;
                }}
            """
            
        elif widget_type == 'QLineEdit':
            stylesheet = f"""
                QLineEdit {{
                    background-color: {self.get_color('canvas_background').name()};
                    color: {self.get_color('text_normal').name()};
                    border: 1px solid {self.get_color('border_normal').name()};
                    border-radius: {self.get_size('border_radius')}px;
                    padding: 4px;
                    selection-background-color: {self.get_color('button_selected').name()};
                }}
                QLineEdit:focus {{
                    border-color: {self.get_color('border_selected').name()};
                }}
            """
            
        elif widget_type == 'QTextEdit':
            stylesheet = f"""
                QTextEdit {{
                    background-color: {self.get_color('canvas_background').name()};
                    color: {self.get_color('text_normal').name()};
                    border: 1px solid {self.get_color('border_normal').name()};
                    border-radius: {self.get_size('border_radius')}px;
                    selection-background-color: {self.get_color('button_selected').name()};
                }}
                QTextEdit:focus {{
                    border-color: {self.get_color('border_selected').name()};
                }}
            """
            
        elif widget_type == 'QComboBox':
            stylesheet = f"""
                QComboBox {{
                    background-color: {self.get_color('button_normal').name()};
                    color: {self.get_color('text_normal').name()};
                    border: 1px solid {self.get_color('border_normal').name()};
                    border-radius: {self.get_size('border_radius')}px;
                    padding: 4px;
                    min-height: {self.get_size('button_height') - 8}px;
                }}
                QComboBox:hover {{
                    background-color: {self.get_color('button_hover').name()};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 20px;
                }}
                QComboBox::down-arrow {{
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 4px solid {self.get_color('text_normal').name()};
                }}
            """
            
        elif widget_type == 'QSlider':
            stylesheet = f"""
                QSlider::groove:horizontal {{
                    border: 1px solid {self.get_color('border_normal').name()};
                    height: 6px;
                    background: {self.get_color('canvas_background').name()};
                    border-radius: 3px;
                }}
                QSlider::handle:horizontal {{
                    background: {self.get_color('button_selected').name()};
                    border: 1px solid {self.get_color('border_selected').name()};
                    width: 16px;
                    height: 16px;
                    margin: -6px 0;
                    border-radius: 8px;
                }}
                QSlider::handle:horizontal:hover {{
                    background: {self.get_color('accent').name()};
                }}
            """
            
        elif widget_type == 'QSpinBox':
            stylesheet = f"""
                QSpinBox {{
                    background-color: {self.get_color('canvas_background').name()};
                    color: {self.get_color('text_normal').name()};
                    border: 1px solid {self.get_color('border_normal').name()};
                    border-radius: {self.get_size('border_radius')}px;
                    padding: 4px;
                    min-height: {self.get_size('button_height') - 8}px;
                }}
                QSpinBox:focus {{
                    border-color: {self.get_color('border_selected').name()};
                }}
                QSpinBox::up-button, QSpinBox::down-button {{
                    background-color: {self.get_color('button_normal').name()};
                    border: 1px solid {self.get_color('border_normal').name()};
                    width: 16px;
                }}
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                    background-color: {self.get_color('button_hover').name()};
                }}
            """
            
        elif widget_type == 'QCheckBox':
            stylesheet = f"""
                QCheckBox {{
                    color: {self.get_color('text_normal').name()};
                    spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 1px solid {self.get_color('border_normal').name()};
                    border-radius: 2px;
                    background-color: {self.get_color('canvas_background').name()};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {self.get_color('button_selected').name()};
                    border-color: {self.get_color('border_selected').name()};
                }}
                QCheckBox::indicator:hover {{
                    border-color: {self.get_color('border_selected').name()};
                }}
            """
            
        # Cache the stylesheet
        self._style_cache[cache_key] = stylesheet
        return stylesheet
        
    def apply_theme_to_widget(self, widget, widget_type=None):
        """Apply current theme to widget"""
        if widget_type is None:
            widget_type = widget.__class__.__name__
            
        stylesheet = self.create_stylesheet(widget_type)
        if stylesheet:
            widget.setStyleSheet(stylesheet)
            
        # Apply font
        font = self.get_font('default')
        widget.setFont(font)
        
    def apply_theme_to_application(self, app):
        """Apply current theme to entire application"""
        # Set application font
        app.setFont(self.get_font('default'))
        
        # Create global stylesheet
        global_stylesheet = f"""
            QMainWindow {{
                background-color: {self.get_color('background').name()};
                color: {self.get_color('text_normal').name()};
            }}
            QWidget {{
                background-color: {self.get_color('background').name()};
                color: {self.get_color('text_normal').name()};
            }}
            QMenuBar {{
                background-color: {self.get_color('background').name()};
                color: {self.get_color('text_normal').name()};
                border-bottom: 1px solid {self.get_color('border_normal').name()};
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 4px 8px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.get_color('button_hover').name()};
            }}
            QMenu {{
                background-color: {self.get_color('background').name()};
                color: {self.get_color('text_normal').name()};
                border: 1px solid {self.get_color('border_normal').name()};
            }}
            QMenu::item {{
                padding: 4px 16px;
            }}
            QMenu::item:selected {{
                background-color: {self.get_color('button_hover').name()};
            }}
            QStatusBar {{
                background-color: {self.get_color('background').name()};
                color: {self.get_color('text_normal').name()};
                border-top: 1px solid {self.get_color('border_normal').name()};
            }}
            QToolBar {{
                background-color: {self.get_color('background').name()};
                border: 1px solid {self.get_color('border_normal').name()};
                spacing: 2px;
            }}
            QDockWidget {{
                color: {self.get_color('text_normal').name()};
                titlebar-close-icon: none;
                titlebar-normal-icon: none;
            }}
            QDockWidget::title {{
                background-color: {self.get_color('button_normal').name()};
                padding: 4px;
                border-bottom: 1px solid {self.get_color('border_normal').name()};
            }}
        """
        
        app.setStyleSheet(global_stylesheet)
        
    def create_custom_style(self, name, base_style=None):
        """Create custom style based on existing style"""
        if base_style and base_style in self._custom_styles:
            self._custom_styles[name] = base_style.copy()
        else:
            self._custom_styles[name] = {}
            
    def set_custom_property(self, style_name, property_name, value):
        """Set custom style property"""
        if style_name not in self._custom_styles:
            self._custom_styles[style_name] = {}
        self._custom_styles[style_name][property_name] = value
        
    def get_custom_property(self, style_name, property_name, default=None):
        """Get custom style property"""
        style = self._custom_styles.get(style_name, {})
        return style.get(property_name, default)
        
    def save_theme(self, theme_name, file_path):
        """Save theme to file"""
        if theme_name not in self._themes:
            return False
            
        try:
            theme_data = self._themes[theme_name].to_dict()
            with open(file_path, 'w') as f:
                json.dump(theme_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving theme: {e}")
            return False
            
    def load_theme(self, file_path):
        """Load theme from file"""
        try:
            with open(file_path, 'r') as f:
                theme_data = json.load(f)
                
            theme = StyleTheme.from_dict(theme_data)
            self._themes[theme.name] = theme
            return theme.name
            
        except Exception as e:
            print(f"Error loading theme: {e}")
            return None
            
    def export_current_theme(self, file_path):
        """Export current theme"""
        if self._current_theme:
            return self.save_theme(self._current_theme.name, file_path)
        return False
        
    def create_color_scheme_from_image(self, image_path, theme_name):
        """Create color scheme from image colors"""
        try:
            from PIL import Image
            import colorsys
            
            # Open and resize image
            img = Image.open(image_path)
            img = img.resize((150, 150))
            
            # Get dominant colors
            colors = img.getcolors(maxcolors=256*256*256)
            if not colors:
                return False
                
            # Sort by frequency and get top colors
            colors.sort(key=lambda x: x[0], reverse=True)
            dominant_colors = [color[1] for color in colors[:10]]
            
            # Create theme with extracted colors
            theme = StyleTheme(theme_name)
            
            # Convert colors and assign to theme
            qt_colors = [QtGui.QColor(*color) for color in dominant_colors]
            
            # Assign colors based on brightness
            sorted_colors = sorted(qt_colors, key=lambda c: c.lightness())
            
            theme.colors = {
                'background': sorted_colors[1],
                'canvas_background': sorted_colors[0],
                'button_normal': sorted_colors[3],
                'button_hover': sorted_colors[4],
                'button_pressed': sorted_colors[2],
                'button_selected': sorted_colors[-2],
                'text_normal': sorted_colors[-1],
                'text_disabled': sorted_colors[5],
                'border_normal': sorted_colors[6],
                'border_selected': sorted_colors[-2],
                'accent': sorted_colors[-3]
            }
            
            # Use default fonts and sizes
            default_theme = self._themes['Default']
            theme.fonts = default_theme.fonts.copy()
            theme.sizes = default_theme.sizes.copy()
            
            self._themes[theme_name] = theme
            return True
            
        except Exception as e:
            print(f"Error creating color scheme from image: {e}")
            return False


class ItemStyleManager:
    """Manages styles for picker items"""
    
    def __init__(self, style_manager):
        self.style_manager = style_manager
        self._item_styles = {}
        
    def create_item_style(self, item_type, style_name='default'):
        """Create style for item type"""
        if item_type not in self._item_styles:
            self._item_styles[item_type] = {}
            
        style = {
            'bg_color': self.style_manager.get_color('button_normal'),
            'bg_hover_color': self.style_manager.get_color('button_hover'),
            'bg_click_color': self.style_manager.get_color('button_pressed'),
            'border_color': self.style_manager.get_color('border_normal'),
            'border_hover_color': self.style_manager.get_color('border_selected'),
            'border_click_color': self.style_manager.get_color('border_selected'),
            'text_color': self.style_manager.get_color('text_normal'),
            'text_hover_color': self.style_manager.get_color('text_normal'),
            'text_click_color': self.style_manager.get_color('text_normal'),
            'border_width': 1,
            'font_family': 'Arial',
            'font_size': 10,
            'font_bold': False,
            'font_italic': False
        }
        
        self._item_styles[item_type][style_name] = style
        return style
        
    def get_item_style(self, item_type, style_name='default'):
        """Get style for item type"""
        if item_type in self._item_styles and style_name in self._item_styles[item_type]:
            return self._item_styles[item_type][style_name]
        return self.create_item_style(item_type, style_name)
        
    def apply_style_to_item(self, item, item_type=None, style_name='default'):
        """Apply style to item"""
        if item_type is None:
            item_type = item.__class__.__name__
            
        style = self.get_item_style(item_type, style_name)
        
        for prop, value in style.items():
            if hasattr(item, prop):
                setattr(item, prop, value)
            elif hasattr(item, f'_{prop}'):
                setattr(item, f'_{prop}', value)
                
        if hasattr(item, 'update'):
            item.update()


# Global style manager instance
_style_manager = None

def get_style_manager():
    """Get global style manager instance"""
    global _style_manager
    if _style_manager is None:
        _style_manager = StyleManager()
    return _style_manager

def apply_theme_to_widget(widget, widget_type=None):
    """Convenience function to apply theme to widget"""
    style_manager = get_style_manager()
    style_manager.apply_theme_to_widget(widget, widget_type)
