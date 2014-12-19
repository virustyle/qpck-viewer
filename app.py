__author__ = 'ringo'

import sys
# from PyQt5 import QtGui
from PyQt4 import QtGui, QtCore
import pck
import re


class ImagesListModel(QtCore.QAbstractItemModel):

    def __init__(self):
        self._data = QtCore.QVariant('sdsd')
        self.rows = 0
        return super(ImagesListModel, self).__init__()

    def set_row_count(self, count):
        self.rows = 0

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 1

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.rows

    def index(self, row, column, QModelIndex_parent=None, *args, **kwargs):
        if row < self.rows:
            return self.createIndex(row, column)
        return QtCore.QModelIndex()

    def parent(self, QModelIndex=None):
        return QtCore.QModelIndex()

    def data(self, QModelIndex, int_role=None):
        if int_role == 0:
            return self._data

if len(sys.argv) > 1:
    ext = re.compile('PCK', 'i')
    pck_name = sys.argv[1]
    tab_name =

app = QtGui.QApplication(sys.argv)
top_window = QtGui.QWidget()
images_list = QtGui.QListView(top_window)
images_list.setFixedWidth(50)
images_list_model = ImagesListModel()
images_list.setModel(images_list_model)
top_window.show()
top_window.resize(400, 200)

sys.exit(app.exec_())
