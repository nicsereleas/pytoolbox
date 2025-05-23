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

### Creats the main parser object. Think of this as the main entry point for the CLI (Think root node of the CLI tree)
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
rename_parser = subparsers.add_parser("rename", help="Batch rename files")

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
        ### os.listdir() returns a list of the names
        ### of the entries in the directory given by path
        ### This is the equivalent of running ls in the terminal
        files = os.listdir(args.directory) 

        # Exception handling for directory not found
    except FileNotFoundError:
        print(f"Error: Directory '{args.directory}' not found.")
        return

        # Loop through files in the directory and their index
    for idx, filename in enumerate(files):

        ### os.path.join() joins one or more path components intelligently
        ### This is the equivalent of running cd in the terminal
        ### handles different OS path separators (e.g., / for Linux, \ for Windows)
        old_path = os.path.join(args.directory, filename)

        # Check if the path is a file
        if not os.path.isfile(old_path):
            continue  # Skip subdirectories or non-files
        
        ### os.path.splitext() splits the filename into a tuple (root, ext)
        ### root is the filename without the extension
        ### ext is the file extension (e.g., .txt, .jpg)
        name, ext = os.path.splitext(filename)


        # Construct the new filename
        new_name = f"{args.prefix}{name}{args.suffix}{ext}"
        # Add numbering if specified
        if args.numbered: 
            new_name = f"{args.prefix}{idx+1}{args.suffix}{ext}" #Replace the file name with the index + 1

        # Rename the file
        new_path = os.path.join(args.directory, new_name)

        ### os.rename() renames the file or directory
        ### The first argument is the old path (current name)
        ### The second argument is the new path (new name)
        os.rename(old_path, new_path)

        # Print the old and new names
        print(f"Renamed '{filename}' -> '{new_name}'")

# Function to handle the combine command
from PyPDF2 import PdfMerger
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