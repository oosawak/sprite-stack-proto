import struct
import numpy as np
from PIL import Image, ImageDraw

# Color Palette (Index 1..9, 0 is empty)
PALETTE = {
    1: (230, 235, 245, 255),  # White/Light Grey Armor
    2: (155, 165, 180, 255),  # Shaded Grey Armor
    3: (220, 45, 50, 255),    # Red Accent / Stripes
    4: (55, 60, 70, 255),     # Dark Metal / Joints / Guns
    5: (35, 175, 240, 255),   # Cyan Canopy / Visor
    6: (165, 235, 255, 255),  # Canopy Highlight
    7: (255, 160, 30, 255),   # Thruster Glow
    8: (255, 240, 150, 255),  # Thruster Core
    9: (40, 65, 130, 255),    # Deep Blue Trim
}

def fill_box(grid, x0, x1, y0, y1, z0, z1, col):
    """Fill a box inclusively in (x, y, z) coordinates."""
    X, Y, Z = grid.shape
    x0, x1 = max(0, min(x0, x1)), min(X - 1, max(x0, x1))
    y0, y1 = max(0, min(y0, y1)), min(Y - 1, max(y0, y1))
    z0, z1 = max(0, min(z0, z1)), min(Z - 1, max(z0, z1))
    grid[x0:x1+1, y0:y1+1, z0:z1+1] = col

def fill_sym_box(grid, x_off0, x_off1, y0, y1, z0, z1, col):
    """Fill symmetrically around X center (X=32 -> center between 15 and 16)."""
    X = grid.shape[0]
    cx_l = X // 2 - 1
    cx_r = X // 2
    fill_box(grid, cx_l - x_off1, cx_l - x_off0, y0, y1, z0, z1, col)
    fill_box(grid, cx_r + x_off0, cx_r + x_off1, y0, y1, z0, z1, col)

# ==========================================
# 1. FIGHTER MODE (32 x 36 x 20)
# ==========================================
def build_fighter():
    grid = np.zeros((32, 36, 20), dtype=np.uint8)
    # Main fuselage (Y: 4=tail -> 34=nose)
    fill_sym_box(grid, 0, 2, 4, 22, 6, 10, 1)
    fill_sym_box(grid, 0, 2, 4, 22, 5, 5, 2) # belly
    fill_sym_box(grid, 0, 1, 23, 29, 6, 9, 1)
    fill_sym_box(grid, 0, 0, 30, 34, 7, 8, 1) # nose tip
    # Red spine stripe & nose tip
    fill_sym_box(grid, 0, 0, 6, 27, 10, 10, 3)
    fill_sym_box(grid, 0, 0, 33, 34, 7, 8, 3)
    # Cockpit canopy
    fill_sym_box(grid, 0, 1, 18, 24, 11, 12, 5)
    fill_sym_box(grid, 0, 0, 20, 23, 13, 13, 6)
    # Twin engine nacelles (under/rear, become legs)
    fill_sym_box(grid, 1, 3, 2, 16, 4, 7, 2)
    fill_sym_box(grid, 2, 3, 2, 14, 5, 7, 1)
    fill_sym_box(grid, 2, 3, 1, 1, 5, 6, 4) # nozzle
    fill_sym_box(grid, 2, 3, 0, 0, 5, 6, 7) # thruster glow
    # Swept main wings
    for i in range(12):
        y_start = 7 + i
        y_end = 17 - i // 3
        if y_start <= y_end:
            fill_sym_box(grid, 3 + i, 3 + i, y_start, y_end, 8, 9, 1)
            if i >= 10:
                fill_sym_box(grid, 3 + i, 3 + i, y_start, y_end, 8, 9, 3) # red wingtips
    # Wing stripes & guns
    fill_sym_box(grid, 5, 9, 11, 12, 9, 9, 3)
    fill_sym_box(grid, 7, 7, 13, 21, 7, 7, 4)
    # Canards
    for i in range(4):
        fill_sym_box(grid, 2 + i, 2 + i, 23 + i // 2, 26 - i // 2, 8, 8, 1)
    fill_sym_box(grid, 5, 5, 24, 25, 8, 8, 3)
    # Twin vertical tail fins
    for h in range(6):
        fill_sym_box(grid, 3 + h // 3, 3 + h // 3, 3 + h // 2, 9 - h // 2, 10 + h, 10 + h, 1 if h < 4 else 3)
    return grid

# ==========================================
# 2. GERWALK MODE (32 x 36 x 28)
# ==========================================
def build_gerwalk():
    grid = np.zeros((32, 36, 28), dtype=np.uint8)
    # Upper fuselage lifted up (Z + 10)
    fill_sym_box(grid, 0, 2, 6, 23, 16, 20, 1)
    fill_sym_box(grid, 0, 2, 6, 23, 15, 15, 2)
    fill_sym_box(grid, 0, 1, 24, 30, 16, 19, 1)
    fill_sym_box(grid, 0, 0, 31, 35, 17, 18, 1)
    fill_sym_box(grid, 0, 0, 8, 28, 20, 20, 3)
    fill_sym_box(grid, 0, 0, 34, 35, 17, 18, 3)
    # Canopy
    fill_sym_box(grid, 0, 1, 19, 25, 21, 22, 5)
    fill_sym_box(grid, 0, 0, 21, 24, 23, 23, 6)
    # Wings spread wide
    for i in range(12):
        y_start = 9 + i
        y_end = 19 - i // 3
        if y_start <= y_end:
            fill_sym_box(grid, 3 + i, 3 + i, y_start, y_end, 18, 19, 1 if i < 10 else 3)
    fill_sym_box(grid, 5, 9, 13, 14, 19, 19, 3)
    # Tail fins
    for h in range(6):
        fill_sym_box(grid, 3 + h // 3, 3 + h // 3, 5 + h // 2, 11 - h // 2, 20 + h, 20 + h, 1 if h < 4 else 3)
    # Arms deployed under wings holding gunpod
    fill_sym_box(grid, 4, 5, 14, 17, 11, 15, 1) # upper arm
    fill_sym_box(grid, 4, 5, 15, 23, 9, 11, 1)  # forearm forward
    fill_sym_box(grid, 4, 5, 19, 20, 11, 11, 3) # red forearm trim
    fill_sym_box(grid, 4, 5, 24, 25, 9, 11, 4)  # hands
    fill_sym_box(grid, 0, 1, 22, 32, 9, 10, 4)  # central gunpod
    # Reverse-jointed (bird-like) legs!
    # Thighs angling forward-down
    for step in range(6):
        fill_sym_box(grid, 2, 4, 12 + step, 15 + step, 14 - step, 15 - step, 2)
    # Knee joint
    fill_sym_box(grid, 2, 4, 16, 19, 7, 9, 4)
    # Lower legs angling backward-down
    for step in range(7):
        fill_sym_box(grid, 2, 4, 17 - step, 20 - step, 7 - step, 8 - step, 1)
    fill_sym_box(grid, 3, 4, 14, 16, 3, 6, 3) # red leg stripe
    # Feet / Thruster nozzles on ground
    fill_sym_box(grid, 2, 4, 10, 16, 0, 1, 4)
    fill_sym_box(grid, 2, 4, 14, 17, 1, 2, 9)
    return grid

# ==========================================
# 3. ROBOT (BATTROID) MODE (32 x 24 x 40)
# ==========================================
def build_robot():
    grid = np.zeros((32, 24, 40), dtype=np.uint8)
    # Feet (Z: 0..2)
    fill_sym_box(grid, 2, 5, 9, 16, 0, 1, 4)
    fill_sym_box(grid, 2, 5, 12, 16, 1, 2, 9)
    # Lower legs (Z: 3..13)
    fill_sym_box(grid, 2, 5, 10, 14, 3, 13, 1)
    fill_sym_box(grid, 5, 5, 11, 13, 5, 11, 3) # red side armor
    fill_sym_box(grid, 3, 4, 14, 15, 11, 14, 9) # knee armor
    # Thighs (Z: 14..20)
    fill_sym_box(grid, 2, 4, 10, 14, 14, 20, 2)
    # Waist / Pelvis (Z: 20..23)
    fill_sym_box(grid, 0, 4, 9, 14, 20, 22, 1)
    fill_sym_box(grid, 0, 1, 9, 15, 20, 23, 3)
    # Torso / Chest (Z: 23..32) - folded nose & canopy as chest plate!
    fill_sym_box(grid, 0, 5, 9, 15, 23, 32, 1)
    fill_sym_box(grid, 0, 2, 14, 16, 24, 31, 9) # blue chest plate
    fill_sym_box(grid, 0, 1, 15, 17, 25, 30, 5) # canopy core in chest
    fill_sym_box(grid, 3, 4, 14, 16, 27, 31, 3) # red chest intakes
    # Backpack with folded wings & tail fins (Y: 5..8)
    fill_sym_box(grid, 1, 3, 6, 8, 22, 31, 2)
    for i in range(8):
        fill_sym_box(grid, 4 + i, 4 + i, 6, 7, 24 - i, 31 - i, 1 if i < 6 else 3)
    fill_sym_box(grid, 2, 2, 4, 6, 24, 32, 3) # vertical fins on back
    # Shoulders & Arms (Z: 17..33)
    fill_sym_box(grid, 6, 9, 10, 14, 29, 33, 1) # shoulder pauldrons
    fill_sym_box(grid, 7, 9, 11, 13, 32, 33, 3) # red shoulder top
    fill_sym_box(grid, 6, 8, 10, 13, 24, 28, 2) # upper arm
    fill_sym_box(grid, 6, 9, 10, 14, 18, 23, 1) # forearm
    fill_sym_box(grid, 9, 9, 11, 13, 19, 22, 3) # red forearm shield
    fill_sym_box(grid, 7, 8, 11, 13, 16, 17, 4) # fists
    # Head (Z: 33..38)
    fill_sym_box(grid, 0, 2, 10, 14, 33, 37, 1)
    fill_sym_box(grid, 0, 1, 14, 15, 34, 35, 5) # glowing cyan visor
    fill_sym_box(grid, 0, 0, 11, 14, 37, 38, 3) # head crest
    fill_sym_box(grid, 2, 2, 11, 12, 36, 39, 4) # twin head lasers
    return grid

# ==========================================
# MAGICA-VOXEL (.vox) EXPORTER
# ==========================================
def export_vox(grid, filename):
    X, Y, Z = grid.shape
    voxels = []
    for x in range(X):
        for y in range(Y):
            for z in range(Z):
                c = grid[x, y, z]
                if c > 0:
                    voxels.append((x, y, z, int(c)))

    # Build SIZE chunk
    size_content = struct.pack('<III', X, Y, Z)
    size_chunk = b'SIZE' + struct.pack('<II', len(size_content), 0) + size_content

    # Build XYZI chunk
    xyzi_content = struct.pack('<I', len(voxels))
    for vx, vy, vz, vc in voxels:
        xyzi_content += struct.pack('<BBBB', vx, vy, vz, vc)
    xyzi_chunk = b'XYZI' + struct.pack('<II', len(xyzi_content), 0) + xyzi_content

    # Build RGBA chunk (256 colors)
    rgba_content = bytearray(256 * 4)
    for idx, (r, g, b, a) in PALETTE.items():
        offset = (idx - 1) * 4
        rgba_content[offset:offset+4] = struct.pack('<BBBB', r, g, b, a)
    rgba_chunk = b'RGBA' + struct.pack('<II', len(rgba_content), 0) + bytes(rgba_content)

    children = size_chunk + xyzi_chunk + rgba_chunk
    main_chunk = b'MAIN' + struct.pack('<II', 0, len(children)) + children
    header = b'VOX ' + struct.pack('<I', 150)

    with open(filename, 'wb') as f:
        f.write(header + main_chunk)
    return len(voxels)

# ==========================================
# TRUE ISOMETRIC / 3D VOXEL RENDERER
# ==========================================
def shade_color(rgba, factor):
    r, g, b, a = rgba
    return (int(min(255, r * factor)), int(min(255, g * factor)), int(min(255, b * factor)), a)

def render_voxel_iso(grid, yaw_deg=35, pitch_deg=25, scale=7, img_size=(340, 360)):
    """Render an actual 3D voxel grid with shaded cube faces (top, left, right)."""
    img = Image.new("RGBA", img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    X, Y, Z = grid.shape
    cx, cy, cz = X / 2.0, Y / 2.0, Z / 2.0

    yaw = np.radians(yaw_deg)
    pitch = np.radians(pitch_deg)
    cos_y, sin_y = np.cos(yaw), np.sin(yaw)
    cos_p, sin_p = np.cos(pitch), np.sin(pitch)

    def project(x, y, z):
        dx, dy, dz = x - cx, y - cy, z - cz
        # Rotate around Z (yaw)
        rx = dx * cos_y - dy * sin_y
        ry = dx * sin_y + dy * cos_y
        rz = dz
        # Tilt (pitch)
        sx = rx * scale + img_size[0] / 2.0
        sy = (ry * sin_p - rz * cos_p) * scale + img_size[1] / 2.0 + 15
        depth = ry * cos_p + rz * sin_p
        return (sx, sy), depth

    # Collect visible voxels and sort back-to-front by camera depth
    visible = []
    for x in range(X):
        for y in range(Y):
            for z in range(Z):
                c = grid[x, y, z]
                if c == 0:
                    continue
                # Occlusion check (skip completely surrounded interior voxels)
                if (0 < x < X-1 and 0 < y < Y-1 and 0 < z < Z-1 and
                    grid[x-1,y,z] and grid[x+1,y,z] and
                    grid[x,y-1,z] and grid[x,y+1,z] and
                    grid[x,y,z-1] and grid[x,y,z+1]):
                    continue
                _, d = project(x + 0.5, y + 0.5, z + 0.5)
                visible.append((d, x, y, z, int(c)))

    visible.sort(key=lambda item: item[0])

    # Cube face definitions (vertices & outward normals)
    faces = [
        # Top (+Z)
        ([(0,0,1), (1,0,1), (1,1,1), (0,1,1)], (0, 0, 1), 1.08),
        # Bottom (-Z)
        ([(0,0,0), (0,1,0), (1,1,0), (1,0,0)], (0, 0, -1), 0.55),
        # Front (-Y)
        ([(0,0,0), (1,0,0), (1,0,1), (0,0,1)], (0, -1, 0), 0.88),
        # Back (+Y)
        ([(1,1,0), (0,1,0), (0,1,1), (1,1,1)], (0, 1, 0), 0.82),
        # Left (-X)
        ([(0,1,0), (0,0,0), (0,0,1), (0,1,1)], (-1, 0, 0), 0.72),
        # Right (+X)
        ([(1,0,0), (1,1,0), (1,1,1), (1,0,1)], (1, 0, 0), 0.95),
    ]

    # View vector in world space
    vx_dir = sin_y * cos_p
    vy_dir = cos_y * cos_p
    vz_dir = sin_p

    for _, x, y, z, c in visible:
        base_col = PALETTE[c]
        for verts, normal, light in faces:
            nx, ny, nz = normal
            # Neighbor check
            nnx, nny, nnz = x + nx, y + ny, z + nz
            if 0 <= nnx < X and 0 <= nny < Y and 0 <= nnz < Z and grid[nnx, nny, nnz] > 0:
                continue
            # Backface culling
            dot = nx * (-vx_dir) + ny * (-vy_dir) + nz * vz_dir
            if dot <= 0:
                continue
            poly = [project(x + vx, y + vy, z + vz)[0] for vx, vy, vz in verts]
            fcol = shade_color(base_col, light)
            draw.polygon(poly, fill=fcol, outline=shade_color(fcol, 0.85))
    return img

# ==========================================
# SPRITE STACKING SHEET EXPORTER
# ==========================================
def export_stack_sheet(grid, filename):
    X, Y, Z = grid.shape
    sheet = Image.new("RGBA", (X * Z, Y), (0, 0, 0, 0))
    for z in range(Z):
        slice_img = Image.new("RGBA", (X, Y), (0, 0, 0, 0))
        px = slice_img.load()
        for x in range(X):
            for y in range(Y):
                c = grid[x, y, z]
                if c > 0:
                    # Flip Y so nose points up
                    px[x, Y - 1 - y] = PALETTE[int(c)]
        sheet.paste(slice_img, (z * X, 0))
    sheet.save(filename)

# Build all 3 voxel models
fighter = build_fighter()
gerwalk = build_gerwalk()
robot = build_robot()

# Export .vox files (MagicaVoxel format)
v_f = export_vox(fighter, "valkyrie_fighter.vox")
v_g = export_vox(gerwalk, "valkyrie_gerwalk.vox")
v_r = export_vox(robot, "valkyrie_robot.vox")

# Export Sprite Stacking sheets
export_stack_sheet(fighter, "sheet_fighter.png")
export_stack_sheet(gerwalk, "sheet_gerwalk.png")
export_stack_sheet(robot, "sheet_robot.png")

# Render True 3D Voxel Showcase Image
canvas = Image.new("RGBA", (1140, 520), (20, 24, 34, 255))
draw = ImageDraw.Draw(canvas)

# Gridlines
for gx in range(0, 1140, 20):
    draw.line([(gx, 0), (gx, 520)], fill=(28, 34, 48, 255), width=1)
for gy in range(0, 520, 20):
    draw.line([(0, gy), (1140, gy)], fill=(28, 34, 48, 255), width=1)

draw.text((24, 16), "TRUE 3D VOXEL MODELS: FIGHTER / GERWALK / ROBOT (Exported to .vox & Sprite Stacking Sheets)", fill=(210, 225, 250, 255))

models = [
    ("1. FIGHTER MODE", f"Grid: 32x36x20 | Voxels: {v_f}", fighter, 7.5, -140, 28),
    ("2. GERWALK MODE", f"Grid: 32x36x28 | Voxels: {v_g}", gerwalk, 7.0, -140, 24),
    ("3. ROBOT (BATTROID)", f"Grid: 32x24x40 | Voxels: {v_r}", robot, 6.8, -145, 20),
]

for idx, (title, meta, m_grid, sc, yaw, pitch) in enumerate(models):
    bx = 24 + idx * 372
    by = 48
    draw.rectangle([bx, by, bx + 348, by + 448], fill=(14, 17, 24, 255), outline=(65, 80, 110, 255), width=2)
    draw.text((bx + 14, by + 12), title, fill=(235, 240, 255, 255))
    draw.text((bx + 14, by + 30), meta, fill=(130, 155, 195, 255))

    # Front-3/4 view
    r_front = render_voxel_iso(m_grid, yaw_deg=yaw, pitch_deg=pitch, scale=sc, img_size=(340, 320))
    canvas.paste(r_front, (bx + 4, by + 46), r_front)

    # Rear-3/4 thumbnail in bottom right
    r_rear = render_voxel_iso(m_grid, yaw_deg=yaw + 150, pitch_deg=pitch, scale=sc * 0.48, img_size=(140, 140))
    draw.rectangle([bx + 196, by + 296, bx + 338, by + 438], fill=(20, 24, 34, 255), outline=(50, 62, 85, 255))
    canvas.paste(r_rear, (bx + 198, by + 298), r_rear)
    draw.text((bx + 204, by + 302), "REAR VIEW", fill=(120, 140, 175, 255))

    # Color palette & slice info at bottom left
    draw.text((bx + 14, by + 412), f"Z-Slices: {m_grid.shape[2]} layers", fill=(160, 180, 210, 255))

canvas.save("true_voxel_3forms_preview.png")
print(f"Exported VOX files: Fighter({v_f}), Gerwalk({v_g}), Robot({v_r})")