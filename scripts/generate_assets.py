import os
import math
from PIL import Image, ImageDraw, ImageFont

PUBLIC_DIR = r"C:\Users\murli mishra\.gemini\antigravity\scratch\LeanInHack\frontend\public"
os.makedirs(PUBLIC_DIR, exist_ok=True)

# 1. Create favicon.svg
svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3B82F6" />
      <stop offset="100%" stop-color="#1D4ED8" />
    </linearGradient>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0B132B" />
      <stop offset="100%" stop-color="#05080F" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="#2563EB" flood-opacity="0.45" />
    </filter>
  </defs>

  <!-- Background rounded card -->
  <rect width="512" height="512" rx="112" fill="url(#bgGrad)" />

  <!-- Shield Shape with subtle outer glow -->
  <g filter="url(#glow)">
    <path d="M 256 70 
             C 330 70, 400 95, 412 110 
             C 412 250, 360 380, 256 442 
             C 152 380, 100 250, 100 110 
             C 112 95, 182 70, 256 70 Z" 
          fill="url(#shieldGrad)" />
  </g>

  <!-- Inner Shield Highlight -->
  <path d="M 256 86 
           C 318 86, 380 108, 394 122 
           C 394 246, 348 360, 256 418 
           C 164 360, 118 246, 118 122 
           C 132 108, 194 86, 256 86 Z" 
        fill="none" 
        stroke="#60A5FA" 
        stroke-width="8" 
        opacity="0.35" />

  <!-- Bold Crisp White Checkmark -->
  <path d="M 190 255 L 235 305 L 325 195" 
        fill="none" 
        stroke="#FFFFFF" 
        stroke-width="36" 
        stroke-linecap="round" 
        stroke-linejoin="round" />
</svg>'''

with open(os.path.join(PUBLIC_DIR, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(svg_content)

print("Generated favicon.svg")

# 2. Draw high resolution PIL icon and downsample with supersampling (anti-aliasing)
def generate_icon(size):
    # Render at 4x for clean supersampling
    scale = 4
    canvas_size = size * scale
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background
    corner_radius = int(canvas_size * 0.22)
    bg_color = (11, 19, 43, 255)  # Navy #0B132B
    draw.rounded_rectangle([0, 0, canvas_size - 1, canvas_size - 1], radius=corner_radius, fill=bg_color)

    # Shield points
    cx = canvas_size / 2
    top_y = canvas_size * 0.14
    bottom_y = canvas_size * 0.86
    left_x = canvas_size * 0.20
    right_x = canvas_size * 0.80

    shield_pts = []
    # Top edge
    steps = 40
    for i in range(steps + 1):
        t = i / steps
        x = left_x + t * (right_x - left_x)
        # Curved peak
        arch = math.sin(t * math.pi) * (canvas_size * 0.05)
        y = top_y - arch
        shield_pts.append((x, y))

    # Right side curving down to bottom tip
    for i in range(steps + 1):
        t = i / steps
        x = right_x - t * (right_x - cx) * 0.95
        y = top_y + t * (bottom_y - top_y)
        shield_pts.append((x, y))

    # Bottom tip back up left side
    for i in range(steps + 1):
        t = i / steps
        x = cx - t * (cx - left_x) * 0.95
        y = bottom_y - t * (bottom_y - top_y)
        shield_pts.append((x, y))

    shield_color = (37, 99, 235, 255)  # Primary #2563EB
    draw.polygon(shield_pts, fill=shield_color)

    # Inner highlight line
    draw.line([(left_x + canvas_size * 0.04, top_y + canvas_size * 0.03), (cx, top_y - canvas_size * 0.02), (right_x - canvas_size * 0.04, top_y + canvas_size * 0.03)], fill=(96, 165, 250, 180), width=int(canvas_size * 0.015))

    # Checkmark: (x1, y1) -> (x2, y2) -> (x3, y3)
    p1 = (cx - canvas_size * 0.13, canvas_size * 0.50)
    p2 = (cx - canvas_size * 0.04, canvas_size * 0.60)
    p3 = (cx + canvas_size * 0.14, canvas_size * 0.38)
    check_width = int(canvas_size * 0.075)

    draw.line([p1, p2, p3], fill=(255, 255, 255, 255), width=check_width, joint="round")
    # Draw rounded ends
    r = check_width // 2
    draw.ellipse([p1[0]-r, p1[1]-r, p1[0]+r, p1[1]+r], fill=(255, 255, 255, 255))
    draw.ellipse([p3[0]-r, p3[1]-r, p3[0]+r, p3[1]+r], fill=(255, 255, 255, 255))

    # Downsample
    return img.resize((size, size), Image.Resampling.LANCZOS)

# Generate icons
for sz in [16, 32, 64, 180, 192, 512]:
    icon = generate_icon(sz)
    if sz == 180:
        icon.save(os.path.join(PUBLIC_DIR, "apple-touch-icon.png"), "PNG")
    elif sz == 192:
        icon.save(os.path.join(PUBLIC_DIR, "pwa-192x192.png"), "PNG")
    elif sz == 512:
        icon.save(os.path.join(PUBLIC_DIR, "pwa-512x512.png"), "PNG")
    elif sz == 32:
        icon.save(os.path.join(PUBLIC_DIR, "favicon-32x32.png"), "PNG")
    elif sz == 16:
        icon.save(os.path.join(PUBLIC_DIR, "favicon-16x16.png"), "PNG")

# Generate favicon.ico (multi-size: 16, 32, 64)
ico_16 = generate_icon(16)
ico_32 = generate_icon(32)
ico_64 = generate_icon(64)
ico_16.save(os.path.join(PUBLIC_DIR, "favicon.ico"), format="ICO", sizes=[(16, 16), (32, 32), (64, 64)])
print("Generated PNG and ICO icons.")

# 3. Generate Social OG Image (1200x630)
og_img = Image.new("RGBA", (1200, 630), (5, 8, 15, 255)) # Dark navy #05080F
og_draw = ImageDraw.Draw(og_img)

# Background subtle card
og_draw.rounded_rectangle([60, 60, 1140, 570], radius=32, fill=(11, 19, 43, 255), outline=(37, 99, 235, 100), width=2)

# Paste large 256x256 shield icon
og_icon = generate_icon(220)
og_img.paste(og_icon, (120, 190), og_icon)

# Draw Title & Tagline text
og_draw.text((380, 210), "ScamLens", fill=(255, 255, 255, 255), font_size=72)
og_draw.text((380, 310), "AI Scam & Threat Detection", fill=(96, 165, 250, 255), font_size=36)
og_draw.text((380, 375), "Detect the scam. Understand the risk. Stay protected.", fill=(156, 163, 175, 255), font_size=24)

og_img.save(os.path.join(PUBLIC_DIR, "og-image.png"), "PNG")
print("Generated og-image.png (1200x630)")
