#!/usr/bin/python2
__author__ = 'ringo'

import sys
import os
import cStringIO
import argparse
from PyQt4 import QtGui, QtCore

import pck


class OpenDialog(QtGui.QWidget):
    ok_clicked = QtCore.pyqtSignal()
    pck_file_path = ''
    tab_file_path = ''
    palette_file_path = ''

    def __init__(self):
        super(OpenDialog, self).__init__()
        pck_open_button = QtGui.QPushButton('...')
        pck_open_button.setFixedWidth(24)

        tab_open_button = QtGui.QPushButton('...')
        tab_open_button.setFixedWidth(24)

        palette_open_button = QtGui.QPushButton('...')
        palette_open_button.setFixedWidth(24)

        self.pck_path_input = QtGui.QLineEdit()
        self.tab_path_input = QtGui.QLineEdit()
        self.palette_path_input = QtGui.QLineEdit()
        ok_button = QtGui.QPushButton('&OK')
        cancel_button = QtGui.QPushButton('&Cancel')

        layout = QtGui.QFormLayout(self)
        layout.addRow(pck_open_button, self.pck_path_input)
        layout.addRow(tab_open_button, self.tab_path_input)
        layout.addRow(palette_open_button, self.palette_path_input)

        buttons_layout = QtGui.QFormLayout()
        buttons_layout.addRow(ok_button, cancel_button)
        layout.addRow(buttons_layout)

        self.connect(pck_open_button,
                     QtCore.SIGNAL('clicked()'),
                     lambda: self.pck_path_input.setText(QtGui.QFileDialog().getOpenFileName(self)))
        self.connect(cancel_button, QtCore.SIGNAL('clicked()'), self.hide)
        self.connect(ok_button, QtCore.SIGNAL('clicked()'), lambda: self.ok_clicked.emit())
        self.resize(400, 100)

    def get_filename(self):
        return QtGui.QFileDialog(self, '')


class PCKLoader(QtCore.QObject):
    loaded = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(PCKLoader, self).__init__()
        self.images = []
        self.files = []

    def set_files(self, pck_filename, tab_filename, palette_filename):
        self.files = [pck_filename, tab_filename, palette_filename]

    # @QtCore.pyqtSlot()
    def load(self):
        self.images = pck.PCK(self.files[0], self.files[1], self.files[2]).images
        self.loaded.emit()


class ImagesListModel(QtCore.QAbstractItemModel):
    def __init__(self, parent):
        super(ImagesListModel, self).__init__(parent)
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

    def __init__(self):
        super(MainWindow, self).__init__()
        self.image_preview = QtGui.QGraphicsView()
        self.loader = PCKLoader()
        self.thread = QtCore.QThread(self)
        self.images_list_model = ImagesListModel(self)
        self.open_dialog = OpenDialog()
        self.zoom_factor = 1
        self.images = []
        self.scene = QtGui.QGraphicsScene(self)
        self.setup_ui()

    def closeEvent(self, q_close_event):
        self.delete_thread()
        QtGui.QWidget.closeEvent(self, q_close_event)

    def setup_ui(self):
        self.scene.addText('Empty').setDefaultTextColor(QtGui.QColor(QtCore.Qt.gray))
        self.image_preview.setScene(self.scene)
        self.image_preview.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.black, QtCore.Qt.SolidPattern))
        self.image_preview.show()

        main_menu = QtGui.QMenuBar(self)
        menu_file = main_menu.addMenu('&File')
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

        open_file = QtGui.QAction('&Open', self)
        open_file.setShortcut(QtGui.QKeySequence('Ctrl+O'))
        self.connect(open_file, QtCore.SIGNAL('triggered()'), self.show_open_dialog)

        menu_file.addAction(open_file)
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

        self.connect(self.open_dialog, QtCore.SIGNAL('ok_clicked()'), self.open_dialog_ok)
        self.setWindowIcon(QtGui.QIcon('apocicon.ico'))
        self.setWindowTitle('PCK viewer')
        self.setContentsMargins(0, 11, 0, 0)
        self.setLayout(layout)
        self.resize(400, 200)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def selection_changed(self, sel):
        if sel and hasattr(sel, 'indexes') and len(sel.indexes()) > 0:
            self.show_image(sel.indexes()[0].row())

    def unload_images(self):
        self.thread.quit()
        self.thread.deleteLater()
        self.scene.clear()
        self.images_list_model.set_images_count(0)
        del self.loader

    def load_data(self, pck_filename, tab_filename=None, palette_filename=None):
        self.unload_images()
        self.thread = QtCore.QThread(self)
        self.loader = PCKLoader()
        self.scene.addText('Loading...').setDefaultTextColor(QtGui.QColor(QtCore.Qt.gray))
        self.loader.set_files(pck_filename, tab_filename, palette_filename)
        self.loader.moveToThread(self.thread)
        self.loader.loaded.connect(self.loaded)
        # noinspection PyUnresolvedReferences
        self.thread.started.connect(self.loader.load)
        self.thread.start()

    def delete_thread(self):
        print('Quit')
        self.thread.quit()
        self.thread.deleteLater()

    @QtCore.pyqtSlot()
    def loaded(self):
        images = self.sender().images
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

    def show_open_dialog(self):
        self.open_dialog.show()

    def open_dialog_ok(self):
        self.open_dialog.hide()
        self.load_data(self.open_dialog.pck_path_input.text(),
                       self.open_dialog.tab_path_input.text(),
                       self.open_dialog.palette_path_input.text())


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

