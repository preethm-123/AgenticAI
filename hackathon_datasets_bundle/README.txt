
Hack the Hackathon: Dataset Documentation
=========================================

This bundle includes sample datasets provided in both CSV and JSON formats to support participants of all skill levels. These datasets are entirely fictitious and are intended for educational use only.

1. participants.csv / participants.json
   - Description: Sample participant profiles
   - Fields:
     - ID: Unique identifier for the participant
     - Name: Fictitious full name
     - Role: Role in the event (e.g., Undergraduate, Graduate, PhD Student)
     - Skills: Technical or domain skills
     - Availability: General time windows participant is available
     - Diet: Dietary restrictions
     - Pronouns: Preferred pronouns

2. event_schedule.csv / event_schedule.json
   - Description: Sample hackathon event schedule
   - Fields:
     - Event: Name of the session
     - Time: Scheduled start time
     - Location: Assigned room or space

3. task_tracker.csv / task_tracker.json
   - Description: Event planning task list
   - Fields:
     - Task: Description of the task
     - Owner: Person responsible
     - Status: Current task status (Completed, Pending, In Progress)
     - Due: Due date

4. email_snippets.json
   - Description: Example internal communication snippets
   - Fields:
     - Subject: Email subject line
     - Body: Main content of the message

5. rules_constraints.json
   - Description: General hackathon rules and judging criteria
   - Keys:
     - max_team_size: Maximum allowed team size
     - min_team_size: Minimum allowed team size
     - allow_cross_skill_teams: Whether diverse skill teams are encouraged
     - no_back_to_back_sessions_for_mentors: Scheduling constraint for mentors
     - judging_criteria: List of judging rubric categories

6. incident_alerts.json
   - Description: Simulated alerts for real-time incident handling
   - Fields:
     - Time: Time of the incident
     - Type: Type of disruption
     - Message: Details of the issue

These files can be used as static inputs or programmatically accessed in student projects. No real data is included.

Enjoy the challenge!
