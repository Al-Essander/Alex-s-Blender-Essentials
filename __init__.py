bl_info = {
    "name": "Symmetric Half Cube",
    "author": "Alex Andrews",
    "version": (2, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Add > Half Cubes",
    "description": "Add symmetric half cubes with Mirror modifier. Perfect for modeling symmetric objects.",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "Add Mesh",
}

import bpy
import bmesh
from mathutils import Vector

def create_half_cube(axis='X', inverted=False):
    # Создаем mesh и объект
    mesh = bpy.data.meshes.new("HalfCube")
    obj = bpy.data.objects.new("HalfCube", mesh)
    
    # Создаем куб через bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    
    # Находим и удаляем грани на нужной стороне
    faces_to_delete = []
    threshold = 1e-6

    for face in bm.faces:
        center = face.calc_center_median()
        
        if axis == 'X':
            if (not inverted and center.x > threshold) or (inverted and center.x < -threshold):
                faces_to_delete.append(face)
        elif axis == 'Y':
            if (not inverted and center.y > threshold) or (inverted and center.y < -threshold):
                faces_to_delete.append(face)
        elif axis == 'Z':
            if (not inverted and center.z > threshold) or (inverted and center.z < -threshold):
                faces_to_delete.append(face)

    # Собираем вершины, которые нужно сместить к плоскости симметрии
    verts_to_move = set()
    for face in faces_to_delete:
        for vert in face.verts:
            verts_to_move.add(vert)
    
    # Удаляем грани
    bmesh.ops.delete(bm, geom=faces_to_delete, context='FACES')
    
    # Смещаем вершины к плоскости симметрии
    for vert in verts_to_move:
        if axis == 'X':
            vert.co.x = 0.0
        elif axis == 'Y':
            vert.co.y = 0.0
        elif axis == 'Z':
            vert.co.z = 0.0

    # Применяем изменения к mesh
    bm.to_mesh(mesh)
    bm.free()

    # Добавляем объект в сцену
    collection = bpy.context.collection
    collection.objects.link(obj)
    
    # Активируем объект
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Переименовываем объект
    direction = "Neg" if inverted else "Pos"
    obj.name = f"HalfCube_{axis}_{direction}"

    # Добавляем модификатор Mirror
    mirror_mod = obj.modifiers.new(name="Mirror", type='MIRROR')
    mirror_mod.use_clip = True
    mirror_mod.use_mirror_merge = True
    mirror_mod.merge_threshold = 0.001

    # Устанавливаем ось отражения
    if axis == 'X':
        mirror_mod.use_axis[0] = True
        if inverted:
            mirror_mod.use_bisect_axis[0] = True
    elif axis == 'Y':
        mirror_mod.use_axis[1] = True
        if inverted:
            mirror_mod.use_bisect_axis[1] = True
    elif axis == 'Z':
        mirror_mod.use_axis[2] = True
        if inverted:
            mirror_mod.use_bisect_axis[2] = True

    return obj

# --- Операторы ---
class MESH_OT_half_cube_x(bpy.types.Operator):
    bl_idname = "mesh.add_half_cube_x"
    bl_label = "Half Cube Mirror X"
    bl_description = "Add a half cube with X-axis mirror modifier (polygons on left)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_half_cube('X', False)
        return {'FINISHED'}

class MESH_OT_half_cube_y(bpy.types.Operator):
    bl_idname = "mesh.add_half_cube_y"
    bl_label = "Half Cube Mirror Y"
    bl_description = "Add a half cube with Y-axis mirror modifier (polygons on front)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_half_cube('Y', False)
        return {'FINISHED'}

class MESH_OT_half_cube_z(bpy.types.Operator):
    bl_idname = "mesh.add_half_cube_z"
    bl_label = "Half Cube Mirror Z"
    bl_description = "Add a half cube with Z-axis mirror modifier (polygons on bottom)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_half_cube('Z', False)
        return {'FINISHED'}

class MESH_OT_half_cube_x_inverted(bpy.types.Operator):
    bl_idname = "mesh.add_half_cube_x_inverted"
    bl_label = "Half Cube Mirror X (Inverted)"
    bl_description = "Add a half cube with X-axis mirror modifier (polygons on right)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_half_cube('X', True)
        return {'FINISHED'}

class MESH_OT_half_cube_y_inverted(bpy.types.Operator):
    bl_idname = "mesh.add_half_cube_y_inverted"
    bl_label = "Half Cube Mirror Y (Inverted)"
    bl_description = "Add a half cube with Y-axis mirror modifier (polygons on back)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_half_cube('Y', True)
        return {'FINISHED'}

class MESH_OT_half_cube_z_inverted(bpy.types.Operator):
    bl_idname = "mesh.add_half_cube_z_inverted"
    bl_label = "Half Cube Mirror Z (Inverted)"
    bl_description = "Add a half cube with Z-axis mirror modifier (polygons on top)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_half_cube('Z', True)
        return {'FINISHED'}

# --- Меню ---
class VIEW3D_MT_add_half_cubes_menu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_add_half_cubes_menu"
    bl_label = "Half Cubes"
    bl_description = "Add various half cube primitives"

    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Standard:", icon='MOD_MIRROR')
        layout.operator("mesh.add_half_cube_x", text="Mirror X (Left)", icon='MESH_CUBE')
        layout.operator("mesh.add_half_cube_y", text="Mirror Y (Front)", icon='MESH_CUBE')
        layout.operator("mesh.add_half_cube_z", text="Mirror Z (Bottom)", icon='MESH_CUBE')
        
        layout.separator()
        
        layout.label(text="Inverted:", icon='MOD_MIRROR')
        layout.operator("mesh.add_half_cube_x_inverted", text="Mirror X (Right)", icon='MESH_CUBE')
        layout.operator("mesh.add_half_cube_y_inverted", text="Mirror Y (Back)", icon='MESH_CUBE')
        layout.operator("mesh.add_half_cube_z_inverted", text="Mirror Z (Top)", icon='MESH_CUBE')

# --- Панель инструментов ---
class VIEW3D_PT_half_cubes_tools(bpy.types.Panel):
    bl_label = "Half Cubes"
    bl_idname = "VIEW3D_PT_half_cubes_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Create"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Add Half Cubes:", icon='ADD')
        
        box.label(text="Standard:")
        box.operator("mesh.add_half_cube_x", text="X Mirror (Left)")
        box.operator("mesh.add_half_cube_y", text="Y Mirror (Front)")
        box.operator("mesh.add_half_cube_z", text="Z Mirror (Bottom)")
        
        box.label(text="Inverted:")
        box.operator("mesh.add_half_cube_x_inverted", text="X Mirror (Right)")
        box.operator("mesh.add_half_cube_y_inverted", text="Y Mirror (Back)")
        box.operator("mesh.add_half_cube_z_inverted", text="Z Mirror (Top)")

# --- Классы для регистрации ---
classes = (
    MESH_OT_half_cube_x,
    MESH_OT_half_cube_y,
    MESH_OT_half_cube_z,
    MESH_OT_half_cube_x_inverted,
    MESH_OT_half_cube_y_inverted,
    MESH_OT_half_cube_z_inverted,
    VIEW3D_MT_add_half_cubes_menu,
    VIEW3D_PT_half_cubes_tools,
)

# --- Функции регистрации ---
def add_half_cubes_menu_early(self, context):
    self.layout.separator()
    self.layout.menu("VIEW3D_MT_add_half_cubes_menu", text="Half Cubes", icon='MESH_CUBE')

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.VIEW3D_MT_add.prepend(add_half_cubes_menu_early)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    bpy.types.VIEW3D_MT_add.remove(add_half_cubes_menu_early)

# Это обязательно для распознавания аддона
def register_addon():
    register()

def unregister_addon():
    unregister()

if __name__ == "__main__":
    register()