# Test Cases

This directory contains test cases for RMLViewer.

## How to Run Tests

### Prerequisites

1. **Python Virtual Environment**

```bash
source ../venv/bin/activate
```

1. **MappingWeaver JAR**

The test script requires `mappingweaver.jar`.
You need to build it manually:

- Clone the MappingWeaver repository: https://github.com/RMLio/MappingWeaver-java
- Follow the build instructions in the repository's README
- Copy the generated JAR file to this directory

Optionally, any other RMLEngine compatible with RML-Core can be used, but this requires a small adaptation of the script.

### Running Tests

**To run all tests:**

```bash
./tests.sh
```

For each folder in this dir, the script will:

1. Run the view-to-csv conversion on each test case
2. Execute the mappingweaver to generate output triples
3. Compare the generated output with the expected output when `output.nq` is present
4. For test cases without `output.nq`, mark the test as `TRUE` when MappingWeaver produces no `output_test.nq` content, otherwise `FALSE`
5. Report results in `result.md`

## Test Case Structure

Each test case directory contains:

- **mapping.ttl** - The RML mapping with `rml:LogicalView` constructs
- **Input data** - JSON or CSV files referenced in the mapping
- **output.nq** - Expected RDF output in N-Quads format, when the test case is expected to produce output
- **README.md** - Description of the test case (when available)

The conversion process:

1. Normalizes the RML mapping to expanded form
2. Materializes logical views as JSON files (view0.json, view1.json, etc.)
3. Generates `mapping_without_views.ttl` - the converted mapping
4. The mapper uses this mapping and the materialized views to generate RDF triples

## Generated Files

After running the conversion, you'll see:

- `view*.json` - Materialized view data
- `mapping_without_views.ttl` - Converted RML mapping without views
- `output_test.nq` - Generated output (for comparison)
- `result.md` - Test results summary

## Cleanup

To remove generated test files (but keep outputs for comparison):

```bash
rm view* mapping_without_views.ttl output_test.nq
```
