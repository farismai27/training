import pdfplumber

pdf_path = r'C:\Users\farismai2\coding\training\OneSuite-Platform User Stories-110126-222135.pdf'

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(text)
        if i < len(pdf.pages) - 1:
            print("\n" + "="*80 + "\n")
