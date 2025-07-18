from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str="westus3.api.azureml.ms;c5d47662-af4d-400e-ace6-ff70828d7d98;az-csi-grp1;agents"
)

sponsor_agent_id = "asst_5SdBY40KzTPlAUTGLl5gzhnB"  # Sponsor Agent ID

def find_sponsors_for_problem(problem_text):
    thread = project_client.agents.create_thread()

    project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=problem_text
    )

    run = project_client.agents.create_and_process_run(
        thread_id=thread.id,
        agent_id=sponsor_agent_id
    )

    messages = project_client.agents.list_messages(thread_id=thread.id)

    return messages.text_messages[0].text["value"]  # ✅ Correct

def send_email(to_email, subject, body, from_email, from_password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()


def find_sponsors_and_send_emails(problem_text, from_email, from_password, event_date):
    sponsor_emails_text = find_sponsors_for_problem(problem_text)

    print("\n🛠 RAW OUTPUT FROM SPONSOR AGENT:")
    print("-" * 60)
    print(sponsor_emails_text)
    print("-" * 60)

    # Extract valid emails using regex
    email_matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", sponsor_emails_text)

    if not email_matches:
        print("❌ No valid email addresses found in agent response.")
        return

    match = re.search(r"Problem Title:\s*(.*)", problem_text)
    problem_title = match.group(1).strip() if match else "Our Upcoming Hackathon"

    for to_email in email_matches:
        subject_line = f"Sponsorship Invitation – Hackathon on {problem_title}"

        body_text = f"""
Hi, this is Indrasena from the Connected Systems Institute (CSI) at the University of Wisconsin–Milwaukee. We are organizing a hackathon focused on "{problem_title}" scheduled for {event_date}.

As a leader in your field, we believe your organization would be an excellent partner for this event. Your expertise aligns perfectly with the theme and goals of this hackathon.

We would love to explore a potential sponsorship or collaboration with your team. Please let us know if you'd be open to a short conversation or receiving additional details.

Thank you for your time and consideration.

Best regards,  
Indrasena Kalyanam  
Graduate Student | CSI, UWM  
Email: kindrasena8@gmail.com
""".strip()

        try:
            print(f"📤 Sending email to: {to_email}")
            send_email(to_email, subject_line, body_text, from_email, from_password)
            print(f"✅ Sent to {to_email}")
        except Exception as e:
            print(f"❌ Failed to send to {to_email}: {str(e)}")