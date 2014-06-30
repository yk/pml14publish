import core.pml as pml,logging
import numpy as np
import coverageshell

class GeoUniformShell(coverageshell.UniformShell):
    """ It uses a plane approximation of the earth in the neighborhood of the pictures"""

    def config(self):
        return dict(earthRadius=float)

    def filter(self,datum):
        if not 'location' in datum.meta():
            return False
        if not 'longitude' in datum.meta()['location']:
            return False
        if not 'latitude' in datum.meta()['location']:
            return False
        return True

    def angleToDistance(self,angle):
        return self._earthRadius*angle*np.pi/180.0
    
    def locate(self,datum):
        x = self.angleToDistance(datum.meta()['location']['longitude'])
        y = self.angleToDistance(datum.meta()['location']['latitude'])
        return np.array([x,y])


class GeoHotspotShell(coverageshell.HotspotShell):
    """ It uses a plane approximation of the earth in the neighborhood of the pictures"""
    
    def config(self):
        return dict(earthRadius=float)
    
    def filter(self,datum):
        if not 'location' in datum.meta():
            return False
        if not 'longitude' in datum.meta()['location']:
            return False
        if not 'latitude' in datum.meta()['location']:
            return False
        return True
    
    def angleToDistance(self,angle):
        return self._earthRadius*angle*np.pi/180.0
    
    def locate(self,datum):
        x = self.angleToDistance(datum.meta()['location']['longitude'])
        y = self.angleToDistance(datum.meta()['location']['latitude'])
        return np.array([x,y])