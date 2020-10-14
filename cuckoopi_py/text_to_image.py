from PIL import Image, ImageDraw, ImageFont, ImageColor
import os


# Calculate the luminance of a color
def __luminance(c):

    red, green, blue = ImageColor.getrgb(c)  # Convert Hex to RGB tuple
    return (.299 * red) + (.587 * green) + (.114 * blue)


# Return True if color 1 is compatible with color 2, and False otherwise.
def __are_compatible(c1, c2):

    return abs(__luminance(c1) - __luminance(c2)) >= 128.0


# Write text to an image file
def text_to_image(image_path: str, common_name: str, binomial: str, font_size_main: int=45, font_size_sub: int=30):

    if not os.path.isfile(image_path):

        raise FileNotFoundError(f"No image file was found at {image_path}.")
    
    # Get font from file
    font_found = False
    while not font_found:

        try:
        
            font_main_file = "config/fonts/LiberationSans-Bold.ttf"
            font_sub_file = "config/fonts/LiberationSans-Italic.ttf"
            font_main = ImageFont.truetype(font_main_file, size=font_size_main, encoding="unic")
            font_sub = ImageFont.truetype(font_sub_file, size=font_size_sub, encoding="unic")
            font_found = True

        except FileNotFoundError("Missing font file(s)."):

            # Load system default font
            font_main = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_found = True
        
        except:

            raise ValueError("There was an error loading fonts for the photo caption.")

    # Load image
    image = Image.open(image_path)

    # Determine background color from region of the image
    w, h = image.size
    left = 0
    top = 0
    right = w * 0.25
    bottom = h * 0.25
  
    # Cropped image of above dimension 
    im = image.crop((left, top, right, bottom))

    # Determine best text color from cropped region (text is black by default)
    num_pixels = im.size[0] * im.size[1]
    colors = sorted(im.getcolors(num_pixels), reverse=True)
    main_color = '#%02x%02x%02x' % colors[0][1]
    text_color = "#%02x%02x%02x" % (255, 255, 255)  # assumes bright colors - black font used

    if not __are_compatible(text_color, main_color):
    
        text_color = "#%02x%02x%02x" % (0, 0, 0)  # dark colors - white font instead
  
    # Position text (top left corner)
    (x, y) = (0.035*w, 0.035*h)  # 3.5% of the width (from left), 3.5% of the height (from top)

    # Draw text on image
    draw = ImageDraw.Draw(image)
    draw.text((x, y), common_name, fill=text_color, font=font_main)
    draw.text((x, y+48), f"{binomial}", fill=text_color, font=font_sub)

    # Save image
    image.save(image_path)
