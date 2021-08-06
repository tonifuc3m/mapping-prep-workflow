# mapping-prep-workflow
Script to prepare files for normalization annotators.
Adds suggestions from 3 datasets (BARR, NER, PharmaCoNER) and from Snomed mapping thanks to TEMUNormalizer.

### Requirements
See TEMUNormalizer requirements. Add pandas and numpy
Needs a data/ folder with 4 TSVs:./data/BARR.tsv, ./data/NER.tsv, ./pharmaconer.tsv and ./data/SpanishSnomed_tmp.tsv
Python3

### Usage usage
```
$ python main.py -d ~/brat_path -a ~/tsv_with_already_normalized_entities.tsv -l labels to ignore -o ~/outpath
```

### Arguments
+ ```-d```: path to folder with Brat files we use as INPUT
+ ```-a```: path to TSV with already normalized entities. Example: 
```
_id_	label	span_norm	code
#ID0	ENFERMEDAD	síndrome de löfgren	238676008
#ID1	ENFERMEDAD	linfoadenopatía mediastínica	52324001
```
+ ```-l```: Brat labels to ignore separated by whitespaces. Example: ```_SUG_ENFERMEDAD ENFERMEDAD SPECIES _SUG_CHEMICAL```
+ ```-o```: Path to output directory where final TSV files will be created


### Output
+ ```all_before_mapping.tsv```: all entities from Brat. Do not give this to annotators.
+ ```this_bunch_already_mapped.tsv```: deduplicated entities from Brat that we had already normalized in this project.
+ ```this_bunch_no_mapping.tsv```: deduplicated entities from Brat that we had NOT normalized in this project.

##### TODO
+ Concat this_bunch_already_mapped.tsv and this_bunch_no_mapping.tsv
+ Upload them to Google Spreadsheet.
