#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" IO functions """

import os



#
#---
# Files and directories
#------------------------

def make_dirs(lstDirectories):
	''' create the desired directory '''
	for string in lstDirectories:
		try:
			os.makedirs(string)
		except OSError:
			if not os.path.isdir(string):
				raise


#
#---
# Graph saving
#-----------------

## to file

def save_reservoir(graph, path=""):
	''' get the neighbours of each vertex
	slow!
	@todo: test csr -> lil, then join '''
	nNodes = graph.get_graph().num_vertices()
	strList = ""
	dicProp = graph.get_dict_properties()
	strName = path + graph.get_name()
	with open(strName,"w") as fileNeighbourList:
		for key, value in dicProp.iteritems():
			fileNeighbourList.write("# {} {}\n".format(key,value))
		for v1 in graph.get_graph().vertices():
			fileNeighbourList.write("{}".format(graph.get_graph().vertex_index[v1]))
			for e in v1.out_edges():
				rWeight = graph.get_graph().edge_properties["type"][e]
				if "weight" in graph.get_graph().edge_properties.keys():
					# on multiplie les poids du graphe pour avoir les arcs négatifs
					rWeight *= graph.get_graph().edge_properties["weight"][e]
				fileNeighbourList.write(" {};{}".format(graph.get_graph().vertex_index[e.target()],rWeight))
			fileNeighbourList.write("\n")
	return strName[strName.rfind("/")+1:]

def save_connect(connect, path, graph_name=''):
	fileName = path +  connect.get_name() + '_' + graph_name
	strHeader = "# InhibFrac {}\n# Density {}\n".format(connect.dicProperties["InhibFrac"], connect.dicProperties["Density"])
	with open(fileName,"w") as fileConnect:
		fileConnect.write(strHeader)
		fileConnect.write(connect.get_list_neighbours())
	return fileName[fileName.rfind("/")+1:]


#
#---
# Socket communication string
#-------------------------------

def csr_arrays(csrMat):
	arrData = csrMat.data
	arrIndices = csrMat.indices
	arrIndptr = csrMat.indptr
	return arrData, arrIndices, arrIndptr

def mat_to_string(csrMat, strId, strStorageClass="V"):
	arrData, arrIndices, arrIndptr = csr_arrays(csrMat)
	strShape = "{} {}".format(*csrMat.shape)
	strData = " ".join(arrData.astype(str))
	strIndices = " ".join(arrIndices.astype(str))
	strIndptr = " ".join(arrIndptr.astype(str))
	strMat = "MATRIX,{0},{1},{2};{3};{4};{5}\r\n".format(strId, strStorageClass, strShape, strData, strIndices, strIndptr)
	return strMat
