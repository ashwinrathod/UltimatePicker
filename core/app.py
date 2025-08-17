# File: core/app.py
"""
Main Application for Ultimate Animation Picker
Central application controller that manages all components
"""

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal

try:
    import maya.cmds as cmds
    import maya.OpenMayaUI as omui
    from shiboken2 import wrapInstance
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False
    print("Maya not available - running in standalone mode")

class UltimateAnimationPicker(QtWidgets.QMainWindow):
    """Main application window for Ultimate Animation Picker"""
    
    def __init__(self, parent=None):
        super(UltimateAnimationPicker, self).__init__(parent)
        
        # Application state
        self._current_file_path = None
        self._modified = False
        self._edit_mode = False
        
        # Setup UI
        self.setWindowTitle("Ultimate Animation Picker")
        self.setWindowIcon(self._create_window_icon())
        self.resize(1200, 800)
        
        # Initialize components
        self.setup_ui()
        self.setup_connections()
        self.setup_shortcuts()
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # Import components
        from .menu_bar import MenuBarManager
        from .tab_manager import TabManager
        from .animation_toolbar import AnimationToolbar
        from ..widgets.enhanced_canvas import EnhancedCanvas
        from ..ui.property_panel import PropertyPanel
        
        # Menu bar
        self.menu_manager = MenuBarManager(self)
        self.setMenuBar(self.menu_manager.get_menu_bar())
        
        # Tab manager and canvas container
        self.tab_manager = TabManager(self)
        main_layout.addWidget(self.tab_manager, 1)
        
        # Animation toolbar
        self.animation_toolbar = AnimationToolbar(self)
        main_layout.addWidget(self.animation_toolbar)
        
        # Property panel (dock widget)
        self.property_panel = PropertyPanel(self)
        property_dock = QtWidgets.QDockWidget("Properties", self)
        property_dock.setWidget(self.property_panel)
        property_dock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable | 
            QtWidgets.QDockWidget.DockWidgetFloatable
        )
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, property_dock)
        
        # Initially hide property panel (shown in edit mode)
        property_dock.setVisible(False)
        self.property_dock = property_dock
        
    def setup_connections(self):
        """Setup signal connections"""
        # Menu connections
        self.menu_manager.edit_mode_toggled.connect(self.set_edit_mode)
        self.menu_manager.new_picker_requested.connect(self.new_picker)
        self.menu_manager.open_picker_requested.connect(self.open_picker)
        self.menu_manager.save_picker_requested.connect(self.save_picker)
        self.menu_manager.save_as_picker_requested.connect(self.save_picker_as)
        
        # Tab manager connections
        self.tab_manager.current_canvas_changed.connect(self._on_current_canvas_changed)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Edit mode toggle
        edit_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("E"), self)
        edit_shortcut.activated.connect(self.toggle_edit_mode)
        
        # File operations
        new_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence.New, self)
        new_shortcut.activated.connect(self.new_picker)
        
        open_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence.Open, self)
        open_shortcut.activated.connect(self.open_picker)
        
        save_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence.Save, self)
        save_shortcut.activated.connect(self.save_picker)
        
        save_as_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence.SaveAs, self)
        save_as_shortcut.activated.connect(self.save_picker_as)
        
    def _create_window_icon(self):
        """Create window icon"""
        # Create a simple icon using QPainter
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtCore.Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw a simple picker icon
        painter.setBrush(QtGui.QBrush(QtGui.QColor(74, 144, 226)))
        painter.setPen(QtGui.QPen(QtGui.QColor(50, 100, 180), 2))
        painter.drawRoundedRect(4, 4, 24, 24, 4, 4)
        
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 2))
        painter.drawText(QtCore.QRect(4, 4, 24, 24), QtCore.Qt.AlignCenter, "UP")
        
        painter.end()
        return QtGui.QIcon(pixmap)
        
    def set_edit_mode(self, edit_mode):
        """Set edit mode for the application"""
        if self._edit_mode != edit_mode:
            self._edit_mode = edit_mode
            
            # Update property panel visibility
            self.property_dock.setVisible(edit_mode)
            
            # Update current canvas
            current_canvas = self.tab_manager.get_current_canvas()
            if current_canvas:
                current_canvas.set_edit_mode(edit_mode)
                
            # Update status
            mode_text = "Edit Mode" if edit_mode else "Pose Mode"
            self.statusBar().showMessage(f"{mode_text} - Ready")
            
    def toggle_edit_mode(self):
        """Toggle edit mode"""
        self.set_edit_mode(not self._edit_mode)
        
    def is_edit_mode(self):
        """Check if in edit mode"""
        return self._edit_mode
        
    def new_picker(self):
        """Create new picker"""
        if self._check_unsaved_changes():
            self.tab_manager.create_new_picker()
            self._current_file_path = None
            self._modified = False
            self.setWindowTitle("Ultimate Animation Picker - New Picker")
            self.statusBar().showMessage("New picker created")
            
    def open_picker(self):
        """Open picker file"""
        if not self._check_unsaved_changes():
            return
            
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Picker",
            "",
            "Picker Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                self.tab_manager.load_picker_file(file_path)
                self._current_file_path = file_path
                self._modified = False
                self.setWindowTitle(f"Ultimate Animation Picker - {file_path}")
                self.statusBar().showMessage(f"Opened: {file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error Opening File",
                    f"Failed to open file:\n{str(e)}"
                )
                
    def save_picker(self):
        """Save picker file"""
        if self._current_file_path:
            try:
                self.tab_manager.save_picker_file(self._current_file_path)
                self._modified = False
                self.statusBar().showMessage(f"Saved: {self._current_file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error Saving File",
                    f"Failed to save file:\n{str(e)}"
                )
        else:
            self.save_picker_as()
            
    def save_picker_as(self):
        """Save picker file as"""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Picker As",
            "",
            "Picker Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                self.tab_manager.save_picker_file(file_path)
                self._current_file_path = file_path
                self._modified = False
                self.setWindowTitle(f"Ultimate Animation Picker - {file_path}")
                self.statusBar().showMessage(f"Saved: {file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error Saving File",
                    f"Failed to save file:\n{str(e)}"
                )
                
    def _check_unsaved_changes(self):
        """Check for unsaved changes"""
        if not self._modified:
            return True
            
        reply = QtWidgets.QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Do you want to save them?",
            QtWidgets.QMessageBox.Save | 
            QtWidgets.QMessageBox.Discard | 
            QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.Save
        )
        
        if reply == QtWidgets.QMessageBox.Save:
            self.save_picker()
            return not self._modified
        elif reply == QtWidgets.QMessageBox.Discard:
            return True
        else:
            return False
            
    def _on_current_canvas_changed(self, canvas):
        """Handle current canvas change"""
        if canvas:
            canvas.set_edit_mode(self._edit_mode)
            # Connect canvas to property panel
            self.property_panel.set_current_canvas(canvas)
            
    def closeEvent(self, event):
        """Handle window close"""
        if self._check_unsaved_changes():
            event.accept()
        else:
            event.ignore()


def get_maya_main_window():
    """Get Maya's main window as parent"""
    if not MAYA_AVAILABLE:
        return None
        
    try:
        main_window_ptr = omui.MQtUtil.mainWindow()
        if main_window_ptr:
            return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    except Exception:
        pass
    return None


def launch_ultimate_picker():
    """Launch Ultimate Animation Picker"""
    # Get Maya main window as parent (if available)
    parent = get_maya_main_window()
    
    # Create and show application
    picker = UltimateAnimationPicker(parent)
    picker.show()
    
    return picker