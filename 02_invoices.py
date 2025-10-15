import random
import shutil
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import os
import json
# --- START: ADDED FOR CUSTOM FONT ---
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sys
# --- END: ADDED FOR CUSTOM FONT ---


# --- Configuration ---
NUMBER_OF_INVOICES = 100
OUTPUT_FOLDER = "./out/02-invoices/"

# Our Company Information
OUR_COMPANY_NAME = "Global Tech Services Inc."
OUR_COMPANY_LOGO_PATH = "./resources/company_logo.png"
OUR_COMPANY_ADDRESS = "789 Tech Park, Bangkok 10110"

# Template Colors
MODERN_BLUE = colors.HexColor('#005cb9')
HEADER_GRAY = colors.HexColor('#4c4c4c')
BOX_GRAY_LIGHT = colors.HexColor('#f0f0f0')

# --- Data for Randomization (Same as before) ---
CUSTOMER_COMPANIES = [
    {"name": "QuantumLeap Tech", "address": "123 Quantum Drive, Silicon Valley, CA 94043"},
    {"name": "StellarWorks Inc.", "address": "456 Galaxy Avenue, Seattle, WA 98101"},
    # ... (rest of the list is unchanged)
]
PRODUCT_ITEMS = [
    {"name": "Quantum Processor Core", "price": 450.00}, {"name": "HyperLoop Data Cable (10m)", "price": 75.50},
    # ... (rest of the list is unchanged)
]


# --- Helper function for drawing table ---
def draw_items_table(c, y_pos, data, table_style):
    width, _ = letter
    c.setFont("Kanit-Bold", 10) # <-- MODIFIED

    # Style customizations
    header_bg_color = table_style.get("header_bg_color", None)
    header_font_color = table_style.get("header_font_color", colors.black)

    if header_bg_color:
        c.setFillColor(header_bg_color)
        c.rect(0.5 * inch, y_pos - 0.1 * inch, width - 1 * inch, 0.3 * inch, stroke=0, fill=1)

    c.setFillColor(header_font_color)
    c.drawString(0.7 * inch, y_pos, "Description")
    c.drawString(4.5 * inch, y_pos, "Quantity")
    c.drawString(5.5 * inch, y_pos, "Unit Price")
    c.drawRightString(width - 0.7 * inch, y_pos, "Total")

    c.setFillColor(colors.black)
    y_pos -= 0.35 * inch

    for item in data["items"]:
        total_price = item["quantity"] * item["price"]
        c.setFont("Kanit", 10) # <-- MODIFIED
        c.drawString(0.7 * inch, y_pos, item["name"])
        c.drawRightString(5.0 * inch, y_pos, str(item["quantity"]))
        c.drawRightString(6.2 * inch, y_pos, f"${item['price']:.2f}")
        c.drawRightString(width - 0.7 * inch, y_pos, f"${total_price:.2f}")
        y_pos -= 0.25 * inch
    return y_pos

# --- TEMPLATE 1: CLASSIC ---
def create_classic_template(c, data):
    width, height = letter
    if os.path.exists(OUR_COMPANY_LOGO_PATH): c.drawImage(OUR_COMPANY_LOGO_PATH, 0.5 * inch, height - 1.25 * inch, width=1*inch, height=1*inch, preserveAspectRatio=True, mask='auto')
    c.setFont("Kanit", 10); c.drawString(0.5 * inch, height - 1.5 * inch, OUR_COMPANY_ADDRESS) # <-- MODIFIED

    c.setFont("Kanit-Bold", 24); c.drawCentredString(width / 2, height - 1 * inch, "INVOICE") # <-- MODIFIED

    c.setFont("Kanit-Bold", 12); c.drawString(width - 3.5 * inch, height - 1 * inch, "Invoice #:"); c.drawString(width - 2.5 * inch, height - 1 * inch, data["invoice_id"]) # <-- MODIFIED
    c.drawString(width - 3.5 * inch, height - 1.25 * inch, "Issue Date:"); c.drawString(width - 2.5 * inch, height - 1.25 * inch, data["issue_date"])

    c.setFont("Kanit-Bold", 12); c.drawString(0.5 * inch, height - 2.5 * inch, "BILL TO:") # <-- MODIFIED
    c.setFont("Kanit", 12); c.drawString(0.5 * inch, height - 2.75 * inch, data["customer"]["name"]); c.drawString(0.5 * inch, height - 2.95 * inch, data["customer"]["address"]) # <-- MODIFIED

    y_pos = draw_items_table(c, height - 4 * inch, data, {})

    c.setFont("Kanit-Bold", 12); c.drawRightString(width - 2.5 * inch, y_pos - 0.5 * inch, "Total:"); c.drawRightString(width - 0.7 * inch, y_pos - 0.5 * inch, f'${data["total"]:.2f}') # <-- MODIFIED

# --- TEMPLATE 2: MODERN MINIMALIST ---
def create_modern_template(c, data):
    width, height = letter
    c.setFillColor(colors.black)
    if os.path.exists(OUR_COMPANY_LOGO_PATH): c.drawImage(OUR_COMPANY_LOGO_PATH, 0.5 * inch, height - 1.1 * inch, width=0.8*inch, height=0.8*inch, preserveAspectRatio=True, mask='auto')

    c.setFont("Kanit-Bold", 16); c.drawString(1.5 * inch, height - 0.9 * inch, OUR_COMPANY_NAME) # <-- MODIFIED
    c.setFont("Kanit", 9); c.drawString(1.5 * inch, height - 1.1 * inch, OUR_COMPANY_ADDRESS) # <-- MODIFIED

    c.setStrokeColor(MODERN_BLUE); c.setLineWidth(2); c.line(0.5 * inch, height - 1.5 * inch, width - 0.5 * inch, height - 1.5 * inch)

    c.setFont("Kanit-Bold", 10); c.drawString(0.5 * inch, height - 1.8 * inch, "BILL TO"); c.drawString(4.5 * inch, height - 1.8 * inch, "INVOICE DETAILS") # <-- MODIFIED
    c.setFont("Kanit", 10); c.drawString(0.5 * inch, height - 2.0 * inch, data["customer"]["name"]); c.drawString(0.5 * inch, height - 2.2 * inch, data["customer"]["address"]) # <-- MODIFIED
    c.drawString(4.5 * inch, height - 2.0 * inch, f"Invoice #: {data['invoice_id']}"); c.drawString(4.5 * inch, height - 2.2 * inch, f"Issue Date: {data['issue_date']}")

    y_pos = draw_items_table(c, height - 3 * inch, data, {"header_font_color": MODERN_BLUE})
    c.setFont("Kanit-Bold", 12); c.drawRightString(width - 2.5 * inch, y_pos - 0.5 * inch, "Total Due:"); c.drawRightString(width - 0.7 * inch, y_pos - 0.5 * inch, f'${data["total"]:.2f}') # <-- MODIFIED

# --- TEMPLATE 3: BOLD HEADER ---
def create_bold_header_template(c, data):
    width, height = letter
    c.setFillColor(HEADER_GRAY); c.rect(0, height - 1.5*inch, width, 1.5*inch, stroke=0, fill=1)

    c.setFillColor(colors.white)
    if os.path.exists(OUR_COMPANY_LOGO_PATH): c.drawImage(OUR_COMPANY_LOGO_PATH, 0.5 * inch, height - 1.25 * inch, width=1*inch, height=1*inch, preserveAspectRatio=True, mask='auto')
    c.setFont("Kanit-Bold", 28); c.drawRightString(width - 0.5 * inch, height - 1.1 * inch, "INVOICE") # <-- MODIFIED

    c.setFillColor(colors.black)
    c.setFont("Kanit-Bold", 10); c.drawString(0.5 * inch, height - 1.8 * inch, "FROM"); c.drawString(4.5 * inch, height - 1.8 * inch, "BILL TO") # <-- MODIFIED
    c.setFont("Kanit", 10); c.drawString(0.5 * inch, height - 2.0 * inch, OUR_COMPANY_NAME); c.drawString(0.5 * inch, height - 2.2 * inch, OUR_COMPANY_ADDRESS) # <-- MODIFIED
    c.drawString(4.5 * inch, height - 2.0 * inch, data["customer"]["name"]); c.drawString(4.5 * inch, height - 2.2 * inch, data["customer"]["address"])

    y_pos = draw_items_table(c, height - 3.5 * inch, data, {"header_bg_color": colors.lightgrey})
    c.setFillColor(HEADER_GRAY); c.rect(width - 3.2 * inch, y_pos - 0.5 * inch, 2.7 * inch, 0.5 * inch, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("Kanit-Bold", 12); c.drawString(width - 3 * inch, y_pos - 0.35 * inch, "TOTAL"); c.drawRightString(width - 0.7 * inch, y_pos - 0.35 * inch, f'${data["total"]:.2f}') # <-- MODIFIED

# --- TEMPLATE 4: BOXED LAYOUT ---
def create_boxed_template(c, data):
    width, height = letter
    c.setFont("Kanit-Bold", 16); c.drawString(0.5*inch, height-0.7*inch, OUR_COMPANY_NAME) # <-- MODIFIED
    c.setFont("Kanit-Bold", 28); c.drawRightString(width - 0.5*inch, height-0.7*inch, "INVOICE") # <-- MODIFIED

    c.setFillColor(BOX_GRAY_LIGHT); c.rect(0.5*inch, height-2.5*inch, 3.5*inch, 1.2*inch, stroke=0, fill=1)
    c.rect(4.5*inch, height-2.5*inch, 3.5*inch, 1.2*inch, stroke=0, fill=1)
    c.setFillColor(colors.black)

    c.setFont("Kanit-Bold", 10); c.drawString(0.7*inch, height-1.5*inch, "BILL TO") # <-- MODIFIED
    c.setFont("Kanit", 10); c.drawString(0.7*inch, height-1.7*inch, data["customer"]["name"]); c.drawString(0.7*inch, height-1.9*inch, data["customer"]["address"]) # <-- MODIFIED

    c.setFont("Kanit-Bold", 10); c.drawString(4.7*inch, height-1.5*inch, "INVOICE #"); c.drawString(4.7*inch, height-1.9*inch, "ISSUE DATE") # <-- MODIFIED
    c.setFont("Kanit", 10); c.drawString(5.7*inch, height-1.5*inch, data["invoice_id"]); c.drawString(5.7*inch, height-1.9*inch, data["issue_date"]) # <-- MODIFIED

    y_pos = draw_items_table(c, height-3*inch, data, {"header_bg_color": colors.black, "header_font_color": colors.white})
    c.setFont("Kanit-Bold", 12); c.drawRightString(width - 2.5 * inch, y_pos - 0.5 * inch, "TOTAL:"); c.drawRightString(width - 0.7 * inch, y_pos - 0.5 * inch, f'${data["total"]:.2f}') # <-- MODIFIED

# --- TEMPLATE 5: CENTERED FORMAL ---
def create_centered_template(c, data):
    width, height = letter
    if os.path.exists(OUR_COMPANY_LOGO_PATH): c.drawCentredString(width/2, height - 0.8 * inch, ""); c.drawImage(OUR_COMPANY_LOGO_PATH, width/2 - 0.5*inch, height - 1*inch, width=1*inch, height=1*inch, preserveAspectRatio=True, mask='auto')

    c.setFont("Kanit-Bold", 16); c.drawCentredString(width/2, height-1.4*inch, OUR_COMPANY_NAME) # <-- MODIFIED
    c.setFont("Kanit", 10); c.drawCentredString(width/2, height-1.6*inch, OUR_COMPANY_ADDRESS) # <-- MODIFIED

    c.setFont("Kanit-Bold", 12); c.drawString(0.5*inch, height-2.5*inch, "BILL TO:"); c.drawRightString(width-0.5*inch, height-2.5*inch, f"INVOICE #: {data['invoice_id']}") # <-- MODIFIED
    c.setFont("Kanit", 10); c.drawString(0.5*inch, height-2.7*inch, data["customer"]["name"]); c.drawRightString(width-0.5*inch, height-2.7*inch, f"DATE: {data['issue_date']}") # <-- MODIFIED

    y_pos = draw_items_table(c, height-3.5*inch, data, {})
    c.setFont("Kanit-Bold", 14); c.drawRightString(width-0.7*inch, y_pos - 0.6 * inch, f'TOTAL: ${data["total"]:.2f}') # <-- MODIFIED
    c.setFont("Kanit-Italic", 10); c.drawCentredString(width/2, y_pos-1.2*inch, "Thank you for your business!") # <-- MODIFIED

# --- PDF Creation Dispatcher ---
# (This function is unchanged)
def create_invoice_pdf(invoice_data, file_path, template_choice):
    c = canvas.Canvas(file_path, pagesize=letter)
    if template_choice == 'classic': create_classic_template(c, invoice_data)
    elif template_choice == 'modern': create_modern_template(c, invoice_data)
    elif template_choice == 'bold_header': create_bold_header_template(c, invoice_data)
    elif template_choice == 'boxed': create_boxed_template(c, invoice_data)
    elif template_choice == 'centered': create_centered_template(c, invoice_data)
    c.save()


# --- Main Generation Loop ---
if __name__ == "__main__":
    # --- START: ADDED FOR CUSTOM FONT ---
    # Define font paths
    font_regular_path = os.path.join("resources", "Kanit-Regular.ttf")
    font_bold_path = os.path.join("resources", "Kanit-Bold.ttf")
    font_italic_path = os.path.join("resources", "Kanit-Italic.ttf")
    font_bold_italic_path = os.path.join("resources", "Kanit-BoldItalic.ttf")

    # Check if font files exist before registering
    if not all(os.path.exists(p) for p in [font_regular_path, font_bold_path, font_italic_path, font_bold_italic_path]):
        print("ERROR: Kanit font files not found in the 'resources' folder.")
        print("Please download Kanit from Google Fonts and place the following files in './resources/':")
        print("- Kanit-Regular.ttf\n- Kanit-Bold.ttf\n- Kanit-Italic.ttf\n- Kanit-BoldItalic.ttf")
        sys.exit(1) # Exit the script

    # Register the Kanit font family
    pdfmetrics.registerFont(TTFont('Kanit', font_regular_path))
    pdfmetrics.registerFont(TTFont('Kanit-Bold', font_bold_path))
    pdfmetrics.registerFont(TTFont('Kanit-Italic', font_italic_path))
    pdfmetrics.registerFont(TTFont('Kanit-BoldItalic', font_bold_italic_path))
    pdfmetrics.registerFontFamily('Kanit', normal='Kanit', bold='Kanit-Bold', italic='Kanit-Italic', boldItalic='Kanit-BoldItalic')
    print("Successfully registered Kanit font family.")
    # --- END: ADDED FOR CUSTOM FONT ---


    # --- START: FOLDER CLEANUP UTILITY ---
    # If the output folder exists, remove it and all its contents
    if os.path.exists(OUTPUT_FOLDER):
        print(f"Removing existing directory: {OUTPUT_FOLDER}")
        shutil.rmtree(OUTPUT_FOLDER)
    # --- END: FOLDER CLEANUP UTILITY ---


    # Create output and resources directory if they don't exist
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists("resources"): os.makedirs("resources")

    if not os.path.exists(OUR_COMPANY_LOGO_PATH):
        print(f"WARNING: Logo file not found at '{OUR_COMPANY_LOGO_PATH}'.")
        print("Please place your logo there to have it included in the invoices.")

    groundtruth_data = {}

    for i in range(1, NUMBER_OF_INVOICES + 1):
        invoice_id = f"INV-2025-{i:04d}"
        issue_date = datetime.now() - timedelta(days=random.randint(0, 30))
        customer = random.choice(CUSTOMER_COMPANIES)

        items, subtotal = [], 0
        for _ in range(random.randint(1, 5)):
            item = random.choice(PRODUCT_ITEMS)
            quantity = random.randint(1, 10)
            items.append({"name": item["name"], "quantity": quantity, "price": item["price"]})
            subtotal += quantity * item["price"]

        tax_rate, tax_amount = 0.07, subtotal * 0.07
        total = subtotal + tax_amount

        invoice_data = {
            "filename": f"invoice_{invoice_id}.pdf", "invoice_id": invoice_id,
            "issue_date": issue_date.strftime("%Y-%m-%d"), "customer": customer,
            "items": items, "subtotal": subtotal, "tax_rate": tax_rate,
            "tax_amount": tax_amount, "total": total,
        }

        template_choice = random.choice(['classic', 'modern', 'bold_header', 'boxed', 'centered'])
        file_path = os.path.join(OUTPUT_FOLDER, invoice_data["filename"])
        create_invoice_pdf(invoice_data, file_path, template_choice)

        # Create and store ground truth data
        groundtruth_record = {
            "invoice_id": invoice_data["invoice_id"],
            "issue_date": invoice_data["issue_date"],
            "customer_name": invoice_data["customer"]["name"],
            "customer_address": invoice_data["customer"]["address"],
            "subtotal": round(invoice_data["subtotal"], 2),
            "tax_amount": round(invoice_data["tax_amount"], 2),
            "total": round(invoice_data["total"], 2),
            "line_items": []
        }
        for item in invoice_data["items"]:
            groundtruth_record["line_items"].append({
                "description": item["name"],
                "quantity": item["quantity"],
                "unit_price": item["price"],
                "line_total": round(item["quantity"] * item["price"], 2)
            })

        groundtruth_data[invoice_data["filename"]] = groundtruth_record

        print(f"({i}/{NUMBER_OF_INVOICES}) Created: {invoice_data['filename']} (Template: {template_choice})")

    # Write the groundtruth JSON file
    groundtruth_file_path = os.path.join(OUTPUT_FOLDER, "groundtruth.json")
    with open(groundtruth_file_path, 'w') as f:
        json.dump(groundtruth_data, f, indent=4)

    print(f"\nSuccessfully generated {NUMBER_OF_INVOICES} invoices in the '{OUTPUT_FOLDER}' folder.")
    print(f"Successfully generated groundtruth.json at '{groundtruth_file_path}'")