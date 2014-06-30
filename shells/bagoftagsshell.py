import core.pml as pml
import numpy as np

class BagOfTagsShell(pml.SubmodularShell):
    def configTypes(self):
        return dict(brevity=float)

    def filter(self,datum):
        return len(datum.meta()['tags']) > 0

    def prepare(self,data):
        pass

    def evaluate(self,subset):
        bag = dict()
        for datum in subset:
            tags = datum.meta()['tags']
            n_tags = len(tags)
            for tag in tags:
                if not tag['text'] in bag:
                    bag[tag['text']] = np.exp((1-n_tags)/self._brevity)
                else:
                    bag[tag['text']] = max(bag[tag['text']],np.exp((1-n_tags)/self._brevity))
        score = 0
        for _,value in bag.iteritems():
            score += value
        return score
