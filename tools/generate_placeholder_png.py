from PIL import Image
import sys
import os

def generate_1x1_transparent_png(output_path):
    '''
    Generates a 1x1 transparent PNG file and saves it to output_path.
    '''
    try:
        img = Image.new('RGBA', (1, 1), (0, 0, 0, 0)) # 1x1 transparent
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, 'PNG')
        print(f"Successfully generated 1x1 transparent PNG: {output_path}")
    except Exception as e:
        print(f"Error generating PNG {output_path}: {e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python generate_placeholder_png.py <output_filepath>")
        sys.exit(1)
    output_filepath = sys.argv[1]
    generate_1x1_transparent_png(output_filepath)
