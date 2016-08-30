#!/bin/env python2
# -*- coding: utf-8 -*-

import sys
import csv
from collections import defaultdict
from itertools import chain, combinations
import os


items = set()
transactions = []
k_frequencies = defaultdict(int)

# Función que expande las canastas de k -> k + 1 items
def expand_set(itemSet, length):
	return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])

# Genera subconjuntos a partir de un arreglo
# Ejemplo tipo http://stackoverflow.com/questions/374626/how-can-i-find-all-the-subsets-of-a-set-with-exactly-n-elements
def subsets(item_arr):
	return chain(*[combinations(item_arr, i + 1) for i, a in enumerate(item_arr)])

def process_args(args):
	if len(args) < 2:
		print('Debes ingresar un archivo como parámetro')
		return
	file = args[1]
	
	if not os.path.isfile(file):
		print('Archivo indicado no existe')
		return
	

	min_confidence = -1
	min_support = -1

	while min_confidence < 0 or min_confidence > 1:
		min_confidence = float(raw_input('Ingrese 0 <= min_confidence <= 1\n'))

	while min_support < 0 or min_support > 1:
		min_support = float(raw_input('Ingrese 0 <= min_support <= 1\n'))

	# Cargamos los datos
	items, transactions = process_file(file)
	# Items "pruneados"
	k_items = prune_baskets(items, min_support)
	k = 2
	# Esto contendrá todos los items frecuentes para cada k
	all_sets = dict()	

	while(k_items != set([])):
		all_sets[k-1] = k_items
		k_items = expand_set(k_items, k)
		k_items = prune_baskets(k_items, min_support)
		k = k + 1

	final_rules = []
	for k, rules in all_sets.items()[1:]:
		for rule in rules:
			# Para cada regla, encontramos sus subconjuntos
			rule_subsets = map(frozenset, [x for x in subsets(rule)])
			for rule_subset in rule_subsets:
				# Obtenemos lo que eudó afuera
				remain = rule.difference(rule_subset)
				if len(remain) > 0:
					support = calculate_support(rule)
					confidence = support/calculate_support(rule_subset)
					lift = confidence/(calculate_support(remain))
					if confidence >= min_confidence:
						# Generamos tupla con información que permite ordenar después
						final_rules.append(((','.join(sorted(rule_subset)) + ';' + ','.join(sorted(remain))),
                                       support, confidence, lift))
	order = "1"			
	output_file = None			
	while order != "4":	
		order = raw_input("1) Ordenar por soporte\n2) Ordenar por confidence\n3) Ordenar por lift\n4) Salir\n")
		if order == "1":
			sorted_rules = sorted(final_rules, key=lambda tup: tup[1], reverse=True)
		elif order == "2":	
			sorted_rules = sorted(final_rules, key=lambda tup: tup[2], reverse=True)
		elif order == "3":
			sorted_rules = sorted(final_rules, key=lambda tup: tup[3], reverse=True)
		elif order == "4":
			return

		if len(args) > 2:
			output = args[2]
			output_file = open(output, 'w')
		for rule in sorted_rules:
			print(';'.join(map(str, [x for x in rule])))
			if output_file is not None:
				output_file.write(';'.join(map(str, [x for x in rule])) + "\n")
		if output_file is not None:
			output_file.close()


# Al usar intern, se hace más eficiente el uso de strings sin necesidad de usar enteros
def interned_item(item):
	return intern(item.strip())

# Calcula soporte para un conjunto
def calculate_support(item):
	return float(k_frequencies[item])/len(transactions)

def prune_baskets(current_items, min_support):

	new_items = set()
	# Frecuencias para set actual
	k_set = defaultdict(int)

	for item in current_items:
		for transaction in transactions:
			if item.issubset(transaction):
				k_set[item] += 1
				# Set global para calcular confidence a posteriori
				k_frequencies[item] += 1
	
	for item, count in k_set.items():
		support = float(count)/len(transactions)
		if support >= min_support:
			new_items.add(item)
	return new_items
				

def process_file(path):
	separator = ''	
	while len(separator) != 1:
		separator = raw_input('Ingrese el separador para el input (un caracter)\n')
	with open(path, 'r') as csvfile:
		input_data = csv.reader(csvfile, delimiter=separator, quotechar='"')
		for row in input_data:
			# Optimización para mejorar comparaciones de strings
			row_items = list(map(interned_item, row))
			transactions.append(row_items)
			for item in row_items:
				# frozenset permite manejar conjuntos de modo fácil
				items.add(frozenset([item]))
		return items, transactions


if __name__ == "__main__":
    process_args(sys.argv)
