#!/usr/bin/python3
# -*- coding: utf-8 -*-

from itertools import count, combinations
from random import sample
from platform import python_version

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

import defines
import gui

version = [0, 1]

def info():
    verstr = '.'.join(map(str, version))
    from PyQt5.Qt import QT_VERSION_STR
    infostr = f'RiskSpec Loops Analyzer v{verstr}, GPLv3.\n' + \
              f'Python {python_version()}\n' + \
              f'Pandas {pd.__version__}\n' + \
              f'NetworkX {nx.__version__}\n' + \
              f'PyQt {QT_VERSION_STR}'
    return infostr


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
    import math
    plt.figure(next(iid))
    pos = nx.spring_layout(g, k=5 / math.sqrt(g.order()))
    if cmap:
        cn = [g.nodes[n]['color'] for n in g.nodes]
        # cn = nx.get_node_attributes(g, 'color')
        print(cn)
        nx.draw(g, pos=pos, alpha=0.6, with_labels=True, node_color=cn, cmap=cmap)
    else:
        nx.draw(g, pos=pos, alpha=0.6, with_labels=True)
    plt.show()


# class DummyNode(object):
# class StronglyOp(DummyNode):
# class WeaklyOp(DummyNode):


class CustomNode(object):

    def __init__(self, data, tstr, text='Unnmaed graph'):
        self._data = data
        self._tstr = tstr
        self._text = text

        self._children = []
        self.initChild()

        self._columncount = 4
        self._parent = None
        self._row = 0

    def initChild(self):
        if self._data is None:
            return
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
        elif column == 2:
            return len(self._data.edges)
        elif column == 3:
            return self.loops_count()

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
        saveFile, filter = gui.QFileDialog.getSaveFileName(caption="Specify a file to save loops",
                                                           filter="Text files (*.txt);;All files (*.*)")
        if saveFile:
            with open(f'{saveFile}.txt', 'w') as file:
                cycles = nx.simple_cycles(self._data)
                for i, cycle in enumerate(cycles, start=1):
                    str = '\t'.join(cycle)
                    file.write(f'{i}\t{str}\n')

    def loops_count(self):
        if len(self._data.nodes) > defines.max_node_loops_calc and \
                len(self._data.edges) > defines.max_edge_loops_calc:
            return 'nodes limit'
        return len(list(nx.simple_cycles(self._data)))

    def condensation_plot(self):
        graph_plot(nx.condensation(self._data))


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
        for i, edge in enumerate(test_edges):
            g.remove_edge(*edge)
            test_pass = True
            for node in cnodes:
                d = nx.algorithms.descendants(g, node)
                test_pass = (dn == d)
                if not test_pass:
                    break
            if test_pass:
                accepted_edges.append(edge)
                print(f'{i}/{len(test_edges)}\t{edge}')
            g.add_edge(*edge)
        return accepted_edges

    def set_comb(self, edges, combset=None):
        if combset != None:
            nl = set()
            for e in edges:
                for comb in combset:
                    s = [el for el in comb]
                    s.append(e)
                    nl.add(frozenset(s))
            return nl
        return {frozenset(e) for e in edges}

    def init_comb(self, edges):
        return {frozenset(comb) for comb in list(combinations(edges, 2))}

    def av(self):
        max_level = 10
        g = self._data
        # Nodes from which the graph is entered
        orange_nodes = [x for x, y in g.nodes(data=True) if y['color'] == 1]
        # Nodes to which reachability is checked
        blue_nodes = frozenset([x for x, y in g.nodes(data=True) if y['color'] == 2])
        # Edges whose unit deletion will not lead to a break in the graph connectivity
        edges = list(g.edges())
        if len(edges) > 50:
            edges = sample(edges, 20)
        edges = self.test(g, orange_nodes, blue_nodes, edges)
        old_set = set([frozenset([e]) for e in edges])
        for level in range(2, max_level):
            print(f'Start of level {level}/{max_level}.')
            iter_count = len(old_set)*len(edges)
            i=0
            new_set = set()
            temp_edges = set()
            for comb in old_set:
                g.remove_edges_from(comb)
                for e in edges:
                    i = i + 1
                    if e not in comb:
                        g.remove_edge(*e)
                        # Test
                        test_pass = True
                        for node in orange_nodes:
                            d = nx.algorithms.descendants(g, node)
                            test_pass = (blue_nodes == d)
                            if not test_pass:
                                break
                        if test_pass:
                            s = [el for el in comb]
                            s.append(e)
                            new_set.add(frozenset(s))
                            print(f'{i}/{iter_count}\t{s}')
                            temp_edges.add(e)
                        g.add_edge(*e)

                g.add_edges_from(comb)
            if len(new_set)>0:
                old_set = new_set
            else:
                print(f'End run. No edge combination on {level}.')
                return
            print(f'End of level {level}/{max_level}, found {len(new_set)} edge combinations. '
                  f'{len(temp_edges)} of {len(edges)} edges left for the test.')
            edges = temp_edges
        print(f'End run. Maximum search nesting level {max_level} reached!')
        return

def loadGraph(params):
    import pyodbc
    with pyodbc.connect(params) as cnxn:
        df = pd.read_sql(gui.sql.getFTGraph, cnxn)
        G = nx.from_pandas_edgelist(df=df, source='Node1', target='Node2', create_using=nx.DiGraph())
    return CustomNode(G, 'g')


def load_graph():
    feft = pd.read_csv('../drawloops/data/FE2FT.csv', sep='\t', header=0)
    feft.rename(columns={'FE': 'FT1', 'FT': 'FT2'}, inplace=True)
    ftft = pd.read_csv('../drawloops/data/FT2FT.csv', sep='\t', header=0)
    df = pd.concat([feft, ftft])
    G = nx.from_pandas_edgelist(df=df, source='FT1', target='FT2', create_using=nx.DiGraph())
    return G
