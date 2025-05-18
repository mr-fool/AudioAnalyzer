import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(self.fig)
        self.setParent(parent)
        plt.rcParams.update({
            'axes.facecolor': '#F0F0F0',
            'figure.facecolor': '#F0F0F0',
        })