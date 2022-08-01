import io
import logging

import matplotlib
import matplotlib.image as mpimg
import matplotlib.pyplot as plt


class Plot:
    def getPlotPath(self, plt_obj):
        buffer = io.BytesIO()
        if isinstance(plt_obj, plt.Figure):
            plt_obj.savefig(buffer, format='png', bbox_inches='tight')
        elif isinstance(plt_obj, matplotlib.axes.Axes):
            plt_obj.get_figure().savefig(buffer, format='png', bbox_inches='tight')
        else:
            logging.error("Error: getPlot method must return an pyplot figure "
                          "or matplotlib Axes object")
        plt.close('all')
        return(buffer)


class Image:
    def getImagePath(self, img_obj):
        buffer = io.BytesIO()
        mpimg.imsave(buffer, img_obj)
        try:
            mpimg.imsave(buffer, img_obj)
        except Exception:
            logging.error("Error: getImage method must return an image object")
        return(buffer)
