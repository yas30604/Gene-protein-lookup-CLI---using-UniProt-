#Project Idea - Gene protein lookup CLI (command-line interface) where you type a gene name
#and it queries UniProt or NCBI API with 'requests' and returns function, length, sequence, subcellular location
#and known interactors, with an option to export a FASTA file


import argparse
import requests
import sys
import re

def main():
    nl = '\n'
    parser = argparse.ArgumentParser(description="Gene Protein Lookup")
    parser.add_argument("gene", help="input your gene name", type=str)
    parser.add_argument("organism", help="input your organism of choice", type =str)
    parser.add_argument('-F', '--fasta', action='store_true') #allow the user to choose if they want a fasta file export
    args = parser.parse_args()
    organism_name = args.organism
    org_id = organism_ID(organism_name.lower())
    try:
        gene_name = organism_gene(args.gene)
    except ValueError:
        sys.exit("invalid gene name")
    json_outcome = API_call(gene_name, org_id)
    #we are asking the user to input a gene name at the command line
    #we have stored the gene name in an object and the users organism of choice

    user_dictionary = response_parse(json_outcome)
    sixty_character_check = user_dictionary['protein sequence']
    sequence_str = sixty_char_check(sixty_character_check)

    final = (
        f"Protein: {user_dictionary['name'] or 'NA'}{nl}"
        f"Accession: {user_dictionary['accession'] or 'NA'}{nl}"
        f"Sequence length: {user_dictionary['protein length'] or 'NA'} amino acids{nl}"
        f"Weight: {user_dictionary['protein weight'] or 'NA'} Da{nl}"
        f"Function: {', '.join(user_dictionary['protein function']) or 'NA'}{nl}"
        f"Location: {', '.join(user_dictionary['protein subcellular location']) or 'NA'}{nl}"
        f"Interactors: {', '.join(user_dictionary['protein_interactors']) or 'NA'}"
    )

    print(final)
    #this counts 60 characters in a string from the protein sequence then introduces line break at the 60th character



    if args.fasta: #this is the same as saying if args.fasta == True:
        with open(f"{gene_name or 'PROTEIN'}.FASTA", "w") as file:
                file.write(f">{user_dictionary.get('accession') or 'NA'} {user_dictionary.get('name') or 'NA'}{nl}"
                        f"{sequence_str}")
        print("successfully exported FASTA file to python directory")


def API_call(gene_name, org_id):


    try:
        response = requests.get(f"https://rest.uniprot.org/uniprotkb/search?query=gene_exact:{gene_name}+AND+organism_id:{org_id}+AND+reviewed:true&format=json"
                                , params={"fields": "accession,protein_name,length,sequence,cc_function,go_f,cc_subcellular_location,cc_interaction"}, timeout=10.0)
        response.raise_for_status() #if the function here cant 'raise_for_status' then it will go into the except and cause an unsuccessful http status code

    except requests.Timeout:
        sys.exit("connetion timed out")
    except requests.ConnectionError:
        sys.exit("network  error")
    except requests.HTTPError:
        sys.exit("unsuccessful HTTP status code")

    except requests.exceptions.RequestException:
        sys.exit("API call error")

    try:
        json_outcome = response.json()
        json_outcome = json_outcome["results"]
        json_outcome = json_outcome[0]
    except IndexError:
        sys.exit("IndexError")

    return json_outcome


def response_parse(json_outcome):

    protein_interactors_final = []
    protein_subcellular_location_final = []
    protein_function_final = []
    user_FASTA = {}

    protein_description_1 = json_outcome.get('proteinDescription', {})
    protein_description = protein_description_1.get('recommendedName', {})
    protein_sequence = json_outcome.get('sequence', {})
    #now that we have the json outcome stored, we need to parse it and find the following
        #accession, protein name, length, sequence, function, subcellular location, interactors
        #need to cope with missing fieldspython final_project.py HLA-A human

    #now storing the parts of the Json that I am interested in as variables
    accession = json_outcome.get('primaryAccession', "")

    name = protein_description.get('fullName', {})
    name = name.get('value', "")

    protein_sequence_1 = protein_sequence.get('value', "")
    protein_length = protein_sequence.get('length', "")
    protein_weight = protein_sequence.get('molWeight', "")

    try:
        protein_function = next((c for c in json_outcome.get('comments', [])
                                    if c['commentType'] == "FUNCTION"))
        for i in protein_function['texts']:
            try:
                protein_function_final.append(i['value'])
            except KeyError:
                pass

    except StopIteration:
        pass


    try: #this allows us to pas on missing values / cases, important as some genes wont have all their cases
        protein_subcellular_location = next(c for c in json_outcome.get('comments', [])
                                    if c['commentType'] == "SUBCELLULAR LOCATION")
        for i in protein_subcellular_location['subcellularLocations']:
            try:
                protein_subcellular_location_final.append(i['location']['value'])
            except KeyError:
                pass

    except StopIteration:
        pass


    try:
        protein_interactors = next((c for c in json_outcome.get('comments', [])
                                if c['commentType'] == "INTERACTION"))
        for i in protein_interactors['interactions']:
                    try:
                        protein_interactors_final.append(i['interactantTwo']['geneName'])
                    except KeyError:
                        pass


    except StopIteration:
        pass

    user_dictionary = {"accession": accession,
                  "name": name,
                  "protein sequence": protein_sequence_1,
                  "protein length": protein_length,
                  "protein weight": protein_weight,
                  "protein function": protein_function_final,
                  "protein subcellular location": protein_subcellular_location_final,
                  "protein_interactors": protein_interactors_final
                  }

    return user_dictionary


def sixty_char_check(sixty_character_check):

    sequence_str = ""
    nl = '\n'
    counter = 0
    for i in sixty_character_check:
        sequence_str += i
        counter = counter + 1
        if counter == 60:
            sequence_str += nl
            counter = 0

    return sequence_str


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


if __name__ == "__main__":
    main()
