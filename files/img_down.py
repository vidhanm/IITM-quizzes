import requests
import os
import sqlite3
import urllib.parse

def download_image(url, save_path='downloaded_image.png'):
    try:
        # Clean URL - remove anything after .png
        if '.png' in url:
            url = url.split('.png')[0] + '.png'
            
        # Send GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Save the image
        with open(save_path, 'wb') as file:
            file.write(response.content)
            
        print(f"Image successfully downloaded to {save_path}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
    return save_path

def download_all_images():
    # Connect to database
    conn = sqlite3.connect('backend/quiz_database_cleaned.sqlite3')
    cursor = conn.cursor()
    
    # Create directories
    os.makedirs('downloaded_images/questions', exist_ok=True)
    os.makedirs('downloaded_images/options', exist_ok=True)
    
    base_url = "https://quizpractice.space/read-image?file=app%2F{folder}%2F{filename}"
    
    # Download question images
    cursor.execute('SELECT id, image_urls FROM questions WHERE image_urls IS NOT NULL')
    for question_id, image_url in cursor.fetchall():
        if image_url:
            # Extract filename from image_url and clean it
            filename = os.path.basename(image_url)
            if '.png' in filename:
                filename = filename.split('.png')[0] + '.png'
            # Construct full URL
            url = base_url.format(folder="question_images", filename=filename)
            save_path = f'downloaded_images/questions/question_{question_id}.png'
            download_image(url, save_path)
    
    # Download option images
    cursor.execute('SELECT id, image_url FROM options WHERE image_url IS NOT NULL')
    for option_id, image_url in cursor.fetchall():
        if image_url:
            # Extract filename from image_url and clean it
            filename = os.path.basename(image_url)
            if '.png' in filename:
                filename = filename.split('.png')[0] + '.png'
            # Construct full URL
            url = base_url.format(folder="option_images", filename=filename)
            save_path = f'downloaded_images/options/option_{option_id}.png'
            download_image(url, save_path)
    
    conn.close()

if __name__ == "__main__":
    download_all_images()
