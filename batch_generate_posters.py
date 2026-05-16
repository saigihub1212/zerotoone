import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def find_coeffs(pa, pb):
    import numpy as np
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

    A = np.matrix(matrix, dtype=float)
    B = np.array(pb).reshape(8)

    res = np.linalg.solve(A, B)
    return np.array(res).reshape(8)

def generate_single_poster(image_path, output_filename):
    # Dimensions for Instagram Story (9:16)
    width, height = 1080, 1920
    
    # Colors
    bg_color = (253, 248, 225)
    yellow = (255, 212, 0)
    maroon = (74, 14, 14)
    red_accent = (244, 67, 54)
    grid_color = (74, 14, 14, 15) # Very transparent maroon
    
    # Create base image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # 1. Draw Grid
    grid_spacing = 60
    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=2)
    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill=grid_color, width=2)
        
    # 2. Draw Corner Dots
    def draw_dots(draw, x_start, y_start, rows, cols, spacing=25):
        for r in range(rows):
            for c in range(cols):
                x = x_start + c * spacing
                y = y_start + r * spacing
                draw.ellipse([x-3, y-3, x+3, y+3], fill=(74, 14, 14, 50))

    draw_dots(draw, 50, 50, 6, 6)
    draw_dots(draw, width-200, 50, 6, 6)
    draw_dots(draw, 50, height-200, 6, 6)
    draw_dots(draw, width-200, height-200, 6, 6)
    
    # 3. Draw Main Frame with Perspective
    frame_width, frame_height = 850, 1400
    frame_layer = Image.new('RGBA', (frame_width + 200, frame_height + 200), (0, 0, 0, 0))
    f_draw = ImageDraw.Draw(frame_layer)
    
    # --- Insert user image ---
    if os.path.exists(image_path):
        inner_w = frame_width - 80
        inner_h = frame_height - 240
        user_img = Image.open(image_path).convert("RGBA")
        
        img_aspect = user_img.width / user_img.height
        frame_aspect = inner_w / inner_h
        
        if img_aspect > frame_aspect:
            new_w = int(inner_h * img_aspect)
            user_img = user_img.resize((new_w, inner_h), Image.LANCZOS)
            left = (new_w - inner_w) // 2
            user_img = user_img.crop((left, 0, left + inner_w, inner_h))
        else:
            new_h = int(inner_w / img_aspect)
            user_img = user_img.resize((inner_w, new_h), Image.LANCZOS)
            top = (new_h - inner_h) // 2
            user_img = user_img.crop((0, top, inner_w, top + inner_h))
            
        mask = Image.new('L', (inner_w, inner_h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, inner_w, inner_h], radius=40, fill=255)
        
        frame_layer.paste(user_img, (90, 90), mask)
    
    # Draw yellow border
    border_thickness = 40
    f_draw.rounded_rectangle(
        [50, 50, 50 + frame_width, 50 + frame_height], 
        radius=80, outline=yellow, width=border_thickness
    )
    
    # Draw yellow bottom bar
    f_draw.rounded_rectangle(
        [50, 50 + frame_height - 200, 50 + frame_width, 50 + frame_height],
        radius=80, fill=yellow
    )
    f_draw.rectangle([50, 50 + frame_height - 200, 50 + frame_width, 50 + frame_height - 150], fill=yellow)

    # 6. Typography (Draw on frame before rotation)
    try:
        font_path = "C:\\Windows\\Fonts\\georgiab.ttf"
        if not os.path.exists(font_path): font_path = "arial.ttf"
        font = ImageFont.truetype(font_path, 60)
    except:
        font = ImageFont.load_default()

    hashtag = "#bootcamp2026"
    try:
        text_bbox = f_draw.textbbox((0, 0), hashtag, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        text_y_offset = text_bbox[1]
    except AttributeError:
        text_w = font.getlength(hashtag) if hasattr(font, 'getlength') else len(hashtag) * 35
        text_h = 60
        text_y_offset = 0

    text_x = 50 + frame_width // 2 - text_w // 2
    text_y = 50 + frame_height - 100 - text_h // 2 - text_y_offset
    f_draw.text((text_x, text_y), hashtag, fill=maroon, font=font)

    # Transform and Paste
    frame_final = frame_layer.rotate(2, expand=True, resample=Image.BICUBIC)
    img.paste(frame_final, (100, 250), frame_final)
    
    # 4. Draw Floating Bubbles
    def draw_bubble(img_draw, x, y, icon_type, rotation=0, tail_pos='bottom_right'):
        bubble_size = 180
        bubble_layer = Image.new('RGBA', (bubble_size + 80, bubble_size + 80), (0, 0, 0, 0))
        b_draw = ImageDraw.Draw(bubble_layer)
        
        # padding is 40
        b_draw.rounded_rectangle([45, 45, 45+bubble_size, 45+bubble_size], radius=40, fill=(0,0,0,30))
        b_draw.rounded_rectangle([40, 40, 40+bubble_size, 40+bubble_size], radius=40, fill=yellow)
        
        # tails
        if tail_pos == 'bottom_right':
            b_draw.polygon([(40+bubble_size - 60, 40+bubble_size), (40+bubble_size - 20, 40+bubble_size), (40+bubble_size - 20, 40+bubble_size + 30)], fill=yellow)
        elif tail_pos == 'bottom_left':
            b_draw.polygon([(40 + 20, 40+bubble_size), (40 + 60, 40+bubble_size), (40 + 20, 40+bubble_size + 30)], fill=yellow)
        elif tail_pos == 'top_right':
            b_draw.polygon([(40+bubble_size - 60, 40), (40+bubble_size - 20, 40), (40+bubble_size - 20, 40 - 30)], fill=yellow)
        elif tail_pos == 'top_left':
            b_draw.polygon([(40 + 20, 40), (40 + 60, 40), (40 + 20, 40 - 30)], fill=yellow)
            
        ic_center = (40 + bubble_size//2, 40 + bubble_size//2)
        if icon_type == 'robot':
            b_draw.rectangle([ic_center[0]-30, ic_center[1]-20, ic_center[0]+30, ic_center[1]+30], fill=maroon)
            b_draw.rectangle([ic_center[0]-20, ic_center[1]-45, ic_center[0]+20, ic_center[1]-25], fill=maroon)
            b_draw.ellipse([ic_center[0]-15, ic_center[1]-40, ic_center[0]-5, ic_center[1]-30], fill=red_accent)
            b_draw.ellipse([ic_center[0]+5, ic_center[1]-40, ic_center[0]+15, ic_center[1]-30], fill=red_accent)
        elif icon_type == 'iot':
            b_draw.rectangle([ic_center[0]-35, ic_center[1]-35, ic_center[0]+35, ic_center[1]+35], outline=maroon, width=6)
            b_draw.rectangle([ic_center[0]-15, ic_center[1]-15, ic_center[0]+15, ic_center[1]+15], fill=red_accent)
        elif icon_type == 'ai':
            b_draw.ellipse([ic_center[0]-40, ic_center[1]-40, ic_center[0]+40, ic_center[1]+40], fill=maroon)
            b_draw.line([ic_center[0]-20, ic_center[1], ic_center[0]+20, ic_center[1]], fill=red_accent, width=4)
        elif icon_type == 'media':
            b_draw.rounded_rectangle([ic_center[0]-45, ic_center[1]-30, ic_center[0]+45, ic_center[1]+30], radius=15, fill=maroon)
            b_draw.polygon([(ic_center[0]-15, ic_center[1]-15), (ic_center[0]+20, ic_center[1]), (ic_center[0]-15, ic_center[1]+15)], fill=yellow, outline=red_accent)

        bubble_layer = bubble_layer.rotate(rotation, expand=True, resample=Image.BICUBIC)
        img.paste(bubble_layer, (x, y), bubble_layer)

    draw_bubble(img, 20, 100, 'robot', -10, 'bottom_right')
    draw_bubble(img, width-260, 100, 'iot', 10, 'bottom_left')
    draw_bubble(img, 20, height-380, 'ai', 5, 'top_right')
    draw_bubble(img, width-260, height-380, 'media', -8, 'top_left')

    # 5. UI Pills
    def draw_pill(img_draw, x, y, text_type, rotation=0):
        pill_w, pill_h = 320, 100
        pill_layer = Image.new('RGBA', (pill_w + 50, pill_h + 50), (0, 0, 0, 0))
        p_draw = ImageDraw.Draw(pill_layer)
        p_draw.rounded_rectangle([10, 10, 10+pill_w, 10+pill_h], radius=50, fill=(0,0,0,50))
        p_draw.rounded_rectangle([5, 5, 5+pill_w, 5+pill_h], radius=50, fill=maroon)
        
        if text_type == 'stars':
            import math
            for i in range(4):
                star_x = 50 + i * 60
                star_center_x = star_x + 20
                star_center_y = 50
                pts = []
                for j in range(10):
                    angle = j * math.pi / 5 - math.pi / 2
                    r = 20 if j % 2 == 0 else 8
                    pts.append((star_center_x + r * math.cos(angle), star_center_y + r * math.sin(angle)))
                p_draw.polygon(pts, fill=red_accent)
        elif text_type == 'chat':
            # Chat bubble icon with a tail
            p_draw.ellipse([30, 30, 80, 70], outline=(255,255,255), width=3)
            p_draw.line([(45, 65), (35, 80), (55, 65)], fill=(255,255,255), width=3)
            # Three red horizontal lines
            p_draw.line([100, 35, 280, 35], fill=red_accent, width=4)
            p_draw.line([100, 50, 280, 50], fill=red_accent, width=4)
            p_draw.line([100, 65, 280, 65], fill=red_accent, width=4)

        pill_layer = pill_layer.rotate(rotation, expand=True, resample=Image.BICUBIC)
        img.paste(pill_layer, (x, y), pill_layer)

    draw_pill(img, -80, height // 2 + 100, 'stars', -10)
    draw_pill(img, width - 240, height // 2 - 300, 'chat', 5)



    img.save(output_filename)
    print(f"Poster saved as {output_filename}")

if __name__ == "__main__":
    input_images = ['image1.png', 'image2.png', 'image3.png']
    for i, img_path in enumerate(input_images):
        out_name = f'bootcamp_poster_{i+1}.png'
        if os.path.exists(img_path):
            generate_single_poster(img_path, out_name)
        else:
            print(f"Skipping {img_path}: File not found.")
