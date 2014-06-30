import core.pml as pml, logging
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.stem.snowball import EnglishStemmer, GermanStemmer


class BagOfWordsShell(pml.SubmodularShell):

    def configTypes(self):
        return dict(analyzer=str, min_df=int, max_df=float, use_idf=int)

    def filter(self, datum):
        return len(datum.meta()['tags']) > 0

    def prepare(self, data):
        alltags = self.get_all_tags(data)
        engStemmer = EnglishStemmer()
        gerStemmer = GermanStemmer()
        alltags = [gerStemmer.stem(engStemmer.stem(imgTags)) for imgTags in alltags]
        self.build_dictionary(alltags)
        self.bow = self.transform(alltags)
        for i, datum in enumerate(data):
            datum.ext['id'] = i

    def evaluate(self, subset):
        score = 0
        if len(subset):
            idx = [datum.ext['id'] for datum in subset]
            bowSubset = self.bow[idx,:]
            if bowSubset.shape[0] and bowSubset.shape[1]:
                score = bowSubset.todense().max().sum()
        return score

    def build_dictionary(self, alltags):
        vectorizer = CountVectorizer(analyzer=self._analyzer, ngram_range=(1,1),
             min_df=self._min_df, max_df=self._max_df, stop_words='english')
        allfeat = vectorizer.fit_transform(alltags)
        transformer = TfidfTransformer(norm='l2', smooth_idf=True, use_idf=bool(self._use_idf))
        transformer.fit(allfeat)
        self.vectorizer = vectorizer
        self.transformer = transformer

        # Print dictionary
        # bowDict = vectorizer.get_feature_names()
        # print bowDict
        # print len(bowDict)


    def get_all_tags(self, data):
        """ Get list of all tags for set of images.
        :return: list of tag strings. Each string contains all tags for 1 image
        """
        alltags = []
        for datum in data:
            tags = [tag['text'] for tag in datum.meta()['tags']]
            alltags.append(" ".join(tags))
        return alltags

    def transform(self, tags):
        return self.transformer.transform(self.vectorizer.transform(tags))

    def sparse_max_per_col(self, mat):
        max_per_col = np.zeros(mat.shape[1])
        for i in range(0, mat.shape[1]):
            max_per_col[i] = mat.getcol(i).max()
        return max_per_col
