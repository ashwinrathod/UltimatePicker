# File: ui/tab_widget.py
"""
Enhanced Tab Widget for Ultimate Animation Picker
Implements main tabs and subtabs with comprehensive management
"""

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal

class CustomTabBar(QtWidgets.QTabBar):
    """Custom tab bar with right-click context menu support"""
    
    # Signals
    tab_right_clicked = Signal(int, QtCore.QPoint)  # tab_index, global_pos
    tab_double_clicked = Signal(int)  # tab_index
    
    def __init__(self, parent=None):
        super(CustomTabBar, self).__init__(parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == QtCore.Qt.RightButton:
            tab_index = self.tabAt(event.pos())
            if tab_index >= 0:
                self.tab_right_clicked.emit(tab_index, event.globalPos())
                return
        super(CustomTabBar, self).mousePressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        """Handle double click events"""
        if event.button() == QtCore.Qt.LeftButton:
            tab_index = self.tabAt(event.pos())
            if tab_index >= 0:
                self.tab_double_clicked.emit(tab_index)
                return
        super(CustomTabBar, self).mouseDoubleClickEvent(event)


class TabContextMenu(QtWidgets.QMenu):
    """Context menu for tab operations"""
    
    # Signals
    rename_requested = Signal(int)  # tab_index
    delete_requested = Signal(int)  # tab_index
    duplicate_requested = Signal(int)  # tab_index
    move_left_requested = Signal(int)  # tab_index
    move_right_requested = Signal(int)  # tab_index
    
    def __init__(self, tab_index, is_main_tab=True, can_delete=True, parent=None):
        super(TabContextMenu, self).__init__(parent)
        self.tab_index = tab_index
        self.is_main_tab = is_main_tab
        self.can_delete = can_delete
        
        self.setup_menu()
        
    def setup_menu(self):
        """Setup context menu actions"""
        # Rename action
        rename_action = self.addAction("Rename")
        rename_action.triggered.connect(lambda: self.rename_requested.emit(self.tab_index))
        
        self.addSeparator()
        
        # Duplicate action
        duplicate_action = self.addAction("Duplicate")
        duplicate_action.triggered.connect(lambda: self.duplicate_requested.emit(self.tab_index))
        
        self.addSeparator()
        
        # Move actions
        move_left_action = self.addAction("Move Left")
        move_left_action.triggered.connect(lambda: self.move_left_requested.emit(self.tab_index))
        
        move_right_action = self.addAction("Move Right")
        move_right_action.triggered.connect(lambda: self.move_right_requested.emit(self.tab_index))
        
        self.addSeparator()
        
        # Delete action
        delete_action = self.addAction("Delete")
        delete_action.setEnabled(self.can_delete)
        delete_action.triggered.connect(lambda: self.delete_requested.emit(self.tab_index))
        
        if not self.can_delete:
            delete_action.setToolTip("Cannot delete the last tab")


class EnhancedTabWidget(QtWidgets.QWidget):
    """Enhanced tab widget with main tabs and subtabs"""
    
    # Signals
    main_tab_changed = Signal(int, str)  # index, name
    sub_tab_changed = Signal(int, str)   # index, name
    tab_renamed = Signal(bool, int, str, str)  # is_main_tab, index, old_name, new_name
    tab_deleted = Signal(bool, int, str)  # is_main_tab, index, name
    tab_added = Signal(bool, int, str)    # is_main_tab, index, name
    
    def __init__(self, parent=None):
        super(EnhancedTabWidget, self).__init__(parent)
        
        self._main_tabs = []  # List of main tab names
        self._sub_tabs = {}   # main_tab_name -> list of sub tab names
        self._current_main_tab = -1
        self._current_sub_tab = -1
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup tab widget UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Main tabs section
        main_tab_layout = QtWidgets.QHBoxLayout()
        main_tab_layout.setContentsMargins(5, 0, 5, 0)
        
        # Main tab bar
        self.main_tab_bar = CustomTabBar()
        self.main_tab_bar.setTabsClosable(False)
        self.main_tab_bar.setMovable(True)
        self.main_tab_bar.setExpanding(False)
        main_tab_layout.addWidget(self.main_tab_bar)
        
        # Add main tab button
        self.add_main_tab_btn = QtWidgets.QPushButton("+")
        self.add_main_tab_btn.setMaximumSize(25, 25)
        self.add_main_tab_btn.setMinimumSize(25, 25)
        self.add_main_tab_btn.setToolTip("Add Main Tab")
        self.add_main_tab_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 12px;
            }
        """)
        main_tab_layout.addWidget(self.add_main_tab_btn)
        
        main_tab_layout.addStretch()
        layout.addLayout(main_tab_layout)
        
        # Sub tabs section
        sub_tab_layout = QtWidgets.QHBoxLayout()
        sub_tab_layout.setContentsMargins(25, 0, 5, 0)
        
        # Sub tab bar
        self.sub_tab_bar = CustomTabBar()
        self.sub_tab_bar.setTabsClosable(False)
        self.sub_tab_bar.setMovable(True)
        self.sub_tab_bar.setExpanding(False)
        sub_tab_layout.addWidget(self.sub_tab_bar)
        
        # Add sub tab button
        self.add_sub_tab_btn = QtWidgets.QPushButton("+")
        self.add_sub_tab_btn.setMaximumSize(25, 25)
        self.add_sub_tab_btn.setMinimumSize(25, 25)
        self.add_sub_tab_btn.setToolTip("Add Sub Tab")
        self.add_sub_tab_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 12px;
            }
        """)
        sub_tab_layout.addWidget(self.add_sub_tab_btn)
        
        sub_tab_layout.addStretch()
        layout.addLayout(sub_tab_layout)
        
        # Tab content area (placeholder)
        self.content_frame = QtWidgets.QFrame()
        self.content_frame.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.content_frame.setMinimumHeight(50)
        layout.addWidget(self.content_frame)
        
    def connect_signals(self):
        """Connect signals"""
        # Main tab signals
        self.main_tab_bar.currentChanged.connect(self.on_main_tab_changed)
        self.main_tab_bar.tab_right_clicked.connect(self.show_main_tab_context_menu)
        self.main_tab_bar.tab_double_clicked.connect(self.rename_main_tab)
        self.add_main_tab_btn.clicked.connect(self.add_main_tab)
        
        # Sub tab signals
        self.sub_tab_bar.currentChanged.connect(self.on_sub_tab_changed)
        self.sub_tab_bar.tab_right_clicked.connect(self.show_sub_tab_context_menu)
        self.sub_tab_bar.tab_double_clicked.connect(self.rename_sub_tab)
        self.add_sub_tab_btn.clicked.connect(self.add_sub_tab)
        
    def add_main_tab(self, name=None):
        """Add a new main tab"""
        if name is None:
            name = self.get_unique_main_tab_name("Character")
            
        # Add to internal list
        self._main_tabs.append(name)
        self._sub_tabs[name] = ["Default"]
        
        # Add to tab bar
        index = self.main_tab_bar.addTab(name)
        
        # Select new tab
        self.main_tab_bar.setCurrentIndex(index)
        
        # Emit signal
        self.tab_added.emit(True, index, name)
        
        return index
        
    def add_sub_tab(self, name=None):
        """Add a new sub tab to current main tab"""
        if self._current_main_tab < 0 or self._current_main_tab >= len(self._main_tabs):
            return -1
            
        main_tab_name = self._main_tabs[self._current_main_tab]
        
        if name is None:
            name = self.get_unique_sub_tab_name(main_tab_name, "SubTab")
            
        # Add to internal list
        self._sub_tabs[main_tab_name].append(name)
        
        # Add to tab bar
        index = self.sub_tab_bar.addTab(name)
        
        # Select new tab
        self.sub_tab_bar.setCurrentIndex(index)
        
        # Emit signal
        self.tab_added.emit(False, index, name)
        
        return index
        
    def get_unique_main_tab_name(self, base_name):
        """Get unique main tab name"""
        if base_name not in self._main_tabs:
            return base_name
            
        counter = 1
        while f"{base_name}_{counter}" in self._main_tabs:
            counter += 1
        return f"{base_name}_{counter}"
        
    def get_unique_sub_tab_name(self, main_tab_name, base_name):
        """Get unique sub tab name"""
        if main_tab_name not in self._sub_tabs:
            return base_name
            
        sub_tabs = self._sub_tabs[main_tab_name]
        if base_name not in sub_tabs:
            return base_name
            
        counter = 1
        while f"{base_name}_{counter}" in sub_tabs:
            counter += 1
        return f"{base_name}_{counter}"
        
    def on_main_tab_changed(self, index):
        """Handle main tab change"""
        if index < 0 or index >= len(self._main_tabs):
            return
            
        self._current_main_tab = index
        main_tab_name = self._main_tabs[index]
        
        # Update sub tabs
        self.update_sub_tabs(main_tab_name)
        
        # Emit signal
        self.main_tab_changed.emit(index, main_tab_name)
        
    def on_sub_tab_changed(self, index):
        """Handle sub tab change"""
        if self._current_main_tab < 0 or index < 0:
            return
            
        main_tab_name = self._main_tabs[self._current_main_tab]
        sub_tabs = self._sub_tabs.get(main_tab_name, [])
        
        if index >= len(sub_tabs):
            return
            
        self._current_sub_tab = index
        sub_tab_name = sub_tabs[index]
        
        # Emit signal
        self.sub_tab_changed.emit(index, sub_tab_name)
        
    def update_sub_tabs(self, main_tab_name):
        """Update sub tab bar for main tab"""
        # Clear current sub tabs
        self.sub_tab_bar.clear()
        
        # Add sub tabs for main tab
        sub_tabs = self._sub_tabs.get(main_tab_name, [])
        for sub_tab_name in sub_tabs:
            self.sub_tab_bar.addTab(sub_tab_name)
            
        # Select first sub tab
        if sub_tabs:
            self.sub_tab_bar.setCurrentIndex(0)
            self._current_sub_tab = 0
        else:
            self._current_sub_tab = -1
            
    def show_main_tab_context_menu(self, tab_index, global_pos):
        """Show context menu for main tab"""
        can_delete = len(self._main_tabs) > 1
        menu = TabContextMenu(tab_index, is_main_tab=True, can_delete=can_delete, parent=self)
        
        # Connect signals
        menu.rename_requested.connect(self.rename_main_tab)
        menu.delete_requested.connect(self.delete_main_tab)
        menu.duplicate_requested.connect(self.duplicate_main_tab)
        menu.move_left_requested.connect(self.move_main_tab_left)
        menu.move_right_requested.connect(self.move_main_tab_right)
        
        menu.exec_(global_pos)
        
    def show_sub_tab_context_menu(self, tab_index, global_pos):
        """Show context menu for sub tab"""
        if self._current_main_tab < 0:
            return
            
        main_tab_name = self._main_tabs[self._current_main_tab]
        can_delete = len(self._sub_tabs.get(main_tab_name, [])) > 1
        
        menu = TabContextMenu(tab_index, is_main_tab=False, can_delete=can_delete, parent=self)
        
        # Connect signals
        menu.rename_requested.connect(self.rename_sub_tab)
        menu.delete_requested.connect(self.delete_sub_tab)
        menu.duplicate_requested.connect(self.duplicate_sub_tab)
        menu.move_left_requested.connect(self.move_sub_tab_left)
        menu.move_right_requested.connect(self.move_sub_tab_right)
        
        menu.exec_(global_pos)
        
    def rename_main_tab(self, tab_index):
        """Rename main tab"""
        if tab_index < 0 or tab_index >= len(self._main_tabs):
            return
            
        old_name = self._main_tabs[tab_index]
        
        new_name, ok = QtWidgets.QInputDialog.getText(
            self,
            "Rename Main Tab",
            "Enter new name:",
            QtWidgets.QLineEdit.Normal,
            old_name
        )
        
        if ok and new_name and new_name != old_name:
            # Check for uniqueness
            if new_name in self._main_tabs:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Name Conflict",
                    f"A main tab named '{new_name}' already exists."
                )
                return
                
            # Update internal data
            self._main_tabs[tab_index] = new_name
            if old_name in self._sub_tabs:
                self._sub_tabs[new_name] = self._sub_tabs.pop(old_name)
                
            # Update tab bar
            self.main_tab_bar.setTabText(tab_index, new_name)
            
            # Emit signal
            self.tab_renamed.emit(True, tab_index, old_name, new_name)
            
    def rename_sub_tab(self, tab_index):
        """Rename sub tab"""
        if self._current_main_tab < 0 or tab_index < 0:
            return
            
        main_tab_name = self._main_tabs[self._current_main_tab]
        sub_tabs = self._sub_tabs.get(main_tab_name, [])
        
        if tab_index >= len(sub_tabs):
            return
            
        old_name = sub_tabs[tab_index]
        
        new_name, ok = QtWidgets.QInputDialog.getText(
            self,
            "Rename Sub Tab",
            "Enter new name:",
            QtWidgets.QLineEdit.Normal,
            old_name
        )
        
        if ok and new_name and new_name != old_name:
            # Check for uniqueness
            if new_name in sub_tabs:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Name Conflict",
                    f"A sub tab named '{new_name}' already exists in this main tab."
                )
                return
                
            # Update internal data
            self._sub_tabs[main_tab_name][tab_index] = new_name
            
            # Update tab bar
            self.sub_tab_bar.setTabText(tab_index, new_name)
            
            # Emit signal
            self.tab_renamed.emit(False, tab_index, old_name, new_name)
            
    def delete_main_tab(self, tab_index):
        """Delete main tab"""
        if tab_index < 0 or tab_index >= len(self._main_tabs) or len(self._main_tabs) <= 1:
            return
            
        tab_name = self._main_tabs[tab_index]
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "Delete Main Tab",
            f"Are you sure you want to delete the main tab '{tab_name}' and all its sub tabs?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # Remove from internal data
            self._main_tabs.pop(tab_index)
            if tab_name in self._sub_tabs:
                del self._sub_tabs[tab_name]
                
            # Remove from tab bar
            self.main_tab_bar.removeTab(tab_index)
            
            # Update current index
            if self._current_main_tab >= tab_index:
                self._current_main_tab = max(0, self._current_main_tab - 1)
                
            # Emit signal
            self.tab_deleted.emit(True, tab_index, tab_name)
            
    def delete_sub_tab(self, tab_index):
        """Delete sub tab"""
        if self._current_main_tab < 0 or tab_index < 0:
            return
            
        main_tab_name = self._main_tabs[self._current_main_tab]
        sub_tabs = self._sub_tabs.get(main_tab_name, [])
        
        if tab_index >= len(sub_tabs) or len(sub_tabs) <= 1:
            return
            
        tab_name = sub_tabs[tab_index]
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "Delete Sub Tab",
            f"Are you sure you want to delete the sub tab '{tab_name}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # Remove from internal data
            self._sub_tabs[main_tab_name].pop(tab_index)
            
            # Remove from tab bar
            self.sub_tab_bar.removeTab(tab_index)
            
            # Update current index
            if self._current_sub_tab >= tab_index:
                self._current_sub_tab = max(0, self._current_sub_tab - 1)
                
            # Emit signal
            self.tab_deleted.emit(False, tab_index, tab_name)
            
    def duplicate_main_tab(self, tab_index):
        """Duplicate main tab"""
        if tab_index < 0 or tab_index >= len(self._main_tabs):
            return
            
        original_name = self._main_tabs[tab_index]
        new_name = self.get_unique_main_tab_name(f"{original_name}_Copy")
        
        # Copy sub tabs
        original_sub_tabs = self._sub_tabs.get(original_name, [])
        self._sub_tabs[new_name] = original_sub_tabs[:]
        
        # Add new main tab
        self.add_main_tab(new_name)
        
    def duplicate_sub_tab(self, tab_index):
        """Duplicate sub tab"""
        if self._current_main_tab < 0 or tab_index < 0:
            return
            
        main_tab_name = self._main_tabs[self._current_main_tab]
        sub_tabs = self._sub_tabs.get(main_tab_name, [])
        
        if tab_index >= len(sub_tabs):
            return
            
        original_name = sub_tabs[tab_index]
        new_name = self.get_unique_sub_tab_name(main_tab_name, f"{original_name}_Copy")
        
        # Add new sub tab
        self.add_sub_tab(new_name)
        
    def move_main_tab_left(self, tab_index):
        """Move main tab left"""
        if tab_index <= 0 or tab_index >= len(self._main_tabs):
            return
            
        # Swap in internal list
        self._main_tabs[tab_index], self._main_tabs[tab_index - 1] = \
            self._main_tabs[tab_index - 1], self._main_tabs[tab_index]
            
        # Move in tab bar
        self.main_tab_bar.moveTab(tab_index, tab_index - 1)
        
    def move_main_tab_right(self, tab_index):
        """Move main tab right"""
        if tab_index < 0 or tab_index >= len(self._main_tabs) - 1:
            return
            
        # Swap in internal list
        self._main_tabs[tab_index], self._main_tabs[tab_index + 1] = \
            self._main_tabs[tab_index + 1], self._main_tabs[tab_index]
            
        # Move in tab bar
        self.main_tab_bar.moveTab(tab_index, tab_index + 1)
        
    def move_sub_tab_left(self, tab_index):
        """Move sub tab left"""
        if self._current_main_tab < 0 or tab_index <= 0:
            return
            
        main_tab_name = self._main_tabs[self._current_main_tab]
        sub_tabs = self._sub_tabs.get(main_tab_name, [])
        
        if tab_index >= len(sub_tabs):
            return
            
        # Swap in internal list
        sub_tabs[tab_index], sub_tabs[tab_index - 1] = \
            sub_tabs[tab_index - 1], sub_tabs[tab_index]
            
        # Move in tab bar
        self.sub_tab_bar.moveTab(tab_index, tab_index - 1)
        
    def move_sub_tab_right(self, tab_index):
        """Move sub tab right"""
        if self._current_main_tab < 0 or tab_index < 0:
            return
            
        main_tab_name = self._main_tabs[self._current_main_tab]
        sub_tabs = self._sub_tabs.get(main_tab_name, [])
        
        if tab_index >= len(sub_tabs) - 1:
            return
            
        # Swap in internal list
        sub_tabs[tab_index], sub_tabs[tab_index + 1] = \
            sub_tabs[tab_index + 1], sub_tabs[tab_index]
            
        # Move in tab bar
        self.sub_tab_bar.moveTab(tab_index, tab_index + 1)
        
    def get_current_main_tab(self):
        """Get current main tab info"""
        if self._current_main_tab >= 0 and self._current_main_tab < len(self._main_tabs):
            return self._current_main_tab, self._main_tabs[self._current_main_tab]
        return -1, ""
        
    def get_current_sub_tab(self):
        """Get current sub tab info"""
        if self._current_main_tab < 0 or self._current_sub_tab < 0:
            return -1, ""
            
        main_tab_name = self._main_tabs[self._current_main_tab]
        sub_tabs = self._sub_tabs.get(main_tab_name, [])
        
        if self._current_sub_tab < len(sub_tabs):
            return self._current_sub_tab, sub_tabs[self._current_sub_tab]
        return -1, ""
        
    def set_current_tabs(self, main_tab_name, sub_tab_name=None):
        """Set current main and sub tab"""
        # Find main tab
        try:
            main_index = self._main_tabs.index(main_tab_name)
            self.main_tab_bar.setCurrentIndex(main_index)
            
            # Find sub tab if specified
            if sub_tab_name:
                sub_tabs = self._sub_tabs.get(main_tab_name, [])
                try:
                    sub_index = sub_tabs.index(sub_tab_name)
                    self.sub_tab_bar.setCurrentIndex(sub_index)
                except ValueError:
                    pass  # Sub tab not found
                    
        except ValueError:
            pass  # Main tab not found
            
    def initialize_default_tabs(self):
        """Initialize with default tab structure"""
        if not self._main_tabs:
            self.add_main_tab("Character")
