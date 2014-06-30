import core.pml as pml,logging
from mahotas.features import surf
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from concurrent import futures

class VisualWordsEstimator(object):
    def __init__(self,vs):
        self._vocabularySize = vs
    def fit(self,X,y=None):
        self.km = KMeans(n_clusters=self._vocabularySize)
        self.km.fit(np.vstack(X))
        return self
    def transform(self,X,y=None):
        return np.array(map(self.km.predict,X))

class BagOfVisualWordsShell(pml.SubmodularShell):
    def configTypes(self):
        return dict(vocabularySize=int,maxFeatures=int)

    def filter(self,datum):
        return True

    def prepare(self,data):
        ftrs = []
        for ind,datum in enumerate(data):
            img = datum.bwimage()
            spoints = surf.surf(img,descriptor_only=True,max_points=self._maxFeatures)
            #spoints = np.hstack((spoints,np.tile(ind,[spoints.shape[0],1])))
            ftrs.append(spoints)
            datum.ext['bagofvisualwords'] = dict(features=spoints)
            logging.info("found %d features in image %d/%d" %(spoints.shape[0],ind,len(data)))
        #ftrs = np.vstack(ftrs)
        #ftrs = np.dstack(ftrs)
        #logging.info("found %d features in total"%ftrs.shape[0])
        logging.info("running kmeans for %d clusters" % self._vocabularySize)
        self.estimator = Pipeline([
            ('kmeans',VisualWordsEstimator(self._vocabularySize)),
            ('wrd',type("Wordizer",(object,),{"transform":lambda self,X,y=None : [" ".join(np.vectorize(str)(x)) for x in X],"fit":lambda self,X,y=None:self})()),
            ('vect', CountVectorizer(token_pattern='\\b\\d+\\b')),
            ('tfidf', TfidfTransformer()),
            ('pred',type("Predictor",(object,),{"transform":lambda self,X,y=None : X,"fit":lambda self,X,y=None:self,"predict":lambda self,X:X})()),
            ])
        self.estimator.fit(ftrs)
        logging.info("kmeans done")

    def evaluate(self,subset):
        if len(subset)==0:
            return 0.0
        ftrs = []
        for datum in subset:
            ftrs.append(datum.ext['bagofvisualwords']['features'])
        #ftrs = np.vstack(ftrs)
        clusters = self.estimator.predict(ftrs)
        score = np.sum(np.max(clusters.toarray(),axis=0))
        return score
