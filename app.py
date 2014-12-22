#!/usr/bin/python2
__author__ = 'ringo'

import sys
import os
import cStringIO
import argparse
from PyQt4 import QtGui, QtCore

import pck


class PCKLoader(QtCore.QObject):
    loaded = QtCore.pyqtSignal()
    images = []
    files = []
    #
    # def __init__(self, parent=None):
    # super(PCKLoader, self).__init__()

    def set_files(self, pck_filename, tab_filename, palette_filename):
        self.files = [pck_filename, tab_filename, palette_filename]

    # @QtCore.pyqtSlot()
    def load(self):
        self.images = pck.PCK(self.files[0], self.files[1], self.files[2]).images
        self.loaded.emit()


class ImagesListModel(QtCore.QAbstractItemModel):
    def __init__(self):
        super(ImagesListModel, self).__init__()
        self._data = [x for x in range(10)]
        self.images = 0

    def set_images_count(self, count):
        self.images = count
        # self.emit(QtCore.SIGNAL('dataChanged()'))
        # noinspection PyUnresolvedReferences
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(count, 0))

    # noinspection PyPep8Naming
    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 1

    # noinspection PyPep8Naming
    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.images

    # noinspection PyPep8Naming
    def index(self, row, column, QModelIndex_parent=None, *args, **kwargs):
        if row < self.images:
            return self.createIndex(row, column)
        return QtCore.QModelIndex()

    # noinspection PyPep8Naming
    def parent(self, QModelIndex=None):
        return QtCore.QModelIndex()

    def data(self, idx, int_role=None):
        if int_role in [0]:
            return idx.row()


class MainWindow(QtGui.QWidget):
    load = QtCore.pyqtSignal()
    images_list_model = ImagesListModel()
    scene = None
    status_bar = None
    images = []
    zoom_factor = 1

    def __init__(self):
        super(MainWindow, self).__init__()
        self.image_preview = QtGui.QGraphicsView()
        self.loader = PCKLoader()
        self.thread = QtCore.QThread()
        self.setup_ui()
        self.zoom_factor = 1

    def setup_ui(self):
        self.scene = QtGui.QGraphicsScene(self)
        self.scene.addText('Empty')
        self.image_preview.setScene(self.scene)
        self.image_preview.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.lightGray, QtCore.Qt.SolidPattern))
        self.image_preview.show()

        main_menu = QtGui.QMenuBar(self)
        menu_view = main_menu.addMenu('&View')

        action_zoom_in = QtGui.QAction('Zoom in', self)
        action_zoom_in.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Plus))
        self.connect(action_zoom_in, QtCore.SIGNAL('triggered()'), self.zoom_in)

        action_zoom_out = QtGui.QAction('Zoom out', self)
        action_zoom_out.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Minus))
        self.connect(action_zoom_out, QtCore.SIGNAL('triggered()'), self.zoom_out)

        action_zoom_reset = QtGui.QAction('Zoom reset', self)
        action_zoom_reset.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_0))
        self.connect(action_zoom_reset, QtCore.SIGNAL('triggered()'), self.zoom_reset)

        menu_view.addAction(action_zoom_in)
        menu_view.addAction(action_zoom_out)
        menu_view.addAction(action_zoom_reset)

        images_list = QtGui.QListView()
        images_list.setStyleSheet('background-color: black; color: lightgrey;')
        images_list.setFlow(images_list.LeftToRight)
        images_list.setFixedHeight(50)
        images_list.setModel(self.images_list_model)
        images_list.selectionModel().selectionChanged.connect(self.selection_changed)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.image_preview)
        layout.addWidget(images_list)

        # self.status_bar = QtGui.QStatusBar(self)
        # self.status_bar.showMessage('Ja-ja!')
        # self.status_bar.show()

        self.setWindowTitle('PCK viewer')
        self.setContentsMargins(0, 11, 0, 0)
        self.setLayout(layout)
        self.resize(400, 200)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def selection_changed(self, sel):
        if sel and hasattr(sel, 'indexes') and len(sel.indexes()) > 0:
            self.show_image(sel.indexes()[0].row())

    def load_data(self, pck_filename, tab_filename=None, palette_filename=None):
        self.scene.clear()
        self.scene.addText('Loading...')
        self.loader.set_files(pck_filename, tab_filename, palette_filename)
        self.loader.moveToThread(self.thread)
        self.loader.loaded.connect(self.loaded)
        # noinspection PyUnresolvedReferences
        self.thread.started.connect(self.loader.load)
        self.thread.start()

    @QtCore.pyqtSlot()
    def loaded(self):
        images = self.sender().images
        self.thread.quit()
        self.thread.deleteLater()
        print 'loaded {} images.'.format(len(images))
        self.images_list_model.set_images_count(len(images))
        self.images = images
        self.show_image(0)

    def show_image(self, number):
        if len(self.images) >= number:
            in_img = self.images[number]
            in_buffer = cStringIO.StringIO()
            in_img.save(in_buffer, 'PNG')
            out_img = QtGui.QImage.fromData(in_buffer.getvalue())
            # noinspection PyArgumentList
            pixmap = QtGui.QPixmap.fromImage(out_img)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
        else:
            print('Out of index: {}/{}.'.format(number), len(self.images))

    def scale_preview(self, x, y):
        self.image_preview.scale(x, y)

    def zoom_in(self):
        self.zoom_factor *= 2.0
        self.image_preview.scale(2, 2)

    def zoom_out(self):
        self.zoom_factor /= 2.0
        self.image_preview.scale(0.5, 0.5)

    def zoom_reset(self):
        self.image_preview.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
        self.zoom_factor = 1

def main():
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument('pck', help='path to the pck file to work on.')
        parser.add_argument('--tab', '-t', help='path to the index file.')
        parser.add_argument('--palette', '-p', help='path to thr palette file.')
        args = parser.parse_args()

        if not os.path.exists(args.pck):
            exit('File not found: ' + args.pck)
        pck_filename = args.pck

        if not args.palette:
            print('We have no palette. Ok. I\'ll deal with it.')
            palette_filename = ''
        else:
            palette_filename = args.palette

        if not args.tab:
            print('There\'s no index file given. So, I should find it by myself.')
            tab_filename = args.pck[:-3] + 'tab'
            if not os.path.exists(tab_filename):
                tab_filename = args.pck[:-3] + 'TAB'
            if not os.path.exists(tab_filename):
                tab_filename = ''
        else:
            tab_filename = args.tab
        main_window.load_data(pck_filename, tab_filename, palette_filename)

    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

