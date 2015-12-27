============
Installation
============


Simple install
==============

Under most linux distributions, the simplest way is to install `pip <https://pip.pypa.io/en/stable/installing/>` and `git <https://git-scm.com/>`_, then simply type into a terminal:
>>> sudo pip install git+https://github.com/Silmathoron/ResCompPackage.git

There are ways for windows users, but the graph library won't work anyway... yet.


Dependencies
============

This package depends on several libraries (the number varies according to which modules you want to use).

Basic dependencies
------------------

Regardless of your needs, the following libraries are required:
	* `numpy <http://www.numpy.org/>`_ 
	* `scipy <http://www.scipy.org/scipylib/index.html>`_
	* `matplotlib <http://matplotlib.org/>`_
	* `graph_tool <http://graph-tool.skewed.de>`_
	* `pyside <@todo>`_
..	* or `igraph <http://igraph.org/>`_
..	* or `networkx <https://networkx.github.io/>`_

.. note::
    If they are not present on your computer, ``pip`` will directly try to install the three first libraries, however:

    * lapack is necessary for scipy and pip cannot install it on its own
    * you will have to install the graph library yourself (only networkx can be installed directly using ``pip``)
