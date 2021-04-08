# ------------------------------------
# Module for storing static functions
# ------------------------------------
import math

# ------------------------------------------
# Returns X position for a passed 2D vector
# ------------------------------------------
def length_dir_x(length, direction):
    return -1 * (math.sin(direction)) * length


# ------------------------------------------
# Returns Y position for a passed 2D vector
# ------------------------------------------
def length_dir_y(length, direction):
    return -1 * (math.tan(direction)) * length


# ------------------------------------------
# Returns Z position for a passed 2D vector
# ------------------------------------------
def length_dir_z(length, direction):
    return math.cos(direction) * length


# ----------------------------
# Returns rotated camera axis
# ----------------------------
def camera_rotate(axis, z_axis, direction):
    axis_out = z_axis * math.sin(direction) + axis * math.cos(direction)
    z_axis_out = z_axis * math.cos(direction) - axis * math.sin(direction)
    return axis_out, z_axis_out

# -----------------------------------------------------
# Returns distance between two points in 3D space
# -----------------------------------------------------
def dist_to_point(x1, y1, z1, x2, y2, z2):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2) + math.pow(z2 - z1, 2))


# Returns Vector3, adjustment for x, y, and z rotation
def point_at(x1, y1, z1, x2, y2, z2):
    return x2 - x1, y2 - y1, z2 - z1


# ----------------------------------
# Returns 3D center point of a face
# ----------------------------------
def center_point(x1, y1, z1, x2, y2, z2, x3, y3, z3):
    x = (x1 + x2 + x3) / 3
    y = (y1 + y2 + y3) / 3
    z = (z1 + z2 + z3) / 3
    return x, y, z


# ------------------------------
# Returns cross product of face
# ------------------------------
def cross_product(x1, y1, x2, y2, x3, y3):
    return (x2 * y3 - x3 * y2) - (x1 * y3 - x3 * y1) + (x1 * y2 - x2 * y1)


# -----------------------------------------------------
# Returns passed variable, limited between min and max
# -----------------------------------------------------
def clamp(x, min, max):
    if x > max:
        x = max
    elif x < min:
        x = min
    return x


# ------------------------------------------------------
# camera: Passed Camera Object
# model: Passed Model Object to be rendered
# scrn_w: Screen Width
# scrn_h: Screen Height
# IF ret_cross:
#  returns list of cross products of each face in model
# ELSE:
#  returns list of 2D position of faces to be drawn
# ------------------------------------------------------
def render_model(camera, model, scrn_w, scrn_h, ret_cross):
    half_screen_w = scrn_w / 2
    half_screen_h = scrn_h / 2

    rendered_model = []

    if model.distance < camera.render_distance:

        translated_points = []  # Holds 2D point data for each polygon in model
        translated_points = project_points(camera, model, scrn_w)

        # Projects 2D points to screen
        for p1, p2, p3, r, g, b in model.faces:

            # Holds depth of each points in tri
            d1 = translated_points[p1][2]
            d2 = translated_points[p2][2]
            d3 = translated_points[p3][2]

            # Checks if points are within view-cone
            if d1 > 0 and d2 > 0 and d3 > 0:

                # Transforms 2D points to screen bounds
                x1 = translated_points[p1][0] + half_screen_w
                y1 = translated_points[p1][1] + half_screen_h
                x2 = translated_points[p2][0] + half_screen_w
                y2 = translated_points[p2][1] + half_screen_h
                x3 = translated_points[p3][0] + half_screen_w
                y3 = translated_points[p3][1] + half_screen_h

                # Finds surface normal cross product of a polygon
                cross_prod = cross_product(x1, y1, x2, y2, x3, y3)

                if ret_cross:
                    rendered_model.append(cross_prod)

                # Draws polygon if back-face cull is good
                if cross_prod > 0 and not ret_cross:
                    rendered_model.append([r, g, b, x1, y1, x2, y2, x3, y3])

    return rendered_model


# ---------------------------------------------
# Projects 3D Vertex data in model to 2D plane
# Returns list of 2D points
# ---------------------------------------------
def project_points(camera, model, screen_w):
    half_screen_w = screen_w / 2

    translated_points = []  # Holds 2D point data for each vertex in model

    # Projects 3D points to 2D surface
    for x, y, z in model.vertices:
        x -= camera.x - model.x
        y -= camera.y - model.y
        z -= camera.z - model.z

        x, y = camera_rotate(x, y, camera.z_rot)
        x, z = camera_rotate(x, z, camera.x_rot)
        y, z = camera_rotate(y, z, camera.y_rot)

        translated_z = half_screen_w / z
        x, y = translated_z * x, translated_z * y
        translated_points.append((x, y, translated_z))

    return translated_points

# -----------------------------------------
# Toggles a boolean between True and False
# -----------------------------------------
def toggle(x):
    if x:
        x = False
    else:
        x = True