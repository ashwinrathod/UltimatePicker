# File: widgets/enhanced_canvas.py
"""
Enhanced Canvas Widget for Ultimate Animation Picker
Provides unlimited work area with advanced navigation, selection, and item management
"""

import math
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal
from ..core.rubber_band import SelectionManager
from ..utils.coordinate_system import ViewportManager, GridSystem
from ..utils.clipboard_manager import get_clipboard_manager

class EnhancedCanvas(QtWidgets.QGraphicsView):
    """Enhanced canvas with unlimited work area and advanced features"""
    
    # Signals
    item_selected = Signal(object)
    item_deselected = Signal(object)
    selection_changed = Signal(list)
    item_added = Signal(object)
    item_removed = Signal(object)
    canvas_clicked = Signal(QtCore.QPointF)
    canvas_double_clicked = Signal(QtCore.QPointF)
    zoom_changed = Signal(float)
    pan_changed = Signal(QtCore.QPointF)
    edit_mode_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super(EnhancedCanvas, self).__init__(parent)
        
        # Canvas properties
        self._edit_mode = False
        self._grid_visible = False
        self._snap_to_grid = False
        self._high_quality_rendering = True
        
        # Navigation state
        self._is_panning = False
        self._is_rubber_band_selecting = False
        self._last_pan_point = QtCore.QPointF()
        self._zoom_factor = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 10.0
        
        # Setup canvas
        self.setup_canvas()
        self.setup_scene()
        self.setup_managers()
        self.setup_interactions()
        
    def setup_canvas(self):
        """Setup canvas properties"""
        # Remove scroll bars
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        
        # Rendering options
        if self._high_quality_rendering:
            self.setRenderHints(
                QtGui.QPainter.Antialiasing | 
                QtGui.QPainter.SmoothPixmapTransform |
                QtGui.QPainter.TextAntialiasing
            )
        
        # View options
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.SmartViewportUpdate)
        self.setOptimizationFlags(QtWidgets.QGraphicsView.DontAdjustForAntialiasing)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        
        # Background
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(45, 45, 45)))
        
        # Frame style
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)
        
    def setup_scene(self):
        """Setup graphics scene"""
        self._scene = QtWidgets.QGraphicsScene(self)
        
        # Set unlimited scene size
        scene_size = 1000000  # Very large scene
        self._scene.setSceneRect(
            -scene_size/2, -scene_size/2, 
            scene_size, scene_size
        )
        
        self.setScene(self._scene)
        
    def setup_managers(self):
        """Setup management systems"""
        # Selection manager
        self.selection_manager = SelectionManager(self)
        self.selection_manager.selection_changed.connect(self.selection_changed.emit)
        
        # Viewport manager (pan/zoom)
        self.viewport_manager = ViewportManager(self)
        self.viewport_manager.viewport_changed.connect(self._on_viewport_changed)
        
        # Grid system
        self.grid_system = GridSystem(self)
        
        # Clipboard manager
        self.clipboard_manager = get_clipboard_manager()
        
    def setup_interactions(self):
        """Setup mouse and keyboard interactions"""
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Focus policy
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        # Context menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
    def set_edit_mode(self, edit_mode):
        """Set edit mode state"""
        if self._edit_mode != edit_mode:
            self._edit_mode = edit_mode
            
            # Update cursor
            if edit_mode:
                self.setCursor(QtCore.Qt.ArrowCursor)
            else:
                self.setCursor(QtCore.Qt.PointingHandCursor)
                
            # Update scene items
            for item in self._scene.items():
                if hasattr(item, 'set_edit_mode'):
                    item.set_edit_mode(edit_mode)
                    
            self.edit_mode_changed.emit(edit_mode)
            
    def is_edit_mode(self):
        """Check if in edit mode"""
        return self._edit_mode
        
    def set_grid_visible(self, visible):
        """Set grid visibility"""
        if self._grid_visible != visible:
            self._grid_visible = visible
            self.grid_system.set_visible(visible)
            self.viewport().update()
            
    def is_grid_visible(self):
        """Check if grid is visible"""
        return self._grid_visible
        
    def set_snap_to_grid(self, snap):
        """Set grid snapping"""
        self._snap_to_grid = snap
        self.grid_system.set_snap_enabled(snap)
        
    def is_snap_to_grid(self):
        """Check if grid snapping is enabled"""
        return self._snap_to_grid
        
    def set_grid_size(self, size):
        """Set grid size"""
        self.grid_system.set_grid_size(size)
        if self._grid_visible:
            self.viewport().update()
            
    def get_grid_size(self):
        """Get grid size"""
        return self.grid_system.get_grid_size()
        
    def add_item(self, item, position=None):
        """Add item to canvas"""
        if position:
            # Snap to grid if enabled
            if self._snap_to_grid:
                position = self.grid_system.snap_to_grid(position)
            item.setPos(position)
            
        # Set edit mode
        if hasattr(item, 'set_edit_mode'):
            item.set_edit_mode(self._edit_mode)
            
        # Add to scene
        self._scene.addItem(item)
        
        # Connect item signals if available
        self._connect_item_signals(item)
        
        self.item_added.emit(item)
        
    def remove_item(self, item):
        """Remove item from canvas"""
        if item in self._scene.items():
            self._scene.removeItem(item)
            
            # Remove from selection
            if item in self.selection_manager.get_selected_items():
                self.selection_manager.deselect_item(item)
                
            self.item_removed.emit(item)
            
    def get_all_items(self):
        """Get all items on canvas"""
        return [item for item in self._scene.items() 
                if not isinstance(item, QtWidgets.QGraphicsProxyWidget)]
                
    def get_selected_items(self):
        """Get selected items"""
        return self.selection_manager.get_selected_items()
        
    def clear_selection(self):
        """Clear all selection"""
        self.selection_manager.clear_selection()
        
    def select_all(self):
        """Select all items"""
        self.selection_manager.select_all()
        
    def delete_selected(self):
        """Delete selected items"""
        selected_items = self.get_selected_items()
        for item in selected_items:
            self.remove_item(item)
            
    def copy_selected(self):
        """Copy selected items to clipboard"""
        selected_items = self.get_selected_items()
        if selected_items:
            self.clipboard_manager.copy_items(selected_items)
            
    def paste_items(self, position=None):
        """Paste items from clipboard"""
        if position is None:
            # Use center of view
            center = self.mapToScene(self.viewport().rect().center())
            position = center
            
        pasted_items = self.clipboard_manager.paste_items(position, self)
        
        # Add pasted items to canvas
        for item in pasted_items:
            self.add_item(item)
            
        # Select pasted items
        if pasted_items:
            self.selection_manager.clear_selection()
            self.selection_manager.select_items(pasted_items)
            
        return pasted_items
        
    def zoom_in(self):
        """Zoom in"""
        center = self.mapToScene(self.viewport().rect().center())
        self.viewport_manager.zoom_manager.zoom_in()
        
    def zoom_out(self):
        """Zoom out"""
        center = self.mapToScene(self.viewport().rect().center())
        self.viewport_manager.zoom_manager.zoom_out()
        
    def zoom_fit(self):
        """Zoom to fit all items"""
        items = self.get_all_items()
        if items:
            viewport_rect = QtCore.QRectF(self.viewport().rect())
            self.viewport_manager.fit_items_in_view(items, viewport_rect)
            
    def zoom_selection(self):
        """Zoom to fit selected items"""
        selected_items = self.get_selected_items()
        if selected_items:
            viewport_rect = QtCore.QRectF(self.viewport().rect())
            self.viewport_manager.fit_items_in_view(selected_items, viewport_rect)
            
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.viewport_manager.zoom_manager.set_zoom_factor(1.0)
        
    def set_zoom_factor(self, factor):
        """Set zoom factor"""
        self.viewport_manager.zoom_manager.set_zoom_factor(factor)
        
    def get_zoom_factor(self):
        """Get current zoom factor"""
        return self.viewport_manager.zoom_manager.get_zoom_factor()
        
    def pan_to_center(self, scene_point):
        """Pan to center point in view"""
        viewport_center = self.viewport().rect().center()
        self.viewport_manager.pan_manager.pan_to_center_point(scene_point, viewport_center)
        
    def reset_view(self):
        """Reset view to default"""
        self.viewport_manager.reset_view()
        
    def _connect_item_signals(self, item):
        """Connect item-specific signals"""
        # This would connect to item-specific signals if the item supports them
        pass
        
    def _on_viewport_changed(self):
        """Handle viewport transformation changes"""
        transform = self.viewport_manager.get_viewport_transform()
        self.setTransform(transform)
        
        # Emit zoom change
        zoom_factor = self.viewport_manager.zoom_manager.get_zoom_factor()
        self.zoom_changed.emit(zoom_factor)
        
        # Emit pan change
        pan_offset = self.viewport_manager.pan_manager.get_pan_offset()
        self.pan_changed.emit(pan_offset)
        
        # Update grid if visible
        if self._grid_visible:
            self.viewport().update()
            
    def _show_context_menu(self, position):
        """Show context menu"""
        scene_pos = self.mapToScene(position)
        item = self.itemAt(position)
        
        # Import context menu
        from .context_menu import CanvasContextMenu
        
        if item and hasattr(item, 'show_context_menu'):
            # Item-specific context menu
            item.show_context_menu(self.mapToGlobal(position))
        else:
            # Canvas context menu
            menu = CanvasContextMenu(self, scene_pos, self.mapToGlobal(position))
            menu.exec_()
            
    # Event handlers
    def mousePressEvent(self, event):
        """Handle mouse press"""
        scene_pos = self.mapToScene(event.pos())
        
        if event.button() == QtCore.Qt.MiddleButton:
            # Start panning
            self._is_panning = True
            self._last_pan_point = event.pos()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            event.accept()
            return
            
        elif event.button() == QtCore.Qt.LeftButton:
            item = self.itemAt(event.pos())
            
            if not item:
                # Click on empty canvas
                modifiers = event.modifiers()
                
                if not (modifiers & QtCore.Qt.ControlModifier):
                    self.clear_selection()
                    
                # Start rubber band selection if in edit mode
                if self._edit_mode:
                    self._is_rubber_band_selecting = True
                    self.selection_manager.start_rubber_band_selection(scene_pos)
                    
                self.canvas_clicked.emit(scene_pos)
                event.accept()
                return
            else:
                # Item clicked
                modifiers = event.modifiers()
                
                if modifiers & QtCore.Qt.ControlModifier:
                    # Toggle selection
                    self.selection_manager.toggle_item_selection(item)
                else:
                    # Select item
                    if item not in self.get_selected_items():
                        self.selection_manager.select_item(item)
                        
        super(EnhancedCanvas, self).mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if self._is_panning:
            # Pan the view
            delta = event.pos() - self._last_pan_point
            self.viewport_manager.pan_manager.update_pan(
                self.mapToScene(event.pos())
            )
            self._last_pan_point = event.pos()
            event.accept()
            return
            
        elif self._is_rubber_band_selecting:
            # Update rubber band selection
            scene_pos = self.mapToScene(event.pos())
            self.selection_manager.update_rubber_band_selection(scene_pos)
            event.accept()
            return
            
        super(EnhancedCanvas, self).mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == QtCore.Qt.MiddleButton and self._is_panning:
            # End panning
            self._is_panning = False
            self.viewport_manager.pan_manager.end_pan()
            self.setCursor(QtCore.Qt.ArrowCursor if self._edit_mode else QtCore.Qt.PointingHandCursor)
            event.accept()
            return
            
        elif event.button() == QtCore.Qt.LeftButton and self._is_rubber_band_selecting:
            # End rubber band selection
            self._is_rubber_band_selecting = False
            scene_pos = self.mapToScene(event.pos())
            self.selection_manager.finish_rubber_band_selection(scene_pos)
            event.accept()
            return
            
        super(EnhancedCanvas, self).mouseReleaseEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        """Handle double click"""
        if event.button() == QtCore.Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            item = self.itemAt(event.pos())
            
            if not item:
                self.canvas_double_clicked.emit(scene_pos)
                
        super(EnhancedCanvas, self).mouseDoubleClickEvent(event)
        
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        if event.modifiers() & QtCore.Qt.ControlModifier:
            # Zoom with Ctrl+Wheel
            zoom_center = self.mapToScene(event.pos())
            zoom_delta = event.angleDelta().y()
            
            self.viewport_manager.zoom_at_point(zoom_delta, zoom_center)
            event.accept()
        else:
            # Pan with wheel
            delta = event.angleDelta()
            pan_delta = QtCore.QPointF(delta.x(), delta.y()) * 0.5
            current_pan = self.viewport_manager.pan_manager.get_pan_offset()
            new_pan = current_pan + pan_delta
            self.viewport_manager.pan_manager.set_pan_offset(new_pan)
            event.accept()
            
    def keyPressEvent(self, event):
        """Handle key press"""
        key = event.key()
        modifiers = event.modifiers()
        
        # Selection shortcuts
        if key == QtCore.Qt.Key_A and modifiers & QtCore.Qt.ControlModifier:
            self.select_all()
            event.accept()
            return
            
        # Copy/Paste shortcuts
        elif key == QtCore.Qt.Key_C and modifiers & QtCore.Qt.ControlModifier:
            self.copy_selected()
            event.accept()
            return
            
        elif key == QtCore.Qt.Key_V and modifiers & QtCore.Qt.ControlModifier:
            cursor_pos = self.mapFromGlobal(QtGui.QCursor.pos())
            scene_pos = self.mapToScene(cursor_pos)
            self.paste_items(scene_pos)
            event.accept()
            return
            
        # Delete shortcut
        elif key == QtCore.Qt.Key_Delete:
            self.delete_selected()
            event.accept()
            return
            
        # Navigation shortcuts
        elif key == QtCore.Qt.Key_F:
            self.zoom_fit()
            event.accept()
            return
            
        elif key == QtCore.Qt.Key_Home:
            self.reset_view()
            event.accept()
            return
            
        # Zoom shortcuts
        elif key == QtCore.Qt.Key_Plus and modifiers & QtCore.Qt.ControlModifier:
            self.zoom_in()
            event.accept()
            return
            
        elif key == QtCore.Qt.Key_Minus and modifiers & QtCore.Qt.ControlModifier:
            self.zoom_out()
            event.accept()
            return
            
        elif key == QtCore.Qt.Key_0 and modifiers & QtCore.Qt.ControlModifier:
            self.reset_zoom()
            event.accept()
            return
            
        super(EnhancedCanvas, self).keyPressEvent(event)
        
    def dragEnterEvent(self, event):
        """Handle drag enter"""
        if event.mimeData().hasText() or event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dragMoveEvent(self, event):
        """Handle drag move"""
        if event.mimeData().hasText() or event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        """Handle drop"""
        scene_pos = self.mapToScene(event.pos())
        
        if event.mimeData().hasText():
            # Handle text drop (could be JSON data for items)
            text = event.mimeData().text()
            try:
                import json
                data = json.loads(text)
                # Handle item data drop
                event.acceptProposedAction()
            except:
                event.ignore()
        elif event.mimeData().hasUrls():
            # Handle file drops
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.endswith('.json'):
                    # Load picker file
                    pass
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def drawForeground(self, painter, rect):
        """Draw foreground elements (grid, etc.)"""
        super(EnhancedCanvas, self).drawForeground(painter, rect)
        
        # Draw grid if visible
        if self._grid_visible:
            self._draw_grid(painter, rect)
            
        # Draw selection indicators
        self._draw_selection_indicators(painter, rect)
        
    def _draw_grid(self, painter, rect):
        """Draw grid lines"""
        transform = self.viewport_manager.get_viewport_transform()
        viewport_rect = QtCore.QRectF(self.viewport().rect())
        
        vertical_lines, horizontal_lines = self.grid_system.get_grid_lines(viewport_rect, transform)
        
        # Set grid pen
        grid_color = QtGui.QColor(68, 68, 68, 128)  # Semi-transparent gray
        grid_pen = QtGui.QPen(grid_color, 1, QtCore.Qt.DotLine)
        painter.setPen(grid_pen)
        
        # Draw vertical lines
        for start_point, end_point in vertical_lines:
            painter.drawLine(start_point, end_point)
            
        # Draw horizontal lines
        for start_point, end_point in horizontal_lines:
            painter.drawLine(start_point, end_point)
            
    def _draw_selection_indicators(self, painter, rect):
        """Draw additional selection indicators"""
        # This could draw additional selection UI elements
        pass
        
    def create_item(self, item_type, position=None):
        """Create new item of specified type"""
        if position is None:
            position = self.mapToScene(self.viewport().rect().center())
            
        # Import item classes as needed
        item = None
        
        try:
            if item_type == 'rectangle':
                from ..items.rectangle import RectangleItem
                item = RectangleItem()
            elif item_type == 'round_rectangle':
                from ..items.button import ButtonItem
                item = ButtonItem()
                item.set_shape('round_rectangle')
            elif item_type == 'circle':
                from ..items.button import ButtonItem  
                item = ButtonItem()
                item.set_shape('circle')
            elif item_type == 'polygon':
                from ..items.polygon import PolygonItem
                item = PolygonItem()
            elif item_type == 'checkbox':
                from ..items.checkbox import CheckboxItem
                item = CheckboxItem()
            elif item_type == 'slider':
                from ..items.slider import SliderItem
                item = SliderItem()
            elif item_type == 'radius_button':
                from ..items.radius_button import RadiusButtonItem
                item = RadiusButtonItem()
            elif item_type == 'pose_button':
                from ..items.pose_button import PoseButtonItem
                item = PoseButtonItem()
            elif item_type == 'text':
                from ..items.text_item import TextItem
                item = TextItem()
            else:
                print(f"Unknown item type: {item_type}")
                return None
                
            if item:
                self.add_item(item, position)
                # Select the new item
                self.clear_selection()
                self.selection_manager.select_item(item)
                
            return item
            
        except ImportError as e:
            print(f"Error creating item {item_type}: {e}")
            return None
            
    def get_canvas_info(self):
        """Get canvas information"""
        return {
            'total_items': len(self.get_all_items()),
            'selected_items': len(self.get_selected_items()),
            'zoom_factor': self.get_zoom_factor(),
            'edit_mode': self._edit_mode,
            'grid_visible': self._grid_visible,
            'grid_size': self.get_grid_size(),
            'snap_to_grid': self._snap_to_grid
        }
        
    def export_canvas_image(self, file_path, size=None):
        """Export canvas as image"""
        try:
            if size is None:
                # Use current viewport size
                size = self.viewport().size()
                
            # Create pixmap
            pixmap = QtGui.QPixmap(size)
            pixmap.fill(self.backgroundBrush().color())
            
            # Render scene
            painter = QtGui.QPainter(pixmap)
            self.render(painter)
            painter.end()
            
            # Save image
            return pixmap.save(file_path)
            
        except Exception as e:
            print(f"Error exporting canvas image: {e}")
            return False
