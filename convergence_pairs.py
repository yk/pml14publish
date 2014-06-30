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


    # Evaluate convergence for pairs viewcount_shell vs all others 


    # -------------------------------------------------------------
    # Params
    # -------------------------------------------------------------

    shells = [gc, gh, bot, bow, ch, cs, em, co] 
    shellNames = ['GeoUni', 'GeoHotspot', 'Bag-Of-Tags', 'Bag-Of-Words', 'ContrastHotspot', 'ContrastSum', 'Emotion', 'Complexity']
    assert (len(shells) == len(shellNames))
    nShells = len(shells)

    botWeights = [0.3, 0.7] # fixed bot weights

    # -------------------------------------------------------------

    colormap = plt.cm.gist_ncar
    plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, nShells)])

    # Run for all pairs with fixed weights
    for i in range(0,nShells):
        mm = core.online.BotFeedbackOnlineOptimizer()
        mm.configureFromFile("configs/online.default.config")
        mm.setBotWeights(botWeights)
        mm.setMaxIter(50)
        mm.addShell(vc, 1.)
        mm.addShell(shells[i], 1.)

        selected = mm.run()
        res = np.array(mm.resList)
        plt.plot(np.arange(0,len(mm.resList)), res, '-') 

    plt.title('Convergence for different shell types')
    plt.yscale('log')
    plt.ylabel('residual')
    plt.xlabel('iteration')
    plt.legend(shellNames, ncol=2, fancybox=True, shadow=True)
    plt.savefig('./plots/convergence_pairs.png', bbox_inches='tight')
    plt.show()