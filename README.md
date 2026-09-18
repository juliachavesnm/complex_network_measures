# Complex Network Measures

Implementation of structural and centrality measures for complex networks in Python, with validation against established NetworkX implementations where applicable.

## Overview

This repository contains from-scratch implementations of commonly used measures for the analysis of complex networks. The implementations operate primarily on unweighted, undirected graphs represented through adjacency matrices and adjacency lists.

The project was developed to study the mathematical definitions and computational implementation of network measures rather than relying exclusively on high-level library functions.

## Implemented Measures

The following network measures are implemented:

* Degree
* Shortest path length
* Characteristic path length
* Global efficiency
* Local efficiency
* Clustering coefficient
* Transitivity
* Modularity
* Closeness centrality
* Betweenness centrality
* Within-module degree z-score
* Participation coefficient
* Average neighbor degree
* Assortativity coefficient

Auxiliary functions are also provided for graph representation, shortest-path computation, and counting shortest paths.

## Methodology

The implementations are based on mathematical formulations from the complex-network literature and were tested using example connected and disconnected graphs.

Where an equivalent implementation is available in [NetworkX](https://networkx.org/), results were compared against the corresponding NetworkX measure.

Some measures were implemented directly from their mathematical definitions when no directly equivalent NetworkX implementation was used.

Detailed methodological notes and mathematical formulations are available in [`docs/methodology.md`](docs/methodology.md).

## Requirements

* Python 3.x
* NumPy
* NetworkX

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

Import the desired functions from the main module:

```python
from src.network_measures import graus, clustering, transitividade
```

The functions generally operate on adjacency representations and auxiliary vectors such as node degrees or community assignments, depending on the measure.

Example:

```python
degrees = graus(graph)

clustering_coefficient = clustering(graph, degrees)

transitivity = transitividade(graph, degrees)
```

See [`docs/methodology.md`](docs/methodology.md) for the expected inputs and mathematical definitions of each measure.

## Validation

The implementations were compared with NetworkX whenever an equivalent function was available.

The comparisons showed agreement for measures including:

* Degree
* Shortest path length
* Clustering coefficient
* Characteristic path length
* Transitivity
* Average neighbor degree
* Assortativity coefficient

For measures with different definitions or no directly equivalent NetworkX implementation, validation was performed against the corresponding mathematical formulation.

## Data

Two example graphs are included:

* `connected_graph.txt` — connected network
* `disconnected_graph.txt` — disconnected network

These examples are used to evaluate how the implementations behave under different network structures, including the presence of unreachable nodes.

## References

The mathematical formulations used in this project are based on the complex-network literature included in the [`reference/`](reference/) directory.
