#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 g <g@ABCL>
#
# Distributed under terms of the MIT license.

# For counting number of instances of an object
from collections import Counter
# For generating combinations of an itemset
from itertools import cycle, combinations
# For static typing (optional)
from typing import Iterable, Counter, List, FrozenSet, Set, Any


class DIC(object):
    '''Class for Dynamic Itemset Counting Algorithm
    Pass it an Iterable of Iterables (Eg. List of strings, or list of lists)
    FrozenSet is used as normal mutable sets cannot be hashed (Used as keys in a dictionary or counter,
    or inserted in a set)
    So Dashed square, dashed circle etc. are sets of frozensets

    Eg:
    >>> print(DIC(['AB', 'A', 'BC', ''], minsupp=1, m=2))
    '''

    def move(self, itemset, set2, set1):
        set1.discard(itemset)
        set2.add(itemset)

    def __init__(self, it: Iterable, minsupp: int, m: int):
        self.minsupp = minsupp
        self.m = m

        self.suppCounter: Counter = Counter()
        self.txnCounter: Counter = Counter()
        self.txns: List[frozenset] = []
        self.items: Any = set()

        # First pass, get all 1-itemsets
        for i in it:
            self.txns.append(frozenset(i))
            for j in i:
                self.items.add(frozenset(j))

        self.items = frozenset(self.items)
        # Initialise DC with 1 itemsets
        self.DC: Set[FrozenSet] = set()
        self.DS: Set[FrozenSet] = set()
        self.SC: Set[FrozenSet] = set()
        self.SS: Set[FrozenSet] = set()

        # Add all one itemsets to Dashed Circle
        self.DC |= self.items

        self.do()

    def __str__(self):
        ''' Utility function to print the DIC Object '''
        from pprint import pformat
        return f'''
DIC {{
    minsupp: {pformat(self.minsupp)}
    m: {pformat(self.m)}
    suppCounter:
    {pformat(self.suppCounter.most_common(), indent=2)}
    txnCounter: {pformat(self.txnCounter.most_common())}
}}
                '''

    def do(self):
        ''' Implements DIC Algorithm
        http://www2.cs.uregina.ca/~dbd/cs831/notes/itemsets/DIC.html
        '''
        (DC, DS, SC, SS, txnCounter, suppCounter, txns, m,
         minsupp) = (self.DC, self.DS, self.SC, self.SS, self.txnCounter,
                     self.suppCounter, self.txns, self.m, self.minsupp)
        infTxns = cycle(txns)
        l = len(txns)
        while DC or DS:
            T = []
            for i in range(m):
                T.append(next(infTxns))
            for tx in T:
                # For all itemsets that are dashed (in DC ∪ DS)
                for itemset in DC | DS:
                    txnCounter[itemset] += 1
                    if itemset <= tx:
                        suppCounter[itemset] += 1
                for itemset in DC.copy():
                    if suppCounter[itemset] >= minsupp:
                        self.move(itemset, DS, DC)
                        self.addSupersets(itemset)
                for itemset in DS.copy():
                    if txnCounter[itemset] >= l:
                        self.move(itemset, SS, DS)
                for itemset in DC.copy():
                    if txnCounter[itemset] >= l:
                        self.move(itemset, SC, DC)

    def addSupersets(self, itemset):
        for item in self.items:
            if item in (self.SS | self.DS):
                new = frozenset(item | itemset)
                if new == itemset:
                    continue
                subsets = set(self.genSubsets(new))
                if subsets <= (self.SS | self.DS):
                    self.DC.add(new)

    def genSubsets(self, itemset):
        l = len(itemset)
        for i in combinations(itemset, l - 1):
            yield frozenset(i)


def main():
    l = ['AB', 'A', 'BC', '']
    m = 2
    minsupp = 1
    print(DIC(l, minsupp, m))


if __name__ == '__main__':
    main()
