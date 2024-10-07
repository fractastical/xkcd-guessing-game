import requests
from PIL import Image
from io import BytesIO
import pytesseract
import openai
import os
import time

# Initialize OpenAI API
openai.api_key = "your-openai-api-key"  # Replace with your OpenAI API key

# Directory to save outputs
OUTPUT_DIR = "xkcd_output"
CHECKPOINT_FILE = os.path.join(OUTPUT_DIR, "checkpoint.txt")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Batch size (how many comics to process in one go)
BATCH_SIZE = 10

# Step 1: Fetch the latest comic to get the maximum comic ID
def get_latest_comic_id():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    return response.json()['num']

# Step 2: Fetch comic metadata using comic ID
def get_comic(comic_id):
    url = f"https://xkcd.com/{comic_id}/info.0.json"
    response = requests.get(url)
    return response.json()

# Step 3: Download comic image
def download_comic_image(comic_url):
    response = requests.get(comic_url)
    img = Image.open(BytesIO(response.content))
    return img

# Step 4: Extract text using Tesseract OCR
def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

# Step 5: Generate AI art based on the extracted text
def generate_image_from_text(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        return response['data'][0]['url']
    except Exception as e:
        print(f"Error generating image for prompt '{prompt}': {e}")
        return None

# Step 6: Save the text and generated image URL
def save_output(comic_id, text, image_url):
    text_file = os.path.join(OUTPUT_DIR, f"xkcd_{comic_id}_text.txt")
    image_url_file = os.path.join(OUTPUT_DIR, f"xkcd_{comic_id}_image_url.txt")
    
    # Save extracted text
    with open(text_file, "w") as f:
        f.write(text)
    
    # Save image URL
    if image_url:
        with open(image_url_file, "w") as f:
            f.write(image_url)

# Step 7: Read or update the checkpoint
def get_last_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return int(f.read().strip())
    return 1

def update_checkpoint(last_comic_id):
    with open(CHECKPOINT_FILE, "w") as f:
        f.write(str(last_comic_id))

# Step 8: Main loop to iterate over comics in batches and process them
def process_xkcd_comics_in_batches():
    latest_comic_id = get_latest_comic_id()  # Get the latest comic ID
    last_comic_id = get_last_checkpoint()  # Get the last processed comic ID
    
    for start_id in range(last_comic_id, latest_comic_id + 1, BATCH_SIZE):
        end_id = min(start_id + BATCH_SIZE - 1, latest_comic_id)
        print(f"Processing comics from {start_id} to {end_id}...")
        
        for comic_id in range(start_id, end_id + 1):
            try:
                # Fetch comic metadata and image
                comic_data = get_comic(comic_id)
                comic_image = download_comic_image(comic_data['img'])
                
                # Extract text from image
                extracted_text = extract_text_from_image(comic_image)
                print(f"Extracted text from comic {comic_id}: {extracted_text}")
                
                # Generate AI art from extracted text
                if extracted_text.strip():  # Ensure the text is not empty
                    ai_image_url = generate_image_from_text(extracted_text)
                    print(f"Generated AI image for comic {comic_id}: {ai_image_url}")
                else:
                    ai_image_url = None
                
                # Save the extracted text and AI image URL
                save_output(comic_id, extracted_text, ai_image_url)

            except Exception as e:
                print(f"Error processing comic {comic_id}: {e}")

        # Update checkpoint after processing each batch
        update_checkpoint(end_id)
        print(f"Checkpoint updated. Last processed comic ID: {end_id}")
        
        # Sleep to avoid overloading API or server requests
        time.sleep(5)

if __name__ == "__main__":
    process_xkcd_comics_in_batches()
