#!/usr/bin/python2
__author__ = 'ringo'

import sys
import os
from PyQt4 import QtGui, QtCore
import pck
import re
import argparse


class ImagesListModel(QtCore.QAbstractItemModel):

    def __init__(self):
        self._data = QtCore.QVariant('sdsd')
        self.rows = 3
        return super(ImagesListModel, self).__init__()

    def set_row_count(self, count):
        self.rows = 0

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.rows

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 1

    def index(self, row, column, QModelIndex_parent=None, *args, **kwargs):
        if column < self.rows:
            return self.createIndex(row, column)
        return QtCore.QModelIndex()

    def parent(self, QModelIndex=None):
        return QtCore.QModelIndex()

    def data(self, QModelIndex, int_role=None):
        if int_role == 0:
            return self._data

if len(sys.argv) > 1:
    parser = argparse.ArgumentParser()
    parser.add_argument('pck', help='path to the pck file to work on.')
    parser.add_argument('--tab', '-t', help='path to the index file.')
    parser.add_argument('--palette', '-p', help='path to thr palette file.')
    args = parser.parse_args()

    if not os.path.exists(args.pck):
        exit('File not found: ' + args.pck)

    if not args.palette:
        print('We have no palette. Ok. I\'ll deal with it.')

    if not args.tab:
        print('There\'s no index file given. So, I should find it by myself.')
        tab_file = args.pck[:-3] + 'tab'
        if not os.path.exists(tab_file):
            tab_file = args.pck[:-3] + 'TAB'
        if not os.path.exists(tab_file):
            tab_file = ''

app = QtGui.QApplication(sys.argv)
top_window = QtGui.QWidget()

image_preview = QtGui.QGraphicsView()
scene = QtGui.QGraphicsScene(image_preview)
scene_font = QtGui.QFont()
scene_font.setBold(True)
scene.addText('Empty', scene_font)

# image_preview.setAutoFillBackground(True)
print(image_preview.sizePolicy().verticalPolicy())
image_preview.setScene(scene)
image_preview.show()

images_list = QtGui.QListView()
images_list.setStyleSheet('background-color: black; color: lightgrey;')
images_list.setFlow(images_list.LeftToRight)
images_list.setFixedHeight(50)
images_list_model = ImagesListModel()
images_list.setModel(images_list_model)

layout = QtGui.QVBoxLayout(top_window)
layout.addChildWidget(image_preview)
layout.addChildWidget(images_list)
top_window.setLayout(layout)
top_window.show()
top_window.resize(400, 200)

sys.exit(app.exec_())
