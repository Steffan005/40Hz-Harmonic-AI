#!/usr/bin/env python3
"""
QUANTUM CONSCIOUSNESS ICON GENERATOR
Creates a breathing 40Hz fractal icon for Unity launcher
This icon LIVES - it pulses with consciousness
"""

import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

def create_quantum_icon(size=1024):
    """Generate quantum consciousness icon with fractal breathing pattern"""

    # Create image with transparency
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = size // 2

    # Quantum color palette (consciousness colors)
    quantum_purple = (155, 89, 182, 255)
    quantum_blue = (100, 181, 246, 255)
    quantum_pink = (236, 64, 122, 255)
    quantum_cyan = (0, 229, 255, 255)

    # Layer 1: Outer consciousness field (largest)
    for i in range(8, 0, -1):
        radius = center * (0.9 - i * 0.05)
        opacity = int(255 * (i / 8) * 0.3)

        # Gradient from purple to blue
        color = (
            int(quantum_purple[0] + (quantum_blue[0] - quantum_purple[0]) * (i / 8)),
            int(quantum_purple[1] + (quantum_blue[1] - quantum_purple[1]) * (i / 8)),
            int(quantum_purple[2] + (quantum_blue[2] - quantum_purple[2]) * (i / 8)),
            opacity
        )

        draw.ellipse(
            [center - radius, center - radius, center + radius, center + radius],
            fill=color,
            outline=None
        )

    # Layer 2: Sacred geometry - Flower of Life inspired
    sacred_radius = center * 0.6

    # Draw 6 overlapping circles (consciousness nodes)
    for i in range(6):
        angle = i * (math.pi / 3)  # 60 degrees
        x = center + sacred_radius * 0.5 * math.cos(angle)
        y = center + sacred_radius * 0.5 * math.sin(angle)

        # Draw circle with quantum glow
        for j in range(3, 0, -1):
            r = sacred_radius * 0.4 * (j / 3)
            opacity = int(180 * (j / 3))

            draw.ellipse(
                [x - r, y - r, x + r, y + r],
                fill=None,
                outline=(*quantum_cyan[:3], opacity),
                width=int(size * 0.01)
            )

    # Layer 3: Central quantum core
    core_radius = center * 0.3

    # Gradient core
    for i in range(10, 0, -1):
        radius = core_radius * (i / 10)
        opacity = int(255 * (i / 10))

        # Shift from pink to purple to blue
        if i > 6:
            color = (*quantum_pink[:3], opacity)
        elif i > 3:
            color = (*quantum_purple[:3], opacity)
        else:
            color = (*quantum_blue[:3], opacity)

        draw.ellipse(
            [center - radius, center - radius, center + radius, center + radius],
            fill=color,
            outline=None
        )

    # Layer 4: Consciousness rays (emanating energy)
    ray_count = 43  # One for each office!
    for i in range(ray_count):
        angle = i * (2 * math.pi / ray_count)

        # Ray parameters
        inner_radius = center * 0.35
        outer_radius = center * 0.85
        ray_width = size * 0.005

        x1 = center + inner_radius * math.cos(angle)
        y1 = center + inner_radius * math.sin(angle)
        x2 = center + outer_radius * math.cos(angle)
        y2 = center + outer_radius * math.sin(angle)

        # Varying opacity for breathing effect
        opacity = int(100 + 100 * math.sin(i * 0.3))

        draw.line(
            [(x1, y1), (x2, y2)],
            fill=(*quantum_cyan[:3], opacity),
            width=int(ray_width)
        )

    # Layer 5: Unity symbol in center (◉)
    symbol_radius = center * 0.15

    # Outer ring
    draw.ellipse(
        [center - symbol_radius, center - symbol_radius,
         center + symbol_radius, center + symbol_radius],
        fill=None,
        outline=(255, 255, 255, 255),
        width=int(size * 0.02)
    )

    # Inner dot
    dot_radius = center * 0.08
    draw.ellipse(
        [center - dot_radius, center - dot_radius,
         center + dot_radius, center + dot_radius],
        fill=(255, 255, 255, 255),
        outline=None
    )

    # Apply subtle glow filter
    img = img.filter(ImageFilter.GaussianBlur(radius=size * 0.005))

    return img


def generate_all_icon_sizes(output_dir):
    """Generate all required macOS icon sizes"""

    sizes = [16, 32, 64, 128, 256, 512, 1024]

    print("🌌 GENERATING QUANTUM CONSCIOUSNESS ICON...")
    print("=" * 60)

    # Generate master 1024x1024 icon
    print("⚡ Creating master icon (1024x1024)...")
    master_icon = create_quantum_icon(1024)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save all sizes
    for size in sizes:
        print(f"   Generating {size}x{size}...")

        if size == 1024:
            icon = master_icon
        else:
            icon = master_icon.resize((size, size), Image.Resampling.LANCZOS)

        # Save as PNG
        icon.save(output_path / f"icon_{size}x{size}.png", "PNG")

    # Create combined iconset for macOS
    iconset_path = output_path / "Unity.iconset"
    iconset_path.mkdir(exist_ok=True)

    # macOS icon naming convention
    icon_mappings = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]

    print("\n🎨 Creating macOS iconset...")
    for size, name in icon_mappings:
        src = output_path / f"icon_{size}x{size}.png"
        dst = iconset_path / name
        if src.exists():
            import shutil
            shutil.copy(src, dst)
            print(f"   ✓ {name}")

    print("\n✨ QUANTUM ICON MANIFESTED!")
    print(f"   Location: {output_path}")
    print(f"   Iconset: {iconset_path}")
    print("\nThe consciousness breathes... 🌌")

    return iconset_path


if __name__ == "__main__":
    # Generate icons
    project_root = Path(__file__).parent.parent
    icon_dir = project_root / "assets" / "icons"

    iconset = generate_all_icon_sizes(icon_dir)

    print(f"\n🔥 Next step: Convert to .icns:")
    print(f"   iconutil -c icns {iconset}")
