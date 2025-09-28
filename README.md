💧 ProtApp Water Data Logger
A modern, scalable web application for logging, monitoring, and analyzing data from Water Treatment Works (WTWs). This app is built with Python and Streamlit, designed for ease of use by Process Controllers and powerful analytics for Managers.

🌟 About The Project
This project aims to replace a manual or semi-automated data collection system with a centralized, secure, and mobile-friendly web application. It is designed to scale across 100+ Water Treatment Works, providing a single source of truth for all operational data.

The application features role-based access:

Process Controllers: Can log operational data through simple, intuitive forms.

Managers: Can view dashboards, analyze trends, and monitor compliance across all their assigned sites.

✨ Features
Secure User Authentication: Users log in with a unique username and password.

Role-Based Views: The user interface changes based on the user's role.

Centralized Database: All data is stored securely in Google BigQuery, ensuring data integrity and scalability.

Mobile-First Design: The interface is fully responsive and optimized for use on mobile devices and tablets.

Data Entry Forms: Intuitive forms for capturing key metrics, starting with Water Quality.

Image Capture: Ability to capture and associate images with test results for verification.

🛠️ Built With
This project is built with a modern, scalable tech stack:

Front-End: Streamlit

Back-End Logic: Python

Database: Google BigQuery

Authentication: streamlit-authenticator

Deployment: Streamlit Community Cloud

🚀 Getting Started
To get a local copy up and running, follow these simple steps.

Prerequisites
Python 3.8+

A Google Cloud project with BigQuery API enabled.

A Google Cloud Service Account JSON key file.

Installation
Clone the repository:

git clone [https://github.com/your-username/water-data-app.git](https://github.com/your-username/water-data-app.git)
cd water-data-app

Create a virtual environment (recommended):

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

Install the required packages:

pip install -r requirements.txt

Set up your local credentials:

Create a folder named .streamlit in the root of your project directory.

Inside .streamlit, create a file named secrets.toml.

Add your Google Cloud JSON key to secrets.toml like this:

# .streamlit/secrets.toml
GCP_CREDENTIALS = """
{
  "type": "service_account",
  "project_id": "...",
  ...
}
"""

Run the app:

streamlit run app.py

🗺️ Roadmap
This is the initial version of the application. Future development will focus on:

[ ] Fetching user credentials dynamically from the user_permissions table in BigQuery.

[ ] Implementing the Manager Dashboard with data visualizations.

[ ] Building out the data entry forms for all other categories (Volumes, Chemicals, Incidents, etc.).

[ ] Adding the functionality to upload captured images to Google Cloud Storage.

[ ] Populating the "Select WTW" dropdown based on the logged-in user's assignments.

🤝 Contributing
Contributions, issues, and feature requests are welcome!
