from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QAction, QMenu, qApp
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.Qt import PYQT_VERSION_STR
from typing import Any


class CustomModel(QAbstractItemModel):
    def __init__(self, node):
        QAbstractItemModel.__init__(self)
        self._root = node
        print('CustomModel init')

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.isValid():
            return parent.internalPointer().childCount()
        return self._root.childCount()

    def columnCount(self, parent: QModelIndex = ...) -> int:
        if parent.isValid():
            return parent.internalPointer().columnCount()
        return self._root.columnCount()

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:

        if not parent or not parent.isValid():
            p = self._root
        else:
            p = parent.internalPointer()

        if not QAbstractItemModel.hasIndex(self, row, column, parent):
            return QModelIndex()

        child = p.child(row)
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        else:
            return QModelIndex()

    def parent(self, child: QModelIndex) -> QModelIndex:
        if child.isValid():
            p = child.internalPointer().parent()
            if p:
                return QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QModelIndex()

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.DisplayRole:
            return node.data(index.column())
        return None



def ff():
    print('FF')
    return

class MainWindow(QMainWindow):
    def __init__(self, node):
        super().__init__()
        self.initUI( node)

    def initUI(self, node):

        self.setWindowTitle('RiskSpec Loops Analyzer')
        self.statusBar().showMessage('Ready')

        openAction = QAction( '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open graph data')

        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        self.treeView = QTreeView()
        self.setCentralWidget(self.treeView)
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.openMenu)
        self.treeView.setModel(CustomModel(node))

    def openMenu(self, position):

        index = self.treeView.indexAt(position)
        if not index.isValid():
            return

        plotAction = QAction('Plot', self)
        plotAction.setStatusTip('Plot graph in Matplotlib')
        plotAction.triggered.connect(index.internalPointer().plot)

        pcPlotAction = QAction('Path contraction plot', self)
        pcPlotAction.setStatusTip('Plot graph in Matplotlib with path contraction')
        pcPlotAction.triggered.connect(index.internalPointer().pcplot)

        menu = QMenu()
        menu.addAction(plotAction)
        menu.addAction(pcPlotAction)

        menu.exec_(self.treeView.viewport().mapToGlobal(position))
