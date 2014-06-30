import core.pml as pml , shells.emotionshell as emotionshell
from core.reports import *

if __name__ == '__main__':
    mm = pml.ShellMixtureMaximizer()
    mm.configureFromFile("configs/main.default.config")

    #ss = stupidshell.StupidShell()
    #ss.configureFromFile("configs/stupid.default.config")
    ss = emotionshell.EmotionSummationShell()

    mm.addShell(ss,1.0)

    selected = mm.run()

    reporters = [HtmlReporter(),KmlReporter()]
    
    createReports(mm,selected,reporters)
