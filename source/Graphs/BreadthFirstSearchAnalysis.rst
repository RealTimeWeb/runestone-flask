..  Copyright (C)  Brad Miller, David Ranum, Jeffrey Elkner, Peter Wentworth, Allen B. Downey, Chris
    Meyers, and Dario Mitchell.  Permission is granted to copy, distribute
    and/or modify this document under the terms of the GNU Free Documentation
    License, Version 1.3 or any later version published by the Free Software
    Foundation; with Invariant Sections being Forward, Prefaces, and
    Contributor List, no Front-Cover Texts, and no Back-Cover Texts.  A copy of
    the license is included in the section entitled "GNU Free Documentation
    License".

Breadth First Search Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before we continue with other graph algorithms let us analyze the run
time performance of the breadth first search algorithm. The first thing
to observe is that the while loop is executed,
at most, one time for each vertex in the graph :math:`|V|`. You can
see that this is true because a vertex must be white before it can be
examined and added to the queue. This gives us :math:`O(V)` for the
while loop. The for loop, which is nested inside the while is executed at most once for each edge in the graph,
:math:`|E|`. The reason is that every vertex is dequeued at most once
and we examine an edge from node :math:`u` to node :math:`v` only
when node :math:`u` is dequeued. This gives us :math:`O(E)` for the
for loop. combining the two loops gives us :math:`O(V + E)`.

Of course doing the breadth first search is only part of the task.
Following the links from the starting node to the goal node is the other
part of the task. The worst case for this would be if the graph was a
single long chain. In this case traversing through all of the vertices
would be :math:`O(V)`. The normal case is going to be some fraction of
:math:`|V|` but we would still write :math:`O(V)`.

Finally, at least for this problem, there is the time required to build
the initial graph. We leave the analysis of the ``buildGraph`` function
as an exercise for you.
