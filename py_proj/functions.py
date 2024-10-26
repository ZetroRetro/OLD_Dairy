from datetime import date, timedelta
from pyqtgraph import AxisItem


def delta2date(today, delta):
    return str(date.fromisoformat(today) + timedelta(delta))


def date2delta(today, Date):
    return (date.fromisoformat(Date) - date.fromisoformat(today)).days


class DateAxisItem(AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [delta2date(str(date.today()), value) for value in values]

    def attachToPlotItem(self, plotItem):
        """Add this axis to the given PlotItem
        :param plotItem: (PlotItem)
        """
        self.setParentItem(plotItem)
        viewBox = plotItem.getViewBox()
        self.linkToView(viewBox)
        self._oldAxis = plotItem.axes[self.orientation]['item']
        self._oldAxis.hide()
        plotItem.axes[self.orientation]['item'] = self
        pos = plotItem.axes[self.orientation]['pos']
        plotItem.layout.addItem(self, *pos)
        self.setZValue(-1000)