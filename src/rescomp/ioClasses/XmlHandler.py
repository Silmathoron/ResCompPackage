#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" XML handler """


from copy import deepcopy
import xml.etree.ElementTree as xmlet
from itertools import product
import numpy as np

from xml_tools import dict_to_xml, xml_to_dict, xml_to_iter_dict, bool_from_string



#
#---
# XML handler class
#------------------------

class XmlHandler:
	
	def __init__(self):
		# parameters
		self.dicType = {"float": float,
						"string": str,
						"int": int,
						"bool": bool_from_string }
		self.lstParamNames = []
		# xml elements
		self.xmlRoot = None
		self.xmlHeader = None
		self.xmlParameters = None
		self.xmlSimulation = None
		self.path = ""

	#------------------#
	# Input processing #
	#------------------#

	## inital processing
	
	def process_input(self, strFileName, path=""):
		self.path = path if self.path == "" or path != "" else self.path
		tree = xmlet.parse(self.path+strFileName)
		self.xmlRoot = tree.getroot()
		# header and main param
		self.xmlHeader = self.xmlRoot.find("header")
		self.xmlParameters = self.xmlRoot.find("parameters")
		self.xmlSimulation = self.xmlRoot.find("simulation")
		if self.xmlRoot is None:
			raise IOError("XML input is probably invalid")
		if self.xmlHeader is None:
			raise NameError("Could not find <header></header> element in XML parameters.")
		if self.xmlParameters is None:
			raise NameError("Could not find <parameters></parameters> element in XML parameters.")
		if self.xmlSimulation is None:
			raise NameError("Could not find <simulation></simulation> element in XML parameters.")

	## parameters

	def get_parameters(self):
		if self.xmlParameters is not None:
			return xml_to_dict(self.xmlParameters, self.dicType)
		else:
			return None
		
	def gen_xml_param(self, input_id, recurrent_id, lstParam):
		table = xmlet.Element("table") # changed from table
		header = xmlet.SubElement(table, "header")
		# generate the column and the lists of param values
		inputFile = xmlet.SubElement(header, "column", {"name": "in_id"})
		recFile = xmlet.SubElement(header, "column", {"name": "rec_id"})
		for name in self.lstParamNames:
			param = xmlet.SubElement(header, "column", {"name": name})
		# generate rows
		for tplValues in lstParam:
			row = xmlet.SubElement(table, "row")
			data1 = xmlet.SubElement(row, "data")
			data1.text = input_id
			data2 = xmlet.SubElement(row, "data")
			data2.text = recurrent_id
			for value in tplValues:
				data = xmlet.SubElement(row, "data")
				data.text = str(value)
		return table

	def gen_grid_search_param(self):
		lstValues = []
		for child in self.xmlParameters:
			# add child to column
			strType = child.tag
			self.lstParamNames.append(child.attrib["name"])
			# generate list of values
			if len(child):
				start = self.dicType[strType](child.find("start").text)
				stop = self.dicType[strType](child.find("stop").text)
				step = self.dicType[strType](child.find("step").text)
				lstValues.append(np.arange(start,stop,step))
			else:
				lstValues.append((self.dicType[strType](child.text),))
		self.grid_param = list(product(*lstValues))
		return self.grid_param

	#------------------------#
	# Retrieving information #
	#------------------------#

	def get_header_item(self, strName):
		strSearch = '*[@name="' + strName + '"]'
		elt = self.xmlHeader.find(strSearch)
		if elt is not None:
			return self.dicType[elt.tag](elt.text)
		else:
			return None

	def get_networks(self):
		eltNet = self.xmlHeader.find('./string[@name="networks"]')
		if eltNet is not None:
			strNetworksFile = self.path+eltNet.text
			if "xml" in strNetworksFile:
				strGenerationType = "xml"
				xmlTree = xmlet.parse(strNetworksFile)
				root = xmlTree.getroot()
				return strGenerationType, root
			elif strNetworksFile:
				strGenerationType = "files"
				return strGenerationType, [ line for line in open(strNetworksFile) ]
		else:
			raise AttributeError("No <string name='networks'> element found in <header>")

	def get_string_context(self):
		strFileContext = self.get_header_item("context")
		tree = xmlet.parse(self.path+strFileContext)
		root = tree.getroot()
		return xmlet.tostring(root)

	#------------#
	# Conversion #
	#------------#

	def convert_xml_to_dict(self, xmlElt, bIterable=False):
		if xmlElt is not None:
			if bIterable:
				return xml_to_iter_dict(xmlElt, self.dicType)
			else:
				return xml_to_dict(xmlElt, self.dicType)
		else:
			return None

	def from_string(self,string):
		return xmlet.fromstring(string)

	def results_dic(self, strXml, lstParam):
		xmlElt = self.from_string(strXml)
		dicResults = { "param_names": [], "results_names": [] }
		# header names
		xmlHeader = xmlElt[0]
		for child in self.xmlParameters:
			dicResults["param_names"].append(child.attrib["name"])
		for child in xmlHeader:
			dicResults["results_names"].append(child.attrib["name"])
		# content
		for i,row in enumerate(xmlElt[1:]):
			lstResult = []
			for result in row:
				lstResult.append(float(result.text))
			dicResults[lstParam[i]] = lstResult
		return dicResults
	
	#-------------#
	# Data saving #
	#-------------#
	
	def save_results(self, strFileName, dicResults, path=''):
		lstHeader = []
		lstParamIdx = []
		print(path)
		strFileName = path + strFileName
		lstHeader = list(dicResults["param_names"])
		lstHeader.extend(dicResults["results_names"])
		del dicResults["param_names"]
		del dicResults["results_names"]
		lstRows = []
		strHeader = " ".join(lstHeader)
		for param, result in dicResults.iteritems():
			row = list(param)
			row.extend(result)
			lstRows.append(row)
		np.savetxt(	strFileName, np.array(lstRows, dtype=str), fmt='%s',
					delimiter=" ", header=strHeader )
		return strFileName
	
	def save_xml(self, strFileName, xmlElt):
		xmlTree = xmlet.ElementTree(xmlElt)
		xmlTree.write(strFileName)
	
	def to_string(self, xmlElt):
		return xmlet.tostring(xmlElt)
	
