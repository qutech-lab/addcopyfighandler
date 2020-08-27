# -*- coding: utf-8 -*-
"""
Monkey-patch plt.figure() to support Ctrl+C for copying to clipboard as an image

@author: Josh Burnett, Sylvain Finot
Modified from code found on Stack Exchange:
    https://stackoverflow.com/questions/31607458/how-to-add-clipboard-support-to-matplotlib-figures
    https://stackoverflow.com/questions/34322132/copy-image-to-clipboard-in-python3

"""


import matplotlib.pyplot as plt
from win32gui import GetWindowText, GetForegroundWindow
import win32clipboard
import io

__version__ = (2, 1, 0)
oldfig = plt.figure


def copyfig(fig=None, *args, **kwargs):
    """
    Parameters
    ----------
    fig : matplotlib figure, optional
        if None, get the figure that has UI focus
    *args : arguments that are passed to savefig
    
    **kwargs : keywords arguments that are passed to savefig

    Raises
    ------
    ValueError
        If the desired format is not supported.
        
    AttributeError
        If no figure is found

    """
    #By digging into windows API
    format_dict = {"png":49375,"svg":49531,"jpg":49374,"jpeg":49374}
    
    #if no format is passed to savefig get the default one
    format = kwargs.get('format', plt.rcParams["savefig.format"])
    format = format.lower()
    
    if not format in format_dict:
        raise ValueError(f"Format {format} is not supported "\
                         f"(supported formats: {', '.join(list(format_dict.keys()))})")
    
    if fig is None:
        # find the figure window that has UI focus right now (not necessarily the same as plt.gcf())
        fig_window_text = GetWindowText(GetForegroundWindow())
        for i in plt.get_fignums():
            if plt.figure(i).canvas.get_window_title() == fig_window_text:
                fig = plt.figure(i)
                break
                
    if fig is None:
        raise AttributeError("No figure found !")
    
    with BytesIO() as buf:
        fig.savefig(buf, *args, **kwargs)
        data = buf.getvalue()
    
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(format_dict[format],data)
    win32clipboard.CloseClipboard()


def newfig(*args, **kwargs):
    fig = oldfig(*args, **kwargs)

    def clipboard_handler(event):
        if event.key == 'ctrl+c':
            copyfig()

    fig.canvas.mpl_connect('key_press_event', clipboard_handler)
    return fig


plt.figure = newfig
