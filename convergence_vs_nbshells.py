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
import timeit

if __name__ == '__main__':

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


    shells = [gh, bot, bow, ch, cs]#, em, co] 
    shells = [gh, co, cs, em, co, bot]#, em, co] 
    # shellNames = ['gc', 'gh', 'bot', 'bow', 'ch', 'cs', 'em', 'co']
    # assert (len(shells) == len(shellNames))
    nShells = len(shells)

    iterNeeded = []
    iterNeededStd = []
    nRuns = 5
    tol = 0.1

    start = timeit.default_timer()
    for i in range(0,nShells):
        iters = []
        for k in range(0,nRuns):
            mm = core.online.BotFeedbackOnlineOptimizer()
            mm.configureFromFile("configs/online.default.config")
            mm.setBotWeights(list(rand.random(i+1)))
            mm.setMaxIter(1000)
            mm.setAbsTerminationCriteria(tol)
            for j in range(0,i+1):
                mm.addShell(shells[j],1.) 

            selected = mm.run()
            iters.append(len(mm.resList)-1)
            res = np.array(mm.resList)
            # plt.plot(np.arange(0,len(mm.resList)), res, '-') 
            print "nShells=%d run=%d" %(i+1,k+1)
        iterNeeded.append(np.mean(iters))
        iterNeededStd.append(np.std(iters))

    # plt.yscale('log') 
    # plt.legend([str(i) for i in np.arange(1,nShells+1)])
    x = np.arange(1,nShells+1) 
    plt.errorbar(x, iterNeeded, yerr=iterNeededStd, marker="o")
    plt.title('Convergence vs #shells')
    plt.xlabel('#shells')
    plt.ylabel('#iterations until residual < 0.1')
    plt.savefig('./plots/convergence_vs_nb_shells.png', bbox_inches='tight')
    plt.show()
    print "iterNeeded",iterNeeded
    print "iterNeededStd",iterNeededStd

    stop = timeit.default_timer()
    print "program took ", stop-start