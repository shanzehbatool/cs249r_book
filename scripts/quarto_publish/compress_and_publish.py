import os
import subprocess
import argparse
import PyPDF4
import sys
from PIL import Image
import io
import ghostscript  # Ensure ghostscript is installed and available

# Default input and output paths
DEFAULT_INPUT_PATH = 'Machine-Learning-Systems.pdf'
DEFAULT_OUTPUT_PATH = 'Machine-Learning-Systems_output.pdf'  # Overwrite the file!

def quarto_pdf_render(output_path):
    """
    Install Quarto's TinyTeX and render the book to PDF.
    """
    print("Installing Quarto TinyTeX")
    subprocess.run(['quarto', 'install', 'tinytex'])
    process = subprocess.run(['quarto', 'render', '--output', output_path, '--to', 'pdf'], check=True)

    print(f"Quarto render process return value: {process.returncode}")

def quarto_publish():
    """
    Publish the rendered book using Quarto.
    """
    print("Publishing the rendered book using Quarto")
    process = subprocess.run(['quarto', 'publish', '--no-render', 'gh-pages'], check=True)

def compress_pdf_pypdf(input_path, output_path):
    """
    Compress a PDF file using PyPDF4 by copying its contents to a new file.

    Args:
        input_path (str): Path to the input PDF file.
        output_path (str): Path to the output compressed PDF file.
    """
    if not os.path.exists(input_path):
        print("Input file does not exist:", input_path)
        return

    print("Compressing PDF using PyPDF4")
    with open(input_path, 'rb') as input_file:
        reader = PyPDF4.PdfFileReader(input_file)
        writer = PyPDF4.PdfFileWriter()
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            writer.addPage(page)
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

def rename_and_overwrite_file(old_path, new_path):
    """
    Rename the new file to the old filename and overwrite it.

    Args:
        old_path (str): Path to the old file.
        new_path (str): Path to the new file.
    """
    print("Renaming", new_path, "to", old_path)
    os.rename(old_path, new_path)  # Rename the new file to the old filename

def compress_pdf_ghostscript(input_path, output_path):
    """
    Compress a PDF file using ghostscript.

    Args:
        input_path (str): Path to the input PDF file.
        output_path (str): Path to the output compressed PDF file.
    """
    print("Compressing PDF using ghostscript")

    command = ['ps2pdf', '-dQUIET', '-dBATCH', '-sDEVICE=pdfwrite',
                '-dPDFSETTINGS=/ebook',
                '-dNOPAUSE',
                f'-sOutputFile={output_path}',
                input_path]

    subprocess.run(command, check=True)

def main():
    """
    Main function to parse command-line arguments and execute the program.
    """
    parser = argparse.ArgumentParser(description="Convert a book to PDF and optionally reduce its size")
    parser.add_argument('-c', '--compress', nargs='?', const='ghostscript', default='ghostscript', choices=['pypdf', 'ghostscript'], help='Compress the PDF file. Default method: ghostscript')
    parser.add_argument('input_path', nargs='?', default=DEFAULT_INPUT_PATH, help='Path to the rendered book file (default: {})'.format(DEFAULT_INPUT_PATH))
    parser.add_argument('output_path', nargs='?', default=DEFAULT_OUTPUT_PATH, help='Path to the output PDF file (default: {})'.format(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    quarto_pdf_render(args.input_path)
    
    full_input_path = os.path.abspath(os.path.join('_book', args.input_path))
    full_output_path = os.path.abspath(os.path.join('_book', args.output_path))

    # Compress if specified
    if args.compress:
        print("Compressing", full_input_path, "to", full_output_path, "using", args.compress)
        if args.compress == 'ghostscript':
            compress_pdf_ghostscript(full_input_path, full_output_path)
        elif args.compress == 'pypdf':  # This option allows for future expansion
            compress_pdf_pypdf(full_input_path, full_output_path)

    rename_and_overwrite_file(full_output_path, full_input_path)

    quarto_publish()

if __name__ == "__main__":
    main()
