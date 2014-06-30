import core.pml as pml,logging
import numpy as np
from PIL import Image
import StringIO

class ComplexityShell(pml.SubmodularShell):

    def config(self):
        return dict()

    def filter(self,datum):
        return True

    def prepare(self, data):
        for datum in data:
            sio = StringIO.StringIO()
            Image.fromarray(datum.image()).save(sio,format="JPEG")
            datum.ext['complexity'] = dict(complexity=float(sio.len)/datum.image().size)

    def evaluate(self,subset):
        return np.sum([datum.ext['complexity']['complexity'] for datum in subset])
