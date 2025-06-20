import fitz
import spacy
nlp = spacy.load("en_core_web_sm")


pdf_path= "second.pdf"
text= ""
doc  = fitz.open(pdf_path)
for page in doc:
    text+=page.get_text()

def chunk_text(text):
    doc = nlp(text)
    return [sent.text for sent in doc.sents]
chunks = chunk_text(text)
for i in chunks:
    print(len(i))