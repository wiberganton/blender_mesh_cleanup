l_info = {
    "name": "Mesh Cleanup",
    "author": "Fredrik Lundblad, Fredrik Prokić",
    "version": (1, 0),
    "blender": (3, 2, 1),
    "description": "Removes noise, holes and inner geometry in mesh"}


import bpy
import bmesh
import time
import os
import textwrap
import sys
import math
from math import radians
from math import *
from mathutils import Matrix
from mathutils import *
from random import randint
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
from pathlib import Path



# Import stl file
class import_stl(Operator, ImportHelper):
    bl_idname = "importstl.func"
    bl_label = "Import Stl"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Make a list of all objects currently in the scene
    prior_objects = [object.name for object in \
                    bpy.context.scene.objects]
    
    #Sorts so that only stl. shows up :)
    filename_ext = ".stl"
    filter_glob: bpy.props.StringProperty(
                default="*.stl",
                options={'HIDDEN'})
                
    def execute(self, context):
        self.report({'INFO'}, "This is {self.bl_idname}")
        if self.filepath:
            bpy.ops.import_mesh.stl(filepath=self.filepath)
            # Print the imported object reference
            print("Imported object:", context.object)
            #puts it in object mode and putting geometry in center 
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            context.object.location = (0, 0, 0)
            context.object.scale = (0.001,0.001,0.001)
                
        bpy.ops.object.mode_set(mode='OBJECT')
        context.object.select_set(True)    
            
        return {'FINISHED'}
    
    
    # Select the newly imported stl
    new_current_objects = [object.name for object in \
                            bpy.context.scene.objects]
                            
    new_objects = set(new_current_objects) - set(prior_objects) 
    
    time.sleep(0.3)
    
    # Rename the imported mesh to more easily call for it later
    for obj in bpy.context.selected_objects:
        obj.name = "ToClean"
        obj.data.name = "ToClean" 
      


# Select the correct object
class OBJECT_CHOOSER_OT_choose_object(bpy.types.Operator):
    """Choose the object to work on."""
    bl_label = "Select object"
    bl_idname = 'chooser.operator'
    
    def execute(self, context):
        
        context = bpy.context
        obj = context.active_object
        
        # Set Object Interaction mode to "Object Mode"
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Select the object in the 3D viewport,
        bpy.data.objects["ToClean"].select_set(True)
    
        return {'FINISHED'}



# Operator for the mesh cleaner
class REMOVEUNLINKED_OT_remove_unlinked(bpy.types.Operator):
    """Remove parts of the mesh that are not connected to the "main part"."""
    bl_label = "Remove unlinked"
    bl_idname = 'remove_unlinked.operator'
    
    def execute(self, context):
        
        context = bpy.context
        obj = context.active_object
        
        # Set Object Interaction mode to "Edit Mode"
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Set Select Mode to "Vertex"
        bpy.ops.mesh.select_mode(type="FACE")
        
        # Deselect all vertices
        bpy.ops.mesh.select_all(action = 'DESELECT')
        
        # Select a random face
        faces_to_select = 1
        
        mesh = bpy.context.object.data
        bm = bmesh.from_edit_mesh(mesh)
        faces_pool = bm.faces[:]
        
        no_selected_verts = 1
        no_total_verts = 3
        
        
        # If the randomly chosen face is not in the "main body", reselect a new random face
        while no_selected_verts < no_total_verts * 0.5:
            
            for face_idx in range(faces_to_select):
                if not faces_pool:
                    break
                if len(faces_pool) == 1:
                    select_face = faces_pool.pop(0)
                else:
                    select_face = faces_pool.pop(randint( \
                                    0, len(faces_pool) - 1))
                
                select_face.select_set(True)
                
            bmesh.update_edit_mesh(mesh)
            
            
            # Select all linked vertices
            bpy.ops.mesh.select_linked(delimit=set())
            
            # Count vertices
            bm = bmesh.from_edit_mesh(obj.data)
            no_selected_verts = len([ v.index for v in \
                                    bm.verts if v.select ])
                                    
            no_total_verts = len(mesh.vertices)
            
            print(no_selected_verts)
            print(no_total_verts)
            
        
        # Invert selection
        bpy.ops.mesh.select_all(action='INVERT')
  
        # Delete selected
        bpy.ops.mesh.delete()
          
        return {'FINISHED'}


# Going through list and mark outer geometry
n = 0
n1 = [0,0,-0.25,180,0,0]
n2 = [0,0,0.25,0,0,0]
n3 = [0,-0.25,0,90,0,0]
n4 = [0.25,0,0,-90,0,-90]
n5 = [-0.25,0,0,+90,0,-90]
n6 = [0,0.25,0,-90,0,0]
n7 = [0.2,-0.2,0,45,90,0]
n8 = [-0.15,0.15,0,-45,-90,0]
n9 = [0.125,0.125,-0.25,220,0,-35]
n10 = [-0.125,-0.125,-0.2,-185,30,35]
n11 = [0.2,0,0.2,0,45,0]
n12 = [-0.2,0,-0.2,0,230,0]
n13 = [0.1,0.1,0.2,30,30,90]
camera_angles = [n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, \
                n11, n12, n13]



class MARKGEO_OT_mark_geo(bpy.types.Operator):
    bl_label = "Mark outer geometry"
    bl_idname = "mark.operator"

    def execute(self, context):
        
        def f_set_and_mark(): 
            
            global camera_angles
            for x in camera_angles:
                print(str(x) + "camera")
                select_geo(x[0], x[1], x[2], x[3], x[4], \
                            x[5])
                            
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1, time_limit=1)


        #Select camera first!!!
        def select_geo(tx,ty,tz,rx,ry,rz):
            def sel_cam(cam):
                bpy.context.scene.camera = \
                            bpy.context.scene.objects[cam]
                        
                return('cam ' + cam + ' selected')


            def cam_set(tx,ty,tz,rx,ry,rz):

                #field of view
                fov = 100.0

                pi = 3.14159265

                scene = bpy.data.scenes["Scene"]

                # Set render resolution
                scene.render.resolution_x = 2048
                scene.render.resolution_y = 1080

                # Set camera fov in degrees
                scene.camera.data.angle = fov*(pi/180.0)

                # Set camera rotation in euler angles
                scene.camera.rotation_mode = 'XYZ'
                scene.camera.rotation_euler[0] = \
                                            rx*(pi/180.0)
                                            
                scene.camera.rotation_euler[1] = \
                                            ry*(pi/180.0)
                                            
                scene.camera.rotation_euler[2] = \
                                            rz*(pi/180.0)

                # Set camera translation
                scene.camera.location.x = tx
                scene.camera.location.y = ty
                scene.camera.location.z = tz


            # Resets the camera view to the new input, initializes it
            def reset_cam():
                area = next(area for area in \
                            bpy.context.screen.areas if \
                            area.type == 'VIEW_3D')
                        
                area.spaces[0].region_3d.view_perspective =  'CAMERA'

            print('hello')

            #Takes the current view and gives inputs for override which later is used to mark with
            def getView3dAreaAndRegion():
                for area in bpy.context.screen.areas:
                    if area.type == "VIEW_3D":
                        for region in area.regions:
                            if region.type == "WINDOW":    
                                return area, region
             
            
            # Needed for view3d as context of which screen/angle/location it is looking from
            view3dArea, view3dRegion = \
                                    getView3dAreaAndRegion()
                                    
            override = bpy.context.copy()
            override['area'] = view3dArea
            override['region'] = view3dRegion


            def reset_Area_and_region():
                view3dArea, view3dRegion = \
                                    getView3dAreaAndRegion()
                                    
                override = bpy.context.copy()
                override['area'] = view3dArea
                override['region'] = view3dRegion
                return override
                
            reset_Area_and_region()

            #Selects a box given by min and max values of x & y in the given view (from override)
            def select_boxxy():
                bpy.ops.view3d.select_box(override,
                                        xmin=00,
                                        xmax=1080, 
                                        ymin=0, 
                                        ymax=1080, 
                                        wait_for_input=False,
                                        mode='ADD')
            
            cam_set(tx,ty,tz,rx,ry,rz)
            getView3dAreaAndRegion()
            reset_Area_and_region()
            reset_cam()
            select_boxxy()

            return{print('hello 2')}


        f_set_and_mark()

        return {'FINISHED'}



# Remove inner geometry
class REMOVEINNER_OT_remove_inner(bpy.types.Operator):
    bl_label = "Remove inner geometry"
    bl_idname = "remove_inner.operator"
    
    def execute(self, context):
        
        # Invert selection
        bpy.ops.mesh.select_all(action='INVERT')
  
        # Delete selected
        bpy.ops.mesh.delete(type='FACE')
        
        return {'FINISHED'}



# Clean up the mesh
class MESHCLEAN_OT_mesh_clean(bpy.types.Operator):
    bl_label = "Clean up mesh"
    bl_idname = "clean_mesh.operator"
    
    def execute(self, context):

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.modifier_add(type='REMESH')
        bpy.context.object.modifiers["Remesh"].mode = \
                                                    'SMOOTH'
        bpy.context.object.modifiers["Remesh"].octree_depth = 9
        
        target_obj = context.active_object
        for modifier in target_obj.modifiers:
            bpy.ops.object.modifier_apply(modifier = \
                                        modifier.name)
        
        return {'FINISHED'}



# Export all obj as stl.
class Export_as_stl(bpy.types.Operator):
    bl_label = "Export object as Stl"
    bl_idname = "exp_stl.operator"
    
    def execute(self, context):
        
        context = bpy.context
        scene = context.scene
        viewlayer = context.view_layer
        
        return {'FINISHED'}



# UI panel with buttons
class Main_panel(bpy.types.Panel):
    bl_label = "Mesh Cleanup"
    bl_category = "Mesh Cleanup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text= "Import the Stl file that needs to be cleaned.")
        row = layout.row()
        row.operator('importstl.func', icon= 'BONE_DATA')
        
        row = layout.row()
        row.label(text= "Remove unlinked mesh.")
        row = layout.row()
        row.operator('remove_unlinked.operator', icon= \
                                            'UNLINKED')
        
        row = layout.row()
        
        # Text wrap in panel
        textTowrap = "Select the outer mesh."
        wrapp = textwrap.TextWrapper(width=40)     
        wList = wrapp.wrap(text=textTowrap)
        
        for text in wList: 
            row = layout.row(align = True)
            row.alignment = 'EXPAND'
            row.label(text=text)

        row = layout.row()
        row.operator('mark.operator', icon= 'VIEW_ORTHO')
        
        row = layout.row()
        row.label(text= "Remove inner mesh.")
        row = layout.row()
        row.operator('remove_inner.operator', icon= \
                                            'OBJECT_HIDDEN')
        
        row = layout.row()
        row.label(text= "Clean up mesh.")
        row = layout.row()
        row.operator('clean_mesh.operator', icon= 'SHADERFX')
        
        row = layout.row()
        row.label(text= "Export as Stl.")
        row = layout.row()
        row.operator('exp_stl.operator', icon= 'FILE_BLEND')
        

        
classes = (Main_panel,
           OBJECT_CHOOSER_OT_choose_object,
           REMOVEUNLINKED_OT_remove_unlinked,
           MARKGEO_OT_mark_geo,
           REMOVEINNER_OT_remove_inner,
           MESHCLEAN_OT_mesh_clean,
           import_stl,Export_as_stl)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
