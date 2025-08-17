# File: core/alignment_tools.py
"""
Alignment Tools for Ultimate Animation Picker
Provides item alignment functionality (left, right, center, top, bottom, middle)
"""

from PySide2 import QtCore, QtGui
import math

class AlignmentTools:
    """Static methods for aligning picker items"""
    
    @staticmethod
    def align_left(items):
        """Align items to the left edge"""
        if len(items) < 2:
            return
            
        # Find leftmost position
        left_pos = min(item.pos().x() for item in items if hasattr(item, 'pos'))
        
        # Align all items to left position
        for item in items:
            if hasattr(item, 'setPos'):
                current_pos = item.pos()
                item.setPos(left_pos, current_pos.y())
                
    @staticmethod
    def align_right(items):
        """Align items to the right edge"""
        if len(items) < 2:
            return
            
        # Find rightmost position
        right_pos = max(item.pos().x() + item.boundingRect().width() 
                       for item in items if hasattr(item, 'pos') and hasattr(item, 'boundingRect'))
        
        # Align all items to right position
        for item in items:
            if hasattr(item, 'setPos') and hasattr(item, 'boundingRect'):
                current_pos = item.pos()
                new_x = right_pos - item.boundingRect().width()
                item.setPos(new_x, current_pos.y())
                
    @staticmethod
    def align_center_horizontal(items):
        """Align items to horizontal center"""
        if len(items) < 2:
            return
            
        # Calculate center position
        left_pos = min(item.pos().x() for item in items if hasattr(item, 'pos'))
        right_pos = max(item.pos().x() + item.boundingRect().width() 
                       for item in items if hasattr(item, 'pos') and hasattr(item, 'boundingRect'))
        center_x = (left_pos + right_pos) / 2.0
        
        # Align all items to center
        for item in items:
            if hasattr(item, 'setPos') and hasattr(item, 'boundingRect'):
                current_pos = item.pos()
                new_x = center_x - item.boundingRect().width() / 2.0
                item.setPos(new_x, current_pos.y())
                
    @staticmethod
    def align_top(items):
        """Align items to the top edge"""
        if len(items) < 2:
            return
            
        # Find topmost position
        top_pos = min(item.pos().y() for item in items if hasattr(item, 'pos'))
        
        # Align all items to top position
        for item in items:
            if hasattr(item, 'setPos'):
                current_pos = item.pos()
                item.setPos(current_pos.x(), top_pos)
                
    @staticmethod
    def align_bottom(items):
        """Align items to the bottom edge"""
        if len(items) < 2:
            return
            
        # Find bottommost position
        bottom_pos = max(item.pos().y() + item.boundingRect().height() 
                        for item in items if hasattr(item, 'pos') and hasattr(item, 'boundingRect'))
        
        # Align all items to bottom position
        for item in items:
            if hasattr(item, 'setPos') and hasattr(item, 'boundingRect'):
                current_pos = item.pos()
                new_y = bottom_pos - item.boundingRect().height()
                item.setPos(current_pos.x(), new_y)
                
    @staticmethod
    def align_middle_vertical(items):
        """Align items to vertical middle"""
        if len(items) < 2:
            return
            
        # Calculate middle position
        top_pos = min(item.pos().y() for item in items if hasattr(item, 'pos'))
        bottom_pos = max(item.pos().y() + item.boundingRect().height() 
                        for item in items if hasattr(item, 'pos') and hasattr(item, 'boundingRect'))
        middle_y = (top_pos + bottom_pos) / 2.0
        
        # Align all items to middle
        for item in items:
            if hasattr(item, 'setPos') and hasattr(item, 'boundingRect'):
                current_pos = item.pos()
                new_y = middle_y - item.boundingRect().height() / 2.0
                item.setPos(current_pos.x(), new_y)
                
    @staticmethod
    def distribute_horizontal(items):
        """Distribute items evenly horizontally"""
        if len(items) < 3:
            return
            
        # Sort items by x position
        sorted_items = sorted(items, key=lambda item: item.pos().x() if hasattr(item, 'pos') else 0)
        
        if len(sorted_items) < 3:
            return
            
        # Get leftmost and rightmost positions
        left_item = sorted_items[0]
        right_item = sorted_items[-1]
        
        left_pos = left_item.pos().x()
        right_pos = right_item.pos().x()
        
        # Calculate spacing
        total_width = right_pos - left_pos
        spacing = total_width / (len(sorted_items) - 1)
        
        # Distribute items
        for i, item in enumerate(sorted_items[1:-1], 1):
            if hasattr(item, 'setPos'):
                current_pos = item.pos()
                new_x = left_pos + spacing * i
                item.setPos(new_x, current_pos.y())
                
    @staticmethod
    def distribute_vertical(items):
        """Distribute items evenly vertically"""
        if len(items) < 3:
            return
            
        # Sort items by y position
        sorted_items = sorted(items, key=lambda item: item.pos().y() if hasattr(item, 'pos') else 0)
        
        if len(sorted_items) < 3:
            return
            
        # Get topmost and bottommost positions
        top_item = sorted_items[0]
        bottom_item = sorted_items[-1]
        
        top_pos = top_item.pos().y()
        bottom_pos = bottom_item.pos().y()
        
        # Calculate spacing
        total_height = bottom_pos - top_pos
        spacing = total_height / (len(sorted_items) - 1)
        
        # Distribute items
        for i, item in enumerate(sorted_items[1:-1], 1):
            if hasattr(item, 'setPos'):
                current_pos = item.pos()
                new_y = top_pos + spacing * i
                item.setPos(current_pos.x(), new_y)
                
    @staticmethod
    def match_width(items, reference_item=None):
        """Match width of all items to reference item or first selected"""
        if len(items) < 2:
            return
            
        if reference_item is None:
            reference_item = items[0]
            
        if not hasattr(reference_item, 'boundingRect'):
            return
            
        reference_width = reference_item.boundingRect().width()
        
        for item in items:
            if item != reference_item and hasattr(item, 'resize'):
                current_size = item.size() if hasattr(item, 'size') else item.boundingRect().size()
                item.resize(reference_width, current_size.height())
                
    @staticmethod
    def match_height(items, reference_item=None):
        """Match height of all items to reference item or first selected"""
        if len(items) < 2:
            return
            
        if reference_item is None:
            reference_item = items[0]
            
        if not hasattr(reference_item, 'boundingRect'):
            return
            
        reference_height = reference_item.boundingRect().height()
        
        for item in items:
            if item != reference_item and hasattr(item, 'resize'):
                current_size = item.size() if hasattr(item, 'size') else item.boundingRect().size()
                item.resize(current_size.width(), reference_height)
                
    @staticmethod
    def match_size(items, reference_item=None):
        """Match size of all items to reference item or first selected"""
        if len(items) < 2:
            return
            
        if reference_item is None:
            reference_item = items[0]
            
        if not hasattr(reference_item, 'boundingRect'):
            return
            
        reference_size = reference_item.boundingRect().size()
        
        for item in items:
            if item != reference_item and hasattr(item, 'resize'):
                item.resize(reference_size.width(), reference_size.height())
                
    @staticmethod
    def space_evenly_horizontal(items, spacing=10):
        """Space items evenly with fixed horizontal spacing"""
        if len(items) < 2:
            return
            
        # Sort items by x position
        sorted_items = sorted(items, key=lambda item: item.pos().x() if hasattr(item, 'pos') else 0)
        
        # Position items with fixed spacing
        current_x = sorted_items[0].pos().x() if hasattr(sorted_items[0], 'pos') else 0
        
        for i, item in enumerate(sorted_items):
            if hasattr(item, 'setPos') and hasattr(item, 'boundingRect'):
                if i > 0:
                    current_x += sorted_items[i-1].boundingRect().width() + spacing
                current_pos = item.pos()
                item.setPos(current_x, current_pos.y())
                
    @staticmethod
    def space_evenly_vertical(items, spacing=10):
        """Space items evenly with fixed vertical spacing"""
        if len(items) < 2:
            return
            
        # Sort items by y position
        sorted_items = sorted(items, key=lambda item: item.pos().y() if hasattr(item, 'pos') else 0)
        
        # Position items with fixed spacing
        current_y = sorted_items[0].pos().y() if hasattr(sorted_items[0], 'pos') else 0
        
        for i, item in enumerate(sorted_items):
            if hasattr(item, 'setPos') and hasattr(item, 'boundingRect'):
                if i > 0:
                    current_y += sorted_items[i-1].boundingRect().height() + spacing
                current_pos = item.pos()
                item.setPos(current_pos.x(), current_y)
                
    @staticmethod
    def create_grid_layout(items, columns=3, spacing=10):
        """Arrange items in a grid layout"""
        if not items:
            return
            
        if len(items) == 1:
            return
            
        # Calculate grid dimensions
        rows = math.ceil(len(items) / columns)
        
        # Find starting position (top-left item)
        start_x = min(item.pos().x() for item in items if hasattr(item, 'pos'))
        start_y = min(item.pos().y() for item in items if hasattr(item, 'pos'))
        
        # Calculate cell size (use largest item dimensions)
        cell_width = max(item.boundingRect().width() for item in items 
                        if hasattr(item, 'boundingRect')) + spacing
        cell_height = max(item.boundingRect().height() for item in items 
                         if hasattr(item, 'boundingRect')) + spacing
        
        # Position items in grid
        for i, item in enumerate(items):
            if hasattr(item, 'setPos'):
                row = i // columns
                col = i % columns
                
                new_x = start_x + col * cell_width
                new_y = start_y + row * cell_height
                
                item.setPos(new_x, new_y)
                
    @staticmethod
    def arrange_in_circle(items, radius=100, center=None):
        """Arrange items in a circle"""
        if len(items) < 2:
            return
            
        if center is None:
            # Calculate center from current positions
            center_x = sum(item.pos().x() for item in items if hasattr(item, 'pos')) / len(items)
            center_y = sum(item.pos().y() for item in items if hasattr(item, 'pos')) / len(items)
            center = QtCore.QPointF(center_x, center_y)
            
        angle_step = 360.0 / len(items)
        
        for i, item in enumerate(items):
            if hasattr(item, 'setPos'):
                angle = math.radians(i * angle_step)
                x = center.x() + radius * math.cos(angle)
                y = center.y() + radius * math.sin(angle)
                item.setPos(x, y)
                
    @staticmethod
    def snap_to_grid(items, grid_size=10):
        """Snap items to grid"""
        for item in items:
            if hasattr(item, 'pos') and hasattr(item, 'setPos'):
                current_pos = item.pos()
                snapped_x = round(current_pos.x() / grid_size) * grid_size
                snapped_y = round(current_pos.y() / grid_size) * grid_size
                item.setPos(snapped_x, snapped_y)
