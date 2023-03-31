#!/usr/bin/env python3
# DM de Vienne - March 2023

# TODO: 
# 1. choix automatique de la base de données?
# 2. détection automatique de la nécessité ou pas d'une mise à jour de la base de taxonomie
# 3. Etre plus intélligent sur la fréquence des requêtes (ici une pause d'une demi seconde entre chaque)
# 4. ajouter la possibilité de donner une clé NCBI API et pouvoir ainsi 
#    faire 10 requêtes par seconde au lieu de 3 (max) sans la clef
# 5. ajouter du parallelisme pour accélerer (en lien avec point 4.)


from ete3 import NCBITaxa,Tree
import argparse
import requests
import pandas as pd
import time
import sys


parser = argparse.ArgumentParser(description='Reads a file with accession numbers in rows and returns a table with NCBI taxid information for each.')
parser.add_argument('-i', '--input', type=str, required=True,
                    help='A file with one accession number per line')
parser.add_argument('-o', '--output', type=str, required=False,
                    help='The output file name')
parser.add_argument('-db', '--database', type=str, default="protein",
                    help='The queried NCBI database. Default to \'protein\' (protein database)')
parser.add_argument('--sep', type=str, default=",",
                    help='Column separator for the output table. Default to \',\'')
parser.add_argument('--clean', action='store_true', default=True, help='Should empty rank columns be removed. Default to True')
parser.add_argument('--updatetaxodb', action='store_true', default=False, help='Should the local NCBI taxonomy database be updated first. Default to False because may take some time (minute). Automatically set to True if no database is found locally (first time using this code for example).')
parser.add_argument('--verbose', action='store_true', default=True, help='Verbose mode (True/False). Default to True.')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')

args = parser.parse_args()
VERB = args.verbose

###############################################
## STEP 1: GET TAXIDS FROM ACCESSION NUMBERS ##
###############################################


# Function that iteratively takes a collection of chunk_size ids and returns acc and taxid
def gettaxidsfromids(ids, chunk_size,db): 
	if VERB : print("Querying " + args.database, "database", end="")
	RES = []
	for i in range(0, len(ids), chunk_size):
		if VERB : print('.', end="", flush=True)
		idssmall = ids[i:i+chunk_size]
		idsok = ','.join(idssmall)
		url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db='+db+'&id='+idsok+'&retmode=json&retmax=1000'
		resp = requests.get(url=url)
		data = resp.json()
		for uid in data['result']['uids']:
			acc = data['result'][uid]['accessionversion']
			tid = data['result'][uid]['taxid']
			RES.append([acc,tid])
		time.sleep(0.5)
	if VERB : print(' done')
	return(RES)

# Open input file and get all ids
with open(args.input, 'r') as f:
    ids = [line.strip() for line in f]

# Get Taxid for each id.
allpairs = gettaxidsfromids(ids, 200, args.database)
if VERB: print("  -> " + str(len(allpairs)) + " accession numbers were successfully retrieved ("+str(round(len(allpairs)/len(ids)*100))+"%)")

###############################################
## STEP 2: GET INFOS FROM TAXIDS 			 ##
###############################################
ncbi = NCBITaxa()

if args.updatetaxodb:
	ncbi.update_taxonomy_database() #if needed, to upload the taxonomy

if VERB: print("Getting ranks from taxids...", end="")

#get the orderd list of ranks from Taxallnomy website (http://bioinfo.icb.ufmg.br/taxallnomy/)
OrderdAllRanks = ["superkingdom","kingdom","subkingdom","superphylum","phylum","subphylum","infraphylum","superclass","class","subclass","infraclass","cohort","subcohort","superorder","order","suborder","infraorder","parvorder","superfamily","family","subfamily","tribe","subtribe","genus","subgenus","section","subsection","series","subseries","species_group","species_subgroup","species","forma_specialis","subspecies","varietas","subvariety","forma","serogroup","serotype","strain","isolate"]

ALLDICT = []
for k in allpairs:
	taxid=k[1]
	lineage = ncbi.get_lineage(taxid)
	lineage.reverse()
	names = ncbi.get_taxid_translator(lineage)
	ranks = ncbi.get_rank(lineage)
	name = names[taxid]
	rank = ranks[taxid]
	rankdict={"acc" : k[0], "taxid" : taxid, "name": name, "rank" : rank}
	for l in lineage:
		if ranks[l]!='no rank':
			rankdict.update({ranks[l] : names[l]})
	ALLDICT.append(rankdict)
if VERB: print("done")

###############################################
## STEP 3: FORMAT AND WRITE OUTPUT 			 ##
###############################################
df = pd.DataFrame(ALLDICT, columns=["acc","taxid","name","rank"]+OrderdAllRanks)

#cleaning
if args.clean: 
	if VERB: print("Removing empty rank columns...", end="")
	df = df.dropna(axis=1, how='all')
	if VERB: print("done")

def WriteFinalTab(dataframe, outfilename):
	if (outfilename==None):
		if VERB: print("Writing to standard output...", end="")
		df.to_csv(sys.stdout, index=False)
	else:
		if VERB: print("Writing to file " + outfilename + "...", end="")
		df.to_csv(args.output, index=False)
	if VERB: print("done")

#writing
WriteFinalTab(df, args.output)

if VERB: print("END")

