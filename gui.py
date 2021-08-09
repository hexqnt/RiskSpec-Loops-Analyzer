import os
import sys
import typing

from PyQt5 import uic
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, qApp, QFileDialog, QDialog, QMessageBox

import sql


class CustomModel(QAbstractItemModel):
    def __init__(self, node):
        QAbstractItemModel.__init__(self)
        self._root = node
        self._header = ["Graph name", 'Nodes', 'Edges', 'Loops']
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
        uic.loadUi('ui/MainWindow.ui', self)  # Load the .ui file
        self.initUI(node)

    def initUI(self, node):

        self.actionOpen.triggered.connect(self.openModelDialog)
        self.actionExit.triggered.connect(qApp.quit)
        self.actionLoadFTGraph.triggered.connect(self.loadFTGraph)
        self.actionAbout.triggered.connect(self.about)
        self.actionWiki.triggered.connect(self.openWiki)

        self.treeView.customContextMenuRequested.connect(self.openMenu)
        # self.treeView.setModel(CustomModel(node))

    def openMenu(self, position):
        index = self.treeView.indexAt(position)
        if not index.isValid():
            return

        pointer = index.internalPointer()
        pdir = dir(pointer)
        menu = QMenu()

        if 'plot' in pdir:
            plotAction = QAction('Plot', self)
            plotAction.setStatusTip('Plot graph in Matplotlib')
            plotAction.triggered.connect(pointer.plot)
            menu.addAction(plotAction)

        if 'pcplot' in pdir:
            pcPlotAction = QAction('Path contraction plot', self)
            pcPlotAction.setStatusTip('Plot graph in Matplotlib with path contraction')
            pcPlotAction.triggered.connect(pointer.pcplot)
            menu.addAction(pcPlotAction)

        if 'condensation_plot' in pdir:
            condensationPlotAction = QAction('Condensation plot', self)
            condensationPlotAction.setStatusTip(
                'Condensation is the graph with each of the strongly connected components contracted into a single node')
            condensationPlotAction.triggered.connect(pointer.condensation_plot)
            menu.addAction(condensationPlotAction)

            menu.addSeparator()

        if 'simple_cycles' in pdir:
            simpleCuclesAction = QAction('Simple cycles', self)
            simpleCuclesAction.setStatusTip('Print simple cycles of graph')
            simpleCuclesAction.triggered.connect(pointer.simple_cycles)
            menu.addAction(simpleCuclesAction)

        if 'av' in pdir:
            loopBreakSearchAction = QAction('Loop break search', self)
            loopBreakSearchAction.setStatusTip('Search for places of breaking logical loops in a graph')
            loopBreakSearchAction.triggered.connect(pointer.av)
            menu.addAction(loopBreakSearchAction)

        menu.exec_(self.treeView.viewport().mapToGlobal(position))

    def openModelDialog(self):
        e = OpenModelDialog(self)
        resultCode = e.exec()
        if resultCode == 1:
            self.sqlparams = e.connetionString()
        else:
            print('None code')

    def loadFTGraph(self):
        import core
        self.treeView.setModel(CustomModel(core.loadGraph(self.sqlparams)))

    def about(self):
        import core
        QMessageBox.about(self, 'About', core.info())

    def openWiki(self):
        import webbrowser
        webbrowser.open('https://github.com/HexQuant/RiskSpec-Loops-Analyzer/wiki', new=2)


class OpenModelDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        uic.loadUi('ui/OpenModelDialog.ui', self)  # Load the .ui file
        self.initUI()

    def initUI(self):
        qr = self.frameGeometry()
        cp = self.parent().geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.updateModelList.clicked.connect(self.getAvalibleModels)
        self.openFileModel.clicked.connect(self.openModelFile)
        self.attachButton.clicked.connect(self.attach)
        self.detachButton.clicked.connect(self.detach)

        self.getAvalibleModels()

    def openModelFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open model file', filter="RPP files (*.RPP);;All files (*.*)")[0]
        self.modelFilePath.setText(os.path.normpath(fname))
        return fname

    def detach(self):
        dbname = self.models.currentText()

        import pyodbc
        params = self.getParams()
        try:
            with pyodbc.connect(params) as cnxn:
                cnxn.autocommit = True
                with cnxn.cursor() as cursor:
                    cursor.execute(
                        f'''
                        USE [master];
                        ALTER DATABASE [{dbname}] SET TRUSTWORTHY ON;
                        EXEC sp_detach_db @dbname={dbname};
                        ''')
        except pyodbc.Error as ex:
            QMessageBox.warning(self, 'pyodbc', ex.args[0])
        self.getAvalibleModels()

    def attach(self):

        path = self.modelFilePath.text()
        dbname = os.path.basename(path).split('.')[0]

        import pyodbc
        params = self.getParams()
        try:
            with pyodbc.connect(params) as cnxn:
                cnxn.autocommit = True
                with cnxn.cursor() as cursor:
                    cursor.execute(
                        f'''
                        USE [master];
                        EXEC sp_attach_db
                        @dbname={dbname},
                        @filename1 = '{path}';
                        ''')
        except pyodbc.Error as ex:
            QMessageBox.warning(self, 'pyodbc', ex.args[0])
        self.getAvalibleModels()
        self.loadFromMemory.setChecked(True)

    def attach_model(self):
        name = 'dd'
        path = self.openModelFile()
        log_path = 'D:\dd'
        sql_str = f"USE[master]\nGO\nEXEC sp_attach_db @dbname = \"{name}\",\n" + \
                  f"@filename1 = \"{path}\",\n" + \
                  f"@filename2 = \"{log_path}\";"

        import pyodbc
        params = self.getParams()
        with pyodbc.connect(params) as cnxn:
            with cnxn.cursor() as cursor:
                cursor.execute(sql_str)
                rows = cursor.fetchall()
                if len(rows) == 0:
                    sys.exit("Нет активных моделей!")

        return sql_str

    def getParams(self, dbname='master', path='', ip='127.0.0.1', port=1433):
        uid = self.uid.text()
        pwd = self.pwd.text()
        serverName = self.serverName.currentText()

        params = None
        # Создаем строку подключенрия со спец. символами
        if sys.platform == 'linux':
            # Удалённое подключение для Linux через FreeTDS и unixODBC
            params = f'DRIVER=FreeTDS;SERVER={ip};PORT={port};DATABASE={dbname};uid={uid};Pwd={pwd};TDS_Version=8.0;'

        elif sys.platform == 'win32':
            # Локальное подключение для Windows со стандартным драйвером
            if path == '':
                params = f'DRIVER={{SQL Server}};SERVER={serverName};DATABASE={dbname};UID={uid};Pwd={pwd};'
            else:
                params = f'DRIVER={{SQL Server}};SERVER={serverName};Trusted_Connection=yes;AttachDbFileName={path}'

        return params

    def getAvalibleModels(self):
        import pyodbc
        params = self.getParams()
        try:
            with pyodbc.connect(params) as cnxn:
                with cnxn.cursor() as cursor:
                    cursor.execute(sql.getAvailableDB)
                    rows = cursor.fetchall()

                    self.models.clear()
                    if len(rows) > 0:
                        a = [r[0] for r in rows]
                        self.models.addItems(a)
        except pyodbc.Error as ex:
            QMessageBox.warning(self, 'pyodbc', ex.args[0])

    def connetionString(self):
        return self.getParams(dbname=self.models.currentText())
