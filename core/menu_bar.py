# File: core/menu_bar.py
"""
Menu Bar System for Ultimate Animation Picker
Provides File, Edit, View, Create, and Help menus with comprehensive functionality
"""

import os
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal

class UltimatePickerMenuBar(QtWidgets.QMenuBar):
    """Enhanced menu bar with all required functionality"""
    
    # Signals for menu actions
    new_picker_requested = Signal()
    save_picker_requested = Signal()
    open_picker_requested = Signal()
    edit_mode_toggled = Signal(bool)
    delete_selected = Signal()
    copy_items = Signal()
    paste_items = Signal()
    copy_style = Signal()
    paste_style = Signal()
    align_left = Signal()
    align_right = Signal()
    align_center = Signal()
    align_top = Signal()
    align_bottom = Signal()
    align_middle = Signal()
    bring_to_front = Signal()
    send_to_back = Signal()
    zoom_in = Signal()
    zoom_out = Signal()
    zoom_fit = Signal()
    zoom_reset = Signal()
    toggle_grid = Signal(bool)
    toggle_animation_toolbar = Signal(bool)
    toggle_property_panel = Signal(bool)
    create_rectangle = Signal()
    create_round_rectangle = Signal()
    create_circle = Signal()
    create_polygon = Signal()
    create_checkbox = Signal()
    create_slider = Signal()
    create_radius_button = Signal()
    create_pose_button = Signal()
    create_text = Signal()
    create_new_tab = Signal()
    show_about = Signal()
    show_help = Signal()
    
    def __init__(self, parent=None):
        super(UltimatePickerMenuBar, self).__init__(parent)
        self._edit_mode = False
        self._grid_visible = False
        self._animation_toolbar_visible = True
        self._property_panel_visible = False
        self.setup_menus()
        
    def setup_menus(self):
        """Setup all menu items"""
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_create_menu()
        self.create_help_menu()
        
    def create_file_menu(self):
        """Create File menu"""
        file_menu = self.addMenu("&File")
        
        # New Picker
        new_action = QtWidgets.QAction("&New Picker", self)
        new_action.setShortcut(QtGui.QKeySequence.New)
        new_action.setStatusTip("Create a new picker")
        new_action.triggered.connect(self.new_picker_requested.emit)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        # Save Picker
        save_action = QtWidgets.QAction("&Save Picker", self)
        save_action.setShortcut(QtGui.QKeySequence.Save)
        save_action.setStatusTip("Save current picker")
        save_action.triggered.connect(self.save_picker_requested.emit)
        file_menu.addAction(save_action)
        
        # Save As
        save_as_action = QtWidgets.QAction("Save &As...", self)
        save_as_action.setShortcut(QtGui.QKeySequence.SaveAs)
        save_as_action.setStatusTip("Save picker with new name")
        save_as_action.triggered.connect(self.save_picker_requested.emit)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Open Picker
        open_action = QtWidgets.QAction("&Open Picker", self)
        open_action.setShortcut(QtGui.QKeySequence.Open)
        open_action.setStatusTip("Open existing picker")
        open_action.triggered.connect(self.open_picker_requested.emit)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Recent Files submenu
        recent_menu = file_menu.addMenu("Recent Files")
        recent_menu.setEnabled(False)  # Will be enabled when recent files are available
        
    def create_edit_menu(self):
        """Create Edit menu"""
        edit_menu = self.addMenu("&Edit")
        
        # Edit Mode Toggle
        self.edit_mode_action = QtWidgets.QAction("&Edit Mode", self)
        self.edit_mode_action.setCheckable(True)
        self.edit_mode_action.setShortcut(QtCore.Qt.Key_E)
        self.edit_mode_action.setStatusTip("Toggle edit mode")
        self.edit_mode_action.triggered.connect(self._toggle_edit_mode)
        edit_menu.addAction(self.edit_mode_action)
        
        edit_menu.addSeparator()
        
        # Delete
        delete_action = QtWidgets.QAction("&Delete", self)
        delete_action.setShortcut(QtGui.QKeySequence.Delete)
        delete_action.setStatusTip("Delete selected items")
        delete_action.triggered.connect(self.delete_selected.emit)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        # Copy/Paste Items
        copy_action = QtWidgets.QAction("&Copy Items", self)
        copy_action.setShortcut(QtGui.QKeySequence.Copy)
        copy_action.setStatusTip("Copy selected items")
        copy_action.triggered.connect(self.copy_items.emit)
        edit_menu.addAction(copy_action)
        
        paste_action = QtWidgets.QAction("&Paste Items", self)
        paste_action.setShortcut(QtGui.QKeySequence.Paste)
        paste_action.setStatusTip("Paste copied items")
        paste_action.triggered.connect(self.paste_items.emit)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        # Copy/Paste Style
        copy_style_action = QtWidgets.QAction("Copy St&yle", self)
        copy_style_action.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_C)
        copy_style_action.setStatusTip("Copy style from selected item")
        copy_style_action.triggered.connect(self.copy_style.emit)
        edit_menu.addAction(copy_style_action)
        
        paste_style_action = QtWidgets.QAction("Paste St&yle", self)
        paste_style_action.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_V)
        paste_style_action.setStatusTip("Paste style to selected items")
        paste_style_action.triggered.connect(self.paste_style.emit)
        edit_menu.addAction(paste_style_action)
        
        edit_menu.addSeparator()
        
        # Alignment submenu
        align_menu = edit_menu.addMenu("&Align")
        
        align_left_action = QtWidgets.QAction("Align &Left", self)
        align_left_action.triggered.connect(self.align_left.emit)
        align_menu.addAction(align_left_action)
        
        align_right_action = QtWidgets.QAction("Align &Right", self)
        align_right_action.triggered.connect(self.align_right.emit)
        align_menu.addAction(align_right_action)
        
        align_center_action = QtWidgets.QAction("Align &Center", self)
        align_center_action.triggered.connect(self.align_center.emit)
        align_menu.addAction(align_center_action)
        
        align_menu.addSeparator()
        
        align_top_action = QtWidgets.QAction("Align &Top", self)
        align_top_action.triggered.connect(self.align_top.emit)
        align_menu.addAction(align_top_action)
        
        align_bottom_action = QtWidgets.QAction("Align &Bottom", self)
        align_bottom_action.triggered.connect(self.align_bottom.emit)
        align_menu.addAction(align_bottom_action)
        
        align_middle_action = QtWidgets.QAction("Align &Middle", self)
        align_middle_action.triggered.connect(self.align_middle.emit)
        align_menu.addAction(align_middle_action)
        
        # Arrange submenu
        arrange_menu = edit_menu.addMenu("A&rrange")
        
        front_action = QtWidgets.QAction("Bring to &Front", self)
        front_action.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_F)
        front_action.triggered.connect(self.bring_to_front.emit)
        arrange_menu.addAction(front_action)
        
        back_action = QtWidgets.QAction("Send to &Back", self)
        back_action.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_B)
        back_action.triggered.connect(self.send_to_back.emit)
        arrange_menu.addAction(back_action)
        
    def create_view_menu(self):
        """Create View menu"""
        view_menu = self.addMenu("&View")
        
        # Zoom controls
        zoom_in_action = QtWidgets.QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_Plus)
        zoom_in_action.triggered.connect(self.zoom_in.emit)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QtWidgets.QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_Minus)
        zoom_out_action.triggered.connect(self.zoom_out.emit)
        view_menu.addAction(zoom_out_action)
        
        zoom_fit_action = QtWidgets.QAction("&Fit to Window", self)
        zoom_fit_action.setShortcut(QtCore.Qt.Key_F)
        zoom_fit_action.triggered.connect(self.zoom_fit.emit)
        view_menu.addAction(zoom_fit_action)
        
        zoom_reset_action = QtWidgets.QAction("&Reset Zoom", self)
        zoom_reset_action.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_0)
        zoom_reset_action.triggered.connect(self.zoom_reset.emit)
        view_menu.addAction(zoom_reset_action)
        
        view_menu.addSeparator()
        
        # Grid toggle
        self.grid_action = QtWidgets.QAction("Show &Grid", self)
        self.grid_action.setCheckable(True)
        self.grid_action.setShortcut(QtCore.Qt.Key_G)
        self.grid_action.triggered.connect(self._toggle_grid)
        view_menu.addAction(self.grid_action)
        
        view_menu.addSeparator()
        
        # Panel toggles
        self.animation_toolbar_action = QtWidgets.QAction("&Animation Toolbar", self)
        self.animation_toolbar_action.setCheckable(True)
        self.animation_toolbar_action.setChecked(True)
        self.animation_toolbar_action.triggered.connect(self._toggle_animation_toolbar)
        view_menu.addAction(self.animation_toolbar_action)
        
        self.property_panel_action = QtWidgets.QAction("&Property Panel", self)
        self.property_panel_action.setCheckable(True)
        self.property_panel_action.triggered.connect(self._toggle_property_panel)
        view_menu.addAction(self.property_panel_action)
        
    def create_create_menu(self):
        """Create Create menu"""
        create_menu = self.addMenu("&Create")
        
        # Button types
        rect_action = QtWidgets.QAction("&Rectangle Button", self)
        rect_action.triggered.connect(self.create_rectangle.emit)
        create_menu.addAction(rect_action)
        
        round_rect_action = QtWidgets.QAction("R&ound Rectangle Button", self)
        round_rect_action.triggered.connect(self.create_round_rectangle.emit)
        create_menu.addAction(round_rect_action)
        
        circle_action = QtWidgets.QAction("&Circle Button", self)
        circle_action.triggered.connect(self.create_circle.emit)
        create_menu.addAction(circle_action)
        
        polygon_action = QtWidgets.QAction("&Polygon Button", self)
        polygon_action.triggered.connect(self.create_polygon.emit)
        create_menu.addAction(polygon_action)
        
        create_menu.addSeparator()
        
        # Controls
        checkbox_action = QtWidgets.QAction("Chec&kbox", self)
        checkbox_action.triggered.connect(self.create_checkbox.emit)
        create_menu.addAction(checkbox_action)
        
        slider_action = QtWidgets.QAction("&Slider", self)
        slider_action.triggered.connect(self.create_slider.emit)
        create_menu.addAction(slider_action)
        
        radius_action = QtWidgets.QAction("Radius &Button", self)
        radius_action.triggered.connect(self.create_radius_button.emit)
        create_menu.addAction(radius_action)
        
        pose_action = QtWidgets.QAction("&Pose Button", self)
        pose_action.triggered.connect(self.create_pose_button.emit)
        create_menu.addAction(pose_action)
        
        create_menu.addSeparator()
        
        # Text
        text_action = QtWidgets.QAction("&Text", self)
        text_action.triggered.connect(self.create_text.emit)
        create_menu.addAction(text_action)
        
        create_menu.addSeparator()
        
        # Tab
        tab_action = QtWidgets.QAction("New &Tab", self)
        tab_action.triggered.connect(self.create_new_tab.emit)
        create_menu.addAction(tab_action)
        
    def create_help_menu(self):
        """Create Help menu"""
        help_menu = self.addMenu("&Help")
        
        help_action = QtWidgets.QAction("&Documentation", self)
        help_action.setShortcut(QtCore.Qt.Key_F1)
        help_action.triggered.connect(self.show_help.emit)
        help_menu.addAction(help_action)
        
        help_menu.addSeparator()
        
        about_action = QtWidgets.QAction("&About Ultimate Picker", self)
        about_action.triggered.connect(self.show_about.emit)
        help_menu.addAction(about_action)
        
    def _toggle_edit_mode(self, checked):
        """Handle edit mode toggle"""
        self._edit_mode = checked
        self.edit_mode_toggled.emit(checked)
        
    def _toggle_grid(self, checked):
        """Handle grid toggle"""
        self._grid_visible = checked
        self.toggle_grid.emit(checked)
        
    def _toggle_animation_toolbar(self, checked):
        """Handle animation toolbar toggle"""
        self._animation_toolbar_visible = checked
        self.toggle_animation_toolbar.emit(checked)
        
    def _toggle_property_panel(self, checked):
        """Handle property panel toggle"""
        self._property_panel_visible = checked
        self.toggle_property_panel.emit(checked)
        
    def set_edit_mode(self, edit_mode):
        """Set edit mode state"""
        self._edit_mode = edit_mode
        self.edit_mode_action.setChecked(edit_mode)
        self.property_panel_action.setEnabled(edit_mode)
        
    def update_ui_state(self, has_selection=False, has_clipboard=False):
        """Update menu states based on current selection and clipboard"""
        # This would be called by the main app to update menu states
        pass
