import core.pml as pml,logging
import numpy as np
import matplotlib

class EmotionSummationShell(pml.SubmodularShell):

    def config(self):
        return dict()

    def filter(self,datum):
        return True

    def prepare(self, data):
        for datum in data:
            hsv = matplotlib.colors.rgb_to_hsv(datum.image())
            datum.ext['emotionsummation'] = dict(emotion=max(0.0,-0.31*np.mean(hsv[:,:,1]) + 0.60*np.mean(hsv[:,:,2])))

    def evaluate(self,subset):
        return np.sum([datum.ext['emotionsummation']['emotion'] for datum in subset])
        
