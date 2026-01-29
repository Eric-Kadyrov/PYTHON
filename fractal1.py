import sys
import time
import math
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# ----------------------------
# Mandelbulb parameters
# ----------------------------
POWER = 8.0
MAX_ITERS = 14
BAILOUT = 4.0

# Point cloud sampling
N = 60                      # grid resolution per axis (60 -> ~216k points tested)
BBOX = 1.25                 # sampling box half-size
POINT_SIZE = 2.0

# Animation
ROT_SPEED = 18.0            # degrees per second
WAVE_SPEED = 1.2
WAVE_AMP = 0.25

# Globals
points = None               # (M,3) float32
colors = None               # (M,3) float32
last_t = None
angle = 0.0

# ----------------------------
# Mandelbulb distance estimator (approx)
# ----------------------------
def mandelbulb_de(p):
    x, y, z = p
    zx, zy, zz = x, y, z
    dr = 1.0
    r = 0.0

    for i in range(MAX_ITERS):
        r = math.sqrt(zx*zx + zy*zy + zz*zz)
        if r > BAILOUT:
            break

        # Convert to polar
        if r == 0.0:
            theta = 0.0
            phi = 0.0
        else:
            theta = math.acos(max(-1.0, min(1.0, zz / r)))
            phi = math.atan2(zy, zx)

        # Scale + derivative
        zr = r ** (POWER - 1.0)
        dr = dr * POWER * zr + 1.0

        # Raise to power
        zr2 = r ** POWER
        theta *= POWER
        phi *= POWER

        # Back to cartesian
        sin_t = math.sin(theta)
        zx = zr2 * sin_t * math.cos(phi) + x
        zy = zr2 * sin_t * math.sin(phi) + y
        zz = zr2 * math.cos(theta) + z

    # Distance estimate
    if r == 0.0:
        return 0.0, i
    de = 0.5 * math.log(r) * r / dr
    return de, i

def hsv_to_rgb(h, s, v):
    # h in [0,1)
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

def generate_point_cloud():
    """
    Sample a 3D grid, keep points that are near the Mandelbulb surface by DE threshold.
    Produces a colorful point cloud with hue based on iteration count + radius.
    """
    global points, colors

    xs = np.linspace(-BBOX, BBOX, N, dtype=np.float32)
    ys = np.linspace(-BBOX, BBOX, N, dtype=np.float32)
    zs = np.linspace(-BBOX, BBOX, N, dtype=np.float32)

    pts = []
    cols = []

    # DE threshold controls "surface thickness"
    # Smaller -> thinner, fewer points; larger -> thicker, more points
    de_threshold = 0.015

    for x in xs:
        for y in ys:
            for z in zs:
                de, it = mandelbulb_de((float(x), float(y), float(z)))
                if 0.0 < de < de_threshold:
                    r = math.sqrt(float(x*x + y*y + z*z))
                    # Hue: mix iteration + radius
                    h = ((it / MAX_ITERS) * 0.75 + r * 0.35) % 1.0
                    s = 0.95
                    v = 1.0
                    rgb = hsv_to_rgb(h, s, v)

                    pts.append((x, y, z))
                    cols.append(rgb)

    points = np.array(pts, dtype=np.float32)
    colors = np.array(cols, dtype=np.float32)

    print(f"Generated {len(points):,} surface points")

# ----------------------------
# OpenGL / GLUT
# ----------------------------
def init_gl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_POINT_SMOOTH)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
    glPointSize(POINT_SIZE)
    glClearColor(0.02, 0.02, 0.03, 1.0)

def reshape(w, h):
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(55.0, float(w) / float(h), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def display():
    global angle

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Camera
    gluLookAt(0.0, 0.0, 3.3,  # eye
              0.0, 0.0, 0.0,  # center
              0.0, 1.0, 0.0)  # up

    # Animated transforms
    glRotatef(angle, 0.0, 1.0, 0.0)
    glRotatef(angle * 0.6, 1.0, 0.0, 0.0)

    # Subtle "breathing" scale
    t = time.time()
    s = 1.0 + WAVE_AMP * math.sin(t * WAVE_SPEED)
    glScalef(s, s, s)

    # Draw points
    if points is not None and len(points) > 0:
        glBegin(GL_POINTS)
        for (p, c) in zip(points, colors):
            glColor3f(float(c[0]), float(c[1]), float(c[2]))
            glVertex3f(float(p[0]), float(p[1]), float(p[2]))
        glEnd()

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
    if key in (b'\x1b', b'q'):  # ESC or q
        sys.exit(0)

def main():
    generate_point_cloud()

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1100, 800)
    glutCreateWindow(b"3D Mandelbulb Fractal (Colorful Motion)")

    init_gl()

    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)

    glutMainLoop()

if __name__ == "__main__":
    main()
