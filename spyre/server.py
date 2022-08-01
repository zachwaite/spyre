import matplotlib

matplotlib.use('Agg')

import os
import os.path

import cherrypy
import jinja2
from cherrypy.lib.static import serve_file, serve_fileobj

from spyre.spyre_controller import SpyreController

# Settings
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

templateLoader = jinja2.FileSystemLoader(searchpath=ROOT_DIR)
templateEnv = jinja2.Environment(loader=templateLoader)


class Root(object):
    def __init__(self, base):
        self.base = base
        
    @cherrypy.expose
    def index(self, **args):
        return self.base._index(**args)

    @cherrypy.expose
    def plot(self, **args):
        cherrypy.response.headers['Content-Type'] = 'image/png'
        return self.base._plot(**args)

    @cherrypy.expose
    def image(self, **args):
        cherrypy.response.headers['Content-Type'] = 'image/jpg'
        return self.base._image(**args)

    @cherrypy.expose
    def data(self, **args):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return self.base._data(**args)

    @cherrypy.expose
    def table(self, **args):
        html = self.base._table(**args)
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return html

    @cherrypy.expose
    def html(self, **args):
        html = self.base._html(**args)
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return html

    @cherrypy.expose
    def download(self, **args):
        args = self.base.clean_args(args)
        filepath = self.base.getDownload(args)

        if type(filepath).__name__ == "str":
            return serve_file(filepath, "application/x-download", "attachment", name='data.csv')
        if type(filepath).__name__ == "instance":
            file_obj = serve_fileobj(
                filepath.getvalue(),
                "application/x-download",
                "attachment",
                name='data.csv'
            )
            return file_obj
        if type(filepath).__name__ == "StringIO":
            file_obj = serve_fileobj(
                filepath.getvalue().encode('utf-8'),
                "application/x-download",
                "attachment",
                name='data.csv'
            )
            return file_obj
        else:
            return "error downloading file. filepath must be string of buffer"

    @cherrypy.expose
    def upload(self, xfile):
        self.base._upload(xfile)

    @cherrypy.expose
    def no_output(self, **args):
        return self.base._no_output(**args)

    @cherrypy.expose
    def spinning_wheel(self, **args):
        cherrypy.response.headers['Content-Type'] = 'image/gif'
        return self.base._spinning_wheel(**args)


class App(object):
    def __init__(self, model):
        self.model = model

    def launch(self, host="local", port=8080, prefix='/', config=None):
        self.prefix = prefix
        webapp = self.getRoot()
        if host != "local":
            cherrypy.server.socket_host = '0.0.0.0'
        cherrypy.server.socket_port = port
        cherrypy.tree.mount(webapp, prefix)
        cherrypy.quickstart(webapp, config=config)

    def getRoot(self):
        controller = SpyreController(
            templateVars=self.model.templateVars,
            title=self.model.title,
            inputs=self.model.inputs,
            outputs=self.model.outputs,
            controls=self.model.controls,
            tabs=self.model.tabs,
            spinnerFile=self.model.spinnerFile,
            getJsonDataFunction=self.model.getJsonData,
            getDataFunction=self.model.getData,
            getTableFunction=self.model.getTable,
            getPlotFunction=self.model.getPlot,
            getImageFunction=self.model.getImage,
            getD3Function=self.model.getD3,
            getCustomJSFunction=self.model.getCustomJS,
            getCustomCSSFunction=self.model.getCustomCSS,
            getCustomHeadFunction=self.model.getCustomHead,
            getHTMLFunction=self.model.getHTML,
            getDownloadFunction=self.model.getDownload,
            noOutputFunction=self.model.noOutput,
            storeUploadFunction=self.model.storeUpload,
            prefix=self.model.prefix
        )
        webapp = Root(controller)
        return webapp

