# File: core/app.py
"""
Main Application for Ultimate Animation Picker
Central application controller that manages all components.
Designed to run inside Maya 2024 (PySide2) but degrades gracefully if outside.
"""

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Qt
import traceback

# Maya integration (optional)
try:
    import maya.OpenMayaUI as omui  # type: ignore
    from shiboken2 import wrapInstance  # type: ignore
    IN_MAYA = True
except Exception:
    omui = None
    wrapInstance = None
    IN_MAYA = False

# Absolute imports (work reliably in Maya)
from UltimatePicker.core.menu_bar import MenuBarManager
try:
    from UltimatePicker.core.animation_toolbar import AnimationToolbar
except Exception:
    AnimationToolbar = None

try:
    from UltimatePicker.core.tab_manager import TabManager
except Exception:
    TabManager = None

try:
    from UltimatePicker.ui.property_panel import PropertyPanel
except Exception:
    PropertyPanel = None

from UltimatePicker.widgets.enhanced_canvas import EnhancedCanvas


def _maya_main_window():
    if not IN_MAYA or omui is None or wrapInstance is None:
        return None
    ptr = omui.MQtUtil.mainWindow()
    if ptr is None:
        return None
    return wrapInstance(int(ptr), QtWidgets.QWidget)


class UltimateAnimationPicker(QtWidgets.QMainWindow):
    """
    Main application window for the Ultimate Animation Picker.
    """

    def __init__(self, parent=None):
        super(UltimateAnimationPicker, self).__init__(parent or _maya_main_window())
        self.setObjectName("UltimateAnimationPickerUI")
        self.setWindowTitle("Ultimate Animation Picker")
        self.resize(1200, 800)

        # Components
        self.menu_manager: MenuBarManager = None  # type: ignore
        self.animation_toolbar = None
        self.property_panel = None
        self.tab_manager = None
        self.canvas: EnhancedCanvas = None  # type: ignore

        self._build_ui()
        self._wire_menu_actions()

    # -----------------------
    # UI
    # -----------------------
    def _build_ui(self):
        # Menu bar
        self.menu_manager = MenuBarManager(self)

        # Canvas as central widget
        self.canvas = EnhancedCanvas(self)
        self.setCentralWidget(self.canvas)

        # Animation toolbar (top)
        if AnimationToolbar is not None:
            try:
                self.animation_toolbar = AnimationToolbar(self)
                self.animation_toolbar.setObjectName("UltimateAnimationToolbar")
                self.addToolBar(Qt.TopToolBarArea, self.animation_toolbar)
            except Exception:
                print("AnimationToolbar failed to initialize:")
                traceback.print_exc()
                self.animation_toolbar = None

        # Property panel (dock, right)
        if PropertyPanel is not None:
            try:
                self.property_panel = PropertyPanel(self)
                self.property_panel.setObjectName("UltimatePropertyPanel")
                self.addDockWidget(Qt.RightDockWidgetArea, self.property_panel)
            except Exception:
                print("PropertyPanel failed to initialize:")
                traceback.print_exc()
                self.property_panel = None

        # Tab manager (logic layer; its widget is managed by its own module)
        if TabManager is not None:
            try:
                self.tab_manager = TabManager(self)
            except Exception:
                print("TabManager failed to initialize:")
                traceback.print_exc()
                self.tab_manager = None

        # Canvas ↔ property panel
        if self.property_panel is not None:
            # When selection changes on canvas, let the property panel react if it exposes an API
            if hasattr(self.canvas, "selection_changed"):
                try:
                    self.canvas.selection_changed.connect(self._on_canvas_selection_changed)
                except Exception:
                    traceback.print_exc()

            # Property changes flowing back to canvas items if your PropertyPanel emits property_changed
            if hasattr(self.property_panel, "property_changed"):
                try:
                    self.property_panel.property_changed.connect(self._on_property_changed)
                except Exception:
                    traceback.print_exc()

    # -----------------------
    # Menu wiring
    # -----------------------
    def _wire_menu_actions(self):
        m = self.menu_manager

        # File
        m.new_picker_requested.connect(self._new_picker)
        m.open_picker_requested.connect(self._open_picker)
        m.save_picker_requested.connect(self._save_picker)
        m.save_as_picker_requested.connect(self._save_picker_as)
        m.import_layout_requested.connect(self._import_layout)
        m.export_layout_requested.connect(self._export_layout)
        m.exit_requested.connect(self.close)

        # Edit
        m.undo_requested.connect(lambda: self._safe_call(self._canvas_call, "undo"))
        m.redo_requested.connect(lambda: self._safe_call(self._canvas_call, "redo"))
        m.cut_requested.connect(lambda: self._safe_call(self._canvas_call, "cut"))
        m.copy_requested.connect(lambda: self._safe_call(self._canvas_call, "copy"))
        m.paste_requested.connect(lambda: self._safe_call(self._canvas_call, "paste"))
        m.duplicate_requested.connect(lambda: self._safe_call(self._canvas_call, "duplicate_selection"))
        m.delete_requested.connect(lambda: self._safe_call(self._canvas_call, "delete_selection"))
        m.select_all_requested.connect(lambda: self._safe_call(self._canvas_call, "select_all"))
        m.select_none_requested.connect(lambda: self._safe_call(self._canvas_call, "clear_selection"))
        m.group_requested.connect(lambda: self._safe_call(self._canvas_call, "group_selection"))
        m.ungroup_requested.connect(lambda: self._safe_call(self._canvas_call, "ungroup_selection"))

        # View / Mode
        m.edit_mode_toggled.connect(self._set_edit_mode)
        m.toggle_grid.connect(self._set_grid_visible)
        m.toggle_snap_to_grid.connect(self._set_snap_to_grid)
        m.toggle_animation_toolbar.connect(self._set_animation_toolbar_visible)
        m.toggle_property_panel.connect(self._set_property_panel_visible)
        m.zoom_in_requested.connect(lambda: self._safe_call(self._canvas_call, "zoom_in"))
        m.zoom_out_requested.connect(lambda: self._safe_call(self._canvas_call, "zoom_out"))
        m.reset_zoom_requested.connect(lambda: self._safe_call(self._canvas_call, "reset_zoom"))
        m.reset_view_requested.connect(lambda: self._safe_call(self._canvas_call, "reset_view"))

        # Create
        m.create_rectangle.connect(lambda: self._safe_call(self._canvas_call, "create_rectangle"))
        m.create_round_rectangle.connect(lambda: self._safe_call(self._canvas_call, "create_round_rectangle"))
        m.create_circle.connect(lambda: self._safe_call(self._canvas_call, "create_circle"))
        m.create_polygon.connect(lambda: self._safe_call(self._canvas_call, "create_polygon"))
        m.create_checkbox.connect(lambda: self._safe_call(self._canvas_call, "create_checkbox"))
        m.create_slider.connect(lambda: self._safe_call(self._canvas_call, "create_slider"))
        m.create_radius_button.connect(lambda: self._safe_call(self._canvas_call, "create_radius_button"))
        m.create_pose_button.connect(lambda: self._safe_call(self._canvas_call, "create_pose_button"))
        m.create_text.connect(lambda: self._safe_call(self._canvas_call, "create_text"))

        # Tabs
        m.add_tab_requested.connect(self._add_tab)
        m.rename_tab_requested.connect(self._rename_tab)
        m.delete_tab_requested.connect(self._delete_tab)

        # Help
        m.show_help.connect(self._show_help)
        m.show_about.connect(self._show_about)

    # -----------------------
    # Canvas helpers
    # -----------------------
    def _canvas_call(self, method_name: str, *args, **kwargs):
        """Safely call a method on the canvas if it exists."""
        method = getattr(self.canvas, method_name, None)
        if callable(method):
            return method(*args, **kwargs)
        # No-op if not implemented on EnhancedCanvas
        print(f"[INFO] Canvas has no method '{method_name}'")

    def _safe_call(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            traceback.print_exc()

    # -----------------------
    # File actions
    # -----------------------
    def _new_picker(self):
        # Optional: clear current canvas, reset state
        self._safe_call(self._canvas_call, "clear_all")

    def _open_picker(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Picker", "", "Picker Files (*.json *.upicker);;All Files (*.*)")
        if not path:
            return
        # Prefer a canvas API if available
        if hasattr(self.canvas, "load_from_file"):
            self._safe_call(self.canvas.load_from_file, path)
        else:
            print("[INFO] load_from_file not implemented on canvas")

    def _save_picker(self):
        # If canvas knows last path, use that
        if hasattr(self.canvas, "save_to_file"):
            self._safe_call(self.canvas.save_to_file, None)  # your canvas can interpret None as "use last path"
        else:
            self._save_picker_as()

    def _save_picker_as(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Picker As", "", "Picker Files (*.json *.upicker);;All Files (*.*)")
        if not path:
            return
        if hasattr(self.canvas, "save_to_file"):
            self._safe_call(self.canvas.save_to_file, path)
        else:
            print("[INFO] save_to_file not implemented on canvas")

    def _import_layout(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Layout", "", "Layout Files (*.json);;All Files (*.*)")
        if not path:
            return
        if hasattr(self.canvas, "import_layout"):
            self._safe_call(self.canvas.import_layout, path)
        else:
            print("[INFO] import_layout not implemented on canvas")

    def _export_layout(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Layout", "", "Layout Files (*.json);;All Files (*.*)")
        if not path:
            return
        if hasattr(self.canvas, "export_layout"):
            self._safe_call(self.canvas.export_layout, path)
        else:
            print("[INFO] export_layout not implemented on canvas")

    # -----------------------
    # View / Mode
    # -----------------------
    def _set_edit_mode(self, edit: bool):
        self._safe_call(self._canvas_call, "set_edit_mode", edit)
        # Sync property panel enable state if it exposes API
        if self.property_panel is not None:
            try:
                self.property_panel.setEnabled(edit)
            except Exception:
                pass

    def _set_grid_visible(self, visible: bool):
        self._safe_call(self._canvas_call, "set_grid_visible", visible)

    def _set_snap_to_grid(self, snap: bool):
        self._safe_call(self._canvas_call, "set_snap_to_grid", snap)

    def _set_animation_toolbar_visible(self, visible: bool):
        if self.animation_toolbar is not None:
            self.animation_toolbar.setVisible(visible)

    def _set_property_panel_visible(self, visible: bool):
        if self.property_panel is not None:
            self.property_panel.setVisible(visible)

    # -----------------------
    # Tabs
    # -----------------------
    def _add_tab(self):
        if self.tab_manager is None:
            QtWidgets.QMessageBox.information(self, "Tabs", "Tab Manager is not available.")
            return
        # Ask whether to add a Main or Sub tab
        choice = QtWidgets.QInputDialog.getItem(self, "Add Tab", "Type:", ["Main Tab", "Sub Tab"], 0, False)
        if not choice[1]:
            return
        tab_type = choice[0]
        name, ok = QtWidgets.QInputDialog.getText(self, "Add Tab", "Tab name:")
        if not ok or not name:
            return
        try:
            if tab_type == "Main Tab":
                self.tab_manager.create_main_tab(name)
            else:
                # Need current main tab; fall back to first if your TabManager exposes it
                current_main = getattr(self.tab_manager, "_current_main_tab", None)
                if not current_main:
                    QtWidgets.QMessageBox.warning(self, "Tabs", "No current main tab to add a sub tab.")
                    return
                self.tab_manager.create_sub_tab(current_main, name)
        except Exception:
            traceback.print_exc()

    def _rename_tab(self):
        if self.tab_manager is None:
            QtWidgets.QMessageBox.information(self, "Tabs", "Tab Manager is not available.")
            return
        current_main = getattr(self.tab_manager, "_current_main_tab", None)
        current_sub = getattr(self.tab_manager, "_current_sub_tab", None)
        if not current_main:
            QtWidgets.QMessageBox.warning(self, "Tabs", "No current tab to rename.")
            return
        # Ask what to rename
        choice = QtWidgets.QInputDialog.getItem(self, "Rename", "Which:", ["Main Tab", "Sub Tab"], 0, False)
        if not choice[1]:
            return
        which = choice[0]
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Rename", "New name:")
        if not ok or not new_name:
            return
        try:
            if which == "Main Tab":
                self.tab_manager.rename_main_tab(current_main, new_name)
            else:
                if not current_sub:
                    QtWidgets.QMessageBox.warning(self, "Tabs", "No current sub tab to rename.")
                    return
                self.tab_manager.rename_sub_tab(current_main, current_sub, new_name)
        except Exception:
            traceback.print_exc()

    def _delete_tab(self):
        if self.tab_manager is None:
            QtWidgets.QMessageBox.information(self, "Tabs", "Tab Manager is not available.")
            return
        current_main = getattr(self.tab_manager, "_current_main_tab", None)
        current_sub = getattr(self.tab_manager, "_current_sub_tab", None)
        if not current_main:
            QtWidgets.QMessageBox.warning(self, "Tabs", "No current tab to delete.")
            return

        choice = QtWidgets.QInputDialog.getItem(self, "Delete", "Which:", ["Main Tab", "Sub Tab"], 0, False)
        if not choice[1]:
            return
        which = choice[0]
        try:
            if which == "Main Tab":
                self.tab_manager.delete_main_tab(current_main)
            else:
                if not current_sub:
                    QtWidgets.QMessageBox.warning(self, "Tabs", "No current sub tab to delete.")
                    return
                self.tab_manager.delete_sub_tab(current_main, current_sub)
        except Exception:
            traceback.print_exc()

    # -----------------------
    # Help
    # -----------------------
    def _show_help(self):
        QtWidgets.QMessageBox.information(
            self, "Ultimate Animation Picker - Help",
            "• Left-click to select\n"
            "• Edit Mode to move/resize items\n"
            "• Use View menu for grid/zoom\n"
            "• Tabs menu manages main/sub tabs\n"
            "• File menu to save/open/import/export"
        )

    def _show_about(self):
        QtWidgets.QMessageBox.information(
            self, "About Ultimate Animation Picker",
            "Ultimate Animation Picker\n"
            "Maya 2024 (PySide2) compatible\n"
            "© Your Name"
        )

    # -----------------------
    # Canvas ↔ Property Panel
    # -----------------------
    def _on_canvas_selection_changed(self, items):
        # If your PropertyPanel has a method to show properties, call it.
        if self.property_panel is None:
            return
        try:
            if hasattr(self.property_panel, "show_properties"):
                self.property_panel.show_properties(items)
            else:
                # minimal behavior: enable panel when something is selected
                self.property_panel.setEnabled(bool(items))
        except Exception:
            traceback.print_exc()

    def _on_property_changed(self, prop_name: str, value):
        # Push property changes into selected items if your canvas exposes an API
        try:
            if hasattr(self.canvas, "apply_property_to_selection"):
                self.canvas.apply_property_to_selection(prop_name, value)
        except Exception:
            traceback.print_exc()


# -----------------------
# Public launcher
# -----------------------
def launch_ultimate_picker(parent=None):
    print("Ultimate Animation Picker - Starting in Maya environment")
    win = UltimateAnimationPicker(parent)
    win.show()
    return win
