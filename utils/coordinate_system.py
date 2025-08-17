# File: utils/coordinate_system.py
"""
Coordinate System Utilities for Ultimate Animation Picker
Handles Local/World coordinate transformations and positioning
"""

from PySide2 import QtCore, QtGui
import math

class CoordinateSystem:
    """Coordinate system types"""
    LOCAL = "Local"
    WORLD = "World"


class CoordinateTransform(QtCore.QObject):
    """Handles coordinate transformations between Local and World space"""
    
    def __init__(self, parent=None):
        super(CoordinateTransform, self).__init__(parent)
        self._canvas_transform = QtGui.QTransform()
        self._zoom_factor = 1.0
        self._pan_offset = QtCore.QPointF(0, 0)
        
    def set_canvas_transform(self, transform):
        """Set canvas transformation matrix"""
        self._canvas_transform = transform
        
    def set_zoom_factor(self, zoom):
        """Set zoom factor"""
        self._zoom_factor = zoom
        
    def set_pan_offset(self, offset):
        """Set pan offset"""
        self._pan_offset = offset
        
    def local_to_world(self, local_point):
        """Transform local coordinates to world coordinates"""
        return self._canvas_transform.map(local_point)
        
    def world_to_local(self, world_point):
        """Transform world coordinates to local coordinates"""
        inverse_transform, invertible = self._canvas_transform.inverted()
        if invertible:
            return inverse_transform.map(world_point)
        return world_point
        
    def local_to_screen(self, local_point):
        """Transform local coordinates to screen coordinates"""
        # Apply zoom and pan
        screen_point = QtCore.QPointF(
            local_point.x() * self._zoom_factor + self._pan_offset.x(),
            local_point.y() * self._zoom_factor + self._pan_offset.y()
        )
        return screen_point
        
    def screen_to_local(self, screen_point):
        """Transform screen coordinates to local coordinates"""
        # Remove pan and zoom
        local_point = QtCore.QPointF(
            (screen_point.x() - self._pan_offset.x()) / self._zoom_factor,
            (screen_point.y() - self._pan_offset.y()) / self._zoom_factor
        )
        return local_point
        
    def apply_zoom_to_point(self, point, zoom_center, old_zoom, new_zoom):
        """Apply zoom transformation around a center point"""
        if old_zoom == 0:
            return point
            
        # Vector from zoom center to point
        offset = point - zoom_center
        
        # Scale the offset
        scale_factor = new_zoom / old_zoom
        scaled_offset = offset * scale_factor
        
        # Return new position
        return zoom_center + scaled_offset


class PositionManager(QtCore.QObject):
    """Manages item positioning with coordinate system support"""
    
    def __init__(self, parent=None):
        super(PositionManager, self).__init__(parent)
        self._coordinate_transform = CoordinateTransform(self)
        
    def set_item_position(self, item, position, coordinate_system=CoordinateSystem.LOCAL):
        """Set item position in specified coordinate system"""
        if not hasattr(item, 'setPos'):
            return False
            
        if coordinate_system == CoordinateSystem.WORLD:
            # Convert world position to local
            local_position = self._coordinate_transform.world_to_local(position)
            item.setPos(local_position)
        else:
            item.setPos(position)
            
        # Store coordinate system preference
        if hasattr(item, 'coordinate_system'):
            item.coordinate_system = coordinate_system
            
        return True
        
    def get_item_position(self, item, coordinate_system=CoordinateSystem.LOCAL):
        """Get item position in specified coordinate system"""
        if not hasattr(item, 'pos'):
            return QtCore.QPointF()
            
        local_position = item.pos()
        
        if coordinate_system == CoordinateSystem.WORLD:
            return self._coordinate_transform.local_to_world(local_position)
        else:
            return local_position
            
    def move_item(self, item, delta, coordinate_system=None):
        """Move item by delta amount"""
        if coordinate_system is None:
            # Use item's preferred coordinate system
            coordinate_system = getattr(item, 'coordinate_system', CoordinateSystem.LOCAL)
            
        current_pos = self.get_item_position(item, coordinate_system)
        new_pos = current_pos + delta
        self.set_item_position(item, new_pos, coordinate_system)
        
    def align_items_to_grid(self, items, grid_size=10, coordinate_system=CoordinateSystem.LOCAL):
        """Snap items to grid"""
        for item in items:
            current_pos = self.get_item_position(item, coordinate_system)
            
            # Snap to grid
            snapped_x = round(current_pos.x() / grid_size) * grid_size
            snapped_y = round(current_pos.y() / grid_size) * grid_size
            snapped_pos = QtCore.QPointF(snapped_x, snapped_y)
            
            self.set_item_position(item, snapped_pos, coordinate_system)


class ZoomManager(QtCore.QObject):
    """Manages zoom operations with coordinate system awareness"""
    
    # Signals
    zoom_changed = QtCore.Signal(float)  # zoom_factor
    
    def __init__(self, parent=None):
        super(ZoomManager, self).__init__(parent)
        self._zoom_factor = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 10.0
        self._zoom_step = 0.1
        
    def set_zoom_factor(self, zoom_factor):
        """Set zoom factor with bounds checking"""
        old_zoom = self._zoom_factor
        self._zoom_factor = max(self._min_zoom, min(self._max_zoom, zoom_factor))
        
        if abs(self._zoom_factor - old_zoom) > 0.001:
            self.zoom_changed.emit(self._zoom_factor)
            
        return self._zoom_factor
        
    def get_zoom_factor(self):
        """Get current zoom factor"""
        return self._zoom_factor
        
    def zoom_in(self, center_point=None):
        """Zoom in by one step"""
        new_zoom = self._zoom_factor + self._zoom_step
        return self.set_zoom_factor(new_zoom)
        
    def zoom_out(self, center_point=None):
        """Zoom out by one step"""
        new_zoom = self._zoom_factor - self._zoom_step
        return self.set_zoom_factor(new_zoom)
        
    def zoom_to_fit(self, rect, viewport_rect):
        """Calculate zoom to fit rectangle in viewport"""
        if rect.isEmpty() or viewport_rect.isEmpty():
            return self._zoom_factor
            
        # Calculate zoom factors for width and height
        zoom_x = viewport_rect.width() / rect.width()
        zoom_y = viewport_rect.height() / rect.height()
        
        # Use the smaller zoom to ensure everything fits
        zoom_factor = min(zoom_x, zoom_y) * 0.9  # 90% to add some margin
        
        return self.set_zoom_factor(zoom_factor)
        
    def zoom_to_selection(self, items, viewport_rect):
        """Zoom to fit selected items"""
        if not items:
            return self._zoom_factor
            
        # Calculate bounding rectangle of all items
        bounding_rect = QtCore.QRectF()
        for item in items:
            if hasattr(item, 'boundingRect') and hasattr(item, 'pos'):
                item_rect = item.boundingRect()
                item_pos = item.pos()
                world_rect = QtCore.QRectF(
                    item_pos.x() + item_rect.x(),
                    item_pos.y() + item_rect.y(),
                    item_rect.width(),
                    item_rect.height()
                )
                
                if bounding_rect.isEmpty():
                    bounding_rect = world_rect
                else:
                    bounding_rect = bounding_rect.united(world_rect)
                    
        return self.zoom_to_fit(bounding_rect, viewport_rect)
        
    def set_zoom_limits(self, min_zoom, max_zoom):
        """Set zoom limits"""
        self._min_zoom = max(0.01, min_zoom)
        self._max_zoom = max(self._min_zoom, max_zoom)
        
        # Clamp current zoom to new limits
        self.set_zoom_factor(self._zoom_factor)


class PanManager(QtCore.QObject):
    """Manages pan operations"""
    
    # Signals
    pan_changed = QtCore.Signal(QtCore.QPointF)  # pan_offset
    
    def __init__(self, parent=None):
        super(PanManager, self).__init__(parent)
        self._pan_offset = QtCore.QPointF(0, 0)
        self._is_panning = False
        self._last_pan_point = QtCore.QPointF()
        
    def start_pan(self, start_point):
        """Start panning operation"""
        self._is_panning = True
        self._last_pan_point = start_point
        
    def update_pan(self, current_point):
        """Update pan during drag"""
        if not self._is_panning:
            return
            
        delta = current_point - self._last_pan_point
        self._pan_offset += delta
        self._last_pan_point = current_point
        
        self.pan_changed.emit(self._pan_offset)
        
    def end_pan(self):
        """End panning operation"""
        self._is_panning = False
        
    def set_pan_offset(self, offset):
        """Set pan offset directly"""
        self._pan_offset = offset
        self.pan_changed.emit(self._pan_offset)
        
    def get_pan_offset(self):
        """Get current pan offset"""
        return self._pan_offset
        
    def reset_pan(self):
        """Reset pan to origin"""
        self.set_pan_offset(QtCore.QPointF(0, 0))
        
    def pan_to_center_point(self, point, viewport_center):
        """Pan so that the given point is at viewport center"""
        new_offset = viewport_center - point
        self.set_pan_offset(new_offset)


class ViewportManager(QtCore.QObject):
    """Manages viewport transformations combining zoom and pan"""
    
    # Signals
    viewport_changed = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(ViewportManager, self).__init__(parent)
        self.zoom_manager = ZoomManager(self)
        self.pan_manager = PanManager(self)
        self.coordinate_transform = CoordinateTransform(self)
        
        # Connect signals
        self.zoom_manager.zoom_changed.connect(self.on_transformation_changed)
        self.pan_manager.pan_changed.connect(self.on_transformation_changed)
        
    def on_transformation_changed(self):
        """Handle transformation changes"""
        # Update coordinate transform
        zoom = self.zoom_manager.get_zoom_factor()
        pan = self.pan_manager.get_pan_offset()
        
        self.coordinate_transform.set_zoom_factor(zoom)
        self.coordinate_transform.set_pan_offset(pan)
        
        # Create combined transform
        transform = QtGui.QTransform()
        transform.translate(pan.x(), pan.y())
        transform.scale(zoom, zoom)
        
        self.coordinate_transform.set_canvas_transform(transform)
        self.viewport_changed.emit()
        
    def get_viewport_transform(self):
        """Get combined viewport transformation matrix"""
        zoom = self.zoom_manager.get_zoom_factor()
        pan = self.pan_manager.get_pan_offset()
        
        transform = QtGui.QTransform()
        transform.translate(pan.x(), pan.y())
        transform.scale(zoom, zoom)
        
        return transform
        
    def map_to_viewport(self, scene_point):
        """Map scene coordinates to viewport coordinates"""
        transform = self.get_viewport_transform()
        return transform.map(scene_point)
        
    def map_from_viewport(self, viewport_point):
        """Map viewport coordinates to scene coordinates"""
        transform = self.get_viewport_transform()
        inverse_transform, invertible = transform.inverted()
        if invertible:
            return inverse_transform.map(viewport_point)
        return viewport_point
        
    def zoom_at_point(self, zoom_delta, zoom_center):
        """Zoom in/out while keeping zoom_center stationary"""
        old_zoom = self.zoom_manager.get_zoom_factor()
        
        # Apply zoom
        if zoom_delta > 0:
            new_zoom = old_zoom * 1.15  # Zoom in
        else:
            new_zoom = old_zoom / 1.15  # Zoom out
            
        new_zoom = self.zoom_manager.set_zoom_factor(new_zoom)
        
        if abs(new_zoom - old_zoom) > 0.001:
            # Adjust pan to keep zoom center stationary
            current_pan = self.pan_manager.get_pan_offset()
            
            # Calculate how much the zoom center moved
            zoom_ratio = new_zoom / old_zoom
            center_offset = zoom_center - current_pan
            new_center_offset = center_offset * zoom_ratio
            new_pan = zoom_center - new_center_offset
            
            self.pan_manager.set_pan_offset(new_pan)
            
    def fit_items_in_view(self, items, viewport_rect, margin=0.1):
        """Fit items in viewport with optional margin"""
        if not items:
            return
            
        # Calculate bounding rectangle
        bounding_rect = QtCore.QRectF()
        for item in items:
            if hasattr(item, 'sceneBoundingRect'):
                item_rect = item.sceneBoundingRect()
            elif hasattr(item, 'boundingRect') and hasattr(item, 'pos'):
                item_rect = item.boundingRect()
                item_pos = item.pos()
                item_rect = QtCore.QRectF(
                    item_pos.x() + item_rect.x(),
                    item_pos.y() + item_rect.y(),
                    item_rect.width(),
                    item_rect.height()
                )
            else:
                continue
                
            if bounding_rect.isEmpty():
                bounding_rect = item_rect
            else:
                bounding_rect = bounding_rect.united(item_rect)
                
        if bounding_rect.isEmpty():
            return
            
        # Add margin
        margin_x = bounding_rect.width() * margin
        margin_y = bounding_rect.height() * margin
        bounding_rect.adjust(-margin_x, -margin_y, margin_x, margin_y)
        
        # Calculate zoom to fit
        zoom_x = viewport_rect.width() / bounding_rect.width()
        zoom_y = viewport_rect.height() / bounding_rect.height()
        zoom_factor = min(zoom_x, zoom_y)
        
        self.zoom_manager.set_zoom_factor(zoom_factor)
        
        # Center the bounding rectangle
        viewport_center = viewport_rect.center()
        bounding_center = bounding_rect.center()
        
        # Calculate pan to center the items
        pan_offset = viewport_center - bounding_center * zoom_factor
        self.pan_manager.set_pan_offset(pan_offset)
        
    def reset_view(self):
        """Reset view to default zoom and pan"""
        self.zoom_manager.set_zoom_factor(1.0)
        self.pan_manager.reset_pan()


class GridSystem(QtCore.QObject):
    """Grid system for snapping and alignment"""
    
    def __init__(self, parent=None):
        super(GridSystem, self).__init__(parent)
        self._grid_size = 10
        self._snap_enabled = False
        self._visible = False
        
    def set_grid_size(self, size):
        """Set grid size"""
        self._grid_size = max(1, size)
        
    def get_grid_size(self):
        """Get grid size"""
        return self._grid_size
        
    def set_snap_enabled(self, enabled):
        """Enable/disable grid snapping"""
        self._snap_enabled = enabled
        
    def is_snap_enabled(self):
        """Check if grid snapping is enabled"""
        return self._snap_enabled
        
    def set_visible(self, visible):
        """Set grid visibility"""
        self._visible = visible
        
    def is_visible(self):
        """Check if grid is visible"""
        return self._visible
        
    def snap_to_grid(self, point):
        """Snap point to grid"""
        if not self._snap_enabled:
            return point
            
        snapped_x = round(point.x() / self._grid_size) * self._grid_size
        snapped_y = round(point.y() / self._grid_size) * self._grid_size
        
        return QtCore.QPointF(snapped_x, snapped_y)
        
    def get_grid_lines(self, viewport_rect, transform):
        """Get grid lines for drawing"""
        if not self._visible:
            return [], []
            
        # Transform viewport to scene coordinates
        inverse_transform, invertible = transform.inverted()
        if not invertible:
            return [], []
            
        scene_rect = inverse_transform.mapRect(viewport_rect)
        
        # Calculate grid line positions
        start_x = math.floor(scene_rect.left() / self._grid_size) * self._grid_size
        end_x = math.ceil(scene_rect.right() / self._grid_size) * self._grid_size
        start_y = math.floor(scene_rect.top() / self._grid_size) * self._grid_size
        end_y = math.ceil(scene_rect.bottom() / self._grid_size) * self._grid_size
        
        # Generate vertical lines
        vertical_lines = []
        x = start_x
        while x <= end_x:
            line_start = transform.map(QtCore.QPointF(x, scene_rect.top()))
            line_end = transform.map(QtCore.QPointF(x, scene_rect.bottom()))
            vertical_lines.append((line_start, line_end))
            x += self._grid_size
            
        # Generate horizontal lines
        horizontal_lines = []
        y = start_y
        while y <= end_y:
            line_start = transform.map(QtCore.QPointF(scene_rect.left(), y))
            line_end = transform.map(QtCore.QPointF(scene_rect.right(), y))
            horizontal_lines.append((line_start, line_end))
            y += self._grid_size
            
        return vertical_lines, horizontal_lines
