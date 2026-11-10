#must have a main() function
#must have 3 custom functions other than main() at the same indentation level as main()
#must have a test function in a test_project.py file

#Project Idea - Gene protein lookup CLI (command-line interface) where you type a gene name
#and it queries UniProt or NCBI API with 'requests' and returns function, length, sequence, subcellular location
#and known interactors, with an option to export a FASTA file

#this project will use the following:
    #API calls
    #sys (command line arugments)
    #loops
    #exceptions

#will use uniprot
#example uniprot URL: 'https://rest.uniprot.org/uniprotkb/search?query=gene_exact:ISG15+AND+organism_id:9606+AND+reviewed:true&format=json'



import argparse
import requests
import sys
import re

def main():
    parser = argparse.ArgumentParser(description="Gene Protein Lookup")
    parser.add_argument("gene", help="input your gene name", type=str)
    parser.add_argument("organism", help="input your organism of choice", type =str)
    args = parser.parse_args()
    organism_name = args.organism
    org_id = organism_ID(organism_name.lower())
    gene_name = organism_gene(args.gene)
    API_call(gene_name, org_id)
    #we are asking the user to input a gene name at the command line
    #we have stored the gene name in an object and the users organism of choice

    response_parse(json_outcome)

def API_call(gene_name, org_id):


    try:
        response = requests.get(f"https://rest.uniprot.org/uniprotkb/search?query=gene_exact:{gene_name}+AND+organism_id:{org_id}+AND+reviewed:true&format=json"
                                , params={"fields": "accession,protein_name,length,sequence,cc_function,go_f,cc_subcellular_location,cc_interaction"}, timeout=10.0)
        response.raise_for_status() #if the function here cant 'raise_for_status' then it will go into the except and cause an unsuccessful http status code

    except requests.ConnectionError:
        sys.exit("network  error")
    except requests.HTTPError:
        sys.exit("unsuccessful HTTP status code")
    except requests.Timeout:
        sys.exit("connetion timed out")
    except requests.exceptions.RequestException:
        sys.exit("API call error")

    try:
        json_outcome = response.json()
        json_outcome = json_outcome["results"]
        json_outcome = json_outcome[0]
    except IndexError:
        sys.exit("IndexError")

    return(json_outcome)


def response_parse(json_outcome):

    protein_interactors_final = []
    protein_subcellular_location_final = []
    protein_function_final = []

    protein_description = json_outcome["proteinDescription"]["recommendedName"]
    protein_sequence = json_outcome["sequence"]
    #now that we have the json outcome stored, we need to parse it and find the following
        #accession, protein name, length, sequence, function, subcellular location, interactors
        #need to cope with missing fields

    #now storing the parts of the Json that I am interested in as variables
    accession = json_outcome['primaryAccession']

    name = protein_description['fullName']['value']

    protein_seqeunce = protein_sequence['value']
    protein_length = f"{protein_sequence['length']} amino acids and {protein_sequence['molWeight']} Da"

    protein_function = next((c for c in json_outcome['comments']
                                if c['commentType'] == "FUNCTION"), None)

    for i in protein_function['texts']:
        protein_function_final.append(i['value'])

    protein_subcellular_location = next(c for c in json_outcome['comments']
                                if c['commentType'] == "SUBCELLULAR LOCATION")

    for i in protein_subcellular_location['subcellularLocations']:
        protein_subcellular_location_final.append(i['location']['value'])


    protein_interactors = next((c for c in json_outcome['comments']
                               if c['commentType'] == "INTERACTION"), None)

    for i in protein_interactors['interactions']:
                protein_interactors_final.append(i['interactantTwo']['geneName'])




#gene names should have a limit of 30 characters, and include numbers and hyphens in them
def organism_gene(gene_name):
    pattern = r"^[A-Za-z0-9\-]{1,30}$"
    if not re.search(pattern, gene_name):
        raise ValueError("invalid gene name")
    else:
        return gene_name


def organism_ID(organism_name):
    organism_dict = {
        "human": 9606,
        "homo sapiens": 9606,
        "mouse": 10090,
        "mus musculus": 10090,
        "rat": 10116,
        "rattus norvegicus": 10116,
        "zebrafish": 7955,
        "danio rerio": 7955,
        "fruit fly": 7227,
        "drosophila melanogaster": 7227,
        "worm": 6239,
        "caenorhabditis elegans": 6239,
        "yeast": 559292,
        "saccharomyces cerevisiae": 559292,
        "e. coli": 83333,
        "escherichia coli": 83333,
    }

    try:
        org_id = organism_dict[organism_name]
        return org_id
    except KeyError:
        sys.exit("Invalid organism name")


main()
