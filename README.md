# NCBI taxonomic classifications from NCBI accession numbers (acc2taxo)

## Description
This Python script `acc2taxo.py` retrieves NCBI taxonomic information associated with a list of accession numbers in a text file. It generates a table with the NCBI taxonomic classification of each accession number. It can also generate a file containing the NCBI taxonomy tree corresponding to the retrieved taxids.

## Usage
The script can be executed from the command line as follows:


```shell
python3 acc2taxo.py -i input_file.txt -o output_file.txt [OPTIONS]
```

The following options are available:

- `-i/--input`: the input file containing one accession number per line (required)
- `-o/--output`: the output file name (required)
- `-db/--database`: the queried NCBI database (default is "protein")
- `--sep`: the column separator for the output table (default is ",")
- `--clean`: remove empty ranks in the final table (default)
- `--no-clean`: keep all ranks in the final table (overrides `--clean`)
- `--updatetaxodb`: update the local NCBI taxonomy database. Must be set when first using the script.Takes about 50 seconds to complete 
- `-t/--tree`: (optional) the file name where to write the NCBI taxonomy tree corresponding to the list of retrieved taxids
- `--verbose`: enable verbose mode (default)
- `-v/--version`: print the version of the script

## Requirements

The script requires Python 3 and the following modules:

- `argparse`
- `requests`
- `pandas`
- `ete3`

All these modules can be easily installed with pip: 
```shell
pip install module_name
```


## Workflow

The script proceeds in two (optionnaly three) steps:

1. Get taxids from accession numbers: reads the input file, retrieves the taxid associated with each accession number from the NCBI eutils API, querying the desired database with chunks of 200 IDs. Default database is set to **protein**. For a list of databases, see https://www.ncbi.nlm.nih.gov/books/NBK25497/table/chapter2.T._entrez_unique_identifiers_ui/?report=objectonly. Note that the script automatically pauses for 0.5 seconds between each eutils API query to comply with NCBI's requirements (max 3 queries/second without a key).
2. Get infos from taxids: retrieves the lineage and names of each taxid from the NCBI taxonomy database.
3. (optional) Get the tree from the list of unique taxids retrieved in step 2.

## Example

An example file `example-acc` is provided. 
It contains 2132 *GI numbers* that can easily be retrieved in the Protein NCBI database.

Calling it as follows: 

```shell
python3 acc2taxo.py -i example-acc -o acc-results.csv -db protein -t out.tre --clean
```
Generates a table, whose first columns and rows look like: 

| acc         | taxid | name                         | rank    | superkingdom | kingdom       | phylum           | ... |
|-------------|-------|------------------------------|---------|--------------|---------------|------------------|-----|
| NP_041191.1 | 58103 | Leishmania RNA virus 1 - 1   | no rank | Viruses      | Orthornavirae | Duplornaviricota | ... |
| NP_056808.1 | 12238 | Odontoglossum ringspot virus | species | Viruses      | Orthornavirae | Kitrinoviricota  | ... |
| NP_056810.1 | 12238 | Odontoglossum ringspot virus | species | Viruses      | Orthornavirae | Kitrinoviricota  | ... |
| ...         | ...   | ...                          | ...     | ...          | ...           | ...              | ... |

- **acc** is the identifier as given in the input file
- **taxid** is the associated NCBI taxid
- **name** is the name of the taxon
- **rank** is his rank
- **superkingdom**,**kingdom**,**phylum**, **...** are the ordered ranks of the full lineage associated to each taxid, going towards the deepest observed taxid in the table. 

The function above also produces a tree in Newick format containing the taxids present in the table as well as all taxids associated to all the nodes in the taxonomic tree. 


## Planned Improvements
The following improvements are planned for future releases:

- [ ] Automatic choice of the eutils NCBI database
- [ ] Automatic detection of the need for a taxonomy database update
- [ ] Smarter query frequency (i.e., pause time, etc.)
- [ ] Possibility to provide an NCBI API key to make 10 queries per second instead of 3 (max) without a key
- [ ] Parallelization to speed up execution (related to point 4)
- [ ] Options for tree format output
- [ ] Function Documentation


## Dependencies Documentation
The script uses the following external resources:

NCBI eutils API (https://www.ncbi.nlm.nih.gov/books/NBK25500/)
NCBI taxonomy database (https://www.ncbi.nlm.nih.gov/taxonomy)
Taxallnomy website (http://bioinfo.icb.ufmg.br/taxallnomy/) - to get the ordered list of ranks used in the output table.

___

This script was written by DM de Vienne in March 2023. 

If you see a bug, please correct it yourself, :wink: 
