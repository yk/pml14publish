import numpy as np
import numpy.random as rand
import pml,jinja2,os,cgi,webbrowser,itertools,logging
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

class OnlineOptimizer(pml.ShellMixtureMaximizer):

    def __init__(self,**kwargs):
        super(OnlineOptimizer,self).__init__(**kwargs)
        self.running_ = True

    def configTypes(self):
        types = super(OnlineOptimizer,self).configTypes()
        types['lambda']=float
        types['alpha']=float
        types['khighest']=int
        return types

    def _optimizeStep(self,rewards=None):
        if rewards is None:
            self.t_ = 0
            self.ndata_,self.nshells_ = len(self.data),len(self.shells)
            self.Mt_ = self._lambda*np.identity(self.nshells_)
            self.bt_ = np.zeros(self.nshells_)
            self.wt_ = np.array(self.weights)
        else:
            self.Mt_ += np.dot(np.transpose(self.dtl__),self.dtl__)
            self.bt_ += np.dot(np.array(rewards),self.dtl__)
            self.wt_ = np.dot(np.linalg.inv(self.Mt_),self.bt_)
        self.wt_ = np.maximum(self.wt_,np.zeros(self.wt_.shape))
        self.wt_ /= np.sum(self.wt_)
        print "weights ",self.wt_
        _At = range(self.ndata_)
        At = []
        dt = []
        for l in range(self._budget):
            deltas = []
            subset = [self.data[i] for i in At]
            subsetShellEvaluation = []
            for shell in self.shells:
                subsetShellEvaluation.append(shell.evaluateNormalized(subset))
                # logging.info("shell %s evaluates the current subset (size %i) as %f",shell.__class__.__name__,len(subset),subsetShellEvaluation[-1])
            for a in _At:
                deltarow = []
                for i,shell in enumerate(self.shells):
                    element = self.data[a]
                    delta = shell.evaluateNormalized(subset + [element]) - subsetShellEvaluation[i]
                    deltarow.append(delta)
                deltas.append(deltarow)
            deltas = np.array(deltas)
            mus = np.dot(deltas,self.wt_)
            cs = self._alpha*np.sqrt(np.sum(deltas*np.dot(deltas,np.transpose(np.linalg.inv(self.Mt_))),axis=1))
            ams = np.argsort(mus+cs)[-self._khighest:]
            am = np.random.choice(ams)
            atl = _At[am]
            At.append(atl)
            _At.remove(atl)
            dt.append(deltas[am,:])

        self.dtl__ = np.vstack(dt)
        self.suggested__ = [self.data[i] for i in At]
        self.t_+=1
        return self.suggested__

    def _maximize(self):
        pass

class ServerRequestHandler(BaseHTTPRequestHandler):

    def sendResponse(self,suggestions):
        loader = jinja2.FileSystemLoader('core/templates')
        env = jinja2.Environment(loader=loader)
        env.globals['include_file'] = lambda name: jinja2.Markup(loader.get_source(env,name)[0])
        env.globals['zip'] = zip
        template = env.get_template('online.template')

        notSelected = list(set(ServerRequestHandler.maximizer.data) - set(suggestions))


        shells = [dict(name=shell.__class__.__name__,weight=weight) for shell,weight in zip(ServerRequestHandler.maximizer.shells,ServerRequestHandler.maximizer.weights)]
        
        shellscores = [shell.evaluateNormalized(suggestions) for shell in ServerRequestHandler.maximizer.shells]

        data = dict(selected=suggestions,notSelected=notSelected,shellscores=shellscores,shells=shells,os=os)

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(template.render(data))

    def do_GET(self):
        if self.path.startswith("/img/"):
            with open(self.path[5:]) as f:
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(f.read())

        if not self.path == '/': return
        suggestions = ServerRequestHandler.maximizer._optimizeStep()
        self.sendResponse(suggestions)

    def do_POST(self):
        if not self.path == '/': return
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={"REQUEST_METHOD": "POST"}
        )

        submitted = dict((item.name, int(item.value)) for item in form.list)
        sugg = ServerRequestHandler.maximizer.suggested__
        rewards = [submitted[s.meta()['id']] for s in sugg]
        suggestions = ServerRequestHandler.maximizer._optimizeStep(rewards)
        self.sendResponse(suggestions)


class UserFeedbackOnlineOptimizer(OnlineOptimizer):
    def __init__(self,port=8080,**kwargs):
        super(UserFeedbackOnlineOptimizer,self).__init__(**kwargs)
        ServerRequestHandler.maximizer = self
        self.port = port
        self.server_ = HTTPServer(('',self.port),ServerRequestHandler)

    def _maximize(self):
        print 'starting server'
        webbrowser.open("http://localhost:" + str(self.port))
        try:
            self.server_.serve_forever()
        except KeyboardInterrupt:
            self.server_.socket.close()
            return self.suggested__

class BotFeedbackOnlineOptimizer(OnlineOptimizer):
    def __init__(self,**kwargs):
        super(BotFeedbackOnlineOptimizer,self).__init__(**kwargs)
        self.maxIter = 1000 
        self.resList = []
        self.useNoise = False
        self.useDiscreteRewards = False
        self.absTol = 1e-12
        self.minVal = 0
        self.maxVal = 1.6

    def setBotWeights(self,weights):
        self.botWeights = weights / np.sum(weights)
        print "botWeights",self.botWeights

    def setMaxIter(self,maxIter):
        self.maxIter = maxIter

    def setAbsTerminationCriteria(self,absTol):
        self.absTol = absTol

    def setNoise(self,stdNoise):
        self.stdNoise = stdNoise;
        self.useNoise = True

    def setUseDiscreteRewards(self,minVal=1,maxVal=5):
        self.bins = np.linspace(0,self.maxVal,maxVal-minVal+2) # rewards in [0,1.6]
        self.minVal = minVal
        self.maxVal = maxVal
        self.useDiscreteRewards = True

    def _maximize(self, normalize=True):
        if len(self.botWeights) != len(self.shells):
            logging.error("The length of the botWeights does not match the number of shells.")
            return None

        try:
            suggested = self._optimizeStep()
            self.resList = []
            self.resList.append(np.linalg.norm(self.wt_/np.sum(self.wt_) - self.botWeights))
            self.scoreList = []
            self.scorePerShellList = []

            for i in range(0,self.maxIter):
                lastScore = 0.0
                reward = []
                subset = []
                scorePerShell = np.zeros((len(self.shells),1))

                for datum in suggested:
                    score = 0.0
                    subset.append(datum)
                    for i,shell in enumerate(self.shells):
                        shellscore = float(shell.evaluateNormalized(subset) if normalize else shell.evaluate(subset))
                        score += shellscore*self.botWeights[i]
                        scorePerShell[i] = shellscore
                    reward.append(score-lastScore)
                    lastScore = score
                self.scoreList.append(np.sum(reward))
                self.scorePerShellList.append(scorePerShell)

                # print "true reward", reward
                if self.useNoise:
                    reward = list(reward + rand.normal(0,self.stdNoise,len(reward)))
                if self.useDiscreteRewards:
                    reward = list(np.digitize(reward,self.bins) + self.minVal - 1)
                reward = list(np.clip(reward, self.minVal, self.maxVal)) 
                # print "reward", reward

                suggested = self._optimizeStep(reward)

                self.resList.append(np.linalg.norm(self.wt_/np.sum(self.wt_) - self.botWeights))
                print "residual", self.resList[-1]
                if (self.resList[-1] < self.absTol):
                    print "Termination criteria satisfied after " + str(i+1) + " iterations"
                    break

        except KeyboardInterrupt:
            return self.suggested__
