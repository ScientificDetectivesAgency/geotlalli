import os
from PIL import Image

def convert_to_webp(directory):
    count = 0
    for filename in os.listdir(directory):
        if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            jpg_path = os.path.join(directory, filename)
            webp_filename = os.path.splitext(filename)[0] + '.webp'
            webp_path = os.path.join(directory, webp_filename)
            
            try:
                # Only convert if webp doesn't exist already
                if not os.path.exists(webp_path):
                    with Image.open(jpg_path) as img:
                        img.save(webp_path, 'webp', optimize=True, quality=80)
                    count += 1
                    print(f"Converted {filename} to {webp_filename}")
                
                # Delete original JPG to save space
                os.remove(jpg_path)
            except Exception as e:
                print(f"Error converting {filename}: {e}")
                
    print(f"Finished converting {count} images to WebP.")

if __name__ == "__main__":
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else 'fotos/fotos'
    convert_to_webp(directory)
