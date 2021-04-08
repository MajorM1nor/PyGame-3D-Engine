import pygame as pyg
from tkinter import Tk
from funcmath import *
from funcmodel import *

DEBUG_MODE = False  # Global, debug mode enabled?
MOUSE_MOVE = False  # Global, is mouse look enabled?
MOUSE_SENS = 0.002  # Global, mouse sensitivity

phys_drag = 0.0002  # Air Resistance present in scene

# Fallback res if full-screen not found
SCREEN_WIDTH, SCREEN_HEIGHT = 720, 480

tk = Tk()
SCREEN_WIDTH = tk.winfo_screenwidth()
SCREEN_HEIGHT = tk.winfo_screenheight()
del tk

HALF_SCREEN_W = int(SCREEN_WIDTH / 2)
HALF_SCREEN_H = int(SCREEN_HEIGHT / 2)

# ---- Creating Color Constants ----
C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)
C_GREEN = (0, 255, 0)
C_BLUE = (0, 0, 255)
C_RED = (255, 0, 0)
C_CYAN = (0, 255, 255)

# ---- PyGame Initialization Code ----
pyg.init()
pyg.display.init()
pyg.font.init()

screen_bgc = (C_BLACK)
font = pyg.font.Font(None, 32)
pyg.display.set_caption("3D Renderer")

scr_flags = pyg.FULLSCREEN | pyg.DOUBLEBUF  # Screen flag parameters

# Surface that holds screen gfx
screen = pyg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), scr_flags)

pyg.mouse.set_visible(False)
pyg.event.set_grab(True)

modelList = []  # List of all currently loaded models


# ---------------------------------
# Handles all event and game logic
# ---------------------------------
def event_handler(event):
    if event.type == pyg.QUIT:
        pyg.quit()

    # Handles key press events
    if event.type == pyg.KEYDOWN:
        if event.key == pyg.K_ESCAPE:
            pyg.quit()

        if event.key == pyg.K_1:
            global DEBUG_MODE
            if DEBUG_MODE:
                DEBUG_MODE = False
                print("Debug Mode Disabled")
            else:
                DEBUG_MODE = True
                print("Debug Mode Enabled")


# ----------------------------------------------
# Clears model list, loads scene into modelList
# ----------------------------------------------
def import_scene(file_name):
    global modelList
    modelList = []

    raw_data = load_file(file_name, "scenes/")

    global player
    stats = raw_data
    stats = stats[stats.find("-Player-\n") + 9:stats.find("-Models-\n") - 1]
    stats = stats.split(",")

    x = float(stats[0])
    y = float(stats[1])
    z = float(stats[2])

    translate(player, x, y, z)

    models = raw_data
    models = models[models.find("-Models-\n") + 9:]
    models = models.split("\n")

    for a in range(len(models)):
        temp_model = models[a].split(", ")

        name = temp_model[0]
        x = float(temp_model[1])
        y = float(temp_model[2])
        z = float(temp_model[3])

        x_rot = float(temp_model[4])
        y_rot = float(temp_model[5])
        z_rot = float(temp_model[6])
        model_scale = float(temp_model[7])

        model = Model(x, y, z, x_rot, y_rot, z_rot, name, True)
        scale(model, model_scale)


# --------------------------------------------------
# Draws debug info to screen if DEBUG_MODE == True
# --------------------------------------------------
def debug():

    # Drawing vertice IDs to Screen
    if DEBUG_MODE:
        for model in modelList:
            vertice_id = 0
            temp_points = project_points(player.cam, model, SCREEN_WIDTH)
            for vert in temp_points:
                depth = temp_points[vertice_id][2]
                if depth > 0:
                    x = vert[0] + HALF_SCREEN_W
                    y = vert[1] + HALF_SCREEN_H
                    HUD.text(x, y, str(vertice_id))
                    vertice_id += 1


# ----------------------------------------------------------------
# Loads file, removing comments and returning text string of data
# ----------------------------------------------------------------
def load_file(file_name, file_path):
    raw_data = ""

    with open(file_path + file_name, "r") as open_file:
        line = open_file.readline()
        # Removing comments in file from data
        while line: 
            if (line.find("#") == -1): 
                raw_data += line
            line = open_file.readline()
    
    return raw_data


# -------------------------------------------------------
# PLAYER CLASS: Acts as event handler for player input,
# as well as controlling player and camera movement
# -------------------------------------------------------
class Player:
    def __init__(self, x, y, z):

        self.x = x
        self.y = y
        self.z = z

        self.move_speed = 0.05

        self.cam = Camera(x, y, z, 0, 0, 0)

    def key_update(self):
        key = pyg.key.get_pressed()

        # Forward / Backward movement
        if key[pyg.K_w]:
            self.x += clamp(length_dir_x(self.move_speed, self.cam.x_rot), 0, self.move_speed)
            self.y += clamp(length_dir_y(self.move_speed, self.cam.y_rot), 0, self.move_speed)
            self.z += clamp(length_dir_z(self.move_speed, self.cam.x_rot), 0, self.move_speed)
        if key[pyg.K_s]:
            self.x -= clamp(length_dir_x(self.move_speed, self.cam.x_rot), 0, self.move_speed)
            self.y -= clamp(length_dir_y(self.move_speed, self.cam.y_rot), 0, self.move_speed)
            self.z -= clamp(length_dir_z(self.move_speed, self.cam.x_rot), 0, self.move_speed)

        # Strafing Left and Right
        if key[pyg.K_a]:
            self.x += length_dir_x(self.move_speed, self.cam.x_rot + math.pi / 2)
            self.z += length_dir_z(self.move_speed, self.cam.x_rot + math.pi / 2)
        if key[pyg.K_d]:
            self.x += length_dir_x(self.move_speed, self.cam.x_rot - math.pi / 2)
            self.z += length_dir_z(self.move_speed, self.cam.x_rot - math.pi / 2)

        # Turning Camera using arrow keys
        if key[pyg.K_LEFT]:
            self.cam.rotate_camera(0.015, 0, 0)
        if key[pyg.K_RIGHT]:
            self.cam.rotate_camera(-0.015, 0, 0)
        if key[pyg.K_UP]:
            self.cam.rotate_camera(0, 0.015, 0)
        if key[pyg.K_DOWN]:
            self.cam.rotate_camera(0, -0.015, 0)

        # Moving Up and Down
        if key[pyg.K_SPACE]:
            transform(self, 0, -self.move_speed, 0)
        if key[pyg.K_LSHIFT]:
            transform(self, 0, self.move_speed, 0)

    def update(self):

        # Translates camera every frame
        translate(self.cam, self.x, self.y, self.z)

        if(MOUSE_MOVE):
            # Rotating camera via mouse movement
            mouse_move_x, mouse_move_y = pyg.mouse.get_rel()
            mouse_move_x *= MOUSE_SENS
            mouse_move_y *= MOUSE_SENS

            self.cam.rotate_camera(-mouse_move_x, -mouse_move_y, 0)

        # Locking Y Rotation to +1.5 and -1.5
        if self.cam.y_rot < -1.5:
            self.cam.y_rot = -1.5
        if self.cam.y_rot > 1.5:
            self.cam.y_rot = 1.5

        self.cam.update()


# ---------------------------------------------------------
# MODEL CLASS: Each currently loaded model is it's own
# model object, holding all positional and rotational data
# ---------------------------------------------------------
class Model:

    def __init__(self, x, y, z, xrot, yrot, zrot, modelname, solid):
        self.x = x  # Model 3D X Position
        self.y = y  # Model 3D Y Position
        self.z = z  # Model 3D Z Position

        self.x_rot = xrot  # Model X-Axis rotation
        self.y_rot = yrot  # Model Y-Axis rotation
        self.z_rot = zrot  # Model Z-Axis rotation

        self.x_vel = 0  # Current Model X Velocity
        self.y_vel = 0  # Current Model Y Velocity
        self.z_vel = 0  # Current Model Z Velocity

        self.x_vel_a = 0  # Current Model Angular X Velocity
        self.y_vel_a = 0  # Current Model Angular Y Velocity
        self.z_vel_a = 0  # Current Model Angular Z Velocity

        self.solid = solid  # Boolean, if model has AABB enabled

        self.vertices = []  # Stores models loaded vertices data
        self.faces = []  # Stores models loaded face data

        self.model_name = modelname  # Name of Model File
        self.import_model(modelname)

        self.distance = 0  # Distance to camera

        modelList.append(self)

    # Unloads model from memory
    def del_model(self):
        modelList.remove(self)
        del self

    # Returns model vertex and face data in 2 lists from txt file
    def import_model(self, file_name):

        raw_data = load_file(file_name, "models/")

        verts = raw_data
        faces = raw_data

        verts = verts[verts.find("Model Vertices\n") + 15:verts.find("Model Faces\n") - 1]
        verts = verts.split("\n")  # Splits model into coordinate triplets

        self.vertices = []
        for a in range(len(verts)):
            self.vertices.append(verts[a].split(","))

        # Converts vertex coordinates to ints
        for a in range(len(self.vertices)):
            for b in range(0, 3):
                self.vertices[a][b] = float(self.vertices[a][b])

        faces = faces[faces.find("Model Faces\n") + 12:]
        faces = faces.split("\n")  # Splits model into coordinate triplets

        self.faces = []
        for a in range(len(faces)):
            self.faces.append(faces[a].split(","))

        for a in range(
                len(self.faces)):  # Converts face point coordinates to ints
            for b in range(0, 6):
                self.faces[a][b] = int(self.faces[a][b])

        # model_vertices[x, y, z]
        # model_faces[vertID1, vertID2, vertID3, r, g, b]

    def physics_update(self):
        transform(self, self.x_vel, self.y_vel, self.z_vel)
        rotate(self, self.x_vel_a, self.y_vel_a, self.z_vel_a)

        global phys_drag

        if self.x_vel > 0:
            self.x_vel -= phys_drag
        elif self.x_vel < 0:
            self.x_vel += phys_drag

        if self.y_vel > 0:
            self.y_vel -= phys_drag
        elif self.y_vel < 0:
            self.y_vel += phys_drag

        if self.z_vel > 0:
            self.z_vel -= phys_drag
        elif self.z_vel < 0:
            self.z_vel += phys_drag


# --------------------------------------------
# CAMERA CLASS: Acts as a view port for world
# renders 3D-Space objects to 2D screen
# --------------------------------------------
class Camera:
    def __init__(self, x, y, z, xrot, yrot, zrot):
        self.x = x
        self.y = y
        self.z = z

        self.x_rot = xrot  # Current camera X-Axis rotation
        self.y_rot = yrot  # Current camera Y-Axis rotation
        self.z_rot = zrot  # Current camera Z-Axis rotation

        self.render_distance = 50  # How far models are rendered

        self.target = None  # Current object target

    def update(self):

        if self.target is not None:
            tar_x, tar_y, tar_z = get_coords(self.target)

            ang_x, ang_y, ang_z = point_at(self.x, self.y, self.z, tar_x, tar_y, tar_z)

            ang_x /= -ang_z
            ang_y /= -ang_z

            self.x_rot = ang_x
            self.y_rot = ang_y

    # Rotates camera
    def rotate_camera(self, x, y, z):
        self.x_rot += x
        self.z_rot += z

        if -90 < self.y_rot < 90:
            self.y_rot += y

    # Sets target object for camera
    def set_target(self, target):
        self.target = target


# ----------------------------------------
# HUD CLASS: Static class to hold methods
# for drawing HUD elements to screen
# ----------------------------------------
class HUD:

    # Draws box to screen
    def box(x, y, w, h):
        pyg.draw.rect(screen, (C_WHITE), (x, y, w, h), 2)

    # Draws filled box to screen
    def rect(x, y, w, h):
        pyg.draw.rect(screen, (C_WHITE), (x, y, w, h), 2)
        pyg.draw.rect(screen, (C_BLACK), (x + 1, y + 1, w - 1, h - 1), 0)

    # Draws text to screen
    def text(x, y, string):
        screen.blit(font.render(string, 0, (C_WHITE)), (x, y))


player = Player(0, 0, 0)
import_scene("sceneTest")

modelList[0].x_vel_a = 0.007
modelList[0].z_vel_a = 0.01

# ---------------------------------------------------------
#                     Main Game Loop
# ---------------------------------------------------------
clock = pyg.time.Clock()
while True:

    clock.tick(60)

    for event in pyg.event.get():
        event_handler(event)

    screen.fill(screen_bgc)

    player.key_update()
    player.update()

    # Sorting master model list, by model depth
    for mod in modelList:
        mod.distance = dist_to_point(player.x, player.y, player.z, mod.x, mod.y, mod.z)
        mod.physics_update()
    modelList.sort(key=lambda x: x.distance, reverse=True)

    # Rendering each model
    for model in modelList:

        # List of every rendered poly in model
        poly = render_model(player.cam, model, SCREEN_WIDTH, SCREEN_HEIGHT, False)

        # Drawing each polygon of model
        for index, polygon in enumerate(poly):
            r, g, b = poly[index][0], poly[index][1], poly[index][2]
            x1, y1 = poly[index][3], poly[index][4]
            x2, y2 = poly[index][5], poly[index][6]
            x3, y3 = poly[index][7], poly[index][8]

            r = clamp(r, 0, 255)
            g = clamp(g, 0, 255)
            b = clamp(b, 0, 255)

            # Draws polygons
            pyg.draw.polygon(screen, (r, g, b), ((x1, y1), (x2, y2), (x3, y3)), 0)

    # Draws dot cross-hair
    pyg.draw.circle(screen, (255, 255, 255), (HALF_SCREEN_W, HALF_SCREEN_H), 2)

    debug()
    pyg.display.flip()
