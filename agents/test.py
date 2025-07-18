import os
import json
import re
from csi_agents.problem_statement import generate_problem_statements_from_agent, read_problem_from_file
from csi_agents.sponsors import find_sponsors_for_problem, find_sponsors_and_send_emails
from csi_agents.marketing_agent import generate_marketing_content, parse_sections

# Folder to store all events
HACKATHON_FOLDER = "hackathons"

def save_hackathon(event_id, data):
    os.makedirs(HACKATHON_FOLDER, exist_ok=True)
    file_path = os.path.join(HACKATHON_FOLDER, f"{event_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"\n💾 Hackathon data saved to {file_path}")

def automate_hackathon_management():
    print("\n🚀 Hackathon Setup Automation Started\n")

    # STEP 1: Problem Selection
    print("📋 Step 1: Select or Generate Problem Statement\n")
    choice = input("1 - Read from file\n2 - Generate new problems\nChoose (1 or 2): ").strip()

    problem_text = ""

    if choice == "1":
        file_path = input("Enter the file path to your problem statement: ").strip()
        problem_text = read_problem_from_file(file_path)
    elif choice == "2":
        domain = input("Enter a specific domain (optional, press Enter to skip): ").strip()
        problems_text = generate_problem_statements_from_agent(domain)

        problems = problems_text.split('---')
        problems = [p.strip() for p in problems if p.strip()]

        print("\nAvailable Problems:")
        for idx, prob in enumerate(problems):
            print(f"\nProblem {idx+1}:\n{prob}")

        selected = int(input("\nSelect a problem (1/2/3/4/5): ").strip())
        if selected < 1 or selected > len(problems):
            print("❌ Invalid selection. Exiting.")
            return

        problem_text = problems[selected - 1]
    else:
        print("❌ Invalid choice. Exiting.")
        return

    print("\n✅ Problem Statement Selected Successfully.\n")

    # STEP 2: Find Sponsors
    print("🏢 Step 2: Finding Potential Sponsors...\n")
    sponsor_emails_text = find_sponsors_for_problem(problem_text)
    sponsor_emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", sponsor_emails_text)

    if not sponsor_emails:
        print("⚠️ Warning: No sponsors found!")
    else:
        print(f"✅ Found {len(sponsor_emails)} potential sponsors.")

    # Send Sponsor Emails (optional)
    send_now = input("\nDo you want to send sponsorship emails now? (yes/no): ").strip().lower()
    if send_now == "yes":
        from_email = input("\nEnter your sending email (example@gmail.com): ").strip()
        from_password = input("Enter your email password or App Password: ").strip()
        event_date_placeholder = "TBD"  # We haven't confirmed event date yet
        find_sponsors_and_send_emails(problem_text, from_email, from_password, event_date_placeholder)
    else:
        print("📨 Skipped sending sponsor emails for now.")

    # STEP 3: Confirm Event Details
    print("\n🎯 Step 3: Confirm Event Details\n")
    event_name = input("Enter Event Name (e.g., Hack the Hackathon): ").strip()
    event_dates = input("Enter Event Dates (e.g., April 25–27, 2025): ").strip()
    event_location = input("Enter Event Location (e.g., CSI Building, UWM): ").strip()

    event_id = event_name.lower().replace(" ", "_") + "_" + event_dates.split()[0]

    # STEP 4: Generate Marketing Content
    print("\n🎨 Step 4: Generate Marketing Materials\n")
    audience = input("Enter Target Audience (e.g., Students, Faculty, Sponsors): ").strip()
    highlights = input("Enter Key Highlights (e.g., Prizes, Workshops, Networking): ").strip()
    tone_style = input("Enter Tone and Style (e.g., Energetic for Students, Professional for Sponsors): ").strip()

    marketing_content = generate_marketing_content(
        event_name, event_dates, event_location, audience, highlights, tone_style
    )

    marketing_sections = parse_sections(marketing_content)

    # STEP 5: Save all together
    hackathon_data = {
        "event_id": event_id,
        "event_name": event_name,
        "event_dates": event_dates,
        "event_location": event_location,
        "problem_statement": problem_text,
        "sponsors": sponsor_emails,
        "marketing_materials": {
            "poster_description": marketing_sections.get("### Section 1: Event Poster Description", ""),
            "email_templates": marketing_sections.get("### Section 2: Email Templates", ""),
            "social_media_posts": marketing_sections.get("### Section 3: Social Media Posts", ""),
            "poster_slogans": marketing_sections.get("### Section 4: Poster Slogans", ""),
            "audience_segmentation": marketing_sections.get("### Section 5: Audience Segmentation", ""),
            "posting_calendar": marketing_sections.get("### Section 6: Posting Calendar", "")
        },
        "logistics_summary": None,
        "catering_email_sent": False
    }

    save_hackathon(event_id, hackathon_data)

    print("\n✅ Hackathon Setup Successfully Completed!\n")
    print("You can now proceed to logistics, registration, and other flows later.")

if __name__ == "__main__":
    automate_hackathon_management()
