import core.pml as pml
import shells.geocoverageshell as geocoverageshell
import shells.bagoftagsshell as bagoftagsshell
import shells.bagofvisualwordsshell as bagofvisualwordsshell
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

def print_convergence_table(res):
    nIter = res.shape[0]-1
    convTab = np.zeros((nIter,3))
    convTab[:,0] = np.arange(1,nIter+1) 
    convTab[:,1] = res[1:]
    convTab[:,2] = res[1:] / res[0:-1]
    print '\n\n{:<5s} {:<10s} {:<10s}'.format(*["Iter", "residual", "rate"])
    print " \n".join(['{:<5.0f} {:<10.3f} {:<10.3f}'.format(*line) for line in convTab]) 

if __name__ == '__main__':
    # mm = core.online.BotFeedbackOnlineOptimizer()
    mm = pml.ShellMixtureMaximizer()
    # mm.configureFromFile("configs/main.default.config")
    mm.configureFromFile("configs/online.default.config")

    gc = geocoverageshell.GeoUniformShell()
    gc.configureFromFile("configs/geocoverage.default.config")

    gh = geocoverageshell.GeoHotspotShell()
    gh.configureFromFile("configs/geohotspot.default.config")

    bot = bagoftagsshell.BagOfTagsShell()
    bot.configureFromFile("configs/bagoftags.default.config")

    bovw = bagofvisualwordsshell.BagOfVisualWordsShell()
    bovw.configureFromFile("configs/bagofvisualwords.default.config")

    bow = bagofwordsshell.BagOfWordsShell()
    bow.configureFromFile("configs/bagofwordsshell.default.config")

    vc = viewcountshell.ViewCountShell()
    vc.configureFromFile("configs/viewcountshell.default.config")

    ch = contrastshell.ContrastHotspotShell()

    cs = contrastshell.ContrastSummationShell()

    em = emotionshell.EmotionSummationShell()

    co = complexityshell.ComplexityShell()

    # mm.addShell(cs, 1)
    # mm.addShell(gh, 1)
    # mm.addShell(gc,1)
    # mm.addShell(bot,1)
    mm.addShell(bovw,1)
    # mm.addShell(bow, 1)
    # mm.addShell(vc, 1)
    # mm.addShell(ch,1)
    # mm.addShell(em, 1)
    # mm.addShell(co, 1)

    # Evaluate noise influence
    nRuns = 4
    nIter = 50
    nShells = len(mm.shells)
    bot = list(rand.random(nShells))
    # mm.setBotWeights(bot)
    # mm.setMaxIter(nIter)

    # Run once without noise
    selected = mm.run()
    # res = np.array(mm.resList)
    # plt.plot(np.arange(0,len(mm.resList)), res, 'o-') 

    reporters = [HtmlReporter()]
    createReports(mm, selected, reporters)

    # Run with noise
    # stdNoise = [0.001, 0.01, 0.1]
    # mm.setUseDiscreteRewards(True, 1,5)
    # for i in range(0,len(stdNoise)):
    #     mm.setNoise(stdNoise[i])

    #     selected = mm.run()
    #     plt.plot(np.arange(0,len(mm.resList)), res, '-') 
    #     # print_convergence_table(res)

    plt.yscale('log')
    plt.legend(['no Noise', 'std=0.001', 'std=0.01', 'std=0.1'])
    # plt.show()

    # nRuns = 5
    # nIter = 20 
    # nShells = len(mm.shells)
    # bot = list(rand.random(nShells))
    # stdNoise = [0]
    # for i in range(0,nRuns):
    #     mm.setBotWeights(bot)
    #     mm.setMaxIter(nIter)
    #         mm.setNoise(0.1)

    #     selected = mm.run()
    #     res = np.array(mm.resList)
    #     plt.plot(np.arange(0,len(mm.resList)), res, 'o-') 
    #     # print_convergence_table(res)

    # plt.yscale('log')
    # plt.show()

    # reporters = [HtmlReporter()]
    # createReports(mm, selected, reporters)