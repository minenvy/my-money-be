import spacy
import os
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
nlp = spacy.load("D:\WorkSpace\my-money\\backend\services\\ner\\model-best\\")
tags = ['MONEY', 'DATE', 'NOTE']


def extract(name):
    img = Image.open(
        'D:\WorkSpace\my-money\\backend\static\images\\' + name)
    orc = pytesseract.image_to_string(img, lang='vie')
    return str(orc)


def recognizeEntity(text):
    doc = nlp(text)
    ner = {}

    for ent in doc.ents:
        ner[ent.label_] = ent.text
    return ner
