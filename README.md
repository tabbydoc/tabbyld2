# TabbyLD2

A web-based application to annotate relational tables and generate knowledge graphs.

## Version

0.3

## Preliminaries

#### Source tabular data description

A source (input) table represents a set of the same type entities in a relational form (a subset of the Cartesian product of *K*-data domains), where:
1.	*Attribute (a column name)* is a name of a data domain in a relationship schema.
2.	*Metadata (a schema)* is an ordered set of *K*-attributes of a relational table.
3.	*Tuple (a record)* is an ordered set of *K*-atomic values (one for each attribute of a relation).
4.	*Data (recordset)* is a set of tuples of a relational table.

A table of the same type entities (*a canonicalized form*) is a relational table in the third normal form (3NF), which contains an ordered set of *N*-rows and *M*-columns.

A table represents a set of entities of the same type, where:
1.	*Categorical column or Named entities column (NE-column)* contains names (text mentions) of some named entities.
2.	*Literal column (L-column)* contains literal values (e.g. dates, numbers).
3.	*Subject (thematic) column (S-column)* is a *NE*-column represented as a potential primary key and defines a subject of a source table.
4.	*Another (non-subject) columns* represent entity properties including their relationships with other entities.

**Assumption 1.** *The first row of a source table is a header containing attribute (column) names.*

**Assumption 2.** *All values of column cells in a source table have the same entity types and data types.*

#### Semantic table interpretation

**TabbyLD2** supports a semantic interpretation (annotation) of separate elements of a source table by using a target knowledge graph. [DBpedia](https://www.dbpedia.org/) is used as a target knowledge graph.

*A knowledge graph* is a graph of data intended to accumulate and convey knowledge of the real world, whose nodes represent entities of interest and whose edges represent relations between these entities ([*Hogan et al. Knowledge Graphs. ACM Computing Surveys, 54(4), 2022, 1-37*](https://arxiv.org/pdf/2003.02320.pdf)). So, a knowledge graph contains:
* *a set of entities*, where an entity is a description of some object of the real world, event or abstract concept (e.g., *"War and Peace"*, *"Leo Tolstoy"*);
* *a set of datatypes*, where a datatype is a primitive type of literal values (e.g., numbers, dates);
* *a set of properties*, where a property is a relationship name between an entity and some literal value or other entity (e.g., *"is-author"*, *"is-written-by"*);
* *a set of classes (types)*, where a class (type) is a set of entities with common properties (e.g., *"Book"*).

**Semantic Table Interpretation (STI)** is the process of recognizing and linking tabular data with external concepts from a target knowledge graph, which includes three main tasks:
1.	*Cell-Entity Annotation (CEA)* is a matching between values of table cells and entities (specific instances) from a target knowledge graph.
2.	*Column-Type Annotation (CTA)* is a matching between columns (or headers, if available) and classes or datatypes from a target knowledge graph.
3.	*Columns Property Annotation (CPA)* is a matching relationship between two columns (S-column and all other columns) and properties (relationships) from a target knowledge graph.

## Installation

First, you need to clone the project into your directory:

```
git clone https://github.com/tabbydoc/tabbyld2.git
```

Next, you need to install all requirements for this project:

```
pip install -r requirements.txt
```

*We recommend you to use Python 3.0 or more.*

#### Additional software

In addition to [SPARQL](https://www.w3.org/TR/rdf-sparql-query/) queries, we use [DBpedia Lookup](https://github.com/dbpedia/dbpedia-lookup) to find candidate entities from DBpedia. This service requires a separate installation.

## Directory Structure

* `datasets` contains datasets of source tables for experimental evaluation:
    * `T2Dv2` contains [T2Dv2 Gold Standard](http://webdatacommons.org/webtables/goldstandardV2.html) dataset, where `col_class_checked_fg.csv` was formed by [SemAIDA](https://github.com/alan-turing-institute/SemAIDA/tree/master/AAAI19/T2Dv2) and is fine-grained ground truth class for all columns.
    * `Tough_Tables` contains [Tough Tables (2T)](https://zenodo.org/record/4246370#.Yf5AO-pBw2w) dataset;
* `experimental_evaluation` contains scripts for obtaining an experimental evaluation on tables presented in `datasets` directory.
* `results` contains processing results of tables (*this directory is created by default*);
* `source_tables` contains examples of source tables in the CSV format for testing;
* `tabbyld2` contains software TabbyLD2 modules, including `main.py` for a console mode and `app.py` for a web mode.

## Usage

#### Console mode

In order to use the TabbyLD2 in *console mode*, you may run the following command:

```
python main.py
```

Run this script to process source tables in CSV format. Tables must be located in the `source_tables` directory.

The processing result are presented as JSON format and will be saved to the `results` directory (`json` and `provenance` subdirectories).

#### Web mode

In order to use the TabbyLD2 in *web mode*, you may run the following command:

```
python app.py
```

**NOTE:** *This mode does not work at the moment!*

## Authors

* [Nikita O. Dorodnykh](mailto:tualatin32@mail.ru)
* [Daria A. Denisova](mailto:daryalich@mail.ru)
* [Vitaliy V. Biryuckov](mailto:stukov.biryuckov2017@yandex.ru)