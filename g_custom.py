import os
import random
import json
from datetime import datetime, timedelta
from faker import Faker
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- CONFIGURATION ---
NUMBER_OF_FORMS = 100
OUTPUT_FOLDER = "out/05_customs_forms_en"
RESOURCES_FOLDER = "./resources/"

# Register Fonts
try:
    pdfmetrics.registerFont(TTFont('Kanit', os.path.join(RESOURCES_FOLDER, 'Kanit-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Kanit-Bold', os.path.join(RESOURCES_FOLDER, 'Kanit-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('Kanit-Italic', os.path.join(RESOURCES_FOLDER, 'Kanit-Italic.ttf')))
    pdfmetrics.registerFont(TTFont('Kanit-BoldItalic', os.path.join(RESOURCES_FOLDER, 'Kanit-BoldItalic.ttf')))
except Exception as e:
    print(f"ERROR: Could not register fonts. Make sure font files are in '{RESOURCES_FOLDER}'")
    print(e)
    exit()

# --- DATA POOLS ---
fake = Faker("en_US")

PERSONS_POOL = [
    {"title": "Mr.", "fname": "Somsak", "lname": "Charoensuk", "dob": "1985-05-15", "occupation": "Engineer", "nationality": "Thai"},
    {"title": "Ms.", "fname": "Ariya", "lname": "Wongrat", "dob": "1992-11-20", "occupation": "Marketing Manager", "nationality": "Thai"},
    {"title": "Mr.", "fname": "Natthapong", "lname": "Saetang", "dob": "1978-02-10", "occupation": "Business Owner", "nationality": "Thai"},
    {"title": "Mrs.", "fname": "Pornthip", "lname": "Kittisiriprasert", "dob": "1980-09-03", "occupation": "Accountant", "nationality": "Thai"},
    {"title": "Mr.", "fname": "Anucha", "lname": "Phakdeesettakun", "dob": "1995-07-22", "occupation": "Software Developer", "nationality": "Thai"},
    {"title": "Ms.", "fname": "Kamonwan", "lname": "Suphantharida", "dob": "2000-01-30", "occupation": "Student", "nationality": "Thai"},
    {"title": "Mr.", "fname": "Weerasak", "lname": "Chaiyaporn", "dob": "1969-12-01", "occupation": "Government Officer", "nationality": "Thai"},
    {"title": "Ms.", "fname": "Thanyarat", "lname": "Lertlum", "dob": "1988-04-18", "occupation": "Graphic Designer", "nationality": "Thai"},
    {"title": "Mr.", "fname": "Chatchai", "lname": "Siripattana", "dob": "1991-08-08", "occupation": "Doctor", "nationality": "Thai"},
    {"title": "Mrs.", "fname": "Sunisa", "lname": "Asavanonda", "dob": "1983-06-25", "occupation": "Teacher", "nationality": "Thai"},
    {"title": "Mr.", "fname": "John", "lname": "Smith", "dob": "1982-03-12", "occupation": "Tourist", "nationality": "American"},
    {"title": "Ms.", "fname": "Emily", "lname": "Jones", "dob": "1990-10-05", "occupation": "Expat", "nationality": "British"},
    {"title": "Mr.", "fname": "Michael", "lname": "Chen", "dob": "1988-07-14", "occupation": "Investor", "nationality": "Singaporean"},
    {"title": "Ms.", "fname": "Yuki", "lname": "Tanaka", "dob": "1995-01-22", "occupation": "Researcher", "nationality": "Japanese"},
    {"title": "Mr.", "fname": "Peter", "lname": "Schmidt", "dob": "1975-11-30", "occupation": "Manager", "nationality": "German"},
    {"title": "Mrs.", "fname": "Isabelle", "lname": "Dubois", "dob": "1980-09-17", "occupation": "Diplomat", "nationality": "French"},
    {"title": "Mr.", "fname": "Boonliang", "lname": "Sae-lim", "dob": "1979-05-21", "occupation": "Tour Guide", "nationality": "Thai"},
    {"title": "Ms.", "fname": "Siriporn", "lname": "Ratanakorn", "dob": "1998-02-14", "occupation": "Flight Attendant", "nationality": "Thai"},
    {"title": "Mr.", "fname": "Prakit", "lname": "Jiradej", "dob": "1986-10-09", "occupation": "Architect", "nationality": "Thai"},
    {"title": "Ms.", "fname": "Waranya", "lname": "Techaphaiboon", "dob": "1993-03-29", "occupation": "Lawyer", "nationality": "Thai"},
]

AIRLINES = ["TG", "EK", "QR", "SQ", "CX", "JL", "KE", "WE", "FD", "XJ"]
CITIES = ["London", "Paris", "Tokyo", "Dubai", "Singapore", "Hong Kong", "Seoul", "Frankfurt", "Sydney", "Doha"]
DECLARED_GOODS = [
    {"item": "Rolex Watch", "value_min": 150000, "value_max": 500000},
    {"item": "Louis Vuitton Bag", "value_min": 80000, "value_max": 250000},
    {"item": "Wine (6 bottles)", "value_min": 15000, "value_max": 40000},
    {"item": "Cigars (250g box)", "value_min": 10000, "value_max": 25000},
    {"item": "iPhone 15 Pro Max", "value_min": 50000, "value_max": 65000},
]

# --- HELPER FUNCTIONS ---
def get_english_date(dt):
    """Formats a datetime object into a standard English date string."""
    return dt.strftime("%B %d, %Y")

def draw_checkbox(c, x, y, size=0.4*cm, checked=False):
    c.saveState()
    c.setLineWidth(1)
    c.rect(x, y, size, size)
    if checked:
        c.setFont('Helvetica', size * 1.2)
        c.drawString(x + size*0.1, y - size*0.05, "X")
    c.restoreState()

def draw_header(c, title, subtitle):
    c.drawImage(os.path.join(RESOURCES_FOLDER, "garuda.png"), 9.75 * cm, 26.5 * cm, width=2.5*cm, height=2.5*cm, preserveAspectRatio=True, mask='auto')
    c.setFont('Kanit-Bold', 16)
    c.drawCentredString(10.5 * cm, 26 * cm, "PASSENGER DECLARATION FORM")
    c.setFont('Kanit', 11)
    c.drawCentredString(10.5 * cm, 25.2 * cm, title)
    c.drawCentredString(10.5 * cm, 24.8 * cm, subtitle)

# --- TEMPLATE 1: Classic Official ---
def create_template_1(c, data):
    draw_header(c, "The Customs Department", "Ministry of Finance, Kingdom of Thailand")
    
    y = 24 * cm
    c.setFont('Kanit-Bold', 11)
    c.drawString(2 * cm, y, "Part 1: Passenger Information")
    
    # Draw content
    c.setFont('Kanit', 10)
    y -= 1 * cm
    c.drawString(2.5 * cm, y, f"Full Name: {data['person']['title']} {data['person']['fname']} {data['person']['lname']}")
    c.drawString(11 * cm, y, f"Date of Birth: {data['dob_str']}")
    y -= 0.8 * cm
    c.drawString(2.5 * cm, y, f"Occupation: {data['person']['occupation']}")
    c.drawString(11 * cm, y, f"Nationality: {data['person']['nationality']}")
    y -= 0.8 * cm
    c.drawString(2.5 * cm, y, f"Passport Number: {data['passport_no']}")
    c.drawString(11 * cm, y, f"Accompanying family members: {data['family_members']}")
    y -= 0.8 * cm
    c.drawString(2.5 * cm, y, f"Arriving Flight No.: {data['flight_no']}")
    c.drawString(11 * cm, y, f"From (City): {data['origin_city']}")

    # Declaration Part
    y -= 1.5 * cm
    c.setStrokeColor(colors.black)
    c.rect(1.5*cm, y - 9.5*cm, 18*cm, 10.5*cm) # Main box
    
    c.setFont('Kanit-Bold', 11)
    c.drawString(2 * cm, y, "Part 2: Declaration")
    
    c.setFont('Kanit', 10)
    y -= 1 * cm
    draw_checkbox(c, 2.5 * cm, y, checked=data['declare_goods'])
    c.drawString(3.5 * cm, y + 0.1*cm, "1. I have articles to declare (taxable, restricted, or prohibited items).")
    
    y -= 1 * cm
    draw_checkbox(c, 2.5 * cm, y, checked=data['declare_currency'])
    c.drawString(3.5 * cm, y + 0.1*cm, "2. I have foreign currency exceeding USD 20,000 or its equivalent.")

    y -= 1 * cm
    draw_checkbox(c, 2.5 * cm, y, checked=not (data['declare_goods'] or data['declare_currency']))
    c.drawString(3.5 * cm, y + 0.1*cm, "3. I have nothing to declare.")
    
    y -= 1.2 * cm
    c.setFont('Kanit-Bold', 10)
    c.drawString(2.5 * cm, y, "Details of declared items:")
    c.setFont('Kanit', 10)
    
    y -= 0.8 * cm
    c.line(2.5*cm, y, 18.5*cm, y)
    c.drawString(3 * cm, y - 0.5*cm, "Description")
    c.drawString(12 * cm, y - 0.5*cm, "Quantity")
    c.drawString(16 * cm, y - 0.5*cm, "Value (THB)")
    y -= 0.8 * cm
    c.line(2.5*cm, y, 18.5*cm, y)
    
    if data['declared_items']:
        for item in data['declared_items']:
            y -= 0.6 * cm
            c.drawString(3 * cm, y, item['item'])
            c.drawRightString(13.5*cm, y, str(item['quantity']))
            c.drawRightString(18*cm, y, f"{item['value']:,.2f}")
    
    # Signature
    y = 5 * cm
    c.drawString(12*cm, y, "Passenger Signature ......................................")
    c.drawString(13*cm, y-0.6*cm, f"({data['person']['title']} {data['person']['fname']} {data['person']['lname']})")
    c.drawString(13*cm, y-1.2*cm, f"Date: {data['arrival_date_str']}")


# --- TEMPLATE 2: Modern Color-Coded ---
def create_template_2(c, data):
    c.setFillColor(colors.HexColor('#ffffff')) # Dark Blue
    c.rect(0, 25*cm, 21*cm, 4.7*cm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    
    c.drawImage(os.path.join(RESOURCES_FOLDER, "garuda.png"), 2 * cm, 26.5 * cm, width=2*cm, height=2*cm, preserveAspectRatio=True, mask='auto')
    c.setFont('Kanit-Bold', 18)
    c.drawString(4.5*cm, 27.5*cm, "Customs Declaration")
    c.setFont('Kanit', 14)
    c.drawString(4.5*cm, 26.7*cm, "Kingdom of Thailand")
    
    c.setFont('Kanit', 10)
    c.drawRightString(19.5*cm, 28*cm, f"Flight No: {data['flight_no']}")
    c.drawRightString(19.5*cm, 27.5*cm, f"Date: {data['arrival_date_str']}")
    c.drawRightString(19.5*cm, 27*cm, f"Passport: {data['passport_no']}")

    c.setFillColor(colors.black)
    y = 24 * cm
    
    # Passenger Info
    c.setFont('Kanit-Bold', 12)
    c.drawString(2 * cm, y, "Passenger Information")
    c.line(2*cm, y-0.2*cm, 19.5*cm, y-0.2*cm)
    y -= 1 * cm
    c.setFont('Kanit', 10)
    c.drawString(2.5 * cm, y, f"Full Name: {data['person']['title']} {data['person']['fname']} {data['person']['lname']}")
    c.drawString(12 * cm, y, f"Nationality: {data['person']['nationality']}")
    y -= 0.8 * cm
    c.drawString(2.5 * cm, y, f"Date of Birth: {data['dob_str']}")
    c.drawString(12 * cm, y, f"Occupation: {data['person']['occupation']}")
    y -= 0.8 * cm
    c.drawString(2.5 * cm, y, f"From (City): {data['origin_city']}")
    c.drawString(12 * cm, y, f"Family Members: {data['family_members']}")

    # Declaration Part
    y -= 1.5 * cm
    c.setFillColor(colors.HexColor('#e8eaf6')) # Light blue
    c.rect(1.5*cm, y - 10*cm, 18*cm, 11*cm, stroke=0, fill=1)
    c.setFillColor(colors.black)
    c.setFont('Kanit-Bold', 12)
    c.drawString(2 * cm, y, "Declaration of Goods")
    c.line(2*cm, y-0.2*cm, 19.5*cm, y-0.2*cm)
    
    c.setFont('Kanit', 10)
    y -= 1 * cm
    draw_checkbox(c, 2.5*cm, y, checked=data['declare_goods'] or data['declare_currency'])
    c.drawString(3.5*cm, y+0.1*cm, "I am carrying goods which are taxable, restricted, or in excess of the allowance.")
    y -= 1*cm
    draw_checkbox(c, 2.5*cm, y, checked=not (data['declare_goods'] or data['declare_currency']))
    c.drawString(3.5*cm, y+0.1*cm, "I have NOTHING TO DECLARE.")

    y -= 1.2 * cm
    c.setFont('Kanit-BoldItalic', 10)
    c.drawString(2.5 * cm, y, "If checked the first box, please provide details below:")
    
    y -= 0.8 * cm
    c.setFillColor(colors.white)
    c.rect(2.5*cm, y - 4*cm, 16*cm, 4*cm, stroke=1, fill=1)
    c.setFillColor(colors.black)
    
    if data['declared_items']:
        y_item = y - 0.6*cm
        for item in data['declared_items']:
            c.drawString(3*cm, y_item, f"- {item['item']} (Value: {item['value']:,.2f} THB)")
            y_item -= 0.7*cm
    
    # Signature
    y = 5 * cm
    c.drawString(12*cm, y, "Signature: .................................................")
    c.drawString(13*cm, y-0.6*cm, f"{data['person']['title']} {data['person']['fname']} {data['person']['lname']}")

# --- TEMPLATE 3: Minimalist Compact ---
def create_template_3(c, data):
    c.setFont('Kanit-Bold', 10)
    c.drawCentredString(10.5*cm, 28*cm, "KINGDOM OF THAILAND - THE CUSTOMS DEPARTMENT")
    c.setFont('Kanit-Bold', 16)
    c.drawCentredString(10.5*cm, 27*cm, "PASSENGER DECLARATION")
    c.line(1.5*cm, 26.5*cm, 19.5*cm, 26.5*cm)

    # Two-column layout
    y=25.5*cm
    c.setFont('Kanit-Bold', 9)
    # Left Column
    c.drawString(2*cm, y, "Family Name:")
    c.drawString(2*cm, y-1*cm, "First Name:")
    c.drawString(2*cm, y-2*cm, "Passport No.:")
    c.drawString(2*cm, y-3*cm, "Arrival Flight No.:")
    
    # Right Column
    c.drawString(11*cm, y, "Date of Birth (D/M/Y):")
    c.drawString(11*cm, y-1*cm, "Nationality:")
    c.drawString(11*cm, y-2*cm, "Occupation:")
    c.drawString(11*cm, y-3*cm, "Origin City:")

    # Data
    c.setFont('Kanit', 10)
    c.drawString(4.5*cm, y, data['person']['lname'])
    c.drawString(4.5*cm, y-1*cm, data['person']['fname'])
    c.drawString(4.5*cm, y-2*cm, data['passport_no'])
    c.drawString(4.5*cm, y-3*cm, data['flight_no'])
    
    c.drawString(14.5*cm, y, datetime.strptime(data['person']['dob'], '%Y-%m-%d').strftime('%d/%m/%Y'))
    c.drawString(14.5*cm, y-1*cm, data['person']['nationality'])
    c.drawString(14.5*cm, y-2*cm, data['person']['occupation'])
    c.drawString(14.5*cm, y-3*cm, data['origin_city'])

    y -= 4 * cm
    c.line(1.5*cm, y, 19.5*cm, y)
    
    y -= 0.8*cm
    c.setFont('Kanit-Bold', 11)
    c.drawString(2*cm, y, "Please check (X) the appropriate box.")
    
    c.setFont('Kanit', 10)
    y -= 1.2*cm
    draw_checkbox(c, 2.5*cm, y, checked=data['declare_goods'] or data['declare_currency'])
    c.drawString(3.5*cm, y+0.1*cm, "I have goods to declare (items exceeding allowances, restricted or prohibited items).")
    
    y -= 1.2*cm
    draw_checkbox(c, 2.5*cm, y, checked=not (data['declare_goods'] or data['declare_currency']))
    c.drawString(3.5*cm, y+0.1*cm, "I have NOTHING TO DECLARE (no taxable or restricted goods).")
    
    y -= 1 * cm
    c.line(1.5*cm, y, 19.5*cm, y)
    
    y -= 0.8*cm
    c.setFont('Kanit-Bold', 11)
    c.drawString(2*cm, y, "Details of Goods Declared")
    y -= 0.6*cm
    c.rect(2*cm, y-5*cm, 17*cm, 5*cm)

    if data['declared_items']:
        y_item = y - 0.7*cm
        c.setFont('Kanit', 10)
        for item in data['declared_items']:
            c.drawString(2.5*cm, y_item, f"{item['item']} - Qty: {item['quantity']}, Value: {item['value']:,.0f} THB")
            y_item -= 0.7*cm

    y = 5 * cm
    c.setFont('Kanit', 10)
    c.drawString(2*cm, y, "I certify that the information I have provided is true and correct.")
    c.line(12*cm, y-0.2*cm, 19*cm, y-0.2*cm)
    c.drawString(14*cm, y-0.8*cm, "Signature")
    c.drawString(2*cm, y-2*cm, f"Date: {data['arrival_date_str']}")

# --- MAIN SCRIPT ---
if __name__ == "__main__":
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    all_groundtruth_data = {}

    for i in range(1, NUMBER_OF_FORMS + 1):
        # 1. Select a person from the pool
        person = random.choice(PERSONS_POOL)
        
        # 2. Generate dynamic data for this form
        arrival_date = datetime.now() - timedelta(days=random.randint(0, 30))
        has_declaration = random.random() < 0.3 # 30% chance of having something to declare
        
        declared_items_list = []
        if has_declaration:
            num_items = random.randint(1,2)
            items_to_declare = random.sample(DECLARED_GOODS, num_items)
            for item in items_to_declare:
                declared_items_list.append({
                    "item": item['item'],
                    "quantity": 1,
                    "value": random.randint(item['value_min'], item['value_max'])
                })

        form_data = {
            "form_id": i,
            "person": person,
            "passport_no": f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1000000, 9999999)}",
            "dob_str": datetime.strptime(person['dob'], '%Y-%m-%d').strftime('%d %B %Y'),
            "flight_no": f"{random.choice(AIRLINES)}{random.randint(100, 999)}",
            "origin_city": random.choice(CITIES),
            "arrival_date": arrival_date.isoformat(),
            "arrival_date_str": get_english_date(arrival_date),
            "family_members": random.randint(0, 3),
            "declare_goods": has_declaration,
            "declare_currency": random.random() < 0.05 if has_declaration else False,
            "declared_items": declared_items_list
        }

        # 3. Create PDF using a random template
        file_name = f"Customs_Form_EN_{form_data['passport_no']}.pdf"
        file_path = os.path.join(OUTPUT_FOLDER, file_name)
        c = canvas.Canvas(file_path, pagesize=A4)
        
        template_choice, template_name = random.choice([
            (create_template_1, 'Classic'), 
            (create_template_2, 'Modern'), 
            (create_template_3, 'Compact')
        ])
        
        template_choice(c, form_data)
        c.save()
        
        # 4. Save ground truth
        form_data['template_used'] = template_name
        all_groundtruth_data[file_name] = form_data
        print(f"({i}/{NUMBER_OF_FORMS}) Created {file_name} using {template_name} template.")

    # 5. Write Ground Truth File
    groundtruth_filepath = os.path.join(OUTPUT_FOLDER, "groundtruth.json")
    with open(groundtruth_filepath, "w", encoding='utf-8') as f:
        json.dump(all_groundtruth_data, f, indent=4, ensure_ascii=False)

    print(f"\nSuccessfully generated {NUMBER_OF_FORMS} forms in '{OUTPUT_FOLDER}'.")
    print(f"Ground truth data saved to '{groundtruth_filepath}'.")