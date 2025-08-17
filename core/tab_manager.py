# File: core/tab_manager.py
"""
Tab Manager for Ultimate Animation Picker
Handles main tabs and subtabs with JSON save/load functionality
"""

import json
import os
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal

class TabManager(QtCore.QObject):
    """Manages tabs and subtabs for the picker"""
    
    # Signals
    tab_changed = Signal(str, str)  # main_tab, sub_tab
    tab_created = Signal(str, str)  # main_tab, sub_tab
    tab_deleted = Signal(str, str)  # main_tab, sub_tab
    tab_renamed = Signal(str, str, str, str)  # old_main, old_sub, new_main, new_sub
    
    def __init__(self, parent=None):
        super(TabManager, self).__init__(parent)
        self._tabs = {}  # main_tab -> {subtabs: [list], data: {subtab: data}}
        self._current_main_tab = None
        self._current_sub_tab = None
        
    def create_main_tab(self, name):
        """Create a new main tab"""
        if name in self._tabs:
            return False
            
        self._tabs[name] = {
            'subtabs': ['Default'],
            'data': {'Default': {'items': [], 'canvas_settings': {}}}
        }
        
        if self._current_main_tab is None:
            self._current_main_tab = name
            self._current_sub_tab = 'Default'
            
        self.tab_created.emit(name, 'Default')
        return True
        
    def create_sub_tab(self, main_tab, sub_name):
        """Create a new subtab under main tab"""
        if main_tab not in self._tabs:
            return False
            
        if sub_name in self._tabs[main_tab]['subtabs']:
            return False
            
        self._tabs[main_tab]['subtabs'].append(sub_name)
        self._tabs[main_tab]['data'][sub_name] = {'items': [], 'canvas_settings': {}}
        
        self.tab_created.emit(main_tab, sub_name)
        return True
        
    def delete_main_tab(self, name):
        """Delete a main tab and all its subtabs"""
        if name not in self._tabs or len(self._tabs) <= 1:
            return False
            
        # Find next available tab
        remaining_tabs = [tab for tab in self._tabs.keys() if tab != name]
        next_tab = remaining_tabs[0] if remaining_tabs else None
        
        del self._tabs[name]
        
        if self._current_main_tab == name:
            self._current_main_tab = next_tab
            self._current_sub_tab = self._tabs[next_tab]['subtabs'][0] if next_tab else None
            
        self.tab_deleted.emit(name, '')
        return True
        
    def delete_sub_tab(self, main_tab, sub_name):
        """Delete a subtab"""
        if main_tab not in self._tabs:
            return False
            
        if sub_name not in self._tabs[main_tab]['subtabs'] or len(self._tabs[main_tab]['subtabs']) <= 1:
            return False
            
        self._tabs[main_tab]['subtabs'].remove(sub_name)
        del self._tabs[main_tab]['data'][sub_name]
        
        # Update current subtab if deleted
        if self._current_main_tab == main_tab and self._current_sub_tab == sub_name:
            self._current_sub_tab = self._tabs[main_tab]['subtabs'][0]
            
        self.tab_deleted.emit(main_tab, sub_name)
        return True
        
    def rename_main_tab(self, old_name, new_name):
        """Rename a main tab"""
        if old_name not in self._tabs or new_name in self._tabs:
            return False
            
        self._tabs[new_name] = self._tabs.pop(old_name)
        
        if self._current_main_tab == old_name:
            self._current_main_tab = new_name
            
        self.tab_renamed.emit(old_name, '', new_name, '')
        return True
        
    def rename_sub_tab(self, main_tab, old_name, new_name):
        """Rename a subtab"""
        if main_tab not in self._tabs:
            return False
            
        if old_name not in self._tabs[main_tab]['subtabs'] or new_name in self._tabs[main_tab]['subtabs']:
            return False
            
        # Update subtabs list
        idx = self._tabs[main_tab]['subtabs'].index(old_name)
        self._tabs[main_tab]['subtabs'][idx] = new_name
        
        # Update data dictionary
        self._tabs[main_tab]['data'][new_name] = self._tabs[main_tab]['data'].pop(old_name)
        
        if self._current_main_tab == main_tab and self._current_sub_tab == old_name:
            self._current_sub_tab = new_name
            
        self.tab_renamed.emit(main_tab, old_name, main_tab, new_name)
        return True
        
    def set_current_tab(self, main_tab, sub_tab=None):
        """Set the current active tab"""
        if main_tab not in self._tabs:
            return False
            
        if sub_tab is None:
            sub_tab = self._tabs[main_tab]['subtabs'][0]
        elif sub_tab not in self._tabs[main_tab]['subtabs']:
            return False
            
        self._current_main_tab = main_tab
        self._current_sub_tab = sub_tab
        self.tab_changed.emit(main_tab, sub_tab)
        return True
        
    def get_current_tab(self):
        """Get current main and sub tab"""
        return self._current_main_tab, self._current_sub_tab
        
    def get_main_tabs(self):
        """Get list of main tabs"""
        return list(self._tabs.keys())
        
    def get_sub_tabs(self, main_tab):
        """Get list of subtabs for a main tab"""
        if main_tab in self._tabs:
            return self._tabs[main_tab]['subtabs'][:]
        return []
        
    def save_tab_data(self, main_tab, sub_tab, data):
        """Save data for a specific tab"""
        if main_tab not in self._tabs or sub_tab not in self._tabs[main_tab]['subtabs']:
            return False
            
        self._tabs[main_tab]['data'][sub_tab] = data
        return True
        
    def get_tab_data(self, main_tab, sub_tab):
        """Get data for a specific tab"""
        if main_tab not in self._tabs or sub_tab not in self._tabs[main_tab]['subtabs']:
            return None
            
        return self._tabs[main_tab]['data'][sub_tab]
        
    def get_current_tab_data(self):
        """Get data for current tab"""
        if self._current_main_tab and self._current_sub_tab:
            return self.get_tab_data(self._current_main_tab, self._current_sub_tab)
        return None
        
    def save_to_file(self, filepath, main_tab=None):
        """Save tab data to JSON file"""
        try:
            if main_tab is None:
                main_tab = self._current_main_tab
                
            if main_tab not in self._tabs:
                return False
                
            save_data = {
                'main_tab': main_tab,
                'tabs': self._tabs[main_tab]
            }
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving tab data: {e}")
            return False
            
    def load_from_file(self, filepath):
        """Load tab data from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            main_tab = data.get('main_tab', 'Loaded')
            tabs_data = data.get('tabs', {})
            
            # Ensure unique main tab name
            original_name = main_tab
            counter = 1
            while main_tab in self._tabs:
                main_tab = f"{original_name}_{counter}"
                counter += 1
                
            self._tabs[main_tab] = tabs_data
            
            # Set as current tab
            self._current_main_tab = main_tab
            self._current_sub_tab = tabs_data['subtabs'][0] if tabs_data['subtabs'] else 'Default'
            
            self.tab_created.emit(main_tab, self._current_sub_tab)
            return True
            
        except Exception as e:
            print(f"Error loading tab data: {e}")
            return False
            
    def initialize_default(self):
        """Initialize with default tab structure"""
        if not self._tabs:
            self.create_main_tab('Character')


class UltimateTabWidget(QtWidgets.QWidget):
    """Custom tab widget with main and sub tabs"""
    
    # Signals
    tab_changed = Signal(str, str)
    tab_context_menu = Signal(str, str, QtCore.QPoint)
    add_main_tab_requested = Signal()
    add_sub_tab_requested = Signal()
    
    def __init__(self, parent=None):
        super(UltimateTabWidget, self).__init__(parent)
        self.tab_manager = TabManager(self)
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup the tab widget UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main tabs
        main_tab_layout = QtWidgets.QHBoxLayout()
        main_tab_layout.setContentsMargins(5, 0, 5, 0)
        
        self.main_tab_bar = QtWidgets.QTabBar()
        self.main_tab_bar.setTabsClosable(False)
        self.main_tab_bar.setMovable(True)
        self.main_tab_bar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        self.add_main_tab_btn = QtWidgets.QPushButton("+")
        self.add_main_tab_btn.setMaximumSize(25, 25)
        self.add_main_tab_btn.setToolTip("Add Main Tab")
        
        main_tab_layout.addWidget(self.main_tab_bar)
        main_tab_layout.addWidget(self.add_main_tab_btn)
        main_tab_layout.addStretch()
        
        # Sub tabs
        sub_tab_layout = QtWidgets.QHBoxLayout()
        sub_tab_layout.setContentsMargins(20, 0, 5, 0)
        
        self.sub_tab_bar = QtWidgets.QTabBar()
        self.sub_tab_bar.setTabsClosable(False)
        self.sub_tab_bar.setMovable(True)
        self.sub_tab_bar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        self.add_sub_tab_btn = QtWidgets.QPushButton("+")
        self.add_sub_tab_btn.setMaximumSize(25, 25)
        self.add_sub_tab_btn.setToolTip("Add Sub Tab")
        
        sub_tab_layout.addWidget(self.sub_tab_bar)
        sub_tab_layout.addWidget(self.add_sub_tab_btn)
        sub_tab_layout.addStretch()
        
        layout.addLayout(main_tab_layout)
        layout.addLayout(sub_tab_layout)
        
    def connect_signals(self):
        """Connect signals"""
        self.main_tab_bar.currentChanged.connect(self._on_main_tab_changed)
        self.sub_tab_bar.currentChanged.connect(self._on_sub_tab_changed)
        self.main_tab_bar.customContextMenuRequested.connect(self._show_main_tab_context_menu)
        self.sub_tab_bar.customContextMenuRequested.connect(self._show_sub_tab_context_menu)
        self.add_main_tab_btn.clicked.connect(self.add_main_tab_requested.emit)
        self.add_sub_tab_btn.clicked.connect(self.add_sub_tab_requested.emit)
        
        self.tab_manager.tab_created.connect(self._on_tab_created)
        self.tab_manager.tab_deleted.connect(self._on_tab_deleted)
        self.tab_manager.tab_renamed.connect(self._on_tab_renamed)
        
    def _on_main_tab_changed(self, index):
        """Handle main tab change"""
        if index >= 0:
            main_tab = self.main_tab_bar.tabText(index)
            sub_tabs = self.tab_manager.get_sub_tabs(main_tab)
            
            # Update sub tab bar
            self.sub_tab_bar.clear()
            for sub_tab in sub_tabs:
                self.sub_tab_bar.addTab(sub_tab)
                
            # Set current tab
            if sub_tabs:
                self.tab_manager.set_current_tab(main_tab, sub_tabs[0])
                
    def _on_sub_tab_changed(self, index):
        """Handle sub tab change"""
        if index >= 0:
            main_tab_index = self.main_tab_bar.currentIndex()
            if main_tab_index >= 0:
                main_tab = self.main_tab_bar.tabText(main_tab_index)
                sub_tab = self.sub_tab_bar.tabText(index)
                self.tab_manager.set_current_tab(main_tab, sub_tab)
                
    def _on_tab_created(self, main_tab, sub_tab):
        """Handle tab creation"""
        # Update main tab bar if needed
        for i in range(self.main_tab_bar.count()):
            if self.main_tab_bar.tabText(i) == main_tab:
                break
        else:
            self.main_tab_bar.addTab(main_tab)
            
        # Update sub tab bar if this is the current main tab
        current_main = self.main_tab_bar.tabText(self.main_tab_bar.currentIndex())
        if current_main == main_tab:
            self.sub_tab_bar.addTab(sub_tab)
            
    def _on_tab_deleted(self, main_tab, sub_tab):
        """Handle tab deletion"""
        if sub_tab:  # Sub tab deleted
            current_main = self.main_tab_bar.tabText(self.main_tab_bar.currentIndex())
            if current_main == main_tab:
                # Remove from sub tab bar
                for i in range(self.sub_tab_bar.count()):
                    if self.sub_tab_bar.tabText(i) == sub_tab:
                        self.sub_tab_bar.removeTab(i)
                        break
        else:  # Main tab deleted
            for i in range(self.main_tab_bar.count()):
                if self.main_tab_bar.tabText(i) == main_tab:
                    self.main_tab_bar.removeTab(i)
                    break
                    
    def _on_tab_renamed(self, old_main, old_sub, new_main, new_sub):
        """Handle tab rename"""
        if old_sub:  # Sub tab renamed
            current_main = self.main_tab_bar.tabText(self.main_tab_bar.currentIndex())
            if current_main == old_main:
                for i in range(self.sub_tab_bar.count()):
                    if self.sub_tab_bar.tabText(i) == old_sub:
                        self.sub_tab_bar.setTabText(i, new_sub)
                        break
        else:  # Main tab renamed
            for i in range(self.main_tab_bar.count()):
                if self.main_tab_bar.tabText(i) == old_main:
                    self.main_tab_bar.setTabText(i, new_main)
                    break
                    
    def _show_main_tab_context_menu(self, pos):
        """Show context menu for main tab"""
        index = self.main_tab_bar.tabAt(pos)
        if index >= 0:
            main_tab = self.main_tab_bar.tabText(index)
            global_pos = self.main_tab_bar.mapToGlobal(pos)
            self.tab_context_menu.emit(main_tab, '', global_pos)
            
    def _show_sub_tab_context_menu(self, pos):
        """Show context menu for sub tab"""
        main_index = self.main_tab_bar.currentIndex()
        sub_index = self.sub_tab_bar.tabAt(pos)
        
        if main_index >= 0 and sub_index >= 0:
            main_tab = self.main_tab_bar.tabText(main_index)
            sub_tab = self.sub_tab_bar.tabText(sub_index)
            global_pos = self.sub_tab_bar.mapToGlobal(pos)
            self.tab_context_menu.emit(main_tab, sub_tab, global_pos)
            
    def initialize_default_tabs(self):
        """Initialize with default tabs"""
        self.tab_manager.initialize_default()
        
        # Update UI
        main_tabs = self.tab_manager.get_main_tabs()
        for main_tab in main_tabs:
            self.main_tab_bar.addTab(main_tab)
            
        if main_tabs:
            self.main_tab_bar.setCurrentIndex(0)
