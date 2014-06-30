import core.pml as pml,shells.bagofvisualwordsshell as bvvs
from core.reports import *

if __name__ == '__main__':
    mm = pml.ShellMixtureMaximizer()
    mm.configureFromFile("configs/main.4l.config")

    ss = bvvs.BagOfVisualWordsShell()
    ss.configureFromFile("configs/bagofvisualwords.default.config")

    mm.addShell(ss,1.0)

    selected = mm.run()

    reporters = [HtmlReporter(),KmlReporter()]
    
    createReports(mm,selected,reporters)
