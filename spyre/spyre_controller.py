import matplotlib

matplotlib.use('Agg')

import copy
import json

import jinja2

from spyre import View, model

INCLUDE_DF_INDEX = False

class SpyreController(object):
    def __init__(
        self,
        templateVars=None,
        title="",
        inputs=[],
        outputs=[],
        controls=[],
        tabs=None,
        spinnerFile=None,
        getJsonDataFunction=None,
        getDataFunction=None,
        getTableFunction=None,
        getPlotFunction=None,
        getImageFunction=None,
        getD3Function=None,
        getCustomCSSFunction=None,
        getCustomJSFunction=None,
        getCustomHeadFunction=None,
        getHTMLFunction=None,
        getDownloadFunction=None,
        noOutputFunction=None,
        storeUploadFunction=None,
        prefix='/'
    ):

        # populate template dictionary for creating input,controler, and output HTML and javascript
        if templateVars is not None:
            self.templateVars = templateVars
        else:
            self.templateVars = {}
            self.templateVars['title'] = title
            if prefix[-1] == '/':
                self.templateVars['prefix'] = prefix[:-1]
            else:
                self.templateVars['prefix'] = prefix
            # necessary to ensure that spyre apps prior to version 0.2.0 still work
            for input in inputs:
                if 'input_type' in input:
                    input['type'] = input['input_type']
                if 'variable_name' in input:
                    input['key'] = input['variable_name']
                if 'linked_variable_name' in input:
                    input['linked_key'] = input['linked_variable_name']
                if 'linked_variable_type' in input:
                    input['linked_type'] = input['linked_variable_type']
            self.templateVars['inputs'] = inputs
            for control in controls:
                if 'control_type' in control:
                    control['type'] = control['control_type']
                if 'control_id' in control:
                    control['id'] = control['control_id']
            self.templateVars['controls'] = controls
            for output in outputs:
                if 'output_type' in output:
                    output['type'] = output['output_type']
                if 'output_id' in output:
                    output['id'] = output['output_id']
            self.templateVars['outputs'] = outputs
            if tabs is not None:
                self.templateVars['tabs'] = tabs
            if spinnerFile is not None:
                self.templateVars['spinnerFile'] = spinnerFile
        self.defaultTemplateVars = self.templateVars

        self.getJsonData = getJsonDataFunction
        self.getData = getDataFunction
        self.getTable = getTableFunction
        self.getPlot = getPlotFunction
        self.getImage = getImageFunction
        self.getD3 = getD3Function
        self.getCustomJS = getCustomJSFunction
        self.getCustomCSS = getCustomCSSFunction
        self.getCustomHead = getCustomHeadFunction
        self.getHTML = getHTMLFunction
        self.noOutput = noOutputFunction
        self.getDownload = getDownloadFunction
        self.storeUpload = storeUploadFunction
        d3 = self.getD3()
        custom_js = self.getCustomJS()
        custom_css = self.getCustomCSS()
        custom_head = self.getCustomHead()

        self.templateVars['d3js'] = d3['js']
        self.templateVars['d3css'] = d3['css']
        self.templateVars['custom_js'] = custom_js
        self.templateVars['custom_css'] = custom_css
        self.templateVars['custom_head'] = custom_head

        v = View.View()
        self.templateVars['document_ready_js'] = ""
        self.templateVars['js'] = v.getJS()
        self.templateVars['css'] = v.getCSS()

        self.upload_file = None

    def clean_args(self, args):
        for k, v in args.items():
            # turn checkbox group string into a list
            if v.rfind("__list__") == 0:
                tmp = v.split(',')
                if len(tmp) > 1:
                    args[k] = tmp[1:]
                else:
                    args[k] = []
            # convert to a number
            if v.rfind("__float__") == 0:
                args[k] = float(v[9:])
        return args


    def use_custom_input_values(self, args):
        input_registration = {}
        index = 0
        for input in self.templateVars['inputs']:
            input_key = input['key']
            # register inputs to be so we can look them up by their variable name later
            if 'action_id' in input:
                input_registration[input_key] = {
                    "type": input['type'],
                    "action_id": input['action_id']
                }
            else:
                input_registration[input_key] = {
                    "type": input['type'],
                    "action_id": None
                }

            if input_key in args.keys():
                # use value from request
                input_value = args[input_key]
            elif 'value' in input:
                # use value from template
                input_value = input['value']
            else:
                # no value specified
                index += 1
                continue

            # use the params passed in with the url switch out the default input values
            if input['type'] in ['text', 'slider', 'searchbox']:
                self.templateVars['inputs'][index]['value'] = input_value
            if input['type'] in ['radiobuttons', 'dropdown']:
                for option in input['options']:
                    option['checked'] = (option['value'] == input_value)
            if input['type'] in ['checkboxgroup', 'multiple']:
                index2 = 0
                for option in input['options']:
                    if option['value'] in input_value:
                        self.templateVars['inputs'][index]['options'][index2]['checked'] = True
                    else:
                        self.templateVars['inputs'][index]['options'][index2]['checked'] = False
                    index2 += 1
            index += 1

    def _index(self, **args):
        # create a deepcopy so other people's changes aren't cached
        self.templateVars = copy.deepcopy(self.defaultTemplateVars)
        clean_args = self.clean_args(args)
        self.use_custom_input_values(clean_args)

        v = View.View()
        template = jinja2.Template(v.getHTML())
        return template.render(self.templateVars)

    def _plot(self, **args):
        args = self.clean_args(args)
        p = self.getPlot(args)
        if p is None:
            return None
        d = model.Plot()
        buffer = d.getPlotPath(p)
        return buffer.getvalue()

    def _image(self, **args):
        args = self.clean_args(args)
        img = self.getImage(args)
        if img is None:
            return None
        d = model.Image()
        buffer = d.getImagePath(img)
        return buffer.getvalue()

    def _data(self, **args):
        args = self.clean_args(args)
        data = self.getJsonData(args)
        if data is None:
            return None
        return json.dumps({'data': data, 'args': args}).encode('utf8')

    def _table(self, **args):
        args = self.clean_args(args)
        df = self.getTable(args)
        if df is None:
            return ""
        html = df.to_html(index=INCLUDE_DF_INDEX, escape=False)
        i = 0
        for col in df.columns:
            html = html.replace(
                '<th>{}'.format(col),
                '<th><a onclick="sortTable({},"table0");"><b>{}</b></a>'.format(i, col)
            )
            i += 1
        html = html.replace(
            'border="1" class="dataframe"',
            'class="sortable" id="sortable"'
        )
        return html.replace('style="text-align: right;"', '')

    def _html(self, **args):
        args = self.clean_args(args)
        html = self.getHTML(args)
        if html is None:
            return ""
        else:
            return html

    def _download(self, **args):
        pass

    def _upload(self, xfile):
        self.storeUpload(xfile.file)
        
    def _no_output(self, **args):
        args = self.clean_args(args)
        self.noOutput(args)
        return ''

    def _spinning_wheel(self, **args):
        v = View.View()
        spinnerFile = self.templateVars.get('spinnerFile')
        buffer = v.getSpinningWheel(spinnerFile)
        return buffer.getvalue()

