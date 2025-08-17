# File: items/button.py
"""
Button Picker Items for Ultimate Animation Picker
Various button types and base button functionality
"""

from PySide2 import QtWidgets, QtCore, QtGui
from .base_item import BasePickerItem

class ButtonItem(BasePickerItem):
    """Generic button picker item"""
    
    def __init__(self, parent=None):
        super(ButtonItem, self).__init__(parent)
        
        # Button-specific properties
        self._width = 80
        self._height = 30
        self._radius = 4
        
    def boundingRect(self):
        """Return bounding rectangle"""
        return QtCore.QRectF(0, 0, self._width, self._height)
        
    def shape(self):
        """Return shape for collision detection"""
        path = QtGui.QPainterPath()
        path.addRoundedRect(self.boundingRect(), self._radius, self._radius)
        return path
        
    def paint(self, painter, option, widget):
        """Paint the button item"""
        bg_color, border_color, text_color = self.get_current_colors()
        
        # Setup painter
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw background
        painter.setBrush(QtGui.QBrush(bg_color))
        painter.setPen(QtGui.QPen(border_color, self._border_width))
        painter.drawRoundedRect(self.boundingRect(), self._radius, self._radius)
        
        # Draw text
        painter.setPen(QtGui.QPen(text_color))
        painter.setFont(self._font)
        
        text_rect = self.boundingRect()
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, self._text)
        
    def set_size(self, width, height):
        """Set button size"""
        self.prepareGeometryChange()
        self._width = width
        self._height = height
        self.update()
        
    def get_size(self):
        """Get button size"""
        return self._width, self._height
        
    def set_radius(self, radius):
        """Set corner radius"""
        self._radius = radius
        self.update()
        
    def get_radius(self):
        """Get corner radius"""
        return self._radius
        
    def to_dict(self):
        """Serialize to dictionary"""
        data = super(ButtonItem, self).to_dict()
        data.update({
            'width': self._width,
            'height': self._height,
            'radius': self._radius
        })
        return data
        
    def from_dict(self, data):
        """Deserialize from dictionary"""
        super(ButtonItem, self).from_dict(data)
        self._width = data.get('width', 80)
        self._height = data.get('height', 30)
        self._radius = data.get('radius', 4)
        self.update()


class BasePickerButton(ButtonItem):
    """Base picker button (alias for backward compatibility)"""
    pass


class RoundRectangleItem(ButtonItem):
    """Round rectangle button item"""
    
    def __init__(self, parent=None):
        super(RoundRectangleItem, self).__init__(parent)
        self._radius = 15
        

class CircleItem(BasePickerItem):
    """Circle picker item"""
    
    def __init__(self, parent=None):
        super(CircleItem, self).__init__(parent)
        
        # Circle-specific properties
        self._radius = 40
        
    @property
    def radius(self):
        """Get circle radius"""
        return self._radius
        
    @radius.setter
    def radius(self, value):
        """Set circle radius"""
        self.prepareGeometryChange()
        self._radius = value
        self.update()
        
    def boundingRect(self):
        """Return bounding rectangle"""
        diameter = self._radius * 2
        return QtCore.QRectF(0, 0, diameter, diameter)
        
    def shape(self):
        """Return shape for collision detection"""
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path
        
    def paint(self, painter, option, widget):
        """Paint the circle item"""
        bg_color, border_color, text_color = self.get_current_colors()
        
        # Setup painter
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw background
        painter.setBrush(QtGui.QBrush(bg_color))
        painter.setPen(QtGui.QPen(border_color, self._border_width))
        painter.drawEllipse(self.boundingRect())
        
        # Draw text
        painter.setPen(QtGui.QPen(text_color))
        painter.setFont(self._font)
        
        text_rect = self.boundingRect()
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, self._text)
        
    def to_dict(self):
        """Serialize to dictionary"""
        data = super(CircleItem, self).to_dict()
        data.update({
            'radius': self._radius
        })
        return data
        
    def from_dict(self, data):
        """Deserialize from dictionary"""
        super(CircleItem, self).from_dict(data)
        self._radius = data.get('radius', 40)
        self.update()