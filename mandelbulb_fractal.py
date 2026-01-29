import sys
import time
import math
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# ----------------------------
# Mandelbulb parameters (more detail + sharper)
# ----------------------------
POWER = 8.0
MAX_ITERS = 18
BAILOUT = 8.0

# Sampling
N = 92              # 92^3 ~ 778k samples tested (heavier, but sharper)
BBOX = 1.25
DE_THRESHOLD = 0.009   # smaller => thinner/sharper surface (try 0.006..0.012)

# Rendering look
POINT_SIZE = 1.6     # smaller points often look sharper
GAMMA = 0.85         # <1 brightens, >1 darkens
SAT = 0.98

# Animation / camera
ROT_SPEED = 14.0
WAVE_SPEED = 1.0
WAVE_AMP = 0.10

CAM_Z = 2.35         # smaller => zoom in
MODEL_SCALE = 1.55   # larger => zoom in further

# Globals
points = None   # (M,3) float32
colors = None   # (M,3) float32
last_t = None
angle = 0.0

# ----------------------------
# Helpers
# ----------------------------
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

        # derivative update
        dr = dr * POWER * (r ** (POWER - 1.0)) + 1.0

        # power
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
# Build a sharper surface point cloud
# ----------------------------
def generate_point_cloud():
    global points, colors

    xs = np.linspace(-BBOX, BBOX, N, dtype=np.float32)
    ys = np.linspace(-BBOX, BBOX, N, dtype=np.float32)
    zs = np.linspace(-BBOX, BBOX, N, dtype=np.float32)

    pts = []
    cols = []

    # Optional: reject points too far from center to focus on “zoomed region”
    # (keeps more samples where the interesting geometry is)
    focus_radius = 1.05

    for x in xs:
        for y in ys:
            for z in zs:
                r0 = float(x*x + y*y + z*z)
                if r0 > focus_radius * focus_radius:
                    continue

                de, it = mandelbulb_de((float(x), float(y), float(z)))
                if 0.0 < de < DE_THRESHOLD:
                    r = math.sqrt(r0)

                    # Color: iteration-driven hue + slight radius shift
                    h = ((it / MAX_ITERS) * 0.85 + r * 0.25) % 1.0
                    s = SAT
                    # Brightness emphasizes near-surface (smaller de => brighter)
                    v = max(0.0, min(1.0, 1.0 - (de / DE_THRESHOLD)))
                    v = v ** GAMMA

                    rgb = hsv_to_rgb(h, s, v)
                    pts.append((x, y, z))
                    cols.append(rgb)

    points = np.asarray(pts, dtype=np.float32)
    colors = np.asarray(cols, dtype=np.float32)

    if len(points) == 0:
        print("No points generated. Increase DE_THRESHOLD slightly (e.g., 0.011).")
    else:
        print(f"Generated {len(points):,} surface points")

# ----------------------------
# OpenGL / GLUT
# ----------------------------
def init_gl():
    glEnable(GL_DEPTH_TEST)

    # Sharper points:
    glDisable(GL_POINT_SMOOTH)   # disable smoothing for crisp points
    glPointSize(POINT_SIZE)

    glClearColor(0.01, 0.01, 0.02, 1.0)

    # Use arrays (much faster)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)

def reshape(w, h):
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50.0, float(w) / float(h), 0.08, 100.0)
    glMatrixMode(GL_MODELVIEW)

def display():
    global angle

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(
        0.0, 0.0, CAM_Z,
        0.0, 0.0, 0.0,
        0.0, 1.0, 0.0
    )

    # Motion
    glRotatef(angle, 0.0, 1.0, 0.0)
    glRotatef(angle * 0.55, 1.0, 0.0, 0.0)

    t = time.time()
    breathe = 1.0 + WAVE_AMP * math.sin(t * WAVE_SPEED)
    scale = MODEL_SCALE * breathe
    glScalef(scale, scale, scale)

    if points is not None and len(points) > 0:
        glVertexPointer(3, GL_FLOAT, 0, points)
        glColorPointer(3, GL_FLOAT, 0, colors)
        glDrawArrays(GL_POINTS, 0, len(points))

    glutSwapBuffers()

def idle():
    global last_t, angle
    now = time.time()
    if last_t is None:
        last_t = now
    dt = now - last_t
    last_t = now
    angle = (angle + ROT_SPEED * dt) % 360.0
    glutPostRedisplay()

def keyboard(key, x, y):
    if key in (b'\x1b', b'q'):
        sys.exit(0)

def main():
    generate_point_cloud()

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1300, 900)
    glutCreateWindow(b"3D Mandelbulb Fractal (Sharper + Zoomed + Detailed)")

    init_gl()
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)

    glutMainLoop()

if __name__ == "__main__":
    main()
