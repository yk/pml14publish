import core.pml as pml, shells.geocoverageshell as geocoverageshell
from core.reports import *
import numpy as np

if __name__ == '__main__':
    mm = pml.ShellMixtureMaximizer()
    mm.configureFromFile("configs/main.geocoverage_test.config")

    for std in np.logspace(-2, 1, 4):
    	gc = geocoverageshell.GeoCoverageShell()
    	gc.configureFromFile("configs/geocoverage.default.config")
    	gc._std = std

    	mm.addShell(gc, 1.0)
    	selected = mm.run()

    	reportName = "geocoverage_std=" + str(std)
    	createReports(mm,selected,[HtmlReporter(),KmlReporter()], reportName)

    createReports(mm,mm.data,[HtmlReporter(),KmlReporter()], "takeAll")
