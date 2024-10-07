# XKCD Comic Text Extractor & AI Art Generator Game

This project is a Python-based script that extracts text from XKCD comics using OCR (Optical Character Recognition) and generates AI art based on the extracted text using OpenAI's DALL·E model. The game component involves matching the AI-generated images to the original XKCD comics based on the extracted text.

## Features
- Extracts text from XKCD comics using `Tesseract` OCR.
- Generates AI art using OpenAI's DALL·E based on the extracted text.
- Saves the extracted text and AI-generated image URLs in a directory.
- Processes comics in batches for efficiency and to avoid API overload.
- Includes a checkpoint system to resume from the last processed comic in case of interruptions.

## How the Game Works

### Game Concept

The game involves:
1. Viewing an AI-generated image.
2. Looking at a set of XKCD comics.
3. The objective is to match the AI-generated image with the appropriate comic based on the comic text.

The AI art is generated using the text extracted from an XKCD comic. The challenge for the player is to figure out which comic the AI art represents!

### Game Play
1. **Start the Game**: Once the script has processed the XKCD comics and generated AI art, you will have pairs of extracted text and AI-generated images.
2. **Match**: Review the AI art and the list of comics (you can use a set of printouts or display them digitally).
3. **Select**: Choose the comic that you think the AI art is based on. Use the extracted text for clues!
4. **Compare**: After selecting a match, check the saved extracted text from the comic and compare it to the AI-generated image. The closer the match, the better!

## Installation

1. Clone the repository or download the code.

2. Install the required dependencies:

   ```bash
   pip install requests pytesseract Pillow openai
