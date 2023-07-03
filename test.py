from services.extract_data import extract, recognizeEntity
import re
import pytesseract
from PIL import Image
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Get the list of all files and directories
path = "D:\WorkSpace\my-money\\backend\static\images"
dir_list = os.listdir(path)

# for filename in dir_list:
#     print(filename)

#     filetext = open('D:\WorkSpace\my-money\\backend\\text.txt',
#                     'a', encoding='utf-8')
#     img = Image.open(
#         'D:\WorkSpace\my-money\\backend\static\images\\' + filename)
#     orc = pytesseract.image_to_string(img)
#     filetext.write(orc)
#     filetext.write('\n***\n')

def test(filename):
    img = Image.open(
        'D:\WorkSpace\my-money\\backend\static\images\\' + filename)
    orc = pytesseract.image_to_string(img)
    print(orc)
    ner = recognizeEntity(orc)
    print(ner)
    # filetext.write(orc)

test('345279166_803177197628419_380700008197776655_n.jpg')
