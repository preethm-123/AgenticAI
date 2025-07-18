from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str="westus3.api.azureml.ms;c5d47662-af4d-400e-ace6-ff70828d7d98;az-csi-grp1;agents"
)

problem_agent_id = "asst_idDBn11Mnpj8tbkaXhiDAvQe"  # Problem Statement Agent ID

def generate_problem_statements_from_agent(domain=""):
    thread = project_client.agents.create_thread()

    if domain:
        message_content = f"Please generate 5 real-world problem statements focused on the {domain} domain."
    else:
        message_content = "Please generate 5 real-world challenging problem statements in technology, healthcare, education, business, or environment."

    project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=message_content
    )

    run = project_client.agents.create_and_process_run(
        thread_id=thread.id,
        agent_id=problem_agent_id
    )

    messages = project_client.agents.list_messages(thread_id=thread.id)

    return messages.text_messages[0].text["value"]  # ✅ Correct

def read_problem_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content