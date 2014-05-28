..  Copyright (C)  Brad Miller, David Ranum, Jeffrey Elkner, Peter Wentworth, Allen B. Downey, Chris
    Meyers, and Dario Mitchell.  Permission is granted to copy, distribute
    and/or modify this document under the terms of the GNU Free Documentation
    License, Version 1.3 or any later version published by the Free Software
    Foundation; with Invariant Sections being Forward, Prefaces, and
    Contributor List, no Front-Cover Texts, and no Back-Cover Texts.  A copy of
    the license is included in the section entitled "GNU Free Documentation
    License".

Performance of Python Data Structures
-------------------------------------

Now that you have a general idea of Big-O notation
and the differences between the different functions, our goal in this
section is to tell you about the Big-O performance for the operations on
Python lists and dictionaries. We will then show you some timing
experiments that illustrate the costs and benefits of using certain
operations on each data structure. It is important for you to understand
the efficiency of these Python data structures because they are the
building blocks we will use as we implement other data structures in the
remainder of the book. In this section we are not going to explain why
the performance is what it is. In later chapters you will see some
possible implementations of both lists and dictionaries and how the
performance depends on the implementation.
