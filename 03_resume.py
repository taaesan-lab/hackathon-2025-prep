import os
import shutil
import random
import json # <--- ADDED: Import the json library
from datetime import datetime, timedelta
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# --- CONFIGURATION ---
NUMBER_OF_RESUMES = 100
OUTPUT_FOLDER = "out/03_resumes"

# Template Colors
MODERN_BLUE = colors.HexColor('#2d5d8a')
SIDEBAR_GRAY = colors.HexColor('#333333')

# --- DATA POOLS (Same as before) ---
INDUSTRY_DATA = {
    "Technology": {
        "company_names": ["Innovatech Solutions", "DataCore Systems", "CloudSphere Inc.", "QuantumLeap AI", "CyberSecure Corp"],
        "job_titles": {
            "entry": ["Junior Developer", "IT Support Specialist", "QA Tester"],
            "mid": ["Software Engineer", "DevOps Specialist", "Data Analyst", "UI/UX Designer"],
            "senior": ["Senior Backend Engineer", "Lead Data Scientist", "Principal Architect", "Product Manager"]
        },
        "skills": ["Python", "Java", "AWS", "Docker", "Kubernetes", "SQL", "React", "Agile Methodologies", "CI/CD"]
    },
    "Healthcare": {
        "company_names": ["Evergreen Health Clinic", "Unity Medical Center", "Wellspring Diagnostics", "CarePoint Hospitals"],
        "job_titles": {
            "entry": ["Medical Assistant", "Lab Technician", "Patient Care Coordinator"],
            "mid": ["Registered Nurse", "Clinical Research Associate", "Healthcare Administrator"],
            "senior": ["Clinical Manager", "Senior Nurse Practitioner", "Hospital Director"]
        },
        "skills": ["Patient Care", "HIPAA Compliance", "EMR/EHR Systems", "Phlebotomy", "Medical Terminology", "BLS/CPR"]
    },
    "Finance": {
        "company_names": ["Summit Financial Group", "Meridian Capital", "Keystone Investments", "Iron Bank Corp"],
        "job_titles": {
            "entry": ["Junior Financial Analyst", "Accounting Clerk", "Audit Associate"],
            "mid": ["Accountant", "Financial Advisor", "Senior Auditor"],
            "senior": ["Investment Banker", "Finance Manager", "VP of Finance"]
        },
        "skills": ["Financial Modeling", "Microsoft Excel", "QuickBooks", "SOX Compliance", "Risk Analysis", "Bloomberg Terminal"]
    },
    "Marketing & Advertising": {
        "company_names": ["Creative Spark Agency", "Momentum Marketing", "BrandVantage", "Digital Tsunami"],
        "job_titles": {
            "entry": ["Marketing Coordinator", "Social Media Assistant", "Content Creator"],
            "mid": ["Digital Marketing Specialist", "SEO/SEM Analyst", "Brand Manager"],
            "senior": ["Marketing Director", "Senior Content Strategist", "VP of Growth"]
        },
        "skills": ["SEO/SEM", "Google Analytics", "Content Marketing", "Email Campaigns", "Adobe Creative Suite", "PPC"]
    },
    "Education": {
        "company_names": ["Northwood Preparatory", "Oak Valley University", "Bright Future Learning", "Global EdTech"],
        "job_titles": {
            "entry": ["Teaching Assistant", "Admissions Counselor", "Tutor"],
            "mid": ["Teacher", "Curriculum Developer", "Instructional Designer"],
            "senior": ["Lead Teacher", "School Principal", "Dean of Academics"]
        },
        "skills": ["Curriculum Design", "Classroom Management", "LMS Platforms (Canvas, Blackboard)", "Student Assessment"]
    },
    "Retail & E-commerce": {
        "company_names": ["Urban Trends", "FreshCart Online", "HomeGoods Emporium", "Velocity Commerce"],
        "job_titles": {
            "entry": ["Sales Associate", "Customer Service Rep", "Stock Clerk"],
            "mid": ["Store Manager", "E-commerce Analyst", "Merchandise Buyer"],
            "senior": ["District Manager", "Head of E-commerce", "Supply Chain Director"]
        },
        "skills": ["Inventory Management", "POS Systems", "Shopify", "Customer Relationship Management (CRM)", "Sales Forecasting"]
    },
    "Manufacturing": {
        "company_names": ["Apex Manufacturing", "Precision Parts Inc.", "IronForge Industries", "SynthETech Polymers"],
        "job_titles": {
            "entry": ["Production Associate", "Quality Control Inspector", "Machine Operator"],
            "mid": ["Process Engineer", "Production Supervisor", "Logistics Coordinator"],
            "senior": ["Plant Manager", "Head of Operations", "Quality Assurance Director"]
        },
        "skills": ["Lean Manufacturing", "Six Sigma", "Quality Control (QC)", "Supply Chain Management", "CAD", "OSHA Safety"]
    },
    "Hospitality": {
        "company_names": ["Grand Vista Hotel", "The Coastal Resort", "Urban Eats Group", "Summit Retreats"],
        "job_titles": {
            "entry": ["Front Desk Agent", "Concierge", "Event Assistant"],
            "mid": ["Hotel Manager", "Event Planner", "Head Chef"],
            "senior": ["General Manager", "Director of Sales", "Regional Hospitality Manager"]
        },
        "skills": ["Customer Service", "Event Planning", "Booking Systems (Opera)", "Food & Beverage Management", "Budgeting"]
    },
    "Real Estate": {
        "company_names": ["Keystone Properties", "Metropolis Real Estate", "Horizon Realty", "AssetMax Commercial"],
        "job_titles": {
            "entry": ["Real Estate Assistant", "Leasing Agent", "Showing Agent"],
            "mid": ["Real Estate Agent", "Property Manager", "Transaction Coordinator"],
            "senior": ["Broker-Owner", "Senior Property Manager", "Real Estate Investor"]
        },
        "skills": ["Property Management", "Real Estate Law", "MLS Systems", "Contract Negotiation", "Client Relations"]
    },
    "Media & Entertainment": {
        "company_names": ["Starlight Studios", "Vortex Media Group", "Echo Broadcasting", "PixelFrame Animation"],
        "job_titles": {
            "entry": ["Production Assistant", "Junior Editor", "Social Media Coordinator"],
            "mid": ["Video Editor", "Producer", "Journalist", "Graphic Designer"],
            "senior": ["Executive Producer", "Creative Director", "Head of Content"]
        },
        "skills": ["Adobe Premiere Pro", "Final Cut Pro", "After Effects", "Content Strategy", "Storytelling", "Digital Media"]
    }
}
UNIVERSITIES = ["State University", "Metropolis University", "Northwood College", "Crestview Institute", "Oak Valley University"]
DEGREES = ["Bachelor of Science", "Bachelor of Arts", "Master of Business Administration", "Master of Science"]


# --- HELPER FUNCTIONS ---
def get_job_title(industry, years_exp):
    if years_exp <= 3: level = "entry"
    elif 4 <= years_exp <= 9: level = "mid"
    else: level = "senior"
    return random.choice(INDUSTRY_DATA[industry]["job_titles"][level])

def wrap_text(c, text, x, y, max_width, line_height, font, size):
    c.setFont(font, size)
    lines = []
    words = text.split()
    if not words: return y
    current_line = words[0]
    for word in words[1:]:
        if c.stringWidth(f"{current_line} {word}", font, size) < max_width:
            current_line += f" {word}"
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    for line in lines:
        c.drawString(x, y, line)
        y -= line_height
    return y

# --- TEMPLATE 1: CLASSIC PROFESSIONAL ---
def create_classic_template(c, data):
    width, height = letter
    # Name & Contact
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2.0, height - 1 * inch, data["name"])
    c.setFont("Helvetica", 10)
    contact_info = f'{data["address"]} | {data["phone"]} | {data["email"]}'
    c.drawCentredString(width / 2.0, height - 1.25 * inch, contact_info)
    y_pos = height - 1.75 * inch

    # Sections
    for section in ["summary", "experience", "education", "skills"]:
        if not data.get(section): continue
        
        c.setFont("Helvetica-Bold", 14)
        title = data[f"{section}_title"] if f"{section}_title" in data else section.replace("_", " ").title()
        c.drawString(1 * inch, y_pos, title)
        c.line(1 * inch, y_pos - 0.05 * inch, width - 1 * inch, y_pos - 0.05 * inch)
        y_pos -= 0.3 * inch

        if section == "summary":
            y_pos = wrap_text(c, data["summary_text"], 1 * inch, y_pos, width - 2 * inch, 14, "Helvetica", 10)
        elif section == "skills":
            skills_text = ", ".join(data["skills"])
            y_pos = wrap_text(c, skills_text, 1 * inch, y_pos, width - 2 * inch, 14, "Helvetica", 10)
        elif section == "education":
            edu = data["education"]
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1 * inch, y_pos, edu["university"])
            c.setFont("Helvetica-Oblique", 11)
            c.drawRightString(width - 1 * inch, y_pos, f'Graduated: {edu["grad_year"]}')
            y_pos -= 0.2 * inch
            c.setFont("Helvetica", 11)
            c.drawString(1 * inch, y_pos, edu["degree"])
        elif section == "experience":
            for job in data["experience"]:
                c.setFont("Helvetica-Bold", 11)
                c.drawString(1 * inch, y_pos, job["title"])
                c.setFont("Helvetica-Oblique", 11)
                c.drawRightString(width - 1 * inch, y_pos, job["dates"])
                y_pos -= 0.2 * inch
                c.setFont("Helvetica", 11)
                c.drawString(1 * inch, y_pos, job["company"])
                y_pos -= 0.25 * inch
                for bullet in job["description"]:
                    y_pos = wrap_text(c, f"• {bullet}", 1.2 * inch, y_pos, width - 2.4 * inch, 14, "Helvetica", 10)
                y_pos -= 0.1 * inch
        y_pos -= 0.25 * inch

# --- TEMPLATE 2: MODERN WITH COLOR ---
def create_modern_template(c, data):
    width, height = letter
    c.setFillColor(colors.black)
    
    # Name & Contact
    c.setFont("Helvetica-Bold", 28)
    c.drawString(1 * inch, height - 1 * inch, data["name"])
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 1.25 * inch, f'{data["email"]} | {data["phone"]}')
    c.drawString(1 * inch, height - 1.4 * inch, data["address"])
    y_pos = height - 2 * inch
    
    # Sections
    for section in ["summary", "experience", "education", "skills"]:
        if not data.get(section): continue
        
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(MODERN_BLUE)
        title = data[f"{section}_title"] if f"{section}_title" in data else section.replace("_", " ").title()
        c.drawString(1 * inch, y_pos, title)
        c.setStrokeColor(MODERN_BLUE)
        c.setLineWidth(2)
        c.line(1 * inch, y_pos - 0.1 * inch, 3 * inch, y_pos - 0.1 * inch)
        c.setFillColor(colors.black)
        y_pos -= 0.35 * inch

        # Logic for drawing content is similar to classic, just different styling
        if section == "summary":
            y_pos = wrap_text(c, data["summary_text"], 1 * inch, y_pos, width - 2 * inch, 15, "Helvetica", 10)
        elif section == "skills":
            skills_text = ", ".join(data["skills"])
            y_pos = wrap_text(c, skills_text, 1 * inch, y_pos, width - 2 * inch, 15, "Helvetica", 10)
        elif section == "education":
            edu = data["education"]
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1 * inch, y_pos, edu["university"])
            c.setFont("Helvetica", 10)
            c.drawRightString(width - 1 * inch, y_pos, f'Graduated: {edu["grad_year"]}')
            y_pos -= 0.2 * inch
            c.setFont("Helvetica-Oblique", 11)
            c.drawString(1 * inch, y_pos, edu["degree"])
        elif section == "experience":
            for job in data["experience"]:
                c.setFont("Helvetica-Bold", 11)
                c.drawString(1 * inch, y_pos, job["title"])
                c.setFont("Helvetica", 10)
                c.drawRightString(width - 1 * inch, y_pos, job["dates"])
                y_pos -= 0.2 * inch
                c.setFont("Helvetica-Oblique", 11)
                c.drawString(1 * inch, y_pos, job["company"])
                y_pos -= 0.25 * inch
                for bullet in job["description"]:
                    y_pos = wrap_text(c, f"• {bullet}", 1.2 * inch, y_pos, width - 2.4 * inch, 14, "Helvetica", 10)
                y_pos -= 0.1 * inch
        y_pos -= 0.25 * inch

# --- TEMPLATE 3: SIDEBAR LAYOUT ---
def create_sidebar_template(c, data):
    width, height = letter
    sidebar_width = 2.5 * inch
    main_margin = 0.5 * inch
    
    # Draw Sidebar
    c.setFillColor(SIDEBAR_GRAY)
    c.rect(0, 0, sidebar_width, height, stroke=0, fill=1)
    
    # --- Sidebar Content ---
    c.setFillColor(colors.white)
    y_pos_side = height - 1 * inch
    
    # Name
    c.setFont("Helvetica-Bold", 20)
    y_pos_side = wrap_text(c, data["name"], main_margin, y_pos_side, sidebar_width - 1 * inch, 22, "Helvetica-Bold", 18)
    y_pos_side -= 0.5 * inch
    
    # Contact
    c.setFont("Helvetica-Bold", 11)
    c.drawString(main_margin, y_pos_side, "Contact")
    c.line(main_margin, y_pos_side - 0.05 * inch, sidebar_width - main_margin, y_pos_side - 0.05 * inch)
    y_pos_side -= 0.25 * inch
    c.setFont("Helvetica", 9)
    y_pos_side = wrap_text(c, data["email"], main_margin, y_pos_side, sidebar_width - 1*inch, 12, "Helvetica", 9)
    y_pos_side = wrap_text(c, data["phone"], main_margin, y_pos_side, sidebar_width - 1*inch, 12, "Helvetica", 9)
    y_pos_side = wrap_text(c, data["address"], main_margin, y_pos_side, sidebar_width - 1*inch, 12, "Helvetica", 9)
    y_pos_side -= 0.4 * inch

    # Skills
    c.setFont("Helvetica-Bold", 11)
    c.drawString(main_margin, y_pos_side, "Skills")
    c.line(main_margin, y_pos_side - 0.05 * inch, sidebar_width - main_margin, y_pos_side - 0.05 * inch)
    y_pos_side -= 0.25 * inch
    c.setFont("Helvetica", 9)
    for skill in data["skills"]:
        y_pos_side = wrap_text(c, f"• {skill}", main_margin, y_pos_side, sidebar_width - 1*inch, 12, "Helvetica", 9)
        
    # --- Main Content ---
    c.setFillColor(colors.black)
    y_pos_main = height - 1 * inch
    main_x = sidebar_width + main_margin
    main_width = width - main_x - main_margin

    # Summary
    c.setFont("Helvetica-Bold", 14)
    c.drawString(main_x, y_pos_main, data["summary_title"])
    y_pos_main -= 0.25 * inch
    y_pos_main = wrap_text(c, data["summary_text"], main_x, y_pos_main, main_width, 15, "Helvetica", 10)
    y_pos_main -= 0.25 * inch

    # Experience
    if data["experience"]:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(main_x, y_pos_main, "Work Experience")
        y_pos_main -= 0.25 * inch
        for job in data["experience"]:
            c.setFont("Helvetica-Bold", 11)
            c.drawString(main_x, y_pos_main, job["title"])
            c.setFont("Helvetica-Oblique", 10)
            c.drawRightString(width - main_margin, y_pos_main, job["dates"])
            y_pos_main -= 0.2 * inch
            c.setFont("Helvetica", 10)
            c.drawString(main_x, y_pos_main, job["company"])
            y_pos_main -= 0.25 * inch
            for bullet in job["description"]:
                y_pos_main = wrap_text(c, f"• {bullet}", main_x + 0.2*inch, y_pos_main, main_width - 0.4*inch, 14, "Helvetica", 10)
            y_pos_main -= 0.1 * inch

    # Education
    c.setFont("Helvetica-Bold", 14)
    c.drawString(main_x, y_pos_main, "Education")
    y_pos_main -= 0.25 * inch
    edu = data["education"]
    c.setFont("Helvetica-Bold", 11)
    c.drawString(main_x, y_pos_main, edu["university"])
    c.setFont("Helvetica-Oblique", 10)
    c.drawRightString(width - main_margin, y_pos_main, f'Graduated: {edu["grad_year"]}')
    y_pos_main -= 0.2 * inch
    c.setFont("Helvetica", 10)
    c.drawString(main_x, y_pos_main, edu["degree"])

# --- PDF Creation Wrapper ---
def create_resume_pdf(resume_data, file_path, template_choice):
    c = canvas.Canvas(file_path, pagesize=letter)
    if template_choice == 'classic':
        create_classic_template(c, resume_data)
    elif template_choice == 'modern':
        create_modern_template(c, resume_data)
    elif template_choice == 'sidebar':
        create_sidebar_template(c, resume_data)
    c.save()

# --- MAIN GENERATION LOGIC ---
if __name__ == "__main__":
    fake = Faker()

    # --- START: FOLDER CLEANUP UTILITY ---
    # If the output folder exists, remove it and all its contents
    if os.path.exists(OUTPUT_FOLDER):
        print(f"Removing existing directory: {OUTPUT_FOLDER}")
        shutil.rmtree(OUTPUT_FOLDER)
    # --- END: FOLDER CLEANUP UTILITY ---

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # <--- ADDED: Initialize a dictionary to hold all ground truth data
    all_groundtruth_data = {}

    print(f"Generating {NUMBER_OF_RESUMES} resumes with random templates...")

    for i in range(NUMBER_OF_RESUMES):
        years_of_experience = random.randint(0, 15)
        industry = random.choice(list(INDUSTRY_DATA.keys()))
        
        name = fake.name()
        if years_of_experience < 2:
            summary_title, summary_text = "Objective", f"Highly motivated individual seeking an entry-level position in the {industry} industry."
        else:
            summary_title, summary_text = "Professional Summary", f"Experienced {get_job_title(industry, years_of_experience)} with {years_of_experience} years of experience in the {industry} sector."

        experience = []
        current_year = datetime.now().year
        end_year = current_year
        if years_of_experience > 0:
            num_jobs = min(3, (years_of_experience + 2) // 4)
            exp_left = years_of_experience
            for j in range(num_jobs):
                job_duration = random.randint(2, max(3, exp_left // (num_jobs-j if num_jobs-j > 0 else 1)))
                start_year = end_year - job_duration
                experience.append({
                    "title": get_job_title(industry, max(1, exp_left)),
                    "company": random.choice(INDUSTRY_DATA[industry]["company_names"]),
                    "dates": f"{start_year} - {end_year if j > 0 else 'Present'}",
                    "description": [fake.bs() + "." for _ in range(random.randint(2, 4))]
                })
                end_year = start_year - 1
                exp_left -= job_duration

        education = {
            "university": random.choice(UNIVERSITIES),
            "degree": random.choice(DEGREES),
            "grad_year": current_year - years_of_experience - random.randint(1, 2)
        }
        
        num_skills = random.randint(5, 8)
        skills = random.sample(INDUSTRY_DATA[industry]["skills"], min(num_skills, len(INDUSTRY_DATA[industry]["skills"])))

        resume_data = {
            "name": name, "address": fake.address().replace("\n", ", "), "phone": fake.phone_number(),
            "email": f'{name.lower().replace(" ", ".")}@example.com', "summary_title": summary_title,
            "summary_text": summary_text, "experience": experience, "education": education, "skills": skills,
        }
        
        # Randomly choose a template
        template_choice = random.choice(['classic', 'modern', 'sidebar'])
        
        file_name = f"resume_{name.replace(' ', '_')}.pdf"
        file_path = os.path.join(OUTPUT_FOLDER, file_name)
        create_resume_pdf(resume_data, file_path, template_choice)
        
        # <--- ADDED: Structure and store the ground truth data for this resume
        groundtruth_entry = {
            "template_used": template_choice,
            "contact_info": {
                "name": resume_data["name"],
                "email": resume_data["email"],
                "phone": resume_data["phone"],
                "address": resume_data["address"]
            },
            "summary": resume_data["summary_text"],
            "work_experience": resume_data["experience"],
            "education": {
                "institution": resume_data["education"]["university"],
                "degree": resume_data["education"]["degree"],
                "graduation_year": resume_data["education"]["grad_year"]
            },
            "skills": resume_data["skills"]
        }
        all_groundtruth_data[file_name] = groundtruth_entry
        # --- END ADDED SECTION ---

        print(f"({i+1}/{NUMBER_OF_RESUMES}) Created: {file_name} (Template: {template_choice})")
    
    # <--- ADDED: Write the collected ground truth data to a single JSON file
    groundtruth_filepath = os.path.join(OUTPUT_FOLDER, "groundtruth.json")
    with open(groundtruth_filepath, "w") as f:
        json.dump(all_groundtruth_data, f, indent=4)
    # --- END ADDED SECTION ---

    print(f"\nSuccessfully generated {NUMBER_OF_RESUMES} resumes in the '{OUTPUT_FOLDER}' folder.")
    print(f"Ground truth data saved to '{groundtruth_filepath}'") # <--- ADDED: Confirmation message