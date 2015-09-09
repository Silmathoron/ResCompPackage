#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" XML tools """


import xml.etree.ElementTree as xmlet
import itertools
import numpy as np



#
#---
# Utils
#------------------------

## translate string to boolean

def bool_from_string(string):
	return True if (string.lower() == "true") else False

## make tensor product

def tensor_product(lstKeys, lstVal):
	lstTensor = []
	for tplValues in itertools.product(*lstVal):
		subDict = {}
		for i,val in enumerate(tplValues):
			subDict[lstKeys[i]] = val
		lstTensor.append(subDict)
	return lstTensor


#
#---
# XML/dict conversions
#------------------------

## converting dictionary to XML

def dict_to_xml(dico, root = None):
	base = None
	if root is not None:
		base = root
	else:
		base = xmlet.Element("base")
	for key,value in dico.items():
		elt = xmlet.Element(key)
		if value.__class__ == dict:
			elt = dict_to_xml(value, elt)
		else:
			elt.text = str(value)
		base.append(elt)
	return base

## converting XML to dictionary

def xml_to_dict(xmlElt, dicTypes):
	dicResult = {}
	for child in xmlElt:
		strName = child.tag
		if len(child):
			elt = child.find("start")
			if elt is not None:
				start = dicTypes[strName](child.find("start").text)
				stop = dicTypes[strName](child.find("stop").text)
				step = dicTypes[strName](child.find("step").text)
				dicResult[child.tag] = np.arange(start,stop,step)
			else:
				dicResult[child.tag] = xml_to_dict(child, dicTypes)
		else:
			dicResult[child.tag] = dicTypes[child.tag](child.text)
	return dicResult

def xml_to_iter_dict(xmlElt, dicTypes):
	dicResult = {}
	for child in xmlElt:
		strName = child.tag
		if len(child):
			elt = child.find("start")
			if elt is not None:
				start = dicTypes[strName](child.find("start").text)
				stop = dicTypes[strName](child.find("stop").text)
				step = dicTypes[strName](child.find("step").text)
				dicResult[child.tag] = np.arange(start,stop,step)
			else:
				dicResult[strName] = xml_to_iter_dict(child, dicTypes),
		else:
			dicResult[strName] = dicTypes[strName](child.text),
	return dicResult
