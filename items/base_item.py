# File: items/base_item.py
"""
Base Picker Item for Ultimate Animation Picker
Provides common functionality for all picker items
"""

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal
import json

class BasePickerItem(QtWidgets.QGraphicsObject):
    """Base class for all picker items"""
    
    # Signals
    clicked = Signal()
    double_clicked = Signal()
    hover_entered = Signal()
    hover_exited = Signal()
    selection_changed = Signal(bool)
    properties_changed = Signal()
    
    def __init__(self, parent=None):
        super(BasePickerItem, self).__init__(parent)
        
        # Basic properties
        self._text = "Button"
        self._command = ""
        self._mel_command = ""
        self._edit_mode = False
        self._coordinate_system = 'Local'  # Local or World
        
        # Visual properties
        self._bg_color = QtGui.QColor(90, 90, 90)
        self._hover_color = QtGui.QColor(106, 106, 106)
        self._click_color = QtGui.QColor(74, 74, 74)
        self._selected_color = QtGui.QColor(74, 144, 226)
        
        self._border_color = QtGui.QColor(102, 102, 102)
        self._border_hover_color = QtGui.QColor(120, 120, 120)
        self._border_click_color = QtGui.QColor(80, 80, 80)
        self._border_selected_color = QtGui.QColor(74, 144, 226)
        self._border_width = 1
        
        self._text_color = QtGui.QColor(255, 255, 255)
        self._text_hover_color = QtGui.QColor(255, 255, 255)
        self._text_click_color = QtGui.QColor(255, 255, 255)
        self._font = QtGui.QFont("Arial", 9)
        
        # State
        self._is_hovered = False
        self._is_pressed = False
        self._is_selected = False
        
        # Setup
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        
    @property
    def text(self):
        """Get item text"""
        return self._text
        
    @text.setter
    def text(self, value):
        """Set item text"""
        self._text = str(value)
        self.update()
        self.properties_changed.emit()
        
    @property
    def command(self):
        """Get Python command"""
        return self._command
        
    @command.setter
    def command(self, value):
        """Set Python command"""
        self._command = str(value)
        self.properties_changed.emit()
        
    @property
    def mel_command(self):
        """Get MEL command"""
        return self._mel_command
        
    @mel_command.setter
    def mel_command(self, value):
        """Set MEL command"""
        self._mel_command = str(value)
        self.properties_changed.emit()
        
    def set_edit_mode(self, edit_mode):
        """Set edit mode state"""
        self._edit_mode = edit_mode
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, edit_mode)
        self.update()
        
    def is_edit_mode(self):
        """Check if in edit mode"""
        return self._edit_mode
        
    def execute_command(self):
        """Execute item command"""
        if self._command and not self._edit_mode:
            try:
                exec(self._command)
            except Exception as e:
                print(f"Error executing Python command: {e}")
                
        if self._mel_command and not self._edit_mode:
            try:
                import maya.mel as mel
                mel.eval(self._mel_command)
            except Exception as e:
                print(f"Error executing MEL command: {e}")
                
    def get_current_colors(self):
        """Get current colors based on state"""
        if self._is_selected:
            bg_color = self._selected_color
            border_color = self._border_selected_color
            text_color = self._text_color
        elif self._is_pressed:
            bg_color = self._click_color
            border_color = self._border_click_color
            text_color = self._text_click_color
        elif self._is_hovered:
            bg_color = self._hover_color
            border_color = self._border_hover_color
            text_color = self._text_hover_color
        else:
            bg_color = self._bg_color
            border_color = self._border_color
            text_color = self._text_color
            
        return bg_color, border_color, text_color
        
    def to_dict(self):
        """Serialize item to dictionary"""
        return {
            'type': self.__class__.__name__,
            'position': [self.pos().x(), self.pos().y()],
            'text': self._text,
            'command': self._command,
            'mel_command': self._mel_command,
            'coordinate_system': self._coordinate_system,
            'bg_color': self._bg_color.name(),
            'hover_color': self._hover_color.name(),
            'click_color': self._click_color.name(),
            'selected_color': self._selected_color.name(),
            'border_color': self._border_color.name(),
            'border_hover_color': self._border_hover_color.name(),
            'border_click_color': self._border_click_color.name(),
            'border_selected_color': self._border_selected_color.name(),
            'border_width': self._border_width,
            'text_color': self._text_color.name(),
            'text_hover_color': self._text_hover_color.name(),
            'text_click_color': self._text_click_color.name(),
            'font': {
                'family': self._font.family(),
                'size': self._font.pointSize(),
                'bold': self._font.bold(),
                'italic': self._font.italic()
            }
        }
        
    def from_dict(self, data):
        """Deserialize item from dictionary"""
        self.setPos(data.get('position', [0, 0])[0], data.get('position', [0, 0])[1])
        self._text = data.get('text', 'Button')
        self._command = data.get('command', '')
        self._mel_command = data.get('mel_command', '')
        self._coordinate_system = data.get('coordinate_system', 'Local')
        
        # Colors
        self._bg_color = QtGui.QColor(data.get('bg_color', '#5A5A5A'))
        self._hover_color = QtGui.QColor(data.get('hover_color', '#6A6A6A'))
        self._click_color = QtGui.QColor(data.get('click_color', '#4A4A4A'))
        self._selected_color = QtGui.QColor(data.get('selected_color', '#4A90E2'))
        
        self._border_color = QtGui.QColor(data.get('border_color', '#666666'))
        self._border_hover_color = QtGui.QColor(data.get('border_hover_color', '#787878'))
        self._border_click_color = QtGui.QColor(data.get('border_click_color', '#505050'))
        self._border_selected_color = QtGui.QColor(data.get('border_selected_color', '#4A90E2'))
        self._border_width = data.get('border_width', 1)
        
        self._text_color = QtGui.QColor(data.get('text_color', '#FFFFFF'))
        self._text_hover_color = QtGui.QColor(data.get('text_hover_color', '#FFFFFF'))
        self._text_click_color = QtGui.QColor(data.get('text_click_color', '#FFFFFF'))
        
        # Font
        font_data = data.get('font', {})
        self._font = QtGui.QFont(
            font_data.get('family', 'Arial'),
            font_data.get('size', 9)
        )
        self._font.setBold(font_data.get('bold', False))
        self._font.setItalic(font_data.get('italic', False))
        
        self.update()
        
    # Event handlers
    def hoverEnterEvent(self, event):
        """Handle hover enter"""
        self._is_hovered = True
        self.update()
        self.hover_entered.emit()
        
    def hoverLeaveEvent(self, event):
        """Handle hover leave"""
        self._is_hovered = False
        self.update()
        self.hover_exited.emit()
        
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == QtCore.Qt.LeftButton:
            self._is_pressed = True
            self.update()
        super(BasePickerItem, self).mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == QtCore.Qt.LeftButton:
            self._is_pressed = False
            self.update()
            
            # Execute command if not in edit mode
            if not self._edit_mode:
                self.execute_command()
                self.clicked.emit()
                
        super(BasePickerItem, self).mouseReleaseEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        """Handle double click"""
        if event.button() == QtCore.Qt.LeftButton:
            self.double_clicked.emit()
        super(BasePickerItem, self).mouseDoubleClickEvent(event)
        
    def itemChange(self, change, value):
        """Handle item changes"""
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            self._is_selected = value
            self.update()
            self.selection_changed.emit(value)
        return super(BasePickerItem, self).itemChange(change, value)