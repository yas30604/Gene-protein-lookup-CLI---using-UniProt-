This is a command line tool used to look up gene in UniProt and gives you back a summary of its protein information as well as an option to export a FASTA 

List of information provided by the summary; 'Protein' (name), 'Accession', 'Sequence length' (in amino acids), 'Weight'  (in Da), 'Function', 'Location' (subcellular location), 'Interactors' (gene interactors)

To use yourself, at the command line type 'python final_project.py GENE_NAME ORGANISM_NAME --fasta(optional)' for example 'python final_project.py ISG15 human --fasta' (based on my MRes project at UCL)

Essentially the script takes the gene and organism input ensuring that the input is valid in structure so that errors are not raised based on poor input, then the organism is matched to a dictionary of organism IDs so that we can give UniProt the correct API call and receive a Json of relevant information. 
Finally the script parses that Json and gives back a summary to the user of information that they might find useful

Using argparse is useful as nothing needs to be typed interactively and typically bioinformatic programs take their inputs as arguments. Also it allows using optional flags like '--fasta' easier and can generate help messages to guide the user

Giving the user more options to choose what data they would and would not want, is probably a better outcome for this project, as well as giving them the opportunity to loop over and get multiple protein lookups for their FASTA export

The purpose of this project as a final project for CS50p (thus the name of the file), and also as an opportunity to get better at implementing what I have learned towards a tool I would find fun.
