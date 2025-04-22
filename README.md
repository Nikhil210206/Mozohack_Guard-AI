Guard AI Project

Welcome to the Guard AI project! 🚨

Guard AI is a lightweight, AI-powered exam monitoring tool that provides real-time proctoring by detecting suspicious activities during online exams such as unauthorized speaking, gaze deviation, and usage of restricted websites.

🔍 Features:
Lip Movement Detection + Audio Analysis
Detects if the user is speaking during the exam.
Differentiates between yawning and speaking.

Gaze Tracking:
Tracks user's eye and head movement.
Detects if the user looks away from the screen.

Website Monitoring:
Detects if the user opens any non-permitted websites.

Comprehensive Report Generation:
Summarizes user behavior during the exam.
Includes start and end times of suspicious activities.
Generates a clean PDF report after each test session.

📚 Project Structure:
guard_ai_project/
│
├── features/
│   ├── __init__.py
│   ├── lip_detection.py
│   ├── gaze_tracking.py
│   └── website_monitor.py
│
├── logs/
│   ├── lip_audio_logs.txt
│   ├── gaze_tracking_logs.txt
│   └── website_usage_logs.txt
│
├── reports/
│   └── final_report.pdf (auto-generated)
│
├── main.py
├── generate_report.py
├── README.md
├── requirements.txt

🔧 Installation:
1. Clone the repository: git clone https://github.com/your-username/guard-ai-project.git
2. Install the required libraries: pip install -r requirements.txt

📅 How to Use:
1. Run the application: python main.py
2. After finishing, you can generate an intermediate report.
3. At the end, generate a final comprehensive PDF report.

📊 Reports:
Reports will be generated automatically in the reports/ folder.

The report includes:
Activities detected.
Time intervals.
Observations.

🎉 Credits

Developed by Nikhil Balamurugan and Vishaal Pillay👨‍💻

🌍 License

This project is licensed under the MIT License.
