..  Copyright (C)  Brad Miller, David Ranum, Jeffrey Elkner, Peter Wentworth, Allen B. Downey, Chris
    Meyers, and Dario Mitchell.  Permission is granted to copy, distribute
    and/or modify this document under the terms of the GNU Free Documentation
    License, Version 1.3 or any later version published by the Free Software
    Foundation; with Invariant Sections being Forward, Prefaces, and
    Contributor List, no Front-Cover Texts, and no Back-Cover Texts.  A copy of
    the license is included in the section entitled "GNU Free Documentation
    License".

Depth First Search Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~


The general running time for depth first search is as follows. The loops
in ``dfs`` both run in :math:`O(V)`,
not counting what happens in ``dfsvisit``, since they are executed once
for each vertex in the graph. In ``dfsvisit`` the loop is executed once for each edge in the adjacency
list of the current vertex. Since ``dfsvisit`` is only called
recursively if the vertex is white, the loop will execute a maximum of
once for every edge in the graph or :math:`O(E)`. So, the total time
for depth first search is :math:`O(V + E)`.

