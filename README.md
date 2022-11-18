# German_affix_splitter
### This Python application was created as an assistant module for the OB1 reader project: https://github.com/PhPeKe/OB1_SAM. (To find out more about the OB1 reader, please read the research paper located at: https://pubmed.ncbi.nlm.nih.gov/30080066/ and explore the aforementioned github page.)

This application implements multiple methods to return German affixes along with their Zipf frequencies. For example, the suffixes **isch : 3.42** and **ischen : 2.48**. The main idea here is that attempting to extract affixes with a single stemmer (for example, Snowball stemmer: https://www.nltk.org/api/nltk.stem.snowball.html) can lead to undesired results. Hence, this application uses multiple methods of affix extraction in an attempt to cast a wide net to gather as many affixes as possible. 

Firstly, as SUBTLEX-DE is a commonly used word/frequency collection, this application will process, select correct encoding and extract the correctly spelled words from a SUBTLEX_DE.txt file without prior tinkering. So you can safely use a SUBTLEX text files, and/or any other text file with each word per line of the text file. Initially, a Snowball stemmer will stem the words and get the differences (suffixes) by comparing them with the non-stemmed words. Similarly, the words will be stemmed by Cistem stemmer (https://www.nltk.org/_modules/nltk/stem/cistem.html). 

Then, compound words will be split using the german_compound_splitter module taken from https://github.com/repodiac/german_compound_splitter (reference: german_compound_splitter, Copyright 2020 by repodiac, see https://github.com/repodiac for updates and further information) and stemmed yet again. The purpose of this splitting is to catch the connecting elements within many German compound words such as: **-ens** in **Herzensgüte**. For compound splitting, a reference text file is needed. This is provided with this repository. 

Finally, suffixes are extracted from the provided and compound split words. Their Zipf frequencies are calculated using `wordfreq` module (https://pypi.org/project/wordfreq/) and the results are saved as a text file. Results can also be pickled if `pickle_it = True` is selected. 

## Version and updates
* `version 0.1` - initial upload to github

## Future plans
* Work on prefix extraction, general improvements.

## Setup
* To be added

## Included in the repository
* `SUBTLEX_DE.txt` is included and can be used as the initail file path provided to the application. 
* `wordlist-german.txt` is zipped and provided. Taken from: https://gist.github.com/MarvinJWendt/2f4f4154b8ae218600eb091a5706b5f4. This text file is large and therfore is zipped. It is need as a reference point for the compound splitter. 

## Example
```
from German_affix_splitter import german_affix_splitter

# prodive the paths to the two text files
files = german_affix_splitter.get_file(r'.../SUBTLEX_DE.txt', '.../wordlist_german.txt')

# Run the result function to get the suffixes printed out, as text files and pickled if needed. 
suffixes = german_affix_splitter.result(files, pickle_it=True)
```

## Required Packages
* `chardet` https://pypi.org/project/chardet/
* `NLTK` https://pypi.org/project/nltk/
* `pyahocorasick` https://pypi.org/project/pyahocorasick/
* `german_compound_splitter` pip install git+https://github.com/repodiac/german_compound_splitter from https://github.com/repodiac/german_compound_splitter
* `wordfreq` https://pypi.org/project/wordfreq/

## Runtime and performance
Because of the large lists and various iteration the approximate run time is `1m20sec`. However, this is highly dependant on hardware. Thanks to `pyahocorasick` a lot of computation time is saved during the compound word splitting process (https://pypi.org/project/pyahocorasick/). 
