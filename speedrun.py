import core.pml as pml,shells.geocoverageshell as geocoverageshell,shells.bagoftagsshell as bagoftagsshell, os, core.online, shells.emotionshell as emotionshell, core.demo, shells.bagofvisualwordsshell,shells.bagofwordsshell,shells.complexityshell,shells.contrastshell,shells.viewcountshell
from core.reports import *
import matplotlib.pyplot as plt
import numpy as np

def evaluateSpeed(shell,n=10):
    mm = pml.ShellMixtureMaximizer()
    mm.configureFromFile("configs/main.default.config")
    mm.addShell(shell,1.0)
    mm._budget = n
    selected = mm.run()
    scores = np.array([shell.evaluateNormalized(selected[:i+1]) for i in range(n)])
    plt.plot(np.arange(1,n+1),scores,'-o',label=shell.__class__.__name__)

if __name__ == '__main__':

    plt.figure()

    es = emotionshell.EmotionSummationShell()
    evaluateSpeed(es)

    gc = geocoverageshell.GeoHotspotShell()
    gc.configureFromFile("configs/geohotspot.default.config")
    evaluateSpeed(gc)

    cmpls = shells.complexityshell.ComplexityShell()
    evaluateSpeed(cmpls)
    
    cntrs = shells.contrastshell.ContrastSummationShell()
    evaluateSpeed(cntrs)

    vcs = shells.viewcountshell.ViewCountShell()
    vcs.configureFromFile('configs/viewcountshell.default.config')
    evaluateSpeed(vcs)

    """
    bts = bagoftagsshell.BagOfTagsShell()
    bts.configureFromFile("configs/bagoftags.default.config")
    evaluateSpeed(bts)

    bvws = shells.bagofvisualwordsshell.BagOfVisualWordsShell()
    bvws.configureFromFile("configs/bagofvisualwords.default.config")
    evaluateSpeed(bvws)

    bws = shells.bagofwordsshell.BagOfWordsShell()
    bws.configureFromFile("configs/bagofwordsshell.default.config")
    evaluateSpeed(bws)
    """

    #reporters = [HtmlReporter()]

    #createReports(mm,selected,reporters)

    plt.title("Normalized objective value for each shell individually")
    plt.xlabel('Budget')
    plt.ylabel('Normalized objective value')
    plt.ylim([0.0,1.0])
    plt.legend(loc=0)
    plt.draw()
    plt.show()
