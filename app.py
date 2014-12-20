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
        print 1

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
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(count, 0))

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 1

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.images

    def index(self, row, column, QModelIndex_parent=None, *args, **kwargs):
        if row < self.images:
            return self.createIndex(row, column)
        return QtCore.QModelIndex()

    def parent(self, QModelIndex=None):
        return QtCore.QModelIndex()

    def data(self, idx, int_role=None):
        if int_role in [0]:
            return idx.row()


class MainWindow(QtGui.QWidget):
    load = QtCore.pyqtSignal()
    images_list_model = ImagesListModel()
    scene = None
    statusbar = None
    images = []
    __pck__ = None

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setup_ui()

    def setup_ui(self):
        image_preview = QtGui.QGraphicsView()
        self.scene = QtGui.QGraphicsScene(self)
        self.scene.addText('Empty')
        image_preview.setScene(self.scene)
        image_preview.show()

        images_list = QtGui.QListView()
        images_list.setStyleSheet('background-color: black; color: lightgrey;')
        images_list.setFlow(images_list.LeftToRight)
        images_list.setFixedHeight(50)
        images_list.setModel(self.images_list_model)
        images_list.selectionModel().selectionChanged.connect(self.selection_changed)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(image_preview)
        layout.addWidget(images_list)

        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.showMessage('Ja-ja!')
        self.statusbar.show()

        self.setLayout(layout)
        self.resize(400, 200)

    def keyPressEvent(self, e):
        print 'Key pressed.%s' % e.key()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def selection_changed(self, sel):
        if sel and hasattr(sel, 'indexes') and len(sel.indexes()) > 0:
            print 'selected: %s' % sel.indexes()[0].row()
            self.show_image(sel.indexes()[0].row())

    def load_data(self, pck_filename, tab_filename=None, palette_filename=None):
        loader = PCKLoader()
        loader.set_files(pck_filename, tab_filename, palette_filename)
        thread = QtCore.QThread()
        loader.moveToThread(thread)
        loader.loaded.connect(self.loaded)
        thread.started.connect(loader.load)
        thread.start()

    @QtCore.pyqtSlot()
    def loaded(self):
        images = self.sender().images
        print 'loaded...%d' % len(images)
        self.images_list_model.set_images_count(len(images))
        self.images = images
        self.show_image(0)

    def show_image(self, number):
        if len(self.images) >= number:
            in_img = self.images[number]
            in_buffer = cStringIO.StringIO()
            in_img.save(in_buffer, 'PNG')
            out_img = QtGui.QImage.fromData(in_buffer.getvalue())
            print out_img.width(), out_img.height()
            pixmap = QtGui.QPixmap.fromImage(QImage=out_img)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
        else:
            print('Out of index: {}.'.format(number))
            print(len(self.__pck__.images))


def main():
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

    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    # main_window.load_data(pck_filename, tab_filename, palette_filename)
    # TODO: Find way to fix it =\
    loader = PCKLoader()
    loader.set_files(pck_filename, tab_filename, palette_filename)
    thread = QtCore.QThread()
    loader.moveToThread(thread)
    loader.loaded.connect(main_window.loaded)
    thread.started.connect(loader.load)
    thread.start()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

