#!/usr/bin/env python3
"""
Generate a simple Unity icon (1024x1024) for Tauri
Uses PIL to create a basic placeholder icon
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    has_pil = True
except ImportError:
    has_pil = False
    print("PIL not available - will create minimal icon")

import os

def create_unity_icon():
    """Create a 1024x1024 Unity icon"""

    if not has_pil:
        print("ERROR: PIL (Pillow) required to generate icons")
        print("Install with: pip install Pillow")
        return False

    # Create 1024x1024 image with gradient background
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw circular background (quantum amber)
    center = size // 2
    radius = int(size * 0.45)

    # Gradient effect (simple radial fill)
    for r in range(radius, 0, -2):
        # Quantum amber to orange gradient
        intensity = int(255 * (r / radius))
        color = (255, 140 + (intensity // 3), 0, 255)  # Orange to amber
        draw.ellipse(
            [(center - r, center - r), (center + r, center + r)],
            fill=color,
            outline=None
        )

    # Draw Unity symbol (stylized U)
    try:
        # Try to use a font (fallback to default)
        font_size = size // 3
        try:
            # Try system fonts
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()

        # Draw "U" for Unity
        text = "U"
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2 - font_size // 8

        # Draw text with shadow
        shadow_offset = 4
        draw.text((text_x + shadow_offset, text_y + shadow_offset), text, fill=(0, 0, 0, 128), font=font)
        draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)

    except Exception as e:
        print(f"Warning: Could not draw text: {e}")
        # Draw simple geometric symbol instead
        symbol_size = size // 4
        draw.rectangle(
            [(center - symbol_size, center - symbol_size),
             (center + symbol_size, center + symbol_size)],
            fill=(255, 255, 255, 200)
        )

    # Save as PNG
    output_path = os.path.join(os.path.dirname(__file__), 'app-icon.png')
    img.save(output_path, 'PNG')
    print(f"✅ Generated Unity icon: {output_path}")
    return True

if __name__ == '__main__':
    success = create_unity_icon()
    exit(0 if success else 1)
