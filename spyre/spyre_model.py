import io


class SpyreModel(object):

    title = ""

    # Will be used when there are more than one app in a site
    app_bar_html = None
    outputs = []
    inputs = []
    controls = []
    tabs = None
    spinnerFile = None
    templateVars = None
    prefix = '/'

    def getJsonData(self, params):
        """turns the DataFrame returned by getData into a dictionary

        arguments:
        the params passed used for table or d3 outputs are forwarded on to getData
        """
        try:
            return eval("self." + str(params['output_id']) + "(params)")
        except AttributeError:
            df = self.getData(params)
            if df is None:
                return None
            return df.to_dict(orient='records')

    def getData(self, params):
        """Override this function

        arguments:
        params (dict)

        returns:
        DataFrame
        """
        return eval("self." + str(params['output_id']) + "(params)")

    def getTable(self, params):
        """Used to create html table. Uses dataframe returned by getData by default
        override to return a different dataframe.

        arguments: params (dict)
        returns: html table
        """
        df = self.getData(params)
        if df is None:
            return None
        return df

    def getDownload(self, params):
        """Override this function

        arguments: params (dict)
        returns: path to file or buffer to be downloaded (string or buffer)
        """
        df = self.getData(params)
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, encoding='utf-8')
        filepath = buffer
        return filepath

    def storeUpload(self, file):
        """Override this function

        arguments: params (dict)
        returns: path to file or buffer to be downloaded (string or buffer)
        """
        pass

    def getPlot(self, params):
        """Override this function

        arguments:
        params (dict)

        returns:
        matplotlib.pyplot figure
        """
        try:
            return eval("self." + str(params['output_id']) + "(params)")
        except AttributeError:
            df = self.getData(params)
            if df is None:
                return None
            return df.plot()

    def getImage(self, params):
        """Override this function

        arguments: params (dict)
        returns: matplotlib.image (figure)
        """
        return eval("self." + str(params['output_id']) + "(params)")

    def getHTML(self, params):
        """Override this function

        arguments: params (dict)
        returns: html (string)
        """
        return eval("self." + str(params['output_id']) + "(params)")

    def noOutput(self, params):
        """Override this function
        A method for doing stuff that doesn't reququire an output (refreshing data,
            updating variables, etc.)

        arguments:
        params (dict)
        """
        return eval("self." + str(params['output_id']) + "(params)")

    def getD3(self):
        d3 = {}
        d3['css'] = ""
        d3['js'] = ""
        return d3

    def getCustomJS(self):
        """Override this function

        returns:
        string of javascript to insert on page load
        """
        return ""

    def getCustomCSS(self):
        """Override this function

        returns:
        string of css to insert on page load
        """
        return ""

    def getCustomHead(self):
        """Override this function

        returns:
        html to put in html header
        """
        return ""
