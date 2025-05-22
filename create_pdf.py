from fpdf import FPDF

def create_dummy_pdf(name, content):
    pdf = FPDF() # Create a PDF object
    pdf.add_page() # Add a page to the PDF
    pdf.set_font("Arial", size=16) # Set the font and size
    pdf.cell(200, 10, txt=content, ln=True, align="C") # Add content to the PDF
    pdf.output(name) # Create a PdfMerger object

# Call the function to create three dummy PDFs
create_dummy_pdf("file1.pdf", "This is File 1")
create_dummy_pdf("file2.pdf", "This is File 2")
create_dummy_pdf("file3.pdf", "This is File 3")