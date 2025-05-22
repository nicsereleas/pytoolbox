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
analyzer_parser = subparsers.add_parser("analyze", help="Analyze a file")

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

# Main function to handle the command-line interface
args = parser.parse_args()

# Check if a command was provided
if args.command == "rename":
    handle_rename(args)