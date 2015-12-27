=========================================================
Welcome to the reservoir computing package documentation!
=========================================================

.. toctree::
   :hidden:

   self

.. user:

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   user/intro
   user/install
   user/psx


Overview
========

The Reservoir Computing package (rescomp) provides tools to study the efficiency of various neural networks (reservoirs) for a given task.


Main classes
------------

``rescomp`` uses two main classes:

:class:`~rescomp.GraphClass`
	provides a simple implementation over graphs objects from graph libraries (namely the addition of a name, management of detailed nodes and connection properties, and simple access to basic graph measurements).
:class:`~rescomp.InputConnect`
    a connectivity matrix that transfers a vector input onto the reservoir's neurons with specific conectivity patterns.

Components
----------

``rescomp`` is divided into several modules:
* GANET
	which allows the generation of various graphs and the study of their properties
* PSX (Phase Space eXplorer)
	which allows the mapping of the system's phase space to find the configurations leading to the best results
* AlgoGen (genetic algorithm module)
	to use evolution in order to find graphs displaying ever more efficient dynamics


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

