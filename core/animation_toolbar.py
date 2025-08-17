# File: core/animation_toolbar.py
"""
Animation Toolbar for Ultimate Animation Picker
Provides pose and animation copy/paste/mirror functionality
"""

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal
import maya.cmds as cmds

class AnimationToolbar(QtWidgets.QToolBar):
    """Animation toolbar with pose and animation tools"""
    
    # Signals for animation operations
    copy_pose_requested = Signal()
    paste_pose_requested = Signal()
    copy_world_pose_requested = Signal()
    paste_world_pose_requested = Signal()
    mirror_pose_requested = Signal()
    copy_animation_requested = Signal()
    paste_animation_requested = Signal()
    copy_world_animation_requested = Signal()
    paste_world_animation_requested = Signal()
    mirror_animation_requested = Signal()
    
    def __init__(self, parent=None):
        super(AnimationToolbar, self).__init__("Animation Tools", parent)
        self.setObjectName("AnimationToolbar")
        self.setup_toolbar()
        
    def setup_toolbar(self):
        """Setup animation toolbar buttons"""
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.setMovable(False)
        
        # Pose operations
        self.add_separator_with_label("Pose Operations")
        
        # Copy Pose
        copy_pose_action = QtWidgets.QAction("Copy Pose", self)
        copy_pose_action.setStatusTip("Copy current pose from selected objects")
        copy_pose_action.triggered.connect(self.copy_pose_requested.emit)
        self.addAction(copy_pose_action)
        
        # Paste Pose
        paste_pose_action = QtWidgets.QAction("Paste Pose", self)
        paste_pose_action.setStatusTip("Paste pose to selected objects")
        paste_pose_action.triggered.connect(self.paste_pose_requested.emit)
        self.addAction(paste_pose_action)
        
        # Mirror Pose
        mirror_pose_action = QtWidgets.QAction("Mirror Pose", self)
        mirror_pose_action.setStatusTip("Mirror pose on selected objects")
        mirror_pose_action.triggered.connect(self.mirror_pose_requested.emit)
        self.addAction(mirror_pose_action)
        
        self.addSeparator()
        
        # World Pose operations
        self.add_separator_with_label("World Pose")
        
        # Copy World Pose
        copy_world_pose_action = QtWidgets.QAction("Copy World Pose", self)
        copy_world_pose_action.setStatusTip("Copy current world space pose")
        copy_world_pose_action.triggered.connect(self.copy_world_pose_requested.emit)
        self.addAction(copy_world_pose_action)
        
        # Paste World Pose
        paste_world_pose_action = QtWidgets.QAction("Paste World Pose", self)
        paste_world_pose_action.setStatusTip("Paste world space pose")
        paste_world_pose_action.triggered.connect(self.paste_world_pose_requested.emit)
        self.addAction(paste_world_pose_action)
        
        self.addSeparator()
        
        # Animation operations
        self.add_separator_with_label("Animation")
        
        # Copy Animation
        copy_anim_action = QtWidgets.QAction("Copy Anim", self)
        copy_anim_action.setStatusTip("Copy animation from selected objects")
        copy_anim_action.triggered.connect(self.copy_animation_requested.emit)
        self.addAction(copy_anim_action)
        
        # Paste Animation
        paste_anim_action = QtWidgets.QAction("Paste Anim", self)
        paste_anim_action.setStatusTip("Paste animation to selected objects")
        paste_anim_action.triggered.connect(self.paste_animation_requested.emit)
        self.addAction(paste_anim_action)
        
        # Mirror Animation
        mirror_anim_action = QtWidgets.QAction("Mirror Anim", self)
        mirror_anim_action.setStatusTip("Mirror animation on selected objects")
        mirror_anim_action.triggered.connect(self.mirror_animation_requested.emit)
        self.addAction(mirror_anim_action)
        
        self.addSeparator()
        
        # World Animation operations
        self.add_separator_with_label("World Animation")
        
        # Copy World Animation
        copy_world_anim_action = QtWidgets.QAction("Copy World Anim", self)
        copy_world_anim_action.setStatusTip("Copy world space animation")
        copy_world_anim_action.triggered.connect(self.copy_world_animation_requested.emit)
        self.addAction(copy_world_anim_action)
        
        # Paste World Animation
        paste_world_anim_action = QtWidgets.QAction("Paste World Anim", self)
        paste_world_anim_action.setStatusTip("Paste world space animation")
        paste_world_anim_action.triggered.connect(self.paste_world_animation_requested.emit)
        self.addAction(paste_world_anim_action)
        
        # Add time range controls
        self.addSeparator()
        self.add_time_range_controls()
        
    def add_separator_with_label(self, text):
        """Add a labeled separator"""
        label = QtWidgets.QLabel(f" {text}: ")
        label.setStyleSheet("QLabel { color: #888; font-weight: bold; }")
        self.addWidget(label)
        
    def add_time_range_controls(self):
        """Add time range selection controls"""
        self.add_separator_with_label("Time Range")
        
        # Start frame
        start_label = QtWidgets.QLabel("Start:")
        self.addWidget(start_label)
        
        self.start_frame_spin = QtWidgets.QSpinBox()
        self.start_frame_spin.setRange(-9999, 9999)
        self.start_frame_spin.setValue(1)
        self.start_frame_spin.setMaximumWidth(60)
        self.addWidget(self.start_frame_spin)
        
        # End frame
        end_label = QtWidgets.QLabel("End:")
        self.addWidget(end_label)
        
        self.end_frame_spin = QtWidgets.QSpinBox()
        self.end_frame_spin.setRange(-9999, 9999)
        self.end_frame_spin.setValue(24)
        self.end_frame_spin.setMaximumWidth(60)
        self.addWidget(self.end_frame_spin)
        
        # Get current range button
        current_range_btn = QtWidgets.QPushButton("Current Range")
        current_range_btn.clicked.connect(self.set_current_time_range)
        self.addWidget(current_range_btn)
        
    def set_current_time_range(self):
        """Set time range to current Maya timeline"""
        try:
            start_time = int(cmds.playbackOptions(query=True, minTime=True))
            end_time = int(cmds.playbackOptions(query=True, maxTime=True))
            self.start_frame_spin.setValue(start_time)
            self.end_frame_spin.setValue(end_time)
        except:
            # Default values if Maya commands fail
            self.start_frame_spin.setValue(1)
            self.end_frame_spin.setValue(24)
            
    def get_time_range(self):
        """Get selected time range"""
        return self.start_frame_spin.value(), self.end_frame_spin.value()
        
    def set_visible(self, visible):
        """Override to properly show/hide toolbar"""
        super(AnimationToolbar, self).setVisible(visible)
        if self.parent():
            if visible:
                self.parent().addToolBar(QtCore.Qt.BottomToolBarArea, self)
            else:
                self.parent().removeToolBar(self)

class AnimationOperations:
    """Helper class for animation operations"""
    
    @staticmethod
    def copy_pose(objects=None):
        """Copy pose from selected or specified objects"""
        if objects is None:
            objects = cmds.ls(selection=True)
            
        if not objects:
            cmds.warning("No objects selected for pose copy")
            return None
            
        pose_data = {}
        for obj in objects:
            # Get all keyable attributes
            attrs = cmds.listAttr(obj, keyable=True) or []
            pose_data[obj] = {}
            
            for attr in attrs:
                try:
                    value = cmds.getAttr(f"{obj}.{attr}")
                    pose_data[obj][attr] = value
                except:
                    continue
                    
        return pose_data
        
    @staticmethod
    def paste_pose(pose_data, objects=None):
        """Paste pose to selected or specified objects"""
        if not pose_data:
            cmds.warning("No pose data to paste")
            return
            
        if objects is None:
            objects = cmds.ls(selection=True)
            
        if not objects:
            cmds.warning("No objects selected for pose paste")
            return
            
        for obj in objects:
            if obj in pose_data:
                for attr, value in pose_data[obj].items():
                    try:
                        cmds.setAttr(f"{obj}.{attr}", value)
                    except:
                        continue
                        
    @staticmethod
    def mirror_pose(objects=None, mirror_axis='X'):
        """Mirror pose on specified axis"""
        if objects is None:
            objects = cmds.ls(selection=True)
            
        if not objects:
            cmds.warning("No objects selected for pose mirror")
            return
            
        # This is a simplified mirror - in production you'd want more sophisticated mirroring
        for obj in objects:
            try:
                if mirror_axis.upper() == 'X':
                    current_rx = cmds.getAttr(f"{obj}.rotateX")
                    current_ry = cmds.getAttr(f"{obj}.rotateY")
                    current_rz = cmds.getAttr(f"{obj}.rotateZ")
                    
                    cmds.setAttr(f"{obj}.rotateX", -current_rx)
                    cmds.setAttr(f"{obj}.rotateY", -current_ry)
                    cmds.setAttr(f"{obj}.rotateZ", current_rz)
            except:
                continue
                
    @staticmethod
    def copy_animation(objects=None, time_range=None):
        """Copy animation keys from objects"""
        if objects is None:
            objects = cmds.ls(selection=True)
            
        if not objects:
            cmds.warning("No objects selected for animation copy")
            return None
            
        if time_range is None:
            start_time = cmds.playbackOptions(query=True, minTime=True)
            end_time = cmds.playbackOptions(query=True, maxTime=True)
            time_range = (start_time, end_time)
            
        # Use Maya's copyKey command
        cmds.copyKey(objects, time=time_range)
        return True
        
    @staticmethod
    def paste_animation(objects=None, time_offset=0):
        """Paste animation keys to objects"""
        if objects is None:
            objects = cmds.ls(selection=True)
            
        if not objects:
            cmds.warning("No objects selected for animation paste")
            return
            
        # Use Maya's pasteKey command
        try:
            cmds.pasteKey(objects, timeOffset=time_offset)
        except:
            cmds.warning("No animation data to paste")
