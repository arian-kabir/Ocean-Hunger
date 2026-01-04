from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
# Camera-related variables
camera_pos = (0,300,100)
player_pos=(0,0,0)
player_angle=0
pov=False
fovY = 120 
GRID_LENGTH = 125  
exp=20
health=100
food=False
counter=0
wave=False
wave_from=""
var=GRID_LENGTH*(6)
wave_colli=False
bait_caught=False
caught_counter=0
escape_chance=0
escape_check=False
rear=False
hpdecrease=0

min_of_x = GRID_LENGTH * (-6)  
max_of_x = GRID_LENGTH * (7)   
min_of_y = GRID_LENGTH * (-7)  
max_of_y = GRID_LENGTH * (6)    
stones = []        
plants = []        
small_fishes = []
big_fishes = []    
plant_wave_offset = 0.0  
hunger_counter = 0         
HUNGER_LIMIT = 1200         
MOVE_SLOW_FACTOR = 0.35     
slow_mode = False           
blink_on = False          
blink_counter = 0       
BLINK_PERIOD_FRAMES = 24   # faster hungry blink cycle
BLINK_ON_FRAMES = 3        # short flash duration per cycle


# Player growth
player_size = 1.0

# Food + trap objects
food_items = []
trap_items = []

FOOD_COUNT = 10
TRAP_COUNT = 6
FOOD_Z_BASE = 65.0
FOOD_Z_AMP = 10.0
FOOD_CATCH_RADIUS = 55.0

# Enemy attack/dodge
DODGE_FRAMES = 18
DODGE_DISTANCE = 170
dodge_timer = 0
enemy_attack_cooldown = 0
ENEMY_DETECT_RADIUS = 220.0
ENEMY_ATTACK_RADIUS = 80.0
ENEMY_DAMAGE = 6
ENEMY_ATTACK_COOLDOWN_FRAMES = 25

# After dodging, enemy won't attack for a while
ENEMY_PEACE_FRAMES = 180
enemy_peace_timer = 0

# Damage blink (for enemy hit / wrong food)
DAMAGE_BLINK_FRAMES = 40
damage_blink_timer = 0

# Animation time
anim_t = 0.0

# Enemy: small count, but actively attacks
ENEMY_COUNT = 2
enemy_event_timer = 0
enemy_attacker_idx = None

# Bite attack (player attacks smaller fish)
ATTACK_RADIUS = 90.0
GROWTH_PER_KILL = 0.08


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _dist2(ax, ay, bx, by):
    dx = ax - bx
    dy = ay - by
    return dx * dx + dy * dy


def spawn_food_and_traps():
    global food_items, trap_items
    food_items = []
    trap_items = []

    # Safe food
    for _ in range(FOOD_COUNT):
        x = random.randint(min_of_x + 120, max_of_x - 120)
        y = random.randint(min_of_y + 120, max_of_y - 120)
        phase = random.uniform(0.0, 6.28)
        food_items.append({"x": x, "y": y, "phase": phase})

    # Trapped bait (string attached)
    for _ in range(TRAP_COUNT):
        x = random.randint(min_of_x + 140, max_of_x - 140)
        y = random.randint(min_of_y + 140, max_of_y - 140)
        phase = random.uniform(0.0, 6.28)
        trap_items.append({"x": x, "y": y, "phase": phase})


def food_z(phase):
    return FOOD_Z_BASE + FOOD_Z_AMP * math.sin(phase)


def draw_food_item(it):
    z = food_z(it["phase"])
    glPushMatrix()
    glTranslatef(it["x"], it["y"], z)
    glColor3f(1.0, 0.8, 0.2)
    gluSphere(gluNewQuadric(), 10, 10, 10)
    glPopMatrix()


def draw_trap_item(it):
    z = food_z(it["phase"])

    # bait
    glPushMatrix()
    glTranslatef(it["x"], it["y"], z)
    glColor3f(0.95, 0.95, 0.95)
    gluSphere(gluNewQuadric(), 9, 10, 10)
    glPopMatrix()

    # string
    glPushMatrix()
    glTranslatef(it["x"], it["y"], z)
    glColor3f(0.8, 0.8, 0.8)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 1.2, 1.2, 70, 6, 1)
    glPopMatrix()


def try_collect_food_or_trap():
    global food, bait_caught, food_items, trap_items, damage_blink_timer, health, exp, caught_counter, escape_check, escape_chance

    # if health <= 0 or exp <= 0:
    #     return

    px, py, _ = player_pos
    catch_r2 = (FOOD_CATCH_RADIUS * player_size) ** 2

    # Safe food first
    remaining_food = []
    for it in food_items:
        if _dist2(px, py, it["x"], it["y"]) <= catch_r2:
            food = True
        else:
            remaining_food.append(it)
    food_items = remaining_food

    # Traps: if collected, player is caught
    remaining_traps = []
    for it in trap_items:
        if _dist2(px, py, it["x"], it["y"]) <= catch_r2:
            # Wrong food: end the game immediately and flash red.
            damage_blink_timer = max(damage_blink_timer, DAMAGE_BLINK_FRAMES)
            # Also clear bait-caught state so the original idle() spin logic can't keep rotating.
            bait_caught = True
            caught_counter = 0
            escape_check = False
            escape_chance = 0
        else:
            remaining_traps.append(it)
    trap_items = remaining_traps


def enemy_ai_and_attack():
    global health, enemy_attack_cooldown, enemy_event_timer, enemy_attacker_idx, damage_blink_timer, enemy_peace_timer

    if health <= 0 or exp <= 0:
        return

    # After a dodge, enemies should not attack.
    if enemy_peace_timer > 0:
        return

    px, py, _ = player_pos

    # Always keep an attacker active (switch attacker occasionally).
    if len(big_fishes) == 0:
        return

    if enemy_event_timer <= 0 or enemy_attacker_idx is None or enemy_attacker_idx >= len(big_fishes):
        enemy_attacker_idx = random.randint(0, len(big_fishes) - 1)
        enemy_event_timer = random.randint(600, 1200)
    else:
        enemy_event_timer -= 1

    if enemy_attack_cooldown > 0:
        enemy_attack_cooldown -= 1

    if enemy_attacker_idx is None or enemy_attacker_idx >= len(big_fishes):
        return

    for idx, f in enumerate(big_fishes):
        if idx != enemy_attacker_idx:
            continue
        dx = px - f["x"]
        dy = py - f["y"]
        d2 = dx * dx + dy * dy

        # Do NOT follow the player. Only face the player when close.
        if d2 <= ENEMY_DETECT_RADIUS * ENEMY_DETECT_RADIUS:
            ang = math.atan2(dx, -dy)
            f["a"] = (math.degrees(ang)) % 360

        # Attack if close (unless dodging)
        if d2 <= ENEMY_ATTACK_RADIUS * ENEMY_ATTACK_RADIUS and dodge_timer <= 0:
            if enemy_attack_cooldown <= 0:
                health = max(0, health - ENEMY_DAMAGE)
                enemy_attack_cooldown = ENEMY_ATTACK_COOLDOWN_FRAMES
                damage_blink_timer = max(damage_blink_timer, DAMAGE_BLINK_FRAMES)


def do_dodge():
    global player_pos, dodge_timer, enemy_peace_timer, enemy_attack_cooldown
    if health <= 0 or exp <= 0:
        return

    if dodge_timer > 0:
        return

    x, y, z = player_pos
    angle = math.radians(player_angle)

    # dash sideways (perpendicular to facing)
    sx = math.cos(angle) * DODGE_DISTANCE
    sy = math.sin(angle) * DODGE_DISTANCE

    nx = _clamp(x + sx, min_of_x + 20, max_of_x - 20)
    ny = _clamp(y + sy, min_of_y + 20, max_of_y - 20)
    player_pos = (nx, ny, z)
    dodge_timer = DODGE_FRAMES
    enemy_peace_timer = ENEMY_PEACE_FRAMES
    enemy_attack_cooldown = ENEMY_ATTACK_COOLDOWN_FRAMES


def tick_enemy_peace_timer():
    global enemy_peace_timer
    if enemy_peace_timer > 0:
        enemy_peace_timer -= 1


def tick_dodge_timer():
    global dodge_timer
    if dodge_timer > 0:
        dodge_timer -= 1


def player_bite_attack():
    global player_size, exp, small_fishes, big_fishes
    if health <= 0 or exp <= 0:
        return

    px, py, _ = player_pos
    r2 = (ATTACK_RADIUS * player_size) ** 2

    # Eat small fishes first
    for i, f in enumerate(list(small_fishes)):
        if _dist2(px, py, f["x"], f["y"]) <= r2 and player_size > 0.55:
            small_fishes.pop(i)
            player_size += GROWTH_PER_KILL
            exp += 1
            return

    # Later, allow eating big fish if player is bigger
    for i, f in enumerate(list(big_fishes)):
        if _dist2(px, py, f["x"], f["y"]) <= r2 and player_size > 1.25:
            big_fishes.pop(i)
            player_size += (GROWTH_PER_KILL * 2.0)
            exp += 2
            return


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player(x,y,z, size=1):
    glPushMatrix()
    glTranslatef(x,y,z)
    glRotatef(player_angle, 0, 0, 1)
    if health<1 or exp<1:
        glRotatef(-90, 1, 0, 0)
    if pov:
        pass
    else:
        glPushMatrix()
        glScalef(1.0*size, 3*size, 2*size)
        glTranslatef(0, 0, 20)
        glColor3f(1, 77/255, 0)
        gluSphere(gluNewQuadric(), 15, 10, 10) 
        glPopMatrix()
        glPushMatrix()
        glScalef(0.2*size, 1*size, 1*size)
        glTranslatef(0,80,0) 
        # glRotatef(90, 0, 1, 0) 
        glRotatef(90, 1, 0, 0) 
        glRotatef(-45, 1, 0, 0) 
        glColor3f(0.8,0.8,1)
        gluCylinder(gluNewQuadric(), 4, 16, 50, 10, 10)  
        glTranslatef(0,50,50) 
        glRotatef(90, 1, 0, 0)  
        gluCylinder(gluNewQuadric(), 4, 16, 50, 10, 10)  
        glPopMatrix()
        glPushMatrix()
        glScalef(1.0*size, 1*size, 1*size)
        glRotatef(150, 1, 0, 0)
        glTranslatef(0,30,-80)
        gluCylinder(gluNewQuadric(), 0, 4, 18, 10, 10)
        glRotatef(-100, 1, 0, 0)
        glTranslatef(0,-60,-50)
        gluCylinder(gluNewQuadric(), 0, 4, 14, 10, 10)  
        glPopMatrix()
    glPopMatrix()

def draw_borders(height=125):  
    xL = min_of_x
    xR = max_of_x
    yB = min_of_y
    yT = max_of_y
    glBegin(GL_QUADS)
    
    # left wall
    glColor3f(0, 0, 1)
    glVertex3f(xL, yB, 0)
    glVertex3f(xL, yB, height)
    glVertex3f(xL, yT, height)
    glVertex3f(xL, yT, 0)

    # right wall
    glColor3f(0, 1, 0)
    glVertex3f(xR, yB, 0)
    glVertex3f(xR, yB, height)
    glVertex3f(xR, yT, height)
    glVertex3f(xR, yT, 0)

    # top wall
    glColor3f(0.0, 0.8, 0.9)
    glVertex3f(xL, yT, 0)
    glVertex3f(xL, yT, height)
    glVertex3f(xR, yT, height)
    glVertex3f(xR, yT, 0)

    # bottom wall
    glColor3f(0.1, 0.3, 0.9)
    glVertex3f(xL, yB, 0)
    glVertex3f(xL, yB, height)
    glVertex3f(xR, yB, height)
    glVertex3f(xR, yB, 0)

    glEnd()

def draw_fish_model(size=1.0, color=(1, 0.3, 0.0)):  
    glPushMatrix()

    glPushMatrix()
    glScalef(1.0*size, 3.0*size, 2.0*size)
    glTranslatef(0, 0, 20)
    glColor3f(color[0], color[1], color[2])
    gluSphere(gluNewQuadric(), 15, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glScalef(0.2*size, 1.0*size, 1.0*size)
    glTranslatef(0, 80, 0)
    glRotatef(90, 1, 0, 0)
    glRotatef(-45, 1, 0, 0)
    glColor3f(0.8, 0.8, 1.0)
    gluCylinder(gluNewQuadric(), 4, 16, 50, 10, 10)
    glTranslatef(0, 50, 50)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 16, 50, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glRotatef(150, 1, 0, 0)
    glTranslatef(0, 30, -80)
    gluCylinder(gluNewQuadric(), 0, 4, 18, 10, 10)
    glRotatef(-100, 1, 0, 0)
    glTranslatef(0, -60, -50)
    gluCylinder(gluNewQuadric(), 0, 4, 14, 10, 10)
    glPopMatrix()

    glPopMatrix()

def draw_npc_fish(x,y,z,angle,size=1.0,color=(0.9,0.9,0.2)):  
    glPushMatrix()
    glTranslatef(x,y,z)
    glRotatef(angle, 0, 0, 1)
    draw_fish_model(size=size, color=color)
    glPopMatrix()

def draw_small_fish(x,y,z,angle): 
    draw_npc_fish(x, y, z, angle, size=0.55, color=(0.2, 1.0, 0.6))

def draw_big_fish(x,y,z,angle):
    draw_npc_fish(x, y, z, angle, size=1.25, color=(0.7, 0.2, 1.0)) 

def draw_stone(x,y,z=0,scale=1.0,sink=0.35):  
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(scale, scale, scale)

    r = 18
    bury = max(0.0, min(sink, 0.95))*r 
    glTranslatef(0, 0, r-bury) 

    glColor3f(0.5, 0.5, 0.5)
    gluSphere(gluNewQuadric(), r, 10, 10)
    glPopMatrix()

def draw_plant(height, wave_offset):  
    seg = 8
    seg_height = height/seg

    for i in range(seg):
        glPushMatrix()
        wave_amount = (i / seg) * 10
        x_offset = math.sin(wave_offset + i * 0.5) * wave_amount
        glTranslatef(x_offset, 0, i * seg_height)
        green_intensity = 0.2 + (i /seg) * 0.4
        glColor3f(0.0, green_intensity, 0.1)
        gluCylinder(gluNewQuadric(), 2 - (i * 0.2), 1.5 - (i * 0.2), seg_height, 6, 1)
        glPopMatrix()

def draw_plant_at(x, y, z, scale, height, extra_offset):  
    glPushMatrix()
    glTranslatef(x, y, z)        
    glScalef(scale, scale, scale)
    draw_plant(height, plant_wave_offset + extra_offset)
    glPopMatrix()

def draw_fullscreen_red_blink():  
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1.0, 0.0, 0.0)  
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_npc_fish(x, y, z, angle, size=1.0, color=(0.9, 0.9, 0.2)):
    # Extra swim animation: slight bob + yaw wiggle.
    wobble = math.sin(anim_t * 0.12 + (x + y) * 0.002) * 6.0
    bob = math.sin(anim_t * 0.10 + (x - y) * 0.001) * 2.0

    glPushMatrix()
    glTranslatef(x, y, z + bob)
    glRotatef(angle + wobble, 0, 0, 1)
    draw_fish_model(size=size, color=color)
    glPopMatrix()


def draw_big_fish(x, y, z, angle):
    # Enemy fish in gray
    draw_npc_fish(x, y, z, angle, size=1.25, color=(0.55, 0.55, 0.55))



def draw_wave(var, direction):
    if wave==True:
        glPushMatrix()
        if direction=="l" or  direction=="r":
            glTranslatef(var, -750, 10)
            glRotatef(-90, 1,0, 0)
            
        elif direction=="t" or direction=="b":
            glTranslatef(-750,var, 10)
            glRotatef(90, 0, 1, 0)
        
        glColor3f(0.2,0.2, 1)
        gluCylinder(gluNewQuadric(), 30,30, 1500, 10, 10)  
        glPopMatrix()

def spawn_environment():  
    global stones, plants, small_fishes, big_fishes, enemy_event_timer, enemy_attacker_idx, enemy_attack_cooldown, enemy_peace_timer
    stones = []
    for i in range(30):  
        sx = random.randint(min_of_x + 60, max_of_x - 60)
        sy = random.randint(min_of_y + 60, max_of_y - 60)
        sc = random.uniform(0.7, 1.8)
        stones.append((sx, sy, 0, sc))

    plants = []
    for i in range(22):
        px = random.randint(min_of_x + 80, max_of_x - 80)
        py = random.randint(min_of_y + 80, max_of_y - 80)
        ps = random.uniform(0.7, 1.4)
        ph = random.uniform(0.0, 6.28)
        h = random.uniform(40, 80) 
        plants.append({"x": px, "y": py, "z": 0, "scale": ps, "wave": ph, "h": h})

    small_fishes = []
    for i in range(10):
        fx = random.randint(min_of_x + 80, max_of_x - 80)
        fy = random.randint(min_of_y + 80, max_of_y - 80)
        fa = random.randint(0, 359)
        fs = random.uniform(1.2, 2.2)
        small_fishes.append({"x": fx, "y": fy, "z": 35, "a": fa, "spd": fs})

    big_fishes = []
    for i in range(5):
        fx = random.randint(min_of_x + 100, max_of_x - 100)
        fy = random.randint(min_of_y + 100, max_of_y - 100)
        fa = random.randint(0, 359)
        fs = random.uniform(0.7, 1.3)
        big_fishes.append({"x": fx, "y": fy, "z": 45, "a": fa, "spd": fs})

    
    if len(big_fishes) > ENEMY_COUNT:
        big_fishes = big_fishes[:ENEMY_COUNT]
    enemy_event_timer = 0
    enemy_attacker_idx = None
    enemy_attack_cooldown = 0
    enemy_peace_timer = 0
    spawn_food_and_traps()


def update_fish_list(flist): 
    for f in flist:
        ang = math.radians(f["a"])
        dx = f["spd"] * math.sin(ang)
        dy = -f["spd"] * math.cos(ang)
        f["x"] += dx
        f["y"] += dy

        if f["x"] < min_of_x + 40 or f["x"] > max_of_x - 40 or f["y"] < min_of_y + 40 or f["y"] > max_of_y - 40:
            f["a"] = (f["a"] + 180 + random.randint(-30, 30)) % 360
            f["x"] = min(max(f["x"], min_of_x + 50), max_of_x - 50)
            f["y"] = min(max(f["y"], min_of_y + 50), max_of_y - 50)

def update_environment():  
    global plant_wave_offset,anim_t, damage_blink_timer
    plant_wave_offset += 0.03  
    update_fish_list(small_fishes)
    update_fish_list(big_fishes)
    
    anim_t += 1.0

    if damage_blink_timer > 0:
        damage_blink_timer -= 1

    # animate floating items
    for it in food_items:
        it["phase"] += 0.04
    for it in trap_items:
        it["phase"] += 0.04

    tick_dodge_timer()
    tick_enemy_peace_timer()
    try_collect_food_or_trap()
    enemy_ai_and_attack()

    # Keep a steady amount of food/traps available
    if len(food_items) < max(3, FOOD_COUNT // 2):
        spawn_food_and_traps()


def keyboardListener(key, x, y):
    global player_pos, player_angle,health, pov, exp,camera_pos, hunger_counter, slow_mode, blink_counter, blink_on, rear
    global bait_caught, caught_counter, escape_check, escape_chance, damage_blink_timer, player_size
    global enemy_event_timer, enemy_attacker_idx, enemy_attack_cooldown, enemy_peace_timer
    
    """
    Handles keyboard inputs for player movement, gun rotation, camera updates, and cheat mode toggles.
    """
    x1,y1,z1= player_pos
    theta=player_angle
    angle= math.radians(theta)
    x2=10*math.sin(angle)
    y2=-10*math.cos(angle)

    if slow_mode:  
        x2 *= MOVE_SLOW_FACTOR  
        y2 *= MOVE_SLOW_FACTOR  
    # Move forward (W key)
    if (key == b'w' or key == b'W') and health>0:
        if GRID_LENGTH*(6)>=y1+y2>=GRID_LENGTH*(-7) and GRID_LENGTH*(7)>=x1+x2>=GRID_LENGTH*(-6):
            y1+=y2
            x1+=x2

    # Move backward (S key)
    if (key == b's' or key == b'S') and health>0:
        if GRID_LENGTH*(-7)<=y1-y2<=GRID_LENGTH*(6) and GRID_LENGTH*(7)>=x1-x2>=GRID_LENGTH*(-6):    
            y1-=y2
            x1-=x2
    # Rotate gun left (A key)
    if (key == b'a' or key==b'A') and health>0:
        if x1+72<GRID_LENGTH*(7):
            theta+=2
    # Rotate gun right (D key)
    if (key == b'd' or key==b'D') and health>0:
        if x1-72>GRID_LENGTH*(-6):
            theta-=2
    player_angle=theta
    player_pos=(x1,y1,z1)
    #rear view
    if (key == b' ' or key==b' ') and health>0:
        if rear==True:
            rear= False
        else:
            rear=True
    # Reset the game if R key is pressed
    if key == b'r' or key==b'R':
        health=100
        exp=20
        pov=False
        camera_pos=(0,300,100)
        hunger_counter = 0      
        slow_mode = False       
        blink_on = False       
        blink_counter = 0 
        rear=False    
        spawn_environment()   
        bait_caught = False
        caught_counter = 0
        escape_check = False
        escape_chance = 0
        damage_blink_timer = 0
        player_size = 1.0
        enemy_event_timer = 0
        enemy_attacker_idx = None
        enemy_attack_cooldown = 0
        enemy_peace_timer = 0
        player_pos=(0,0,0)

    
    if key == b'c':
        do_dodge()

    # F: bite attack (eat smaller fish to grow)
    if key == b'f' or key == b'F':
        player_bite_attack()




def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle and height.
    """
    global camera_pos
    x, y, z = camera_pos
    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        if z+10<400:
            z+=10
    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        if z-10>50:
            z-=10
    camera_pos = (x, y, z)


def mouseListener(button, state, x, y):
    global pov, player_pos, player_angle
    
    """
    Handles mouse inputs for firing bullets (left click) and toggling camera mode (right click).
    """
        # Left mouse button fires a bullet
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        x1,y1,z1= player_pos
        # Right mouse button toggles camera tracking mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if pov==False:
            pov=True
        else:
            pov=False


def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    global pov, player_pos, player_angle,rear, bait_caught
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    if pov==False:
        gluPerspective(fovY, 1.25, 0.1, 2400) # Think why aspect ration is 1.25?
    else: 
        gluPerspective(120, 1.25,0.1,2000)
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    # Extract camera position and look-at target
    x, y, z = camera_pos
    x1,y1,z1= player_pos
    #finding target for pov
    angle = math.radians(player_angle)
    x2 = x1 + 100 * math.sin(angle)
    y2 = y1 - 100 * math.cos(angle)
    z2 = z1 + 140
    #editing camera position based on player
    xc= x1 - 100 * math.sin(angle)
    yc = y1 + 100 * math.cos(angle)
    
    # Position the camera and set its orientation 
    if bait_caught==False:
        if pov==False and rear==False:
            gluLookAt(xc, yc, z,
                    x1,y1,z1, 
                    0, 0, 1)  
        elif pov==False and rear ==True:
            gluLookAt(x1,y1,z, 
                    xc, yc, z1,
                    0, 0, 1)  
        elif pov==True:
            gluLookAt(x1, y1, z1+80, 
            x2,y2,z2,  # Look-at target
            0, 0, 1) 
    else:
        if pov==False and rear==False:
            gluLookAt(x1, y1-100, z+100,
                    x1,y1,z1, 
                    0, 0, 1)  
        elif pov==False and rear ==True:
            gluLookAt(x1,y1,z, 
                    x, y, z1,
                    0, 0, 1)  
        elif pov==True:
            gluLookAt(x1, y1, z1+80, 
            x2,y2,z2,  # Look-at target
            0, 0, 1) 
     

def idle():
    """
    Idle function that runs continuously:
    - Triggers screen redraw for real-time updates.
    """
    global player_pos, health, player_angle,exp,pov, food,counter, wave_from, wave,var,wave_colli, bait_caught, caught_counter,escape_check, escape_chance ,hunger_counter, slow_mode, blink_counter, blink_on, hpdecrease
    player_angle = player_angle % 360
    if health <= 0 or exp <= 0:
        bait_caught = False
        caught_counter = 0
        escape_check = False
        escape_chance = 0
    if exp<1:
        health=0
    if health<1:
        exp=0
    hunger_counter += 1  
    #health and exp logic
    """With each food intake health increases by 20. If health value exceeds 100 the rest goes to the exp"""
    if food==True:
        hunger_counter = 0 
        if health+20<=100:
            health+=20
        else:
            exp+=(health+20-100)
            health=100
        food=False
        
    if hunger_counter >= HUNGER_LIMIT:
        hpdecrease+=1
        if hpdecrease>200:
            hpdecrease=0
            health-=5
        slow_mode = True
        blink_counter = (blink_counter + 1) % (2 * BLINK_PERIOD_FRAMES)
        blink_on = blink_counter < BLINK_PERIOD_FRAMES
    else:
        slow_mode = False
        blink_on = False
        blink_counter = 0
        hpdecrease=0

    update_environment()  
    
    #wave logic===========================================================
    if wave==False:
        counter+=0.5
        if counter>=1000:
            wave=True
            wave_colli=False
            counter=0
            wave_from= random.choice(['l','r','t','b'])
            if wave_from=="l":
                var=GRID_LENGTH*(7)
            elif wave_from=="r":    
                var=GRID_LENGTH*(-6)
            elif wave_from=="t":
                var=GRID_LENGTH*(-7)
            elif wave_from=="b":
                var=GRID_LENGTH*(6)
    else:
        if wave_from=="l" or wave_from=="b":
            var-=1
            if var<-750:
                wave=False
        else:
            var+=1
            if var>750:
                wave=False
        xp,yp,zp=player_pos
        if wave_colli==False:
            if wave_from=="l" or wave_from== "r":
                if abs(var-xp) <20:
                    wave_colli=True
                    if wave_from=="l":
                        xp-=50
                    else:
                        xp+=50
            elif wave_from=="t" or wave_from=="b":
                if abs(var-yp)< 20:
                    wave_colli=True
                    if wave_from=="t":
                        yp +=50
                    else:
                        yp -=50

        player_pos=(xp,yp, zp)
    # bait caught=====================================================
    if bait_caught:
        caught_counter += 1

        # struggle animation (always happens)
        if (caught_counter // 200) % 20 == 0:
            player_angle += 30
        elif (caught_counter // 200) % 30 == 0:
            player_angle -= 30

        # decide fate once, after struggle duration
        if not escape_check and caught_counter >= 200:
            escape_check = True
            escape_chance = random.choice([0, 1])  # 50% chance

        # resolve outcome after struggle continues a bit more
        if escape_check and caught_counter >= 260:
            if escape_chance == 0:
                health = 0
                exp = 0
            bait_caught = False
            caught_counter = 0
            escape_check = False
            escape_chance = 0

    glutPostRedisplay()


def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
    global player_angle, player_angle, bait_caught, caught_counter, escape_check, escape_chance
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()  # Configure camera perspective

    # Draw a random points
    glPointSize(20)
    glBegin(GL_POINTS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glEnd()

    # Draw the grid (game floor)
    glBegin(GL_QUADS)
    blue=True
    startx= GRID_LENGTH*(-6)
    starty= GRID_LENGTH*(-7)
    for i in range(1,14):
        for j in range(1,14):
            if blue==True:
                glColor3f(0,0, 1)
                blue=False
            else:
                glColor3f(0,0,0.5)
                blue=True
                
            glVertex3f(startx,starty, 0)
            glVertex3f(startx+GRID_LENGTH, starty, 0)
            glVertex3f(startx+GRID_LENGTH, starty+GRID_LENGTH, 0)
            glVertex3f(startx, starty+GRID_LENGTH, 0)
            
            startx+=GRID_LENGTH
        startx=GRID_LENGTH*(-6)
        starty+=GRID_LENGTH
    glEnd()
    
    draw_borders(125)
    
    for sx, sy, sz, sc in stones:
        draw_stone(sx, sy, sz, sc)

    for p in plants:
        draw_plant_at(p["x"], p["y"], p["z"], p["scale"], p["h"], p["wave"])  

    # Food and traps (floating bait)
    for it in food_items:
        draw_food_item(it)
    for it in trap_items:
        draw_trap_item(it)

    for f in small_fishes:
        draw_small_fish(f["x"], f["y"], f["z"], f["a"])
    for f in big_fishes:
        draw_big_fish(f["x"], f["y"], f["z"], f["a"])

    # Display game info text at a fixed screen position
    if health==0 or exp==0:
        draw_text(10, 770, "Game is Over.")
        draw_text(10, 740, 'Press "R" RESTART the Game')
    else:    
        draw_text(10, 770, f"Health: {health}")
        draw_text(10, 740, f"Exp: {exp}")
        
        if slow_mode:
            draw_text(10, 710, "HUNGRY! Find food fast!")
            
    x,y,z=player_pos
    _saved_angle = player_angle
    wiggle = math.sin(anim_t * 0.12) * 3.0
    player_angle = _saved_angle + wiggle
    draw_player(x, y, z + math.sin(anim_t * 0.10) * 2.5, size=player_size)
    player_angle = _saved_angle

    if blink_on and health > 0 and exp > 0:
        draw_fullscreen_red_blink()

    if wave:
        draw_wave(var, wave_from)
    if damage_blink_timer > 0 and ((damage_blink_timer % 12) < 2):
        draw_fullscreen_red_blink()

# Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()



# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"Ocean Hunger")  # Create the window

    spawn_environment() 
    
    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()

