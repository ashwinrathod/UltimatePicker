# File: core/menu_bar.py
"""
Menu Bar System for Ultimate Animation Picker
Provides File, Edit, View, Create, Tabs and Help menus with comprehensive functionality
"""

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal


class UltimatePickerMenuBar(QtWidgets.QMenuBar):
    """Enhanced menu bar that exposes signals for the main app."""

    # ===== File =====
    new_picker_requested = Signal()
    open_picker_requested = Signal()
    save_picker_requested = Signal()
    save_as_picker_requested = Signal()
    import_layout_requested = Signal()
    export_layout_requested = Signal()
    exit_requested = Signal()

    # ===== Edit =====
    undo_requested = Signal()
    redo_requested = Signal()
    cut_requested = Signal()
    copy_requested = Signal()
    paste_requested = Signal()
    duplicate_requested = Signal()
    delete_requested = Signal()
    select_all_requested = Signal()
    select_none_requested = Signal()
    group_requested = Signal()
    ungroup_requested = Signal()

    # ===== View / Mode =====
    edit_mode_toggled = Signal(bool)
    toggle_grid = Signal(bool)
    toggle_snap_to_grid = Signal(bool)
    toggle_animation_toolbar = Signal(bool)
    toggle_property_panel = Signal(bool)
    zoom_in_requested = Signal()
    zoom_out_requested = Signal()
    reset_view_requested = Signal()
    reset_zoom_requested = Signal()

    # ===== Create =====
    create_rectangle = Signal()
    create_round_rectangle = Signal()
    create_circle = Signal()
    create_polygon = Signal()
    create_checkbox = Signal()
    create_slider = Signal()
    create_radius_button = Signal()
    create_pose_button = Signal()
    create_text = Signal()

    # ===== Tabs =====
    add_tab_requested = Signal()
    rename_tab_requested = Signal()
    delete_tab_requested = Signal()

    # ===== Help =====
    show_help = Signal()
    show_about = Signal()

    # ----- state -----
    def __init__(self, parent=None):
        super(UltimatePickerMenuBar, self).__init__(parent)
        self._edit_mode = False
        self._grid_visible = False
        self._snap_to_grid = False
        self._anim_toolbar_visible = True
        self._prop_panel_visible = True

        self._build_menus()

    # ---------------------------
    # Build Menus
    # ---------------------------
    def _build_menus(self):
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_create_menu()
        self._create_tabs_menu()
        self._create_help_menu()

    # ===== File =====
    def _create_file_menu(self):
        m = self.addMenu("&File")

        act = QtWidgets.QAction("&New Picker", self)
        act.setShortcut(QtGui.QKeySequence.New)
        act.triggered.connect(self.new_picker_requested.emit)
        m.addAction(act)

        act = QtWidgets.QAction("&Open…", self)
        act.setShortcut(QtGui.QKeySequence.Open)
        act.triggered.connect(self.open_picker_requested.emit)
        m.addAction(act)

        m.addSeparator()

        act = QtWidgets.QAction("&Save", self)
        act.setShortcut(QtGui.QKeySequence.Save)
        act.triggered.connect(self.save_picker_requested.emit)
        m.addAction(act)

        act = QtWidgets.QAction("Save &As…", self)
        act.setShortcut(QtGui.QKeySequence("Ctrl+Shift+S"))
        act.triggered.connect(self.save_as_picker_requested.emit)
        m.addAction(act)

        m.addSeparator()

        act = QtWidgets.QAction("&Import Layout…", self)
        act.setShortcut(QtGui.QKeySequence("Ctrl+I"))
        act.triggered.connect(self.import_layout_requested.emit)
        m.addAction(act)

        act = QtWidgets.QAction("&Export Layout…", self)
        act.setShortcut(QtGui.QKeySequence("Ctrl+E"))
        act.triggered.connect(self.export_layout_requested.emit)
        m.addAction(act)

        m.addSeparator()

        act = QtWidgets.QAction("E&xit", self)
        act.setShortcut(QtGui.QKeySequence("Ctrl+Q"))
        act.triggered.connect(self.exit_requested.emit)
        m.addAction(act)

    # ===== Edit =====
    def _create_edit_menu(self):
        m = self.addMenu("&Edit")

        def add(title, shortcut, signal):
            a = QtWidgets.QAction(title, self)
            if shortcut:
                a.setShortcut(QtGui.QKeySequence(shortcut))
            a.triggered.connect(signal.emit)
            m.addAction(a)

        add("&Undo", QtGui.QKeySequence.Undo, self.undo_requested)
        add("&Redo", QtGui.QKeySequence.Redo, self.redo_requested)
        m.addSeparator()
        add("Cu&t", QtGui.QKeySequence.Cut, self.cut_requested)
        add("&Copy", QtGui.QKeySequence.Copy, self.copy_requested)
        add("&Paste", QtGui.QKeySequence.Paste, self.paste_requested)
        add("&Duplicate", "Ctrl+D", self.duplicate_requested)
        add("&Delete", QtGui.QKeySequence.Delete, self.delete_requested)
        m.addSeparator()
        add("Select &All", QtGui.QKeySequence.SelectAll, self.select_all_requested)
        add("Select &None", "Ctrl+Shift+A", self.select_none_requested)
        m.addSeparator()
        add("&Group", "Ctrl+G", self.group_requested)
        add("&Ungroup", "Ctrl+Shift+G", self.ungroup_requested)

    # ===== View / Mode =====
    def _create_view_menu(self):
        m = self.addMenu("&View")

        # Edit mode toggle
        self.edit_mode_action = QtWidgets.QAction("&Edit Mode", self, checkable=True)
        self.edit_mode_action.setChecked(self._edit_mode)
        self.edit_mode_action.setShortcut(QtGui.QKeySequence("E"))
        self.edit_mode_action.toggled.connect(self._on_edit_mode_toggled)
        m.addAction(self.edit_mode_action)

        m.addSeparator()

        # Grid
        self.grid_action = QtWidgets.QAction("Show &Grid", self, checkable=True)
        self.grid_action.setChecked(self._grid_visible)
        self.grid_action.toggled.connect(self._on_grid_toggled)
        m.addAction(self.grid_action)

        self.snap_action = QtWidgets.QAction("&Snap to Grid", self, checkable=True)
        self.snap_action.setChecked(self._snap_to_grid)
        self.snap_action.toggled.connect(self._on_snap_toggled)
        m.addAction(self.snap_action)

        m.addSeparator()

        # Toolbars / Panels
        self.anim_toolbar_action = QtWidgets.QAction("Show &Animation Toolbar", self, checkable=True)
        self.anim_toolbar_action.setChecked(self._anim_toolbar_visible)
        self.anim_toolbar_action.toggled.connect(self._on_anim_toolbar_toggled)
        m.addAction(self.anim_toolbar_action)

        self.prop_panel_action = QtWidgets.QAction("Show &Property Panel", self, checkable=True)
        self.prop_panel_action.setChecked(self._prop_panel_visible)
        self.prop_panel_action.toggled.connect(self._on_prop_panel_toggled)
        m.addAction(self.prop_panel_action)

        m.addSeparator()

        # Zoom/View
        a = QtWidgets.QAction("Zoom &In", self)
        a.setShortcut(QtGui.QKeySequence.ZoomIn)
        a.triggered.connect(self.zoom_in_requested.emit)
        m.addAction(a)

        a = QtWidgets.QAction("Zoom &Out", self)
        a.setShortcut(QtGui.QKeySequence.ZoomOut)
        a.triggered.connect(self.zoom_out_requested.emit)
        m.addAction(a)

        a = QtWidgets.QAction("&Reset Zoom", self)
        a.setShortcut(QtGui.QKeySequence("Ctrl+0"))
        a.triggered.connect(self.reset_zoom_requested.emit)
        m.addAction(a)

        a = QtWidgets.QAction("Reset &View", self)
        a.setShortcut(QtGui.QKeySequence("Ctrl+Shift+0"))
        a.triggered.connect(self.reset_view_requested.emit)
        m.addAction(a)

    # ===== Create =====
    def _create_create_menu(self):
        m = self.addMenu("&Create")

        def add(title, signal, shortcut=None):
            a = QtWidgets.QAction(title, self)
            if shortcut:
                a.setShortcut(QtGui.QKeySequence(shortcut))
            a.triggered.connect(signal.emit)
            m.addAction(a)

        add("&Rectangle", self.create_rectangle, "R")
        add("&Round Rectangle", self.create_round_rectangle)
        add("&Circle", self.create_circle, "C")
        add("&Polygon", self.create_polygon)
        m.addSeparator()
        add("&Checkbox", self.create_checkbox)
        add("&Slider", self.create_slider)
        add("&Radius Button", self.create_radius_button)
        add("&Pose Button", self.create_pose_button)
        m.addSeparator()
        add("&Text", self.create_text, "T")

    # ===== Tabs =====
    def _create_tabs_menu(self):
        m = self.addMenu("&Tabs")

        a = QtWidgets.QAction("&Add Tab…", self)
        a.setShortcut(QtGui.QKeySequence("Ctrl+T"))
        a.triggered.connect(self.add_tab_requested.emit)
        m.addAction(a)

        a = QtWidgets.QAction("&Rename Tab…", self)
        a.setShortcut(QtGui.QKeySequence("Ctrl+R"))
        a.triggered.connect(self.rename_tab_requested.emit)
        m.addAction(a)

        a = QtWidgets.QAction("&Delete Tab…", self)
        a.setShortcut(QtGui.QKeySequence("Ctrl+Shift+D"))
        a.triggered.connect(self.delete_tab_requested.emit)
        m.addAction(a)

    # ===== Help =====
    def _create_help_menu(self):
        m = self.addMenu("&Help")

        a = QtWidgets.QAction("&Help", self)
        a.setShortcut(QtGui.QKeySequence.HelpContents)
        a.triggered.connect(self.show_help.emit)
        m.addAction(a)

        a = QtWidgets.QAction("&About", self)
        a.triggered.connect(self.show_about.emit)
        m.addAction(a)

    # ---------------------------
    # Internal Handlers (update state + emit)
    # ---------------------------
    def _on_edit_mode_toggled(self, checked: bool):
        self._edit_mode = checked
        self.edit_mode_toggled.emit(checked)

    def _on_grid_toggled(self, checked: bool):
        self._grid_visible = checked
        self.toggle_grid.emit(checked)

    def _on_snap_toggled(self, checked: bool):
        self._snap_to_grid = checked
        self.toggle_snap_to_grid.emit(checked)

    def _on_anim_toolbar_toggled(self, checked: bool):
        self._anim_toolbar_visible = checked
        self.toggle_animation_toolbar.emit(checked)

    def _on_prop_panel_toggled(self, checked: bool):
        self._prop_panel_visible = checked
        self.toggle_property_panel.emit(checked)

    # Optional external update (if app wants to push UI state back into menu)
    def set_edit_mode(self, edit_mode: bool):
        if self._edit_mode != edit_mode:
            self._edit_mode = edit_mode
            self.edit_mode_action.setChecked(edit_mode)

    def set_panels_visible(self, anim_toolbar: bool = None, property_panel: bool = None):
        if anim_toolbar is not None:
            self._anim_toolbar_visible = anim_toolbar
            self.anim_toolbar_action.setChecked(anim_toolbar)
        if property_panel is not None:
            self._prop_panel_visible = property_panel
            self.prop_panel_action.setChecked(property_panel)


class MenuBarManager:
    """
    Thin wrapper used by the main app to attach the menu bar and
    re-expose all signals as attributes for easy connection.
    """
    def __init__(self, parent: QtWidgets.QMainWindow):
        self.parent = parent
        self.menu_bar = UltimatePickerMenuBar(parent)
        parent.setMenuBar(self.menu_bar)

        # Re-expose every signal for convenience
        for name in dir(self.menu_bar):
            sig = getattr(self.menu_bar, name)
            if isinstance(sig, Signal):
                # PySide2 signals aren't normal Python objects; we skip this path.
                # We just explicitly mirror attributes below.
                pass

        # File
        self.new_picker_requested = self.menu_bar.new_picker_requested
        self.open_picker_requested = self.menu_bar.open_picker_requested
        self.save_picker_requested = self.menu_bar.save_picker_requested
        self.save_as_picker_requested = self.menu_bar.save_as_picker_requested
        self.import_layout_requested = self.menu_bar.import_layout_requested
        self.export_layout_requested = self.menu_bar.export_layout_requested
        self.exit_requested = self.menu_bar.exit_requested

        # Edit
        self.undo_requested = self.menu_bar.undo_requested
        self.redo_requested = self.menu_bar.redo_requested
        self.cut_requested = self.menu_bar.cut_requested
        self.copy_requested = self.menu_bar.copy_requested
        self.paste_requested = self.menu_bar.paste_requested
        self.duplicate_requested = self.menu_bar.duplicate_requested
        self.delete_requested = self.menu_bar.delete_requested
        self.select_all_requested = self.menu_bar.select_all_requested
        self.select_none_requested = self.menu_bar.select_none_requested
        self.group_requested = self.menu_bar.group_requested
        self.ungroup_requested = self.menu_bar.ungroup_requested

        # View / Mode
        self.edit_mode_toggled = self.menu_bar.edit_mode_toggled
        self.toggle_grid = self.menu_bar.toggle_grid
        self.toggle_snap_to_grid = self.menu_bar.toggle_snap_to_grid
        self.toggle_animation_toolbar = self.menu_bar.toggle_animation_toolbar
        self.toggle_property_panel = self.menu_bar.toggle_property_panel
        self.zoom_in_requested = self.menu_bar.zoom_in_requested
        self.zoom_out_requested = self.menu_bar.zoom_out_requested
        self.reset_view_requested = self.menu_bar.reset_view_requested
        self.reset_zoom_requested = self.menu_bar.reset_zoom_requested

        # Create
        self.create_rectangle = self.menu_bar.create_rectangle
        self.create_round_rectangle = self.menu_bar.create_round_rectangle
        self.create_circle = self.menu_bar.create_circle
        self.create_polygon = self.menu_bar.create_polygon
        self.create_checkbox = self.menu_bar.create_checkbox
        self.create_slider = self.menu_bar.create_slider
        self.create_radius_button = self.menu_bar.create_radius_button
        self.create_pose_button = self.menu_bar.create_pose_button
        self.create_text = self.menu_bar.create_text

        # Tabs
        self.add_tab_requested = self.menu_bar.add_tab_requested
        self.rename_tab_requested = self.menu_bar.rename_tab_requested
        self.delete_tab_requested = self.menu_bar.delete_tab_requested

        # Help
        self.show_help = self.menu_bar.show_help
        self.show_about = self.menu_bar.show_about

    def get_menu_bar(self) -> UltimatePickerMenuBar:
        return self.menu_bar
