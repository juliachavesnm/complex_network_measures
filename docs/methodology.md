# Methodology

This document details the implementation of the network-analysis functions in this repository and describes how their results were evaluated.

The implementations were developed from the mathematical formulations provided in the reference literature, particularly the formulations presented by Rubinov and Sporns, and were compared with equivalent functions from the [NetworkX](https://networkx.org/) library whenever an equivalent implementation was available.

The functions operate on different graph representations depending on the measure. These include adjacency lists stored as dictionaries, binary adjacency matrices, degree vectors, shortest-path dictionaries, and module/community assignments.

---

## 1. Degree

### Implementation

```python
def degree(adjacency_list):
    degrees = []

    for i in range(len(adjacency_list)):
        degrees.append(len(adjacency_list[i]))

    return degrees
```

The function uses a dictionary whose keys correspond to vertices and whose values contain the respective neighboring vertices. The degree of each vertex can therefore be obtained directly by applying `len()` to its list of neighbors.

The output is a vector of size `n`, where `n` is the number of vertices. The `i`-th entry corresponds to the degree of vertex `i`.

### Validation

The result was compared with `nx.degree()` from NetworkX and was found to be equivalent.

---

## 2. Shortest Path Length

### Implementation

```python
def shortest_path_length(adjacency_matrix, source, target):
    if source == target:
        return 0

    found = False
    distance = 0
    visited = []
    to_visit = [source]

    while len(to_visit) > 0 and not found:
        current = to_visit.pop()
        distance += 1

        for j in range(len(adjacency_matrix[current])):
            if adjacency_matrix[current][j] == 1:
                if j == target:
                    found = True
                    break
                elif j not in visited:
                    to_visit.append(j)
                    visited.append(j)

    if not found:
        return "infinite"
    else:
        return distance
```

This function performs a breadth-first search on an unweighted adjacency matrix. It receives the adjacency matrix, a source vertex, and a target vertex.

If the source and target vertices are identical, the function returns zero. If no path exists between them, it returns `"infinite"`.

Otherwise, the implementation explores the neighbors of the current vertex and adds previously unvisited vertices to the search structure. The search is terminated when the target vertex is reached, using the `found` indicator.

### Validation

The results are consistent with those obtained using:

```python
nx.shortest_path_length(graph, i, j)
```

from NetworkX.

An additional feature of the implementation is its explicit treatment of disconnected vertices. NetworkX raises an error when no path exists, whereas this implementation returns `"infinite"`.

---

## 3. Number of Triangles

### Implementation

```python
def triangles(adjacency_matrix, i):
    triangles_i = 0
    n = len(adjacency_matrix[0])

    for j in range(n):
        for h in range(n):
            triangles_i += (
                int(adjacency_matrix[i][j])
                * int(adjacency_matrix[i][h])
                * int(adjacency_matrix[j][h])
            )

    triangles_i = triangles_i / 2

    return triangles_i
```

This function is a direct application of the formulation provided in Rubinov and Sporns.

It receives an unweighted, undirected adjacency matrix and a vertex `i`, around which the number of triangles is calculated.

Two nested loops are used to determine whether vertices `j` and `h` are both connected to `i` and whether they are connected to each other. When all three connections exist, the combination forms a triangle involving vertex `i`.

The final sum is divided by two to account for the double counting that occurs in an undirected graph.

### Validation

The output is equivalent to:

```python
nx.triangles(graph, i)
```

from NetworkX.

---

## 4. Characteristic Path Length

### Implementation

```python
def characteristic_path_length(adjacency_matrix, distances, n):
    n = len(distances)
    total = 0

    for i in range(n):
        for j in range(n):
            try:
                total += distances[(i, j)]
            except:
                continue

    characteristic_length = total / n

    return characteristic_length
```

The characteristic path length is calculated as an average of the shortest paths between pairs of vertices.

The implementation uses the `shortest_paths()` function described below to obtain a dictionary containing the shortest paths between vertex pairs.

Paths that are `"infinite"` are ignored through the `try/except` structure. This allows disconnected graphs to be handled without including nonexistent paths in the average.

For optimization, redundant paths are not computed separately. Because the graph is undirected, paths `(i, j)` and `(j, i)` are equivalent. The shortest-path dictionary therefore stores only one of these combinations.

As a consequence, a simple average over the stored paths can be performed without separately accounting for `(i, j)` and `(j, i)`.

### Validation

The result was compared with:

```python
nx.average_shortest_path_length(graph)
```

and produced the same result for the tested graphs.

### All-Pairs Shortest Paths

The following auxiliary function generates the shortest-path dictionary used by several other measures:

```python
def shortest_paths(adjacency_matrix, n):
    paths = {}
    visited_pairs = []

    for a in range(n):
        for b in range(n):
            if [a, b] in visited_pairs or [b, a] in visited_pairs:
                continue

            visited_pairs.append([a, b])

            if a == b:
                paths[a, b] = 0
            else:
                paths[a, b] = shortest_path_length(
                    adjacency_matrix, a, b
                )

    return paths
```

The function avoids computing redundant pairs by checking whether either `(a, b)` or `(b, a)` has already been evaluated.

---

## 5. Global Efficiency

### Implementation

```python
def global_efficiency(n, distances):
    n = int(n)
    total_i = 0

    for i in range(n):
        total_j = 0

        for j in range(n):
            if i == j:
                continue

            try:
                d_ij = distances[i, j]
            except:
                d_ij = distances[j, i]

            if d_ij != "infinite":
                total_j += 1 / d_ij

        total_i += total_j / (n - 1)

    efficiency = total_i / n

    return efficiency
```

Global efficiency is calculated as the average of the efficiencies of individual vertices.

For each vertex `i`, its efficiency is given by the sum of the inverse shortest-path distances between `i` and every other vertex, divided by `n - 1`.

The function receives `n`, the number of vertices, and the shortest-path dictionary generated by `shortest_paths()`.

Because the shortest-path dictionary contains only one of `(i, j)` and `(j, i)`, the implementation uses `try/except` to retrieve whichever representation is available.

When two vertices are disconnected, their shortest-path distance is `"infinite"`. Its inverse is therefore treated as zero, so no contribution is added to the sum.

The `i == j` case is also ignored because the formulation specifies that `j ≠ i`.

After calculating the sum over `j`, the result is divided by `n - 1` to obtain the efficiency associated with vertex `i`. The final global efficiency is obtained by averaging over all `n` vertices.

### NetworkX comparison

The value returned by this implementation does **not** initially match the corresponding NetworkX function.

Testing showed that the two values become equal if the final division is performed by `n - 1` rather than `n`.

However, the division by `n` was retained in the implementation because it follows the formulation provided in the reference article used for the project.

This distinction is intentionally documented rather than silently modifying the implementation to reproduce the NetworkX result.

---

## 6. Clustering Coefficient

### Implementation

```python
def clustering(adjacency_matrix, degree):
    total = 0

    for i in range(len(adjacency_matrix)):
        triangles_i = triangles(adjacency_matrix, i)

        if degree[i] > 1:
            total += (
                2 * triangles_i
            ) / (
                degree[i] * (degree[i] - 1)
            )

    total = total / len(adjacency_matrix[0])

    return total
```

The clustering coefficient is calculated according to the formulation presented by Rubinov and Sporns.

For each vertex, the function first obtains the number of triangles associated with that vertex using `triangles()`.

Its degree is obtained from the degree vector, whose `i`-th entry corresponds to the degree of vertex `i`.

The local clustering coefficient is then calculated and added to a cumulative sum. Finally, the sum is divided by the total number of vertices, producing the average clustering coefficient for the graph.

---

## 7. Transitivity

### Implementation

```python
def transitivity(adjacency_matrix, degree):
    numerator = 0
    denominator = 0

    for i in range(len(adjacency_matrix)):
        k_i = degree[i]
        triangles_i = triangles(adjacency_matrix, i)

        numerator += 2 * triangles_i
        denominator += k_i * (k_i - 1)

    try:
        transitivity_value = numerator / denominator
    except:
        transitivity_value = 0

    return transitivity_value
```

Transitivity is calculated according to the formulation provided in the reference material.

For each vertex `i`, `t_i` denotes the number of triangles around the vertex and `k_i` denotes its degree.

The implementation defines two variables:

* `numerator`, corresponding to the sum of twice the number of triangles;
* `denominator`, corresponding to the sum of `k_i(k_i - 1)`.

The function receives an unweighted, undirected adjacency matrix and the degree vector.

For every vertex, the number of triangles is calculated using `triangles()`. Twice this value is added to the numerator, while the corresponding degree term is added to the denominator.

A `try/except` block handles the case in which the denominator is zero. This occurs, for example, when all vertices have degree one. In this case, transitivity is defined as zero.

### Validation

The output agrees with the equivalent NetworkX implementation.

---

## 8. Local Efficiency

### Implementation

```python
def local_efficiency(adjacency_list, adjacency_matrix, degree):
    total = 0

    for i in range(len(adjacency_list)):
        new_graph = {}
        vertices = adjacency_list[i]
        new_graph[i] = vertices

        for a in vertices:
            neighbors = [i]

            for v in adjacency_list[a]:
                if v in vertices:
                    neighbors.append(v)

            new_graph[a] = sorted(neighbors)

        distances = shortest_paths(
            make_matrix(adjacency_matrix, new_graph),
            len(make_matrix(adjacency_matrix, new_graph))
        )

        for j in range(len(adjacency_matrix)):
            for h in range(len(adjacency_matrix)):
                if j == i or j == h:
                    continue

                try:
                    distance = distances[j, h]
                except:
                    distance = distances[h, j]

                if distance != "infinite" and degree[i] >= 2:
                    total += (
                        adjacency_matrix[i][j]
                        * adjacency_matrix[i][h]
                        * (1 / distance)
                    )

        if degree[i] > 1:
            efficiency_i = total / (
                degree[i] * (degree[i] - 1)
            )
        else:
            efficiency_i = 0

        total = 0

    efficiency = efficiency_i / len(adjacency_matrix[0])

    return efficiency
```

Local efficiency is calculated according to the formulation in the reference material.

For each vertex `i`, the quantity `d_jh(N_i)` represents the shortest path between vertices `j` and `h` restricted to the subgraph formed by the neighbors of `i`.

To calculate these restricted shortest paths, the implementation constructs a smaller graph for each vertex.

For each `i`, a new dictionary is created containing `i` and its neighbors, together with the connections among those vertices. This dictionary is then converted into a binary adjacency matrix using `make_matrix()` so that the previously implemented shortest-path functions can be reused.

After the restricted graph has been constructed, `shortest_paths()` is used to calculate the corresponding shortest paths.

The degree of `i` is then retrieved from the degree vector, and the local-efficiency expression is applied.

Vertices with fewer than two neighbors cannot form the relevant neighbor pairs, so their local efficiency is set to zero.

### Auxiliary Matrix Construction

```python
def make_matrix(adjacency_matrix, adjacency_list):
    matrix = []

    for i in range(len(adjacency_matrix)):
        row = n * [0]

        if i in adjacency_list.keys():
            for v in adjacency_list[i]:
                row[v] += 1

        matrix.append(row)

    return matrix
```

`make_matrix()` takes a base binary adjacency matrix and a dictionary specifying a subset of connections.

It creates a new adjacency matrix with the same dimensions as the original matrix, but containing only the connections specified in the dictionary.

This allows the restricted neighborhood graphs required for local efficiency to be represented in the same format used by the shortest-path functions.

---

## 9. Modularity

### Implementation

```python
def modularity(adjacency_matrix, degree, modules, l):
    Q = 0

    for i in range(len(adjacency_matrix)):
        for j in range(len(adjacency_matrix)):
            if modules[i] == modules[j]:
                Q += (
                    adjacency_matrix[i][j]
                    - ((degree[i] * degree[j]) / l)
                )

    Q = Q / l

    return Q
```

Modularity is calculated using the formulation provided in the reference material.

The function receives:

* the binary adjacency matrix;
* the degree vector;
* the module assignment of each vertex;
* `l`, the number of links used in the formulation.

For an undirected graph, `l` is defined as `2m`, where `m` is the number of edges.

The module-assignment condition implements the delta term in the modularity expression: when `m_i != m_j`, the contribution is zero, so the summation is performed only for pairs of vertices belonging to the same module.

For vertices within the same module, the function subtracts the expected connection term from the observed adjacency value and accumulates the result. The final sum is then divided by `l`.

### Validation

No directly equivalent library implementation was identified for the specific formulation used in the project.

As a basic consistency check, the resulting modularity values were expected to lie between `-1` and `1`, and this was observed in the tests performed.

---

## 10. Closeness Centrality

### Implementation

```python
def closeness(i, distances, n):
    total = 0

    for j in range(n):
        try:
            d_ij = distances[i, j]
        except:
            d_ij = distances[j, i]

        if d_ij != "infinite":
            total += d_ij

    L_i = total / (n - 1)

    return 1 / L_i
```

Closeness centrality is defined as the inverse of the characteristic path length associated with a given vertex.

The function receives:

* vertex `i`;
* the shortest-path dictionary;
* the number of vertices `n`.

For every vertex `j`, the corresponding shortest path is retrieved from the dictionary. Because the dictionary does not contain both `(i, j)` and `(j, i)`, the function checks both possibilities.

Infinite paths are excluded from the sum.

After the shortest paths are summed, the result is divided by `n - 1`, producing the characteristic path length associated with vertex `i`, denoted by `L_i`.

The function then returns:

```text
1 / L_i
```

which corresponds to closeness centrality according to the formulation used in the project.

---

## 11. Betweenness Centrality

### Implementation

```python
def betweenness_centrality(
    adjacency_matrix,
    adjacency_list,
    i,
    n,
    distances
):
    total = 0

    for h in range(len(adjacency_matrix[0])):
        for j in range(len(adjacency_matrix[0])):
            if h == j or h == i or j == i:
                continue

            try:
                d_jh = distances[j, h]
            except:
                d_jh = distances[h, j]

            if d_jh == 1:
                phi = 1
                phi_i = 0
            else:
                phi = number_of_shortest_paths(
                    adjacency_list, j, h, distances
                )

                phi_i = (
                    number_of_shortest_paths(
                        adjacency_list, i, j, distances
                    )
                    * number_of_shortest_paths(
                        adjacency_list, i, h, distances
                    )
                )

            if phi == 0:
                continue

            total += phi_i / phi

    normalization = 1 / ((n - 1) * (n - 2))

    return normalization * total
```

Betweenness centrality is calculated according to the formulation given by Rubinov and Sporns.

The function receives:

* the adjacency matrix;
* the adjacency-list representation;
* vertex `i`;
* the number of vertices `n`;
* the shortest-path dictionary.

For each pair of vertices `j` and `h`, excluding cases where either is equal to `i` or where `j == h`, the function determines the number of shortest paths between `j` and `h`.

If the shortest path has length one, there is exactly one direct path between the vertices.

Otherwise, the auxiliary function `number_of_shortest_paths()` is used.

The number of shortest paths passing through vertex `i` is obtained from the combinatorial principle that such paths correspond to the product of:

* the number of shortest paths from `j` to `i`; and
* the number of shortest paths from `i` to `h`.

The resulting ratio is accumulated over all vertex pairs and multiplied by the normalization factor:

```text
1 / ((n - 1)(n - 2))
```

### Counting Shortest Paths

```python
def number_of_shortest_paths(adjacency_list, a, b, distances):
    visited = []
    to_visit = []
    current = None
    count = 0

    paths = {}
    number_of_paths = 0

    if a == b:
        return 0

    try:
        shortest_distance = distances[a, b]
    except:
        shortest_distance = distances[b, a]

    to_visit.append([a, 0])
    visited.append([a, 0])

    while len(to_visit) > 0:
        current = to_visit.pop()
        count = current[1]
        current = current[0]
        count += 1

        if count <= shortest_distance:
            for e in adjacency_list[current]:

                if e == b:
                    number_of_paths += 1
                    paths[number_of_paths] = count

                elif [e, count] not in visited:
                    to_visit.append([e, count])
                    visited.append([e, count])

    return number_of_paths
```

This auxiliary function counts the number of shortest paths between two vertices using a depth-first search.

The length of the shortest path between the two vertices is first retrieved from the shortest-path dictionary. This distance is used to limit the search.

If a path being explored exceeds the known shortest-path length, it is not continued and therefore cannot be counted as a shortest path.

The `to_visit` list operates as a stack, providing the depth-first search behavior. Each item stores both the current vertex and the number of steps taken to reach it.

Whenever the target vertex is reached within the shortest-path limit, the number of shortest paths is incremented.

A `paths` dictionary also records the paths found and their lengths. Although this dictionary is not returned, it was useful during debugging to verify that the paths being counted were shortest paths and that all shortest paths were being identified.

---

## 12. Within-Module Degree z-Score

### Implementation

```python
def within_module_z_score(adjacency_list, n, modules, i):
    connections = {}

    for j in range(n):
        connections[j] = []
        module = modules[j]

        for a in adjacency_list[j]:
            if modules[a] == module:
                connections[j].append(a)

    k_m_i = len(connections[i])

    k = []

    for j in range(n):
        k.append(len(connections[j]))

    k_mean = statistics.mean(k)
    std = statistics.stdev(k)

    z = (k_m_i - k_mean) / std

    return z
```

The module assignment vector is used to determine the number of within-module connections for each vertex.

For every vertex, the function examines its neighbors and retains those that belong to the same module as the vertex itself.

The resulting `connections` dictionary records the within-module neighbors associated with each vertex.

For the target vertex `i`, the number of within-module connections is denoted by `k_m_i`.

The distribution of within-module degrees across all vertices is then used to calculate the mean and standard deviation using Python's `statistics` library.

Finally, the within-module degree z-score is obtained by applying the formulation from the reference article:

```text
z = (k_m_i - mean(k_m)) / std(k_m)
```

---

## 13. Participation Coefficient

### Implementation

```python
def participation_coefficient(degree, adjacency_list, modules, i):
    total = 0

    number_of_modules = len(set(modules))

    for index in range(number_of_modules):
        module_id = modules[index]
        module_vertices = []

        for a in range(len(modules)):
            if modules[a] == module_id:
                module_vertices.append(a)

        connections = []

        for vertex in adjacency_list[i]:
            if vertex in module_vertices:
                connections.append(vertex)

        k_m_i = len(connections)
        k_i = degree[i]

        total += (k_m_i / k_i) ** 2

    participation = 1 - total

    return participation
```

The participation coefficient is calculated according to the formulation in the reference material.

The function first determines the number of distinct modules by converting the module-assignment list into a set.

For each module, the vertices belonging to that module are identified. The function then examines the neighbors of vertex `i` and determines which of them belong to the module under consideration.

The number of connections from vertex `i` to module `m` is represented by `k_m_i`, while `k_i` represents the total degree of vertex `i`.

For each module, the squared proportion:

```text
(k_m_i / k_i)^2
```

is added to the cumulative sum.

After all modules have been considered, the participation coefficient is calculated as:

```text
P_i = 1 - sum_m (k_m_i / k_i)^2
```

---

## 14. Average Neighbor Degree

### Implementation

```python
def average_neighbor_degree(adjacency_list, i, degree):
    total = 0

    for vertex in adjacency_list[i]:
        total += degree[vertex]

    total = total / degree[i]

    return total
```

Average neighbor degree represents the mean degree of the neighbors of a given vertex `i`.

The function receives:

* an adjacency-list dictionary;
* vertex `i`;
* the degree vector.

For each neighbor of `i`, its degree is added to a cumulative sum.

The sum is then divided by the degree of vertex `i`, producing the average degree of its neighbors.

### Validation

The result was compared with:

```python
nx.average_neighbor_degree(graph)
```

from NetworkX, and the returned values were equivalent for the tested graphs.

---

## 15. Assortativity Coefficient

### Implementation

```python
def assortativity_coefficient(l, degree, adjacency_matrix):
    sum1 = 0
    sum2 = 0
    sum3 = 0

    for i in range(len(adjacency_matrix[0])):
        for j in range(len(adjacency_matrix[0])):
            if adjacency_matrix[i][j] == 1:
                sum1 += degree[i] * degree[j]
                sum2 += (1 / 2) * (degree[i] + degree[j])
                sum3 += (1 / 2) * (
                    degree[i] ** 2 + degree[j] ** 2
                )

    numerator = (
        sum1 / l
        - (sum2 / l) ** 2
    )

    denominator = (
        sum3 / l
        - (sum2 / l) ** 2
    )

    assortativity = numerator / denominator

    return assortativity
```

The assortativity coefficient is a direct implementation of the formula provided in the reference material.

The function receives:

* `l`, the number of links as defined in the formulation;
* `degree`, the degree vector;
* `adjacency_matrix`, the binary adjacency matrix.

Three separate sums are calculated.

### `sum1`

Computes the sum of the products of the degrees of connected vertices:

```text
Σ k_i k_j
```

### `sum2`

Computes the sum of the mean degree of each connected pair:

```text
Σ (k_i + k_j) / 2
```

### `sum3`

Computes the sum of the mean squared degrees:

```text
Σ (k_i² + k_j²) / 2
```

These quantities are then substituted into the assortativity expression:

```text
[sum1/l - (sum2/l)²]
--------------------------------
[sum3/l - (sum2/l)²]
```

The numerator and denominator were kept as separate variables in the implementation for clarity.

### Validation

The resulting values agree with those returned by the equivalent NetworkX implementation.

---

# Handling Disconnected Vertices

After the original methodological report was written, minor changes were made to the implementations to prevent division-by-zero errors in cases involving disconnected vertices or vertices without neighbors.

These changes do not alter the general operation of the functions.

For measures that become undefined or cannot be computed for vertices without neighbors, the implementation returns `0` by default.

The handling of disconnected shortest paths is also explicit: shortest paths that do not exist are represented as `"infinite"` and are excluded from calculations where their contribution would otherwise be undefined.

---

# Validation Summary

The implementations were evaluated by comparison with NetworkX whenever a corresponding function was available.

The following measures produced results consistent with NetworkX in the tests performed:

* Degree
* Shortest path length
* Number of triangles
* Characteristic path length
* Transitivity
* Average neighbor degree
* Assortativity coefficient

Global efficiency deserves separate mention because its result depends on the final normalization used. The implementation follows the formulation from the reference article rather than modifying the expression to reproduce the NetworkX result.

Modularity was not directly compared with an equivalent library implementation. Instead, its output was checked against the expected range of the measure, and the values obtained in testing were within `[-1, 1]`.

For measures involving disconnected vertices or vertices with insufficient neighbors, explicit handling was added to avoid undefined operations and division-by-zero errors.

---

# References

The mathematical formulations used in this project are based on the article "Complex network measures of brain connectivity: uses and interpretations" by Rubinov and Sporns, 2010, that can be accessed [here](https://pubmed.ncbi.nlm.nih.gov/19819337/).
