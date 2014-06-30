import core.pml as pml,logging
import numpy as np
import coverageshell

class ContrastHotspotShell(coverageshell.HotspotShell):

    def config(self):
        return dict()

    def filter(self,datum):
        return True
    
    def locate(self,datum):
        I = datum.image()/255.0
        return np.array([ np.std(I[:,:,i]) for i in xrange(3)])


class ContrastSummationShell(pml.SubmodularShell):

    def config(self):
        return dict()

    def filter(self,datum):
        return True

    def prepare(self, data):
        self.std = []
        self.dataList = []
        for datum in data:
            I = datum.bwimage()/255.0
            self.std.append(np.std(I))
            self.dataList.append(datum)
        self.std = np.array(self.std)

    def evaluate(self,subset):
        indices = []
        for datum in subset:
            indices.append(self.dataList.index(datum))
        return np.sum(self.std[indices])
        
