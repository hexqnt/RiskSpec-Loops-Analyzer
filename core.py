#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from platform import python_version
import gui


from itertools import count
iid = count()

def rem(G):
    for i in range(1,3):
        for node in list(G.nodes):
            if G.in_degree(node) == G.out_degree(node) == 1:
                edges = list(nx.all_neighbors(G, node))
                G.add_edge(edges[0], edges[1])
                G.remove_node(node)
    return G

def graph_plot(g):
    plt.figure(next(iid))
    pos = nx.spring_layout(g, k=0.5)
    nx.draw(g, pos=pos, alpha=0.6, with_labels=True)
    plt.show()




class CustomNode(object):

    def __init__(self, data, tstr):
        self._data = data
        self._tstr = tstr
        if type(data) == tuple:
            self._data = list(data)
        if type(data) is str or not hasattr(data, '__getitem__'):
            self._data = [data]

        self._children = []

        if tstr== 'g':
            weakly_nodes_list = list(filter(lambda x: len(x)>1,
                                            nx.weakly_connected_components(self._data)))
            weakly_nodes_list.sort(key=lambda x: len(x), reverse=True)
            for weakly_nodes in weakly_nodes_list:
                g = self._data.subgraph(weakly_nodes)
                child = CustomNode(g, 'w')
                child._parent=self
                self._children.append(child)
        elif tstr == 'w':
            strongly_nodes_list = list(filter(lambda x: len(x)>1,
                                              nx.strongly_connected_components(self._data)))
            for strongly_nodes in strongly_nodes_list:
                g =  self._data.subgraph(strongly_nodes)
                child = CustomNode(g, 's')
                child._parent = self
                child._row = len(self._children)
                self._children.append(child)

        elif tstr == 's':
            print('s')
            #print(list(nx.simple_cycles(data)))


        self._columncount = 2
        self._parent = None
        self._row = 0

    def data(self, column):

        if column == 0:
            return self._tstr
        elif column == 1:
            return  len(self._data.nodes)

    def columnCount(self):
        return self._columncount

    def childCount(self):
        return len(self._children)

    def child(self, row):
        if row >= 0 and row < self.childCount():
            return self._children[row]

    def parent(self):
        return self._parent

    def row(self):
        return self._row

    def plot(self):
       graph_plot(self._data)

    def pcplot(self):
        g = rem(self._data.copy())
        graph_plot(g)



def load_graph():
    feft = pd.read_csv('../drawloops/data/FE2FT.csv', sep='\t', header=0)
    feft.rename(columns={'FE':'FT1', 'FT':'FT2'}, inplace=True)
    ftft = pd.read_csv('../drawloops/data/FT2FT.csv', sep='\t', header=0)
    df = pd.concat([feft, ftft])
    G = nx.from_pandas_edgelist(df=df, source='FT1', target='FT2', create_using=nx.DiGraph())
    return  G

def main():
    print('RiskSpec Loops Analyzer\n',
          f'Python {python_version()}\n',
          f'Pandas {pd.__version__}\n',
          f'NetworkX {nx.__version__}\n',
          f'PyQt {gui.PYQT_VERSION_STR}')

    G = load_graph()
    node = CustomNode(G, 'g')

    app = gui.QApplication(sys.argv)
    window = gui.MainWindow(node)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()