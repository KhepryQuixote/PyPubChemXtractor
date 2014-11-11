# -*- coding: utf-8 -*-

'''
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
'''

import codecs
import csv
import os
import re
import sys
import time

# source file full path
srcFileFullPath = "~/data/fracking/CID-Synonym-filtered_2013-07-10.txt"

# master file's full path
masFileFullPath = "~/data/fracking/CID-CASRN-SynXref-Master.txt"

# summary file's full path
sumFileFullPath = "~/data/fracking/CID-CASRN-SynXref-Summary.txt"

# synonyms file's full path
synFileFullPath = "~/data/fracking/CID-CASRN-SynXref-Synonyms.txt";

# maximum number of matches desired
# 0 = unlimited number of matches
# greater than 0 = specified number of matches allowed
maxMatches = 0

maxRows = 0

flushCount = 100000

# source file column separator
srcDelim = "\t";
srcFieldNames = ['cid','synonym']

# master file column separator
masDelim = "\t";
masFieldNames = ['cid','casrn']

# summary file column separator
sumDelim = "\t";
sumCasrnDelim = "|";
sumFieldNames = ['cid','casrns']

# synonyms file column separator
synDelim = "\t";
synFieldNames = ['cid','synonym']

# summary value separator (ALT+1 is ☺)
sumValSeparator = "|";

# Chemical Abstract Service Registry Number regular expression pattern
regExprCasRegNbr = "^[1-9][0-9]{1,6}\\-[0-9]{2}\\-[0-9]$"


# =============================================================================    
# Main routine:
# =============================================================================    
def main():
    
    global srcFileFullPath
    global masFileFullPath
    global sumFileFullPath
    global synFileFullPath
        
    bgnTime = time.time()
    
    prevCID = ""
    
    # if necessary
    if srcFileFullPath.startswith('~'):
        # expand the source file path with the user's folder
        srcFileFullPath = os.path.expanduser(srcFileFullPath)
        
    # verify that the source file exists    
    if not os.path.exists(srcFileFullPath):
        sys.stderr.write('srcFileFullPath does NOT exist: %s%s' % (srcFileFullPath, os.linesep))
        return
        
    # make sure the target folders exist
    masFileFullPath = os.path.expanduser(masFileFullPath)
    if not os.path.exists(os.path.dirname(masFileFullPath)):
        os.makedirs(os.path.dirname(masFileFullPath))
    sumFileFullPath = os.path.expanduser(sumFileFullPath)
    if not os.path.exists(os.path.dirname(sumFileFullPath)):
        os.makedirs(os.path.dirname(synFileFullPath))
    synFileFullPath = os.path.expanduser(synFileFullPath)
    if not os.path.exists(os.path.dirname(synFileFullPath)):
        os.makedirs(os.path.dirname(synFileFullPath))

    srcFile = codecs.open(srcFileFullPath, 'rb', 'cp1252')
    masFile = codecs.open(masFileFullPath, 'wb', 'cp1252')
    sumFile = codecs.open(sumFileFullPath, 'wb', 'cp1252')    
    synFile = codecs.open(synFileFullPath, 'wb', 'cp1252')
    
    srcReader = csv.DictReader(srcFile, delimiter=srcDelim, fieldnames=srcFieldNames)
    masWriter = csv.DictWriter(masFile, delimiter=masDelim, fieldnames=masFieldNames)
    sumWriter = csv.DictWriter(sumFile, delimiter=sumDelim, fieldnames=sumFieldNames)
    synWriter = csv.DictWriter(synFile, delimiter=synDelim, fieldnames=synFieldNames)
    
    masWriter.writeheader()
    sumWriter.writeheader()
    synWriter.writeheader()
    
    # compile the CASRN regex pattern
    # for later use in CASRN matching    
    pattern = re.compile(regExprCasRegNbr)   
    
    casrns = []
    synonyms = []
    
    rows = 0        
    for rowDict in srcReader:
        rows += 1
        # break on exceeding maximum rows
        if maxRows > 0 and rows > maxRows:
            break
        # if level-break on CID
        if prevCID != "" and rowDict['cid'] != prevCID:
            # if CASRNs were found
            if len(casrns) > 0:
                # output rows to appropriate files
                for casrn in casrns:
                    masWriter.writerow({'cid':prevCID, 'casrn':casrn})
                sumWriter.writerow({'cid':prevCID, 'casrns':sumCasrnDelim.join(casrns)})
                for synonym in synonyms:
                    synWriter.writerow({'cid':prevCID, 'synonym':synonym})
                del casrns[:]
            del synonyms[:]
        
        prevCID = rowDict['cid']
        synonyms.append(rowDict['synonym'])
        # if synonym matches CASRN regex pattern
        if pattern.match(rowDict['synonym']):
            # append it for later file output
            casrns.append(rowDict['synonym'])
            
        if rows % flushCount == 0:
            masFile.flush()
            sumFile.flush()
            synFile.flush()
            endTime = time.time()
            seconds = endTime - bgnTime
            if seconds > 0:
                rcdsPerSec = rows / seconds
            else:
                rcdsPerSec = 0
            print ("CID Synonym Rows: {:,} in {:,.0f} seconds @ {:,.0f} records/second".format(rows, seconds, rcdsPerSec))

    # end-of-source-file processing
    if prevCID != "":
        # if CASRNs were found
        if len(casrns) > 0:
            # output rows to appropriate files
            for casrn in casrns:
                masWriter.writerow({'cid':prevCID, 'casrn':casrn})
            sumWriter.writerow({'cid':prevCID, 'casrns':sumCasrnDelim.join(casrns)})
            for synonym in synonyms:
                synWriter.writerow({'cid':prevCID, 'synonym':synonym})
            del casrns[:]
        del synonyms[:]

    # close all files
    srcFile.close()
    masFile.close()
    sumFile.close()
    synFile.close()
    
    print ("-----------------------------------")
    endTime = time.time()
    seconds = endTime - bgnTime
    if seconds > 0:
        rcdsPerSec = rows / seconds
    else:
        rcdsPerSec = 0
    print ("CID Synonym Rows: {:,} in {:,} seconds @ {:,.0f} records/second".format(rows, seconds, rcdsPerSec))
        
    return

    
# ============================================================================
# execute the mainline processing routine
# ============================================================================

if (__name__ == "__main__"):
     retval = main()
