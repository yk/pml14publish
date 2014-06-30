import core.pml as pml
import shells.geocoverageshell as geocoverageshell
import shells.bagoftagsshell as bagoftagsshell
# import shells.bagofvisualwordsshell as bagofvisualwordsshell
import shells.bagofwordsshell as bagofwordsshell
import shells.viewcountshell as viewcountshell
import shells.contrastshell as contrastshell
import shells.emotionshell as emotionshell
import shells.complexityshell as complexityshell
import os
import core.online
from core.reports import *
import numpy as np
import numpy.random as rand
from matplotlib import pyplot as plt

if __name__ == '__main__':

    gc = geocoverageshell.GeoUniformShell()
    gc.configureFromFile("configs/geocoverage.default.config")
    gh = geocoverageshell.GeoHotspotShell()
    gh.configureFromFile("configs/geohotspot.default.config")
    bot = bagoftagsshell.BagOfTagsShell()
    bot.configureFromFile("configs/bagoftags.default.config")
    # bovw = bagofvisualwordsshell.BagOfVisualWordsShell()
    # bovw.configureFromFile("configs/bagofvisualwords.default.config")
    bow = bagofwordsshell.BagOfWordsShell()
    bow.configureFromFile("configs/bagofwordsshell.default.config")
    vc = viewcountshell.ViewCountShell()
    vc.configureFromFile("configs/viewcountshell.default.config")
    ch = contrastshell.ContrastHotspotShell()
    cs = contrastshell.ContrastSummationShell()
    em = emotionshell.EmotionSummationShell()
    co = complexityshell.ComplexityShell()


    # -------------------------------------------------------------
    # Params
    # -------------------------------------------------------------

    # shells = [gh, bot, bow, ch, cs, em, co]  # Shells to be used
    shells = [vc, gh, bot]  # Shells to be used
    nShells = len(shells)

    nRuns = 20     # #repeats for averaging
    nIters = 30   # #iterations done 

    botWeights = rand.random((nRuns,nShells))   # random bot weights

    # -------------------------------------------------------------


    # Optimal Feedback
    res = np.empty((nIters+1,nRuns))
    for i in range(0,nRuns):
        mm = core.online.BotFeedbackOnlineOptimizer()
        mm.configureFromFile("configs/online.default.config")
        mm.setBotWeights(botWeights[i])
        mm.setMaxIter(nIters)
        for s in shells:
            mm.addShell(s)
        mm.run()
        print mm.resList
        res[:,i] = np.array(mm.resList)
    resStd = np.std(res,axis=1)
    res = np.mean(res,axis=1)
    plt.errorbar(np.arange(0,nIters+1),res,yerr=resStd,label="no noise")

    # Optimal Feedback with noise
    stdNoise = [0.001, 0.01,0.1,0.3] 
    for std in stdNoise:
        res = np.empty((nIters+1,nRuns))
        for i in range(0,nRuns):
            mm = core.online.BotFeedbackOnlineOptimizer()
            mm.configureFromFile("configs/online.default.config")
            mm.setBotWeights(botWeights[i])
            mm.setMaxIter(nIters)
            mm.setNoise(std)
            for s in shells:
                mm.addShell(s)
            mm.run()
            print mm.resList
            res[:,i] = np.array(mm.resList)
        resStd = np.std(res,axis=1)
        res = np.mean(res,axis=1)
        plt.errorbar(np.arange(0,nIters+1),res,yerr=resStd,label="std="+str(std))

    plt.yscale('log')
    plt.legend(fancybox=True,shadow=True)
    plt.xlabel('iteration')
    plt.ylabel('residual')
    plt.title('Convergence for different kinds of feedback')
    plt.savefig('./plots/convergence_feedback.png', bbox_inches='tight')
    plt.show()