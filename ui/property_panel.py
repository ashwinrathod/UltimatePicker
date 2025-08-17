# File: ui/property_panel.py
"""
Property Panel for Ultimate Animation Picker
Comprehensive item properties editor with color, text, and behavior options
"""

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal
from .color_editor import ColorEditor
from .text_formatter import TextFormatter

class PropertyPanel(QtWidgets.QDockWidget):
    """Property editing panel for picker items"""
    
    # Signals
    property_changed = Signal(str, object)  # property_name, value
    
    def __init__(self, parent=None):
        super(PropertyPanel, self).__init__("Properties", parent)
        self.setObjectName("PropertyPanel")
        
        # Current item being edited
        self._current_item = None
        self._updating = False  # Prevent feedback loops
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup property panel UI"""
        # Main widget
        main_widget = QtWidgets.QWidget()
        self.setWidget(main_widget)
        
        # Scroll area for properties
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        # Properties widget
        self.properties_widget = QtWidgets.QWidget()
        self.properties_layout = QtWidgets.QVBoxLayout(self.properties_widget)
        self.properties_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll.setWidget(self.properties_widget)
        
        # Main layout
        layout = QtWidgets.QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
        # Create property sections
        self.create_item_info_section()
        self.create_appearance_section()
        self.create_text_section()
        self.create_behavior_section()
        self.create_commands_section()
        self.create_coordinate_section()
        
        # Add stretch at the end
        self.properties_layout.addStretch()
        
    def create_item_info_section(self):
        """Create item information section"""
        self.info_group = self.create_group_box("Item Information")
        layout = QtWidgets.QFormLayout(self.info_group)
        
        # Item ID
        self.item_id_edit = QtWidgets.QLineEdit()
        self.item_id_edit.textChanged.connect(lambda text: self.emit_property_change('id', text))
        layout.addRow("ID:", self.item_id_edit)
        
        # Item type (read-only)
        self.item_type_label = QtWidgets.QLabel("-")
        layout.addRow("Type:", self.item_type_label)
        
        # Item name
        self.item_name_edit = QtWidgets.QLineEdit()
        self.item_name_edit.textChanged.connect(lambda text: self.emit_property_change('name', text))
        layout.addRow("Name:", self.item_name_edit)
        
        # Description
        self.description_edit = QtWidgets.QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.textChanged.connect(lambda: self.emit_property_change('description', self.description_edit.toPlainText()))
        layout.addRow("Description:", self.description_edit)
        
    def create_appearance_section(self):
        """Create appearance properties section"""
        self.appearance_group = self.create_group_box("Appearance")
        layout = QtWidgets.QFormLayout(self.appearance_group)
        
        # Colors section
        colors_widget = QtWidgets.QWidget()
        colors_layout = QtWidgets.QVBoxLayout(colors_widget)
        colors_layout.setContentsMargins(0, 0, 0, 0)
        
        # Background colors
        bg_group = QtWidgets.QGroupBox("Background Colors")
        bg_layout = QtWidgets.QFormLayout(bg_group)
        
        self.bg_normal_color = ColorEditor()
        self.bg_normal_color.color_changed.connect(lambda c: self.emit_property_change('bg_color', c))
        bg_layout.addRow("Normal:", self.bg_normal_color)
        
        self.bg_hover_color = ColorEditor()
        self.bg_hover_color.color_changed.connect(lambda c: self.emit_property_change('bg_hover_color', c))
        bg_layout.addRow("Hover:", self.bg_hover_color)
        
        self.bg_click_color = ColorEditor()
        self.bg_click_color.color_changed.connect(lambda c: self.emit_property_change('bg_click_color', c))
        bg_layout.addRow("Click:", self.bg_click_color)
        
        colors_layout.addWidget(bg_group)
        
        # Edge/Border colors
        edge_group = QtWidgets.QGroupBox("Edge Colors")
        edge_layout = QtWidgets.QFormLayout(edge_group)
        
        self.edge_normal_color = ColorEditor()
        self.edge_normal_color.color_changed.connect(lambda c: self.emit_property_change('edge_color', c))
        edge_layout.addRow("Normal:", self.edge_normal_color)
        
        self.edge_hover_color = ColorEditor()
        self.edge_hover_color.color_changed.connect(lambda c: self.emit_property_change('edge_hover_color', c))
        edge_layout.addRow("Hover:", self.edge_hover_color)
        
        self.edge_click_color = ColorEditor()
        self.edge_click_color.color_changed.connect(lambda c: self.emit_property_change('edge_click_color', c))
        edge_layout.addRow("Click:", self.edge_click_color)
        
        colors_layout.addWidget(edge_group)
        
        layout.addRow(colors_widget)
        
        # Edge width
        self.edge_width_spin = QtWidgets.QSpinBox()
        self.edge_width_spin.setRange(0, 10)
        self.edge_width_spin.valueChanged.connect(lambda v: self.emit_property_change('edge_width', v))
        layout.addRow("Edge Width:", self.edge_width_spin)
        
        # Opacity
        self.opacity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(lambda v: self.emit_property_change('opacity', v / 100.0))
        
        opacity_layout = QtWidgets.QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QtWidgets.QLabel("100%")
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_label.setText(f"{v}%"))
        opacity_layout.addWidget(self.opacity_label)
        
        opacity_widget = QtWidgets.QWidget()
        opacity_widget.setLayout(opacity_layout)
        layout.addRow("Opacity:", opacity_widget)
        
    def create_text_section(self):
        """Create text formatting section"""
        self.text_group = self.create_group_box("Text Formatting")
        layout = QtWidgets.QVBoxLayout(self.text_group)
        
        # Text formatter widget
        self.text_formatter = TextFormatter()
        self.text_formatter.text_property_changed.connect(self.on_text_property_changed)
        layout.addWidget(self.text_formatter)
        
    def create_behavior_section(self):
        """Create behavior properties section"""
        self.behavior_group = self.create_group_box("Behavior")
        layout = QtWidgets.QFormLayout(self.behavior_group)
        
        # Local/World coordinate system
        self.coordinate_system_combo = QtWidgets.QComboBox()
        self.coordinate_system_combo.addItems(["Local", "World"])
        self.coordinate_system_combo.currentTextChanged.connect(lambda text: self.emit_property_change('coordinate_system', text))
        layout.addRow("Coordinate System:", self.coordinate_system_combo)
        
        # Interactive checkbox
        self.interactive_check = QtWidgets.QCheckBox()
        self.interactive_check.toggled.connect(lambda checked: self.emit_property_change('interactive', checked))
        layout.addRow("Interactive:", self.interactive_check)
        
        # Selectable checkbox
        self.selectable_check = QtWidgets.QCheckBox()
        self.selectable_check.toggled.connect(lambda checked: self.emit_property_change('selectable', checked))
        layout.addRow("Selectable:", self.selectable_check)
        
        # Movable checkbox
        self.movable_check = QtWidgets.QCheckBox()
        self.movable_check.toggled.connect(lambda checked: self.emit_property_change('movable', checked))
        layout.addRow("Movable:", self.movable_check)
        
        # Z-order
        self.z_order_spin = QtWidgets.QSpinBox()
        self.z_order_spin.setRange(-1000, 1000)
        self.z_order_spin.valueChanged.connect(lambda v: self.emit_property_change('z_order', v))
        layout.addRow("Z-Order:", self.z_order_spin)
        
    def create_commands_section(self):
        """Create command properties section"""
        self.commands_group = self.create_group_box("Commands")
        layout = QtWidgets.QVBoxLayout(self.commands_group)
        
        # Command type
        cmd_type_layout = QtWidgets.QHBoxLayout()
        self.python_radio = QtWidgets.QRadioButton("Python")
        self.mel_radio = QtWidgets.QRadioButton("MEL")
        self.python_radio.setChecked(True)
        cmd_type_layout.addWidget(self.python_radio)
        cmd_type_layout.addWidget(self.mel_radio)
        cmd_type_layout.addStretch()
        
        layout.addLayout(cmd_type_layout)
        
        # Left click command
        layout.addWidget(QtWidgets.QLabel("Left Click Command:"))
        self.left_click_cmd = QtWidgets.QTextEdit()
        self.left_click_cmd.setMaximumHeight(80)
        self.left_click_cmd.textChanged.connect(lambda: self.emit_property_change('left_click_command', self.left_click_cmd.toPlainText()))
        layout.addWidget(self.left_click_cmd)
        
        # Right click command
        layout.addWidget(QtWidgets.QLabel("Right Click Command:"))
        self.right_click_cmd = QtWidgets.QTextEdit()
        self.right_click_cmd.setMaximumHeight(80)
        self.right_click_cmd.textChanged.connect(lambda: self.emit_property_change('right_click_command', self.right_click_cmd.toPlainText()))
        layout.addWidget(self.right_click_cmd)
        
        # Test command button
        test_button = QtWidgets.QPushButton("Test Command")
        test_button.clicked.connect(self.test_command)
        layout.addWidget(test_button)
        
    def create_coordinate_section(self):
        """Create coordinate properties section"""
        self.coord_group = self.create_group_box("Position & Size")
        layout = QtWidgets.QFormLayout(self.coord_group)
        
        # Position
        pos_layout = QtWidgets.QHBoxLayout()
        
        self.pos_x_spin = QtWidgets.QDoubleSpinBox()
        self.pos_x_spin.setRange(-10000, 10000)
        self.pos_x_spin.valueChanged.connect(self.on_position_changed)
        pos_layout.addWidget(QtWidgets.QLabel("X:"))
        pos_layout.addWidget(self.pos_x_spin)
        
        self.pos_y_spin = QtWidgets.QDoubleSpinBox()
        self.pos_y_spin.setRange(-10000, 10000)
        self.pos_y_spin.valueChanged.connect(self.on_position_changed)
        pos_layout.addWidget(QtWidgets.QLabel("Y:"))
        pos_layout.addWidget(self.pos_y_spin)
        
        pos_widget = QtWidgets.QWidget()
        pos_widget.setLayout(pos_layout)
        layout.addRow("Position:", pos_widget)
        
        # Size (for items that support it)
        size_layout = QtWidgets.QHBoxLayout()
        
        self.size_w_spin = QtWidgets.QDoubleSpinBox()
        self.size_w_spin.setRange(1, 5000)
        self.size_w_spin.valueChanged.connect(self.on_size_changed)
        size_layout.addWidget(QtWidgets.QLabel("W:"))
        size_layout.addWidget(self.size_w_spin)
        
        self.size_h_spin = QtWidgets.QDoubleSpinBox()
        self.size_h_spin.setRange(1, 5000)
        self.size_h_spin.valueChanged.connect(self.on_size_changed)
        size_layout.addWidget(QtWidgets.QLabel("H:"))
        size_layout.addWidget(self.size_h_spin)
        
        size_widget = QtWidgets.QWidget()
        size_widget.setLayout(size_layout)
        layout.addRow("Size:", size_widget)
        
        # Rotation
        self.rotation_spin = QtWidgets.QDoubleSpinBox()
        self.rotation_spin.setRange(-360, 360)
        self.rotation_spin.setSuffix("°")
        self.rotation_spin.valueChanged.connect(lambda v: self.emit_property_change('rotation', v))
        layout.addRow("Rotation:", self.rotation_spin)
        
    def create_group_box(self, title):
        """Create a collapsible group box"""
        group = QtWidgets.QGroupBox(title)
        group.setCheckable(True)
        group.setChecked(False)  # Start collapsed
        self.properties_layout.addWidget(group)
        return group
        
    def set_current_item(self, item):
        """Set the current item to edit"""
        self._current_item = item
        self.update_properties()
        
    def update_properties(self):
        """Update property panel with current item's properties"""
        if not self._current_item:
            self.clear_properties()
            return
            
        self._updating = True
        
        try:
            # Item info
            self.item_id_edit.setText(getattr(self._current_item, 'id', ''))
            self.item_type_label.setText(type(self._current_item).__name__)
            self.item_name_edit.setText(getattr(self._current_item, 'name', ''))
            self.description_edit.setPlainText(getattr(self._current_item, 'description', ''))
            
            # Appearance
            if hasattr(self._current_item, 'bg_color'):
                self.bg_normal_color.set_color(self._current_item.bg_color)
            if hasattr(self._current_item, 'bg_hover_color'):
                self.bg_hover_color.set_color(self._current_item.bg_hover_color)
            if hasattr(self._current_item, 'bg_click_color'):
                self.bg_click_color.set_color(self._current_item.bg_click_color)
                
            if hasattr(self._current_item, 'pen_color'):
                self.edge_normal_color.set_color(self._current_item.pen_color)
            if hasattr(self._current_item, 'pen_width'):
                self.edge_width_spin.setValue(self._current_item.pen_width)
                
            if hasattr(self._current_item, 'opacity'):
                self.opacity_slider.setValue(int(self._current_item.opacity() * 100))
                
            # Text formatting
            self.text_formatter.set_item(self._current_item)
            
            # Behavior
            coord_sys = getattr(self._current_item, 'coordinate_system', 'Local')
            self.coordinate_system_combo.setCurrentText(coord_sys)
            
            # Position & Size
            if hasattr(self._current_item, 'pos'):
                pos = self._current_item.pos()
                self.pos_x_spin.setValue(pos.x())
                self.pos_y_spin.setValue(pos.y())
                
            if hasattr(self._current_item, 'boundingRect'):
                rect = self._current_item.boundingRect()
                self.size_w_spin.setValue(rect.width())
                self.size_h_spin.setValue(rect.height())
                
            if hasattr(self._current_item, 'rotation'):
                self.rotation_spin.setValue(self._current_item.rotation())
                
            # Commands
            left_cmd = getattr(self._current_item, 'left_click_command', '')
            self.left_click_cmd.setPlainText(left_cmd)
            
            right_cmd = getattr(self._current_item, 'right_click_command', '')
            self.right_click_cmd.setPlainText(right_cmd)
            
        finally:
            self._updating = False
            
    def clear_properties(self):
        """Clear all property fields"""
        self._updating = True
        
        try:
            # Clear all fields
            self.item_id_edit.clear()
            self.item_type_label.setText("-")
            self.item_name_edit.clear()
            self.description_edit.clear()
            
            # Reset colors
            self.bg_normal_color.set_color(QtCore.Qt.gray)
            self.bg_hover_color.set_color(QtCore.Qt.lightGray)
            self.bg_click_color.set_color(QtCore.Qt.darkGray)
            self.edge_normal_color.set_color(QtCore.Qt.black)
            
            # Reset values
            self.edge_width_spin.setValue(1)
            self.opacity_slider.setValue(100)
            self.coordinate_system_combo.setCurrentIndex(0)
            
            # Clear position/size
            self.pos_x_spin.setValue(0)
            self.pos_y_spin.setValue(0)
            self.size_w_spin.setValue(100)
            self.size_h_spin.setValue(50)
            self.rotation_spin.setValue(0)
            
            # Clear commands
            self.left_click_cmd.clear()
            self.right_click_cmd.clear()
            
        finally:
            self._updating = False
            
    def emit_property_change(self, property_name, value):
        """Emit property change signal"""
        if not self._updating and self._current_item:
            self.property_changed.emit(property_name, value)
            
    def on_text_property_changed(self, property_name, value):
        """Handle text property changes"""
        self.emit_property_change(property_name, value)
        
    def on_position_changed(self):
        """Handle position changes"""
        if not self._updating:
            pos = QtCore.QPointF(self.pos_x_spin.value(), self.pos_y_spin.value())
            self.emit_property_change('position', pos)
            
    def on_size_changed(self):
        """Handle size changes"""
        if not self._updating:
            size = QtCore.QSizeF(self.size_w_spin.value(), self.size_h_spin.value())
            self.emit_property_change('size', size)
            
    def test_command(self):
        """Test the current command"""
        if not self._current_item:
            return
            
        command = self.left_click_cmd.toPlainText()
        if not command:
            command = self.right_click_cmd.toPlainText()
            
        if command:
            try:
                if self.python_radio.isChecked():
                    exec(command)
                else:
                    import maya.mel as mel
                    mel.eval(command)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Command Error", f"Error executing command:\n{str(e)}")
                
    def copy_properties(self):
        """Copy properties from current item"""
        if self._current_item and hasattr(self._current_item, 'to_dict'):
            return self._current_item.to_dict()
        return None
        
    def paste_properties(self, properties_data):
        """Paste properties to current item"""
        if self._current_item and properties_data and hasattr(self._current_item, 'from_dict'):
            self._current_item.from_dict(properties_data)
            self.update_properties()
            return True
        return False
        
    def reset_to_defaults(self):
        """Reset current item to default properties"""
        if not self._current_item:
            return
            
        reply = QtWidgets.QMessageBox.question(
            self,
            "Reset Properties",
            "Reset all properties to default values?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # Reset to defaults (this would need item-specific implementation)
            if hasattr(self._current_item, 'reset_to_defaults'):
                self._current_item.reset_to_defaults()
                self.update_properties()
