import requests
import os

def download_image(url, save_path='downloaded_image.png'):
    try:
        # Send GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Save the image
        with open(save_path, 'wb') as file:
            file.write(response.content)
            
        print(f"Image successfully downloaded to {save_path}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")

# URL of your image
url = "https://quizpractice.space/read-image?file=app%2Fquestion_images%2FxPEL0TvMqXWsSuqBSPTIRhuFCGrNbZ2t9BKHzl3NJvUZ9na0wI.png"

# Download the image
download_image(url)
