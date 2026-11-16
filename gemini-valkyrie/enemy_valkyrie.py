import struct
import zipfile
import numpy as np
from PIL import Image, ImageDraw

# Enemy Dark-Stealth Color Palette (Index 1..9, 0 is empty)
PALETTE = {
    1: (42, 46, 56, 255),     # Matte Stealth Black/Charcoal Armor
    2: (24, 26, 32, 255),     # Deep Shadow Black Armor
    3: (155, 45, 220, 255),   # Neon Violet / Plasma Purple Accent
    4: (75, 82, 95, 255),     # Gunmetal / Mechanical Joints
    5: (255, 45, 75, 255),    # Crimson Glowing Visor / Canopy
    6: (255, 150, 170, 255),  # Visor Highlight
    7: (190, 60, 255, 255),   # Purple Plasma Thruster Glow
    8: (245, 190, 255, 255),  # Thruster Core
    9: (140, 25, 45, 255),    # Dark Crimson Trim
}

def fill_box(grid, x0, x1, y0, y1, z0, z1, col):
    X, Y, Z = grid.shape
    x0, x1 = max(0, min(x0, x1)), min(X - 1, max(x0, x1))
    y0, y1 = max(0, min(y0, y1)), min(Y - 1, max(y0, y1))
    z0, z1 = max(0, min(z0, z1)), min(Z - 1, max(z0, z1))
    grid[x0:x1+1, y0:y1+1, z0:z1+1] = col

def fill_sym_box(grid, x_off0, x_off1, y0, y1, z0, z1, col):
    X = grid.shape[0]
    cx_l = X // 2 - 1
    cx_r = X // 2
    fill_box(grid, cx_l - x_off1, cx_l - x_off0, y0, y1, z0, z1, col)
    fill_box(grid, cx_r + x_off0, cx_r + x_off1, y0, y1, z0, z1, col)

# ==========================================
# 1. ENEMY FIGHTER (Forward-Swept Stealth Jet: 32 x 36 x 20)
# ==========================================
def build_enemy_fighter():
    grid = np.zeros((32, 36, 20), dtype=np.uint8)
    # Angular stealth fuselage (Y: 4=tail -> 35=sharp nose)
    fill_sym_box(grid, 0, 2, 4, 21, 6, 10, 1)
    fill_sym_box(grid, 0, 2, 4, 21, 5, 5, 2)
    fill_sym_box(grid, 0, 1, 22, 29, 6, 9, 1)
    fill_sym_box(grid, 0, 0, 30, 35, 7, 8, 1)
    # Violet spine & sharp nose tip
    fill_sym_box(grid, 0, 0, 5, 26, 10, 10, 3)
    fill_sym_box(grid, 0, 0, 33, 35, 7, 8, 3)
    # Crimson sensor canopy
    fill_sym_box(grid, 0, 1, 17, 23, 11, 12, 5)
    fill_sym_box(grid, 0, 0, 19, 22, 13, 13, 6)
    # Heavy angular engine nacelles
    fill_sym_box(grid, 2, 4, 2, 16, 4, 7, 2)
    fill_sym_box(grid, 2, 4, 2, 14, 5, 7, 1)
    fill_sym_box(grid, 2, 4, 1, 1, 5, 6, 4)
    fill_sym_box(grid, 2, 4, 0, 0, 5, 6, 7)
    # FORWARD-SWEPT WINGS (distinctive silhouette!)
    for i in range(11):
        # Wings angle forward as x increases
        y_start = 8 + i // 2
        y_end = 15 + i
        fill_sym_box(grid, 4 + i, 4 + i, y_start, y_end, 8, 9, 1)
        # Forward-pointing wingtip claws/blades
        if i >= 9:
            fill_sym_box(grid, 4 + i, 4 + i, y_start - 2, y_end + 3, 8, 9, 3)
    # Wing violet energy lines
    fill_sym_box(grid, 6, 10, 12, 13, 9, 9, 3)
    # Rear horizontal tailplanes + V-cant twin vertical stabilizers
    fill_sym_box(grid, 5, 8, 3, 6, 7, 7, 2)
    for h in range(6):
        # Outward angled V-fins
        fill_sym_box(grid, 3 + h // 2, 3 + h // 2, 2 + h // 2, 8 - h // 2, 10 + h, 10 + h, 1 if h < 4 else 9)
    return grid

# ==========================================
# 2. ENEMY GERWALK (Heavy Gunship Walker: 32 x 36 x 28)
# ==========================================
def build_enemy_gerwalk():
    grid = np.zeros((32, 36, 28), dtype=np.uint8)
    # Lifted stealth fuselage
    fill_sym_box(grid, 0, 2, 6, 22, 16, 20, 1)
    fill_sym_box(grid, 0, 2, 6, 22, 15, 15, 2)
    fill_sym_box(grid, 0, 1, 23, 30, 16, 19, 1)
    fill_sym_box(grid, 0, 0, 31, 35, 17, 18, 1)
    fill_sym_box(grid, 0, 0, 7, 27, 20, 20, 3)
    fill_sym_box(grid, 0, 0, 34, 35, 17, 18, 3)
    # Crimson canopy
    fill_sym_box(grid, 0, 1, 18, 24, 21, 22, 5)
    fill_sym_box(grid, 0, 0, 20, 23, 23, 23, 6)
    # Forward-swept wings
    for i in range(11):
        y_start = 10 + i // 2
        y_end = 17 + i
        fill_sym_box(grid, 4 + i, 4 + i, y_start, y_end, 18, 19, 1 if i < 9 else 3)
        if i >= 9:
            fill_sym_box(grid, 4 + i, 4 + i, y_start - 2, y_end + 3, 18, 19, 3)
    # V-tail fins
    for h in range(6):
        fill_sym_box(grid, 3 + h // 2, 3 + h // 2, 4 + h // 2, 10 - h // 2, 20 + h, 20 + h, 1 if h < 4 else 9)
    # Twin arm-mounted plasma cannons (no handheld gun, dual arm blasters!)
    fill_sym_box(grid, 5, 6, 14, 17, 11, 15, 1)
    fill_sym_box(grid, 5, 6, 15, 27, 9, 11, 2)
    fill_sym_box(grid, 5, 6, 20, 24, 11, 11, 3)
    fill_sym_box(grid, 5, 6, 28, 30, 10, 10, 5) # crimson cannon muzzles
    # Heavy armored reverse-joint legs
    for step in range(6):
        fill_sym_box(grid, 2, 4, 12 + step, 15 + step, 14 - step, 15 - step, 2)
    fill_sym_box(grid, 2, 4, 16, 20, 7, 9, 4) # spiked knee guard
    fill_sym_box(grid, 3, 3, 20, 21, 8, 9, 3)
    for step in range(7):
        fill_sym_box(grid, 2, 4, 17 - step, 20 - step, 7 - step, 8 - step, 1)
    fill_sym_box(grid, 4, 4, 13, 16, 3, 6, 9)
    # Clawed feet
    fill_sym_box(grid, 2, 4, 10, 17, 0, 1, 4)
    fill_sym_box(grid, 2, 2, 17, 18, 0, 1, 3)
    fill_sym_box(grid, 4, 4, 17, 18, 0, 1, 3)
    return grid

# ==========================================
# 3. ENEMY ROBOT (Spiked Ace Mech: 32 x 24 x 40)
# ==========================================
def build_enemy_robot():
    grid = np.zeros((32, 24, 40), dtype=np.uint8)
    # Clawed Feet (Z: 0..2)
    fill_sym_box(grid, 2, 5, 9, 16, 0, 1, 4)
    fill_sym_box(grid, 2, 2, 16, 17, 0, 1, 3)
    fill_sym_box(grid, 5, 5, 16, 17, 0, 1, 3)
    # Heavy Lower Legs (Z: 3..13)
    fill_sym_box(grid, 2, 5, 10, 14, 3, 13, 1)
    fill_sym_box(grid, 5, 5, 11, 13, 4, 12, 3) # violet leg blade trim
    fill_sym_box(grid, 3, 4, 14, 16, 11, 15, 9) # crimson spiked knee
    # Thighs (Z: 14..20)
    fill_sym_box(grid, 2, 4, 10, 14, 14, 20, 2)
    # Angular Waist (Z: 20..23)
    fill_sym_box(grid, 0, 4, 9, 14, 20, 22, 1)
    fill_sym_box(grid, 0, 1, 9, 15, 20, 23, 9)
    # Angular Stealth Torso (Z: 23..32)
    fill_sym_box(grid, 0, 5, 9, 15, 23, 32, 1)
    fill_sym_box(grid, 0, 2, 14, 16, 24, 31, 2)
    fill_sym_box(grid, 0, 1, 15, 17, 25, 30, 5) # glowing crimson core/canopy
    fill_sym_box(grid, 3, 4, 14, 16, 26, 31, 3) # violet chest vents
    # Backpack with Forward-Swept Wings pointing UPWARD like demon wings!
    fill_sym_box(grid, 1, 3, 6, 8, 22, 31, 2)
    for i in range(9):
        # Wings angle up & outward
        fill_sym_box(grid, 4 + i, 4 + i, 6, 7, 26 + i // 2, 32 + i, 1 if i < 7 else 3)
    fill_sym_box(grid, 2, 2, 4, 6, 22, 30, 9)
    # Spiked Shoulder Pauldrons & Claws (Z: 17..35)
    fill_sym_box(grid, 6, 9, 10, 14, 29, 33, 1)
    fill_sym_box(grid, 8, 10, 11, 13, 33, 35, 3) # vertical shoulder spikes!
    fill_sym_box(grid, 6, 8, 10, 13, 24, 28, 2)
    fill_sym_box(grid, 6, 9, 10, 14, 18, 23, 1)
    fill_sym_box(grid, 9, 9, 11, 13, 18, 23, 9) # forearm blade
    fill_sym_box(grid, 7, 8, 11, 13, 16, 17, 4)
    # Horned / Mono-Eye Ace Head (Z: 33..39)
    fill_sym_box(grid, 0, 2, 10, 14, 33, 37, 1)
    fill_sym_box(grid, 0, 1, 14, 15, 34, 35, 5) # glowing red mono-eye visor
    fill_sym_box(grid, 2, 3, 12, 15, 36, 39, 3) # twin V-horns on forehead!
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

    size_content = struct.pack('<III', X, Y, Z)
    size_chunk = b'SIZE' + struct.pack('<II', len(size_content), 0) + size_content

    xyzi_content = struct.pack('<I', len(voxels))
    for vx, vy, vz, vc in voxels:
        xyzi_content += struct.pack('<BBBB', vx, vy, vz, vc)
    xyzi_chunk = b'XYZI' + struct.pack('<II', len(xyzi_content), 0) + xyzi_content

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

def render_voxel_iso(grid, yaw_deg=-140, pitch_deg=25, scale=7, img_size=(340, 320)):
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
        rx = dx * cos_y - dy * sin_y
        ry = dx * sin_y + dy * cos_y
        rz = dz
        sx = rx * scale + img_size[0] / 2.0
        sy = (ry * sin_p - rz * cos_p) * scale + img_size[1] / 2.0 + 15
        depth = ry * cos_p + rz * sin_p
        return (sx, sy), depth

    visible = []
    for x in range(X):
        for y in range(Y):
            for z in range(Z):
                c = grid[x, y, z]
                if c == 0:
                    continue
                if (0 < x < X-1 and 0 < y < Y-1 and 0 < z < Z-1 and
                    grid[x-1,y,z] and grid[x+1,y,z] and
                    grid[x,y-1,z] and grid[x,y+1,z] and
                    grid[x,y,z-1] and grid[x,y,z+1]):
                    continue
                _, d = project(x + 0.5, y + 0.5, z + 0.5)
                visible.append((d, x, y, z, int(c)))

    visible.sort(key=lambda item: item[0])

    faces = [
        ([(0,0,1), (1,0,1), (1,1,1), (0,1,1)], (0, 0, 1), 1.15),
        ([(0,0,0), (0,1,0), (1,1,0), (1,0,0)], (0, 0, -1), 0.55),
        ([(0,0,0), (1,0,0), (1,0,1), (0,0,1)], (0, -1, 0), 0.92),
        ([(1,1,0), (0,1,0), (0,1,1), (1,1,1)], (0, 1, 0), 0.85),
        ([(0,1,0), (0,0,0), (0,0,1), (0,1,1)], (-1, 0, 0), 0.72),
        ([(1,0,0), (1,1,0), (1,1,1), (1,0,1)], (1, 0, 0), 1.05),
    ]

    vx_dir = sin_y * cos_p
    vy_dir = cos_y * cos_p
    vz_dir = sin_p

    for _, x, y, z, c in visible:
        base_col = PALETTE[c]
        for verts, normal, light in faces:
            nx, ny, nz = normal
            nnx, nny, nnz = x + nx, y + ny, z + nz
            if 0 <= nnx < X and 0 <= nny < Y and 0 <= nnz < Z and grid[nnx, nny, nnz] > 0:
                continue
            dot = nx * (-vx_dir) + ny * (-vy_dir) + nz * vz_dir
            if dot <= 0:
                continue
            poly = [project(x + vx, y + vy, z + vz)[0] for vx, vy, vz in verts]
            fcol = shade_color(base_col, light)
            # Subtle bright edge highlight on dark armor so silhouette pops
            edge_col = shade_color(fcol, 1.25) if c in [1, 2] else shade_color(fcol, 0.85)
            draw.polygon(poly, fill=fcol, outline=edge_col)
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
                    px[x, Y - 1 - y] = PALETTE[int(c)]
        sheet.paste(slice_img, (z * X, 0))
    sheet.save(filename)

# Build all 3 enemy voxel models
e_fighter = build_enemy_fighter()
e_gerwalk = build_enemy_gerwalk()
e_robot = build_enemy_robot()

# Export .vox files
vf = export_vox(e_fighter, "enemy_dark_fighter.vox")
vg = export_vox(e_gerwalk, "enemy_dark_gerwalk.vox")
vr = export_vox(e_robot, "enemy_dark_robot.vox")

# Export Sprite Stacking sheets
export_stack_sheet(e_fighter, "sheet_enemy_fighter.png")
export_stack_sheet(e_gerwalk, "sheet_enemy_gerwalk.png")
export_stack_sheet(e_robot, "sheet_enemy_robot.png")

# Bundle .vox + sprite sheets into a single ZIP
zip_filename = "enemy_dark_valkyrie_pack.zip"
with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write("enemy_dark_fighter.vox")
    zf.write("enemy_dark_gerwalk.vox")
    zf.write("enemy_dark_robot.vox")
    zf.write("sheet_enemy_fighter.png")
    zf.write("sheet_enemy_gerwalk.png")
    zf.write("sheet_enemy_robot.png")

# Render 3D Showcase Preview
canvas = Image.new("RGBA", (1140, 520), (18, 20, 28, 255))
draw = ImageDraw.Draw(canvas)

for gx in range(0, 1140, 20):
    draw.line([(gx, 0), (gx, 520)], fill=(26, 29, 40, 255), width=1)
for gy in range(0, 520, 20):
    draw.line([(0, gy), (1140, gy)], fill=(26, 29, 40, 255), width=1)

draw.text((24, 16), "ENEMY STEALTH ACE: FORWARD-SWEPT FIGHTER / HEAVY GERWALK / HORNED ROBOT (.vox + Sprite Sheets)", fill=(225, 205, 245, 255))

models = [
    ("1. ENEMY FIGHTER (Forward-Swept)", f"Grid: 32x36x20 | Voxels: {vf}", e_fighter, 7.5, -140, 28),
    ("2. ENEMY GERWALK (Twin Blasters)", f"Grid: 32x36x28 | Voxels: {vg}", e_gerwalk, 7.0, -140, 24),
    ("3. ENEMY ROBOT (Horned Ace)", f"Grid: 32x24x40 | Voxels: {vr}", e_robot, 6.8, -145, 20),
]

for idx, (title, meta, m_grid, sc, yaw, pitch) in enumerate(models):
    bx = 24 + idx * 372
    by = 48
    draw.rectangle([bx, by, bx + 348, by + 448], fill=(12, 14, 20, 255), outline=(110, 55, 150, 255), width=2)
    draw.text((bx + 14, by + 12), title, fill=(245, 230, 255, 255))
    draw.text((bx + 14, by + 30), meta, fill=(175, 130, 210, 255))

    r_front = render_voxel_iso(m_grid, yaw_deg=yaw, pitch_deg=pitch, scale=sc, img_size=(340, 320))
    canvas.paste(r_front, (bx + 4, by + 46), r_front)

    r_rear = render_voxel_iso(m_grid, yaw_deg=yaw + 150, pitch_deg=pitch, scale=sc * 0.48, img_size=(140, 140))
    draw.rectangle([bx + 196, by + 296, bx + 338, by + 438], fill=(18, 20, 28, 255), outline=(80, 45, 110, 255))
    canvas.paste(r_rear, (bx + 198, by + 298), r_rear)
    draw.text((bx + 204, by + 302), "REAR VIEW", fill=(165, 120, 195, 255))

    draw.text((bx + 14, by + 412), f"Z-Slices: {m_grid.shape[2]} layers", fill=(180, 160, 205, 255))

canvas.save("enemy_dark_3forms_preview.png")
print("Generated:", zip_filename)
