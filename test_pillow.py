from PIL import Image, ImageDraw, ImageFont
import sys
import os

def test_pillow_installation():
    """Test that Pillow is installed correctly by creating a simple test image."""
    print(f"Using Pillow version: {Image.__version__}")
    
    # Create a test image
    img = Image.new('RGB', (400, 200), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    
    # Add some text
    d.text((10,10), "Pillow Test Image", fill=(255,255,0))
    d.text((10,50), f"Pillow version: {Image.__version__}", fill=(255,255,0))
    
    # Save to the screenshots directory
    os.makedirs('screenshots', exist_ok=True)
    test_image_path = 'screenshots/test_pillow.png'
    img.save(test_image_path)
    
    print(f"Test image saved to {test_image_path}")
    return True

if __name__ == "__main__":
    if test_pillow_installation():
        print("Pillow installation is working correctly!")
    else:
        print("There was an issue with the Pillow installation.")
        sys.exit(1) 