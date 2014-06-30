import core.pml as pml,shells.geocoverageshell as geocoverageshell,shells.bagoftagsshell as bagoftagsshell, os, core.online, shells.emotionshell as emotionshell, core.demo, shells.bagofvisualwordsshell,shells.bagofwordsshell,shells.complexityshell,shells.contrastshell,shells.viewcountshell
import sys
from core.reports import *

if __name__ == '__main__':
    port = 8080
    if len(sys.argv) > 1:
        port = sys.argv[1]
    mm = core.demo.DemoOptimizer(port=port)
    mm.configureFromFile("configs/demo.default.config")

    es = emotionshell.EmotionSummationShell()
    mm.addShell(es)

    gc = geocoverageshell.GeoHotspotShell()
    gc.configureFromFile("configs/geohotspot.default.config")
    mm.addShell(gc)

    cmpls = shells.complexityshell.ComplexityShell()
    mm.addShell(cmpls)
    
    cntrs = shells.contrastshell.ContrastSummationShell()
    mm.addShell(cntrs)

    vcs = shells.viewcountshell.ViewCountShell()
    vcs.configureFromFile('configs/viewcountshell.default.config')
    mm.addShell(vcs)

    """
    bvws = shells.bagofvisualwordsshell.BagOfVisualWordsShell()
    bvws.configureFromFile("configs/bagofvisualwords.default.config")
    mm.addShell(bvws)

    bts = bagoftagsshell.BagOfTagsShell()
    bts.configureFromFile("configs/bagoftags.default.config")
    mm.addShell(bts)


    bws = shells.bagofwordsshell.BagOfWordsShell()
    bws.configureFromFile("configs/bagofwordsshell.default.config")
    mm.addShell(bws)
    """


    selected = mm.run()

    #reporters = [HtmlReporter()]

    #createReports(mm,selected,reporters)
