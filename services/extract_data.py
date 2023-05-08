# %%
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def extract(name):
  img = Image.open('D:\WorkSpace\my-money\\backend\static\images\\' + name)
  orc = pytesseract.image_to_string(img)
  print(orc)


# %%
# import spacy

# nlp = spacy.load("xx_ent_wiki_sm")
# doc = nlp("10220 ® @ - HH l. KOẠI m C . . ^ S ø^ 18/05/2023 10:20 VietinBonk 524S2530U6L9N5H4, Quý khách đõ giơo dịch thành công! Từ tời khoản T††tttD940 TRUONG THỊ HANH Đến tời khoón 2011856886886 NGUYEN THỊ DIEM Ngôn hờng Ngôn hởng Quôn đội Số tiền 500,000 VND Bơ trăm nghìn đồng Phí Miễn phí Nội dung con Nguyen hơ my dong quy lop ơ ee , . n | 9 ớôI G = Ẻ : .< lống ngoy Alios miễn phí = WX HY 9 N Y Y HH m Ô À DoOeovASEON œzz _ằ. L p ˆ l v _¬ ^L, Tải về Œ Chio sẻ u mv vAi n m = D <q")

# for ent in doc.ents:
#     print(ent.text, ent.start_char, ent.end_char, ent.label_)



