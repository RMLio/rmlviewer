# RMLViewer

RMLViewer is a proof-of-concept implementation for [RML Logical Views](https://github.com/kg-construct/rml-lv).
For more information we refer to our [paper](https://biblio.ugent.be/publication/01J1YD9J9RBMKM1YC7VSSPASHM).

## Prerequisites

The code is written and tested using Python 3.12.3.
To install the needed libraries, run below command.

```bash
pip install -r requirements.txt
```

## Use

The script takes as input an RML mapping (conform with https://kg-construct.github.io/rml-resources/portal/) and returns an equivalent normalized mapping without logical views
(named `mapping_without_views.ttl`).  
The normalizations steps are described [here](#normalization).  
All logical views are converted to logical sources with JSON files as source.  
These JSON files are the materialization of the original logical views.  
The new mapping file together with the original input data and the newly generated JSON files can be processed by any RML mapping engine that supports JSON source data.  

The following source path semantics are implemented: when `rml:root` is set to `rml:MappingDirectory`, relative `rml:path` values are resolved against the mapping file directory; when `rml:root` is omitted, relative paths are resolved against the current working directory.

Compared to the initial `RML-view-to-CSV` version (till v1.2.0), the legacy options `--optimize` and `--no_ref_object_map` are currently not supported in `RMLViewer`.

```text
usage: rmlviewer.py [-h] [--version] [--mapping MAPPING] [--output_dir OUTPUT_DIR]

Copyright by (c) Els de Vleeschauwer (2024), available under the MIT license
options:
  -h, --help                show this help message and exit
  --version                 show program's version number and exit
  --mapping MAPPING         The mapping file that needs to be converted.
  --output_dir OUTPUT_DIR   Directory to which the output is saved, default is "./"
```

## Implemented features

- Flattening of nested data structures
- Handling of mixed data formats
- Extended joining of data sources  
- Field indexes
- Templates and constants in Expression Fields
- Natural datatype mapping (for datatypes supported by JSON)

## Supported data formats

- CSV
- JSON (standard JSONPath references, plus several [extensions](https://github.com/h2non/jsonpath-ng/#extensions))
- XML

## Examples

Examples of mapping rules that can be handled with this implementation, can be found in the test cases and use cases.

- [Test cases](./test_cases)
- [Use cases](./use_cases)

## COVERAGE of RML-LV TEST CASES

| Test Case ID      | Covered? |
|-------------------|----------|
| ./RMLLVTC0000a/ | True |
| ./RMLLVTC0000b/ | True |
| ./RMLLVTC0000c/ | True |
| ./RMLLVTC0001a/ | True |
| ./RMLLVTC0001b/ | True |
| ./RMLLVTC0001c/ | True |
| ./RMLLVTC0001d/ | True |
| ./RMLLVTC0002a/ | True |
| ./RMLLVTC0002b/ | True |
| ./RMLLVTC0002c/ | True |
| ./RMLLVTC0003a/ | True |
| ./RMLLVTC0003b/ | True |
| ./RMLLVTC0003c/ | True |
| ./RMLLVTC0004a/ | True |
| ./RMLLVTC0004b/ | True |
| ./RMLLVTC0004c/ | True |
| ./RMLLVTC0004d/ | True |
| ./RMLLVTC0005a/ | True |
| ./RMLLVTC0005b/ | True |
| ./RMLLVTC0005c/ | True |
| ./RMLLVTC0006a/ | True |
| ./RMLLVTC0006b/ | True |
| ./RMLLVTC0006c/ | True |
| ./RMLLVTC0006d/ | True |
| ./RMLLVTC0006e/ | True |
| ./RMLLVTC0006f/ | True |
| ./RMLLVTC0007a/ | True |
| ./RMLLVTC0007b/ | True |
| ./RMLLVTC0007c/ | True |
| ./RMLLVTC0008a/ | True |
| ./RMLLVTC0008b/ | True |
| ./RMLLVTC0008c/ | True |
| ./RMLLVTC0008d/ | True |
| ./RMLLVTC0009a/ | True |
| ./RMLLVTC0009b/ | True |
| ./RMLLVTC0009c/ | True |
| ./RMLLVTC0010a/ | True |
| ./RMLLVTC0010b/ | True |
| ./RMLLVTC0010c/ | True |
| ./RMLLVTC0010d/ | True |
| ./RMLLVTC0010e/ | True |

## Normalization

The resulting mapping file is normalized.

#### Properties Normalized

| Shorthand | Expanded Form | Transformation |
|-----------|---------------|-----------------|
| `rml:subject` | `rml:subjectMap` | Creates blank node with `rml:constant` |
| `rml:class` | `rml:predicateObjectMap` | Creates nested structure with rdf:type |
| `rml:predicate` | `rml:predicateMap` | Creates blank node with `rml:constant` |
| `rml:object` | `rml:objectMap` | Creates blank node with `rml:constant` |
| `rml:child` | `rml:childMap` | Creates blank node with `rml:reference` |
| `rml:parent` | `rml:parentMap` | Creates blank node with `rml:reference` |
| `rml:datatype` | `rml:datatypeMap` | Creates blank node, sets termType=Literal |
| `rml:language` | `rml:languageMap` | Creates blank node, sets termType=Literal |

#### Type Declarations Added

- `rml:TriplesMap` - for triple map subjects
- `rml:SubjectMap` - for subject maps
- `rml:PredicateObjectMap` - for predicate-object maps
- `rml:PredicateMap` - for predicate maps
- `rml:ObjectMap` - for object maps
- `rml:RefObjectMap` - for referencing object maps
- `rml:TermMap` - for term maps
- `rml:GraphMap` - for graph maps
