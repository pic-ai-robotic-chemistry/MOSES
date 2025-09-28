from typing import TypedDict, List, Annotated, Tuple, Dict, Union
from operator import add

from owlready2 import *

from config import settings
from concept_extractor import IndividualMetaData, ClassMetaData, DataPropertyMetaData, parse_llm_output, llm
from src.ontology.preprocess import create_metadata_properties
from src.agents.builder_team.individual_classifier import generate_relationship_prompt, generate_relationship_prompt_all

class BuilderTeamState(TypedDict):
    ontology: Annotated[owlready2.namespace.Ontology, settings.ONTOLOGY_CONFIG["ontology"]]
    classes: Annotated[List[ClassMetaData], add]
    individuals: Annotated[List[IndividualMetaData], add]
    individual_classifications: Annotated[
        List[Dict[
            str,
            Union[IndividualMetaData, ClassMetaData]
        ]],
        add
    ]
    data_properties: Annotated[
        List[
            Tuple[
                DataPropertyMetaData,
                Dict[str, str]
            ]
        ],
        add
    ]
    object_properties: Annotated[
        List[
            Tuple[
                Union[IndividualMetaData, ClassMetaData],
                str,
                Union[IndividualMetaData, ClassMetaData]
            ]
        ],
        add
    ]


output = """
Name: Electron donation
Is data property: False
Information: Electron donation affects chemical shifts by influencing electron distribution in benzene rings.

Name: Electron withdrawal
Is data property: False
Information: Electron withdrawal affects chemical shifts through inductive effects and conjugation.

Name: Chemical shift
Is data property: True
Information: Chemical shift is influenced by electron donation and withdrawal in benzene rings.

Name: Benzene ring
Is data property: False
Information: Benzene rings with substituents in the 1 and 4 positions have identical hydrogens affecting chemical shifts.

Name: Conjugation
Is data property: False
Information: Conjugation affects chemical shifts through π bonds and is discussed in Chapter 7.

Name: Inductive effect
Is data property: False
Information: Inductive effects result from electron withdrawal or donation through polarization of σ bonds.

Name: Nitro group
Is data property: False
Information: The nitro group is the most powerful electron-withdrawing group by conjugation.

Name: Carbonyl group
Is data property: False
Information: The carbonyl group follows the nitro group in electron-withdrawing power by conjugation.

Name: Nitrile group
Is data property: False
Information: The nitrile group is a strong electron-withdrawing group by conjugation.

Name: CF3 group
Is data property: False
Information: The CF3 group is an important example of a group showing simple inductive withdrawal.

Name: Halogens
Is data property: False
Information: Halogens show a balance between inductive electron withdrawal and lone pair donation.

Name: Alkyl group
Is data property: False
Information: Alkyl groups are weak inductive electron donors.

Name: Amino group
Is data property: False
Information: Amino groups are the best electron donors by conjugation of lone pairs.

Name: NO2 group
Is data property: False
Information: The NO2 group is the best electron withdrawer among nitrogen-based functional groups.

Name: NH2 group
Is data property: False
Information: The NH2 group is the best electron donor among nitrogen-based functional groups.

Name: Lone pair
Is data property: False
Information: Lone pairs on halogens, O, and N affect electron donation and chemical shifts.

Name: Electronegativity
Is data property: True
Information: Electronegativity influences the electron donation ability of elements with lone pairs.

Name: Fluorine (F)
Is data property: False
Information: Fluorine is the most electronegative element and the weakest donor among first-row p block elements.

Name: Oxygen (O)
Is data property: False
Information: Oxygen is an electronegative element with lone pairs affecting electron donation.

Name: Nitrogen (N)
Is data property: False
Information: Nitrogen is an electronegative element with lone pairs affecting electron donation.

Name: Chlorine (Cl)
Is data property: False
Information: Chlorine is a halogen with lone pairs in 3p orbitals affecting electron donation.

Name: Bromine (Br)
Is data property: False
Information: Bromine is a halogen with lone pairs in 4p orbitals affecting electron donation.

Name: Iodine (I)
Is data property: False
Information: Iodine is a halogen with lone pairs in 5p orbitals affecting electron donation.
"""

context = """
###### How electron donation and withdrawal change chemical shifts  \nWe can get an idea of the effect of electron distribution by looking at a series of benzene rings\nwith the same substituent in the 1 and 4 positions. This pattern makes all four hydrogens on\nthe ring identical. Here are a few compounds listed in order of chemical shift: largest shift\n(lowest fi eld; most deshielded) fi rst. Conjugation is shown by the usual curly arrows, and\ninductive effects by a straight arrow by the side of the group. Only one hydrogen atom and\none set of arrows are shown.  \nConjugation, as discussed in\nChapter 7, is felt through π bonds,\nwhile inductive effects are the\nresult of electron withdrawal or\ndonation felt simply by polarization\nof the σ bonds of the molecule.\nSee p. 135.  \nthe effect of electron-withdrawing groups\nby conjugation  \nby inductive effects  \n**H**  \n**O**  \n**O**  \n**HO**  \n**N**  \nδH 8.48 δH 8.10 **C** δH 8.10 δH 8.07 δH 7.78  \n**N**  \n**O**  \n**O**  \n**OH**  \n**C**  \n**N**  \n**O**  \n**H**  \n**F** **F**  \n**F**  \nThe largest shifts come from groups that withdraw electrons by conjugation. Nitro is the\nmost powerful—this should not surprise you as we saw the same in non-aromatic compounds\nin both [13]C and [1]H NMR spectra. Then come the carbonyl and nitrile group followed by groups\nshowing simple inductive withdrawal. CF3 is an important example of this kind of group—\nthree fl uorine atoms combine to exert a powerful effect.  \n-----  \nIn the middle of our sequence, around the position of benzene itself at 7.27 ppm, come\nthe halogens, whose inductive electron withdrawal and lone pair donation are nearly\nbalanced.  \nbalance between withdrawal by inductive effect and donation of lone pairs by conjugation  \n**I** δH 7.40 **Br** δH 7.32 δH 7.27 **Cl** δH 7.24 **F** δH 7.00  \n**I**  \n**Br**  \n**Cl**  \n**F**  \nAlkyl groups are weak inductive donators, but the groups which give the most shielding—\nperhaps surprisingly—are those containing the electronegative atoms O and N. Despite being\ninductively electron withdrawing (the C–O and C–N σ bonds are polarized with δ + C), on\nbalance conjugation of their lone pairs with the ring (as you saw on p. 278) makes them net\nelectron donors. They increase the shielding at the ring hydrogens. Amino groups are the best.\nNote that one nitrogen-based functional group (NO2) is the best electron withdrawer while\nanother (NH2) is the best electron donor.  \nthe effect of electron-donating groups  \nby inductive effect  \nbalance between withdrawal by inductive effect and donation\nof lone pairs by conjugation—electron donation wins  \n**H**  \nδH 7.03  \n**H**  \n**H**  \n**CH3**  \nδH 6.80 **O**  \n**H** **H**  \nδH 6.59 **N**  \n**H**  \nδH 6.35  \n**H**  \n**H**  \n**CH3**  \n**O**  \n**CH3**  \n**H**  \n**H**  \n**N**  \n**O**  \nδH 7.27  \n**H**  \n**H**  \nδH 7.27  \nδH 5.68  \n**H**  \n**H**  \nδH 5.68  \n**O**  \nδH 6.0  \n**H**  \n**H**  \nδH 7.0  \nδH 4.65  \n**H**  \n**H**  \nδH 6.35  \nAs far as the donors with lone pairs are concerned (the halogens plus O and N), two factors\nare important—the size of the lone pairs and the electronegativity of the element. If we look\nat the four halides at the top of this page the lone pairs are in 2p (F), 3p (Cl), 4p (Br), and 5p (I)\norbitals. In all cases the orbitals on the benzene ring are 2p so the fl uorine orbital is of the\nright size to interact well and the others too large. Even though fl uorine is the most electronegative, it is still the best donor. The others don’t pull so much electron density away, but\nthey can’t give so much back either.\nIf we compare the fi rst row of the p block elements—F, OH, and NH2—all have lone pairs\nin 2p orbitals so now electronegativity is the only variable. As you would expect, the most\nelectronegative element, F, is now the weakest donor.
"""

# ontology = settings.ONTOLOGY_CONFIG["ontology"]

# create_metadata_properties(ontology)

class_concepts, data_properties = parse_llm_output(output)

# test_state = BuilderTeamState(ontology=ontology, classes=class_concepts, individuals=individual_concepts, individual_classifications=[], data_properties=[], object_properties=[])

# prompt = generate_prompt(individual_concepts, class_concepts, context)

# print(prompt)

# for object in class_concepts:
#     print(llm.invoke(generate_relationship_prompt("Nitro group", object.name, context)).content)

print(llm.invoke(generate_relationship_prompt_all("Nitro group", class_concepts, context)).content)

# for individual in individual_concepts:
#     for class_ in class_concepts:
#         print(llm.invoke(generate_relationship_prompt(individual.name, class_.name)).content)

# print(llm.invoke(prompt).content)

# create_classes(test_state)

# create_individuals(test_state)

# ontology.save()
