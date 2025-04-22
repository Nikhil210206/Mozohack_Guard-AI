from flask import Flask, render_template, request, jsonify, send_file, Response
import subprocess
import os
import signal
import time

app = Flask(__name__, static_folder="Frontend", template_folder="Frontend")
process = None  
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/features")
def features():
    return render_template("feature.html")
@app.route("/start-guard-ai", methods=["POST"])
def start_guard_ai():
    global process
    try:
        if process is None:
            process = subprocess.Popen(["python3", "main.py"], cwd=os.getcwd())
            return jsonify({"status": "success", "message": "Guard AI started successfully!"})
        else:
            return jsonify({"status": "error", "message": "Guard AI is already running!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
@app.route("/stop-guard-ai", methods=["POST"])
def stop_guard_ai():
    global process
    try:
        if process is not None:
            os.kill(process.pid, signal.SIGTERM)
            process = None
            return jsonify({"status": "success", "message": "Guard AI stopped successfully!"})
        else:
            return jsonify({"status": "error", "message": "Guard AI is not running!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
@app.route("/download-report", methods=["GET"])
def download_report():
    report_path = "logs/final_report.pdf"
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    else:
        return jsonify({"status": "error", "message": "Report not found!"})
@app.route("/stream-logs")
def stream_logs():
    def generate_logs():
        log_file = "logs/guard_ai_logs.txt"
        with open(log_file, "r") as f:
            while True:
                line = f.readline()
                if line:
                    yield f"data: {line}\n\n"
                else:
                    time.sleep(1)

    return Response(generate_logs(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)