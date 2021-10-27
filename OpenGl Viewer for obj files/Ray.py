import numpy as np

class Ray(object):
    def __init__(self, origin, direction):
        self.origin = origin # point
        self.direction = normal(direction) # vector

    def __repr__(self):
        return 'Ray(%s,%s)' %(repr(self.origin), repr(self.direction))

    def pointAtParameter(self, t):
        return self.origin + self.direction * t

def normal(vector):
    return vector / np.linalg.norm(vector)