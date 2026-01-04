This is a small university project with a lot of constraints and limitation.
Ocean Hunger is an interactive 3D survival game built using Python and OpenGL. 
The player has to navigate an underwater grid as a fish, surviving environmental hazards like oceanic waves and avoiding lethal bait traps.


FeaturesDynamic 3D Environment:
A grid representing the ocean floor with a custom-built 3D player model.
Dual Camera Modes: Switch between a Third-Person View for better awareness and a POV (Point of View) mode for immersive gameplay.
Environmental Hazards: Randomly spawning tidal waves that sweep across the grid, damaging and pushing the player.
Bait Traps: A "Struggle" mechanic where the player can get caught, jittering uncontrollably with a 25% chance of escape—otherwise, it's Game Over.
Progressive Stats: Manage your Health and Exp.
Use the "R" key to recover if you fall in battle.

Controls:
Movement & Actions
Key                    Action
W/S           Move Forward / Backward
A/D           Rotate Player Left/Right
R             Restart Game (when Game Over)
spacebar      View rear
Right ClickToggle POV / Third-Person 
ViewCamera ControlKeyActionArrow Up / DownAdjust 


The Wave System
Waves spawn from one of four directions (Left, Right, Top, Bottom). They are rendered as semi-transparent blue cylinders.
Collision: If the player's coordinates overlap with the wave's var position, the player is pushed back 60 units and loses 10 Health.2.
Bait & StruggleEvery 1000 frames, a trap triggers.Struggle Phase: The player's model jitters to simulate a struggle.
Outcome: After a set period, the game rolls a random chance. A "1" results in death, while any other number allows the player to break free and continue.

Hunger
After a set period of not consuming food the player struggles and slows down and eventually dies. 

Food Consumption
This allows the player to survive and continue the game. The food intake also allows the player's experience in envolve causing the player to level up.

Installation & SetupPrerequisites:
Python 3.xPyOpenGLPyOpenGL_accelerate (Optional, for better performance)
Install Dependencies:Bashpip install PyOpenGL PyOpenGL_accelerate
Run the Game:Bashpython project.py

Technical DetailsGraphics Pipeline: Fixed-function pipeline using glPushMatrix and glPopMatrix for hierarchical modeling.
Projections: Uses gluPerspective for the 3D world and gluOrtho2D for the 2D UI overlay (Health/Exp).
