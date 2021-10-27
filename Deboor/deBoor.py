"""
/*******************************************************************************
 *
 *            #, #,         CCCCCC  VV    VV MM      MM RRRRRRR
 *           %  %(  #%%#   CC    CC VV    VV MMM    MMM RR    RR
 *           %    %## #    CC        V    V  MM M  M MM RR    RR
 *            ,%      %    CC        VV  VV  MM  MM  MM RRRRRR
 *            (%      %,   CC    CC   VVVV   MM      MM RR   RR
 *              #%    %*    CCCCCC     VV    MM      MM RR    RR
 *             .%    %/
 *                (%.      Computer Vision & Mixed Reality Group
 *
 ******************************************************************************/
/**          @copyright:   Hochschule RheinMain,
 *                         University of Applied Sciences
 *              @author:   Prof. Dr. Ulrich Schwanecke
 *             @version:   0.9
 *                @date:   23.05.2020
 ******************************************************************************/
/**         bezierTemplate.py
 *
 *          Simple Python OpenGL program that uses PyOpenGL + GLFW to get an
 *          OpenGL 3.2 context and display a Bezier curve.
 ****
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np

gewichtungHoch = False
startPoint = 0
angefassterPunktIndex = 0

class Scene:
    """ OpenGL 2D scene class """
    # initialization
    def __init__(self, width, height, 
                scenetitle="Bezier Curve Template"):
        self.scenetitle = scenetitle
        self.pointsize = 7
        self.linewidth = 5
        self.width = width
        self.height = height
        self.points = []
        self.lines = []
        self.knots = []
        self.controlpoints = []
        self.gewichtung = []
        self.splines = []
        # hier einfach mal 4 wählen, sollte laut konsti passen
        self.k = 4
        self.anzahlFaktor = 10


    # set scene dependent OpenGL states
    def setOpenGLStates(self):
        glPointSize(self.pointsize)
        glLineWidth(self.linewidth)
        glEnable(GL_POINT_SMOOTH)


    # render 
    def render(self):
        global gewichtungHoch

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # set foreground color to black
        glColor(0.0, 0.0, 0.0)
        #glBegin(GL_LINE)

        # Control polygon, hoffentlich ist das wie oben -> PASST
        glBegin(GL_LINE_STRIP)
        for i in range(len(self.controlpoints)):
            glVertex2f(self.controlpoints[i][0], self.controlpoints[i][1])
        glEnd()  

        # Punkte können wir noch anzeigen lassen
        glBegin(GL_POINTS)
        for p in self.controlpoints:
            glVertex2f(p[0], p[1])
        glEnd()   

        # Spline polygon noch rendern
        glColor(0,0.4,0.6)
        glBegin(GL_LINE_STRIP)
        for i in range(len(self.splines)):
            # Perspektivische division
            self.splines[i][0] /= self.splines[i][2]
            self.splines[i][1] /= self.splines[i][2]
            glVertex2f(self.splines[i][0], self.splines[i][1])
        glEnd()  

        
        glColor(0,0.6,0.4)
        glBegin(GL_POINTS)
        for i in range(len(self.splines)):
            glVertex2f(self.splines[i][0], self.splines[i][1])
        glEnd()  

        #muss neu berechnet werden, sodass wir die WErte angepasst einbringen können
        self.calcSpline()            

                
    # punkt hinzu
    def add_point(self, p):
        self.calcSpline(p)

    # clear polygon
    def clear(self):
        self.controlpoints = []
        self.gewichtung = []
        self.knots = []
        self.splines = []


    # bezier nicht mehr nötig, trotzdem danke konsti
    '''def determine_points_on_bezier_curve(self):
        self.points_on_bezier_curve = []
        t = 0
        while t <= 1:
            p = self.casteljau(t, self.points)
            t += 0.05
            self.points_on_bezier_curve.append(p)'''

            
    def calcSpline(self, p = None):
        global M
        if p is not None:
            self.controlpoints.append(p)
            self.gewichtung.append(1)
            print(len(self.gewichtung))
        # erst knoten berechnen 
        self.knotenBerechnen()
        self.splines = []
        t = 0
        #laut tut
        while t < self.knots[-1]:
            # R fuer deboor finden, folie 293
            r = self.findRForDeboor(t)
            # Deboor ausführen
            b = self.deBoor(self.controlpoints, self.knots, t, self.k - 1, r)
            self.splines.append(b)
            # So sollten wir die anzahl beeinflussen koennen
            t += 1 / float(self.anzahlFaktor)

    def findRForDeboor(self, t):
        #Folie 293, t teil aus [tr, tr+1] finden und zum deboor mitgeben
        for i in range(len(self.knots) - 1):
            if self.knots[i] > t:
                return i - 1

    def knotenBerechnen(self):
        #Knotenvektor berechnen
        #anzahl füllen
        self.knots = [0] * self.k
        #knotenpunkte -> Siehe arbeitsblatt
        for n in range(1, len(self.controlpoints) -1 - (self.k - 2)):
            self.knots.append(n)
        #Siehe arbeitsblatt
        for n in range(self.k):
            self.knots.append(len(self.controlpoints) - (self.k - 1))

    #Rekursion wie bei casteljau
    def deBoor(self, controlPoints, knot, t, recursion, i):
        # alpha = (x - t[j + k - p]) / (t[j + 1 + k - r] - t[j + k - p]) d[j] = 
        # (1.0 - alpha) * d[j - 1] + alpha * d[j]
        # deboor geht jetzt, aber gewichtung will einfach nicht - 09:40, 
        # Nach dem tut: ES GEHT
        if recursion == 0:
            # print(controlPoints[i])
            # print(controlPoints[i]) * self.gewichtung[i]
            return controlPoints[i] * self.gewichtung[i]
        #der Algorithmus selber
        alpha = (t - knot[i]) / (knot[i - recursion + self.k] - knot[i])
        b = ((1 - alpha) * self.deBoor(controlPoints, knot, t, recursion - 1, i - 1) 
            + alpha * self.deBoor(controlPoints, knot, t, recursion - 1, i))
        return b

class RenderWindow:
    """GLFW Rendering window class"""
    def __init__(self, scene):
        
        # save current working directory
        cwd = os.getcwd()
        
        # Initialize the library
        if not glfw.init():
            return
        
        # restore cwd
        os.chdir(cwd)
        
        # version hints
        #glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        #glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        #glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
        #glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        
        # buffer hints
        glfw.window_hint(glfw.DEPTH_BITS, 32)

        # define desired frame rate
        self.frame_rate = 100
        # make a window
        self.width, self.height = scene.width, scene.height
        self.aspect = self.width/float(self.height)
        self.window = glfw.create_window(self.width, self.height, scene.scenetitle, None, None)
        if not self.window:
            glfw.terminate()
            return
        # Make the window's context current
        glfw.make_context_current(self.window)
        # initialize GL

        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)

        glOrtho(0, self.width, self.height, 0,  -1, 1)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        glLoadIdentity()

        glMatrixMode(GL_MODELVIEW)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_window_size_callback(self.window, self.onSize)
        glfw.set_cursor_pos_callback(self.window, self.mousemoved)
        
        # create scene
        self.scene = scene #Scene(self.width, self.height)
        self.scene.setOpenGLStates()
        
        # exit flag
        self.exitNow = False
    
    def mousemoved(self, window, x, y):
        global gewichtungHoch, angefassterPunktIndex, startPoint
        if gewichtungHoch == True:
            if startPoint < y and self.scene.gewichtung[angefassterPunktIndex]-0.5 >= 1:
                self.scene.gewichtung[angefassterPunktIndex] -= 0.5 
            elif startPoint > y and self.scene.gewichtung[angefassterPunktIndex]+0.5 <= 10:
                self.scene.gewichtung[angefassterPunktIndex] += 0.5
            print(self.scene.gewichtung[angefassterPunktIndex])

    def onMouseButton(self, win, button, action, mods):
        global gewichtungHoch, startPoint, angefassterPunktIndex
        if button == glfw.MOUSE_BUTTON_LEFT:
            if mods == glfw.MOD_SHIFT:
                if action == glfw.PRESS:
                    x, y = glfw.get_cursor_pos(win)
                    startPoint = y
                    for point in self.scene.points:
                        #Bereich von +-50 pixeln in dem man clicken kann für nen punkt
                        if point[0] - 30 < x < point[0] + 30 and point[1] - 30 < y < point[1] + 30:
                            for i in range(len(self.scene.controlpoints)):
                                # Zum punkte in nem bereich finden
                                if (((x - self.scene.width/2) / (self.scene.width/2) - 0.05 < self.scene.controlpoints[i][0] < (x - self.scene.width/2) / (self.scene.width/2) + 0.05) and
                                    (1 - (y / (self.scene.height/2)) - 0.05 < self.scene.controlpoints[i][1] < 1 - (y / (self.scene.height/2)) + 0.05)):
                                        # Index speichern um zu wissen welchen punkt wir gewichten wollen
                                        angefassterPunktIndex = i
                                        gewichtungHoch = True
                                        #print(x, y)
                                        #print(self.scene.gewichtung[angefassterPunktIndex])
                                        break
                elif action == glfw.RELEASE:
                    gewichtungHoch = False
            else:
                if action == glfw.PRESS:    
                    p = np.array(glfw.get_cursor_pos(win))
                    # Punkt noch in allgemeines array appenden
                    self.scene.points.append((p[0], p[1]))
                    # Auf fenster anpassen vergessen, goodbye 2.5 stunden zeit
                    p[0] = (p[0] - self.scene.width/2) / (self.scene.width/2) 
                    p[1] = 1 - (p[1] / (self.scene.height/2))
                    pointToCheck = np.array([p[0], p[1], 1])
                    self.scene.add_point(pointToCheck)            

    def onKeyboard(self, win, key, scancode, action, mods):
        if action == glfw.PRESS:
            #Ordnung
            if key == glfw.KEY_K:
                if mods == glfw.MOD_SHIFT:
                    # Das funktioniert jetzt
                    if self.scene.k < len(self.scene.controlpoints):
                        self.scene.k += 1
                else:
                    # siehe oben, aber andersrum 
                    if self.scene.k-1 > 2:
                        self.scene.k -= 1
                    else:
                        self.scene.k = 2
            #anzahl an punkten noch implementieren
            if key == glfw.KEY_M:
                if mods == glfw.MOD_SHIFT:
                    self.scene.anzahlFaktor += 10
                else:
                    #mindestanzahl einfahc mal 5 oder so
                    if self.scene.anzahlFaktor-10 < 10:
                        self.scene.anzahlFaktor = 10
                    else:
                        self.scene.anzahlFaktor -= 10
            # Szene säubern
            if key == glfw.KEY_C:
                self.scene.clear()


    def onSize(self, win, width, height):
        self.width = width
        self.height = height
        self.aspect = width/float(height)
        glViewport(0, 0, self.width, self.height)
    

    def run(self):
        # initializer timer
        glfw.set_time(0.0)
        t = 0.0
        while not glfw.window_should_close(self.window) and not self.exitNow:
            # update every x seconds
            currT = glfw.get_time()
            if currT - t > 1.0/self.frame_rate:
                # update time
                t = currT
                # clear viewport
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                # render scene
                self.scene.render()
                # swap front and back buffer
                glfw.swap_buffers(self.window)
                # Poll for and process events
                glfw.poll_events()
        # end
        glfw.terminate()

# call main
if __name__ == '__main__':
    print("deBoor.py")
    print("pressing 'C' should clear the everything")

    # set size of render viewport
    width, height = 640, 480

    # instantiate a scene
    scene = Scene(width, height, "Bezier Curve Template")

    rw = RenderWindow(scene)
    rw.run()