import ConfigParser

class Configurable(object):
    def configTypes(self):
        return dict()

    def configure(self,**kwargs):
        types = self.configTypes()
        for k,v in kwargs.iteritems():
            t = types[k] if k in types else str
            self.__dict__["_%s"%k] = t(v)

    def configureFromFile(self,filename,section="Configuration"):
        config = ConfigParser.ConfigParser()
        config.optionxform = str
        config.read(filename)
        if config.has_section(section):
            configitems = dict(config.items(section))
            self.configure(**configitems)
