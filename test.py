import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def extract(name):
  img = Image.open('D:\WorkSpace\my-money\\backend\static\images\\' + name)
  orc = pytesseract.image_to_string(img)
  print(orc)

extract('z4223859879142_212bd0e9f1e8c98bab5c10afc8bc6f48.jpg')

