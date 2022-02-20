import sys

import networkx as nx
from pydriller import Repository
import argparse


class Change():
    commit: str
    file: str
    function: str

    def __init__(self, commit, file, function):
        self.commit = commit
        self.file = file
        self.function = function

    def __hash__(self):
        return hash(str(hash(self.file) + hash(self.function) + hash(self.commit)))

    def __str__(self):
        return f'{self.commit}---{self.file}----{self.function}'

    def __eq__(self, other):
        return self.commit == other.commit and self.file == other.file and self.function == other.function

    def get_node(self):
        return f'{self.file}-{self.function}'


def get_changes(repo, verbose):
    def mprint(str):
        if verbose:
            print(str)

    changes = set()
    for commit in Repository(repo).traverse_commits():
        for file in commit.modified_files:
            for method in file.changed_methods:
                change = Change(commit.hash, file.filename, method.name)
                changes.add(change)
                mprint(f'{len(changes) + 1} {change}')
    return changes


def create_graph(changes):
    G = nx.MultiGraph()
    for c in changes:
        n = c.get_node()
        if n not in G.nodes:
            G.add_node(n)

    for c1 in changes:
        n1 = c1.get_node()
        for c2 in changes:
            n2 = c2.get_node()
            if c1 == c2:
                continue
            if c1.commit == c2.commit:
                G.add_edge(n1, n2, color='red')
            if c1.file == c2.file and c1.function == c2.function:
                G.add_edge(n1, n2, color='blue')
    return G


def get_centralises(path, verbose=True):
    print('getting changes')
    changes = get_changes(path, verbose)
    print('creating graph')
    G = create_graph(changes)
    print('got graph')
    pgrank = nx.algorithms.pagerank(G)
    centrality = nx.algorithms.closeness_centrality(G)
    common_neighbor = nx.algorithms.common_neighbor_centrality(G)
    return {'page_rank': pgrank, 'closeness': centrality, 'common_neighbor': common_neighbor}


def print_centralities(path, verbose):
    print(get_centralises(path, verbose))


def main():
    parser = argparse.ArgumentParser(description='git graph analysis')
    parser.add_argument('--path', help='path to the git repository')
    parser.add_argument('--verbose', default=True)
    args = parser.parse_args()
    print_centralities(args.path, args.verbose)


if __name__ == '__main__':
    main()
