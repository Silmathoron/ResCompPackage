=====================
Exploring phase space
=====================

Principle
=========

This module interacts directly with Nicolas' soft (NS) in the following fashion:
* networks (reservoirs and connectivities) are sent,
* the parameters of the neurons/connections are also sent,
* NS performs the evaluation of the system,
* it sends the results back.


Components
==========

To perform the whole procedure, the module uses the following component:
* a :class:`~rescomp.Psx` instance that manages the other objects;
* an explorer (:class:`~rescomp.PSX.GridSearcher` or :class:`~rescomp.PSX.Metropolis`), which sample regions of phase space that should be tested;
* a communicator (:class:`~rescomp.PSX.CommPSX`), which manages the transfer back and forth between the module and NS;
* translators (:class:`~rescomp.ioClasses.XmlHandler`) which convert data to and from common xml strings.

.. note:
	The explorer and communicator are running concurrently on two separate processes; each contains an instance of :class:`~rescomp.ioClasses.XmlHandler` to perform the required conversions.


The communicator
================

This is one of the most annoying objects in the library. I uses two different tools to communicate with the other components:
* a :class:`~multiprocessing.Pipe` to send or receive objects aand instructions to/from the explorer (the client)
* a socket protocol to send/receive xml strings to/from NS (the server).

The :class:`~multiprocessing.Pipe` is contained in the `connectionComm` attribute (information using this channel is processed continuously in a first thread), whereas the communication with the server is performed internally in a second thread.
