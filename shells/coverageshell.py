import core.pml as pml,logging
import numpy as np

def readArray(s):
    s=s.strip().split(',')
    a=[]
    for e in s:
        a.append(float(e))
    return np.array(a)

class UniformShell(pml.SubmodularShell):
    """ A general coverage shell in n-dimensions. In practice, it is instantiated for small dimensions like geocoverage, timecoverage. """
    
    def configTypes(self):
        return dict(self.config().items(),std=float,gridResolution=readArray,gridMargin=readArray)
    
    def createGrid(self):
        self.grid = np.zeros(tuple(self._gridResolution)+(len(self._gridResolution),))
        it = np.nditer(self.grid, flags=['multi_index'], op_flags=['readwrite'])
        while not it.finished:
            it[0] = self.minPos[it.multi_index[-1]] + it.multi_index[it.multi_index[-1]]/float(self._gridResolution[it.multi_index[-1]]-1)*self.gridSize[it.multi_index[-1]]
            it.iternext()

    def prepare(self,data):
        isSet=False
        for datum in data:
            p = self.locate(datum)
            if not isSet:
                self.minPos = p
                self.maxPos = p
                isSet=True
            else:
                self.minPos = np.minimum(self.minPos, p)
                self.maxPos = np.maximum(self.maxPos, p)
    
        self.gridSize = self.maxPos-self.minPos
        logging.info("The pictures are contained in a rectangle of size %f x %f" % tuple(self.gridSize))
        self.minPos -= self._gridMargin*self.gridSize
        self.maxPos += self._gridMargin*self.gridSize
        self.gridSize = self.maxPos-self.minPos
        
        self.createGrid()
        self.std = self._std*max(self.gridSize/self._gridResolution)
    
    
    def evaluate(self,subset):
        score = np.zeros(self.grid.shape[:-1])
        shape_tuple = (1,)*(len(self.grid.shape)-1)+(self.grid.shape[-1],)
        for datum in subset:
            position =  self.locate(datum).reshape(shape_tuple)
            p = np.tile(position,tuple(self.grid.shape[:-1])+(1,))
            score = np.maximum(score, np.exp(-0.5*(np.sum((self.grid-p)**2, len(self.grid.shape)-1))/self.std**2) )
        return np.sum(score)

    def config(self):
        pass

    def filter(self,datum):
        pass

    def locate(self,datum):
        pass


class HotspotShell(pml.SubmodularShell):
    """ A general hotspot shell in n-dimensions. It minimizes the k-means cost function.
        In practice, it is instantiated for small dimensions like geocoverage, timecoverage. """
    
    def configTypes(self):
        return self.config()
    
    def prepare(self,data):
        d = max(self.locate(data[0]).shape)
        n = len(data)
        
        points = np.zeros((n,d))
        self.origin = None
        for i,datum in enumerate(data):
            p = self.locate(datum)
            datum.ext['hotspot'] = dict(index=i)
            points[i,:] = p
            if self.origin == None:
                self.origin = p
            else:
                self.origin = np.minimum(self.origin,p)
        
        sqNorm = np.sum(points**2, axis=1)
        self.sqDistance = np.tile(sqNorm,(n,1)).T+np.tile(sqNorm,(n,1))-2*np.dot(points,points.T)
        
        maxDistance = np.sqrt(np.amax(self.sqDistance))
        self.origin -= 2*maxDistance*np.ones(self.origin.shape)
        
        self.costToOrigin = np.sum((points-np.tile(self.origin,(n,1)))**2)
    
    def evaluate(self,subset):
        indices = [datum.ext['hotspot']['index'] for datum in subset]
        
        score = self.costToOrigin
        
        if indices == []:
            return 0.0
        
        score -= np.sum(np.amin(self.sqDistance[:,indices],axis=1))
        
        return score
    
    
    
    def config(self):
        pass
    
    def filter(self,datum):
        pass
    
    def locate(self,datum):
        pass
