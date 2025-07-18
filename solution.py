import os
import json
import re
from agents.problem_statement import generate_problem_statements_from_agent, read_problem_from_file
from agents.sponsors import find_sponsors_for_problem, find_sponsors_and_send_emails
from agents.marketingagent import generate_marketing_content, parse_sections, save_sections, generate_poster_images, parse_participant_emails, send_emails_to_participants_from_list

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

    send_now = input("\nDo you want to send sponsorship emails now? (yes/no): ").strip().lower()
    if send_now == "yes":
        from_email = input("\nEnter your sending email (example@gmail.com): ").strip()
        from_password = input("Enter your email password or App Password: ").strip()
        event_date_placeholder = "TBD"  # Event date not confirmed yet
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

    full_marketing_content = generate_marketing_content(
        event_name, event_dates, event_location, audience, highlights, tone_style
    )
    sections = parse_sections(full_marketing_content)

    # Save individual files
    save_sections(sections)

    # Generate Poster
    poster_section_key = None
    for key in sections:
        if "poster description" in key.lower():
            poster_section_key = key
            break

    if poster_section_key:
        raw_poster_text = sections[poster_section_key].strip()
        event_match = re.search(r'\*\*Event\*\*:\s*(.*)', raw_poster_text)
        dates_match = re.search(r'\*\*Dates\*\*:\s*(.*)', raw_poster_text)
        location_match = re.search(r'\*\*Location\*\*:\s*(.*)', raw_poster_text)
        tagline_match = re.search(r'\*\*Tagline\*\*:\s*(.*)', raw_poster_text)

        event_name_extracted = event_match.group(1).strip() if event_match else event_name
        event_dates_extracted = dates_match.group(1).strip() if dates_match else event_dates
        event_location_extracted = location_match.group(1).strip() if location_match else event_location
        tagline_extracted = tagline_match.group(1).strip() if tagline_match else "Join Us!"

        poster_prompt = f"""
Create a vibrant event poster for "{event_name_extracted}".
The event is happening at "{event_location_extracted}" on {event_dates_extracted}.
Theme: {tagline_extracted}.
Include visuals of students coding, workshops, prizes, networking.
Use bright and inspiring colors.
Focus on energy, innovation, and technology.
"""
        print("\n🎯 Generating Poster Image...\n")
        generate_poster_images(poster_prompt)

    else:
        print("⚠️ No poster description section found. Skipping poster image generation.")

    # STEP 5: Optionally send participant emails
    participant_email_section = None
    for key in sections:
        if "section 7" in key.lower() and "participant" in key.lower():
            participant_email_section = sections[key]
            break

    if participant_email_section:
        participants = parse_participant_emails(participant_email_section)

        student_email_section = None
        for key in sections:
            if "section 2" in key.lower() and "email" in key.lower():
                student_email_section = sections[key]
                break

        if student_email_section:
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
                subject_line = ""
                body_lines = []
                for l in student_email_text.strip().split("\n"):
                    if "subject" in l.lower():
                        parts = l.split(":", 1)
                        if len(parts) > 1:
                            subject_line = parts[1].strip()
                    else:
                        body_lines.append(l)

                email_subject = subject_line
                email_body = "\n".join(body_lines).strip()

                print("\n📬 Sending participant invitation emails...\n")
                send_emails_to_participants_from_list(email_subject, email_body, participants)

    else:
        print("\n⚠️ No participants found in Section 7. Skipping email sending.")

    # Final Save
    hackathon_data = {
        "event_id": event_id,
        "event_name": event_name,
        "event_dates": event_dates,
        "event_location": event_location,
        "problem_statement": problem_text,
        "sponsors": sponsor_emails,
        "marketing_materials": {
            "poster_description": sections.get("### Section 1: Event Poster Description", ""),
            "email_templates": sections.get("### Section 2: Email Templates", ""),
            "social_media_posts": sections.get("### Section 3: Social Media Posts", ""),
            "poster_slogans": sections.get("### Section 4: Poster Slogans", ""),
            "audience_segmentation": sections.get("### Section 5: Audience Segmentation", ""),
            "posting_calendar": sections.get("### Section 6: Posting Calendar", "")
        },
        "logistics_summary": None,
        "catering_email_sent": False
    }

    save_hackathon(event_id, hackathon_data)

    print("\n✅ Hackathon Setup Successfully Completed!")
    print("You can now proceed to logistics, registration, and other flows later.\n")

if __name__ == "__main__":
    automate_hackathon_management()
