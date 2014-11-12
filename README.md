PyPubChemXtractor
=================

Python 3.4 script to extract Chemical Abstract Society Registry Numbers (CASRNs) from PubChem's CID Synonym file.

Name: PyPubChemXtractor.py
Author: Khepry Quixote
Date: 11 Nov 2014
Language: Python 3.4
Narrative:

This Python 3.4 program will extract CASRN values from PubChem's
CID Synonym file, which can be found at the following address:

    ftp://ftp.ncbi.nlm.nih.gov/pubchem/Compound/Extras/CID-Synonym-filtered.gz
    
As of 11 Nov 2014, this file is approximately 1.2 GB in size.

Lists of Chemical Abstract Society (CAS) Registration Numbers (CASRNs) are hard to find,
and this list is no exception.  Within this list, the CASRNs are NOT explicitly identified as such,
possibly because CAS would rather have you go through them for access to the numbers in question.

However, CASRNs do seem to follow a particular pattern and as such can be extracted via
a regular expression pattern: "^[1-9][0-9]{1,6}\\-[0-9]{2}\\-[0-9]$".  This is what this
program does, extracting CASRNs from the synonym list via regular expression pattern recognition.

The "master" output file contains a row for each CID, CASRN combination.

The "summary" output file contains a row for each CID, with all of the CASRNs for that CID number.

The "synonym" output file contains a row for each CID and synonym combination.

TODO: output these files as tables within one SQLite database file.
