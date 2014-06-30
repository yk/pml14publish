import heapq,itertools,logging,os,json,core.pmlutil,random
from scipy import misc

logging.basicConfig(level=logging.DEBUG)

class SubmodularShell(core.pmlutil.Configurable):
    def filter(self,datum):
        return True

    def prepare(self,data):
        pass

    def evaluate(self,subset):
        pass

    def evaluateNormalized(self,subset):
        score = float(self.evaluate(subset))
        bestSolo = self.getBestSoloScore()
        worstSolo = self.getWorstSoloScore()
        maximum = self.getMaximum()
        score = (score - worstSolo) / (maximum - worstSolo)
        return score

    def getMaximum(self):
        if not hasattr(self,'maximum'):
            raise Exception('shell has no maximum')
        else:
            return self.maximum

    def getBestSoloScore(self):
        if not hasattr(self,'bestSoloScore'):
            raise Exception('shell has no bestSoloScore')
        else:
            return self.bestSoloScore

    def getWorstSoloScore(self):
        if not hasattr(self,'worstSoloScore'):
            raise Exception('shell has no worstSoloScore')
        else:
            return self.worstSoloScore

class Datum(object):
    def __init__(self,metaFilePath,imageFilePath):
        self.metaFilePath = metaFilePath
        self.imageFilePath = imageFilePath
        self._meta,self._image,self._bwimage = None,None,None
        self.ext = dict()

    def meta(self):
        if not self._meta:
            with open(self.metaFilePath) as f:
                self._meta = json.load(f)
        return self._meta

    def image(self):
        if self._image == None:
            self._image = misc.imread(self.imageFilePath)
        return self._image

    def bwimage(self):
        if self._bwimage == None:
            self._bwimage = misc.imread(self.imageFilePath,True)
        return self._bwimage

class ShellMixtureMaximizer(core.pmlutil.Configurable):

    def __init__(self):
        self.shells = []
        self.weights = []
        self.data = None

    def configTypes(self):
        return dict(amount=int, budget=int)

    def addShell(self,shell,weight=1.0):
        self.shells.append(shell)
        self.weights.append(weight)
        logging.info("added shell %s with weight %f" % (shell.__class__.__name__,weight))

    def _loadData(self):
        logging.info("loading data")
        self.data = []
        count = 0
        for fn in os.listdir(self._datafolder):
            if not self._amount < 1 and count >= self._amount:
                break
            if fn.endswith(self._metaextension):
                stem = fn[:-len(self._metaextension)]
                mfn = self._datafolder + "/" + fn
                ifn = self._datafolder + "/" + stem + self._imgextension
                if os.path.isfile(ifn):
                    ddm = Datum(mfn,ifn)
                    good = True
                    for shell in self.shells:
                        good = good and shell.filter(ddm)
                    if good:
                        self.data.append(ddm)
                        count += 1
                else:
                    logging.error("no image found for %s" % mfn)
        logging.info("loaded %d data" % count)

    def _prepare(self):
        for shell in self.shells:
            shell.prepare(self.data)

        tmp = (self.shells,self.weights)

        logging.info("calculating maxima")

        for shell in tmp[0]:
            self.shells,self.weigths = [shell],[1.0]
            selected,minmax = ShellMixtureMaximizer._maximize(self,normalize=False,returnMinMax=True)
            shell.worstSoloScore,shell.bestSoloScore = minmax
            shell.maximum = float(shell.evaluate(selected))
            logging.info("the maximum for shell %s is %f, the best single item score is %f, the worst is %f",shell.__class__.__name__,shell.maximum,shell.bestSoloScore,shell.worstSoloScore)

        self.shells,self.weights = tmp

    def _evaluate(self,subset,normalize=True):
        total = 0.0
        for shell,w in itertools.izip(self.shells,self.weights):
            shellscore = float(shell.evaluateNormalized(subset) if normalize else shell.evaluate(subset))
            total += shellscore*w
        return -total

    def _initialPass(self,normalize=True):
        logging.info("performing initial pass")
        scores = [self._evaluate([datum],normalize=normalize) for datum in self.data]
        return scores

    def _maximize(self,khighest=1,normalize=True,returnMinMax=False):
        logging.info("starting maximization procedure")
        scores = self._initialPass(normalize=normalize)
        minmax = (-max(*scores),-min(*scores)) if returnMinMax else None
        queue = zip(scores,self.data)
        heapq.heapify(queue)
        selected = []
        value_selected = 1.0
        logging.info("begin greedy procedure")
        while len(selected) < self._budget and len(queue) >= khighest:
            tops = []
            while len(tops) < khighest:
                top = heapq.heappop(queue)
                prevscore = top[0]
                value_top = self._evaluate(selected+[top[1]],normalize=normalize)
                topscore = value_top - value_selected
                second = queue[0]
                if topscore > second[0]:
                    heapq.heappush(queue,(topscore,top[1]))
                else:
                    tops.append((topscore,prevscore,value_top,top[1]))
            topInd = random.choice(range(len(tops)))
            top = tops.pop(topInd)
            for rt in tops:
                heapq.heappush(queue,(rt[0],rt[3]))
            selected.append(top[3])
            value_selected = self._evaluate(selected,normalize=normalize)
            logging.info("selected datum %s" % selected[-1].meta()['id'])
            logging.info("selected %d / %d (obj. value: %f)" %(len(selected),min(self._budget,len(queue)+len(selected)),-value_selected))
        return (selected,minmax) if returnMinMax else selected
    
    def getData(self):
        return self.data

    def run(self):
        if not self.data:
            self._loadData()
        if not self.data:
            logging.error("no data")
            return
        self._prepare()
        selected = self._maximize()
        return selected
