class DocType:
    def __init__(self, docType_code, desc, sale):
        self.docType_code = str(docType_code)
        self.desc = desc
        self.sale = sale

    def __str__(self):
        return f"{self.docType_code} || {self.desc} || {self.sale}"