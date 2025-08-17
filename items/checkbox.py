# File: items/checkbox.py
"""
Checkbox Item for Ultimate Animation Picker
Interactive checkbox control for boolean attribute manipulation
"""

import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore, QtGui
from .base_item import BasePickerItem

class CheckboxItem(BasePickerItem):
    """Interactive checkbox picker item"""
    
    # Signals
    toggled = QtCore.Signal(bool)
    
    def __init__(self, parent=None):
        super(CheckboxItem, self).__init__(parent)
        
        # Checkbox properties
        self._checked = False
        self._tristate = False  # Allow indeterminate state
        self._check_state = QtCore.Qt.Unchecked
        
        # Visual properties
        self._box_size = 16
        self._check_mark_color = QtCore.Qt.darkGreen
        self._box_color = QtCore.Qt.white
        self._box_border_color = QtCore.Qt.gray
        self._hover_color = QtCore.Qt.lightGray
        
        # Size
        self._width = 80
        self._height = 20
        
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Connected attributes
        self._connected_objects = []
        self._connected_attribute = ""
        
        # State
        self._is_hovered = False
        
    def boundingRect(self):
        """Return bounding rectangle"""
        return QtCore.QRectF(0, 0, self._width, self._height)
        
    def paint(self, painter, option, widget):
        """Paint the checkbox"""
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.boundingRect()
        
        # Calculate checkbox box position
        box_y = (rect.height() - self._box_size) / 2
        box_rect = QtCore.QRectF(2, box_y, self._box_size, self._box_size)
        
        # Draw checkbox box
        if self._is_hovered:
            painter.setBrush(QtGui.QBrush(self._hover_color))
        else:
            painter.setBrush(QtGui.QBrush(self._box_color))
            
        painter.setPen(QtGui.QPen(self._box_border_color, 1))
        painter.drawRect(box_rect)
        
        # Draw check mark or indeterminate state
        if self._check_state == QtCore.Qt.Checked:
            self.draw_check_mark(painter, box_rect)
        elif self._check_state == QtCore.Qt.PartiallyChecked:
            self.draw_indeterminate_mark(painter, box_rect)
            
        # Draw label text
        if self.text:
            text_rect = QtCore.QRectF(
                box_rect.right() + 5,
                rect.y(),
                rect.width() - box_rect.width() - 7,
                rect.height()
            )
            
            painter.setPen(self.text_color)
            font = QtGui.QFont(self.font_family, self.font_size)
            font.setBold(self.font_bold)
            font.setItalic(self.font_italic)
            painter.setFont(font)
            
            painter.drawText(text_rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft, self.text)
            
    def draw_check_mark(self, painter, box_rect):
        """Draw check mark inside box"""
        painter.setPen(QtGui.QPen(self._check_mark_color, 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        
        # Create check mark path
        margin = 3
        check_rect = box_rect.adjusted(margin, margin, -margin, -margin)
        
        # Check mark points
        p1 = QtCore.QPointF(check_rect.left(), check_rect.center().y())
        p2 = QtCore.QPointF(check_rect.center().x() - 1, check_rect.bottom() - 2)
        p3 = QtCore.QPointF(check_rect.right(), check_rect.top() + 1)
        
        # Draw check mark
        painter.drawLine(p1, p2)
        painter.drawLine(p2, p3)
        
    def draw_indeterminate_mark(self, painter, box_rect):
        """Draw indeterminate mark (dash) inside box"""
        painter.setPen(QtGui.QPen(self._check_mark_color, 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        
        margin = 4
        y_center = box_rect.center().y()
        x_start = box_rect.left() + margin
        x_end = box_rect.right() - margin
        
        painter.drawLine(QtCore.QPointF(x_start, y_center), QtCore.QPointF(x_end, y_center))
        
    def set_checked(self, checked):
        """Set checkbox checked state"""
        old_state = self._check_state
        
        if checked:
            self._check_state = QtCore.Qt.Checked
        else:
            self._check_state = QtCore.Qt.Unchecked
            
        self._checked = checked
        
        if self._check_state != old_state:
            self.update()
            self.toggled.emit(checked)
            self.apply_value_to_maya()
            
    def is_checked(self):
        """Get checkbox checked state"""
        return self._check_state == QtCore.Qt.Checked
        
    def set_check_state(self, state):
        """Set checkbox state (supports tristate)"""
        old_state = self._check_state
        self._check_state = state
        self._checked = (state == QtCore.Qt.Checked)
        
        if self._check_state != old_state:
            self.update()
            self.toggled.emit(self._checked)
            self.apply_value_to_maya()
            
    def get_check_state(self):
        """Get checkbox state"""
        return self._check_state
        
    def set_tristate(self, tristate):
        """Enable/disable tristate mode"""
        self._tristate = tristate
        
    def is_tristate(self):
        """Check if tristate mode is enabled"""
        return self._tristate
        
    def toggle(self):
        """Toggle checkbox state"""
        if self._tristate:
            if self._check_state == QtCore.Qt.Unchecked:
                self.set_check_state(QtCore.Qt.PartiallyChecked)
            elif self._check_state == QtCore.Qt.PartiallyChecked:
                self.set_check_state(QtCore.Qt.Checked)
            else:
                self.set_check_state(QtCore.Qt.Unchecked)
        else:
            self.set_checked(not self._checked)
            
    def connect_to_maya_attribute(self, objects, attribute):
        """Connect checkbox to Maya boolean attribute"""
        self._connected_objects = objects if isinstance(objects, list) else [objects]
        self._connected_attribute = attribute
        
        # Get current value from Maya
        if self._connected_objects and self._connected_attribute:
            try:
                current_value = cmds.getAttr(f"{self._connected_objects[0]}.{self._connected_attribute}")
                self.set_checked(bool(current_value))
            except:
                pass
                
    def apply_value_to_maya(self):
        """Apply current value to connected Maya attributes"""
        if not self._connected_objects or not self._connected_attribute:
            return
            
        value = 1 if self._checked else 0
        
        for obj in self._connected_objects:
            try:
                cmds.setAttr(f"{obj}.{self._connected_attribute}", value)
            except Exception as e:
                print(f"Failed to set {obj}.{self._connected_attribute}: {e}")
                
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == QtCore.Qt.LeftButton:
            self.toggle()
            event.accept()
        else:
            super(CheckboxItem, self).mousePressEvent(event)
            
    def keyPressEvent(self, event):
        """Handle keyboard input"""
        if event.key() == QtCore.Qt.Key_Space:
            self.toggle()
            event.accept()
        else:
            super(CheckboxItem, self).keyPressEvent(event)
            
    def hoverEnterEvent(self, event):
        """Handle hover enter"""
        self._is_hovered = True
        self.update()
        super(CheckboxItem, self).hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        """Handle hover leave"""
        self._is_hovered = False
        self.update()
        super(CheckboxItem, self).hoverLeaveEvent(event)
        
    def set_colors(self, check_color=None, box_color=None, border_color=None, hover_color=None):
        """Set checkbox colors"""
        if check_color is not None:
            self._check_mark_color = check_color
        if box_color is not None:
            self._box_color = box_color
        if border_color is not None:
            self._box_border_color = border_color
        if hover_color is not None:
            self._hover_color = hover_color
        self.update()
        
    def set_box_size(self, size):
        """Set checkbox box size"""
        self._box_size = max(8, min(32, size))
        self.update()
        
    def resize(self, width, height):
        """Resize checkbox item"""
        self._width = width
        self._height = height
        self.update()
        
    def create_checkbox_group(checkboxes, exclusive=False):
        """Create a group of checkboxes (static method)"""
        if exclusive:
            # Radio button behavior - only one can be checked
            def on_checkbox_toggled(checked, sender):
                if checked:
                    for checkbox in checkboxes:
                        if checkbox != sender and checkbox.is_checked():
                            checkbox.set_checked(False)
                            
            for checkbox in checkboxes:
                # Connect to group behavior
                checkbox.toggled.connect(lambda checked, cb=checkbox: on_checkbox_toggled(checked, cb))
                
        return checkboxes
        
    def to_dict(self):
        """Serialize to dictionary"""
        data = super(CheckboxItem, self).to_dict()
        data.update({
            'checked': self._checked,
            'tristate': self._tristate,
            'check_state': int(self._check_state),
            'box_size': self._box_size,
            'width': self._width,
            'height': self._height,
            'connected_objects': self._connected_objects,
            'connected_attribute': self._connected_attribute,
            'check_mark_color': self._check_mark_color.name() if hasattr(self._check_mark_color, 'name') else str(self._check_mark_color),
            'box_color': self._box_color.name() if hasattr(self._box_color, 'name') else str(self._box_color),
            'box_border_color': self._box_border_color.name() if hasattr(self._box_border_color, 'name') else str(self._box_border_color),
            'hover_color': self._hover_color.name() if hasattr(self._hover_color, 'name') else str(self._hover_color)
        })
        return data
        
    def from_dict(self, data):
        """Deserialize from dictionary"""
        super(CheckboxItem, self).from_dict(data)
        
        self._checked = data.get('checked', False)
        self._tristate = data.get('tristate', False)
        self._check_state = QtCore.Qt.CheckState(data.get('check_state', QtCore.Qt.Unchecked))
        self._box_size = data.get('box_size', 16)
        self._width = data.get('width', 80)
        self._height = data.get('height', 20)
        self._connected_objects = data.get('connected_objects', [])
        self._connected_attribute = data.get('connected_attribute', "")
        
        # Colors
        if 'check_mark_color' in data:
            self._check_mark_color = QtGui.QColor(data['check_mark_color'])
        if 'box_color' in data:
            self._box_color = QtGui.QColor(data['box_color'])
        if 'box_border_color' in data:
            self._box_border_color = QtGui.QColor(data['box_border_color'])
        if 'hover_color' in data:
            self._hover_color = QtGui.QColor(data['hover_color'])
