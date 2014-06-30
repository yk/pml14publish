import core.pml as pml
import shells.geocoverageshell as geocoverageshell
import shells.bagoftagsshell as bagoftagsshell
# import shells.bagofvisualwordsshell as bagofvisualwordsshell
import shells.bagofwordsshell as bagofwordsshell
import shells.viewcountshell as viewcountshell
import shells.contrastshell as contrastshell
import shells.emotionshell as emotionshell
import shells.complexityshell as complexityshell
import core.online
from core.reports import *
import numpy as np
import numpy.random as rand
from matplotlib import pyplot as plt
import logging

regretType = 'cumulative'

def plotRegret(mm, shells, nIters, botWeigths, optimalScore, labelStr):
    mm.configureFromFile("configs/online.default.config")
    mm.setBotWeights(botWeights)
    mm.setMaxIter(nIters)
    for s in shells:
        mm.addShell(s)
    mm.run()

    if regretType == 'cumulative':
        regret = np.cumsum(np.maximum(0,optimalScore*np.ones(nIters) - np.array(mm.scoreList)))
    elif regretType == 'perIter':
        regret = np.maximum(0,optimalScore - np.array(mm.scoreList))
    else:
        logging.error('regretType not supported')

    # print "regret",regret
    # print "scoreList",mm.scoreList

    x = np.arange(1,nIters+1)
    y = regret / x
    plt.plot(x,y,label=labelStr)



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

    # Specify regret type to be used {cumulative, perIter}
    regretType = 'cumulative'
    np.random.seed(12)
    # np.random.seed(42)
    # np.random.seed(1020)


    shells = [gh, gc, bot, bow, ch, cs, em, co]  # Shells to be used
    # shells = [gh, bot, bow, ch, cs, em, co]  # Shells to be used
    # shells = [vc,bot,gh,bow,ch,co]
    nShells = len(shells)

    nIters = 200   # #iterations done 

    minVal = 1
    maxVal = 5

    botWeights = rand.random((nShells))   # random bot weights
    botWeights /= np.sum(botWeights)

    # -------------------------------------------------------------


    # Determine score of optimal strategy
    mm = pml.ShellMixtureMaximizer()
    mm.configureFromFile("configs/online.default.config")
    for j,s in enumerate(shells):
        mm.addShell(s,botWeights[j])
    selected = mm.run()
    optimalScore = -mm._evaluate(selected)



    plt.figure()

    # Optimal feedback
    mm = core.online.BotFeedbackOnlineOptimizer()
    plotRegret(mm, shells, nIters, botWeights, optimalScore, "optimal")


    # Feedback with noise
    stdNoise = [0.1,0.2]
    for std in stdNoise:
        mm = core.online.BotFeedbackOnlineOptimizer()
        mm.setNoise(std)
        plotRegret(mm, shells, nIters, botWeights, optimalScore, "std="+str(std))


    # Discrete feedback
    mm = core.online.BotFeedbackOnlineOptimizer()
    mm.setUseDiscreteRewards(minVal, maxVal)
    plotRegret(mm, shells, nIters, botWeights, optimalScore, "discrete")

    # Discrete feedback with noise
    stdNoise = [0.1,0.2]
    for std in stdNoise:
        mm = core.online.BotFeedbackOnlineOptimizer()
        mm.setUseDiscreteRewards(minVal,maxVal)
        mm.setNoise(std)
        plotRegret(mm, shells, nIters, botWeights, optimalScore, "std="+str(std) + " (discrete)")


    plt.xscale('log')
    plt.legend(fancybox=True,shadow=True)
    plt.xlabel('iteration')
    plt.ylabel('Average regret')
    # plt.title('Convergence of regret')
    plt.savefig('./plots/convergence_regret.png', bbox_inches='tight')
    plt.show()