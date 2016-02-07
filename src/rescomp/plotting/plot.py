#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Plotting functions """

import numpy as np
import itertools

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import Axes3D

from rescomp.plotting.custom_plt import palette



#-----------------------------------------------------------------------------#
# Plotting phase space
#-----------------------
#

def phase_space(filename, cols_var=[0], cols_result=[-1], col_size=None,
				heatmap=False):
	'''
	Plot the results of a phase space exploration.

	Parameters
	----------
	filename : string
		Complete path to the file.
	cols_var : lst of ints, optional (default : [0])
		Cols where the variables will be read (the first row by default)
	cols_result : list of ints, optional (default: [-1])
		Cols where the results are stored (last row by default)
	col_size : int, optional (default: None)
		Index of the column where the size of the marker is stored (in the
		Metropolis algorithm, this shows the number of times a bin has been
		visited).
	heatmaps : bool, optional (default: False)
		Whether phase space should be visualized using 2D heatmaps.
	'''
	# get data
	arrPS = np.loadtxt(filename)
	lstHeader = None
	with open(filename, 'r') as rfile:
		strHeader = rfile.readline()
		while not strHeader[0].isalpha():
			strHeader = strHeader[1:]
		lstHeader = strHeader.split(' ')
	arrCols = []
	# make different plots for each conditions
	if len(cols_var) > 1:
		fig, axes = _var_phase_space(arrCols, cols_var, cols_result, heatmap)
		cols_result = np.repeat(cols_result, len(axes)).tolist()
		if heatmap:
			for ax,cols in zip(axes,arrCols):
				col = cols_result.pop()
				x, y, z = arrPS[:,cols[0]], arrPS[:,cols[1]], arrPS[:,col]
				width = x.max()-x.min()
				height = y.max() - y.min()
				gridsize = (len(set(x))/2-1, len(set(y))/2-1)
				im = ax.hexbin(x/width, y/height, z, gridsize=gridsize, cmap=plt.get_cmap('gnuplot'))
				ax.set_aspect(1)
				ax.set_xticklabels([x*width for x in ax.get_xticks()])
				ax.set_yticklabels([y*height for y in ax.get_yticks()])
				ax.set_xlabel(lstHeader[cols[0]])
				ax.set_ylabel(lstHeader[cols[1]])
				divider = make_axes_locatable(ax)
				cax = divider.append_axes("right", size="5%", pad="1%")
				plt.colorbar(im, cax=cax)
		else: # 3D
			for ax,cols in zip(axes,arrCols):
				x, y, z = arrPS[:,cols[0]], arrPS[:,cols[1]], arrPS[:,cols[2]]
				s = arrPS[:,col_size] if col_size is not None else 15
				c = arrPS[:,cols_result.pop()]
				ax.scatter(x,y,z,c=c,s=s,cmap=plt.get_cmap('gnuplot'))
				ax.set_xlabel(lstHeader[cols[0]])
				ax.set_ylabel(lstHeader[cols[1]])
				ax.set_zlabel(lstHeader[cols[2]])
	else:
		fig, ax = plt.subplots()
		colors = np.linspace(0.05, 0.95, len(cols_result))
		for i,row in enumerate(cols_result):
			ax.plot(arrPS[cols_var[0]],arrPS[row])
			ax.set_xlabel(lstHeader[cols_var[0]])
			ax.set_ylabel(lstHeader[cols_result[i]])
	#~ fig.set_tight_layout(True)
	plt.show()

def phase_space_pca(filename, cols_result=[-1], cols_var=[0], variance=90.):
	pass


#-----------------------------------------------------------------------------#
# Tools
#-----------------------
#

def _var_phase_space(arrCols, cols_var, cols_result, heatmap):
	fig, axes = None, None
	if len(cols_var) == 2:
		fig, axes = plt.subplots(len(cols_result))
		arrCols.extend(cols_var)
	elif len(cols_var) > 2:
		num_dim = 2 if heatmap else 3
		kw = {} if heatmap else {'projection':'3d'}
		arrCols.extend(itertools.combinations(cols_var, num_dim))
		fig, axes = plt.subplots(len(arrCols), subplot_kw=kw)
	if not hasattr(axes, "__len__"):
		axes = [axes]
	return fig, axes

def _heatmap(ax, data):
	ax.pcolor(data)
	# put the major ticks at the middle of each cell
	ax.set_xticks(np.arange(data.shape[0])+0.5, minor=False)
	ax.set_yticks(np.arange(data.shape[1])+0.5, minor=False)
	# want a more natural, table-like display
	ax.invert_yaxis()
	ax.xaxis.tick_top()
	ax.set_xticklabels(data[0], minor=False)
	ax.set_yticklabels(data[1], minor=False)
