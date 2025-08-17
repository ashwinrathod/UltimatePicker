# File: items/polygon.py
"""
Polygon Item for Ultimate Animation Picker
Editable multi-point polygon with add/remove points functionality
"""

import math
from PySide2 import QtWidgets, QtCore, QtGui
from .base_item import BasePickerItem

class PolygonItem(BasePickerItem):
    """Editable polygon picker item"""
    
    def __init__(self, points=None, parent=None):
        super(PolygonItem, self).__init__(parent)
        
        # Initialize with default triangle if no points provided
        if points is None:
            self._points = [
                QtCore.QPointF(0, -30),
                QtCore.QPointF(-25, 25),
                QtCore.QPointF(25, 25)
            ]
        else:
            self._points = list(points)
            
        self._is_editing_points = False
        self._selected_point_index = -1
        self._hover_point_index = -1
        self._handle_radius = 4
        self._closed_polygon = True
        
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        self.update_bounding_rect()
        
    def boundingRect(self):
        """Return bounding rectangle"""
        if not self._points:
            return QtCore.QRectF()
            
        # Calculate bounds from points
        min_x = min(point.x() for point in self._points)
        max_x = max(point.x() for point in self._points)
        min_y = min(point.y() for point in self._points)
        max_y = max(point.y() for point in self._points)
        
        # Add padding for handles and pen width
        padding = max(self._handle_radius + 2, self.pen_width + 2)
        
        return QtCore.QRectF(
            min_x - padding,
            min_y - padding,
            max_x - min_x + 2 * padding,
            max_y - min_y + 2 * padding
        )
        
    def update_bounding_rect(self):
        """Update bounding rectangle and notify of changes"""
        self.prepareGeometryChange()
        
    def paint(self, painter, option, widget):
        """Paint the polygon"""
        if not self._points:
            return
            
        # Set up painter
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Create polygon from points
        polygon = QtGui.QPolygonF(self._points)
        
        # Fill polygon
        if self._closed_polygon:
            painter.setBrush(self.get_current_brush())
        else:
            painter.setBrush(QtCore.Qt.NoBrush)
            
        painter.setPen(self.get_current_pen())
        
        if self._closed_polygon:
            painter.drawPolygon(polygon)
        else:
            painter.drawPolyline(polygon)
            
        # Draw text if present
        if self.text:
            self.draw_text(painter)
            
        # Draw editing handles if in edit mode
        if self._is_editing_points:
            self.draw_point_handles(painter)
            
    def draw_point_handles(self, painter):
        """Draw point editing handles"""
        painter.setBrush(QtCore.Qt.white)
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        
        for i, point in enumerate(self._points):
            # Highlight selected or hovered point
            if i == self._selected_point_index:
                painter.setBrush(QtCore.Qt.red)
            elif i == self._hover_point_index:
                painter.setBrush(QtCore.Qt.yellow)
            else:
                painter.setBrush(QtCore.Qt.white)
                
            painter.drawEllipse(point, self._handle_radius, self._handle_radius)
            
    def set_points(self, points):
        """Set polygon points"""
        self._points = list(points)
        self.update_bounding_rect()
        self.update()
        
    def get_points(self):
        """Get polygon points"""
        return self._points[:]
        
    def add_point(self, position, insert_index=None):
        """Add a point to the polygon"""
        if insert_index is None:
            self._points.append(position)
        else:
            self._points.insert(insert_index, position)
            
        self.update_bounding_rect()
        self.update()
        
    def remove_point(self, index):
        """Remove a point from the polygon"""
        if 0 <= index < len(self._points) and len(self._points) > 3:
            del self._points[index]
            
            # Update selected point index
            if self._selected_point_index >= index:
                self._selected_point_index = max(-1, self._selected_point_index - 1)
                
            self.update_bounding_rect()
            self.update()
            return True
        return False
        
    def move_point(self, index, new_position):
        """Move a point to new position"""
        if 0 <= index < len(self._points):
            self._points[index] = new_position
            self.update_bounding_rect()
            self.update()
            
    def set_editing_points(self, editing):
        """Set point editing mode"""
        self._is_editing_points = editing
        self.update()
        
    def is_editing_points(self):
        """Check if in point editing mode"""
        return self._is_editing_points
        
    def set_closed_polygon(self, closed):
        """Set whether polygon is closed or open polyline"""
        self._closed_polygon = closed
        self.update()
        
    def is_closed_polygon(self):
        """Check if polygon is closed"""
        return self._closed_polygon
        
    def mousePressEvent(self, event):
        """Handle mouse press for point editing"""
        if self._is_editing_points and event.button() == QtCore.Qt.LeftButton:
            point_index = self.get_point_at_position(event.pos())
            
            if point_index >= 0:
                self._selected_point_index = point_index
                self.update()
                return
            elif event.modifiers() & QtCore.Qt.ControlModifier:
                # Add new point
                self.add_new_point_at_position(event.pos())
                return
                
        super(PolygonItem, self).mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """Handle mouse move for point dragging"""
        if self._is_editing_points and self._selected_point_index >= 0:
            self.move_point(self._selected_point_index, event.pos())
            return
            
        super(PolygonItem, self).mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if self._is_editing_points:
            self._selected_point_index = -1
            self.update()
            return
            
        super(PolygonItem, self).mouseReleaseEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        """Handle double click to add/remove points"""
        if self._is_editing_points:
            point_index = self.get_point_at_position(event.pos())
            
            if point_index >= 0:
                # Remove point on double click
                self.remove_point(point_index)
            else:
                # Add point on double click in empty area
                self.add_new_point_at_position(event.pos())
        else:
            super(PolygonItem, self).mouseDoubleClickEvent(event)
            
    def hoverMoveEvent(self, event):
        """Handle hover for point highlighting"""
        if self._is_editing_points:
            self._hover_point_index = self.get_point_at_position(event.pos())
            self.update()
        else:
            super(PolygonItem, self).hoverMoveEvent(event)
            
    def hoverLeaveEvent(self, event):
        """Handle hover leave"""
        if self._is_editing_points:
            self._hover_point_index = -1
            self.update()
        else:
            super(PolygonItem, self).hoverLeaveEvent(event)
            
    def get_point_at_position(self, pos):
        """Get point index at given position"""
        for i, point in enumerate(self._points):
            distance = math.sqrt((point.x() - pos.x())**2 + (point.y() - pos.y())**2)
            if distance <= self._handle_radius + 2:
                return i
        return -1
        
    def add_new_point_at_position(self, pos):
        """Add new point at position, inserting at best location"""
        if len(self._points) < 2:
            self.add_point(pos)
            return
            
        # Find best edge to insert the new point
        best_edge_index = 0
        min_distance = float('inf')
        
        for i in range(len(self._points)):
            next_i = (i + 1) % len(self._points)
            edge_distance = self.point_to_line_distance(pos, self._points[i], self._points[next_i])
            
            if edge_distance < min_distance:
                min_distance = edge_distance
                best_edge_index = next_i
                
        # Insert point after the best edge
        self.add_point(pos, best_edge_index)
        
    def point_to_line_distance(self, point, line_start, line_end):
        """Calculate distance from point to line segment"""
        # Vector from line start to line end
        line_vec = QtCore.QPointF(line_end.x() - line_start.x(), line_end.y() - line_start.y())
        # Vector from line start to point
        point_vec = QtCore.QPointF(point.x() - line_start.x(), point.y() - line_start.y())
        
        # Calculate the projection parameter
        line_len_sq = line_vec.x()**2 + line_vec.y()**2
        if line_len_sq == 0:
            return math.sqrt(point_vec.x()**2 + point_vec.y()**2)
            
        t = max(0, min(1, (point_vec.x() * line_vec.x() + point_vec.y() * line_vec.y()) / line_len_sq))
        
        # Find the projection point
        projection = QtCore.QPointF(
            line_start.x() + t * line_vec.x(),
            line_start.y() + t * line_vec.y()
        )
        
        # Calculate distance from point to projection
        distance_vec = QtCore.QPointF(point.x() - projection.x(), point.y() - projection.y())
        return math.sqrt(distance_vec.x()**2 + distance_vec.y()**2)
        
    def create_regular_polygon(self, sides, radius, center=None):
        """Create a regular polygon"""
        if center is None:
            center = QtCore.QPointF(0, 0)
            
        points = []
        angle_step = 2 * math.pi / sides
        
        for i in range(sides):
            angle = i * angle_step - math.pi / 2  # Start from top
            x = center.x() + radius * math.cos(angle)
            y = center.y() + radius * math.sin(angle)
            points.append(QtCore.QPointF(x, y))
            
        self.set_points(points)
        
    def create_star_polygon(self, outer_radius, inner_radius, points=5, center=None):
        """Create a star polygon"""
        if center is None:
            center = QtCore.QPointF(0, 0)
            
        star_points = []
        angle_step = math.pi / points
        
        for i in range(points * 2):
            angle = i * angle_step - math.pi / 2
            radius = outer_radius if i % 2 == 0 else inner_radius
            x = center.x() + radius * math.cos(angle)
            y = center.y() + radius * math.sin(angle)
            star_points.append(QtCore.QPointF(x, y))
            
        self.set_points(star_points)
        
    def simplify_polygon(self, tolerance=5.0):
        """Simplify polygon by removing redundant points"""
        if len(self._points) <= 3:
            return
            
        simplified_points = [self._points[0]]
        
        for i in range(1, len(self._points) - 1):
            # Check if point is redundant using Douglas-Peucker style check
            prev_point = self._points[i - 1]
            current_point = self._points[i]
            next_point = self._points[i + 1]
            
            distance = self.point_to_line_distance(current_point, prev_point, next_point)
            
            if distance > tolerance:
                simplified_points.append(current_point)
                
        simplified_points.append(self._points[-1])
        
        if len(simplified_points) >= 3:
            self.set_points(simplified_points)
            
    def get_polygon_area(self):
        """Calculate polygon area"""
        if len(self._points) < 3:
            return 0
            
        area = 0
        for i in range(len(self._points)):
            j = (i + 1) % len(self._points)
            area += self._points[i].x() * self._points[j].y()
            area -= self._points[j].x() * self._points[i].y()
            
        return abs(area) / 2.0
        
    def get_polygon_perimeter(self):
        """Calculate polygon perimeter"""
        if len(self._points) < 2:
            return 0
            
        perimeter = 0
        for i in range(len(self._points)):
            j = (i + 1) % len(self._points)
            dx = self._points[j].x() - self._points[i].x()
            dy = self._points[j].y() - self._points[i].y()
            perimeter += math.sqrt(dx*dx + dy*dy)
            
        return perimeter
        
    def to_dict(self):
        """Serialize to dictionary"""
        data = super(PolygonItem, self).to_dict()
        data.update({
            'points': [(point.x(), point.y()) for point in self._points],
            'closed_polygon': self._closed_polygon
        })
        return data
        
    def from_dict(self, data):
        """Deserialize from dictionary"""
        super(PolygonItem, self).from_dict(data)
        
        if 'points' in data:
            points = [QtCore.QPointF(x, y) for x, y in data['points']]
            self.set_points(points)
            
        if 'closed_polygon' in data:
            self.set_closed_polygon(data['closed_polygon'])
