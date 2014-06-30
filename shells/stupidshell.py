import core.pml as pml

class StupidShell(pml.SubmodularShell):
    def configTypes(self):
        return dict(numberOfFingers=int)

    def filter(self,datum):
        return len(datum.meta()['tags']) > 0

    def prepare(self,data):
        print 'hi, my name is %s, my favorite dish is %s and I have %d fingers' % (self.__class__.__name__,self._favoriteDish,self._numberOfFingers)

    def evaluate(self,subset):
        score = 0
        for datum in subset:
            meta = datum.meta()
            score += len(meta['title'])
        return score
