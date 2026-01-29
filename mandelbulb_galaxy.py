import sys
import time
import math
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# ----------------------------
# Mandelbulb (base fractal)
# ----------------------------
POWER = 8.0
MAX_ITERS = 18
BAILOUT = 8.0

# ----------------------------
# Higher detail sampling
# ----------------------------
N = 100                 # higher => more detail (heavy). Try 80 if slow.
BBOX = 1.25
DE_THRESHOLD = 0.010    # lower => sharper / thinner surface (0.007..0.012)

# ----------------------------
# "Galaxy" warp parameters
# ----------------------------
ARM_COUNT = 4                 # spiral arms
TWIST_STRENGTH = 3.2          # how tightly it spirals (bigger => more twist)
DISK_THINNING = 0.30          # compress Z to resemble a disk (0..1)
CORE_PULL = 0.20              # pull points slightly toward center (0..1)
NOISE_WIGGLE = 0.03           # tiny wiggle for nebula feel (0..0.1)

# ----------------------------
# Rendering / resolution
# ----------------------------
WIN_W, WIN_H = 1600, 1000     # higher "resolution"
POINT_SIZE = 1.3
GAMMA = 0.85
SAT = 1.0

# ----------------------------
# Camera / animation
# ----------------------------
CAM_Z = 2.25
MODEL_SCALE = 1.6
ROT_SPEED = 0.0               # we’ll do custom galaxy rotation per-point instead
TIME_SPEED = 1.0              # overall animation speed

# Globals
base_points = None    # (M,3) float32 (original fractal surface)
base_colors = None    # (M,3) float32 (static base color)
draw_points = None    # (M,3) float32 (warped+animated)
draw_colors = None    # (M,3) float32 (warped colors)
last_t = None

# ----------------------------
# Color helpers (more colors!)
# ----------------------------
def clamp01(x): 
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

def hsv_to_rgb(h, s, v):
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)
    i %= 6
    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else: r, g, b = v, p, q
    return r, g, b

def palette(h, glow, band):
    """
    "More colors" palette:
    - Multi-band hue shifts
    - Slight nebula tint
    - Glow controls brightness
    """
    # 3-band hue modulation
    h = (h + 0.18 * math.sin(2.0 * math.pi * (band + h))
           + 0.12 * math.sin(2.0 * math.pi * (2.7 * band + 1.3 * h))) % 1.0

    s = SAT
    v = clamp01(glow) ** GAMMA

    r, g, b = hsv_to_rgb(h, s, v)

    # Nebula tint (adds extra chroma variation)
    r = clamp01(r * (0.92 + 0.18 * band))
    g = clamp01(g * (0.92 + 0.10 * math.sin(6.0 * band)))
    b = clamp01(b * (0.92 + 0.22 * (1.0 - band)))

    return r, g, b

# ----------------------------
# Mandelbulb distance estimator
# ----------------------------
def mandelbulb_de(p):
    x, y, z = p
    zx, zy, zz = x, y, z
    dr = 1.0
    r = 0.0
    it = 0

    for it in range(MAX_ITERS):
        r = math.sqrt(zx*zx + zy*zy + zz*zz)
        if r > BAILOUT:
            break

        if r == 0.0:
            theta = 0.0
            phi = 0.0
        else:
            theta = math.acos(max(-1.0, min(1.0, zz / r)))
            phi = math.atan2(zy, zx)

        dr = dr * POWER * (r ** (POWER - 1.0)) + 1.0

        zr = r ** POWER
        theta *= POWER
        phi *= POWER

        sin_t = math.sin(theta)
        zx = zr * sin_t * math.cos(phi) + x
        zy = zr * sin_t * math.sin(phi) + y
        zz = zr * math.cos(theta) + z

    if r == 0.0:
        return 0.0, it
    de = 0.5 * math.log(r) * r / dr
    return de, it

# ----------------------------
# Generate base fractal surface points
# ----------------------------
def generate_fractal_surface():
    global base_points, base_colors

    xs = np.linspace(-BBOX, BBOX, N, dtype=np.float32)
    ys = np.linspace(-BBOX, BBOX, N, dtype=np.float32)
    zs = np.linspace(-BBOX, BBOX, N, dtype=np.float32)

    pts = []
    cols = []

    focus_radius = 1.08
    fr2 = focus_radius * focus_radius

    for x in xs:
        for y in ys:
            for z in zs:
                r0 = float(x*x + y*y + z*z)
                if r0 > fr2:
                    continue

                de, it = mandelbulb_de((float(x), float(y), float(z)))
                if 0.0 < de < DE_THRESHOLD:
                    r = math.sqrt(r0)

                    # base hue & glow
                    h = ((it / MAX_ITERS) * 0.85 + r * 0.35) % 1.0
                    glow = 1.0 - (de / DE_THRESHOLD)       # closer to surface => brighter
                    band = clamp01(r / focus_radius)       # 0..1

                    rgb = palette(h, glow, band)
                    pts.append((x, y, z))
                    cols.append(rgb)

    base_points = np.asarray(pts, dtype=np.float32)
    base_colors = np.asarray(cols, dtype=np.float32)

    if len(base_points) == 0:
        print("No points generated. Try increasing DE_THRESHOLD slightly.")
    else:
        print(f"Generated {len(base_points):,} fractal surface points")

# ----------------------------
# Galaxy spiral warp + rotation curve
# ----------------------------
def rotate_y(p, ang):
    ca = math.cos(ang)
    sa = math.sin(ang)
    x, y, z = p
    return (x * ca + z * sa, y, -x * sa + z * ca)

def rotate_z(p, ang):
    ca = math.cos(ang)
    sa = math.sin(ang)
    x, y, z = p
    return (x * ca - y * sa, x * sa + y * ca, z)

def update_galaxy_points(t):
    """
    Warp base_points into a spiral galaxy:
    - log-spiral twist based on radius
    - disk thinning (compress Z)
    - per-point angular velocity (inner rotates faster)
    - optional arms by quantizing angle offsets
    """
    global draw_points, draw_colors

    pts = base_points
    cols = base_colors

    out_pts = np.empty_like(pts)
    out_cols = np.empty_like(cols)

    # Convert time to radians
    tt = t * TIME_SPEED

    for i in range(len(pts)):
        x, y, z = float(pts[i, 0]), float(pts[i, 1]), float(pts[i, 2])

        # Disk thinning (galaxy-like)
        z *= DISK_THINNING

        # Radius in XY plane
        r = math.sqrt(x*x + y*y) + 1e-6
        ang = math.atan2(y, x)

        # Spiral arms: create an "arm phase" from angle
        arm_phase = (ang / (2.0 * math.pi)) * ARM_COUNT
        arm_frac = arm_phase - math.floor(arm_phase)  # 0..1 within arm

        # Log spiral twist: more twist further out
        twist = TWIST_STRENGTH * math.log(1.0 + r * 3.0)

        # Rotation curve: inner rotates faster
        # omega ~ 1/sqrt(r) (clamped), gives nice galaxy feel
        omega = 1.2 / math.sqrt(r + 0.02)
        omega = min(6.0, omega)

        # Total angle: base + twist + time rotation (depends on radius)
        ang2 = ang + twist + omega * tt

        # Slightly lock to arms (creates visible spiral arms)
        # pull angle toward nearest arm center
        arm_center = (round(arm_phase) / ARM_COUNT) * 2.0 * math.pi
        arm_pull = 0.20 * (1.0 - clamp01(r / 1.05)) + 0.05
        ang2 = (1.0 - arm_pull) * ang2 + arm_pull * (arm_center + twist + omega * tt)

        # New XY after spiral
        nx = r * math.cos(ang2)
        ny = r * math.sin(ang2)

        # Core pull (makes a denser bright center)
        nx *= (1.0 - CORE_PULL * math.exp(-r * 2.5))
        ny *= (1.0 - CORE_PULL * math.exp(-r * 2.5))

        # Tiny nebula wiggle
        wig = NOISE_WIGGLE
        nx += wig * math.sin(5.0 * ang + 1.7 * tt) * (0.6 + 0.4 * arm_frac)
        ny += wig * math.cos(4.0 * ang + 1.3 * tt) * (0.6 + 0.4 * arm_frac)
        z  += wig * math.sin(6.0 * ang + 1.9 * tt) * 0.3

        out_pts[i, 0] = nx
        out_pts[i, 1] = ny
        out_pts[i, 2] = z

        # Boost colors near center + along arms for "galaxy glow"
        band = clamp01(r / 1.05)
        core_glow = math.exp(-r * 2.6)
        arm_glow = 0.35 * math.sin(2.0 * math.pi * arm_frac) ** 2
        glow = clamp01(0.55 + 0.55 * core_glow + arm_glow)

        # Recompute palette for extra color richness
        base_r, base_g, base_b = float(cols[i, 0]), float(cols[i, 1]), float(cols[i, 2])
        # Derive hue proxy from base color (approx)
        hue_proxy = (0.33 * base_r + 0.57 * base_g + 0.11 * base_b)
        h = (hue_proxy * 0.9 + 0.25 * (1.0 - band) + 0.10 * math.sin(tt * 0.7)) % 1.0

        rr, gg, bb = palette(h, glow, band)
        out_cols[i, 0] = rr
        out_cols[i, 1] = gg
        out_cols[i, 2] = bb

    draw_points = out_pts
    draw_colors = out_cols

# ----------------------------
# OpenGL / GLUT
# ----------------------------
def init_gl():
    glEnable(GL_DEPTH_TEST)

    # Crisp points
    glDisable(GL_POINT_SMOOTH)
    glPointSize(POINT_SIZE)

    glClearColor(0.005, 0.005, 0.012, 1.0)

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)

def reshape(w, h):
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(48.0, float(w) / float(h), 0.08, 100.0)
    glMatrixMode(GL_MODELVIEW)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(
        0.0, 0.0, CAM_Z,
        0.0, 0.0, 0.0,
        0.0, 1.0, 0.0
    )

    # mild global tilt for cinematic galaxy view
    glRotatef(22.0, 1.0, 0.0, 0.0)

    s = MODEL_SCALE
    glScalef(s, s, s)

    if draw_points is not None and len(draw_points) > 0:
        glVertexPointer(3, GL_FLOAT, 0, draw_points)
        glColorPointer(3, GL_FLOAT, 0, draw_colors)
        glDrawArrays(GL_POINTS, 0, len(draw_points))

    glutSwapBuffers()

def idle():
    t = time.time()
    update_galaxy_points(t)
    glutPostRedisplay()

def keyboard(key, x, y):
    if key in (b'\x1b', b'q'):
        sys.exit(0)

def main():
    generate_fractal_surface()

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutCreateWindow(b"Mandelbulb Galaxy Spiral (More Colors + Higher Resolution)")

    init_gl()
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)

    glutMainLoop()

if __name__ == "__main__":
    main()
