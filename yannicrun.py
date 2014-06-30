import core.pml as pml , shells.emotionshell as emotionshell, shells.complexityshell as complexityshell
from core.reports import *

if __name__ == '__main__':
    mm = pml.ShellMixtureMaximizer()
    mm.configureFromFile("configs/main.default.config")

    #ss = stupidshell.StupidShell()
    #ss.configureFromFile("configs/stupid.default.config")
    es = emotionshell.EmotionSummationShell()
    cs = complexityshell.ComplexityShell()

    mm.addShell(es,0.5)
    mm.addShell(cs,0.5)

    selected = mm.run()

    reporters = [HtmlReporter(),KmlReporter()]
    
    createReports(mm,selected,reporters)
