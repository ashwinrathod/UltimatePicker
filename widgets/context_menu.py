# File: widgets/context_menu.py
"""
Context Menu System for Ultimate Animation Picker
Provides context-sensitive menus for canvas and items
"""

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal
import maya.cmds as cmds

class BaseContextMenu(QtWidgets.QMenu):
    """Base context menu with common functionality"""
    
    def __init__(self, parent=None):
        super(BaseContextMenu, self).__init__(parent)
        self.setup_style()
        
    def setup_style(self):
        """Setup menu style"""
        self.setStyleSheet("""
            QMenu {
                background-color: #3E3E3E;
                color: #FFFFFF;
                border: 1px solid #666666;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #4A90E2;
            }
            QMenu::item:disabled {
                color: #888888;
            }
            QMenu::separator {
                height: 1px;
                background-color: #666666;
                margin: 4px 0px;
            }
        """)
        
    def add_action_with_icon(self, text, icon_name=None, shortcut=None):
        """Add action with optional icon and shortcut"""
        action = self.addAction(text)
        
        if shortcut:
            action.setShortcut(shortcut)
            
        if icon_name:
            # You could load icons from resources here
            pass
            
        return action


class CanvasContextMenu(BaseContextMenu):
    """Context menu for empty canvas areas"""
    
    def __init__(self, canvas, scene_pos, global_pos, parent=None):
        super(CanvasContextMenu, self).__init__(parent)
        self.canvas = canvas
        self.scene_pos = scene_pos
        self.global_pos = global_pos
        self.setup_menu()
        
    def setup_menu(self):
        """Setup canvas context menu"""
        # Create items submenu
        create_menu = self.addMenu("Create")
        
        # Button types
        buttons_menu = create_menu.addMenu("Buttons")
        
        rect_action = buttons_menu.addAction("Rectangle Button")
        rect_action.triggered.connect(lambda: self.create_item('rectangle'))
        
        round_rect_action = buttons_menu.addAction("Round Rectangle Button")
        round_rect_action.triggered.connect(lambda: self.create_item('round_rectangle'))
        
        circle_action = buttons_menu.addAction("Circle Button")
        circle_action.triggered.connect(lambda: self.create_item('circle'))
        
        polygon_action = buttons_menu.addAction("Polygon Button")
        polygon_action.triggered.connect(lambda: self.create_item('polygon'))
        
        create_menu.addSeparator()
        
        # Controls
        controls_menu = create_menu.addMenu("Controls")
        
        checkbox_action = controls_menu.addAction("Checkbox")
        checkbox_action.triggered.connect(lambda: self.create_item('checkbox'))
        
        slider_action = controls_menu.addAction("Slider")
        slider_action.triggered.connect(lambda: self.create_item('slider'))
        
        radius_action = controls_menu.addAction("Radius Button")
        radius_action.triggered.connect(lambda: self.create_item('radius_button'))
        
        pose_action = controls_menu.addAction("Pose Button")
        pose_action.triggered.connect(lambda: self.create_item('pose_button'))
        
        create_menu.addSeparator()
        
        # Text
        text_action = create_menu.addAction("Text")
        text_action.triggered.connect(lambda: self.create_item('text'))
        
        self.addSeparator()
        
        # Paste if available
        from ..utils.clipboard_manager import get_clipboard_manager
        clipboard_manager = get_clipboard_manager()
        
        if clipboard_manager.has_items():
            paste_action = self.addAction("Paste")
            paste_action.setShortcut(QtGui.QKeySequence.Paste)
            paste_action.triggered.connect(self.paste_items)
            
        # Select All
        select_all_action = self.addAction("Select All")
        select_all_action.setShortcut(QtGui.QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.canvas.select_all)
        
        self.addSeparator()
        
        # View options
        view_menu = self.addMenu("View")
        
        # Grid options
        grid_action = view_menu.addAction("Toggle Grid")
        grid_action.setCheckable(True)
        grid_action.setChecked(self.canvas.is_grid_visible())
        grid_action.triggered.connect(self.toggle_grid)
        
        snap_action = view_menu.addAction("Snap to Grid")
        snap_action.setCheckable(True)
        snap_action.setChecked(self.canvas.is_snap_to_grid())
        snap_action.triggered.connect(self.toggle_snap_to_grid)
        
        view_menu.addSeparator()
        
        # Zoom options
        zoom_fit_action = view_menu.addAction("Zoom to Fit")
        zoom_fit_action.triggered.connect(self.canvas.zoom_fit)
        
        zoom_reset_action = view_menu.addAction("Reset Zoom")
        zoom_reset_action.triggered.connect(self.canvas.reset_zoom)
        
        reset_view_action = view_menu.addAction("Reset View")
        reset_view_action.triggered.connect(self.canvas.reset_view)
        
        self.addSeparator()
        
        # Canvas properties
        properties_action = self.addAction("Canvas Properties...")
        properties_action.triggered.connect(self.show_canvas_properties)
        
    def create_item(self, item_type):
        """Create new item at context menu position"""
        self.canvas.create_item(item_type, self.scene_pos)
        
    def paste_items(self):
        """Paste items at context menu position"""
        self.canvas.paste_items(self.scene_pos)
        
    def toggle_grid(self, checked):
        """Toggle grid visibility"""
        self.canvas.set_grid_visible(checked)
        
    def toggle_snap_to_grid(self, checked):
        """Toggle grid snapping"""
        self.canvas.set_snap_to_grid(checked)
        
    def show_canvas_properties(self):
        """Show canvas properties dialog"""
        dialog = CanvasPropertiesDialog(self.canvas, self)
        dialog.exec_()


class ItemContextMenu(BaseContextMenu):
    """Context menu for picker items"""
    
    def __init__(self, item, canvas, global_pos, parent=None):
        super(ItemContextMenu, self).__init__(parent)
        self.item = item
        self.canvas = canvas
        self.global_pos = global_pos
        self.setup_menu()
        
    def setup_menu(self):
        """Setup item context menu"""
        # Item-specific actions
        if hasattr(self.item, 'text'):
            edit_text_action = self.addAction("Edit Text...")
            edit_text_action.triggered.connect(self.edit_item_text)
            
        if hasattr(self.item, 'execute_command'):
            test_command_action = self.addAction("Test Command")
            test_command_action.triggered.connect(self.test_item_command)
            
        if hasattr(self.item, 'store_current_pose'):
            store_pose_action = self.addAction("Store Current Pose")
            store_pose_action.triggered.connect(self.store_current_pose)
            
        self.addSeparator()
        
        # Transform actions
        transform_menu = self.addMenu("Transform")
        
        # Alignment options
        align_menu = transform_menu.addMenu("Align")
        
        align_left_action = align_menu.addAction("Align Left")
        align_left_action.triggered.connect(lambda: self.align_items('left'))
        
        align_right_action = align_menu.addAction("Align Right")
        align_right_action.triggered.connect(lambda: self.align_items('right'))
        
        align_center_action = align_menu.addAction("Align Center")
        align_center_action.triggered.connect(lambda: self.align_items('center'))
        
        align_menu.addSeparator()
        
        align_top_action = align_menu.addAction("Align Top")
        align_top_action.triggered.connect(lambda: self.align_items('top'))
        
        align_bottom_action = align_menu.addAction("Align Bottom")
        align_bottom_action.triggered.connect(lambda: self.align_items('bottom'))
        
        align_middle_action = align_menu.addAction("Align Middle")
        align_middle_action.triggered.connect(lambda: self.align_items('middle'))
        
        # Arrange options
        arrange_menu = transform_menu.addMenu("Arrange")
        
        bring_front_action = arrange_menu.addAction("Bring to Front")
        bring_front_action.triggered.connect(self.bring_to_front)
        
        send_back_action = arrange_menu.addAction("Send to Back")
        send_back_action.triggered.connect(self.send_to_back)
        
        self.addSeparator()
        
        # Edit actions
        copy_action = self.addAction("Copy")
        copy_action.setShortcut(QtGui.QKeySequence.Copy)
        copy_action.triggered.connect(self.copy_item)
        
        # Copy style
        copy_style_action = self.addAction("Copy Style")
        copy_style_action.triggered.connect(self.copy_item_style)
        
        # Paste style if available
        from ..utils.clipboard_manager import get_clipboard_manager
        clipboard_manager = get_clipboard_manager()
        
        if clipboard_manager.has_style():
            paste_style_action = self.addAction("Paste Style")
            paste_style_action.triggered.connect(self.paste_item_style)
            
        duplicate_action = self.addAction("Duplicate")
        duplicate_action.triggered.connect(self.duplicate_item)
        
        self.addSeparator()
        
        delete_action = self.addAction("Delete")
        delete_action.setShortcut(QtGui.QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_item)
        
        self.addSeparator()
        
        # Properties
        properties_action = self.addAction("Properties...")
        properties_action.triggered.connect(self.show_item_properties)
        
    def edit_item_text(self):
        """Edit item text"""
        if hasattr(self.item, 'show_text_edit_dialog'):
            self.item.show_text_edit_dialog()
        elif hasattr(self.item, 'text'):
            text, ok = QtWidgets.QInputDialog.getText(
                self.canvas,
                "Edit Text",
                "Text:",
                QtWidgets.QLineEdit.Normal,
                self.item.text
            )
            if ok:
                self.item.text = text
                if hasattr(self.item, 'update'):
                    self.item.update()
                    
    def test_item_command(self):
        """Test item command"""
        if hasattr(self.item, 'execute_command'):
            try:
                self.item.execute_command()
            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self.canvas,
                    "Command Error",
                    f"Error executing command:\n{str(e)}"
                )
                
    def store_current_pose(self):
        """Store current pose for pose buttons"""
        if hasattr(self.item, 'store_current_pose'):
            self.item.store_current_pose()
            
    def align_items(self, alignment):
        """Align selected items"""
        selected_items = self.canvas.get_selected_items()
        if len(selected_items) < 2:
            return
            
        from ..core.alignment_tools import AlignmentTools
        
        if alignment == 'left':
            AlignmentTools.align_left(selected_items)
        elif alignment == 'right':
            AlignmentTools.align_right(selected_items)
        elif alignment == 'center':
            AlignmentTools.align_center_horizontal(selected_items)
        elif alignment == 'top':
            AlignmentTools.align_top(selected_items)
        elif alignment == 'bottom':
            AlignmentTools.align_bottom(selected_items)
        elif alignment == 'middle':
            AlignmentTools.align_middle_vertical(selected_items)
            
    def bring_to_front(self):
        """Bring item to front"""
        max_z = -1
        for item in self.canvas.get_all_items():
            if hasattr(item, 'zValue'):
                max_z = max(max_z, item.zValue())
                
        if hasattr(self.item, 'setZValue'):
            self.item.setZValue(max_z + 1)
            
    def send_to_back(self):
        """Send item to back"""
        min_z = 1
        for item in self.canvas.get_all_items():
            if hasattr(item, 'zValue'):
                min_z = min(min_z, item.zValue())
                
        if hasattr(self.item, 'setZValue'):
            self.item.setZValue(min_z - 1)
            
    def copy_item(self):
        """Copy item to clipboard"""
        from ..utils.clipboard_manager import get_clipboard_manager
        clipboard_manager = get_clipboard_manager()
        clipboard_manager.copy_items([self.item])
        
    def copy_item_style(self):
        """Copy item style to clipboard"""
        from ..utils.clipboard_manager import get_clipboard_manager
        clipboard_manager = get_clipboard_manager()
        clipboard_manager.copy_style(self.item)
        
    def paste_item_style(self):
        """Paste style to selected items"""
        selected_items = self.canvas.get_selected_items()
        if selected_items:
            from ..utils.clipboard_manager import get_clipboard_manager
            clipboard_manager = get_clipboard_manager()
            clipboard_manager.paste_style(selected_items)
            
    def duplicate_item(self):
        """Duplicate item"""
        from ..utils.clipboard_manager import get_clipboard_manager
        clipboard_manager = get_clipboard_manager()
        
        # Copy and paste the item
        clipboard_manager.copy_items([self.item])
        
        # Offset position slightly
        offset_pos = self.item.pos() + QtCore.QPointF(20, 20)
        new_items = clipboard_manager.paste_items(offset_pos, self.canvas)
        
        # Add to canvas
        for item in new_items:
            self.canvas.add_item(item)
            
    def delete_item(self):
        """Delete item"""
        self.canvas.remove_item(self.item)
        
    def show_item_properties(self):
        """Show item properties dialog"""
        # This would open the property panel or dialog
        from ..ui.property_panel import PropertyPanel
        
        # Get main window to show property panel
        main_window = self.canvas.window()
        if hasattr(main_window, 'property_panel'):
            main_window.property_panel.set_current_item(self.item)
            if not main_window.property_panel.isVisible():
                main_window.property_panel.show()


class CanvasPropertiesDialog(QtWidgets.QDialog):
    """Dialog for canvas properties"""
    
    def __init__(self, canvas, parent=None):
        super(CanvasPropertiesDialog, self).__init__(parent)
        self.canvas = canvas
        self.setWindowTitle("Canvas Properties")
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Canvas info
        info_group = QtWidgets.QGroupBox("Canvas Information")
        info_layout = QtWidgets.QFormLayout(info_group)
        
        canvas_info = self.canvas.get_canvas_info()
        
        info_layout.addRow("Total Items:", QtWidgets.QLabel(str(canvas_info['total_items'])))
        info_layout.addRow("Selected Items:", QtWidgets.QLabel(str(canvas_info['selected_items'])))
        info_layout.addRow("Zoom Factor:", QtWidgets.QLabel(f"{canvas_info['zoom_factor']:.1f}x"))
        info_layout.addRow("Edit Mode:", QtWidgets.QLabel("Yes" if canvas_info['edit_mode'] else "No"))
        
        layout.addWidget(info_group)
        
        # Grid settings
        grid_group = QtWidgets.QGroupBox("Grid Settings")
        grid_layout = QtWidgets.QFormLayout(grid_group)
        
        # Grid visible
        self.grid_visible_check = QtWidgets.QCheckBox()
        self.grid_visible_check.setChecked(canvas_info['grid_visible'])
        grid_layout.addRow("Show Grid:", self.grid_visible_check)
        
        # Grid size
        self.grid_size_spin = QtWidgets.QSpinBox()
        self.grid_size_spin.setRange(5, 100)
        self.grid_size_spin.setValue(canvas_info['grid_size'])
        grid_layout.addRow("Grid Size:", self.grid_size_spin)
        
        # Snap to grid
        self.snap_to_grid_check = QtWidgets.QCheckBox()
        self.snap_to_grid_check.setChecked(canvas_info['snap_to_grid'])
        grid_layout.addRow("Snap to Grid:", self.snap_to_grid_check)
        
        layout.addWidget(grid_group)
        
        # Background settings
        bg_group = QtWidgets.QGroupBox("Background")
        bg_layout = QtWidgets.QFormLayout(bg_group)
        
        # Background color
        self.bg_color_button = QtWidgets.QPushButton()
        self.bg_color_button.setMaximumHeight(30)
        self.bg_color_button.clicked.connect(self.choose_background_color)
        bg_layout.addRow("Background Color:", self.bg_color_button)
        
        layout.addWidget(bg_group)
        
        # Export options
        export_group = QtWidgets.QGroupBox("Export")
        export_layout = QtWidgets.QVBoxLayout(export_group)
        
        export_image_btn = QtWidgets.QPushButton("Export as Image...")
        export_image_btn.clicked.connect(self.export_canvas_image)
        export_layout.addWidget(export_image_btn)
        
        layout.addWidget(export_group)
        
        # Dialog buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.apply_changes)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
    def choose_background_color(self):
        """Choose background color"""
        current_color = self.canvas.backgroundBrush().color()
        color = QtWidgets.QColorDialog.getColor(current_color, self)
        
        if color.isValid():
            # Update button color
            self.bg_color_button.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #666666;"
            )
            self._background_color = color
            
    def export_canvas_image(self):
        """Export canvas as image"""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export Canvas Image",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        
        if file_path:
            success = self.canvas.export_canvas_image(file_path)
            if success:
                QtWidgets.QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Canvas exported to:\n{file_path}"
                )
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Export Failed",
                    "Failed to export canvas image."
                )
                
    def apply_changes(self):
        """Apply changes to canvas"""
        # Apply grid settings
        self.canvas.set_grid_visible(self.grid_visible_check.isChecked())
        self.canvas.set_grid_size(self.grid_size_spin.value())
        self.canvas.set_snap_to_grid(self.snap_to_grid_check.isChecked())
        
        # Apply background color
        if hasattr(self, '_background_color'):
            self.canvas.setBackgroundBrush(QtGui.QBrush(self._background_color))
            
        self.accept()


class MenuItemContextMenu(BaseContextMenu):
    """Context menu for menu items and UI elements"""
    
    def __init__(self, menu_item, parent=None):
        super(MenuItemContextMenu, self).__init__(parent)
        self.menu_item = menu_item
        self.setup_menu()
        
    def setup_menu(self):
        """Setup menu item context menu"""
        # Customize menu item
        customize_action = self.addAction("Customize...")
        customize_action.triggered.connect(self.customize_menu_item)
        
        # Reset to default
        reset_action = self.addAction("Reset to Default")
        reset_action.triggered.connect(self.reset_menu_item)
        
        self.addSeparator()
        
        # Hide menu item
        hide_action = self.addAction("Hide")
        hide_action.triggered.connect(self.hide_menu_item)
        
    def customize_menu_item(self):
        """Customize menu item"""
        # This would open a customization dialog
        pass
        
    def reset_menu_item(self):
        """Reset menu item to default"""
        # This would reset the menu item properties
        pass
        
    def hide_menu_item(self):
        """Hide menu item"""
        if hasattr(self.menu_item, 'setVisible'):
            self.menu_item.setVisible(False)


class TabContextMenu(BaseContextMenu):
    """Context menu for tabs"""
    
    # Signals
    rename_requested = Signal(object)
    delete_requested = Signal(object) 
    duplicate_requested = Signal(object)
    
    def __init__(self, tab_widget, tab_index, parent=None):
        super(TabContextMenu, self).__init__(parent)
        self.tab_widget = tab_widget
        self.tab_index = tab_index
        self.setup_menu()
        
    def setup_menu(self):
        """Setup tab context menu"""
        # Rename tab
        rename_action = self.addAction("Rename")
        rename_action.triggered.connect(self.rename_tab)
        
        # Duplicate tab
        duplicate_action = self.addAction("Duplicate")
        duplicate_action.triggered.connect(self.duplicate_tab)
        
        self.addSeparator()
        
        # Delete tab
        delete_action = self.addAction("Delete")
        delete_action.triggered.connect(self.delete_tab)
        
        # Disable delete if it's the last tab
        if hasattr(self.tab_widget, 'count') and self.tab_widget.count() <= 1:
            delete_action.setEnabled(False)
            
    def rename_tab(self):
        """Rename tab"""
        self.rename_requested.emit(self.tab_index)
        
    def duplicate_tab(self):
        """Duplicate tab"""
        self.duplicate_requested.emit(self.tab_index)
        
    def delete_tab(self):
        """Delete tab"""
        self.delete_requested.emit(self.tab_index)


def show_context_menu(widget, position, menu_type='default', **kwargs):
    """Convenience function to show appropriate context menu"""
    if menu_type == 'canvas':
        menu = CanvasContextMenu(kwargs.get('canvas'), kwargs.get('scene_pos'), position)
    elif menu_type == 'item':
        menu = ItemContextMenu(kwargs.get('item'), kwargs.get('canvas'), position)
    elif menu_type == 'tab':
        menu = TabContextMenu(kwargs.get('tab_widget'), kwargs.get('tab_index'))
    else:
        menu = BaseContextMenu()
        
    menu.exec_(position)
