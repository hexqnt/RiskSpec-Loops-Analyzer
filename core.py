#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from platform import python_version
import gui

from itertools import count

# Graph numbering counter for plotting
iid = count()


# Removing nodes for path contraction
def rem(G):
    for i in range(1, 3):
        for node in list(G.nodes):
            if G.in_degree(node) == G.out_degree(node) == 1:
                edges = list(nx.all_neighbors(G, node))
                G.add_edge(edges[0], edges[1])
                G.remove_node(node)
    return G


def graph_plot(g, cmap=False):
    plt.figure(next(iid))
    pos = nx.spring_layout(g, k=0.5)
    if cmap:
        cn = [g.nodes[n]['color'] for n in g.nodes]
        # cn = nx.get_node_attributes(g, 'color')
        print(cn)
        nx.draw(g, pos=pos, alpha=0.6, with_labels=True, node_color=cn, cmap=cmap)
    else:
        nx.draw(g, pos=pos, alpha=0.6, with_labels=True)
    plt.show()


class CustomNode(object):

    def __init__(self, data, tstr, text='Unnmaed graph'):
        self._data = data
        self._tstr = tstr
        self._text = text

        self._children = []
        self.initChild()

        self._columncount = 2
        self._parent = None
        self._row = 0

    def initChild(self):
        weakly_nodes_list = list(filter(lambda x: len(x) > 1,
                                        nx.weakly_connected_components(self._data)))
        weakly_nodes_list.sort(key=lambda x: len(x), reverse=True)
        for weakly_nodes in weakly_nodes_list:
            g = self._data.subgraph(weakly_nodes)
            child = WeaklyNode(g, 'w', f'Weakly component {self.childCount() + 1}')
            child._parent = self
            child._row - self.childCount()
            self._children.append(child)

    def data(self, column):

        if column == 0:
            return self._text
        elif column == 1:
            return len(self._data.nodes)

    def columnCount(self):
        return self._columncount

    def childCount(self):
        return len(self._children)

    def child(self, row):
        if 0 <= row < self.childCount():
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

    def simple_cycles(self):
        saveFile, filter = gui.QFileDialog.getSaveFileName(caption="Specify a file to save loops", filter="Text files (*.txt);;All files (*.*)")
        if saveFile:
            with open(f'{saveFile}.txt', 'w') as file:
                cycles = nx.simple_cycles(self._data)
                for i, cycle in enumerate(cycles, start=1):
                    str = '\t'.join(cycle)
                    file.write(f'{i}\t{str}\n')



class WeaklyNode(CustomNode):

    def initChild(self):
        strongly_nodes_list = list(filter(lambda x: len(x) > 1,
                                          nx.strongly_connected_components(self._data)))
        for strongly_nodes in strongly_nodes_list:

            # g = self._data.subgraph(strongly_nodes)

            # Set of nodes from which there is an entrance to the subgraph
            outin_nodes = set()
            edges = self._data.in_edges(strongly_nodes)
            for e in edges:
                source, targer = e
                outin_nodes.add(source)

            strongly_nodes_with_entrance = outin_nodes
            entrance_nodes = outin_nodes.difference(strongly_nodes)

            g = self._data.subgraph(strongly_nodes_with_entrance)
            m = g.copy()
            betwen_edges = g.in_edges(entrance_nodes)
            m.remove_edges_from(betwen_edges)
            g = m
            # The color indicating attribute is used when rendering a graph
            nx.set_node_attributes(g, 2, 'color')
            for n in entrance_nodes:
                a = g.nodes.get(n, None)
                if a:
                    a['color'] = 1

            child = StronglyNode(g, 's', f'Strongly component {self.childCount() + 1}')
            child._parent = self
            child._row = self.childCount()
            self._children.append(child)


class StronglyNode(CustomNode):

    def initChild(self):
        # g = rem(self._data.copy())
        # child = CustomNode(g, 't', f'Struct component {self.childCount() + 1}')
        # child._parent = self
        # child._row - self.childCount()
        # self._children.append(child)
        print('Strongly Node (init child)')

    def plot(self):
        graph_plot(self._data, cmap=plt.cm.get_cmap('Set1'))


    def test(self, g, cnodes, dn, test_edges):
        accepted_edges = []
        for edge in test_edges:
            g.remove_edge(edge[0], edge[1])

            test = True
            for node in cnodes:
                d = nx.algorithms.descendants(g, node)
                test = dn == set(d)
                if not test:
                    break
            if test:
                #print(f'accept edge {edge}')
                accepted_edges.append(edge)


            g.add_edge(edge[0], edge[1])

        return  accepted_edges


    def av(self):
        g = self._data
        cnodes= [x for x,y in g.nodes(data=True) if y['color']==1]
        dnodes= [x for x,y in g.nodes(data=True) if y['color']==2]
        dn = set(dnodes)
        #print(f'{cnodes}\n{dnodes}')
        edges = list(g.edges())
        print(self.test(g,cnodes,dn,edges))



def load_graph():
    feft = pd.read_csv('../drawloops/data/FE2FT.csv', sep='\t', header=0)
    feft.rename(columns={'FE': 'FT1', 'FT': 'FT2'}, inplace=True)
    ftft = pd.read_csv('../drawloops/data/FT2FT.csv', sep='\t', header=0)
    df = pd.concat([feft, ftft])
    G = nx.from_pandas_edgelist(df=df, source='FT1', target='FT2', create_using=nx.DiGraph())
    return G


def main():
    print('RiskSpec Loops Analyzer\n',
          f'Python {python_version()}\n',
          f'Pandas {pd.__version__}\n',
          f'NetworkX {nx.__version__}\n',
          f'PyQt {gui.PYQT_VERSION_STR}')
    gui.sql.init_sql_queries()
    G = load_graph()
    node = CustomNode(G, 'g')

    app = gui.QApplication(sys.argv)
    window = gui.MainWindow(node)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()