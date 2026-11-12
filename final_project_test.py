from final_project import organism_gene, response_parse, sixty_char_check
import pytest


FAKE_ENTRY = {
    "primaryAccession": "P00001",
    "proteinDescription": {
        "recommendedName": {"fullName": {"value": "Test protein"}}
    },
    "sequence": {"value": "MKTAYIAKQR", "length": 10, "molWeight": 1234},
    "comments": [
        {"commentType": "FUNCTION", "texts": [{"value": "Does something useful."}]},
        {"commentType": "SUBCELLULAR LOCATION",
         "subcellularLocations": [
             {"location": {"value": "Cytoplasm"}},
             {"location": {"value": "Nucleus"}},
         ]},
        {"commentType": "INTERACTION",
         "interactions": [
             {"interactantTwo": {"geneName": "GENE1"}},
             {"interactantTwo": {}},
         ]},
    ],
}


def test_organism_gene():
    gene = "ISG15"
    wrong_gene_name = "IS?G15"
    assert organism_gene(gene) == "ISG15"

    with pytest.raises(ValueError):
        organism_gene(wrong_gene_name)

def test_response_parse():
    z = response_parse(FAKE_ENTRY)
    assert z == {
    "accession": "P00001",
    "name": "Test protein",
    "protein sequence": "MKTAYIAKQR",
    "protein length": 10,
    "protein weight": 1234,
    "protein function": ["Does something useful."],
    "protein subcellular location": ["Cytoplasm", "Nucleus"],
    "protein_interactors": ["GENE1"],
}


def test_sixty_char_check():
    y = 'MKTAYIAKQR'
    assert sixty_char_check(y)  == "MKTAYIAKQR"
    assert "\n" not in sixty_char_check(y)

    assert sixty_char_check(y * 7) == "MKTAYIAKQRMKTAYIAKQRMKTAYIAKQRMKTAYIAKQRMKTAYIAKQRMKTAYIAKQR\nMKTAYIAKQR"
