from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QAction, QMenu, qApp, QFileDialog, QWidget,\
    QComboBox, QDialog, QLabel, QDesktopWidget
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.Qt import PYQT_VERSION_STR, QColor
import typing
import sys


class CustomModel(QAbstractItemModel):
    def __init__(self, node):
        QAbstractItemModel.__init__(self)
        self._root = node
        self._header = ["Graph name", 'Nodes count']
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

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            node = index.internalPointer()
            return node.data(index.column())
        if role == Qt.EditRole:
            node = index.internalPointer()
            return node

        return None

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        node = index.internalPointer()
        node._text = value
        return True

    # Indicate how we can interact with the relevant elements
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemFlags()
        # Standard interaction type
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        # Allow renaming of the graph
        if index.column() == 0:
            flags = flags | Qt.ItemIsEditable
        return flags

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal and \
                role == Qt.DisplayRole and \
                section <= len(self._header):
            return self._header[section]
        return None


class MainWindow(QMainWindow):
    def __init__(self, node):
        super().__init__()
        uic.loadUi('ui/mainwindow.ui', self) # Load the .ui file
        #self.show() # Show the GUI
        self.initUI(node)

    def initUI(self, node):

        self.actionOpen.triggered.connect(self.openModelDialog)
        self.actionExit.triggered.connect(qApp.quit)

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

        simpleCuclesAction = QAction('Simple cycles', self)
        simpleCuclesAction.setStatusTip('Print simple cycles of graph')
        simpleCuclesAction.triggered.connect(index.internalPointer().simple_cycles)

        menu = QMenu()
        menu.addAction(plotAction)
        menu.addAction(pcPlotAction)
        menu.addAction(simpleCuclesAction)

        menu.exec_(self.treeView.viewport().mapToGlobal(position))

    def openModelDialog(self):
        e = OpenModelDialog(self)
        e.exec_()
        #self.geometry().center()


class OpenModelDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        uic.loadUi('ui/openmodeldialog.ui', self) # Load the .ui file
        self.initUI()

    def initUI(self):
        qr = self.frameGeometry()
        cp = self.parent().geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.updateModelList.clicked.connect(self.getAvalibleModels)

    def getAvalibleModels(self):
        dbname = 'master'
        ip ='127.0.0.1'
        port = 1433
        uid = self.uid.text()
        pwd = self.pwd.text()
        serverName = self.serverName.currentText()

        # Создаем строку подключенрия со спец. символами
        if sys.platform == 'linux':
            # Удалённое подключение для Linux через FreeTDS и unixODBC
            params = f'DRIVER=FreeTDS;SERVER={ip};PORT={port};DATABASE={dbname};UID={uid};Pwd={pwd};TDS_Version=8.0;'

        elif sys.platform == 'win32':
            # Локальное подключение для Windows со стандартным драйвером
            params = f'DRIVER={{SQL Server}};SERVER={serverName};DATABASE={dbname};UID={uid};Pwd={pwd}'
        else:
            return None

        import pyodbc
        with pyodbc.connect(params) as cnxn:
            with cnxn.cursor() as cursor:
                cursor.execute("SELECT name FROM master.dbo.sysdatabases WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')")
                rows = cursor.fetchall()
                if len(rows)==0:
                    sys.exit("Нет активных моделей!")
                    return None

                a = [r[0] for r in rows]
                self.models.addItems(a)

    def connetionString(self):
        if sys.platform == 'linux':
            # Удалённое подключение для Linux через FreeTDS и unixODBC
            params = f'DRIVER=FreeTDS;SERVER={ip};PORT={port};DATABASE={dbname};UID={uid};Pwd={pwd};TDS_Version=8.0;'

        elif sys.platform == 'win32':
            # Локальное подключение для Windows со стандартным драйвером
            params = f'DRIVER={{SQL Server}};SERVER={serverName};DATABASE={dbname};UID={uid};Pwd={pwd}'
        else:
            return None

        return params






