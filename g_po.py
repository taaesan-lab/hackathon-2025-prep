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
# NOTE: You may need to install this library: pip install num2words
from num2words import num2words

# --- CONFIGURATION ---
NUMBER_OF_POS = 100
OUTPUT_FOLDER = "out/04_english_pos"
RESOURCES_FOLDER = "./resources/"
FONT_REGULAR = "Sarabun-Regular"
FONT_BOLD = "Sarabun-Bold"

# --- DATA POOLS ---
# Using Faker for addresses to make them more realistic in English
fake_en = Faker("en_US")

GOV_AGENCIES = [
    {"name": "Digital Government Development Agency", "address": fake_en.address().replace('\n', ', '), "tax_id": "0994000155261"},
    {"name": "Ministry of Finance", "address": fake_en.address().replace('\n', ', '), "tax_id": "0994000021239"},
    {"name": "Department of International Trade Promotion", "address": fake_en.address().replace('\n', ', '), "tax_id": "0994000226354"},
]

SI_COMPANIES = [
    {"name": "Siam Integration Tech Co., Ltd."},
    {"name": "Bangkok Digital Solutions Co., Ltd."},
    {"name": "Chao Phraya Systems PCL."},
    {"name": "Cloud Computing (Thailand) Co., Ltd."},
    {"name": "Network Expert Consulting Co., Ltd."},
    {"name": "Datacenter Solutions Group Ltd."},
    {"name": "IT Infrastructure & Service Co., Ltd."},
    {"name": "Cyber Security Enterprise Co., Ltd."},
    {"name": "FutureTech Innovations Co., Ltd."},
    {"name": "Asia Pacific Systems Integrator Co., Ltd."},
    {"name": "Smart Government Solutions Co., Ltd."},
    {"name": "Thai Digital Platform Co., Ltd."},
    {"name": "Advance Business Integration Ltd."},
    {"name": "Amazing Technology Group Co., Ltd."},
    {"name": "Elite IT Consultants Co., Ltd."},
    {"name": "Professional Network Engineering Ltd."},
    {"name": "Kingdom IT Solutions PCL."},
    {"name": "GlobalTech Integration Co., Ltd."},
    {"name": "Ultimate Software & Hardware Co., Ltd."},
    {"name": "Premier Data Systems Co., Ltd."},
]

IT_PROJECTS = [
    "Data Center Network Upgrade Project",
    "Government Cloud Development Project",
    "Cybersecurity Enhancement Project",
    "High-Performance Server Procurement Project",
]

IT_ITEMS = {
    'hardware': [
        {"name": "Enterprise Server Dell R760", "price": 15000.00},
        {"name": "Core Switch Cisco C9500", "price": 9500.00},
        {"name": "Storage Array 50TB", "price": 20000.00},
        {"name": "Firewall FortiGate 200F", "price": 6800.00},
    ],
    'software': [
        {"name": "Network Management Software License (3-Year)", "price": 4200.00},
        {"name": "VMWare vSphere Enterprise License (16 cores)", "price": 5000.00},
        {"name": "Database Server License", "price": 6000.00},
    ],
    'service': [
        {"name": "System Installation & Configuration Service", "price": 8000.00},
        {"name": "Administrator Training Service", "price": 1500.00},
        {"name": "1-Year Maintenance Service", "price": 5500.00},
    ]
}

# --- HELPER FUNCTIONS ---
def get_english_date(dt):
    """Formats a datetime object into a standard English date string."""
    return dt.strftime("%B %d, %Y")

def draw_wrapped_text(c, text, x, y, max_width, font_name, font_size):
    """Draws text with wrapping."""
    c.setFont(font_name, font_size)
    lines = []
    for line in text.split('\n'):
        words = line.split()
        current_line = ""
        for word in words:
            if c.stringWidth(current_line + " " + word, font_name, font_size) <= max_width:
                current_line += " " + word if current_line else word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
    
    y_pos = y
    for line in lines:
        c.drawString(x, y_pos, line)
        y_pos -= font_size * 1.2
    return y_pos


def draw_header_footer_template1(c, data):
    """Classic template with Garuda"""
    c.drawImage(os.path.join(RESOURCES_FOLDER, "garuda.png"), 9.5 * cm, 26 * cm, width=3*cm, height=3*cm, preserveAspectRatio=True, mask='auto')
    c.setFont(FONT_BOLD, 24)
    c.drawCentredString(10.5 * cm, 25 * cm, "Purchase Order")
    c.setFont(FONT_REGULAR, 12)
    c.drawString(15 * cm, 24 * cm, f"PO No.: {data['po_number']}")
    c.drawString(15 * cm, 23.5 * cm, f"Date: {data['po_date_str']}")
    c.drawString(2 * cm, 24 * cm, f"Project No.: {data['project_number']}")

def draw_parties_template1(c, data):
    c.setFont(FONT_BOLD, 14)
    c.drawString(2 * cm, 22.5 * cm, "Buyer:")
    draw_wrapped_text(c, f"{data['buyer']['name']}\nAddress: {data['buyer']['address']}\nTax ID: {data['buyer']['tax_id']}", 2 * cm, 21.8 * cm, 8*cm, FONT_REGULAR, 12)
    
    c.drawString(11 * cm, 22.5 * cm, "Vendor:")
    draw_wrapped_text(c, f"{data['vendor']['name']}\nAddress: {data['vendor']['address']}\nTax ID: {data['vendor']['tax_id']} (Head Office)", 11 * cm, 21.8 * cm, 8*cm, FONT_REGULAR, 12)

def draw_line_items_table(c, y_start, data):
    c.setFont(FONT_BOLD, 12)
    c.rect(1.5*cm, y_start - 0.8*cm, 18*cm, 0.8*cm)
    c.drawCentredString(2.5*cm, y_start - 0.5*cm, "No.")
    c.drawCentredString(8*cm, y_start - 0.5*cm, "Description")
    c.drawCentredString(13.5*cm, y_start - 0.5*cm, "Quantity")
    c.drawCentredString(15.5*cm, y_start - 0.5*cm, "Unit Price")
    c.drawCentredString(18*cm, y_start - 0.5*cm, "Total Amount")
    
    y = y_start - 1.5 * cm
    c.setFont(FONT_REGULAR, 12)
    for i, item in enumerate(data['items']):
        c.drawCentredString(2.5*cm, y, str(i+1))
        c.drawString(4*cm, y, item['name'])
        c.drawCentredString(13.5*cm, y, f"{item['quantity']:,} {item['unit']}")
        c.drawRightString(16.5*cm, y, f"{item['unit_price']:,.2f}")
        c.drawRightString(19*cm, y, f"{item['total']:,.2f}")
        y -= 0.8 * cm
    
    c.line(1.5*cm, y_start - 0.8*cm, 1.5*cm, y + 0.5*cm) # Left
    c.line(3.5*cm, y_start - 0.8*cm, 3.5*cm, y + 0.5*cm) # No.
    c.line(12.5*cm, y_start - 0.8*cm, 12.5*cm, y + 0.5*cm) # Qty
    c.line(14.5*cm, y_start - 0.8*cm, 14.5*cm, y + 0.5*cm) # Unit Price
    c.line(17*cm, y_start - 0.8*cm, 17*cm, y + 0.5*cm) # Total
    c.line(19.5*cm, y_start - 0.8*cm, 19.5*cm, y + 0.5*cm) # Right
    c.line(1.5*cm, y + 0.5*cm, 19.5*cm, y + 0.5*cm) # Bottom
    return y

def draw_totals_and_signature(c, y_start, data):
    y = y_start
    c.setFont(FONT_REGULAR, 12)
    c.drawRightString(16.5 * cm, y, "Subtotal")
    c.drawRightString(19 * cm, y, f"{data['subtotal']:,.2f}")
    y -= 0.7 * cm
    c.drawRightString(16.5 * cm, y, "VAT 7%")
    c.drawRightString(19 * cm, y, f"{data['vat_amount']:,.2f}")
    y -= 0.7 * cm
    c.setFont(FONT_BOLD, 12)
    c.drawRightString(16.5 * cm, y, "Grand Total")
    c.drawRightString(19 * cm, y, f"{data['grand_total']:,.2f}")
    
    y = draw_wrapped_text(c, f"Grand Total (in words): {data['grand_total_en_str']}", 2*cm, y, 10*cm, FONT_REGULAR, 11)
    
    y -= 0.5*cm
    c.setFont(FONT_REGULAR, 12)
    c.drawString(2*cm, y, f"Less Withholding Tax 3% (on service total of {data['service_total']:,.2f}): {data['wht_amount']:,.2f}")
    c.setFont(FONT_BOLD, 12)
    c.drawString(2*cm, y - 0.7*cm, f"Net Payable: {data['net_payable']:,.2f}")
    
    # Signature
    y -= 4 * cm
    c.setFont(FONT_REGULAR, 12)
    c.drawCentredString(15.5*cm, y, "Signature ................................................................")
    c.drawCentredString(15.5*cm, y - 0.8*cm, f"({data['approver_name']})")
    c.drawCentredString(15.5*cm, y - 1.4*cm, data['approver_title'])
    c.drawCentredString(15.5*cm, y - 2.0*cm, "Authorized Signatory")

# --- TEMPLATE FUNCTIONS ---
def create_template_1(c, data):
    """Classic Official Template with Garuda."""
    draw_header_footer_template1(c, data)
    draw_parties_template1(c, data)
    c.setFont(FONT_BOLD, 12)
    c.drawString(2 * cm, 19.5 * cm, f"Reference: {data['project_name']}")
    y = draw_line_items_table(c, 18.5 * cm, data)
    draw_totals_and_signature(c, y, data)

def create_template_2(c, data):
    """Modern Template with Blue Header."""
    c.setFillColor(colors.HexColor('#2d3e50'))
    c.rect(0, 25*cm, 21*cm, 4.7*cm, stroke=0, fill=1)
    
    c.setFillColor(colors.white)
    c.setFont(FONT_BOLD, 36)
    c.drawString(2*cm, 27*cm, "Purchase Order")
    
    c.setFont(FONT_REGULAR, 12)
    c.drawRightString(19.5 * cm, 28 * cm, f"PO No.: {data['po_number']}")
    c.drawRightString(19.5 * cm, 27.5 * cm, f"Date: {data['po_date_str']}")
    c.drawRightString(19.5 * cm, 27 * cm, f"Project No.: {data['project_number']}")

    c.setFillColor(colors.black)
    draw_parties_template1(c, data)
    c.setFont(FONT_BOLD, 12)
    c.drawString(2 * cm, 19.5 * cm, f"Reference: {data['project_name']}")
    y = draw_line_items_table(c, 18.5 * cm, data)
    draw_totals_and_signature(c, y, data)

def create_template_3(c, data):
    """Boxed Layout Template."""
    c.setFont(FONT_BOLD, 24)
    c.drawString(2 * cm, 27.5 * cm, "Purchase Order")
    
    # Info Box
    c.setStrokeColor(colors.lightgrey)
    c.rect(13*cm, 26*cm, 6.5*cm, 2.5*cm)
    c.setFont(FONT_BOLD, 12)
    c.drawString(13.5*cm, 28*cm, "PO No.:")
    c.drawString(13.5*cm, 27.3*cm, "Date:")
    c.drawString(13.5*cm, 26.6*cm, "Project No.:")
    c.setFont(FONT_REGULAR, 12)
    c.drawString(16*cm, 28*cm, data['po_number'])
    c.drawString(16*cm, 27.3*cm, data['po_date_str'])
    c.drawString(16*cm, 26.6*cm, data['project_number'])

    draw_parties_template1(c, data)
    c.setFont(FONT_BOLD, 12)
    c.drawString(2 * cm, 19.5 * cm, f"Reference: {data['project_name']}")
    y = draw_line_items_table(c, 18.5 * cm, data)
    draw_totals_and_signature(c, y, data)


# --- MAIN SCRIPT ---
if __name__ == "__main__":
    # 1. Setup and Pre-flight Checks
    fake = Faker("en_US")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    try:
        pdfmetrics.registerFont(TTFont(FONT_REGULAR, os.path.join(RESOURCES_FOLDER, 'Sarabun-Regular.ttf')))
        pdfmetrics.registerFont(TTFont(FONT_BOLD, os.path.join(RESOURCES_FOLDER, 'Sarabun-Bold.ttf')))
    except Exception:
        print("ERROR: Font files not found in 'resources' folder.")
        print("Please make sure 'Sarabun-Regular.ttf' and 'Sarabun-Bold.ttf' are present.")
        exit()

    if not os.path.exists(os.path.join(RESOURCES_FOLDER, "garuda.png")):
        print("WARNING: 'garuda.png' not found. Template 1 will be missing the national emblem.")

    all_groundtruth_data = {}

    # 2. Main Generation Loop
    for i in range(1, NUMBER_OF_POS + 1):
        # Generate raw data for a single PO
        po_date = datetime.now() - timedelta(days=random.randint(0, 30))
        delivery_date = po_date + timedelta(days=random.randint(60, 90))
        
        buyer = random.choice(GOV_AGENCIES)
        vendor_profile = random.choice(SI_COMPANIES)
        
        vendor = {
            "name": vendor_profile['name'],
            "address": fake.address().replace('\n', ', '),
            "tax_id": fake.unique.numerify(text='01055' + '#' * 8)
        }
        
        items = []
        for _ in range(random.randint(2, 5)):
            item_type = random.choice(['hardware', 'software', 'service'])
            item_profile = random.choice(IT_ITEMS[item_type])
            quantity = random.randint(1, 5) if item_type == 'hardware' else 1
            
            item_data = {
                "name": item_profile['name'],
                "quantity": quantity,
                "unit": "Unit(s)" if item_type == 'hardware' else "Set" if item_type == 'software' else "Service",
                "unit_price": item_profile['price'],
                "total": item_profile['price'] * quantity,
                "type": item_type
            }
            items.append(item_data)
        
        subtotal = sum(item['total'] for item in items)
        vat_amount = subtotal * 0.07
        grand_total = subtotal + vat_amount
        service_total = sum(item['total'] for item in items if item['type'] == 'service')
        wht_amount = service_total * 0.03 if service_total > 0 else 0
        net_payable = grand_total - wht_amount

        # Assemble final data dictionary
        po_data = {
            "po_number": f"PO-{po_date.year}-{i:04d}",
            "po_date": po_date.isoformat(),
            "po_date_str": get_english_date(po_date),
            "delivery_date_str": get_english_date(delivery_date),
            "project_number": fake.unique.numerify(text=f'PROJ-{po_date.year}-' + '#####'),
            "project_name": random.choice(IT_PROJECTS),
            "buyer": buyer,
            "vendor": vendor,
            "items": items,
            "subtotal": subtotal,
            "vat_amount": vat_amount,
            "grand_total": grand_total,
            "grand_total_en_str": num2words(grand_total, to='currency', lang='en_US').title(),
            "service_total": service_total,
            "wht_amount": wht_amount,
            "net_payable": net_payable,
            "approver_name": fake.name(),
            "approver_title": "Chief Financial Officer"
        }

        # Create PDF using a random template
        file_name = f"PO_{po_data['po_number']}.pdf"
        file_path = os.path.join(OUTPUT_FOLDER, file_name)
        c = canvas.Canvas(file_path, pagesize=A4)
        
        template_choice = random.choice(['template1', 'template2', 'template3'])
        if template_choice == 'template1':
            create_template_1(c, po_data)
        elif template_choice == 'template2':
            create_template_2(c, po_data)
        else: # template3
            create_template_3(c, po_data)
        
        c.save()
        
        # Save ground truth for this PO
        all_groundtruth_data[file_name] = po_data
        print(f"({i}/{NUMBER_OF_POS}) Created {file_name} using {template_choice}")

    # 3. Write Ground Truth File
    groundtruth_filepath = os.path.join(OUTPUT_FOLDER, "groundtruth.json")
    with open(groundtruth_filepath, "w", encoding='utf-8') as f:
        json.dump(all_groundtruth_data, f, indent=4, ensure_ascii=False)

    print(f"\nSuccessfully generated {NUMBER_OF_POS} POs in '{OUTPUT_FOLDER}'.")
    print(f"Ground truth data saved to '{groundtruth_filepath}'.")