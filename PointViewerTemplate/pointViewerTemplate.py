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
 *                @date:   03.06.2019
 ******************************************************************************/
/**         RenderWindow.py
 *
 *          Simple Python OpenGL program that uses PyOpenGL + GLFW to get an
 *          OpenGL 3.2 context and display some 2D animation.
 ****
"""

from sys import argv
from OpenGL.arrays import vbo
from OpenGL.GL import shaders, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import math

tMat = np.eye(4)
sMat = np.eye(4)
rMat = np.eye(4)

myVBO = None

# Scale
doScaleButton = False
startPoint = 0

# Perspective
ortho = True

# Rotation
doRotation = False
actOri = np.identity(4)
angle = 0
axis = np.array([0,1,0])
start_p = np.array([0, 0, 0])

# Move
doMove = False
horizontalMove = 0
verticalMove = 0
horAndVerMove = np.array([0,0,0])

# Shadows
l = np.array([4000, 4000, 4000])
hatSchatten = False


# set size of render viewport
width, height = 640, 480

class Scene:
    """ OpenGL 2D scene class """
    # initialization
    def __init__(self, width, height, vertexShader, fragmentShader,
                points=[np.array([0, 0, 0, 1])],   
                scenetitle="2D Scene"):
        # time
        self.t = 0
        self.dt = 0.001
        self.scenetitle = scenetitle
        self.pointsize = 7
        self.linewidth = 3
        self.vertexShader = vertexShader
        self.fragmentShader = fragmentShader
        self.color = (0.9,0.9,0.9) 
        self.width = width
        self.height = height
        self.points = points
        self.animate = False
        self.alpha = 0 # rotation angle around x-axis
        self.beta = 0  # rotation angle around y-axis
        self.gamma = 0 # rotation angle around z-axis
        self.boundingBox = [np.array(list(map(min, list(zip(*points))))), np.array(list(map(max, list(zip(*points)))))]
        self.center = (self.boundingBox[0] + self.boundingBox[1]) /2
        self.scale =  2/max(self.boundingBox[1]-self.boundingBox[0])
        self.shader = None
        
    # set scene dependent OpenGL states
    def setOpenGLStates(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)   
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)

    # animation
    def animation(self):
        if self.animate: 
            self.beta += 10
            if self.beta > 360:
                self.beta = 0        


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
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        if self.width <= self.height:
            glOrtho( -1, 1, -1 * self.height / self.width, 1*self.height/self.width, -10, 10) 
        else:
            glOrtho( -1* self.width / self.height, 1, -1 , 1* self.width / self.height, -10, 10) 
        glMatrixMode(GL_MODELVIEW)
        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_cursor_pos_callback(self.window, self.mousemoved)
        glfw.set_scroll_callback(self.window, self.scrollPls)
        glfw.set_window_size_callback(self.window, self.onSize)
        # create scene
        self.scene = scene #Scene(self.width, self.height)
        self.scene.setOpenGLStates()
        self.lightPos = np.array([150, 150, 0])
        self.cameraPos = np.array([0, 200, -300])

        self.exitNow = False
        # animation flags
        self.forward_animation = False
        self.backward_animation = False

    def scrollPls(self, action, x, y):
        if y > 0 :
            self.scene.scale *= 1.15
        if y < 0 :
            self.scene.scale /= 1.15

    def onMouseButton(self, win, button, action, mods):
        global startP, actOri, angle, doRotation, doMove, horizontalMove, verticalMove, horAndVerMove, doScaleButton, startPoint
        if button == glfw.MOUSE_BUTTON_LEFT:
            x, y = glfw.get_cursor_pos(win)
            r = min(self.width,self.height)/2.0
            if action == glfw.PRESS:
                startP = self.projectOnSphere(x,y,r)
                doRotation = True
            if action == glfw.RELEASE:
                doRotation = False
                actOri = np.dot(actOri, self.rotate(angle,axis))
                angle = 0
        if button == glfw.MOUSE_BUTTON_RIGHT:
            x, y = glfw.get_cursor_pos(win)
            if action == glfw.PRESS:
                horAndVerMove = np.array([(x/self.width)-horizontalMove,(1-y/self.height)-verticalMove, 0])
                doMove = True
            if action == glfw.RELEASE:
                doMove = False
        if button == glfw.MOUSE_BUTTON_MIDDLE:
            x, y = glfw.get_cursor_pos(win)
            startPoint = x
            if action == glfw.PRESS:
                doScaleButton = True
            if action == glfw.RELEASE:
                doScaleButton = False

    def objectMoved(self, x, y):
        global horAndVerMove, horizontalMove, verticalMove
        if doMove:
            horizontalMove = x - horAndVerMove[0]
            verticalMove = y - horAndVerMove[1]

    def projectOnSphere(self,x,y,r):
        x, y = x-self.width/2.0, self.height/2-y
        a = min(r*r, x**2 + y**2)
        z = math.sqrt(r*r - a)
        l = math.sqrt(x**2 + y**2 + z**2)
        return x/l, y/l, z/l
        
    def retLength(self, x,y,r):
        x, y = x-self.width/2.0, self.height/2.0-y
        a = min(r*r, x**2+y**2)
        z = math.sqrt(r*r-a)
        l = math.sqrt(x**2+y**2+z**2)
        return l

    def mousemoved(self, window, x, y):
        global angle, axis, startP
        if doRotation:
            r = min(self.width, self.height)/2.0
            if -1 <= np.dot(startP,self.projectOnSphere(x,y,r)) <= 1:
                moveP = self.projectOnSphere(x,y,r)
                angle = np.arccos(np.dot(startP, moveP))
                axis = np.cross(startP, moveP)
        if doMove:
                self.objectMoved((x/self.width), 1-y/self.height)
        if doScaleButton:
            if startPoint > x:
                self.scene.scale *= 0.97
            else:
                self.scene.scale /= 0.97

    def rotate(self, angle, axis):
        c, mc = math.cos(angle), 1-math.cos(angle)
        s = math.sin(angle)
        l = math.sqrt(np.dot(np.array(axis), np.array(axis)))
        if l == 0:
            return np.identity(4)
        x, y, z = np.array(axis)/l
        r = np.array (
            [[x*x*mc+c, x*y*mc-z*s, x*z*mc+y*s, 0], 
            [x*y*mc+z*s, y*y*mc+c, y*z*mc-x*s, 0],
            [x*z*mc-y*s, y*z*mc+x*s, z*z*mc+c, 0],
            [0, 0, 0, 1]])
        return np.transpose(r)

    def onKeyboard(self, win, key, scancode, action, mods):
        global ortho, hatSchatten
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True
            if mods == glfw.MOD_SHIFT:
                if key == glfw.KEY_S:
                    self.scene.color = (0.2,0.2,0.2)
                if key == glfw.KEY_R:
                    self.scene.color = (1,0,0)
                if key == glfw.KEY_G:
                    self.scene.color = (0,1,0)
                if key == glfw.KEY_B:
                    self.scene.color = (0,0,1)
                if key == glfw.KEY_W:
                    self.scene.color = (0.9,0.9,0.9,1)   
            else:
                if key == glfw.KEY_S:
                    glClearColor(0, 0, 0, 0)
                if key == glfw.KEY_G:
                    glClearColor(0, 1, 0, 0)
                if key == glfw.KEY_R:
                    glClearColor(1, 0, 0, 1)
                if key == glfw.KEY_B:
                    glClearColor(0, 0, 1, 1)
                if key == glfw.KEY_W:
                    glClearColor(1, 1, 1, 1)
                if key == glfw.KEY_P:
                    ortho = False
                if key == glfw.KEY_O:
                    ortho = True
                if key == glfw.KEY_J:
                    if hatSchatten == False:
                        hatSchatten = True
                    else:
                        hatSchatten = False
            
    def onSize(self, win, width, height):
        print("onsize: ", win, width, height)
        if height <= 0:
            self.height = 1
        elif width <= 0:
            self.width = 1
        else:
            self.width = width
            self.height = height
            self.aspect = width/float(height)
        
        glViewport(0, 0, self.width, self.height)
    
    def run(self):
        global ortho, hatSchatten, l, startPoint
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
                # render 
                self.display(t)
                # swap front and back buffer
                glfw.swap_buffers(self.window)
                # Poll for and process events
                glfw.poll_events()
        # end
        glfw.terminate()
    
    def display(self, t):
        myVBO.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glVertexPointer(3, GL_FLOAT, 24, myVBO)
        glNormalPointer(GL_FLOAT, 24, myVBO + 12)
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if not ortho:
            if self.width <= self.height:
                glFrustum(-1.5, 1.5, -1.5*self.height/self.width, 1.5*self.height/self.width, 1, 10)
                gluLookAt(0,0,5,0,0,0,0,1,0)
            else:
                glFrustum(-1.5*self.width/self.height, 1.5*self.width/self.height, -1.5, 1.5, 1, 10)
                gluLookAt(0,0,5,0,0,0,0,1,0)
        else:
            if self.width <= self.height:
                glOrtho(-1.5, 1.5, -1.5*self.height/self.width, 1.5*self.height/self.width, -5, 10)
            else:
                glOrtho(-1.5*self.width/self.height, 1.5*self.width/self.height, -1.5, 1.5, -5, 10)

        glMatrixMode(GL_MODELVIEW)
        glTranslate(horizontalMove, verticalMove, 0)
        glMultMatrixf(np.dot(actOri, self.rotate(angle,axis)))
        glScalef(self.scene.scale,self.scene.scale,self.scene.scale)
        glTranslatef(-self.scene.center[0], -self.scene.center[1], -self.scene.center[2]) 
        if hatSchatten:
            self.renderShadow()
        glColor(self.scene.color)
        glDrawArrays(GL_TRIANGLES,0,len(data))
        myVBO.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)

    def renderShadow(self):
        schattenPos = np.array([[1.0,0,0,0],
                        [0,1.0,0,0],
                        [0,0,1.0,0],
                        [0,1.0/-l[1],0,0]]).transpose()  
        glPushMatrix()
        glTranslatef(0,self.scene.boundingBox[0][1],0)
        glTranslatef(l[0],l[1],l[2])
        glMultMatrixf(schattenPos)
        glTranslatef(-l[0],-l[1],-l[2])
        glTranslatef(0,-self.scene.boundingBox[0][1],0)
        glColor(0.4, 0.4, 0.4)
        glDisable(GL_LIGHTING)
        glDrawArrays(GL_TRIANGLES, 0, len(data))
        glEnable(GL_LIGHTING)      
        glPopMatrix()

def readobj(path):
    vertices, faces, normals, ifNoNormals = [],[],[],[]
    with open(path,"r") as file:
        for line in file:
            if line.startswith('vn'):
                split = line.split()
                normals.append(split[1:])
            elif line.startswith('v'):
                split = line.split()
                split = split[1:]
                vertex = [float(split[0]),float(split[1]), float(split[2])]
                vertices.append(vertex)
            elif line.startswith('f'):
                split = line.split()
                face = split[1:]
                face = [f.split('/') for f in face]
                faces.append(face)

    vertices = np.array(vertices)

    if len(normals) == 0:
        if len(vertices) < 1:
            print("given file is wrong")
            sys.exit(1)
        ifNoNormals = [0] * len(vertices)
        for face in faces:
            normal = np.cross(vertices[int(face[2][0])-1] - vertices[int(face[0][0])-1], vertices[int(face[2][0])-1] - vertices[int(face[1][0])-1])
            ifNoNormals[int(face[0][0])-1] = normal
            ifNoNormals[int(face[1][0])-1] = normal
            ifNoNormals[int(face[2][0])-1] = normal

    return vertices, faces, normals, ifNoNormals

# call main
if __name__ == '__main__':
    
    vertexShader = open("vertexShader.vs","r").read()
    fragmentShader = open("fragShader.fs", "r").read()
    
    lightPos = np.array([-2.0, 4.0, -1.0])
    
    if(len(sys.argv) != 2):
        print("pointViewerTemplate.py File.obj")
        sys.exit(1)
    readFile = readobj(sys.argv[1])
    vertices, faces, normals, ifNoNormals = readFile[0], readFile[1], readFile[2], readFile[3]
    data = []
    if len(normals) != 0:
        for face in faces:
            for vertex in face: 
                vn = int(vertex[0])-1
                nn = int(vertex[2])-1
                data.append(vertices[vn])
                data.append(normals[nn])
    else:
        for face in faces:
            for vertex in face:
                vn = int(vertex[0])-1
                data.append(vertices[vn])
                data.append(ifNoNormals[vn])
    
    scene = Scene(width, height, vertexShader, fragmentShader, vertices, "pointViewer Template")
    myVBO = vbo.VBO(np.array(data, 'f'))

    rw = RenderWindow(scene)
    rw.run()