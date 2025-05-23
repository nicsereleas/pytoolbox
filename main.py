"""
PyToolbox CLI Utility Suite
Author: Nic Sereleas
Description:
A modular command-line tool written in Python. This file initializes the base CLI interface and its subcommands.
"""

### = Notes for Nic

### Argparse module is used to create command-line interfaces (CLI)
### Handles parsing CL arguments, displaying the help text (--help), and validating output
### https://docs.python.org/3/library/argparse.html
import argparse


### Provides a way to interact with the operating system, especially for file and directory manipulation
### List files/directories, manipulate files, get file properties, etc.
### https://docs.python.org/3/library/os.html
import os

### PyPDF2 is a library for manipulating PDF files
### It allows you to read, write, and manipulate PDF files in Python
### https://pypdf2.readthedocs.io/en/latest/
from PyPDF2 import PdfMerger


### FPDF is a library for creating PDF files in Python
### It allows you to create PDF documents from scratch, add text, images, and other elements
### https://pyfpdf.readthedocs.io/en/latest/
from fpdf import FPDF

import pdfplumber

### Creates the main parser object. Think of this as the main entry point for the CLI (Think root node of the CLI tree)
### Description is optional, but will appear when running --help
parser = argparse.ArgumentParser(description="PyToolbox CLI Utility Suite")

### This is where we setup the subcommands so we can create multiple tools in one toolbox/"tree"
### The dest argumend specifies the name of the subcommand will be stored in args.comman
subparsers = parser.add_subparsers(dest="command")


### Here we register all of the subcommands.
### The first argument is the name of the subcommand
### The help argument is a short description of the subcommand when running --help
### Each subcommand will have its own parser object and functionality
# Rename command
rename_parser = subparsers.add_parser("rename", help="Batch rename files or overwrite individual files")

# Combine command
combine_parser = subparsers.add_parser("combine", help="Combine PDF files")

# Test Analyzer command
analyzer_parser = subparsers.add_parser("analyze", help="Analyze a .txt file", description="If not flags are specified, all will be shown")

### add_argument() tells the parser object what argument to expect when the subcommand is called
### The first argument is the name of the argument
### The help argument is a short description of the argument when running --help
### The default argument is the default value of the argument if not specified
### "--"" prefix means that the argument is optional
### Action argument tells argparser what to do when the command is in CL
### python main.py rename <directory> [options]
rename_parser.add_argument("directory", help="Directory containing the files to rename")
rename_parser.add_argument("--prefix", help="Prefix to add to each file", default="")
rename_parser.add_argument("--suffix", help="Suffix to add to each file", default="")
rename_parser.add_argument(
    "--numbered", action="store_true", help="Add sequential numbering to filenames"
)
rename_parser.add_argument("--overwrite", nargs='+', help="Overwrite existing files, change the base name of the file (do not include extension)", default=None)
rename_parser.add_argument("--txtpdfconvert", action="store_true", help="Convert .txt files to .pdf files or a .pdf file to .txt file", default=False)

### This is the setup for the combine command
### Adding arguments to the combine parser object
### nargs is the number of arguments to be expected
### The "+" means one or more arguments are expected
combine_parser.add_argument(
    "files", nargs="+", help="PDF files to combine (in order)"
)
combine_parser.add_argument(
    "--output", default="combined.pdf", help="Name of the output file"
)

### This is the setup for the analyzer command

analyzer_parser.add_argument("file", help="Text file to analyze")
analyzer_parser.add_argument("--freq", action="store_true", help="Show word frequency count")
analyzer_parser.add_argument("--lines", action="store_true", help="Show total number of lines")
analyzer_parser.add_argument("--words", action="store_true", help="Show total number of words")
analyzer_parser.add_argument("--chars", action="store_true", help="Show total number of characters")


### This function will be called when the rename command is executed
# Function to handle the rename command
def handle_rename(args):
    try:
        # Determine whether the input is a directory or a single file
        if os.path.isdir(args.directory):
            files = os.listdir(args.directory)
            files = [os.path.join(args.directory, f) for f in files]
        elif os.path.isfile(args.directory):
            files = [args.directory]
        else:
            print(f"Path not found: {args.directory}")
            return
        
    except FileNotFoundError:
        print(f"Error: '{args.directory}' not found.")
        return


    for idx, filepath in enumerate(files):
        # Skip subdirectories or non-files
        if not os.path.isfile(filepath):
            continue

        name, ext = os.path.splitext(os.path.basename(filepath))
        if args.overwrite and idx < len(args.overwrite):
            if args.overwrite[idx] is None:
                print(f"Error: Overwrite name cannot be None")
                return
            elif args.overwrite[idx] == "":
                print(f"Error: Overwrite name cannot be empty")
                return
            elif len(args.overwrite) != idx + 1:
                print(f"Error: Overwrite name must be the same length as the number of files")
                return
            new_base = args.overwrite[idx]
        else:
            new_base = name
        new_name = f"{args.prefix}{new_base}{args.suffix}{ext}"
        # If numbering is enabled, it overrides both name and overwrite
        if args.numbered:
            new_name = f"{args.prefix}{idx+1}{args.suffix}{ext}"

        # Build the new path in the same directory
        new_path = os.path.join(os.path.dirname(filepath), new_name)

        # Check if the file is a .txt file and if the user wants to convert it to .pdf
        if args.txtpdfconvert and ext.lower() == ".txt":
            pdf = FPDF() # Create a PDF object
            pdf.add_page() # Add a page to the PDF
            pdf.set_font("Arial", size = 15) # Set the font and size
            
            # Read the .txt file and add its content to the PDF
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    pdf.cell(200, 10, txt=line.encode('latin-1', 'replace').decode('latin-1'), ln=True) # Add content to the PDF
            output_dir = "./output_pdf" # Create the output directory
            os.makedirs(output_dir, exist_ok=True) # Create the output directory if it doesn't exist
            output_pdf = os.path.join(output_dir, f"{args.prefix}{name}{args.suffix}.pdf") # Create the output PDF name
            pdf.output(output_pdf) # Create the PDF file

        # Check if the file is a .pdf file and if the user wants to convert it to .txt
        elif args.txtpdfconvert and ext.lower() == ".pdf":
            with pdfplumber.open(filepath) as pdf: # Open the PDF file
                text = "" # Initialize an empty string to store the text
                for page in pdf.pages: # Iterate through each page of the PDF
                    text += page.extract_text() # Extract text from the page
            output_dir = "./output_txt"
            os.makedirs(output_dir, exist_ok=True)
            output_txt = os.path.join(output_dir, f"{args.prefix}{name}{args.suffix}.txt") # Create the output .txt name
            # Write the extracted text to a .txt file
            with open(output_txt, "w", encoding="utf-8") as f:
                f.write(text)


        os.rename(filepath, new_path)
        print(f"Renamed '{os.path.basename(filepath)}' -> '{new_name}'")



# Function to handle the combine command
def handle_combine(args):

    ### Creates a PdfMerger object to handle the merging
    # Initialize object
    merger = PdfMerger()

    # Skip the non-PDF files
    for file in args.files:
        if not file.endswith(".pdf"):
            print(f"Skipping non-PDF: {file}")
            continue
        
        # Attemps to append each file to the merger
        try:
            merger.append(file)
            print(f"Added: {file}")
        except FileNotFoundError: # File not found
            print(f"File not found: {file}")
        except Exception as e: # General exception handling
            # Handles other exceptions (e.g., file not readable)
            print(f"Error adding {file}: {e}")

    ### merger.write() writes the merged PDF to the specified output file
    ### merger.close() closes the merger object
    ### This is important to free up resources and finalize the output file
    # Attempt to write the merged PDF to the output file
    try:
        merger.write(args.output)
        merger.close()
        print(f"Combined PDF saved as: {args.output}") # Output message
    except Exception as e: # General exception handling
        print(f"Failed to write output PDF: {e}")

from collections import Counter

def handle_analyze(args):
    try:
        # Open the file in read mode and save the file in text
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError: # General exception handling
        print(f"File not found: {args.file}")
        return

    # Split the text into lines, words, and characters
    lines = text.splitlines()
    words = text.split()
    chars = len(text)

    # Count the frequency of each word
    freq = Counter(words)

    if not (args.freq or args.lines or args.words or args.chars):
        args.freq = args.lines = args.words = args.chars = True

    if args.lines:
        print(f"Total lines: {len(lines)}")
    if args.words:
        print(f"Total words: {len(words)}")
    if args.chars:
        print(f"Total characters: {chars}")
    if args.freq:
        print("\nTop 10 most common words:")
        for word, count in freq.most_common(10):
            print(f"{word}: {count}")


# Main function to handle the command-line interface
args = parser.parse_args()

# Check if a command was provided
if args.command == "rename":
    handle_rename(args)
elif args.command == "combine":
    handle_combine(args)
elif args.command == "analyze":
    handle_analyze(args)