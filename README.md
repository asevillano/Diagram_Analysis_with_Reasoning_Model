# Connections Design Analysis

This repo has the aim to demostrate the o1 capabilities to analyze complex images of Connections Design to understand the legends of connections types and the legends of symbols, and use them to identify them by their names and extract the design connections between devices using the connection types and names specified in the legends.

## Image file names for pre-procesing:
**Legend pages:** [ProductName]_legend_1.png, [ProductName]_legend_2.png, etc.

**Schema file name:** [ProductName]_schema.png:
- the legend of connections types should be in the main schema, to extract them in the first step of analysis
- the connections between devices should be in this image

## Pre-procesing:
The notebook (analyze-image-file.ipynb)[./analyze-image-file.ipynb] does everything, pre-processing the documens, extracting connection types and extract connections.
Pre-processing the documentation:
- Extract pages from PDFs to PNG files (after this step you have to rename the files according the "lengend" or "schema" naming)
- Stitch legends pages and schema page in a single image (first you have to create a directory and move the legends PNG pages and the schema to that directory, and specify in the notebook). It will generate the file [ProductName]_stitchted.png
- Step 1: extract the connection types from the schema image, specifying the schema PNG file name ([ProductName]_schema.png)
- Step 2: extract the connections from the stitched image with the legends and the schema [ProductName]_stitchted.png

## Streamlit demo app:
The streamlit demo app has to be run with this command: streamlit run analyze-images-app.py

## Requirements:

  - Python 3.12+
  - python-dotenv (pip install python-dotenv)
  - openai (pip install openai)
  - PymuPDF (pip install pymupdf)
  - Pillow (pip install pillow)
