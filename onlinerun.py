
import core.pml as pml,shells.geocoverageshell as geocoverageshell,shells.bagoftagsshell as bagoftagsshell, os, core.online, shells.emotionshell as emotionshell
import core.pml as pml,shells.geocoverageshell as geocoverageshell,shells.bagoftagsshell as bagoftagsshell, os, core.online, shells.emotionshell as emotionshell, core.demo, shells.bagofvisualwordsshell,shells.bagofwordsshell,shells.complexityshell,shells.contrastshell,shells.viewcountshell
from core.reports import *

if __name__ == '__main__':
    port = 8080
    if len(sys.argv) > 1:
        port = sys.argv[1]
    mm = core.online.UserFeedbackOnlineOptimizer(port=port)
    mm.configureFromFile("configs/online.default.config")

    es = emotionshell.EmotionSummationShell()
    gc = geocoverageshell.GeoHotspotShell()
    gc.configureFromFile("configs/geohotspot.default.config")

    cmpls = shells.complexityshell.ComplexityShell()

    cntrs = shells.contrastshell.ContrastSummationShell()

    vcs = shells.viewcountshell.ViewCountShell()
    vcs.configureFromFile('configs/viewcountshell.default.config')

    '''
    bvws = shells.bagofvisualwordsshell.BagOfVisualWordsShell()
    bvws.configureFromFile("configs/bagofvisualwords.default.config")

    mm.addShell(bvws,0.2)
    '''
    mm.addShell(es,0.2)
    mm.addShell(gc,0.2)
    mm.addShell(cmpls,0.2)
    mm.addShell(cntrs,0.2)
    mm.addShell(vcs,0.2)

    selected = mm.run()

    #reporters = [HtmlReporter()]

