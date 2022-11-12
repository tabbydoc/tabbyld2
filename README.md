# TabbyLD2

A web-based application to annotate relational tables and generate knowledge graphs.

## Version

0.4

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

*We recommend you to use Python 3.7 or more.*

#### Additional software

1. In addition to [SPARQL](https://www.w3.org/TR/rdf-sparql-query/) queries, we use [DBpedia Lookup](https://github.com/dbpedia/dbpedia-lookup) to find candidate entities from DBpedia. This service requires a separate installation.

2. **TabbyLD2** uses [ColNet](https://arxiv.org/abs/1811.01304) for CTA task. ColNet is a framework based on Convolutional Neural Networks (CNNs) to predict the most suitable (relevant) class from a set of candidates for each named entity column. The ColNet framework uses *Tensorflow* as a machine learning platform.

**ColNet** requirements:

* Wikipedia corpus (e.g., https://github.com/attardi/wikiextractor)
* Pre-train word2vec (e.g., https://radimrehurek.com/gensim/models/word2vec.html)
* Pre-trained word2vec model by Wikipedia Dump: https://drive.google.com/open?id=1d_xrUPRLQjpcZrlm_cpKJO3jWBFKYhcl

**NOTE 1:** to use `sparql.query` in Python 3.7 and more, go to sparql library, find the IRI class and change return of the `__str__()` function.

From:
```
def __str__(self):
    return self.value.encode("unicode-escape")
```
to:
```to:
def __str__(self):
    return self.value
```

**NOTE 2:** The version of *Tensorflow* and *Keras* libraries must match.

## Directory Structure

* `datasets` contains datasets of source tables for experimental evaluation:
    * `T2Dv2` contains [T2Dv2 Gold Standard](http://webdatacommons.org/webtables/goldstandardV2.html) dataset, where `col_class_checked_fg.csv` was formed by [SemAIDA](https://github.com/alan-turing-institute/SemAIDA/tree/master/AAAI19/T2Dv2) and is fine-grained ground truth class for all columns;
    * `Tough_Tables` contains [Tough Tables (2T)](https://zenodo.org/record/4246370#.Yf5AO-pBw2w) dataset. **NOTE:** `CEA_2T_gt.zip` must be unzipped before receiving an experimental evaluation;
    * `GitTables_SemTab_2022` contains [GitTables](https://gittables.github.io/) dataset that was applied in the [SemTab-2022](https://sem-tab-challenge.github.io/2022/) competition for Column Type Annotation by DBpedia (GT-CTA-DBP).
* `examples` contains table examples in the CSV format for testing;
* `experimental_evaluation` contains scripts for obtaining an experimental evaluation on tables presented in `datasets` directory;
* `results` contains processing results of tables (*this directory is created by default*);
* `source_tables` is the folder in which you need to place CSV files of source tables for processing (*contains two table files for testing by default*);
* `tabbyld2` contains TabbyLD2 modules, including `main.py` for a console mode and `app.py` for a web mode, and also:
    * `datamodel` contains description of tabular data and knowledge graph models;
    * `helpers` contains various useful functions for working with files, data, etc.;
    * `preprocessing` contains table preprocessing module, which includes data cleaning, atomic column classification, subject column identification;
    * `table_annotation` contains semantic table annotator for CEA and CTA tasks. This module also contains:
        * `colnet` contains ColNet framework for annotating categorical columns (NE-columns);
        * `w2v_model` contains pre-train word2vec model. **NOTE:** this model is installed and placed independently.

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