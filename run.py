import sys
import gui
import core

def main():
    print(core.info())
    gui.sql.init_sql_queries()
    #G = load_graph()
    G = None
    node = core.CustomNode(G, 'g')

    app = gui.QApplication(sys.argv)
    window = gui.MainWindow(node)
    window.show()
    sys.exit(app.exec_())



if __name__ == '__main__':
    main()