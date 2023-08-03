import spacy
import os
import pytesseract
from PIL import Image
import re
from datetime import datetime

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


banks = ['vietinbank']
def getBankFromText(text):
  for bank in banks:
    if (bank in text.lower()):
      return bank
  return 'Tiền mặt'


def standardizedEntity(money, date, note, bank):
    note = '"""' + note + '"""' if note else ''

    money = re.sub("[^\d\.]", "", money.replace(
        'o', '0').replace('O', '0')) if money else 0

    if not date:
        date = datetime.now()
    else:
        yearFirstRegex = '\d{4}\/\d{2}\/\d{2}|\d{4}\-\d{2}\-\d{2}'
        dayFirstRegex = '\d{2}\-\d{2}\-\d{4}|\d{2}\/\d{2}\/\d{4}'
        dateString = re.search(yearFirstRegex, date)
        if dateString:
            date = datetime.strptime(dateString.group(), '%Y/%m/%d')
        else:
            dateString = re.search(dayFirstRegex, date)
            if dateString:
                date = datetime.strptime(dateString.group(), '%d/%m/%Y')
            else:
                date = datetime.now()

    if note:
        textsInNote = note.split()
        note = ' '.join([str(ele)
                        for ele in textsInNote]).replace('"""', '')

    bank = bank.lower()

    return [money, date, note, bank]


def getClosestWalletName(wallets, bank):
    walletId = ''
    for wallet in wallets:
        if (wallet[1].lower() in bank):
            walletId = wallet[0]
            break
    return walletId
        
