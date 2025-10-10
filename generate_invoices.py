import random
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import os

# --- Configuration ---
NUMBER_OF_INVOICES = 100
OUTPUT_FOLDER = "./output/01-resume"

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
    {"name": "Apex Innovations", "address": "789 Peak Plaza, Denver, CO 80202"},
    {"name": "Nexus Solutions", "address": "101 Connect Blvd, Austin, TX 78701"},
    {"name": "Visionary Dynamics", "address": "212 Future Way, Boston, MA 02110"},
    {"name": "BlueRidge Data", "address": "333 Mountain Pass, Asheville, NC 28801"},
    {"name": "Pinnacle Group", "address": "444 Summit Street, New York, NY 10001"},
    {"name": "Synergy Corp", "address": "555 Unity Lane, Chicago, IL 60606"},
    {"name": "Evergreen Systems", "address": "666 Forest Rd, Portland, OR 97204"},
    {"name": "Momentum AI", "address": "777 Acceleration Ave, Cambridge, MA 02139"},
    {"name": "Redwood Robotics", "address": "888 Giant Tree Grove, Palo Alto, CA 94301"},
    {"name": "Oasis Digital", "address": "999 Mirage Ct, Phoenix, AZ 85001"},
    {"name": "Terraform Labs", "address": "111 Earth St, Boulder, CO 80302"},
    {"name": "Helios Energy", "address": "222 Sunbeam Rd, Miami, FL 33101"},
    {"name": "Cyclone Networks", "address": "321 Vortex Point, Oklahoma City, OK 73102"},
    {"name": "IronClad Security", "address": "432 Vault Dr, Washington, DC 20001"},
    {"name": "SilverLining Cloud", "address": "543 Stratus Way, San Francisco, CA 94103"},
    {"name": "Crimson Analytics", "address": "654 Data St, Raleigh, NC 27601"},
    {"name": "Horizon Exports", "address": "765 Global View, Houston, TX 77002"},
    {"name": "Triton Logistics", "address": "876 Ocean Dr, Long Beach, CA 90802"},
    {"name": "AlphaWave AI", "address": "159 Alpha Ave, Pittsburgh, PA 15213"},
    {"name": "Zenith Grid", "address": "753 Zenith Crest, Salt Lake City, UT 84101"},
    {"name": "Fusion Dynamics", "address": "951 Fusion Blvd, San Diego, CA 92101"},
    {"name": "Catalyst Corp", "address": "357 Reaction Rd, Detroit, MI 48226"},
    {"name": "Echo Systems", "address": "852 Resonance Way, Nashville, TN 37203"},
    {"name": "Nova Solutions", "address": "654 Supernova St, Orlando, FL 32801"},
    {"name": "Vertex Ventures", "address": "147 Vertex Path, Indianapolis, IN 46204"},
    {"name": "Keystone Technologies", "address": "258 Arch Avenue, Philadelphia, PA 19106"},
    {"name": "Spire Digital", "address": "963 Spire Circle, Minneapolis, MN 55402"},
    {"name": "Granite State Analytics", "address": "147 Granite St, Manchester, NH 03101"},
    {"name": "Bridge Water Data", "address": "258 Bridge Rd, Hartford, CT 06103"},
    {"name": "Aperture Labs", "address": "369 Aperture Way, Cleveland, OH 44114"},
    {"name": "Core Axiom Inc.", "address": "741 Axiom Plaza, St. Louis, MO 63102"},
    {"name": "Pacific Rim Exports", "address": "852 Coastal Dr, San Jose, CA 95113"},
    {"name": "Midland Manufacturing", "address": "963 Central Ave, Kansas City, MO 64106"},
    {"name": "Polaris Navigation", "address": "159 North Star, Anchorage, AK 99501"},
    {"name": "Solstice Energy", "address": "753 Solstice Blvd, Albuquerque, NM 87102"},
    {"name": "Matrix Integrators", "address": "951 Matrix Way, Dallas, TX 75201"},
    {"name": "Cascade Consulting", "address": "357 Cascade Pass, Boise, ID 83702"},
    {"name": "Omega Finality Corp", "address": "852 Omega Pt, Atlanta, GA 30303"},
]
PRODUCT_ITEMS = [
    {"name": "Quantum Processor Core", "price": 450.00}, {"name": "HyperLoop Data Cable (10m)", "price": 75.50},
    {"name": "AI Model Training (Hour)", "price": 250.00}, {"name": "Cloud Storage (TB/Month)", "price": 50.00},
    {"name": "Enterprise Software License", "price": 1200.00}, {"name": "Cybersecurity Audit", "price": 2500.00},
    {"name": "System Integration Service", "price": 1800.00}, {"name": "IoT Sensor Pack", "price": 320.00},
    {"name": "VR Development Kit", "price": 999.00}, {"name": "Data Migration Service (Per TB)", "price": 1500.00},
    {"name": "API Gateway License (Annual)", "price": 3500.00}, {"name": "Blockchain Notary Service", "price": 200.00},
    {"name": "Edge Computing Node", "price": 750.00}, {"name": "Predictive Analytics Module", "price": 4800.00},
    {"name": "Load Balancer Subscription", "price": 150.00}, {"name": "Disaster Recovery Plan", "price": 5500.00},
    {"name": "IT Strategy Consulting (Day)", "price": 2200.00}, {"name": "Penetration Testing Service", "price": 6000.00},
    {"name": "Custom Software Patch", "price": 850.00}, {"name": "AR Overlay SDK", "price": 1300.00},
    {"name": "Biometric Scanner Unit", "price": 430.00}, {"name": "Server Rack (42U)", "price": 1100.00},
    {"name": "Fiber Optic Transceiver", "price": 120.00}, {"name": "DevOps Pipeline Setup", "price": 3200.00},
    {"name": "Redundant Power Supply", "price": 280.00}, {"name": "Cloud Cost Optimization Report", "price": 950.00},
    {"name": "Technical Support Retainer (Month)", "price": 500.00}, {"name": "Database Replication Setup", "price": 1600.00},
    {"name": "Managed Kubernetes Cluster", "price": 700.00},
]

# --- Helper function for drawing table ---
def draw_items_table(c, y_pos, data, table_style):
    width, _ = letter
    c.setFont("Helvetica-Bold", 10)
    
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
        c.setFont("Helvetica", 10)
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
    c.setFont("Helvetica", 10); c.drawString(0.5 * inch, height - 1.5 * inch, OUR_COMPANY_ADDRESS)
    
    c.setFont("Helvetica-Bold", 24); c.drawCentredString(width / 2, height - 1 * inch, "INVOICE")

    c.setFont("Helvetica-Bold", 12); c.drawString(width - 3.5 * inch, height - 1 * inch, "Invoice #:"); c.drawString(width - 2.5 * inch, height - 1 * inch, data["invoice_id"])
    c.drawString(width - 3.5 * inch, height - 1.25 * inch, "Issue Date:"); c.drawString(width - 2.5 * inch, height - 1.25 * inch, data["issue_date"])

    c.setFont("Helvetica-Bold", 12); c.drawString(0.5 * inch, height - 2.5 * inch, "BILL TO:")
    c.setFont("Helvetica", 12); c.drawString(0.5 * inch, height - 2.75 * inch, data["customer"]["name"]); c.drawString(0.5 * inch, height - 2.95 * inch, data["customer"]["address"])

    y_pos = draw_items_table(c, height - 4 * inch, data, {})

    c.setFont("Helvetica-Bold", 12); c.drawRightString(width - 2.5 * inch, y_pos - 0.5 * inch, "Total:"); c.drawRightString(width - 0.7 * inch, y_pos - 0.5 * inch, f'${data["total"]:.2f}')

# --- TEMPLATE 2: MODERN MINIMALIST ---
def create_modern_template(c, data):
    width, height = letter
    c.setFillColor(colors.black)
    if os.path.exists(OUR_COMPANY_LOGO_PATH): c.drawImage(OUR_COMPANY_LOGO_PATH, 0.5 * inch, height - 1.1 * inch, width=0.8*inch, height=0.8*inch, preserveAspectRatio=True, mask='auto')
    
    c.setFont("Helvetica-Bold", 16); c.drawString(1.5 * inch, height - 0.9 * inch, OUR_COMPANY_NAME)
    c.setFont("Helvetica", 9); c.drawString(1.5 * inch, height - 1.1 * inch, OUR_COMPANY_ADDRESS)
    
    c.setStrokeColor(MODERN_BLUE); c.setLineWidth(2); c.line(0.5 * inch, height - 1.5 * inch, width - 0.5 * inch, height - 1.5 * inch)

    c.setFont("Helvetica-Bold", 10); c.drawString(0.5 * inch, height - 1.8 * inch, "BILL TO"); c.drawString(4.5 * inch, height - 1.8 * inch, "INVOICE DETAILS")
    c.setFont("Helvetica", 10); c.drawString(0.5 * inch, height - 2.0 * inch, data["customer"]["name"]); c.drawString(0.5 * inch, height - 2.2 * inch, data["customer"]["address"])
    c.drawString(4.5 * inch, height - 2.0 * inch, f"Invoice #: {data['invoice_id']}"); c.drawString(4.5 * inch, height - 2.2 * inch, f"Issue Date: {data['issue_date']}")

    y_pos = draw_items_table(c, height - 3 * inch, data, {"header_font_color": MODERN_BLUE})
    c.setFont("Helvetica-Bold", 12); c.drawRightString(width - 2.5 * inch, y_pos - 0.5 * inch, "Total Due:"); c.drawRightString(width - 0.7 * inch, y_pos - 0.5 * inch, f'${data["total"]:.2f}')

# --- TEMPLATE 3: BOLD HEADER ---
def create_bold_header_template(c, data):
    width, height = letter
    c.setFillColor(HEADER_GRAY); c.rect(0, height - 1.5*inch, width, 1.5*inch, stroke=0, fill=1)
    
    c.setFillColor(colors.white)
    if os.path.exists(OUR_COMPANY_LOGO_PATH): c.drawImage(OUR_COMPANY_LOGO_PATH, 0.5 * inch, height - 1.25 * inch, width=1*inch, height=1*inch, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 28); c.drawRightString(width - 0.5 * inch, height - 1.1 * inch, "INVOICE")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10); c.drawString(0.5 * inch, height - 1.8 * inch, "FROM"); c.drawString(4.5 * inch, height - 1.8 * inch, "BILL TO")
    c.setFont("Helvetica", 10); c.drawString(0.5 * inch, height - 2.0 * inch, OUR_COMPANY_NAME); c.drawString(0.5 * inch, height - 2.2 * inch, OUR_COMPANY_ADDRESS)
    c.drawString(4.5 * inch, height - 2.0 * inch, data["customer"]["name"]); c.drawString(4.5 * inch, height - 2.2 * inch, data["customer"]["address"])

    y_pos = draw_items_table(c, height - 3.5 * inch, data, {"header_bg_color": colors.lightgrey})
    c.setFillColor(HEADER_GRAY); c.rect(width - 3.2 * inch, y_pos - 0.5 * inch, 2.7 * inch, 0.5 * inch, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 12); c.drawString(width - 3 * inch, y_pos - 0.35 * inch, "TOTAL"); c.drawRightString(width - 0.7 * inch, y_pos - 0.35 * inch, f'${data["total"]:.2f}')

# --- TEMPLATE 4: BOXED LAYOUT ---
def create_boxed_template(c, data):
    width, height = letter
    c.setFont("Helvetica-Bold", 16); c.drawString(0.5*inch, height-0.7*inch, OUR_COMPANY_NAME)
    c.setFont("Helvetica-Bold", 28); c.drawRightString(width - 0.5*inch, height-0.7*inch, "INVOICE")
    
    c.setFillColor(BOX_GRAY_LIGHT); c.rect(0.5*inch, height-2.5*inch, 3.5*inch, 1.2*inch, stroke=0, fill=1)
    c.rect(4.5*inch, height-2.5*inch, 3.5*inch, 1.2*inch, stroke=0, fill=1)
    c.setFillColor(colors.black)

    c.setFont("Helvetica-Bold", 10); c.drawString(0.7*inch, height-1.5*inch, "BILL TO")
    c.setFont("Helvetica", 10); c.drawString(0.7*inch, height-1.7*inch, data["customer"]["name"]); c.drawString(0.7*inch, height-1.9*inch, data["customer"]["address"])

    c.setFont("Helvetica-Bold", 10); c.drawString(4.7*inch, height-1.5*inch, "INVOICE #"); c.drawString(4.7*inch, height-1.9*inch, "ISSUE DATE")
    c.setFont("Helvetica", 10); c.drawString(5.7*inch, height-1.5*inch, data["invoice_id"]); c.drawString(5.7*inch, height-1.9*inch, data["issue_date"])

    y_pos = draw_items_table(c, height-3*inch, data, {"header_bg_color": colors.black, "header_font_color": colors.white})
    c.setFont("Helvetica-Bold", 12); c.drawRightString(width - 2.5 * inch, y_pos - 0.5 * inch, "TOTAL:"); c.drawRightString(width - 0.7 * inch, y_pos - 0.5 * inch, f'${data["total"]:.2f}')

# --- TEMPLATE 5: CENTERED FORMAL ---
def create_centered_template(c, data):
    width, height = letter
    if os.path.exists(OUR_COMPANY_LOGO_PATH): c.drawCentredString(width/2, height - 0.8 * inch, ""); c.drawImage(OUR_COMPANY_LOGO_PATH, width/2 - 0.5*inch, height - 1*inch, width=1*inch, height=1*inch, preserveAspectRatio=True, mask='auto')
    
    c.setFont("Helvetica-Bold", 16); c.drawCentredString(width/2, height-1.4*inch, OUR_COMPANY_NAME)
    c.setFont("Helvetica", 10); c.drawCentredString(width/2, height-1.6*inch, OUR_COMPANY_ADDRESS)

    c.setFont("Helvetica-Bold", 12); c.drawString(0.5*inch, height-2.5*inch, "BILL TO:"); c.drawRightString(width-0.5*inch, height-2.5*inch, f"INVOICE #: {data['invoice_id']}")
    c.setFont("Helvetica", 10); c.drawString(0.5*inch, height-2.7*inch, data["customer"]["name"]); c.drawRightString(width-0.5*inch, height-2.7*inch, f"DATE: {data['issue_date']}")

    y_pos = draw_items_table(c, height-3.5*inch, data, {})
    c.setFont("Helvetica-Bold", 14); c.drawRightString(width-0.7*inch, y_pos - 0.6 * inch, f'TOTAL: ${data["total"]:.2f}')
    c.setFont("Helvetica-Oblique", 10); c.drawCentredString(width/2, y_pos-1.2*inch, "Thank you for your business!")

# --- PDF Creation Dispatcher ---
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
    # Create output and resources directory if they don't exist
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists("resources"): os.makedirs("resources")

    if not os.path.exists(OUR_COMPANY_LOGO_PATH):
        print(f"WARNING: Logo file not found at '{OUR_COMPANY_LOGO_PATH}'.")
        print("Please place your logo there to have it included in the invoices.")

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
        
        print(f"({i}/{NUMBER_OF_INVOICES}) Created: {invoice_data['filename']} (Template: {template_choice})")

    print(f"\nSuccessfully generated {NUMBER_OF_INVOICES} invoices in the '{OUTPUT_FOLDER}' folder.")