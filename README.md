# ExploreCoursesGraph

Generates a graph of Stanford courses and their prerequisites.

# Usage
```python
from grapher import Graph

course_graph = Graph("2021-2022")
course_graph.graph_depts("PHYSICS")
```

Output:
![alt text](https://github.com/FlyingWorkshop/ExploreCoursesGraph/blob/main/physics.gv.png)


# Limitations

To my knowledge, there is no structured data that contains a list of prerequisites for Stanford courses. Consequently, course prerequisite information had to be parsed directly from raw course descriptions. This introduced a host of problems (e.g. typos like "STAT 116" instead of "STATS 116"; mentions of courses that no longer exist like "CME 103" and "CHEM 31X"; vagueries like "a basic understanding of undergraduate physics" that don't map to a single course or suite of courses). To overcome this, I deployed a small arsenal of strategies to scrape, infer, and correct various mentions of prerequisites. While this method works for the vast majority of courses, there are certain shortcomings. In the example below, for instance, the node for "MATH 20" does not connect to the node for "MATH 21" even though they are clearly related. No edge is formed between the two nodes, because the 2021-2022 course description for "MATH 21" doesn't explicitly mention prerequisites. For the parser to acknowledge prerequisites, the word "prerequisite" must appear in some form or another. 

On the whole however, I feel that the display is fairly comprehensive.
