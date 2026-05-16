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
        inner_h = frame_height - 280
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

    # Transform and Paste
    frame_final = frame_layer.rotate(2, expand=True, resample=Image.BICUBIC)
    img.paste(frame_final, (100, 250), frame_final)
    
    # 4. Draw Floating Bubbles
    def draw_bubble(img_draw, x, y, icon_type, rotation=0):
        bubble_size = 180
        bubble_layer = Image.new('RGBA', (bubble_size + 40, bubble_size + 40), (0, 0, 0, 0))
        b_draw = ImageDraw.Draw(bubble_layer)
        b_draw.rounded_rectangle([15, 15, 15+bubble_size, 15+bubble_size], radius=40, fill=(0,0,0,30))
        b_draw.rounded_rectangle([10, 10, 10+bubble_size, 10+bubble_size], radius=40, fill=yellow)
        b_draw.polygon([(bubble_size//2 - 20, 10+bubble_size), (bubble_size//2 + 20, 10+bubble_size), (bubble_size//2, 10+bubble_size + 30)], fill=yellow)
        
        ic_center = (10 + bubble_size//2, 10 + bubble_size//2)
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
            b_draw.polygon([(ic_center[0]-15, ic_center[1]-15), (ic_center[0]+20, ic_center[1]), (ic_center[0]-15, ic_center[1]+15)], fill=red_accent)

        bubble_layer = bubble_layer.rotate(rotation, expand=True, resample=Image.BICUBIC)
        img.paste(bubble_layer, (x, y), bubble_layer)

    draw_bubble(img, 80, 200, 'robot', -10)
    draw_bubble(img, width-280, 180, 'iot', 10)
    draw_bubble(img, 120, height-500, 'ai', 5)
    draw_bubble(img, width-300, height-480, 'media', -8)

    # 5. UI Pills
    def draw_pill(img_draw, x, y, text_type, rotation=0):
        pill_w, pill_h = 320, 100
        pill_layer = Image.new('RGBA', (pill_w + 50, pill_h + 50), (0, 0, 0, 0))
        p_draw = ImageDraw.Draw(pill_layer)
        p_draw.rounded_rectangle([10, 10, 10+pill_w, 10+pill_h], radius=50, fill=(0,0,0,50))
        p_draw.rounded_rectangle([5, 5, 5+pill_w, 5+pill_h], radius=50, fill=maroon)
        p_draw.pieslice([5, 5, 5+pill_w, 5+pill_h*2], 180, 0, fill=(255,255,255,30))
        
        if text_type == 'stars':
            for i in range(4):
                star_x = 50 + i * 60
                p_draw.ellipse([star_x, 30, star_x+40, 70], fill=red_accent)
        elif text_type == 'chat':
            p_draw.ellipse([30, 30, 80, 70], outline=(255,255,255), width=3)
            p_draw.line([100, 40, 280, 40], fill=(255,255,255), width=4)

        pill_layer = pill_layer.rotate(rotation, expand=True, resample=Image.BICUBIC)
        img.paste(pill_layer, (x, y), pill_layer)

    draw_pill(img, -80, height // 2 + 100, 'stars', -10)
    draw_pill(img, width - 240, height // 2 - 300, 'chat', 5)

    # 6. Typography
    try:
        font_path = "C:\\Windows\\Fonts\\georgiab.ttf"
        if not os.path.exists(font_path): font_path = "arial.ttf"
        font = ImageFont.truetype(font_path, 80)
    except:
        font = ImageFont.load_default()

    hashtag = "#bootcamp2026"
    text_bbox = draw.textbbox((0, 0), hashtag, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_x = width // 2 - text_w // 2
    text_y = 1530 
    
    txt_layer = Image.new('RGBA', (width, height), (0,0,0,0))
    t_draw = ImageDraw.Draw(txt_layer)
    t_draw.text((text_x, text_y), hashtag, fill=maroon, font=font)
    txt_layer = txt_layer.rotate(2, expand=False, resample=Image.BICUBIC)
    img.paste(txt_layer, (0, 0), txt_layer)

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
