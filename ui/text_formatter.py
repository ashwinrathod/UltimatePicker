# File: ui/text_formatter.py
"""
Text Formatter Widget for Ultimate Animation Picker
Comprehensive text formatting controls for picker items
"""

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal

class TextFormatter(QtWidgets.QWidget):
    """Text formatting widget with all text properties"""
    
    # Signals
    text_property_changed = Signal(str, object)  # property_name, value
    
    def __init__(self, parent=None):
        super(TextFormatter, self).__init__(parent)
        self._current_item = None
        self._updating = False
        self.setup_ui()
        
    def setup_ui(self):
        """Setup text formatter UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Text content
        self.create_text_content_section(layout)
        
        # Font properties
        self.create_font_section(layout)
        
        # Text colors
        self.create_color_section(layout)
        
        # Text alignment
        self.create_alignment_section(layout)
        
        # Text effects
        self.create_effects_section(layout)
        
    def create_text_content_section(self, parent_layout):
        """Create text content section"""
        content_group = QtWidgets.QGroupBox("Text Content")
        layout = QtWidgets.QVBoxLayout(content_group)
        
        # Text input
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setMaximumHeight(60)
        self.text_edit.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.text_edit)
        
        # Rich text option
        self.rich_text_check = QtWidgets.QCheckBox("Rich Text (HTML)")
        self.rich_text_check.toggled.connect(lambda checked: self.emit_property_change('rich_text', checked))
        layout.addWidget(self.rich_text_check)
        
        parent_layout.addWidget(content_group)
        
    def create_font_section(self, parent_layout):
        """Create font properties section"""
        font_group = QtWidgets.QGroupBox("Font")
        layout = QtWidgets.QFormLayout(font_group)
        
        # Font family
        self.font_combo = QtWidgets.QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.on_font_changed)
        layout.addRow("Family:", self.font_combo)
        
        # Font size
        size_layout = QtWidgets.QHBoxLayout()
        self.font_size_spin = QtWidgets.QSpinBox()
        self.font_size_spin.setRange(6, 72)
        self.font_size_spin.setValue(10)
        self.font_size_spin.valueChanged.connect(lambda v: self.emit_property_change('font_size', v))
        size_layout.addWidget(self.font_size_spin)
        
        # Font size slider for quick adjustment
        self.font_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.font_size_slider.setRange(6, 72)
        self.font_size_slider.setValue(10)
        self.font_size_slider.valueChanged.connect(self.on_font_size_slider_changed)
        size_layout.addWidget(self.font_size_slider)
        
        font_size_widget = QtWidgets.QWidget()
        font_size_widget.setLayout(size_layout)
        layout.addRow("Size:", font_size_widget)
        
        # Font style buttons
        style_layout = QtWidgets.QHBoxLayout()
        
        self.bold_btn = QtWidgets.QPushButton("B")
        self.bold_btn.setMaximumSize(30, 25)
        self.bold_btn.setCheckable(True)
        self.bold_btn.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        self.bold_btn.toggled.connect(lambda checked: self.emit_property_change('font_bold', checked))
        style_layout.addWidget(self.bold_btn)
        
        self.italic_btn = QtWidgets.QPushButton("I")
        self.italic_btn.setMaximumSize(30, 25)
        self.italic_btn.setCheckable(True)
        font = QtGui.QFont("Arial", 10)
        font.setItalic(True)
        self.italic_btn.setFont(font)
        self.italic_btn.toggled.connect(lambda checked: self.emit_property_change('font_italic', checked))
        style_layout.addWidget(self.italic_btn)
        
        self.underline_btn = QtWidgets.QPushButton("U")
        self.underline_btn.setMaximumSize(30, 25)
        self.underline_btn.setCheckable(True)
        font = QtGui.QFont("Arial", 10)
        font.setUnderline(True)
        self.underline_btn.setFont(font)
        self.underline_btn.toggled.connect(lambda checked: self.emit_property_change('font_underline', checked))
        style_layout.addWidget(self.underline_btn)
        
        style_layout.addStretch()
        
        style_widget = QtWidgets.QWidget()
        style_widget.setLayout(style_layout)
        layout.addRow("Style:", style_widget)
        
        parent_layout.addWidget(font_group)
        
    def create_color_section(self, parent_layout):
        """Create text color section"""
        color_group = QtWidgets.QGroupBox("Text Colors")
        layout = QtWidgets.QFormLayout(color_group)
        
        # Import ColorEditor from the same package
        from .color_editor import ColorEditor
        
        # Normal text color
        self.text_normal_color = ColorEditor()
        self.text_normal_color.color_changed.connect(lambda c: self.emit_property_change('text_color', c))
        layout.addRow("Normal:", self.text_normal_color)
        
        # Hover text color
        self.text_hover_color = ColorEditor()
        self.text_hover_color.color_changed.connect(lambda c: self.emit_property_change('text_hover_color', c))
        layout.addRow("Hover:", self.text_hover_color)
        
        # Click text color
        self.text_click_color = ColorEditor()
        self.text_click_color.color_changed.connect(lambda c: self.emit_property_change('text_click_color', c))
        layout.addRow("Click:", self.text_click_color)
        
        parent_layout.addWidget(color_group)
        
    def create_alignment_section(self, parent_layout):
        """Create text alignment section"""
        alignment_group = QtWidgets.QGroupBox("Alignment")
        layout = QtWidgets.QGridLayout(alignment_group)
        
        # Horizontal alignment
        h_align_group = QtWidgets.QButtonGroup(self)
        
        self.align_left_btn = QtWidgets.QPushButton("◀")
        self.align_left_btn.setCheckable(True)
        self.align_left_btn.setMaximumSize(30, 25)
        self.align_left_btn.setToolTip("Align Left")
        h_align_group.addButton(self.align_left_btn, int(QtCore.Qt.AlignLeft))
        layout.addWidget(self.align_left_btn, 0, 0)
        
        self.align_center_btn = QtWidgets.QPushButton("▬")
        self.align_center_btn.setCheckable(True)
        self.align_center_btn.setMaximumSize(30, 25)
        self.align_center_btn.setToolTip("Align Center")
        h_align_group.addButton(self.align_center_btn, int(QtCore.Qt.AlignHCenter))
        layout.addWidget(self.align_center_btn, 0, 1)
        
        self.align_right_btn = QtWidgets.QPushButton("▶")
        self.align_right_btn.setCheckable(True)
        self.align_right_btn.setMaximumSize(30, 25)
        self.align_right_btn.setToolTip("Align Right")
        h_align_group.addButton(self.align_right_btn, int(QtCore.Qt.AlignRight))
        layout.addWidget(self.align_right_btn, 0, 2)
        
        # Vertical alignment
        v_align_group = QtWidgets.QButtonGroup(self)
        
        self.align_top_btn = QtWidgets.QPushButton("▲")
        self.align_top_btn.setCheckable(True)
        self.align_top_btn.setMaximumSize(30, 25)
        self.align_top_btn.setToolTip("Align Top")
        v_align_group.addButton(self.align_top_btn, int(QtCore.Qt.AlignTop))
        layout.addWidget(self.align_top_btn, 1, 0)
        
        self.align_middle_btn = QtWidgets.QPushButton("■")
        self.align_middle_btn.setCheckable(True)
        self.align_middle_btn.setMaximumSize(30, 25)
        self.align_middle_btn.setToolTip("Align Middle")
        v_align_group.addButton(self.align_middle_btn, int(QtCore.Qt.AlignVCenter))
        layout.addWidget(self.align_middle_btn, 1, 1)
        
        self.align_bottom_btn = QtWidgets.QPushButton("▼")
        self.align_bottom_btn.setCheckable(True)
        self.align_bottom_btn.setMaximumSize(30, 25)
        self.align_bottom_btn.setToolTip("Align Bottom")
        v_align_group.addButton(self.align_bottom_btn, int(QtCore.Qt.AlignBottom))
        layout.addWidget(self.align_bottom_btn, 1, 2)
        
        # Connect alignment signals
        h_align_group.idClicked.connect(self.on_horizontal_alignment_changed)
        v_align_group.idClicked.connect(self.on_vertical_alignment_changed)
        
        parent_layout.addWidget(alignment_group)
        
    def create_effects_section(self, parent_layout):
        """Create text effects section"""
        effects_group = QtWidgets.QGroupBox("Effects")
        layout = QtWidgets.QFormLayout(effects_group)
        
        # Text shadow
        self.shadow_check = QtWidgets.QCheckBox()
        self.shadow_check.toggled.connect(lambda checked: self.emit_property_change('text_shadow', checked))
        layout.addRow("Shadow:", self.shadow_check)
        
        # Shadow color
        from .color_editor import ColorEditor
        self.shadow_color = ColorEditor(QtCore.Qt.gray)
        self.shadow_color.color_changed.connect(lambda c: self.emit_property_change('shadow_color', c))
        layout.addRow("Shadow Color:", self.shadow_color)
        
        # Shadow offset
        shadow_offset_layout = QtWidgets.QHBoxLayout()
        
        self.shadow_x_spin = QtWidgets.QSpinBox()
        self.shadow_x_spin.setRange(-20, 20)
        self.shadow_x_spin.setValue(2)
        self.shadow_x_spin.valueChanged.connect(self.on_shadow_offset_changed)
        shadow_offset_layout.addWidget(QtWidgets.QLabel("X:"))
        shadow_offset_layout.addWidget(self.shadow_x_spin)
        
        self.shadow_y_spin = QtWidgets.QSpinBox()
        self.shadow_y_spin.setRange(-20, 20)
        self.shadow_y_spin.setValue(2)
        self.shadow_y_spin.valueChanged.connect(self.on_shadow_offset_changed)
        shadow_offset_layout.addWidget(QtWidgets.QLabel("Y:"))
        shadow_offset_layout.addWidget(self.shadow_y_spin)
        
        shadow_offset_widget = QtWidgets.QWidget()
        shadow_offset_widget.setLayout(shadow_offset_layout)
        layout.addRow("Shadow Offset:", shadow_offset_widget)
        
        # Letter spacing
        self.letter_spacing_spin = QtWidgets.QDoubleSpinBox()
        self.letter_spacing_spin.setRange(-5.0, 10.0)
        self.letter_spacing_spin.setSingleStep(0.5)
        self.letter_spacing_spin.setValue(0.0)
        self.letter_spacing_spin.valueChanged.connect(lambda v: self.emit_property_change('letter_spacing', v))
        layout.addRow("Letter Spacing:", self.letter_spacing_spin)
        
        # Line spacing
        self.line_spacing_spin = QtWidgets.QDoubleSpinBox()
        self.line_spacing_spin.setRange(0.5, 3.0)
        self.line_spacing_spin.setSingleStep(0.1)
        self.line_spacing_spin.setValue(1.0)
        self.line_spacing_spin.valueChanged.connect(lambda v: self.emit_property_change('line_spacing', v))
        layout.addRow("Line Spacing:", self.line_spacing_spin)
        
        parent_layout.addWidget(effects_group)
        
    def set_item(self, item):
        """Set current item to format"""
        self._current_item = item
        self.update_from_item()
        
    def update_from_item(self):
        """Update formatter from current item"""
        if not self._current_item:
            return
            
        self._updating = True
        
        try:
            # Text content
            text = getattr(self._current_item, 'text', '')
            if hasattr(self._current_item, '_rich_text') and self._current_item._rich_text:
                self.text_edit.setHtml(text)
                self.rich_text_check.setChecked(True)
            else:
                self.text_edit.setPlainText(text)
                self.rich_text_check.setChecked(False)
                
            # Font properties
            font_family = getattr(self._current_item, 'font_family', 'Arial')
            self.font_combo.setCurrentFont(QtGui.QFont(font_family))
            
            font_size = getattr(self._current_item, 'font_size', 10)
            self.font_size_spin.setValue(font_size)
            self.font_size_slider.setValue(font_size)
            
            # Font style
            self.bold_btn.setChecked(getattr(self._current_item, 'font_bold', False))
            self.italic_btn.setChecked(getattr(self._current_item, 'font_italic', False))
            self.underline_btn.setChecked(getattr(self._current_item, 'font_underline', False))
            
            # Text colors
            text_color = getattr(self._current_item, 'text_color', QtCore.Qt.black)
            self.text_normal_color.set_color(text_color)
            
            # Text alignment
            alignment = getattr(self._current_item, '_text_alignment', QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.update_alignment_buttons(alignment)
            
            # Effects
            shadow_enabled = getattr(self._current_item, '_text_shadow', False)
            self.shadow_check.setChecked(shadow_enabled)
            
            if hasattr(self._current_item, '_shadow_offset'):
                offset = self._current_item._shadow_offset
                self.shadow_x_spin.setValue(int(offset.x()))
                self.shadow_y_spin.setValue(int(offset.y()))
                
            letter_spacing = getattr(self._current_item, '_letter_spacing', 0.0)
            self.letter_spacing_spin.setValue(letter_spacing)
            
            line_spacing = getattr(self._current_item, '_line_spacing', 1.0)
            self.line_spacing_spin.setValue(line_spacing)
            
        finally:
            self._updating = False
            
    def update_alignment_buttons(self, alignment):
        """Update alignment button states"""
        # Horizontal alignment
        if alignment & QtCore.Qt.AlignLeft:
            self.align_left_btn.setChecked(True)
        elif alignment & QtCore.Qt.AlignHCenter:
            self.align_center_btn.setChecked(True)
        elif alignment & QtCore.Qt.AlignRight:
            self.align_right_btn.setChecked(True)
            
        # Vertical alignment
        if alignment & QtCore.Qt.AlignTop:
            self.align_top_btn.setChecked(True)
        elif alignment & QtCore.Qt.AlignVCenter:
            self.align_middle_btn.setChecked(True)
        elif alignment & QtCore.Qt.AlignBottom:
            self.align_bottom_btn.setChecked(True)
            
    def on_text_changed(self):
        """Handle text content change"""
        if self._updating:
            return
            
        if self.rich_text_check.isChecked():
            text = self.text_edit.toHtml()
        else:
            text = self.text_edit.toPlainText()
            
        self.emit_property_change('text', text)
        
    def on_font_changed(self, font):
        """Handle font family change"""
        self.emit_property_change('font_family', font.family())
        
    def on_font_size_slider_changed(self, value):
        """Handle font size slider change"""
        self.font_size_spin.setValue(value)
        
    def on_horizontal_alignment_changed(self, alignment_id):
        """Handle horizontal alignment change"""
        # Get current vertical alignment
        current_alignment = getattr(self._current_item, '_text_alignment', QtCore.Qt.AlignTop)
        vertical_part = current_alignment & (QtCore.Qt.AlignTop | QtCore.Qt.AlignVCenter | QtCore.Qt.AlignBottom)
        
        new_alignment = QtCore.Qt.Alignment(alignment_id) | vertical_part
        self.emit_property_change('text_alignment', new_alignment)
        
    def on_vertical_alignment_changed(self, alignment_id):
        """Handle vertical alignment change"""
        # Get current horizontal alignment
        current_alignment = getattr(self._current_item, '_text_alignment', QtCore.Qt.AlignLeft)
        horizontal_part = current_alignment & (QtCore.Qt.AlignLeft | QtCore.Qt.AlignHCenter | QtCore.Qt.AlignRight)
        
        new_alignment = horizontal_part | QtCore.Qt.Alignment(alignment_id)
        self.emit_property_change('text_alignment', new_alignment)
        
    def on_shadow_offset_changed(self):
        """Handle shadow offset change"""
        offset = QtCore.QPointF(self.shadow_x_spin.value(), self.shadow_y_spin.value())
        self.emit_property_change('shadow_offset', offset)
        
    def emit_property_change(self, property_name, value):
        """Emit property change signal"""
        if not self._updating:
            self.text_property_changed.emit(property_name, value)
            
    def create_text_preset_buttons(self):
        """Create preset text format buttons"""
        presets_layout = QtWidgets.QHBoxLayout()
        
        # Title preset
        title_btn = QtWidgets.QPushButton("Title")
        title_btn.clicked.connect(lambda: self.apply_text_preset("title"))
        presets_layout.addWidget(title_btn)
        
        # Subtitle preset
        subtitle_btn = QtWidgets.QPushButton("Subtitle")
        subtitle_btn.clicked.connect(lambda: self.apply_text_preset("subtitle"))
        presets_layout.addWidget(subtitle_btn)
        
        # Body preset
        body_btn = QtWidgets.QPushButton("Body")
        body_btn.clicked.connect(lambda: self.apply_text_preset("body"))
        presets_layout.addWidget(body_btn)
        
        # Caption preset
        caption_btn = QtWidgets.QPushButton("Caption")
        caption_btn.clicked.connect(lambda: self.apply_text_preset("caption"))
        presets_layout.addWidget(caption_btn)
        
        return presets_layout
        
    def apply_text_preset(self, preset_name):
        """Apply text formatting preset"""
        presets = {
            "title": {
                "font_size": 16,
                "font_bold": True,
                "text_color": QtCore.Qt.darkBlue
            },
            "subtitle": {
                "font_size": 12,
                "font_bold": True,
                "text_color": QtCore.Qt.black
            },
            "body": {
                "font_size": 10,
                "font_bold": False,
                "text_color": QtCore.Qt.black
            },
            "caption": {
                "font_size": 8,
                "font_italic": True,
                "text_color": QtCore.Qt.gray
            }
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            for prop, value in preset.items():
                self.emit_property_change(prop, value)
