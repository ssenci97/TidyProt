# A tool to retrieve and parse protein data from UniprotKB and NCBI
Several packages already allow to query and download data and are widely adopted by the scientific community [ref?!]
Here, we propose a simple and intuitive data structure and a toolkit to reshape data from NCBI and UniprotKB API.
The project aims at providing a toolkit with few dependencies, high stability, maximal data retrieval and simplest possible format.

## Tidyprot format
A simple relational database consisting of:
1. A table allocating data referring to the full entry
2. A table allocating annotations related to sequence ranges


