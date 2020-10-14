from PIL import Image, ImageDraw, ImageFont
import os


image_path = "/home/pi/Projects/CuckooPi/cache/Buteo_lineatus/photo/50397774597.jpg"

def text_to_image(image_path: str, text: str):

    if not os.path.isfile(image_path):

        raise FileNotFoundError("No image file was found.")
    
    # Load image
    image = Image.open(image_path)

    # Draw context
    draw = ImageDraw.Draw(image)
    
    # Get font from file (or download)
    font_found = False
    while not font_found:

        try:
        
            font_file = "/usr/share/fonts/lato/Lato-Bold.ttf"
            font = ImageFont.truetype(font_file, size=40, encoding="unic")
            #font = ImageFont.load_default()
            font_found = True

        except FileNotFoundError:

            # Run font download script
            os.system("python3 config/get_font.py")
        
        except:

            pass

    # Position text
    (x, y) = (25, 10)
    color = "#%02x%02x%02x" % (255, 255, 255)  # white

    # Draw text on image
    draw.text((x, y), text, fill=color, font=font)

    # Save image
    image.save(image_path)
    