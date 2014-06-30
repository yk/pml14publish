import numpy as np
import pml,jinja2,os,cgi,webbrowser,itertools,logging,json
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

class ServerRequestHandler(BaseHTTPRequestHandler):

    def sendResponse(self,results):
        loader = jinja2.FileSystemLoader('core/templates')
        env = jinja2.Environment(loader=loader)
        env.globals['include_file'] = lambda name: jinja2.Markup(loader.get_source(env,name)[0])
        env.globals['zip'] = zip
        template = env.get_template('demo.template')

        shells = [dict(name=shell.__class__.__name__,weight=weight) for shell,weight in zip(ServerRequestHandler.maximizer.shells,ServerRequestHandler.maximizer.weights)]
        
        shellscores = [[shell.evaluateNormalized(result) for shell in ServerRequestHandler.maximizer.shells] for result in results]

        notSelected = [list(set(ServerRequestHandler.maximizer.data) - set(result)) for result in results]

        data = dict(results=results,shellscores=shellscores,shells=shells,notSelected=notSelected,json=json,os=os)

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(template.render(data))

    def do_GET(self):
        if self.path.startswith("/img/"):
            with open(self.path[5:]) as f:
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(f.read())

        if not self.path == '/': return
        #results = ServerRequestHandler.maximizer.maximize()
        results = []
        self.sendResponse(results)

    def do_POST(self):
        if not self.path == '/': return
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={"REQUEST_METHOD": "POST"}
        )

        submitted = dict((item.name, float(item.value)) for item in form.list)
        totalWeight = np.sum(submitted.values())
        if totalWeight > 0:
            for key,val in submitted.iteritems():
                ServerRequestHandler.maximizer.weights[int(key)] = val/totalWeight
        results = [ServerRequestHandler.maximizer.maximize()]
        print results
        self.sendResponse(results)


class DemoOptimizer(pml.ShellMixtureMaximizer):
    def __init__(self,port=8080,**kwargs):
        super(DemoOptimizer,self).__init__(**kwargs)
        self.port = port
        ServerRequestHandler.maximizer = self
        self.server_ = HTTPServer(('',self.port),ServerRequestHandler)

    def configTypes(self):
        types = super(DemoOptimizer,self).configTypes()
        types['numsolutions']=int
        return types

    def maximize(self):
        return super(DemoOptimizer,self)._maximize()

    def _maximize(self):
        print 'starting server'
        webbrowser.open("http://localhost:" + str(self.port))
        try:
            self.server_.serve_forever()
        except KeyboardInterrupt:
            self.server_.socket.close()
            return []

