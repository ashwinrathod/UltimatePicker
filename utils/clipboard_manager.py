# File: utils/clipboard_manager.py
"""
Clipboard Manager for Ultimate Animation Picker
Handles copy/paste operations for items and styles
"""

import json
import copy
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Signal

class ClipboardData:
    """Container for clipboard data"""
    
    TYPE_ITEMS = "items"
    TYPE_STYLE = "style"
    TYPE_POSE = "pose"
    TYPE_ANIMATION = "animation"
    
    def __init__(self, data_type, data, metadata=None):
        self.data_type = data_type
        self.data = data
        self.metadata = metadata or {}
        self.timestamp = QtCore.QDateTime.currentDateTime()
        
    def is_valid(self):
        """Check if clipboard data is valid"""
        return self.data_type and self.data is not None
        
    def get_age_seconds(self):
        """Get age of clipboard data in seconds"""
        return self.timestamp.secsTo(QtCore.QDateTime.currentDateTime())


class ClipboardManager(QtCore.QObject):
    """Manages clipboard operations for picker items"""
    
    # Signals
    data_copied = Signal(str)  # data_type
    data_pasted = Signal(str, int)  # data_type, item_count
    clipboard_changed = Signal(bool)  # has_data
    
    def __init__(self, parent=None):
        super(ClipboardManager, self).__init__(parent)
        self._clipboard_data = None
        self._system_clipboard = QtWidgets.QApplication.clipboard()
        self._max_age_hours = 24  # Maximum age for clipboard data
        
    def copy_items(self, items):
        """Copy items to clipboard"""
        if not items:
            return False
            
        try:
            # Serialize items
            items_data = []
            for item in items:
                if hasattr(item, 'to_dict'):
                    item_data = item.to_dict()
                    # Store position relative to first item
                    if items_data:
                        first_pos = items_data[0].get('position', (0, 0))
                        current_pos = item_data.get('position', (0, 0))
                        relative_pos = (
                            current_pos[0] - first_pos[0],
                            current_pos[1] - first_pos[1]
                        )
                        item_data['relative_position'] = relative_pos
                    else:
                        item_data['relative_position'] = (0, 0)
                        
                    items_data.append(item_data)
                    
            if items_data:
                metadata = {
                    'count': len(items_data),
                    'types': [item.get('type', 'unknown') for item in items_data]
                }
                
                self._clipboard_data = ClipboardData(
                    ClipboardData.TYPE_ITEMS,
                    items_data,
                    metadata
                )
                
                # Also copy to system clipboard as JSON
                json_data = json.dumps(items_data, indent=2)
                self._system_clipboard.setText(json_data)
                
                self.data_copied.emit(ClipboardData.TYPE_ITEMS)
                self.clipboard_changed.emit(True)
                return True
                
        except Exception as e:
            print(f"Error copying items: {e}")
            
        return False
        
    def paste_items(self, target_position=None, parent_widget=None):
        """Paste items from clipboard"""
        if not self.has_items():
            return []
            
        try:
            items_data = self._clipboard_data.data
            pasted_items = []
            
            # Calculate paste position
            if target_position is None:
                target_position = QtCore.QPointF(0, 0)
                
            # Create items from data
            for item_data in items_data:
                # Calculate final position
                relative_pos = item_data.get('relative_position', (0, 0))
                final_position = QtCore.QPointF(
                    target_position.x() + relative_pos[0],
                    target_position.y() + relative_pos[1]
                )
                
                # Update position in data
                item_data_copy = copy.deepcopy(item_data)
                item_data_copy['position'] = (final_position.x(), final_position.y())
                
                # Create item based on type
                item = self._create_item_from_data(item_data_copy, parent_widget)
                if item:
                    pasted_items.append(item)
                    
            if pasted_items:
                self.data_pasted.emit(ClipboardData.TYPE_ITEMS, len(pasted_items))
                
            return pasted_items
            
        except Exception as e:
            print(f"Error pasting items: {e}")
            
        return []
        
    def copy_style(self, item):
        """Copy item style to clipboard"""
        if not item or not hasattr(item, 'to_dict'):
            return False
            
        try:
            item_data = item.to_dict()
            
            # Extract style-related properties
            style_data = {}
            style_properties = [
                'bg_color', 'bg_hover_color', 'bg_click_color',
                'pen_color', 'pen_hover_color', 'pen_click_color',
                'pen_width', 'text_color', 'text_hover_color', 'text_click_color',
                'font_family', 'font_size', 'font_bold', 'font_italic',
                'opacity', 'border_radius'
            ]
            
            for prop in style_properties:
                if prop in item_data:
                    style_data[prop] = item_data[prop]
                    
            if style_data:
                metadata = {
                    'source_type': item_data.get('type', 'unknown'),
                    'property_count': len(style_data)
                }
                
                self._clipboard_data = ClipboardData(
                    ClipboardData.TYPE_STYLE,
                    style_data,
                    metadata
                )
                
                self.data_copied.emit(ClipboardData.TYPE_STYLE)
                self.clipboard_changed.emit(True)
                return True
                
        except Exception as e:
            print(f"Error copying style: {e}")
            
        return False
        
    def paste_style(self, items):
        """Paste style to items"""
        if not self.has_style() or not items:
            return False
            
        try:
            style_data = self._clipboard_data.data
            applied_count = 0
            
            for item in items:
                if hasattr(item, 'from_dict'):
                    # Apply style properties to item
                    for prop, value in style_data.items():
                        if hasattr(item, prop):
                            setattr(item, prop, value)
                        elif hasattr(item, f'_{prop}'):
                            setattr(item, f'_{prop}', value)
                            
                    # Update item display
                    if hasattr(item, 'update'):
                        item.update()
                        
                    applied_count += 1
                    
            if applied_count > 0:
                self.data_pasted.emit(ClipboardData.TYPE_STYLE, applied_count)
                return True
                
        except Exception as e:
            print(f"Error pasting style: {e}")
            
        return False
        
    def copy_pose(self, pose_data, pose_name="Copied Pose"):
        """Copy pose data to clipboard"""
        try:
            metadata = {
                'pose_name': pose_name,
                'object_count': len(pose_data) if isinstance(pose_data, dict) else 0
            }
            
            self._clipboard_data = ClipboardData(
                ClipboardData.TYPE_POSE,
                pose_data,
                metadata
            )
            
            self.data_copied.emit(ClipboardData.TYPE_POSE)
            self.clipboard_changed.emit(True)
            return True
            
        except Exception as e:
            print(f"Error copying pose: {e}")
            
        return False
        
    def paste_pose(self):
        """Get pose data from clipboard"""
        if self.has_pose():
            return self._clipboard_data.data
        return None
        
    def copy_animation(self, animation_data, time_range, anim_name="Copied Animation"):
        """Copy animation data to clipboard"""
        try:
            metadata = {
                'animation_name': anim_name,
                'time_range': time_range,
                'object_count': len(animation_data) if isinstance(animation_data, dict) else 0
            }
            
            self._clipboard_data = ClipboardData(
                ClipboardData.TYPE_ANIMATION,
                animation_data,
                metadata
            )
            
            self.data_copied.emit(ClipboardData.TYPE_ANIMATION)
            self.clipboard_changed.emit(True)
            return True
            
        except Exception as e:
            print(f"Error copying animation: {e}")
            
        return False
        
    def paste_animation(self):
        """Get animation data from clipboard"""
        if self.has_animation():
            return self._clipboard_data.data, self._clipboard_data.metadata
        return None, None
        
    def has_data(self):
        """Check if clipboard has any data"""
        return (self._clipboard_data and 
                self._clipboard_data.is_valid() and
                self._clipboard_data.get_age_seconds() < self._max_age_hours * 3600)
                
    def has_items(self):
        """Check if clipboard has items"""
        return (self.has_data() and 
                self._clipboard_data.data_type == ClipboardData.TYPE_ITEMS)
                
    def has_style(self):
        """Check if clipboard has style data"""
        return (self.has_data() and 
                self._clipboard_data.data_type == ClipboardData.TYPE_STYLE)
                
    def has_pose(self):
        """Check if clipboard has pose data"""
        return (self.has_data() and 
                self._clipboard_data.data_type == ClipboardData.TYPE_POSE)
                
    def has_animation(self):
        """Check if clipboard has animation data"""
        return (self.has_data() and 
                self._clipboard_data.data_type == ClipboardData.TYPE_ANIMATION)
                
    def get_clipboard_info(self):
        """Get information about clipboard contents"""
        if not self.has_data():
            return "Clipboard is empty"
            
        data_type = self._clipboard_data.data_type
        metadata = self._clipboard_data.metadata
        age_minutes = self._clipboard_data.get_age_seconds() // 60
        
        info_parts = [f"Type: {data_type}"]
        
        if data_type == ClipboardData.TYPE_ITEMS:
            count = metadata.get('count', 0)
            types = metadata.get('types', [])
            info_parts.append(f"Items: {count}")
            if types:
                unique_types = list(set(types))
                info_parts.append(f"Types: {', '.join(unique_types)}")
                
        elif data_type == ClipboardData.TYPE_STYLE:
            prop_count = metadata.get('property_count', 0)
            source_type = metadata.get('source_type', 'unknown')
            info_parts.append(f"Properties: {prop_count}")
            info_parts.append(f"From: {source_type}")
            
        elif data_type == ClipboardData.TYPE_POSE:
            pose_name = metadata.get('pose_name', 'Unknown')
            obj_count = metadata.get('object_count', 0)
            info_parts.append(f"Pose: {pose_name}")
            info_parts.append(f"Objects: {obj_count}")
            
        elif data_type == ClipboardData.TYPE_ANIMATION:
            anim_name = metadata.get('animation_name', 'Unknown')
            time_range = metadata.get('time_range', (0, 0))
            obj_count = metadata.get('object_count', 0)
            info_parts.append(f"Animation: {anim_name}")
            info_parts.append(f"Frames: {time_range[0]}-{time_range[1]}")
            info_parts.append(f"Objects: {obj_count}")
            
        info_parts.append(f"Age: {age_minutes}m")
        
        return " | ".join(info_parts)
        
    def clear_clipboard(self):
        """Clear clipboard data"""
        self._clipboard_data = None
        self.clipboard_changed.emit(False)
        
    def import_from_system_clipboard(self):
        """Import data from system clipboard"""
        try:
            text_data = self._system_clipboard.text()
            if text_data:
                # Try to parse as JSON
                import_data = json.loads(text_data)
                
                # Determine data type
                if isinstance(import_data, list) and import_data:
                    # Assume it's items data
                    metadata = {
                        'count': len(import_data),
                        'imported': True
                    }
                    
                    self._clipboard_data = ClipboardData(
                        ClipboardData.TYPE_ITEMS,
                        import_data,
                        metadata
                    )
                    
                    self.clipboard_changed.emit(True)
                    return True
                    
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error importing from system clipboard: {e}")
            
        return False
        
    def _create_item_from_data(self, item_data, parent_widget):
        """Create item instance from serialized data"""
        item_type = item_data.get('type', 'unknown')
        
        # Import item classes with fallback for different import contexts
        try:
            if item_type == 'RectangleItem':
                try:
                    from ..items.rectangle import RectangleItem
                except ImportError:
                    from items.rectangle import RectangleItem
                item = RectangleItem()
            elif item_type == 'ButtonItem':
                try:
                    from ..items.button import ButtonItem
                except ImportError:
                    from items.button import ButtonItem
                item = ButtonItem()
            elif item_type == 'PolygonItem':
                try:
                    from ..items.polygon import PolygonItem
                except ImportError:
                    from items.polygon import PolygonItem
                item = PolygonItem()
            elif item_type == 'SliderItem':
                try:
                    from ..items.slider import SliderItem
                except ImportError:
                    from items.slider import SliderItem
                item = SliderItem()
            elif item_type == 'CheckboxItem':
                try:
                    from ..items.checkbox import CheckboxItem
                except ImportError:
                    from items.checkbox import CheckboxItem
                item = CheckboxItem()
            elif item_type == 'RadiusButtonItem':
                try:
                    from ..items.radius_button import RadiusButtonItem
                except ImportError:
                    from items.radius_button import RadiusButtonItem
                item = RadiusButtonItem()
            elif item_type == 'PoseButtonItem':
                try:
                    from ..items.pose_button import PoseButtonItem
                except ImportError:
                    from items.pose_button import PoseButtonItem
                item = PoseButtonItem()
            elif item_type == 'TextItem':
                try:
                    from ..items.text_item import TextItem
                except ImportError:
                    from items.text_item import TextItem
                item = TextItem()
            else:
                print(f"Unknown item type: {item_type}")
                return None
                
            # Restore item data
            if hasattr(item, 'from_dict'):
                item.from_dict(item_data)
                
            return item
            
        except Exception as e:
            print(f"Error creating item from data: {e}")
            
        return None


class ClipboardHistory(QtCore.QObject):
    """Manages clipboard history"""
    
    def __init__(self, max_history=10, parent=None):
        super(ClipboardHistory, self).__init__(parent)
        self._history = []
        self._max_history = max_history
        self._current_index = -1
        
    def add_to_history(self, clipboard_data):
        """Add clipboard data to history"""
        # Remove any items after current index (when navigating back)
        if self._current_index < len(self._history) - 1:
            self._history = self._history[:self._current_index + 1]
            
        # Add new item
        self._history.append(clipboard_data)
        
        # Trim history if too long
        if len(self._history) > self._max_history:
            self._history.pop(0)
        else:
            self._current_index += 1
            
        # Set current index to latest
        self._current_index = len(self._history) - 1
        
    def get_previous(self):
        """Get previous clipboard data"""
        if self._current_index > 0:
            self._current_index -= 1
            return self._history[self._current_index]
        return None
        
    def get_next(self):
        """Get next clipboard data"""
        if self._current_index < len(self._history) - 1:
            self._current_index += 1
            return self._history[self._current_index]
        return None
        
    def get_current(self):
        """Get current clipboard data"""
        if 0 <= self._current_index < len(self._history):
            return self._history[self._current_index]
        return None
        
    def get_history_list(self):
        """Get list of history items with descriptions"""
        history_list = []
        for i, data in enumerate(self._history):
            description = f"{data.data_type}"
            if data.metadata:
                if 'count' in data.metadata:
                    description += f" ({data.metadata['count']} items)"
                elif 'pose_name' in data.metadata:
                    description += f" ({data.metadata['pose_name']})"
                    
            age_minutes = data.get_age_seconds() // 60
            description += f" - {age_minutes}m ago"
            
            history_list.append({
                'index': i,
                'description': description,
                'is_current': i == self._current_index,
                'data': data
            })
            
        return history_list
        
    def clear_history(self):
        """Clear clipboard history"""
        self._history.clear()
        self._current_index = -1


# Global clipboard manager instance
_clipboard_manager = None

def get_clipboard_manager():
    """Get global clipboard manager instance"""
    global _clipboard_manager
    if _clipboard_manager is None:
        _clipboard_manager = ClipboardManager()
    return _clipboard_manager
