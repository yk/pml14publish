import markup,os,core.pmlutil,webbrowser,simplekml,time,logging,jinja2
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class Reporter(core.pmlutil.Configurable):
    def report(self,maximizer,selected,reportPath):
        pass

class HtmlReporter(Reporter):
    def configTypes(self):
        return dict(openBrowser=int) 

    def report(self,maximizer,selected,reportPath):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader('core/templates'))
        template = env.get_template('html.template')

        data = dict(selected=selected,notSelected=list(set(maximizer.data)-set(selected)),os=os)

        fileName = os.path.join(reportPath,"report.html")
        with open(fileName,'w') as f:
            f.write(template.render(data))
        if self._openBrowser:
            webbrowser.open("file://"+os.path.abspath(fileName))

class KmlReporter(Reporter):
    def configTypes(self):
        return dict(includeImages=int,iconScale=float,tagTitles=int)

    def report(self,maximizer,selected,reportPath):
        kml = simplekml.Kml()
        
        notSelected = list(set(maximizer.getData())-set(selected))
        
        for img in notSelected:
            if 'location' in img.meta() and 'longitude' in img.meta()['location']:
                longitude = img.meta()['location']['longitude']
                latitude = img.meta()['location']['latitude']
                pnt = kml.newpoint(name=str(img.meta()['id']), coords=[(longitude, latitude)])
                pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png'
            else:
                logging.warn('No position information for %s' % img.meta()['id'])

        for img in selected:
            if 'location' in img.meta() and 'longitude' in img.meta()['location']:
                longitude = img.meta()['location']['longitude']
                latitude = img.meta()['location']['latitude']
                pnt = kml.newpoint(name=str(img.meta()['id']), coords=[(longitude, latitude)])

                if 'tags' in img.meta():
                    tags = ",".join([tag['text'] for tag in img.meta()['tags']])

                    if self._tagTitles:
                        pnt.name = tags
                        pnt.description = img.meta()['id']
                    else:
                        pnt.description = tags
                else:
                    loggin.warn('No tag information for %s' % img.meta()['id'])

                if self._includeImages:
                    pnt.style.iconstyle.scale = self._iconScale
                    pnt.style.iconstyle.icon.href = os.path.abspath(img.imageFilePath)
            else:
                logging.warn('No position information for %s' % img.meta()['id'])

        kml.save(os.path.join(reportPath,'report.kml'))

defaultReporters = [HtmlReporter()]

def createReports(maximizer,selected,reporters=defaultReporters,reportName=None,reportDirPath="reports",configFileName="configs/reporters.default.config"):
    if not reporters:
        return
    if not reportName:
        reportName = str(int(time.time()))
    folder = os.path.join(reportDirPath,reportName)
    if not os.path.isdir(folder):
        os.makedirs(folder)

    logging.info("Creating reports")
    for reporter in reporters:
        if configFileName:
            reporter.configureFromFile(configFileName,section=reporter.__class__.__name__)
        reporter.report(maximizer,selected,folder)
