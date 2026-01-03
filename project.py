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
BLINK_PERIOD_FRAMES = 120 


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
    global stones, plants, small_fishes, big_fishes
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
    global plant_wave_offset
    plant_wave_offset += 0.03  
    update_fish_list(small_fishes)
    update_fish_list(big_fishes)

def keyboardListener(key, x, y):
    global player_pos, player_angle,health, pov, exp,camera_pos, hunger_counter, slow_mode, blink_counter, blink_on
    
    """
    Handles keyboard inputs for player movement, gun rotation, camera updates, and cheat mode toggles.
    """
    x1,y1,z1= player_pos
    theta=player_angle
    angle= math.radians(theta)
    x2=5*math.sin(angle)
    y2=-5*math.cos(angle)

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
    if (key == b'a') and health>0:
        if x1+72<GRID_LENGTH*(7):
            theta+=2
    # Rotate gun right (D key)
    if (key == b'd') and health>0:
        if x1-72>GRID_LENGTH*(-6):
            theta-=2
    player_angle=theta
    player_pos=(x1,y1,z1)
        
    # Reset the game if R key is pressed
    if key == b'r':
        health=100
        exp=20
        pov=False
        camera_pos=(0,300,100)
        hunger_counter = 0      
        slow_mode = False       
        blink_on = False       
        blink_counter = 0     
        spawn_environment()     

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
    # # moving camera left (LEFT arrow key)
    # if key == GLUT_KEY_LEFT:
    #     if x<300 and y==300:
    #         x+=20
    #     elif x==300 and y>-300:
    #         y-=20
    #     elif x>-300 and y==-300:
    #         x-=20
    #     elif x==-300 and y<300:
    #         y+=20

    # # moving camera right (RIGHT arrow key)
    # if key == GLUT_KEY_RIGHT:
    #     if x>-300 and y==300:
    #         x-=20
    #     elif x==-300 and y>-300:
    #         y-=20
    #     elif x<300 and y==-300:
    #         x+=20
    #     elif x==300 and y<300:
    #         y+=20
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
    global pov, player_pos, player_angle
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
    if pov==False:
        gluLookAt(xc, yc, z,  # Camera position
                x1,y1,z1,  # Look-at target
                0, 0, 1)  # Up vector (z-axis)
    else:
        gluLookAt(x1, y1, z1+80, 
        x2,y2,z2,  # Look-at target
        0, 0, 1)  

def idle():
    """
    Idle function that runs continuously:
    - Triggers screen redraw for real-time updates.
    """
    global player_pos, health, player_angle,exp,pov, food,counter, wave_from, wave,var,wave_colli, bait_caught, caught_counter,escape_check, escape_chance ,hunger_counter, slow_mode, blink_counter, blink_on 
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
        slow_mode = True
        blink_counter = (blink_counter + 1) % (2 * BLINK_PERIOD_FRAMES)
        blink_on = blink_counter < BLINK_PERIOD_FRAMES
    else:
        slow_mode = False
        blink_on = False
        blink_counter = 0

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
    #bait caught=====================================================
        # bait_caught=True
        # caught_counter=0
        # escape_check= False
    if bait_caught==True:
        caught_counter= (caught_counter+1)%2400
        if (caught_counter//300)%2==0:
            player_angle+=30
        else:
            player_angle-=30

        if escape_check==False and caught_counter>=2000:
            escape_chance= random.choice([1,2,3,4])
            escape_check=True
            if escape_chance==1:
                health=0
            else:
                bait_caught=False
                escape_check=False
                caught_counter=0
    glutPostRedisplay()

def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
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
    #bullet
    # for i in bullet:
    #     draw_bullet(i[0],i[1], i[2])
    # if health>0 or missed<10:
    #     draw_enemy(li1)

    draw_player(x,y,z)
    if wave:
        draw_wave(var, wave_from)
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

    
    
    #====================================================================================================
    #     bullet=[]
    # if radius >= 50:
    #     decrease = True
    # elif radius <= 25:
    #     decrease = False

    # if decrease:
    #     radius -= 0.05
    # else:
    #     radius += 0.05
    #enemy movement===================================================
    # x1,y1,z1=player_pos
    # for k in range(5):
    #     if health>0 or missed>=10:
    #         i,j= li1[k][0], li1[k][1]
    #         if i<x1:
    #             i+=enemyspeed
    #         elif i>x1:
    #             i-=enemyspeed
    #         if j<y1:
    #             j+=enemyspeed
    #         elif j>y1:
    #             j-=enemyspeed
    #         if abs(i-x1)<40 and abs(j-y1)<40:
    #             health-=1
    #             print("Remaining Player health:", health)
    #             i=random.randint(GRID_LENGTH*(-6)+25,GRID_LENGTH*(7)-25)
    #             j=random.randint(GRID_LENGTH*(-7)+25,GRID_LENGTH*(6)-25)
            
    #         li1[k][0], li1[k][1]=i,j
    #bullet================================================================
#     new_bullets = []
#     for i in bullet:
#         xb, yb, zb, bangle = i
#         angle = math.radians(bangle)
#         xb +=2 * math.sin(angle)
#         yb -=2 * math.cos(angle)
#         hit=False
#         for i in range(len(li1)):
#             diff= math.sqrt((xb - li1[i][0])**2 + (yb - li1[i][1])**2)
#             ang= math.degrees(math.atan2((li1[i][0]-x1),-(li1[i][1]-y1)))
#             if diff <= radius+8:
#                 exp += 1
#                 li1[i][0] = random.randint(GRID_LENGTH*(-6)+25, GRID_LENGTH*(7)-25)
#                 li1[i][1] = random.randint(GRID_LENGTH*(-7)+25, GRID_LENGTH*(6)-25)
#                 hit=True
#                 fired[i]=False
#                 continue

#         if hit==False:
#             if GRID_LENGTH*(-6) <= xb <= GRID_LENGTH*(7) and GRID_LENGTH*(-7) <= yb <= GRID_LENGTH*(6):
#                 new_bullets.append([xb, yb, zb, bangle])
#             else:
#                 missed+=1
#                 if missed>=10:
#                     health=0
#                     cheat=pov=auto=False
#                 else:    
#                     print("Missed Bullet:", missed)
        
#     bullet = new_bullets         
# #cheat===================================================================================
#     if cheat==True:
#         if cooldown==0:
#             player_angle+=2
#         if player_angle>360:
#             player_angle-=360
#         xc,yc,zc=player_pos
#         if cooldown > 0:
#             cooldown -= 1


#         for i in range(len(li1)):
#             ang= math.degrees(math.atan2((li1[i][0]-xc),-(li1[i][1]-yc)))
#             if fired[i]==True:
#                 continue
#             if ang<0:
#                 ang+=360
#             if abs(player_angle-ang)<2 and cooldown==0:
#                 bullet.append([xc,yc,125, player_angle])
#                 cooldown=15
#                 fired[i]=True
#                 break
#borders
# glColor3f(0, 0, 1)
    # glVertex3f(GRID_LENGTH*(-6), GRID_LENGTH*(-7), 0)
    # glVertex3f(GRID_LENGTH*(-6), GRID_LENGTH*(-7), 125)
    # glVertex3f(GRID_LENGTH*(7), GRID_LENGTH*(-7), 125)
    # glVertex3f(GRID_LENGTH*(7), GRID_LENGTH*(-7), 0)
    # glColor3f(130/255, 200/255, 229/255)
    # glVertex3f(GRID_LENGTH*(-6), GRID_LENGTH*(6), 0)
    # glVertex3f(GRID_LENGTH*(-6), GRID_LENGTH*(6), 125)
    # glVertex3f(GRID_LENGTH*(7), GRID_LENGTH*(6), 125)
    # glVertex3f(GRID_LENGTH*(7), GRID_LENGTH*(6), 0)
    # glColor3f(0, 1, 0)
    # glVertex3f(GRID_LENGTH*(-6), GRID_LENGTH*(-7), 0)
    # glVertex3f(GRID_LENGTH*(-6), GRID_LENGTH*(-7), 125)
    # glVertex3f(GRID_LENGTH*(-6), GRID_LENGTH*(6), 125)
    # glVertex3f(GRID_LENGTH*(-6), GRID_LENGTH*(6), 0)
    # glColor3f(68/255, 212/255, 59/255)
    # glVertex3f(GRID_LENGTH*(7), GRID_LENGTH*(-7), 0)
    # glVertex3f(GRID_LENGTH*(7), GRID_LENGTH*(-7), 125)
    # glVertex3f(GRID_LENGTH*(7), GRID_LENGTH*(6), 125)
    # glVertex3f(GRID_LENGTH*(7), GRID_LENGTH*(6), 0)
    # glEnd()




