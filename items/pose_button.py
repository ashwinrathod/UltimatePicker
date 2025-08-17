# File: items/pose_button.py
"""
Pose Button Item for Ultimate Animation Picker
Button with thumbnail capture and pose storage functionality
"""

import os
import json
import base64
from io import BytesIO
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore, QtGui
from .base_item import BasePickerItem

try:
    import shiboken2
except ImportError:
    import shiboken

class PoseButtonItem(BasePickerItem):
    """Pose button with thumbnail and pose storage"""
    
    # Signals
    pose_applied = QtCore.Signal(str)  # pose name
    thumbnail_captured = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(PoseButtonItem, self).__init__(parent)
        
        # Pose properties
        self._pose_name = "Pose"
        self._pose_data = {}
        self._thumbnail_data = None
        self._thumbnail_size = QtCore.QSize(64, 64)
        self._show_thumbnail = True
        
        # Visual properties
        self._thumbnail_border_color = QtCore.Qt.gray
        self._thumbnail_background_color = QtCore.Qt.lightGray
        
        # Size
        self._width = 80
        self._height = 80
        
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Connected objects for pose storage
        self._pose_objects = []
        
        # Default thumbnail (camera icon as fallback)
        self.create_default_thumbnail()
        
    def boundingRect(self):
        """Return bounding rectangle"""
        return QtCore.QRectF(0, 0, self._width, self._height)
        
    def paint(self, painter, option, widget):
        """Paint the pose button"""
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.boundingRect()
        
        # Draw button background
        painter.setBrush(self.get_current_brush())
        painter.setPen(self.get_current_pen())
        painter.drawRoundedRect(rect, 4, 4)
        
        # Draw thumbnail if available
        if self._show_thumbnail and self._thumbnail_data:
            self.draw_thumbnail(painter, rect)
        
        # Draw pose name text
        if self.text or self._pose_name:
            display_text = self.text if self.text else self._pose_name
            self.draw_pose_text(painter, rect, display_text)
            
    def draw_thumbnail(self, painter, rect):
        """Draw pose thumbnail"""
        # Calculate thumbnail rectangle (leave space for text)
        thumb_margin = 4
        text_height = 16
        thumb_rect = QtCore.QRectF(
            rect.x() + thumb_margin,
            rect.y() + thumb_margin,
            rect.width() - 2 * thumb_margin,
            rect.height() - text_height - 2 * thumb_margin
        )
        
        # Draw thumbnail border
        painter.setPen(QtGui.QPen(self._thumbnail_border_color, 1))
        painter.setBrush(QtGui.QBrush(self._thumbnail_background_color))
        painter.drawRect(thumb_rect)
        
        # Draw thumbnail image
        if self._thumbnail_data:
            try:
                # Convert base64 to QPixmap
                image_data = base64.b64decode(self._thumbnail_data)
                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(image_data)
                
                if not pixmap.isNull():
                    # Scale pixmap to fit thumbnail rect
                    scaled_pixmap = pixmap.scaled(
                        thumb_rect.size().toSize(),
                        QtCore.Qt.KeepAspectRatio,
                        QtCore.Qt.SmoothTransformation
                    )
                    
                    # Center the scaled pixmap
                    draw_rect = QtCore.QRectF(
                        thumb_rect.x() + (thumb_rect.width() - scaled_pixmap.width()) / 2,
                        thumb_rect.y() + (thumb_rect.height() - scaled_pixmap.height()) / 2,
                        scaled_pixmap.width(),
                        scaled_pixmap.height()
                    )
                    
                    painter.drawPixmap(draw_rect.toRect(), scaled_pixmap)
                    
            except Exception as e:
                # Draw fallback icon
                self.draw_fallback_icon(painter, thumb_rect)
        else:
            self.draw_fallback_icon(painter, thumb_rect)
            
    def draw_fallback_icon(self, painter, rect):
        """Draw fallback camera icon"""
        painter.setPen(QtGui.QPen(QtCore.Qt.darkGray, 2))
        painter.setBrush(QtCore.Qt.NoBrush)
        
        # Simple camera icon
        camera_rect = rect.adjusted(8, 8, -8, -8)
        painter.drawRoundedRect(camera_rect, 2, 2)
        
        # Camera lens
        lens_size = min(camera_rect.width(), camera_rect.height()) * 0.4
        lens_rect = QtCore.QRectF(
            camera_rect.center().x() - lens_size / 2,
            camera_rect.center().y() - lens_size / 2,
            lens_size,
            lens_size
        )
        painter.drawEllipse(lens_rect)
        
        # Camera flash
        flash_rect = QtCore.QRectF(
            camera_rect.x() + 4,
            camera_rect.y() + 2,
            4,
            3
        )
        painter.drawRect(flash_rect)
        
    def draw_pose_text(self, painter, rect, text):
        """Draw pose name text"""
        text_rect = QtCore.QRectF(
            rect.x() + 2,
            rect.bottom() - 16,
            rect.width() - 4,
            14
        )
        
        painter.setPen(self.text_color)
        font = QtGui.QFont(self.font_family, max(8, self.font_size - 2))
        font.setBold(self.font_bold)
        font.setItalic(self.font_italic)
        painter.setFont(font)
        
        # Elide text if too long
        metrics = painter.fontMetrics()
        elided_text = metrics.elidedText(text, QtCore.Qt.ElideRight, int(text_rect.width()))
        
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, elided_text)
        
    def create_default_thumbnail(self):
        """Create default thumbnail"""
        # Create a simple default thumbnail
        pixmap = QtGui.QPixmap(64, 64)
        pixmap.fill(QtCore.Qt.lightGray)
        
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtGui.QPen(QtCore.Qt.darkGray, 2))
        painter.drawRoundedRect(pixmap.rect().adjusted(4, 4, -4, -4), 4, 4)
        painter.end()
        
        # Convert to base64
        buffer = BytesIO()
        pixmap.save(buffer, "PNG")
        self._thumbnail_data = base64.b64encode(buffer.getvalue()).decode()
        
    def capture_maya_viewport_thumbnail(self, selection_only=False):
        """Capture thumbnail from Maya viewport"""
        try:
            # Get Maya's main window
            maya_window = omui.MQtUtil.mainWindow()
            if not maya_window:
                return False
                
            # Get active viewport
            current_panel = cmds.getPanel(withFocus=True)
            if not current_panel or not cmds.getPanel(typeOf=current_panel) == 'modelPanel':
                current_panel = cmds.getPanel(type='modelPanel')[0]
                
            # Capture viewport
            temp_file = os.path.join(cmds.internalVar(userTmpDir=True), "picker_thumbnail.png")
            
            # Set capture options
            cmds.playblast(
                frame=cmds.currentTime(query=True),
                format='image',
                filename=temp_file,
                widthHeight=[self._thumbnail_size.width(), self._thumbnail_size.height()],
                percent=100,
                quality=70,
                viewer=False,
                showOrnaments=False,
                compression='png'
            )
            
            # Load captured image
            if os.path.exists(temp_file + ".png"):
                pixmap = QtGui.QPixmap(temp_file + ".png")
                
                if not pixmap.isNull():
                    # Convert to base64
                    buffer = BytesIO()
                    pixmap.save(buffer, "PNG")
                    self._thumbnail_data = base64.b64encode(buffer.getvalue()).decode()
                    
                    # Clean up temp file
                    try:
                        os.remove(temp_file + ".png")
                    except:
                        pass
                        
                    self.update()
                    self.thumbnail_captured.emit()
                    return True
                    
        except Exception as e:
            print(f"Error capturing Maya viewport thumbnail: {e}")
            
        return False
        
    def capture_custom_thumbnail(self, pixmap):
        """Set custom thumbnail from QPixmap"""
        if pixmap and not pixmap.isNull():
            # Scale to thumbnail size
            scaled_pixmap = pixmap.scaled(
                self._thumbnail_size,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            
            # Convert to base64
            buffer = BytesIO()
            scaled_pixmap.save(buffer, "PNG")
            self._thumbnail_data = base64.b64encode(buffer.getvalue()).decode()
            
            self.update()
            self.thumbnail_captured.emit()
            return True
            
        return False
        
    def store_current_pose(self, objects=None):
        """Store current pose from selected objects"""
        if objects is None:
            objects = cmds.ls(selection=True)
            
        if not objects:
            print("No objects selected for pose storage")
            return False
            
        self._pose_objects = objects
        pose_data = {}
        
        for obj in objects:
            # Get all keyable attributes
            attrs = cmds.listAttr(obj, keyable=True) or []
            pose_data[obj] = {}
            
            for attr in attrs:
                try:
                    value = cmds.getAttr(f"{obj}.{attr}")
                    pose_data[obj][attr] = value
                except:
                    continue
                    
        self._pose_data = pose_data
        return True
        
    def apply_stored_pose(self, objects=None):
        """Apply stored pose to objects"""
        if not self._pose_data:
            print(f"No pose data stored in {self._pose_name}")
            return False
            
        if objects is None:
            objects = cmds.ls(selection=True) if cmds.ls(selection=True) else self._pose_objects
            
        if not objects:
            print("No objects selected for pose application")
            return False
            
        applied_count = 0
        
        for obj in objects:
            if obj in self._pose_data:
                for attr, value in self._pose_data[obj].items():
                    try:
                        cmds.setAttr(f"{obj}.{attr}", value)
                        applied_count += 1
                    except Exception as e:
                        print(f"Failed to set {obj}.{attr}: {e}")
                        
        self.pose_applied.emit(self._pose_name)
        print(f"Applied pose '{self._pose_name}' to {len(objects)} objects ({applied_count} attributes)")
        return applied_count > 0
        
    def set_pose_name(self, name):
        """Set pose name"""
        self._pose_name = name
        self.update()
        
    def get_pose_name(self):
        """Get pose name"""
        return self._pose_name
        
    def set_thumbnail_size(self, size):
        """Set thumbnail size"""
        self._thumbnail_size = size
        self.update()
        
    def get_thumbnail_size(self):
        """Get thumbnail size"""
        return self._thumbnail_size
        
    def set_show_thumbnail(self, show):
        """Set whether to show thumbnail"""
        self._show_thumbnail = show
        self.update()
        
    def has_pose_data(self):
        """Check if pose has stored data"""
        return bool(self._pose_data)
        
    def has_thumbnail(self):
        """Check if pose has thumbnail"""
        return bool(self._thumbnail_data)
        
    def clear_pose_data(self):
        """Clear stored pose data"""
        self._pose_data = {}
        
    def clear_thumbnail(self):
        """Clear thumbnail"""
        self._thumbnail_data = None
        self.create_default_thumbnail()
        self.update()
        
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == QtCore.Qt.LeftButton:
            # Apply pose on left click
            self.apply_stored_pose()
            event.accept()
        elif event.button() == QtCore.Qt.RightButton:
            # Show context menu
            self.show_context_menu(event.screenPos())
            event.accept()
        else:
            super(PoseButtonItem, self).mousePressEvent(event)
            
    def mouseDoubleClickEvent(self, event):
        """Handle double click to store pose"""
        if event.button() == QtCore.Qt.LeftButton:
            self.store_current_pose()
            event.accept()
        else:
            super(PoseButtonItem, self).mouseDoubleClickEvent(event)
            
    def show_context_menu(self, global_pos):
        """Show context menu for pose operations"""
        menu = QtWidgets.QMenu()
        
        # Store current pose
        store_action = menu.addAction("Store Current Pose")
        store_action.triggered.connect(lambda: self.store_current_pose())
        
        # Apply pose
        apply_action = menu.addAction("Apply Pose")
        apply_action.setEnabled(self.has_pose_data())
        apply_action.triggered.connect(lambda: self.apply_stored_pose())
        
        menu.addSeparator()
        
        # Capture thumbnail
        capture_viewport_action = menu.addAction("Capture Viewport Thumbnail")
        capture_viewport_action.triggered.connect(lambda: self.capture_maya_viewport_thumbnail())
        
        # Clear thumbnail
        clear_thumb_action = menu.addAction("Clear Thumbnail")
        clear_thumb_action.setEnabled(self.has_thumbnail())
        clear_thumb_action.triggered.connect(self.clear_thumbnail)
        
        menu.addSeparator()
        
        # Export/Import pose
        export_action = menu.addAction("Export Pose...")
        export_action.setEnabled(self.has_pose_data())
        export_action.triggered.connect(self.export_pose)
        
        import_action = menu.addAction("Import Pose...")
        import_action.triggered.connect(self.import_pose)
        
        menu.exec_(global_pos.toPoint())
        
    def export_pose(self):
        """Export pose data to file"""
        if not self.has_pose_data():
            return
            
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            None,
            "Export Pose",
            f"{self._pose_name}.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                export_data = {
                    'pose_name': self._pose_name,
                    'pose_data': self._pose_data,
                    'thumbnail_data': self._thumbnail_data,
                    'pose_objects': self._pose_objects
                }
                
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                    
                print(f"Pose exported to {file_path}")
                
            except Exception as e:
                print(f"Error exporting pose: {e}")
                
    def import_pose(self):
        """Import pose data from file"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Import Pose",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    import_data = json.load(f)
                    
                self._pose_name = import_data.get('pose_name', self._pose_name)
                self._pose_data = import_data.get('pose_data', {})
                self._thumbnail_data = import_data.get('thumbnail_data')
                self._pose_objects = import_data.get('pose_objects', [])
                
                self.update()
                print(f"Pose imported from {file_path}")
                
            except Exception as e:
                print(f"Error importing pose: {e}")
                
    def to_dict(self):
        """Serialize to dictionary"""
        data = super(PoseButtonItem, self).to_dict()
        data.update({
            'pose_name': self._pose_name,
            'pose_data': self._pose_data,
            'thumbnail_data': self._thumbnail_data,
            'thumbnail_size': (self._thumbnail_size.width(), self._thumbnail_size.height()),
            'show_thumbnail': self._show_thumbnail,
            'pose_objects': self._pose_objects
        })
        return data
        
    def from_dict(self, data):
        """Deserialize from dictionary"""
        super(PoseButtonItem, self).from_dict(data)
        
        self._pose_name = data.get('pose_name', 'Pose')
        self._pose_data = data.get('pose_data', {})
        self._thumbnail_data = data.get('thumbnail_data')
        self._show_thumbnail = data.get('show_thumbnail', True)
        self._pose_objects = data.get('pose_objects', [])
        
        if 'thumbnail_size' in data:
            w, h = data['thumbnail_size']
            self._thumbnail_size = QtCore.QSize(w, h)
