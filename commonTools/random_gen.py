#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Random generators used in several projects """

import numpy as np


__all__ = [ "rand_float_trunc_pl", "rand_int_trunc_exp" ]


#
#---
# Random generators
#------------------------

def rand_float_trunc_pl(rMax,rMin,tau,nSamples):
	''' Power-lay distributed random floats:
	distribution F(x) = A * (tau-1)*x^{-tau} between rMax and rMin '''
	lstRndUnif = np.random.uniform(0,1,nSamples)
	return np.power((np.power(rMax,1-tau)-1)*lstRndUnif+1,1/(1-tau))

def rand_int_trunc_exp(nMin,nMax,rLambda=0.2,nSamples=1):
	''' Power-lay distributed random integers:
	distribution F(x) = A * e^{-x/rLambda} between rMax and rMin '''
	lstRndUnif = np.multiply(np.random.uniform(0,1,nSamples),1-np.exp(-1.0/rLambda))
	return np.floor(nMin+np.multiply((nMin-nMax)*rLambda,np.log(1.0-lstRndUnif))).astype(int)
