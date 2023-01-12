
import numpy as np
from OpenGL.GL import *

class Scene:
    """ OpenGL 2D scene class """
    # initialization
    def __init__(self, width, height,  
                points=[np.array([0, 0, 0, 1])],   
                scenetitle="2D Scene", ):
        # time
        self.t = 0
        self.dt = 0.001
        self.scenetitle = scenetitle
        self.pointsize = 7
        self.linewidth = 3
        """Die Szene kennt die Farbe der Objekte"""
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
        
    # set scene dependent OpenGL states
    def setOpenGLStates(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)
        
    # animation
    def animation(self):
        if self.animate: 
            self.beta += 10
            if self.beta > 360:
                self.beta = 0        
