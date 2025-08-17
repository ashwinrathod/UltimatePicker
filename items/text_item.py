# File: items/text_item.py
"""
Text Item for Ultimate Animation Picker
Standalone text display with comprehensive formatting options
"""

from PySide2 import QtWidgets, QtCore, QtGui
from .base_item import BasePickerItem

class TextItem(BasePickerItem):
    """Standalone text item with advanced formatting"""
    
    def __init__(self, text="Text", parent=None):
        super(TextItem, self).__init__(parent)
        
        # Text properties
        self.text = text
        self._rich_text = False  # Support for HTML formatting
        self._word_wrap = True
        self._text_alignment = QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop
        self._line_spacing = 1.0
        self._letter_spacing = 0.0
        
        # Visual properties
        self._background_visible = False
        self._background_color = QtCore.Qt.white
        self._background_opacity = 0.8
        self._border_visible = False
        self._border_color = QtCore.Qt.black
        self._border_width = 1
        self._border_style = QtCore.Qt.SolidLine
        
        # Text effects
        self._text_shadow = False
        self._shadow_color = QtCore.Qt.gray
        self._shadow_offset = QtCore.QPointF(2, 2)
        self._shadow_blur_radius = 0
        
        # Size constraints
        self._min_width = 50
        self._min_height = 20
        self._max_width = 500
        self._max_height = 300
        self._width = 120
        self._height = 30
        
        # Auto-size options
        self._auto_resize = True
        self._fixed_width = False
        self._fixed_height = False
        
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Calculate initial size
        self.update_text_size()
        
    def boundingRect(self):
        """Return bounding rectangle"""
        return QtCore.QRectF(0, 0, self._width, self._height)
        
    def paint(self, painter, option, widget):
        """Paint the text item"""
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        
        rect = self.boundingRect()
        
        # Draw background if visible
        if self._background_visible:
            self.draw_background(painter, rect)
            
        # Draw border if visible
        if self._border_visible:
            self.draw_border(painter, rect)
            
        # Draw text with shadow if enabled
        if self._text_shadow:
            self.draw_text_shadow(painter, rect)
            
        # Draw main text
        self.draw_main_text(painter, rect)
        
    def draw_background(self, painter, rect):
        """Draw background"""
        color = QtGui.QColor(self._background_color)
        color.setAlphaF(self._background_opacity)
        painter.setBrush(QtGui.QBrush(color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(rect)
        
    def draw_border(self, painter, rect):
        """Draw border"""
        pen = QtGui.QPen(self._border_color, self._border_width, self._border_style)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(rect.adjusted(self._border_width/2, self._border_width/2, 
                                       -self._border_width/2, -self._border_width/2))
        
    def draw_text_shadow(self, painter, rect):
        """Draw text shadow"""
        shadow_rect = rect.translated(self._shadow_offset)
        
        # Apply shadow color
        painter.setPen(self._shadow_color)
        
        # Set font
        font = self.get_text_font()
        painter.setFont(font)
        
        # Draw shadow text
        if self._rich_text:
            self.draw_rich_text(painter, shadow_rect, self._shadow_color)
        else:
            self.draw_plain_text(painter, shadow_rect, self._shadow_color)
            
    def draw_main_text(self, painter, rect):
        """Draw main text"""
        painter.setPen(self.text_color)
        font = self.get_text_font()
        painter.setFont(font)
        
        if self._rich_text:
            self.draw_rich_text(painter, rect, self.text_color)
        else:
            self.draw_plain_text(painter, rect, self.text_color)
            
    def draw_plain_text(self, painter, rect, color):
        """Draw plain text"""
        painter.setPen(color)
        
        # Apply letter spacing
        font = painter.font()
        if self._letter_spacing != 0:
            font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, self._letter_spacing)
            painter.setFont(font)
            
        # Draw text with alignment and word wrapping
        if self._word_wrap:
            flags = self._text_alignment | QtCore.Qt.TextWordWrap
        else:
            flags = self._text_alignment
            
        painter.drawText(rect, flags, self.text)
        
    def draw_rich_text(self, painter, rect, color):
        """Draw rich text (HTML formatting)"""
        # Create QTextDocument for rich text rendering
        doc = QtGui.QTextDocument()
        doc.setHtml(self.text)
        doc.setDefaultFont(self.get_text_font())
        
        # Set document width for word wrapping
        if self._word_wrap:
            doc.setTextWidth(rect.width())
        else:
            doc.setTextWidth(-1)
            
        # Set default text color
        doc.setDefaultStyleSheet(f"body {{ color: {color.name()}; }}")
        
        # Translate painter to text position
        painter.save()
        painter.translate(rect.topLeft())
        
        # Clip to text rectangle
        painter.setClipRect(QtCore.QRectF(0, 0, rect.width(), rect.height()))
        
        # Draw the document
        doc.drawContents(painter)
        painter.restore()
        
    def get_text_font(self):
        """Get configured font"""
        font = QtGui.QFont(self.font_family, self.font_size)
        font.setBold(self.font_bold)
        font.setItalic(self.font_italic)
        
        # Apply line spacing
        if self._line_spacing != 1.0:
            font.setLineSpacing(self._line_spacing)
            
        return font
        
    def set_text(self, text):
        """Set text content"""
        self.text = text
        if self._auto_resize:
            self.update_text_size()
        self.update()
        
    def get_text(self):
        """Get text content"""
        return self.text
        
    def set_rich_text(self, rich_text):
        """Enable/disable rich text (HTML) formatting"""
        self._rich_text = rich_text
        if self._auto_resize:
            self.update_text_size()
        self.update()
        
    def is_rich_text(self):
        """Check if rich text is enabled"""
        return self._rich_text
        
    def set_word_wrap(self, wrap):
        """Enable/disable word wrapping"""
        self._word_wrap = wrap
        if self._auto_resize:
            self.update_text_size()
        self.update()
        
    def set_text_alignment(self, alignment):
        """Set text alignment"""
        self._text_alignment = alignment
        self.update()
        
    def get_text_alignment(self):
        """Get text alignment"""
        return self._text_alignment
        
    def set_line_spacing(self, spacing):
        """Set line spacing multiplier"""
        self._line_spacing = max(0.5, min(3.0, spacing))
        if self._auto_resize:
            self.update_text_size()
        self.update()
        
    def set_letter_spacing(self, spacing):
        """Set letter spacing in pixels"""
        self._letter_spacing = spacing
        if self._auto_resize:
            self.update_text_size()
        self.update()
        
    def set_background_visible(self, visible):
        """Show/hide background"""
        self._background_visible = visible
        self.update()
        
    def set_background_color(self, color):
        """Set background color"""
        self._background_color = color
        self.update()
        
    def set_background_opacity(self, opacity):
        """Set background opacity (0.0 to 1.0)"""
        self._background_opacity = max(0.0, min(1.0, opacity))
        self.update()
        
    def set_border_visible(self, visible):
        """Show/hide border"""
        self._border_visible = visible
        self.update()
        
    def set_border_color(self, color):
        """Set border color"""
        self._border_color = color
        self.update()
        
    def set_border_width(self, width):
        """Set border width"""
        self._border_width = max(1, width)
        self.update()
        
    def set_border_style(self, style):
        """Set border style"""
        self._border_style = style
        self.update()
        
    def set_text_shadow(self, enabled):
        """Enable/disable text shadow"""
        self._text_shadow = enabled
        self.update()
        
    def set_shadow_color(self, color):
        """Set shadow color"""
        self._shadow_color = color
        self.update()
        
    def set_shadow_offset(self, offset):
        """Set shadow offset"""
        self._shadow_offset = offset
        self.update()
        
    def set_auto_resize(self, auto_resize):
        """Enable/disable auto-resizing to fit text"""
        self._auto_resize = auto_resize
        if auto_resize:
            self.update_text_size()
            
    def update_text_size(self):
        """Update size to fit text content"""
        if not self._auto_resize:
            return
            
        # Calculate text size
        font = self.get_text_font()
        
        if self._rich_text:
            # Use QTextDocument for rich text size calculation
            doc = QtGui.QTextDocument()
            doc.setHtml(self.text)
            doc.setDefaultFont(font)
            
            if self._word_wrap and not self._fixed_width:
                doc.setTextWidth(self._max_width)
            else:
                doc.setTextWidth(-1)
                
            text_size = doc.size()
        else:
            # Use QFontMetrics for plain text
            metrics = QtGui.QFontMetrics(font)
            
            if self._word_wrap and not self._fixed_width:
                # Calculate size with word wrapping
                rect = metrics.boundingRect(
                    QtCore.QRect(0, 0, self._max_width, self._max_height),
                    QtCore.Qt.TextWordWrap | self._text_alignment,
                    self.text
                )
                text_size = rect.size()
            else:
                # Single line or no wrapping
                text_size = metrics.boundingRect(self.text).size()
                
        # Apply size constraints
        if not self._fixed_width:
            self._width = max(self._min_width, min(self._max_width, text_size.width() + 10))
        if not self._fixed_height:
            self._height = max(self._min_height, min(self._max_height, text_size.height() + 10))
            
        self.prepareGeometryChange()
        
    def set_size_constraints(self, min_width=None, min_height=None, max_width=None, max_height=None):
        """Set size constraints"""
        if min_width is not None:
            self._min_width = min_width
        if min_height is not None:
            self._min_height = min_height
        if max_width is not None:
            self._max_width = max_width
        if max_height is not None:
            self._max_height = max_height
            
        if self._auto_resize:
            self.update_text_size()
            
    def set_fixed_width(self, width):
        """Set fixed width"""
        self._fixed_width = True
        self._width = width
        self.prepareGeometryChange()
        self.update()
        
    def set_fixed_height(self, height):
        """Set fixed height"""
        self._fixed_height = True
        self._height = height
        self.prepareGeometryChange()
        self.update()
        
    def set_fixed_size(self, width, height):
        """Set fixed size"""
        self._fixed_width = True
        self._fixed_height = True
        self._width = width
        self._height = height
        self.prepareGeometryChange()
        self.update()
        
    def clear_fixed_size(self):
        """Remove fixed size constraints"""
        self._fixed_width = False
        self._fixed_height = False
        if self._auto_resize:
            self.update_text_size()
            
    def mouseDoubleClickEvent(self, event):
        """Handle double click to edit text"""
        if event.button() == QtCore.Qt.LeftButton:
            self.show_text_edit_dialog()
            event.accept()
        else:
            super(TextItem, self).mouseDoubleClickEvent(event)
            
    def show_text_edit_dialog(self):
        """Show text editing dialog"""
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle(f"Edit Text")
        dialog.resize(400, 300)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Text editor
        if self._rich_text:
            text_edit = QtWidgets.QTextEdit()
            text_edit.setHtml(self.text)
        else:
            text_edit = QtWidgets.QPlainTextEdit()
            text_edit.setPlainText(self.text)
            
        layout.addWidget(text_edit)
        
        # Rich text checkbox
        rich_text_cb = QtWidgets.QCheckBox("Rich Text (HTML)")
        rich_text_cb.setChecked(self._rich_text)
        layout.addWidget(rich_text_cb)
        
        # Buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Show dialog
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            # Update text
            if rich_text_cb.isChecked():
                self.set_text(text_edit.toHtml())
                self.set_rich_text(True)
            else:
                self.set_text(text_edit.toPlainText())
                self.set_rich_text(False)
                
    def create_text_styles():
        """Create predefined text styles (static method)"""
        styles = {
            'heading': {
                'font_size': 16,
                'font_bold': True,
                'text_color': QtCore.Qt.darkBlue
            },
            'subheading': {
                'font_size': 12,
                'font_bold': True,
                'text_color': QtCore.Qt.black
            },
            'body': {
                'font_size': 10,
                'font_bold': False,
                'text_color': QtCore.Qt.black
            },
            'caption': {
                'font_size': 8,
                'font_italic': True,
                'text_color': QtCore.Qt.gray
            },
            'label': {
                'font_size': 9,
                'font_bold': True,
                'background_visible': True,
                'background_color': QtCore.Qt.lightGray,
                'border_visible': True
            }
        }
        return styles
        
    def apply_text_style(self, style_name):
        """Apply predefined text style"""
        styles = self.create_text_styles()
        if style_name in styles:
            style = styles[style_name]
            
            for attr, value in style.items():
                if hasattr(self, attr):
                    setattr(self, attr, value)
                elif hasattr(self, f"_{attr}"):
                    setattr(self, f"_{attr}", value)
                    
            if self._auto_resize:
                self.update_text_size()
            self.update()
            
    def to_dict(self):
        """Serialize to dictionary"""
        data = super(TextItem, self).to_dict()
        data.update({
            'rich_text': self._rich_text,
            'word_wrap': self._word_wrap,
            'text_alignment': int(self._text_alignment),
            'line_spacing': self._line_spacing,
            'letter_spacing': self._letter_spacing,
            'background_visible': self._background_visible,
            'background_color': self._background_color.name() if hasattr(self._background_color, 'name') else str(self._background_color),
            'background_opacity': self._background_opacity,
            'border_visible': self._border_visible,
            'border_color': self._border_color.name() if hasattr(self._border_color, 'name') else str(self._border_color),
            'border_width': self._border_width,
            'border_style': int(self._border_style),
            'text_shadow': self._text_shadow,
            'shadow_color': self._shadow_color.name() if hasattr(self._shadow_color, 'name') else str(self._shadow_color),
            'shadow_offset': (self._shadow_offset.x(), self._shadow_offset.y()),
            'shadow_blur_radius': self._shadow_blur_radius,
            'auto_resize': self._auto_resize,
            'fixed_width': self._fixed_width,
            'fixed_height': self._fixed_height,
            'width': self._width,
            'height': self._height
        })
        return data
        
    def from_dict(self, data):
        """Deserialize from dictionary"""
        super(TextItem, self).from_dict(data)
        
        self._rich_text = data.get('rich_text', False)
        self._word_wrap = data.get('word_wrap', True)
        self._text_alignment = QtCore.Qt.Alignment(data.get('text_alignment', QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop))
        self._line_spacing = data.get('line_spacing', 1.0)
        self._letter_spacing = data.get('letter_spacing', 0.0)
        self._background_visible = data.get('background_visible', False)
        self._background_opacity = data.get('background_opacity', 0.8)
        self._border_visible = data.get('border_visible', False)
        self._border_width = data.get('border_width', 1)
        self._border_style = QtCore.Qt.PenStyle(data.get('border_style', QtCore.Qt.SolidLine))
        self._text_shadow = data.get('text_shadow', False)
        self._shadow_blur_radius = data.get('shadow_blur_radius', 0)
        self._auto_resize = data.get('auto_resize', True)
        self._fixed_width = data.get('fixed_width', False)
        self._fixed_height = data.get('fixed_height', False)
        self._width = data.get('width', 120)
        self._height = data.get('height', 30)
        
        # Colors
        if 'background_color' in data:
            self._background_color = QtGui.QColor(data['background_color'])
        if 'border_color' in data:
            self._border_color = QtGui.QColor(data['border_color'])
        if 'shadow_color' in data:
            self._shadow_color = QtGui.QColor(data['shadow_color'])
            
        # Shadow offset
        if 'shadow_offset' in data:
            x, y = data['shadow_offset']
            self._shadow_offset = QtCore.QPointF(x, y)
