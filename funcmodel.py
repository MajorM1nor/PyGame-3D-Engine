# --------------------------------------------------
# Module for Model Related transformation functions
# --------------------------------------------------
import math

# -----------------------------------------------------
# Transforms passed object's position in 3D space
# -----------------------------------------------------
def transform(object, x, y, z):
    object.x += x
    object.y += y
    object.z += z

# -----------------------------------------------------
# Translates passed object's position in 3D space
# -----------------------------------------------------
def translate(object, x, y, z):
    object.x = x
    object.y = y
    object.z = z

# ------------------------------------------
# Returns x, y, z position of passed object
# ------------------------------------------
def get_coords(object):
    object = model.x
    object = model.y
    object = model.z
    return x, y, z

# ------------------------------------
# Scales given model
# ------------------------------------
def scale(model, scale):
    for a in range(len(model.vertices)):
        model.vertices[a][0] *= scale
        model.vertices[a][1] *= scale
        model.vertices[a][2] *= scale

# --------------------------------------------
# Rotates given model using rotation matrices
# --------------------------------------------
def rotate(model, xrot, yrot, zrot):
    model.x_rot = xrot
    model.y_rot = yrot
    model.z_rot = zrot

    cosA = math.cos(zrot)
    sinA = math.sin(zrot)
    cosB = math.cos(xrot)
    sinB = math.sin(xrot)
    cosC = math.cos(yrot)
    sinC = math.sin(yrot)

    matXX = cosA * cosB
    matXY = cosA * sinB * sinC - sinA * cosC
    matXZ = cosA * sinB * cosC + sinA * sinC

    matYX = sinA * cosB
    matYY = sinA * sinB * sinC + cosA * cosC
    matYZ = sinA * sinB * cosC - cosA * sinC

    matZX = -sinB
    matZY = cosB * sinC
    matZZ = cosB * cosC

    for a in range(len(model.vertices)):
        x = model.vertices[a][0]
        y = model.vertices[a][1]
        z = model.vertices[a][2]

        model.vertices[a][0] = matXX * x + matXY * y + matXZ * z
        model.vertices[a][1] = matYX * x + matYY * y + matYZ * z
        model.vertices[a][2] = matZX * x + matZY * y + matZZ * z