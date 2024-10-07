# PDF to Image Converter

## Description
This project is a PDF to Image Converter that allows users to convert specific pages of a PDF document into image format as PNG. The application is built using Python with a graphical user interface (GUI) developed in PyQt6. 

> [!NOTE]
> The ```.tex``` and ```.html``` files are excluded from this project because the GUI was created using PyQt6 Designer, and the executable was generated with PyInstaller. As a result, only Python is listed as the primary language in this repository, even though additional tools were used for the development process.

### Version
This is the very first beta version (1.0) of this project, _and it works only for the PDF file inside the project._

## Features
- Select specific pages from a PDF to convert.
- Convert pages to PNG format.
- Simple and user-friendly interface.

## Requirements
To run this project, you need the following Python packages:
- PyQt6
- Pillow
- zlib (built-in)
- io (built-in)
- subprocess (built-in)
- argparse (built-in)

You can install the required packages using pip:

```bash
pip install PyQt6 Pillow
```
## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/code-freq/pdf-to-image-converter.git
   ```
2. Navigate to the project directory:
   ```bash
   cd pdf-to-image-converter
   ```
3. Install the required packages using pip as mentioned above:
   
## Usage
1. To use the application, run the ```pdf2img.exe``` file located in the ```dist``` folder.

> [!WARNING]
> *Currently, this code works only for the specific PDF file _```image_only.pdf```_ included in the project.*

