import core.pml as pml, core.pmlutil as pmlutil, logging, os
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import ElasticNetCV

def readArray(s):
    s=s.strip().split(',')
    a=[]
    for e in s:
        a.append(float(e))
    return np.array(a)

class CommentsAnalyzer(pmlutil.Configurable):
    
    def configTypes(self):
        return dict(amount=int, min_ngram=int, max_ngram=int, min_df=int, max_df=float, use_idf=int, alpha=readArray, l1_ratio=readArray, n_folds=int)

    def _loadData(self):
        logging.info("loading data")
        self.data = []
        count = 0
        for fn in os.listdir(self._datafolder):
            if not self._amount < 1 and count >= self._amount:
                break
            if fn.endswith(self._metaextension):
                mfn = self._datafolder + "/" + fn
                ddm = pml.Datum(mfn,None)
                if len(ddm.meta()['comments'])>0:
                    self.data.append(ddm)
                    count +=1
        logging.info("loaded %d data" % count)

    def __init__(self):
        self.data=[]

    def _aggregateComments(self, subset):
        allcomments = []
        for datum in subset:
            comments = []
            for comment in datum.meta()['comments']:
                comments.append(comment['text'])
            allcomments.append(" ".join(comments))
        return np.array(allcomments)

    def _buildDictionary(self, allcomments):
        print allcomments
        self.vectorizer = TfidfVectorizer(analyzer=self._analyzer, ngram_range=(self._min_ngram,self._max_ngram),
                                     min_df=self._min_df, max_df=self._max_df, norm='l2', smooth_idf=True, use_idf=bool(self._use_idf))
        self.vectorizer.fit(allcomments)

    def run(self):
        allcomments = self._aggregateComments(self.data)
        self._buildDictionary(allcomments)

        # create representation of documents
        tfidfArray = self.vectorizer.transform(allcomments)

        # create labelling
        labels = []
        for datum in self.data:
            labels.append(len(datum.meta()['favorites']))
        labels = np.array(labels)

        print self.vectorizer.get_params()
        print self.vectorizer.get_feature_names()

        # training
        self.elasticNet = ElasticNetCV(alphas=self._alpha, l1_ratio=self._l1_ratio, fit_intercept=True, normalize=False, precompute='auto', max_iter=1000, copy_X=True, tol=0.0001, rho=None, cv=self._n_folds)
        self.elasticNet.fit(tfidfArray,labels)

        for i,l1_ratio in enumerate(self._l1_ratio):
            for j,alpha in enumerate(self._alpha):
                print "alpha: %f, l1_ratio: %f --> %f" % (alpha,l1_ratio,np.mean(self.elasticNet.mse_path_[i,j,:]))

        print self.vectorizer.inverse_transform(self.elasticNet.coef_)

