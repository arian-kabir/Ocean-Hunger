from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
# Camera-related variables
camera_pos = (0,700,700)
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

def keyboardListener(key, x, y):
    global player_pos, player_angle,health, pov, exp,camera_pos
    """
    Handles keyboard inputs for player movement, gun rotation, camera updates, and cheat mode toggles.
    """
    x1,y1,z1= player_pos
    theta=player_angle
    angle= math.radians(theta)
    x2=5*math.sin(angle)
    y2=-5*math.cos(angle)
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
        camera_pos=(0,700,700)
        
def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle and height.
    """
    global camera_pos
    x, y, z = camera_pos
    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        if z+10<900:
            z+=10
    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        if z-10>0:
            z-=10
    # moving camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        if x<GRID_LENGTH*(8) and y==700:
            x+=20
        elif x==GRID_LENGTH*(8) and y>-700:
            y-=20
        elif x>-GRID_LENGTH*(8) and y==-700:
            x-=20
        elif x==-GRID_LENGTH*(8) and y<700:
            y+=20

    # moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        if x>-GRID_LENGTH*(8) and y==700:
            x-=20
        elif x==-GRID_LENGTH*(8) and y>-700:
            y-=20
        elif x<GRID_LENGTH*(8) and y==-700:
            x+=20
        elif x==GRID_LENGTH*(8) and y<700:
            y+=20
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
    # Position the camera and set its orientation 
    if pov==False:
        gluLookAt(x, y, z,  # Camera position
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
    global player_pos, health, player_angle,exp,pov, food,counter, wave_from, wave,var,wave_colli, bait_caught, caught_counter,escape_check, escape_chance
    if exp<1:
        health=0
    if health<1:
        exp=0
        
    #health and exp logic
    """With each food intake health increases by 20. If health value exceeds 100 the rest goes to the exp"""
    if food==True:
        if health+20<=100:
            health+=20
        else:
            exp+=(health+20-100)
            health=100
        food=False
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
        if abs(var-xp)<10 and wave_colli==False:
            wave_colli=True
            if wave_from=="l":
                xp-=50
            elif wave_from=="r":
                xp+=50
        elif abs(var-yp)<10 and wave_colli==False:
            wave_colli=True
            if wave_from=="t":
                yp+=50
            elif wave_from=="b":
                yp-=50
        player_pos=(xp,yp,zp)
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
    # Display game info text at a fixed screen position
    if health==0 or exp==0:
        draw_text(10, 770, "Game is Over.")
        draw_text(10, 740, 'Press "R" RESTART the Game')
    else:    
        draw_text(10, 770, f"Health: {health}")
        draw_text(10, 740, f"Exp: {exp}")
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
