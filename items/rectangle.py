# File: items/rectangle.py
"""
Rectangle Picker Item for Ultimate Animation Picker
Standard rectangular button item
"""

from PySide2 import QtWidgets, QtCore, QtGui
from .base_item import BasePickerItem

class RectangleItem(BasePickerItem):
    """Rectangle picker item"""
    
    def __init__(self, parent=None):
        super(RectangleItem, self).__init__(parent)
        
        # Rectangle-specific properties
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
        """Paint the rectangle item"""
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
        """Set rectangle size"""
        self.prepareGeometryChange()
        self._width = width
        self._height = height
        self.update()
        
    def get_size(self):
        """Get rectangle size"""
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
        data = super(RectangleItem, self).to_dict()
        data.update({
            'width': self._width,
            'height': self._height,
            'radius': self._radius
        })
        return data
        
    def from_dict(self, data):
        """Deserialize from dictionary"""
        super(RectangleItem, self).from_dict(data)
        self._width = data.get('width', 80)
        self._height = data.get('height', 30)
        self._radius = data.get('radius', 4)
        self.update()