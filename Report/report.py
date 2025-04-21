from fpdf import FPDF
import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Guard AI - Session Report', ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
pdf = PDF()
pdf.add_page()

pdf.set_font('Arial', '', 12)
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
pdf.cell(0, 10, f"Session Date and Time: {current_time}", ln=True)
pdf.ln(5)

# Read Gaze Tracking logs
try:
    with open('gaze_logs.txt', 'r') as f:
        gaze_logs = f.readlines()
except FileNotFoundError:
    gaze_logs = []

# Read Lip Audio logs
try:
    with open('lip_audio_logs.txt', 'r') as f:
        lip_logs = f.readlines()
except FileNotFoundError:
    lip_logs = []

# Section: Gaze Tracking
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, 'Gaze Tracking Events:', ln=True)
pdf.set_font('Arial', '', 12)

if gaze_logs:
    for log in gaze_logs:
        pdf.multi_cell(0, 10, log.strip())
else:
    pdf.cell(0, 10, 'No Gaze Tracking events recorded.', ln=True)

pdf.ln(10)

# Section: Lip + Audio Detection
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, 'Lip & Audio Detection Events:', ln=True)
pdf.set_font('Arial', '', 12)

if lip_logs:
    for log in lip_logs:
        pdf.multi_cell(0, 10, log.strip())
else:
    pdf.cell(0, 10, 'No Lip/Audio events recorded.', ln=True)

# Save the final PDF
pdf.output('GuardAI_Report.pdf')

print("✅ Report generated successfully: GuardAI_Report.pdf")
