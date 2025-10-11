import os
import random
import re
import json
import sys
from datetime import datetime, timedelta
from faker import Faker
from PIL import Image, ImageDraw, ImageFont
import pydenticon
import hashlib
from io import BytesIO

# --- CONFIGURATION ---
NUMBER_OF_IMAGES = 100
OUTPUT_FOLDER = "out/01_passports_realistic"
RESOURCES_FOLDER = "./resources/"
# --- START: MODIFIED SECTION ---
# Enter the filename of your chosen 1000x600 background image here
BACKGROUND_IMAGE_FILE = "passport_background_blue.png" 
# --- END: MODIFIED SECTION ---


# --- DATA FOR REALISM ---
PASSPORT_FORMATS = {
    'USA': 'NNNNNNNNN',
    'CAN': 'LLNNNNNN',
    'DEU': 'LLNNNNLNN',
    'GBR': 'NNNNNNNNN',
    'AUS': 'LNNNNNNN'
}

# --- HELPER FUNCTIONS for MRZ ---
# (No changes in this section)
def calculate_checksum(s):
    s = s.upper()
    weights = [7, 3, 1]
    total = 0
    char_map = {str(i): i for i in range(10)}
    char_map.update({chr(ord('A') + i): 10 + i for i in range(26)})
    
    for i, char in enumerate(s):
        if char == '<':
            val = 0
        else:
            val = char_map.get(char, 0)
        total += val * weights[i % 3]
    return str(total % 10)

def format_for_mrz(text, length):
    return text.upper().replace(' ', '<').ljust(length, '<')

def generate_passport_number(country_code):
    fmt = PASSPORT_FORMATS.get(country_code, 'LNNNNNNNN')
    num = []
    for char_code in fmt:
        if char_code == 'L':
            num.append(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        elif char_code == 'N':
            num.append(str(random.randint(0, 9)))
    return "".join(num)

def generate_mrz(data):
    line1 = "P<" + data['nationality']
    surname_mrz = data['surname'].upper().replace(' ', '<')
    given_names_mrz = data['given_names'].upper().replace(' ', '<')
    full_name_mrz = f"{surname_mrz}<<{given_names_mrz}"
    line1 += format_for_mrz(full_name_mrz, 39)
    
    passport_num_padded = format_for_mrz(data['passport_number'], 9)
    passport_checksum = calculate_checksum(passport_num_padded)
    dob_str = data['date_of_birth'].strftime('%y%m%d')
    dob_checksum = calculate_checksum(dob_str)
    expiry_str = data['date_of_expiry'].strftime('%y%m%d')
    expiry_checksum = calculate_checksum(expiry_str)
    personal_num_padded = format_for_mrz('', 14)
    personal_num_checksum = calculate_checksum(personal_num_padded)
    composite_check_str = f"{passport_num_padded}{passport_checksum}{dob_str}{dob_checksum}{expiry_str}{expiry_checksum}{personal_num_padded}{personal_num_checksum}"
    final_checksum = calculate_checksum(composite_check_str)
    line2 = f"{passport_num_padded}{passport_checksum}{data['nationality']}{dob_str}{dob_checksum}{data['sex']}{expiry_str}{expiry_checksum}{personal_num_padded}{personal_num_checksum}{final_checksum}"
    
    return line1, line2

# --- IMAGE GENERATION ---
def create_passport_image(data, avatar_image, file_path, font_paths, background_path): # <-- background_path added
    width, height = 1000, 600
    base_bg_color = (240, 245, 250) # A plain color for the base
    font_color = (10, 10, 10)
    label_color = (100, 100, 100)
    
    # --- START: BACKGROUND LOADING MODIFIED ---
    # Create a plain base background
    plain_background = Image.new('RGB', (width, height), base_bg_color)
    
    try:
        # Load the complex background image
        complex_background = Image.open(background_path).convert('RGB')
        if complex_background.size != (width, height):
            complex_background = complex_background.resize((width, height), Image.LANCZOS)
        
        # Blend the plain base with the complex background.
        # alpha=0.6 means 60% of the complex_background and 40% of the plain_background.
        image = Image.blend(plain_background, complex_background, alpha=0.6)

    except FileNotFoundError:
        print(f"WARNING: Background file not found at '{background_path}'. Using plain background.")
        image = plain_background # Fallback to the plain background if file is missing
    # --- END: BACKGROUND LOADING MODIFIED ---

    draw = ImageDraw.Draw(image)
    
    # Load fonts
    font_bold = ImageFont.truetype(font_paths['arial_bold'], 26)
    font_regular = ImageFont.truetype(font_paths['arial_regular'], 22)
    font_label = ImageFont.truetype(font_paths['arial_regular'], 16)
    font_mrz = ImageFont.truetype(font_paths['ocr_b'], 36)
    watermark_font = ImageFont.truetype(font_paths['arial_regular'], 150)

    # Draw all text and other elements onto the blended background
    draw.text((250, 30), "REPUBLIC OF HACKATHON", fill=label_color, font=font_bold)
    draw.text((250, 65), "PASSPORT / PASSEPORT", fill=label_color, font=font_regular)
    
    draw.rectangle([30, 30, 210, 210], outline=label_color, width=2)
    image.paste(avatar_image, (40, 40))

    # Watermark layer
    watermark = Image.new("RGBA", image.size)
    watermark_draw = ImageDraw.Draw(watermark)
    watermark_draw.text((width/2, height/2), "SPECIMEN", font=watermark_font, fill=(255, 0, 0, 80), anchor="ms")
    image.paste(watermark, (0, 0), watermark)

    # Adjust these coordinates as needed to fit your background image
    fields = [
        (250, 120, "1. Surname / Nom", data['surname']),
        (650, 120, "2. Given Names / Prénoms", data['given_names']),
        (250, 200, "3. Nationality / Nationalité", data['nationality_long']),
        (650, 200, "4. Date of Birth", data['date_of_birth'].strftime('%d %b %Y').upper()),
        (250, 280, "5. Sex / Sexe", data['sex']),
        (450, 280, "6. Date of Issue", data['date_of_issue'].strftime('%d %b %Y').upper()),
        (750, 280, "7. Date of Expiry", data['date_of_expiry'].strftime('%d %b %Y').upper()),
        (250, 360, "8. Passport No.", data['passport_number']),
    ]
    for x, y, label, value in fields:
        draw.text((x, y), label, fill=label_color, font=font_label)
        draw.text((x, y + 25), value, fill=font_color, font=font_regular)

    draw.text((30, 500), data['mrz_line1'], fill=font_color, font=font_mrz)
    draw.text((30, 550), data['mrz_line2'], fill=font_color, font=font_mrz)
    
    image.save(file_path)

# --- MAIN SCRIPT ---
if __name__ == "__main__":
    font_paths = {
        'ocr_b': os.path.join(RESOURCES_FOLDER, "OCR-B.ttf"),
        'arial_regular': os.path.join(RESOURCES_FOLDER, "arial.ttf"),
        'arial_bold': os.path.join(RESOURCES_FOLDER, "arialbd.ttf")
    }

    missing_fonts = [name for name, path in font_paths.items() if not os.path.exists(path)]
    if missing_fonts:
        print(f"ERROR: Missing required font files in '{RESOURCES_FOLDER}' directory.")
        for name in missing_fonts:
            print(f" - File not found: {os.path.basename(font_paths[name])}")
        print("\nPlease ensure these fonts are in the resources folder before running.")
        sys.exit(1)

    background_image_path = os.path.join(RESOURCES_FOLDER, BACKGROUND_IMAGE_FILE) # <-- Path for background

    fake = Faker()
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(RESOURCES_FOLDER, exist_ok=True)
        
    avatar_generator = pydenticon.Generator(8, 8, digest=hashlib.sha256)
    
    all_groundtruth_data = {}

    for i in range(NUMBER_OF_IMAGES):
        nat_code = random.choice(list(PASSPORT_FORMATS.keys()))
        country_name = fake.country()
        sex = random.choice(['M', 'F'])
        first_name = fake.first_name_male() if sex == 'M' else fake.first_name_female()
        last_name = fake.last_name()
        
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)
        issue_date = fake.date_between(start_date=birth_date + timedelta(days=18*365), end_date=datetime.now())
        expiry_date = issue_date + timedelta(days=10*365 - random.randint(1,30))

        passport_data = {
            'passport_number': generate_passport_number(nat_code),
            'surname': last_name.upper(),
            'given_names': first_name.upper(),
            'nationality': nat_code,
            'nationality_long': country_name.upper(),
            'sex': sex,
            'date_of_birth': birth_date,
            'date_of_issue': issue_date,
            'date_of_expiry': expiry_date,
        }
        
        mrz1, mrz2 = generate_mrz(passport_data)
        passport_data['mrz_line1'] = mrz1
        passport_data['mrz_line2'] = mrz2

        avatar_seed = f"{passport_data['passport_number']}-{passport_data['surname']}"
        avatar_image_bytes = avatar_generator.generate(avatar_seed, 170, 170, output_format="png")
        avatar_image_pil = Image.open(BytesIO(avatar_image_bytes))

        file_name = f"passport_{passport_data['passport_number']}.png"
        file_path = os.path.join(OUTPUT_FOLDER, file_name)
        
        # Pass the background image path to the function
        create_passport_image(passport_data, avatar_image_pil, file_path, font_paths, background_image_path)

        groundtruth_entry = {
            'passport_number': passport_data['passport_number'],
            'surname': passport_data['surname'],
            'given_names': passport_data['given_names'],
            'nationality_code': passport_data['nationality'],
            'nationality_long': passport_data['nationality_long'],
            'sex': passport_data['sex'],
            'date_of_birth': passport_data['date_of_birth'].isoformat(),
            'date_of_issue': passport_data['date_of_issue'].isoformat(),
            'date_of_expiry': passport_data['date_of_expiry'].isoformat(),
            'mrz_line1': passport_data['mrz_line1'],
            'mrz_line2': passport_data['mrz_line2']
        }
        all_groundtruth_data[file_name] = groundtruth_entry
        
        print(f"({i+1}/{NUMBER_OF_IMAGES}) Generated realistic passport image: {file_name}")

    groundtruth_filepath = os.path.join(OUTPUT_FOLDER, "groundtruth.json")
    with open(groundtruth_filepath, "w") as f:
        json.dump(all_groundtruth_data, f, indent=4)

    print(f"\nGeneration complete in folder '{OUTPUT_FOLDER}'")
    print(f"Ground truth data saved to '{groundtruth_filepath}'")