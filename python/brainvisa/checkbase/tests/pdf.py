
from soma.qt_gui.qt_backend.Qt import QPrinter, QTextDocument, QSizeF


class PDFReportPrinter():
    '''
    This class allows to generate a PDF file from some HTML source. The document title
    can be specified as parameter.

    :Example:

    >>> printer = PDFReportPrinter('/tmp/report.pdf', docname='Document Title', html=html_source_code)
    >>> printer.print_()

    '''

    def setHTMLDocument(self, html):
        self.document.setHtml(html)

    def print_(self):
        self.document.print_(self.printer)

    def __init__(self, filename, docname="Report", html=None, doc_height=250.0):

        # Generating the PDF report
        self.printer = QPrinter()
        self.printer.setOutputFileName(str(filename))
        self.printer.setOutputFormat(QPrinter.PdfFormat)

        self.printer.setColorMode(QPrinter.Color)
        self.printer.setCreator('Qlctst')
        self.printer.setDocName(str(docname))
        self.printer.setDoubleSidedPrinting(True)
        self.printer.setFontEmbeddingEnabled(True)
        self.printer.setFromTo(0, 0)
        self.printer.setPageMargins(5., 5., 5., 5., QPrinter.Millimeter)
        # self.printer.setOrientation(QPrinter.Landscape)
        # self.printer.setPageSize(QPrinter.Custom)
        self.printer.setPaperSize(QSizeF(70., doc_height), QPrinter.Millimeter)
        self.printer.setFullPage(True)
        self.printer.setNumCopies(1)
        self.printer.setResolution(100)
        self.printer.setOrientation(QPrinter.Portrait)

        self.printer.setPageOrder(QPrinter.FirstPageFirst)
        #self.printer.setPageSize ( QPrinter.A4 )
        self.printer.setPaperSource(QPrinter.Auto)
        self.printer.setPrintRange(QPrinter.AllPages)

        self.document = QTextDocument()

        if not html is None:
            self.setHTMLDocument(html)
