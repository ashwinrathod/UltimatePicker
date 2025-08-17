# File: ui/thumbnail_capture.py
"""
Thumbnail Capture System for Ultimate Animation Picker
Captures Maya viewport thumbnails for pose buttons and other items
"""

import os
import tempfile
import base64
from io import BytesIO
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal

try:
    import shiboken2
except ImportError:
    import shiboken

class ThumbnailCapture(QtCore.QObject):
    """Maya viewport thumbnail capture system"""
    
    # Signals
    capture_completed = Signal(str)  # base64 encoded image data
    capture_failed = Signal(str)     # error message
    
    def __init__(self, parent=None):
        super(ThumbnailCapture, self).__init__(parent)
        self._default_size = QtCore.QSize(128, 128)
        self._quality = 85
        self._temp_dir = tempfile.gettempdir()
        
    def capture_viewport(self, size=None, panel=None):
        """Capture current Maya viewport"""
        if size is None:
            size = self._default_size
            
        try:
            # Get current or specified panel
            if panel is None:
                panel = cmds.getPanel(withFocus=True)
                if not panel or cmds.getPanel(typeOf=panel) != 'modelPanel':
                    # Get first available model panel
                    model_panels = cmds.getPanel(type='modelPanel')
                    if model_panels:
                        panel = model_panels[0]
                    else:
                        self.capture_failed.emit("No model panel available")
                        return False
                        
            # Generate unique filename
            import time
            timestamp = str(int(time.time() * 1000))
            temp_filename = os.path.join(self._temp_dir, f"picker_thumb_{timestamp}")
            
            # Capture viewport using playblast
            result = cmds.playblast(
                frame=cmds.currentTime(query=True),
                format='image',
                filename=temp_filename,
                widthHeight=[size.width(), size.height()],
                percent=100,
                quality=self._quality,
                viewer=False,
                showOrnaments=False,
                compression='png',
                startTime=cmds.currentTime(query=True),
                endTime=cmds.currentTime(query=True)
            )
            
            # The actual filename includes frame number
            actual_filename = f"{temp_filename}.{int(cmds.currentTime(query=True)):04d}.png"
            
            if os.path.exists(actual_filename):
                # Convert to base64
                base64_data = self.image_to_base64(actual_filename)
                
                # Clean up temp file
                try:
                    os.remove(actual_filename)
                except:
                    pass
                    
                if base64_data:
                    self.capture_completed.emit(base64_data)
                    return True
                else:
                    self.capture_failed.emit("Failed to convert image to base64")
                    return False
            else:
                self.capture_failed.emit(f"Capture file not created: {actual_filename}")
                return False
                
        except Exception as e:
            self.capture_failed.emit(f"Viewport capture failed: {str(e)}")
            return False
            
    def capture_selection_area(self, rect, size=None):
        """Capture specific area of viewport"""
        if size is None:
            size = self._default_size
            
        try:
            # This is a simplified implementation
            # In production, you might want to use Maya's API for more precise control
            return self.capture_viewport(size)
            
        except Exception as e:
            self.capture_failed.emit(f"Selection area capture failed: {str(e)}")
            return False
            
    def capture_widget(self, widget, size=None):
        """Capture QWidget as thumbnail"""
        if size is None:
            size = self._default_size
            
        try:
            # Create pixmap from widget
            pixmap = widget.grab()
            
            if not pixmap.isNull():
                # Scale to desired size
                scaled_pixmap = pixmap.scaled(
                    size,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                
                # Convert to base64
                base64_data = self.pixmap_to_base64(scaled_pixmap)
                if base64_data:
                    self.capture_completed.emit(base64_data)
                    return True
                    
            self.capture_failed.emit("Failed to capture widget")
            return False
            
        except Exception as e:
            self.capture_failed.emit(f"Widget capture failed: {str(e)}")
            return False
            
    def image_to_base64(self, image_path):
        """Convert image file to base64 string"""
        try:
            pixmap = QtGui.QPixmap(image_path)
            if not pixmap.isNull():
                return self.pixmap_to_base64(pixmap)
        except Exception as e:
            print(f"Error converting image to base64: {e}")
        return None
        
    def pixmap_to_base64(self, pixmap):
        """Convert QPixmap to base64 string"""
        try:
            buffer = BytesIO()
            pixmap.save(buffer, "PNG")
            image_data = buffer.getvalue()
            return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            print(f"Error converting pixmap to base64: {e}")
        return None
        
    def base64_to_pixmap(self, base64_data):
        """Convert base64 string to QPixmap"""
        try:
            image_data = base64.b64decode(base64_data)
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(image_data)
            return pixmap
        except Exception as e:
            print(f"Error converting base64 to pixmap: {e}")
        return QtGui.QPixmap()
        
    def set_quality(self, quality):
        """Set capture quality (0-100)"""
        self._quality = max(0, min(100, quality))
        
    def set_default_size(self, size):
        """Set default capture size"""
        self._default_size = size


class ThumbnailCaptureDialog(QtWidgets.QDialog):
    """Dialog for interactive thumbnail capture"""
    
    # Signals
    thumbnail_captured = Signal(str)  # base64 data
    
    def __init__(self, parent=None):
        super(ThumbnailCaptureDialog, self).__init__(parent)
        self.setWindowTitle("Capture Thumbnail")
        self.setModal(True)
        self.resize(300, 400)
        
        self.capture_system = ThumbnailCapture(self)
        self.captured_thumbnail = None
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Instructions
        instructions = QtWidgets.QLabel(
            "Position your Maya viewport to show the desired pose/view, "
            "then click 'Capture Viewport' to create a thumbnail."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Size selection
        size_group = QtWidgets.QGroupBox("Thumbnail Size")
        size_layout = QtWidgets.QHBoxLayout(size_group)
        
        self.size_combo = QtWidgets.QComboBox()
        self.size_combo.addItems([
            "64x64 (Small)",
            "128x128 (Medium)",
            "256x256 (Large)",
            "512x512 (Extra Large)"
        ])
        self.size_combo.setCurrentIndex(1)  # Default to medium
        size_layout.addWidget(self.size_combo)
        
        layout.addWidget(size_group)
        
        # Quality selection
        quality_group = QtWidgets.QGroupBox("Image Quality")
        quality_layout = QtWidgets.QHBoxLayout(quality_group)
        
        self.quality_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.quality_slider.setRange(50, 100)
        self.quality_slider.setValue(85)
        quality_layout.addWidget(self.quality_slider)
        
        self.quality_label = QtWidgets.QLabel("85%")
        quality_layout.addWidget(self.quality_label)
        
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_label.setText(f"{v}%")
        )
        
        layout.addWidget(quality_group)
        
        # Preview area
        preview_group = QtWidgets.QGroupBox("Preview")
        preview_layout = QtWidgets.QVBoxLayout(preview_group)
        
        self.preview_label = QtWidgets.QLabel()
        self.preview_label.setMinimumSize(128, 128)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #888888;
                background-color: #f0f0f0;
            }
        """)
        self.preview_label.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_label.setText("No thumbnail captured")
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_group)
        
        # Capture buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.capture_viewport_btn = QtWidgets.QPushButton("Capture Viewport")
        self.capture_viewport_btn.clicked.connect(self.capture_viewport)
        button_layout.addWidget(self.capture_viewport_btn)
        
        self.capture_selection_btn = QtWidgets.QPushButton("Capture Selection Area")
        self.capture_selection_btn.clicked.connect(self.capture_selection_area)
        button_layout.addWidget(self.capture_selection_btn)
        
        layout.addLayout(button_layout)
        
        # Dialog buttons
        dialog_buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)
        
        self.ok_button = dialog_buttons.button(QtWidgets.QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)
        
        layout.addWidget(dialog_buttons)
        
    def connect_signals(self):
        """Connect signals"""
        self.capture_system.capture_completed.connect(self.on_capture_completed)
        self.capture_system.capture_failed.connect(self.on_capture_failed)
        
    def get_selected_size(self):
        """Get selected thumbnail size"""
        size_map = {
            0: QtCore.QSize(64, 64),
            1: QtCore.QSize(128, 128),
            2: QtCore.QSize(256, 256),
            3: QtCore.QSize(512, 512)
        }
        return size_map.get(self.size_combo.currentIndex(), QtCore.QSize(128, 128))
        
    def capture_viewport(self):
        """Capture Maya viewport"""
        size = self.get_selected_size()
        quality = self.quality_slider.value()
        
        self.capture_system.set_quality(quality)
        self.capture_system.set_default_size(size)
        
        self.capture_viewport_btn.setEnabled(False)
        self.capture_viewport_btn.setText("Capturing...")
        
        self.capture_system.capture_viewport(size)
        
    def capture_selection_area(self):
        """Capture selection area (simplified implementation)"""
        # For now, this just captures the viewport
        # In a full implementation, you might show an overlay for area selection
        self.capture_viewport()
        
    def on_capture_completed(self, base64_data):
        """Handle successful capture"""
        self.captured_thumbnail = base64_data
        
        # Show preview
        pixmap = self.capture_system.base64_to_pixmap(base64_data)
        if not pixmap.isNull():
            # Scale preview to fit label
            preview_size = self.preview_label.size()
            scaled_pixmap = pixmap.scaled(
                preview_size,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
            
        # Enable OK button
        self.ok_button.setEnabled(True)
        
        # Reset capture button
        self.capture_viewport_btn.setEnabled(True)
        self.capture_viewport_btn.setText("Capture Viewport")
        
    def on_capture_failed(self, error_message):
        """Handle capture failure"""
        QtWidgets.QMessageBox.warning(
            self,
            "Capture Failed",
            f"Failed to capture thumbnail:\n{error_message}"
        )
        
        # Reset capture button
        self.capture_viewport_btn.setEnabled(True)
        self.capture_viewport_btn.setText("Capture Viewport")
        
    def accept(self):
        """Accept dialog and emit thumbnail"""
        if self.captured_thumbnail:
            self.thumbnail_captured.emit(self.captured_thumbnail)
        super(ThumbnailCaptureDialog, self).accept()
        
    def get_captured_thumbnail(self):
        """Get captured thumbnail data"""
        return self.captured_thumbnail


class ThumbnailManager(QtCore.QObject):
    """Manages thumbnails for picker items"""
    
    def __init__(self, parent=None):
        super(ThumbnailManager, self).__init__(parent)
        self._thumbnails = {}  # item_id -> base64_data
        self._thumbnail_cache = {}  # base64_data -> QPixmap
        
    def store_thumbnail(self, item_id, base64_data):
        """Store thumbnail for item"""
        self._thumbnails[item_id] = base64_data
        
    def get_thumbnail(self, item_id):
        """Get thumbnail for item"""
        return self._thumbnails.get(item_id)
        
    def get_thumbnail_pixmap(self, item_id, size=None):
        """Get thumbnail as QPixmap"""
        base64_data = self.get_thumbnail(item_id)
        if not base64_data:
            return QtGui.QPixmap()
            
        # Check cache first
        cache_key = f"{base64_data}_{size}" if size else base64_data
        if cache_key in self._thumbnail_cache:
            return self._thumbnail_cache[cache_key]
            
        # Create pixmap
        try:
            image_data = base64.b64decode(base64_data)
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(image_data)
            
            if size and not pixmap.isNull():
                pixmap = pixmap.scaled(
                    size,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                
            # Cache the result
            self._thumbnail_cache[cache_key] = pixmap
            return pixmap
            
        except Exception as e:
            print(f"Error creating thumbnail pixmap: {e}")
            
        return QtGui.QPixmap()
        
    def remove_thumbnail(self, item_id):
        """Remove thumbnail for item"""
        if item_id in self._thumbnails:
            base64_data = self._thumbnails[item_id]
            del self._thumbnails[item_id]
            
            # Clear from cache
            cache_keys_to_remove = [key for key in self._thumbnail_cache.keys() if key.startswith(base64_data)]
            for key in cache_keys_to_remove:
                del self._thumbnail_cache[key]
                
    def clear_all_thumbnails(self):
        """Clear all thumbnails"""
        self._thumbnails.clear()
        self._thumbnail_cache.clear()
        
    def export_thumbnails(self, file_path):
        """Export thumbnails to file"""
        import json
        try:
            with open(file_path, 'w') as f:
                json.dump(self._thumbnails, f)
            return True
        except Exception as e:
            print(f"Error exporting thumbnails: {e}")
            return False
            
    def import_thumbnails(self, file_path):
        """Import thumbnails from file"""
        import json
        try:
            with open(file_path, 'r') as f:
                imported_thumbnails = json.load(f)
                self._thumbnails.update(imported_thumbnails)
                # Clear cache to force regeneration
                self._thumbnail_cache.clear()
            return True
        except Exception as e:
            print(f"Error importing thumbnails: {e}")
            return False


# Global thumbnail manager instance
_thumbnail_manager = None

def get_thumbnail_manager():
    """Get global thumbnail manager instance"""
    global _thumbnail_manager
    if _thumbnail_manager is None:
        _thumbnail_manager = ThumbnailManager()
    return _thumbnail_manager
