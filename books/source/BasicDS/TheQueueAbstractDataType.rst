..  Copyright (C)  Brad Miller, David Ranum, Jeffrey Elkner, Peter Wentworth, Allen B. Downey, Chris
    Meyers, and Dario Mitchell.  Permission is granted to copy, distribute
    and/or modify this document under the terms of the GNU Free Documentation
    License, Version 1.3 or any later version published by the Free Software
    Foundation; with Invariant Sections being Forward, Prefaces, and
    Contributor List, no Front-Cover Texts, and no Back-Cover Texts.  A copy of
    the license is included in the section entitled "GNU Free Documentation
    License".

The Queue Abstract Data Type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The queue abstract data type is defined by the following structure and
operations. A queue is structured, as described above, as an ordered
collection of items which are added at one end, called the “rear,” and
removed from the other end, called the “front.” Queues maintain a FIFO
ordering property. The queue operations are given below.

-  ``Queue()`` creates a new queue that is empty. It needs no parameters
   and returns an empty queue.

-  ``enqueue(item)`` adds a new item to the rear of the queue. It needs
   the item and returns nothing.

-  ``dequeue()`` removes the front item from the queue. It needs no
   parameters and returns the item. The queue is modified.

-  ``isEmpty()`` tests to see whether the queue is empty. It needs no
   parameters and returns a boolean value.

-  ``size()`` returns the number of items in the queue. It needs no
   parameters and returns an integer.

As an example, if we assume that ``q`` is a queue that has been created
and is currently empty, then :ref:`Table 1 <tbl_queueoperations>` shows the
results of a sequence of queue operations. The queue contents are shown
such that the front is on the right. 4 was the first item enqueued so it
is the first item returned by dequeue.

.. _tbl_queueoperations:

.. table:: **Table 1: Example Queue Operations**

    ============================ ======================== ================== 
             **Queue Operation**       **Queue Contents**   **Return Value** 
    ============================ ======================== ================== 
                 ``q.isEmpty()``                   ``[]``           ``True`` 
                ``q.enqueue(4)``                  ``[4]``                    
            ``q.enqueue('dog')``            ``['dog',4]``                    
             ``q.enqueue(True)``       ``[True,'dog',4]``                    
                    ``q.size()``       ``[True,'dog',4]``              ``3`` 
                 ``q.isEmpty()``       ``[True,'dog',4]``          ``False`` 
              ``q.enqueue(8.4)``   ``[8.4,True,'dog',4]``                    
                 ``q.dequeue()``     ``[8.4,True,'dog']``              ``4`` 
                 ``q.dequeue()``           ``[8.4,True]``          ``'dog'`` 
                    ``q.size()``           ``[8.4,True]``              ``2`` 
    ============================ ======================== ================== 


