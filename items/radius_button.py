# File: items/radius_button.py
"""
Radius Button Item for Ultimate Animation Picker
Interactive radius/distance control for attribute manipulation
"""

import math
import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore, QtGui
from .base_item import BasePickerItem

class RadiusButtonItem(BasePickerItem):
    """Interactive radius button picker item"""
    
    # Signals
    radius_changed = QtCore.Signal(float)
    
    def __init__(self, parent=None):
        super(RadiusButtonItem, self).__init__(parent)
        
        # Radius properties
        self._min_radius = 5.0
        self._max_radius = 100.0
        self._current_radius = 25.0
        self._center_radius = 5.0  # Size of center handle
        self._snap_to_angles = False
        self._angle_snap_degrees = 15.0
        
        # Visual properties
        self._circle_color = QtCore.Qt.blue
        self._center_color = QtCore.Qt.darkBlue
        self._handle_color = QtCore.Qt.white
        self._handle_border_color = QtCore.Qt.black
        self._guide_line_color = QtCore.Qt.gray
        
        # Interaction state
        self._is_dragging = False
        self._drag_start_pos = QtCore.QPointF()
        self._center_point = QtCore.QPointF(50, 50)  # Default center
        self._handle_position = QtCore.QPointF()
        
        # Size
        self._width = 100
        self._height = 100
        
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Connected attributes
        self._connected_objects = []
        self._connected_attribute = ""
        
        # Update handle position
        self.update_handle_position()
        
    def boundingRect(self):
        """Return bounding rectangle"""
        max_radius = max(self._max_radius, self._current_radius)
        padding = 10  # Extra padding for handles
        size = (max_radius + padding) * 2
        
        return QtCore.QRectF(
            self._center_point.x() - max_radius - padding,
            self._center_point.y() - max_radius - padding,
            size,
            size
        )
        
    def paint(self, painter, option, widget):
        """Paint the radius button"""
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw guide circle (max radius)
        if self._max_radius > self._current_radius:
            painter.setPen(QtGui.QPen(self._guide_line_color, 1, QtCore.Qt.DashLine))
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawEllipse(self._center_point, self._max_radius, self._max_radius)
            
        # Draw current radius circle
        painter.setPen(QtGui.QPen(self._circle_color, 2))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawEllipse(self._center_point, self._current_radius, self._current_radius)
        
        # Draw radius line
        painter.setPen(QtGui.QPen(self._circle_color, 1))
        painter.drawLine(self._center_point, self._handle_position)
        
        # Draw center handle
        painter.setBrush(QtGui.QBrush(self._center_color))
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        painter.drawEllipse(self._center_point, self._center_radius, self._center_radius)
        
        # Draw radius handle
        painter.setBrush(QtGui.QBrush(self._handle_color))
        painter.setPen(QtGui.QPen(self._handle_border_color, 1))
        handle_size = 6
        painter.drawEllipse(self._handle_position, handle_size, handle_size)
        
        # Draw radius value text
        radius_text = f"R: {self._current_radius:.1f}"
        painter.setPen(QtCore.Qt.black)
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        
        text_pos = QtCore.QPointF(
            self._center_point.x() - 20,
            self._center_point.y() - self._current_radius - 15
        )
        painter.drawText(text_pos, radius_text)
        
        # Draw angle snap guides if enabled
        if self._snap_to_angles:
            self.draw_angle_guides(painter)
            
        # Draw text if present
        if self.text:
            text_rect = QtCore.QRectF(
                self._center_point.x() - 50,
                self._center_point.y() + self._current_radius + 10,
                100,
                20
            )
            painter.setPen(self.text_color)
            font = QtGui.QFont(self.font_family, self.font_size)
            font.setBold(self.font_bold)
            font.setItalic(self.font_italic)
            painter.setFont(font)
            painter.drawText(text_rect, QtCore.Qt.AlignCenter, self.text)
            
    def draw_angle_guides(self, painter):
        """Draw angle snap guide lines"""
        painter.setPen(QtGui.QPen(self._guide_line_color, 1, QtCore.Qt.DotLine))
        
        angle_step = math.radians(self._angle_snap_degrees)
        current_angle = 0
        
        while current_angle < 2 * math.pi:
            end_x = self._center_point.x() + self._max_radius * math.cos(current_angle)
            end_y = self._center_point.y() + self._max_radius * math.sin(current_angle)
            end_point = QtCore.QPointF(end_x, end_y)
            
            painter.drawLine(self._center_point, end_point)
            current_angle += angle_step
            
    def update_handle_position(self):
        """Update handle position based on current radius"""
        # Default angle (0 degrees = right)
        angle = 0
        
        self._handle_position = QtCore.QPointF(
            self._center_point.x() + self._current_radius * math.cos(angle),
            self._center_point.y() + self._current_radius * math.sin(angle)
        )
        
    def set_radius(self, radius):
        """Set radius value"""
        old_radius = self._current_radius
        self._current_radius = max(self._min_radius, min(self._max_radius, radius))
        
        if abs(self._current_radius - old_radius) > 0.1:
            self.update_handle_position()
            self.update()
            self.radius_changed.emit(self._current_radius)
            self.apply_value_to_maya()
            
    def get_radius(self):
        """Get current radius"""
        return self._current_radius
        
    def set_radius_range(self, min_radius, max_radius):
        """Set radius range"""
        self._min_radius = max(1.0, min_radius)
        self._max_radius = max(self._min_radius + 1.0, max_radius)
        # Clamp current radius to new range
        self.set_radius(self._current_radius)
        
    def get_radius_range(self):
        """Get radius range"""
        return self._min_radius, self._max_radius
        
    def set_center_point(self, center):
        """Set center point"""
        self._center_point = center
        self.update_handle_position()
        self.prepareGeometryChange()
        self.update()
        
    def get_center_point(self):
        """Get center point"""
        return self._center_point
        
    def set_angle_snap(self, enabled, degrees=15.0):
        """Set angle snapping"""
        self._snap_to_angles = enabled
        self._angle_snap_degrees = degrees
        self.update()
        
    def connect_to_maya_attribute(self, objects, attribute):
        """Connect radius to Maya attribute"""
        self._connected_objects = objects if isinstance(objects, list) else [objects]
        self._connected_attribute = attribute
        
        # Get current value from Maya
        if self._connected_objects and self._connected_attribute:
            try:
                current_value = cmds.getAttr(f"{self._connected_objects[0]}.{self._connected_attribute}")
                self.set_radius(current_value)
            except:
                pass
                
    def apply_value_to_maya(self):
        """Apply current radius to connected Maya attributes"""
        if not self._connected_objects or not self._connected_attribute:
            return
            
        for obj in self._connected_objects:
            try:
                cmds.setAttr(f"{obj}.{self._connected_attribute}", self._current_radius)
            except Exception as e:
                print(f"Failed to set {obj}.{self._connected_attribute}: {e}")
                
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == QtCore.Qt.LeftButton:
            # Check if clicking on center or handle
            center_dist = self.distance_to_point(event.pos(), self._center_point)
            handle_dist = self.distance_to_point(event.pos(), self._handle_position)
            
            if center_dist <= self._center_radius + 2:
                # Dragging center - move entire control
                super(RadiusButtonItem, self).mousePressEvent(event)
            elif handle_dist <= 8:
                # Dragging handle - adjust radius
                self._is_dragging = True
                self._drag_start_pos = event.pos()
                event.accept()
            else:
                # Click elsewhere - set new radius
                new_radius = self.distance_to_point(event.pos(), self._center_point)
                self.set_radius(new_radius)
                event.accept()
        else:
            super(RadiusButtonItem, self).mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if self._is_dragging:
            # Calculate new radius from mouse position
            new_radius = self.distance_to_point(event.pos(), self._center_point)
            
            # Apply angle snapping if enabled
            if self._snap_to_angles:
                angle = self.angle_to_point(event.pos(), self._center_point)
                snapped_angle = self.snap_angle(angle)
                
                # Update handle position with snapped angle
                self._handle_position = QtCore.QPointF(
                    self._center_point.x() + new_radius * math.cos(snapped_angle),
                    self._center_point.y() + new_radius * math.sin(snapped_angle)
                )
            else:
                self._handle_position = event.pos()
                
            self.set_radius(new_radius)
            event.accept()
        else:
            super(RadiusButtonItem, self).mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == QtCore.Qt.LeftButton and self._is_dragging:
            self._is_dragging = False
            self.update_handle_position()  # Snap to exact position
            event.accept()
        else:
            super(RadiusButtonItem, self).mouseReleaseEvent(event)
            
    def wheelEvent(self, event):
        """Handle mouse wheel for radius adjustment"""
        delta = event.angleDelta().y()
        radius_step = 2.0 if delta > 0 else -2.0
        new_radius = self._current_radius + radius_step
        self.set_radius(new_radius)
        event.accept()
        
    def distance_to_point(self, point1, point2):
        """Calculate distance between two points"""
        dx = point1.x() - point2.x()
        dy = point1.y() - point2.y()
        return math.sqrt(dx * dx + dy * dy)
        
    def angle_to_point(self, point, center):
        """Calculate angle from center to point"""
        dx = point.x() - center.x()
        dy = point.y() - center.y()
        return math.atan2(dy, dx)
        
    def snap_angle(self, angle):
        """Snap angle to nearest guide angle"""
        angle_step = math.radians(self._angle_snap_degrees)
        snapped_steps = round(angle / angle_step)
        return snapped_steps * angle_step
        
    def create_distance_constraint(self, obj1, obj2):
        """Create Maya distance constraint visualization"""
        try:
            # This would create a visual representation of distance between two objects
            if cmds.objExists(obj1) and cmds.objExists(obj2):
                pos1 = cmds.xform(obj1, query=True, worldSpace=True, translation=True)
                pos2 = cmds.xform(obj2, query=True, worldSpace=True, translation=True)
                
                distance = math.sqrt(
                    (pos1[0] - pos2[0])**2 + 
                    (pos1[1] - pos2[1])**2 + 
                    (pos1[2] - pos2[2])**2
                )
                
                self.set_radius(distance)
                self._connected_objects = [obj1, obj2]
                self._connected_attribute = "distance"
                
        except Exception as e:
            print(f"Error creating distance constraint: {e}")
            
    def set_colors(self, circle_color=None, center_color=None, handle_color=None, 
                   handle_border_color=None, guide_color=None):
        """Set radius button colors"""
        if circle_color is not None:
            self._circle_color = circle_color
        if center_color is not None:
            self._center_color = center_color
        if handle_color is not None:
            self._handle_color = handle_color
        if handle_border_color is not None:
            self._handle_border_color = handle_border_color
        if guide_color is not None:
            self._guide_line_color = guide_color
        self.update()
        
    def to_dict(self):
        """Serialize to dictionary"""
        data = super(RadiusButtonItem, self).to_dict()
        data.update({
            'min_radius': self._min_radius,
            'max_radius': self._max_radius,
            'current_radius': self._current_radius,
            'center_radius': self._center_radius,
            'center_point': (self._center_point.x(), self._center_point.y()),
            'snap_to_angles': self._snap_to_angles,
            'angle_snap_degrees': self._angle_snap_degrees,
            'connected_objects': self._connected_objects,
            'connected_attribute': self._connected_attribute,
            'circle_color': self._circle_color.name() if hasattr(self._circle_color, 'name') else str(self._circle_color),
            'center_color': self._center_color.name() if hasattr(self._center_color, 'name') else str(self._center_color),
            'handle_color': self._handle_color.name() if hasattr(self._handle_color, 'name') else str(self._handle_color),
            'handle_border_color': self._handle_border_color.name() if hasattr(self._handle_border_color, 'name') else str(self._handle_border_color),
            'guide_line_color': self._guide_line_color.name() if hasattr(self._guide_line_color, 'name') else str(self._guide_line_color)
        })
        return data
        
    def from_dict(self, data):
        """Deserialize from dictionary"""
        super(RadiusButtonItem, self).from_dict(data)
        
        self._min_radius = data.get('min_radius', 5.0)
        self._max_radius = data.get('max_radius', 100.0)
        self._current_radius = data.get('current_radius', 25.0)
        self._center_radius = data.get('center_radius', 5.0)
        self._snap_to_angles = data.get('snap_to_angles', False)
        self._angle_snap_degrees = data.get('angle_snap_degrees', 15.0)
        self._connected_objects = data.get('connected_objects', [])
        self._connected_attribute = data.get('connected_attribute', "")
        
        if 'center_point' in data:
            x, y = data['center_point']
            self._center_point = QtCore.QPointF(x, y)
            
        # Colors
        if 'circle_color' in data:
            self._circle_color = QtGui.QColor(data['circle_color'])
        if 'center_color' in data:
            self._center_color = QtGui.QColor(data['center_color'])
        if 'handle_color' in data:
            self._handle_color = QtGui.QColor(data['handle_color'])
        if 'handle_border_color' in data:
            self._handle_border_color = QtGui.QColor(data['handle_border_color'])
        if 'guide_line_color' in data:
            self._guide_line_color = QtGui.QColor(data['guide_line_color'])
            
        self.update_handle_position()
