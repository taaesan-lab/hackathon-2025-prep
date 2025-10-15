import os
import shutil
import csv
import random
from datetime import datetime, timedelta
from faker import Faker

# --- CONFIGURATION ---
NUMBER_OF_FILES = 100
LINES_PER_FILE = 200
OUTPUT_FOLDER = "out/06_tickets"

# --- DATA FOR REALISM ---
# Pre-define issue templates for more realistic tickets
ISSUE_TEMPLATES = {
    "Software": {
        "subjects": ["Outlook Crashing", "Excel Formula Error", "Cannot Install Application", "Software License Expired"],
        "descriptions": [
            "Every time I open Outlook, it crashes after a few seconds. I've already tried restarting my computer.",
            "My VLOOKUP formula in the attached spreadsheet is returning an #N/A error, but the data seems correct.",
            "I'm trying to install Adobe Reader, but I'm getting a permissions error. My user is {employee_name}.",
            "I received a notification that my license for Microsoft Visio has expired. I need it for my project."
        ]
    },
    "Hardware": {
        "subjects": ["Monitor Not Working", "Laptop Battery Draining Fast", "Docking Station Issue", "Broken Keyboard Key"],
        "descriptions": [
            "My second monitor is not being detected. I've checked the cables and they seem to be connected properly.",
            "The battery on my Dell laptop (Asset: {asset_tag}) is draining from 100% to 20% in under an hour.",
            "The USB ports on my docking station are not working. The displays are fine, but my mouse and keyboard don't connect.",
            "The 'S' key on my keyboard is stuck and not working correctly. It makes typing very difficult."
        ]
    },
    "Network": {
        "subjects": ["Slow WiFi Connection", "Cannot Connect to VPN", "Unable to Access Shared Drive", "Firewall Blocking Site"],
        "descriptions": [
            "The WiFi in the conference room on the 3rd floor is extremely slow and keeps disconnecting.",
            "I am working from home and the VPN client fails to connect. The error code is 789-A.",
            # --- THIS IS THE FIXED LINE ---
            r"I can't access the 'Marketing' shared drive (\\fileserver\marketing). It says my access is denied.",
            "I need to access www.analytics-example.com for my work, but it appears to be blocked by the company firewall."
        ]
    },
    "Account": {
        "subjects": ["Password Reset Needed", "Locked Out of Salesforce", "Request for New Software Account", "Permission Change Request"],
        "descriptions": [
            "I have forgotten my Windows password and need it to be reset. My username is {employee_username}.",
            "I'm locked out of my Salesforce account after too many failed login attempts.",
            "My team needs access to the Miro whiteboard software. Please create accounts for me and my colleagues.",
            "I need read/write access to the 'Project_Alpha' folder on the shared drive for my new assignment."
        ]
    }
}

# Pre-generate a list of employees to make the data more consistent
fake = Faker()
EMPLOYEES = []
for _ in range(150): # A pool of 150 employees
    name = fake.name()
    EMPLOYEES.append({
        "name": name,
        "email": f'{name.lower().replace(" ", ".")}@examplecorp.com',
        "username": f'{name.split()[0][0].lower()}{name.split()[-1].lower()}'
    })


# --- MAIN SCRIPT ---
if __name__ == "__main__":

    # --- START: FOLDER CLEANUP UTILITY ---
    # If the output folder exists, remove it and all its contents
    if os.path.exists(OUTPUT_FOLDER):
        print(f"Removing existing directory: {OUTPUT_FOLDER}")
        shutil.rmtree(OUTPUT_FOLDER)
    # --- END: FOLDER CLEANUP UTILITY ---

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # Global ticket counter to ensure unique IDs across all files
    ticket_id_counter = 1
    
    print(f"Starting generation of {NUMBER_OF_FILES} files...")

    for i in range(1, NUMBER_OF_FILES + 1):
        file_name = f"it_support_tickets_{i:03d}.csv"
        file_path = os.path.join(OUTPUT_FOLDER, file_name)

        with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            
            # Write the header row
            writer.writerow(['ticket_id', 'timestamp', 'employee_name', 'employee_email', 'subject', 'description', 'urgency', 'status'])

            for j in range(LINES_PER_FILE):
                # 1. Select a random employee
                employee = random.choice(EMPLOYEES)
                
                # 2. Select a random issue type and its templates
                issue_category = random.choice(list(ISSUE_TEMPLATES.keys()))
                subject_template = random.choice(ISSUE_TEMPLATES[issue_category]["subjects"])
                desc_template = random.choice(ISSUE_TEMPLATES[issue_category]["descriptions"])
                
                # 3. Populate templates with specific details
                description = desc_template.format(
                    employee_name=employee["name"],
                    employee_username=employee["username"],
                    asset_tag=f"LT-{random.randint(1000, 9999)}"
                )

                # 4. Generate other data points
                timestamp = (datetime.now() - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))).isoformat() + "Z"
                urgency = random.choices(['Low', 'Medium', 'High', 'Critical'], weights=[40, 40, 15, 5], k=1)[0]
                status = random.choices(['Closed', 'Open', 'In Progress'], weights=[70, 20, 10], k=1)[0]
                
                # 5. Write the ticket to the CSV file
                writer.writerow([
                    f"TIX-{ticket_id_counter:06d}",
                    timestamp,
                    employee["name"],
                    employee["email"],
                    subject_template,
                    description,
                    urgency,
                    status
                ])
                
                ticket_id_counter += 1
        
        print(f"  ({i}/{NUMBER_OF_FILES}) Successfully created file: {file_name}")

    print(f"\nGeneration complete. {NUMBER_OF_FILES} files with {LINES_PER_FILE} tickets each are in the '{OUTPUT_FOLDER}' folder.")