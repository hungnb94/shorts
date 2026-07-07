#!/usr/bin/env python3
"""
Cosmic Bloom - Character 01: Terra (Earth)
Low-poly 3D alien character for Blender 5.1+ (headless render)
Renders a 360-degree turntable animation (72 frames @ 15fps = 4.8s)
"""

import bpy
import bmesh
import os
import sys

# Output path (passed via -- python command line)
OUTPUT_DIR = "/Users/hung/code/ai/shorts/output/animated/cosmic_bloom"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===== SCENE SETUP =====
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create scene
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 72
scene.render.fps = 15
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100

# Camera
bpy.ops.object.camera_add(location=(0, -3.5, 2))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0)
scene.camera = camera

# Lighting
bpy.ops.object.light_add(type='SUN', location=(3, 3, 5))
light = bpy.context.active_object
light.data.energy = 3.0
light.data.color = (1, 0.98, 0.9)

bpy.ops.object.light_add(type='AREA', location=(-2, -2, 3))
fill = bpy.context.active_object
fill.data.energy = 1.0
fill.data.color = (0.6, 0.8, 1.0)

# World (dark blue space with some ambient)
world = bpy.data.worlds.new("CosmicWorld")
scene.world = world
world.use_nodes = True
world.node_tree.nodes.clear()
wnodes = world.node_tree.nodes
wlinks = world.node_tree.links

background = wnodes.new('ShaderNodeBackground')
background.inputs[0].default_value = (0.02, 0.04, 0.12, 1.0)
background.inputs[1].default_value = 0.5
output = wnodes.new('ShaderNodeOutputWorld')
wlinks.new(background.outputs[0], output.inputs[0])


# ===== CHARACTER: TERRA (Earth) =====
# Low-poly cute alien: big round head, small body, big eyes

def make_material(name, color, roughness=0.3, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    
    if emission > 0:
        bsdf.inputs['Emission'].default_value = (*color, emission)
        bsdf.inputs['Emission Strength'].default_value = emission
    
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(bsdf.outputs[0], output.inputs[0])
    return mat

mat_skin   = make_material("skin",   (0.35, 0.75, 0.4),  roughness=0.4)
mat_face   = make_material("face",   (0.9, 0.95, 0.85), roughness=0.5)
mat_eye    = make_material("eye",    (0.08, 0.08, 0.1), roughness=0.1, metallic=0.8)
mat_accent = make_material("accent", (0.2, 0.9, 1.0),   roughness=0.2, emission=0.5)
mat_orb    = make_material("orb",    (1.0, 0.8, 0.2),   roughness=0.1, emission=0.6)
mat_root   = make_material("root",   (0.6, 0.35, 0.15), roughness=0.7)

# BODY (small, rounded torso)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, segments=12, ring_count=8, location=(0, 0, 0.3))
body = bpy.context.active_object
body.scale = (1.0, 0.8, 0.9)
body.data.materials.append(mat_skin)
bpy.ops.object.modifier_add(type='SUBSURF')
body.modifiers['Subdivision Surface'].levels = 2
bpy.ops.object.modifier_apply(modifier='Subdivision Surface')

# HEAD (big round head)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9, segments=16, ring_count=12, location=(0, 0, 1.4))
head = bpy.context.active_object
head.scale = (1.0, 1.0, 0.95)
head.data.materials.append(mat_skin)
bpy.ops.object.modifier_add(type='SUBSURF')
head.modifiers['Subdivision Surface'].levels = 2
bpy.ops.object.modifier_apply(modifier='Subdivision Surface')

# EYES (large, cute, slightly offset)
for x_side in [-0.3, 0.3]:
    # Eye white / sclera
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, segments=10, ring_count=6, location=(x_side, 0.62, 1.5))
    eye = bpy.context.active_object
    eye.scale = (1.0, 0.4, 1.0)
    eye.data.materials.append(mat_face)
    
    # Pupil
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, segments=8, ring_count=6, location=(x_side, 0.76, 1.5))
    pupil = bpy.context.active_object
    pupil.scale = (1.0, 0.2, 1.0)
    pupil.data.materials.append(mat_eye)

# ACCENT: leaf on head (Earth motif)
bpy.ops.mesh.primitive_cone_add(radius1=0.2, depth=0.6, vertices=6, location=(0, 0, 2.2))
leaf = bpy.context.active_object
leaf.rotation_euler = (-0.4, 0, 0)
leaf.data.materials.append(mat_accent)

# ACCENT: small floating orbs (planetary system mini)
for i in range(3):
    angle = i * 2.094
    x = 1.4 * cos(angle)
    z = 1.4 + 1.4 * sin(angle)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, segments=6, ring_count=4, location=(x, 0.4, z))
    orb = bpy.context.active_object
    orb.data.materials.append(mat_orb)

# ROOT PLATFORM (connect to ground)
bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=0.1, vertices=16, location=(0, 0, -0.1))
root = bpy.context.active_object
root.data.materials.append(mat_root)

# PARTICLES: small stars
for i in range(20):
    import random
    random.seed(42 + i)
    x = random.uniform(-3, 3)
    y = random.uniform(-3, 3)
    z = random.uniform(0, 4)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, segments=4, ring_count=3, location=(x, y, z))
    star = bpy.context.active_object
    star_mat = make_material(f"star_{i}", 
                            (random.uniform(0.8,1), random.uniform(0.8,1), random.uniform(0.7,1)),
                            roughness=0, emission=2.0)
    star.data.materials.append(star_mat)


# ===== ANIMATION: Turntable rotation =====
# Rotate the character group around Y axis
# We'll rotate the whole scene by wrapping in an empty

bpy.ops.object.empty_add(location=(0, 0, 1.0))
empty = bpy.context.active_object
empty.name = "Rotator"

# Parent all character parts to the empty
for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj != root:  # Keep root on floor
        obj.parent = empty

# Keyframe: 0 rotation at frame 1, 360 at frame 72
empty.rotation_euler = (0, 0, 0)
empty.keyframe_insert(data_path="rotation_euler", frame=1)
empty.rotation_euler = (0, 0, 6.28318)  # 360 degrees
empty.keyframe_insert(data_path="rotation_euler", frame=72)

# Set linear interpolation
for fcurve in empty.animation_data.action.fcurves:
    for kf in fcurve.keyframe_points:
        kf.interpolation = 'LINEAR'


# ===== RENDER SETTINGS =====
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True

# Output: image sequence (frames 1-72)
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = os.path.join(OUTPUT_DIR, "terra_frame_")

print(f"[TERRA] Rendering 72 frames to {OUTPUT_DIR}/terra_frame_*.png")
print(f"[TERRA] Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
print(f"[TERRA] Engine: {scene.render.engine}, Samples: {scene.cycles.samples}")

# Render
bpy.ops.render.render(animation=True, write_still=False)
print("[TERRA] Render complete!")

# Export final status
with open(os.path.join(OUTPUT_DIR, "terra_status.txt"), "w") as f:
    f.write("TERRA RENDER COMPLETE\n")
    f.write(f"Frames: 1-72\n")
    f.write(f"Output: {OUTPUT_DIR}/terra_frame_*.png\n")
