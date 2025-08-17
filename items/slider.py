# File: items/slider.py
"""
Slider Item for Ultimate Animation Picker
Interactive slider control for attribute manipulation
"""

import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore, QtGui
from .base_item import BasePickerItem

class SliderItem(BasePickerItem):
    """Interactive slider picker item"""
    
    # Signals
    value_changed = QtCore.Signal(float)
    
    def __init__(self, parent=None):
        super(SliderItem, self).__init__(parent)
        
        # Slider properties
        self._min_value = 0.0
        self._max_value = 1.0
        self._current_value = 0.0
        self._step_size = 0.01
        self._orientation = QtCore.Qt.Horizontal
        self._handle_size = 12
        self._track_height = 6
        self._precision = 2
        
        # Visual properties
        self._track_color = QtCore.Qt.gray
        self._fill_color = QtCore.Qt.blue
        self._handle_color = QtCore.Qt.white
        self._handle_border_color = QtCore.Qt.darkGray
        
        # Interaction state
        self._is_dragging = False
        self._drag_start_pos = QtCore.QPointF()
        self._drag_start_value = 0.0
        
        # Size
        self._width = 120
        self._height = 20
        
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Connected attributes
        self._connected_objects = []
        self._connected_attribute = ""
        
    def boundingRect(self):
        """Return bounding rectangle"""
        return QtCore.QRectF(0, 0, self._width, self._height)
        
    def paint(self, painter, option, widget):
        """Paint the slider"""
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.boundingRect()
        
        if self._orientation == QtCore.Qt.Horizontal:
            self.paint_horizontal_slider(painter, rect)
        else:
            self.paint_vertical_slider(painter, rect)
            
        # Draw text if present
        if self.text:
            self.draw_text(painter)
            
    def paint_horizontal_slider(self, painter, rect):
        """Paint horizontal slider"""
        # Calculate track rectangle
        track_y = (rect.height() - self._track_height) / 2
        track_rect = QtCore.QRectF(
            self._handle_size / 2,
            track_y,
            rect.width() - self._handle_size,
            self._track_height
        )
        
        # Draw track background
        painter.setBrush(QtGui.QBrush(self._track_color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(track_rect, self._track_height / 2, self._track_height / 2)
        
        # Draw filled portion
        if self._current_value > self._min_value:
            fill_width = track_rect.width() * self.get_normalized_value()
            fill_rect = QtCore.QRectF(track_rect.x(), track_rect.y(), fill_width, track_rect.height())
            painter.setBrush(QtGui.QBrush(self._fill_color))
            painter.drawRoundedRect(fill_rect, self._track_height / 2, self._track_height / 2)
            
        # Draw handle
        handle_x = track_rect.x() + track_rect.width() * self.get_normalized_value() - self._handle_size / 2
        handle_y = (rect.height() - self._handle_size) / 2
        handle_rect = QtCore.QRectF(handle_x, handle_y, self._handle_size, self._handle_size)
        
        painter.setBrush(QtGui.QBrush(self._handle_color))
        painter.setPen(QtGui.QPen(self._handle_border_color, 1))
        painter.drawEllipse(handle_rect)
        
        # Draw value text
        value_text = f"{self._current_value:.{self._precision}f}"
        painter.setPen(QtCore.Qt.black)
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        
        text_rect = QtCore.QRectF(rect.x(), rect.y() - 15, rect.width(), 12)
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, value_text)
        
    def paint_vertical_slider(self, painter, rect):
        """Paint vertical slider"""
        # Calculate track rectangle
        track_x = (rect.width() - self._track_height) / 2
        track_rect = QtCore.QRectF(
            track_x,
            self._handle_size / 2,
            self._track_height,
            rect.height() - self._handle_size
        )
        
        # Draw track background
        painter.setBrush(QtGui.QBrush(self._track_color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(track_rect, self._track_height / 2, self._track_height / 2)
        
        # Draw filled portion (from bottom)
        if self._current_value > self._min_value:
            fill_height = track_rect.height() * self.get_normalized_value()
            fill_rect = QtCore.QRectF(
                track_rect.x(),
                track_rect.y() + track_rect.height() - fill_height,
                track_rect.width(),
                fill_height
            )
            painter.setBrush(QtGui.QBrush(self._fill_color))
            painter.drawRoundedRect(fill_rect, self._track_height / 2, self._track_height / 2)
            
        # Draw handle
        handle_x = (rect.width() - self._handle_size) / 2
        handle_y = track_rect.y() + track_rect.height() * (1.0 - self.get_normalized_value()) - self._handle_size / 2
        handle_rect = QtCore.QRectF(handle_x, handle_y, self._handle_size, self._handle_size)
        
        painter.setBrush(QtGui.QBrush(self._handle_color))
        painter.setPen(QtGui.QPen(self._handle_border_color, 1))
        painter.drawEllipse(handle_rect)
        
        # Draw value text
        value_text = f"{self._current_value:.{self._precision}f}"
        painter.setPen(QtCore.Qt.black)
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        
        text_rect = QtCore.QRectF(rect.x() + rect.width() + 5, rect.y(), 50, rect.height())
        painter.drawText(text_rect, QtCore.Qt.AlignVCenter, value_text)
        
    def get_normalized_value(self):
        """Get normalized value (0.0 to 1.0)"""
        if self._max_value == self._min_value:
            return 0.0
        return (self._current_value - self._min_value) / (self._max_value - self._min_value)
        
    def set_value(self, value):
        """Set slider value"""
        old_value = self._current_value
        self._current_value = max(self._min_value, min(self._max_value, value))
        
        if abs(self._current_value - old_value) > 1e-6:
            self.update()
            self.value_changed.emit(self._current_value)
            self.apply_value_to_maya()
            
    def get_value(self):
        """Get slider value"""
        return self._current_value
        
    def set_range(self, min_value, max_value):
        """Set slider range"""
        self._min_value = min_value
        self._max_value = max_value
        # Clamp current value to new range
        self.set_value(self._current_value)
        
    def get_range(self):
        """Get slider range"""
        return self._min_value, self._max_value
        
    def set_step_size(self, step):
        """Set step size for discrete values"""
        self._step_size = step
        
    def set_orientation(self, orientation):
        """Set slider orientation"""
        self._orientation = orientation
        if orientation == QtCore.Qt.Vertical:
            self._width, self._height = self._height, self._width
        self.update()
        
    def set_precision(self, precision):
        """Set decimal precision for display"""
        self._precision = max(0, min(10, precision))
        self.update()
        
    def connect_to_maya_attribute(self, objects, attribute):
        """Connect slider to Maya attribute"""
        self._connected_objects = objects if isinstance(objects, list) else [objects]
        self._connected_attribute = attribute
        
        # Get current value from Maya
        if self._connected_objects and self._connected_attribute:
            try:
                current_value = cmds.getAttr(f"{self._connected_objects[0]}.{self._connected_attribute}")
                self.set_value(current_value)
            except:
                pass
                
    def apply_value_to_maya(self):
        """Apply current value to connected Maya attributes"""
        if not self._connected_objects or not self._connected_attribute:
            return
            
        for obj in self._connected_objects:
            try:
                cmds.setAttr(f"{obj}.{self._connected_attribute}", self._current_value)
            except Exception as e:
                print(f"Failed to set {obj}.{self._connected_attribute}: {e}")
                
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == QtCore.Qt.LeftButton:
            self._is_dragging = True
            self._drag_start_pos = event.pos()
            self._drag_start_value = self._current_value
            
            # Calculate value from click position
            new_value = self.value_from_position(event.pos())
            self.set_value(new_value)
            
            event.accept()
        else:
            super(SliderItem, self).mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if self._is_dragging:
            new_value = self.value_from_position(event.pos())
            self.set_value(new_value)
            event.accept()
        else:
            super(SliderItem, self).mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == QtCore.Qt.LeftButton and self._is_dragging:
            self._is_dragging = False
            event.accept()
        else:
            super(SliderItem, self).mouseReleaseEvent(event)
            
    def wheelEvent(self, event):
        """Handle mouse wheel"""
        delta = event.angleDelta().y()
        step_value = self._step_size if delta > 0 else -self._step_size
        new_value = self._current_value + step_value
        self.set_value(new_value)
        event.accept()
        
    def value_from_position(self, pos):
        """Calculate value from mouse position"""
        rect = self.boundingRect()
        
        if self._orientation == QtCore.Qt.Horizontal:
            # Horizontal slider
            track_x = self._handle_size / 2
            track_width = rect.width() - self._handle_size
            
            if track_width <= 0:
                return self._min_value
                
            normalized = (pos.x() - track_x) / track_width
        else:
            # Vertical slider
            track_y = self._handle_size / 2
            track_height = rect.height() - self._handle_size
            
            if track_height <= 0:
                return self._min_value
                
            # Invert for vertical (top = max, bottom = min)
            normalized = 1.0 - (pos.y() - track_y) / track_height
            
        # Clamp to 0-1 range
        normalized = max(0.0, min(1.0, normalized))
        
        # Convert to value range
        value = self._min_value + normalized * (self._max_value - self._min_value)
        
        # Apply step size if specified
        if self._step_size > 0:
            steps = round((value - self._min_value) / self._step_size)
            value = self._min_value + steps * self._step_size
            
        return value
        
    def keyPressEvent(self, event):
        """Handle keyboard input"""
        step_value = self._step_size
        
        if event.key() == QtCore.Qt.Key_Left or event.key() == QtCore.Qt.Key_Down:
            self.set_value(self._current_value - step_value)
            event.accept()
        elif event.key() == QtCore.Qt.Key_Right or event.key() == QtCore.Qt.Key_Up:
            self.set_value(self._current_value + step_value)
            event.accept()
        elif event.key() == QtCore.Qt.Key_Home:
            self.set_value(self._min_value)
            event.accept()
        elif event.key() == QtCore.Qt.Key_End:
            self.set_value(self._max_value)
            event.accept()
        else:
            super(SliderItem, self).keyPressEvent(event)
            
    def reset_to_default(self):
        """Reset to default value (middle of range)"""
        default_value = (self._min_value + self._max_value) / 2.0
        self.set_value(default_value)
        
    def set_colors(self, track_color=None, fill_color=None, handle_color=None, handle_border_color=None):
        """Set slider colors"""
        if track_color is not None:
            self._track_color = track_color
        if fill_color is not None:
            self._fill_color = fill_color
        if handle_color is not None:
            self._handle_color = handle_color
        if handle_border_color is not None:
            self._handle_border_color = handle_border_color
        self.update()
        
    def to_dict(self):
        """Serialize to dictionary"""
        data = super(SliderItem, self).to_dict()
        data.update({
            'min_value': self._min_value,
            'max_value': self._max_value,
            'current_value': self._current_value,
            'step_size': self._step_size,
            'orientation': self._orientation,
            'precision': self._precision,
            'width': self._width,
            'height': self._height,
            'connected_objects': self._connected_objects,
            'connected_attribute': self._connected_attribute,
            'track_color': self._track_color.name() if hasattr(self._track_color, 'name') else str(self._track_color),
            'fill_color': self._fill_color.name() if hasattr(self._fill_color, 'name') else str(self._fill_color),
            'handle_color': self._handle_color.name() if hasattr(self._handle_color, 'name') else str(self._handle_color),
            'handle_border_color': self._handle_border_color.name() if hasattr(self._handle_border_color, 'name') else str(self._handle_border_color)
        })
        return data
        
    def from_dict(self, data):
        """Deserialize from dictionary"""
        super(SliderItem, self).from_dict(data)
        
        self._min_value = data.get('min_value', 0.0)
        self._max_value = data.get('max_value', 1.0)
        self._current_value = data.get('current_value', 0.0)
        self._step_size = data.get('step_size', 0.01)
        self._orientation = data.get('orientation', QtCore.Qt.Horizontal)
        self._precision = data.get('precision', 2)
        self._width = data.get('width', 120)
        self._height = data.get('height', 20)
        self._connected_objects = data.get('connected_objects', [])
        self._connected_attribute = data.get('connected_attribute', "")
        
        # Colors
        if 'track_color' in data:
            self._track_color = QtGui.QColor(data['track_color'])
        if 'fill_color' in data:
            self._fill_color = QtGui.QColor(data['fill_color'])
        if 'handle_color' in data:
            self._handle_color = QtGui.QColor(data['handle_color'])
        if 'handle_border_color' in data:
            self._handle_border_color = QtGui.QColor(data['handle_border_color'])
