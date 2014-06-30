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

if __name__ == '__main__':
    mm = core.online.BotFeedbackOnlineOptimizer()
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

    mm.addShell(cs, 1)
    mm.addShell(gh, 1)
    # mm.addShell(gc,1)
    # mm.addShell(bot,1)
    # mm.addShell(bovw,1)
    mm.addShell(bow, 1)
    mm.addShell(vc, 1)
    # mm.addShell(ch,1)
    mm.addShell(em, 1)
    mm.addShell(co, 1)

    bot = [1, 1, 0, 0, 1, 1]

    mm.setBotWeights(bot)

    selected = mm.run()

    reporters = [HtmlReporter()]

    createReports(mm, selected, reporters)
