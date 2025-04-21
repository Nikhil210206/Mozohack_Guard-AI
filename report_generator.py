import os
from fpdf import FPDF

# Helper function to read logs from files
def read_log_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read()
    return "No data available."

# Function to generate partial report for one feature
def generate_partial_report(feature_name):
    log_file = f"logs/{feature_name}_logs.txt"
    report_content = read_log_file(log_file)
    
    # Create report folder if doesn't exist
    report_folder = "reports/partial_reports"
    os.makedirs(report_folder, exist_ok=True)

    report_file = f"reports/partial_reports/{feature_name}_report.txt"
    with open(report_file, 'w') as f:
        f.write(f"Report for {feature_name}\n")
        f.write("=" * 40 + "\n")
        f.write(report_content)
    
    print(f"{feature_name} partial report generated!")

# Function to generate final comprehensive report (PDF)
def generate_final_pdf_report():
    # Create final PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Comprehensive Exam Report", ln=True, align='C')
    pdf.ln(10)

    # Add partial reports content to the PDF
    for feature in ["lip_audio", "gaze_tracking", "website_usage"]:
        log_file = f"logs/{feature}_logs.txt"
        report_content = read_log_file(log_file)
        
        pdf.cell(200, 10, txt=f"{feature.replace('_', ' ').title()}:", ln=True)
        pdf.multi_cell(0, 10, txt=report_content)
        pdf.ln(10)

    # Save the final PDF report
    final_report_path = "reports/final_report.pdf"
    pdf.output(final_report_path)
    print(f"Final PDF report generated at {final_report_path}")
