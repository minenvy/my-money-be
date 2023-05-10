import spacy
from spacy.tokens import DocBin
from tqdm import tqdm

nlp = spacy.blank("en") # load a new spacy model
db = DocBin() # create a DocBin object

import json

file = open(
        'D:\WorkSpace\my-money\\backend\services\\ner\\training_data.json', 'r', encoding='utf-8')
TRAIN_DATA = json.loads(file.read())
file.close()

for text, annot in tqdm(TRAIN_DATA['annotations']): 
    doc = nlp.make_doc(text) 
    ents = []
    for start, end, label in annot["entities"]:
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            print("Skipping entity")
        else:
            ents.append(span)
    doc.ents = ents 
    db.add(doc)

db.to_disk("D:\WorkSpace\my-money\\backend\services\\ner\\training_data.spacy") # save the docbin object