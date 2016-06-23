import matplotlib

matplotlib.use('TkAgg')
import sys

if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from copy import copy

__author__ = "Thomas Schweich"


class GraphWindow(Tk.Frame):
    def __init__(self, graph, *args, **kwargs):
        """A frame object who's open() method creates a Tk.Toplevel (new window) with its contents"""
        Tk.Frame.__init__(self, *args, **kwargs)
        self.widgets = {}
        self.graph = graph
        self.newGraph = None
        self.newSubPlot = None
        self.root = self.graph.root
        self.window = None
        self.radioVar = Tk.IntVar()
        self.fitBox = None
        self.sliceBox = None
        self.addBox = None
        self.multBox = None
        self.canvas = None
        self.f = None
        self.rbFrame = None
        self.optionsFrame = None
        self.pack()
        self.isOpen = False

    def open(self):
        """Opens a graph window only if there isn't already one open for this GraphWindow

        Thus only one window per Graph can be open using this method (assuming Graphs only have one GraphWindow)"""
        if not self.isOpen:
            self.window = Tk.Toplevel(self)
            self.window.wm_title(str(self.graph.title))
            self.window.protocol("WM_DELETE_WINDOW", self.close)
            self.f = Figure(figsize=(2, 1), dpi=150)
            graphSubPlot = self.f.add_subplot(121)
            self.graph.plot(subplot=graphSubPlot)
            self.newSubPlot = self.f.add_subplot(122)
            self.newGraph = copy(self.graph)
            self.newGraph.setTitle("Transformation of " + str(self.graph.title))
            self.newGraph.plot(subplot=self.newSubPlot)
            self.canvas = FigureCanvasTkAgg(self.f, self.window)
            self.canvas.show()
            self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
            self.optionsFrame = Tk.Frame(self.window)
            self.optionsFrame.pack(side=Tk.BOTTOM, fill=Tk.BOTH)
            self.rbFrame = Tk.Frame(self.window)
            self.rbFrame.pack(side=Tk.BOTTOM, fill=Tk.BOTH)
            self.populate()
            self.refreshOptions()

    def close(self):
        """Destroys the window, sets the GraphWindows's Toplevel instance to None"""
        del self.widgets
        self.widgets = {}
        self.window.destroy()
        # self.pack_forget()
        self.isOpen = False

    def populate(self):
        """Adds all widgets to the window in their proper frames, with proper cascading"""
        # FIT
        self.fitBox = self.addWidget(Tk.Radiobutton, command=self.refreshOptions, text="Fit Options",
                                     variable=self.radioVar, value=0)
        self.fitBox.val = 0
        self.addWidget(Tk.Button, parent=self.fitBox, command=self.quarticFit, text="Quartic Fit")
        self.addWidget(Tk.Button, parent=self.fitBox, command=self.cubicFit, text="Cubic Fit")
        self.addWidget(Tk.Button, parent=self.fitBox, command=self.quadraticFit, text="Quadratic Fit")
        self.addWidget(Tk.Button, parent=self.fitBox, command=self.linearFit, text="Linear Fit")

        # SLICE
        self.sliceBox = self.addWidget(Tk.Radiobutton, command=self.refreshOptions, text="Slice Options",
                                       variable=self.radioVar, value=1)
        self.sliceBox.val = 1
        sliceVar = Tk.IntVar()
        self.addWidget(Tk.Radiobutton, parent=self.sliceBox,
                       text="By index (from 0 to " + str(len(self.graph.getRawData()[0])) +
                            ")", variable=sliceVar, value=0)
        self.addWidget(Tk.Radiobutton, parent=self.sliceBox,
                       text="By nearest x value (from " + str(self.graph.getRawData()[0][0]) + " to " + str(
                           self.graph.getRawData()[0][len(self.graph.getRawData()[0]) - 1]) + ")",
                       variable=sliceVar, value=1)

        start = self.addWidget(Tk.Entry, parent=self.sliceBox)
        start.insert(0, "Start")
        end = self.addWidget(Tk.Entry, parent=self.sliceBox)
        end.insert(0, "End")
        self.addWidget(Tk.Button, parent=self.sliceBox, command=lambda: self.addSlice(sliceVar, start.get(), end.get()),
                       text="Preview")

        # ADD
        self.addBox = self.addWidget(Tk.Radiobutton, command=self.refreshOptions,
                                     text="Add/Subtract Graphs", variable=self.radioVar, value=2)
        self.addBox.val = 2

        # MULTIPLY
        self.multBox = self.addWidget(Tk.Radiobutton, command=self.refreshOptions,
                                      text="Multiply/Divide Graphs", variable=self.radioVar, value=3)
        self.multBox.val = 3

    def refreshOptions(self):
        """Refreshes the displayed options based on the currently selected Radiobutton"""
        for k, v in self.widgets.iteritems():
            for widget in v:
                if widget.winfo_exists():
                    widget.pack_forget()
            # Main Radiobuttons
            try:
                if k.val == self.radioVar.get():
                    for widget in v:
                        widget.pack(side=Tk.TOP)
            except AttributeError:
                pass

    def addWidget(self, widgetType, parent=None, *args, **kwargs):
        """Adds a widget to the window.

        If a parent is specified, it will be placed in the widgets widgets dict under its parent.
        If no parent is specified, it will get its own entry in widgets, and immediately be packed.
        If a parent is specified which doesn't already have its own entry, one will be created for it. Thus, cascading
        trees of widgets can be created. A widget may be both a parent and a child.
        All values are added in lists so that a parent widget may have more than one child.
        """
        if not parent:
            wid = widgetType(self.rbFrame, *args, **kwargs)
            self.widgets[wid] = []
            wid.pack(expand=True, side=Tk.LEFT)
        else:
            wid = widgetType(self.optionsFrame, *args, **kwargs)
            if self.widgets[parent] in self.widgets.values():
                self.widgets[parent].append(wid)
            else:
                self.widgets[parent] = [wid]
        print self.widgets[wid if not parent else parent]
        return wid

    def plotWithReference(self, graph):
        """Plots the graph while maintaining a copy of the original graph on the same axes"""
        self.f.delaxes(self.newSubPlot)
        self.newSubPlot = self.f.add_subplot(122)
        referenceGraph = copy(self.graph)
        self.newGraph = graph
        referenceGraph.plot(subplot=self.newSubPlot)
        self.newGraph.plot(subplot=self.newSubPlot)
        self.canvas.show()

    def plotAlone(self, graph):
        """Replaces the plot of the original graph in the new graph window with the graph specified"""
        self.f.delaxes(self.newSubPlot)
        self.newSubPlot = self.f.add_subplot(122)
        self.newGraph = graph
        self.newGraph.plot(subplot=self.newSubPlot)
        self.canvas.show()

    def quarticFit(self):
        self.plotWithReference(self.graph.getCurveFit(
            fitFunction=lambda x, a, b, c, d, e: a * x ** 4 + b * x ** 3 + c * x ** 2 + d * x + e))

    def cubicFit(self):
        self.plotWithReference(
            self.graph.getCurveFit(fitFunction=lambda x, a, b, c, d: a * x ** 3 + b * x ** 2 + c * x + d))

    def quadraticFit(self):
        self.plotWithReference(self.graph.getCurveFit(fitFunction=lambda x, a, b, c: a * x ** 2 + b * x + c))

    def linearFit(self):
        self.plotWithReference(self.graph.getCurveFit(fitFunction=lambda x, a, b: a * x + b))

    def addSlice(self, tkVar, begin, end):
        if tkVar.get() == 0:
            self.plotAlone(self.graph.slice(begin=float(begin), end=float(end)))
        elif tkVar.get() == 1:
            results = np.searchsorted(self.graph.getRawData()[0], np.array([np.float64(begin), np.float64(end)]))
            self.plotAlone(self.graph.slice(begin=results[0], end=results[1]))
