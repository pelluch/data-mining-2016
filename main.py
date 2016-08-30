#!/bin/env python2

import sys
import csv
from collections import defaultdict
from itertools import chain, combinations
import itertools


separator = ','
min_support = 0.4
min_confidence = 0.1
items = set()
transactions = []
k_frequencies = defaultdict(int)

def joinSet(itemSet, length):
	return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])

def subsets(arr):
	return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])

def process_args(args):
	file = args[1]
	items, transactions = process_file(file)
	k_items = prune_baskets(items)
	k = 2
	all_sets = dict()

	while(k_items != set([])):
		all_sets[k-1] = k_items
		k_items = joinSet(k_items, k)
		k_items = prune_baskets(k_items)
		k = k + 1

	toRetItems = []
	for k, rules in all_sets.items():	    
	
		toRetItems.extend([(tuple(item), getSupport(item))
                           for item in rules])

	toRetRules = []
	for k, rules in all_sets.items()[1:]:
		for rule in rules:
			rule_subsets = map(frozenset, [x for x in subsets(item)])
			for rule_subset in rule_subsets:
				remain = rule.difference(rule_subset)
				if len(remain) > 0:
					support = getSupport(rule)
					confidence = support/getSupport(rule_subset)
					lift = confidence/(getSupport(remain))
					if confidence >= min_confidence:
						toRetRules.append(((','.join(rule_subset) + ';' + ','.join(remain)),
                                       support, confidence, lift))

	sorted_rules = sorted(toRetRules, key=lambda tup: tup[1])
	


def interned_item(item):
	return intern(item.strip())

def getSupport(item):
	return float(k_frequencies[item])/len(transactions)

def prune_baskets(current_items):

	new_items = set()
	k_set = defaultdict(int)

	for item in current_items:
		for transaction in transactions:
			if item.issubset(transaction):
				k_set[item] += 1
				k_frequencies[item] += 1
	
	for item, count in k_set.items():
		support = float(count)/len(transactions)
		if support >= min_support:
			new_items.add(item)
	return new_items
				

def process_file(path):
	with open(path, 'r') as csvfile:
		input_data = csv.reader(csvfile, delimiter=separator, quotechar='"')
		for row in input_data:
			row_items = list(map(interned_item, row))
			transactions.append(row_items)
			for item in row_items:
				items.add(frozenset([item]))
		return items, transactions


if __name__ == "__main__":
    process_args(sys.argv)
