from PIL import Image

def invert_colors(r, g, b):
    """
    Invert the color of a pixel.

    :param r: Red channel
    :param g: Green channel
    :param b: Blue channel
    :return: Tuple of (r, g, b) after inversion
    """
    # Invert the pixel
    r = 255 - r
    g = 255 - g
    b = 255 - b

    return r, g, b

def process_image(image_path):
    # Read the image
    image = Image.open(image_path)
    image = image.convert('RGB')

    # Create a new image for output to avoid changing the original one
    output_image = Image.new('RGB', image.size)

    # Process each pixel
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = image.getpixel((x, y))
            new_color = invert_colors(r, g, b)
            output_image.putpixel((x, y), new_color)

    # Save the modified image without any additional color profile
    output_image.save('abc.png', 'PNG')

    return 'abc.png'


# Example usage:
# Invert the colors of the image at '123.png'
process_image('123.png')
