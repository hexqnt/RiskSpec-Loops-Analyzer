import sys

import core
import gui


def main():
    print(core.info())
    G = None
    node = core.CustomNode(G, 'g')

    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = gui.MainWindow(node)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
