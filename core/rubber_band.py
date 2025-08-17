# File: core/rubber_band.py
"""
Rubber Band Selection for Ultimate Animation Picker
Provides visual selection rectangle and multi-select functionality
"""

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal

class RubberBandSelector(QtCore.QObject):
    """Handles rubber band selection on canvas"""
    
    # Signals
    selection_started = Signal(QtCore.QPoint)
    selection_updated = Signal(QtCore.QRect)
    selection_finished = Signal(QtCore.QRect)
    
    def __init__(self, parent_widget):
        super(RubberBandSelector, self).__init__()
        self.parent_widget = parent_widget
        self.rubber_band = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, parent_widget)
        self.start_point = QtCore.QPoint()
        self.is_selecting = False
        
        # Style the rubber band
        self.rubber_band.setStyleSheet("""
            QRubberBand {
                border: 2px dashed #4A90E2;
                background-color: rgba(74, 144, 226, 30);
            }
        """)
        
    def start_selection(self, point):
        """Start rubber band selection"""
        self.start_point = point
        self.is_selecting = True
        self.rubber_band.setGeometry(QtCore.QRect(point, QtCore.QSize()))
        self.rubber_band.show()
        self.selection_started.emit(point)
        
    def update_selection(self, point):
        """Update rubber band selection"""
        if not self.is_selecting:
            return
            
        rect = QtCore.QRect(self.start_point, point).normalized()
        self.rubber_band.setGeometry(rect)
        self.selection_updated.emit(rect)
        
    def finish_selection(self, point):
        """Finish rubber band selection"""
        if not self.is_selecting:
            return
            
        rect = QtCore.QRect(self.start_point, point).normalized()
        self.rubber_band.hide()
        self.is_selecting = False
        self.selection_finished.emit(rect)
        
    def cancel_selection(self):
        """Cancel current selection"""
        if self.is_selecting:
            self.rubber_band.hide()
            self.is_selecting = False
            
    def is_active(self):
        """Check if selection is active"""
        return self.is_selecting


class SelectionManager(QtCore.QObject):
    """Manages item selection with rubber band support"""
    
    # Signals
    selection_changed = Signal(list)  # List of selected items
    
    def __init__(self, canvas_widget):
        super(SelectionManager, self).__init__()
        self.canvas_widget = canvas_widget
        self.rubber_band = RubberBandSelector(canvas_widget)
        self.selected_items = []
        self.last_selected_item = None
        
        # Connect rubber band signals
        self.rubber_band.selection_finished.connect(self._on_rubber_band_selection)
        
    def select_item(self, item, multi_select=False):
        """Select a single item"""
        if not multi_select:
            self.clear_selection()
            
        if item not in self.selected_items:
            self.selected_items.append(item)
            item.set_selected(True)
            self.last_selected_item = item
            
        self.selection_changed.emit(self.selected_items[:])
        
    def deselect_item(self, item):
        """Deselect a single item"""
        if item in self.selected_items:
            self.selected_items.remove(item)
            item.set_selected(False)
            
            if self.last_selected_item == item:
                self.last_selected_item = self.selected_items[-1] if self.selected_items else None
                
        self.selection_changed.emit(self.selected_items[:])
        
    def toggle_item_selection(self, item):
        """Toggle item selection state"""
        if item in self.selected_items:
            self.deselect_item(item)
        else:
            self.select_item(item, multi_select=True)
            
    def select_items(self, items, multi_select=False):
        """Select multiple items"""
        if not multi_select:
            self.clear_selection()
            
        for item in items:
            if item not in self.selected_items:
                self.selected_items.append(item)
                item.set_selected(True)
                
        if items:
            self.last_selected_item = items[-1]
            
        self.selection_changed.emit(self.selected_items[:])
        
    def clear_selection(self):
        """Clear all selection"""
        for item in self.selected_items:
            item.set_selected(False)
            
        self.selected_items.clear()
        self.last_selected_item = None
        self.selection_changed.emit([])
        
    def get_selected_items(self):
        """Get list of selected items"""
        return self.selected_items[:]
        
    def get_last_selected_item(self):
        """Get the last selected item"""
        return self.last_selected_item
        
    def has_selection(self):
        """Check if any items are selected"""
        return len(self.selected_items) > 0
        
    def start_rubber_band_selection(self, point):
        """Start rubber band selection"""
        self.rubber_band.start_selection(point)
        
    def update_rubber_band_selection(self, point):
        """Update rubber band selection"""
        self.rubber_band.update_selection(point)
        
    def finish_rubber_band_selection(self, point):
        """Finish rubber band selection"""
        self.rubber_band.finish_selection(point)
        
    def cancel_rubber_band_selection(self):
        """Cancel rubber band selection"""
        self.rubber_band.cancel_selection()
        
    def is_rubber_band_active(self):
        """Check if rubber band selection is active"""
        return self.rubber_band.is_active()
        
    def _on_rubber_band_selection(self, rect):
        """Handle rubber band selection completion"""
        # Find items intersecting with selection rectangle
        intersecting_items = self._find_items_in_rect(rect)
        
        # Select intersecting items
        if intersecting_items:
            self.select_items(intersecting_items, multi_select=QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.ControlModifier)
        elif not (QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.ControlModifier):
            self.clear_selection()
            
    def _find_items_in_rect(self, rect):
        """Find items that intersect with the given rectangle"""
        intersecting_items = []
        
        # Get all items from the canvas
        if hasattr(self.canvas_widget, 'get_all_items'):
            all_items = self.canvas_widget.get_all_items()
            
            for item in all_items:
                if hasattr(item, 'get_bounding_rect'):
                    item_rect = item.get_bounding_rect()
                    if rect.intersects(item_rect):
                        intersecting_items.append(item)
                        
        return intersecting_items
        
    def select_all(self):
        """Select all items on canvas"""
        if hasattr(self.canvas_widget, 'get_all_items'):
            all_items = self.canvas_widget.get_all_items()
            self.select_items(all_items)
            
    def invert_selection(self):
        """Invert current selection"""
        if hasattr(self.canvas_widget, 'get_all_items'):
            all_items = self.canvas_widget.get_all_items()
            unselected_items = [item for item in all_items if item not in self.selected_items]
            
            self.clear_selection()
            self.select_items(unselected_items)


class SelectionBox(QtWidgets.QWidget):
    """Visual selection indicator for items"""
    
    def __init__(self, parent=None):
        super(SelectionBox, self).__init__(parent)
        self.setStyleSheet("""
            SelectionBox {
                border: 2px solid #4A90E2;
                background-color: transparent;
            }
        """)
        self.hide()
        
    def show_around_item(self, item):
        """Show selection box around an item"""
        if hasattr(item, 'get_bounding_rect'):
            rect = item.get_bounding_rect()
            # Expand rect slightly for visual padding
            expanded_rect = rect.adjusted(-2, -2, 2, 2)
            self.setGeometry(expanded_rect)
            self.show()
            self.raise_()
            
    def hide_selection(self):
        """Hide selection box"""
        self.hide()


class MultiSelectionIndicator(QtWidgets.QWidget):
    """Indicator for multiple selected items"""
    
    def __init__(self, parent=None):
        super(MultiSelectionIndicator, self).__init__(parent)
        self.selected_items = []
        self.selection_boxes = []
        
    def show_selection(self, items):
        """Show selection indicators for multiple items"""
        self.clear_selection_boxes()
        self.selected_items = items[:]
        
        for item in items:
            selection_box = SelectionBox(self.parent())
            selection_box.show_around_item(item)
            self.selection_boxes.append(selection_box)
            
    def clear_selection_boxes(self):
        """Clear all selection boxes"""
        for box in self.selection_boxes:
            box.deleteLater()
        self.selection_boxes.clear()
        self.selected_items.clear()
        
    def update_selection_boxes(self):
        """Update selection box positions"""
        for i, item in enumerate(self.selected_items):
            if i < len(self.selection_boxes):
                self.selection_boxes[i].show_around_item(item)
