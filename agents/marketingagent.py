import os
import requests
import urllib.request
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import smtplib
from email.mime.text import MIMEText
import json
import re

# Connect to Azure AI Project
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str="westus3.api.azureml.ms;c5d47662-af4d-400e-ace6-ff70828d7d98;az-csi-grp1;agents"
)

marketing_agent_id = "asst_EQ6jMEjhLeOcfNfYJoxCg8oL"  # <-- Replace if different

# Function to generate marketing content
def generate_marketing_content(event_name, dates, location, audience, highlights, tone_style):
    thread = project_client.agents.create_thread()

    input_message = f"""
Inputs:
Event Name: {event_name}
Dates: {dates}
Location: {location}
Audience: {audience}
Key Highlights: {highlights}
Tone and Style: {tone_style}

Please generate full marketing materials accordingly.
"""

    project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=input_message
    )

    run = project_client.agents.create_and_process_run(
        thread_id=thread.id,
        agent_id=marketing_agent_id
    )

    messages = project_client.agents.list_messages(thread_id=thread.id)

    return messages.text_messages[0].text["value"]

# Function to parse sections
def parse_sections(content):
    sections = {}
    current_section = None
    for line in content.splitlines():
        # Better matching: check if line startswith ### Section
        if line.strip().lower().startswith("### section"):
            current_section = line.strip()
            sections[current_section] = ""
        elif current_section:
            sections[current_section] += line + "\n"
    return sections


# Function to save sections into files
def save_sections(sections):
    os.makedirs("generated_content", exist_ok=True)

    mapping = {
        "section 1": "poster_description.txt",
        "section 2": "emails.txt",
        "section 3": "social_posts.txt",
        "section 4": "poster_slogans.txt",
        "section 5": "audience_segmentation.txt",
        "section 6": "posting_calendar.txt",
    }

    for section_name, file_name in mapping.items():
        for key in sections:
            if section_name in key.lower():
                with open(f"generated_content/{file_name}", "w", encoding="utf-8") as f:
                    f.write(sections[key].strip())
                print(f"✅ Saved {file_name}")
                
def format_markdown_to_html(text):
    html = text
    
    # Replace **bold**
    html = html.replace("**", "<b>").replace("</b><b>", "")  # fix double bolds

    # Replace bullet points (- something) with <ul><li>something</li></ul>
    lines = html.splitlines()
    html_lines = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            item = stripped[2:].strip()
            html_lines.append(f"<li>{item}</li>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(line + "<br>")  # Add line break manually
    
    if in_list:
        html_lines.append("</ul>")

    final_html = "\n".join(html_lines)
    return f"<html><body>{final_html}</body></html>"

# Function to generate poster images
def generate_poster_images(poster_prompt_text):
    endpoint = "https://kuruv-m9ynxl8q-swedencentral.services.ai.azure.com/openai/deployments/dall-e-3/images/generations?api-version=2023-12-01-preview"
    api_key = "CfD4xpPE7BHCy390wncyeHBSOyp4ukgTY2KdJj5Z4OBP6nfRri90JQQJ99BDACfhMk5XJ3w3AAAAACOGUzDo"

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    payload = {
        "prompt": poster_prompt_text,
        "n": 1,  # generate 3 images
        "size": "1024x1024"
    }

    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code == 200:
        os.makedirs("generated_content/posters", exist_ok=True)
        response_data = response.json()
        for idx, img in enumerate(response_data["data"]):
            img_url = img["url"]
            local_filename = f"generated_content/posters/poster_{idx+1}.png"
            urllib.request.urlretrieve(img_url, local_filename)
            print(f"✅ Saved Poster {idx+1}: {local_filename}")
    else:
        print(f"❌ Poster generation failed: {response.status_code}")
        print(response.text)
        
        
def parse_participant_emails(section7_text):
    participants = []
    for line in section7_text.strip().splitlines():
        line = line.strip()
        if line.startswith("-"):
            parts = line.lstrip("-").strip().split(",", 1)
            if len(parts) == 2:
                name = parts[0].strip()
                email = parts[1].strip()

                # 🛡️ Fix: Remove any garbage after the email (like spaces, 【, etc.)
                email = re.split(r'\s|【', email)[0].strip()

                participants.append({"Name": name, "Email": email})
    return participants


def send_emails_to_participants_from_list(email_subject, email_template, participants):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "kindrasena8@gmail.com"  # your real email
    sender_password = "sdecbbhtntaqoysp"     # app password (never share real password)

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    for participant in participants:
        recipient_email = participant["Email"]
        recipient_name = participant["Name"].split()[0]  # Use first name only

        personalized_email = (email_template
                      .replace("[Student's First Name]", recipient_name)
                      .replace("[Student Name]", recipient_name)
                      .replace("[Name]", recipient_name)
                      .replace("[Your Name]", "Hackathon Team"))

        formatted_html = format_markdown_to_html(personalized_email)
        msg = MIMEText(formatted_html, "html")
        msg["Subject"] = email_subject
        msg["From"] = sender_email
        msg["To"] = recipient_email

        server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"✅ Email sent to {recipient_name} ({recipient_email})")

    server.quit()
# Main Runner
if __name__ == "__main__":
    print("\n📢 Please Enter Hackathon/Event Details:\n")

    # Take dynamic input from user
    event_name = input("Enter Event Name: ").strip()
    dates = input("Enter Event Dates (e.g., April 25–27, 2025): ").strip()
    location = input("Enter Event Location: ").strip()
    audience = input("Enter Target Audience (e.g., Students, Faculty, Sponsors): ").strip()
    highlights = input("Enter Key Highlights (e.g., Prizes, Workshops, Networking): ").strip()
    tone_style = input("Enter Tone and Style (e.g., Energetic for Students, Professional for Sponsors): ").strip()

    # Step 1: Generate marketing content
    full_content = generate_marketing_content(event_name, dates, location, audience, highlights, tone_style)
    print("\n====== Full Generated Marketing Content ======\n")
    print(full_content)

    # Step 2: Parse sections
    sections = parse_sections(full_content)

    # Step 3: Save each section into separate file
    save_sections(sections)

    # Step 4: Generate poster images from Section 1
    poster_section_key = None
    for key in sections:
        if "poster description" in key.lower():
            poster_section_key = key
            break

    poster_prompt = None

    if poster_section_key:
    # Clean the raw poster description
        raw_poster_text = sections[poster_section_key].strip()

    # 🧠 Try to extract event details
        import re

        event_match = re.search(r'\*\*Event\*\*:\s*(.*)', raw_poster_text)
        dates_match = re.search(r'\*\*Dates\*\*:\s*(.*)', raw_poster_text)
        location_match = re.search(r'\*\*Location\*\*:\s*(.*)', raw_poster_text)
        tagline_match = re.search(r'\*\*Tagline\*\*:\s*(.*)', raw_poster_text)

        event_name_extracted = event_match.group(1).strip() if event_match else ""
        event_dates_extracted = dates_match.group(1).strip() if dates_match else ""
        event_location_extracted = location_match.group(1).strip() if location_match else ""
        tagline_extracted = tagline_match.group(1).strip() if tagline_match else ""

        if event_name_extracted:
            poster_prompt = f"""
Create a vibrant event poster for "{event_name_extracted}".
The event is happening at "{event_location_extracted}" on {event_dates_extracted}.
Theme: {tagline_extracted}.
Include visuals of students coding, workshops, prizes, networking.
Use bright and inspiring colors.
Focus on energy, innovation, and technology.
"""
        else:
            print("⚠️ Section 1 exists but parsing failed, fallback to basic poster.")

# 🛡️ If no Section 1 found or parsing failed, fallback to simple prompt
    if not poster_prompt:
        print("⚠️ No Poster Description found. Using fallback basic poster prompt.")
        poster_prompt = f"""
Create a colorful hackathon poster for the event "{event_name}".
It will be held at "{location}" from {dates}.
Focus on themes of prizes, workshops, mentorship, networking, and energy.
Make it exciting, futuristic, and student-focused.
"""

# ✅ Now always generate posters!
    print("\n🎯 Sending this poster prompt for image generation:\n")
    print(poster_prompt)

    generate_poster_images(poster_prompt)
    
    student_email_section = ""
    for key in sections:
        if "section 2" in key.lower() and "email" in key.lower():
            student_email_section = sections[key]
            break


    # Extract only Student Email Template
    # 🧠 Step 5: Extract Student Email Template ONLY
    student_email_text = ""
    inside_student_email = False

    for line in student_email_section.splitlines():
        if "**Student Email Template" in line:
            inside_student_email = True
            continue
        if inside_student_email:
            if "**Faculty Email Template" in line or "**Sponsor Email Template" in line or line.strip() == "---":
                break
            student_email_text += line + "\n"
            

    if student_email_text:
        # Extract Subject and Body
        lines = student_email_text.strip().split("\n")
        subject_line = ""
        body_lines = []

        for l in lines:
            if "subject" in l.lower():
                parts = l.split(":", 1)
                if len(parts) > 1:
                    subject_line = parts[1].strip()
            else:
                body_lines.append(l)

        email_subject = subject_line
        email_body = "\n".join(body_lines).strip()

        # 🧠 Step 6: Parse Participants from Section 7
        participant_emails_text = ""
        for key in sections:
            if "section 7" in key.lower() and "participant" in key.lower():
                participant_emails_text = sections[key]
                break

        participants = parse_participant_emails(participant_emails_text)

        # 🧠 Step 7: Send Emails
        print("\n📬 Sending emails to participants...\n")
        send_emails_to_participants_from_list(email_subject, email_body, participants)

    else:
        print("⚠️ No Student Email Template found. Skipping email sending.")
