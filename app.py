from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import urllib3
import logging
from datetime import datetime

# ================= CONFIG =================
PHPSESSID = "j47ivf433pr815o8sfd48lb01c"
BASE_URL = "http://109.236.84.81/ints/test/res/data_testsmscdr.php"

# ================= SETUP =================
app = FastAPI(title="SMS Fetcher API")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ================= HELPERS =================
def get_today_range():
    today = datetime.now().strftime("%Y-%m-%d")
    return f"{today} 00:00:00", f"{today} 23:59:59"

def fetch_sms_messages():
    """Fetch SMS messages from the source server."""
    start, end = get_today_range()

    cookies = {'PHPSESSID': PHPSESSID}
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'http://109.236.84.81/ints/test/TestSMSCDRStats',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    params = {
        "fdate1": start,
        "fdate2": end,
        "fg": "0",
        "sEcho": "1",
        "iColumns": "5",
        "iDisplayStart": "0",
        "iDisplayLength": "25",
    }

    try:
        response = requests.get(BASE_URL, cookies=cookies, headers=headers, params=params, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"❌ SMS fetch failed: {e}")
        return {"error": str(e)}

# ================= API ENDPOINT =================
@app.get("/api/sms/latest")
def get_latest_sms():
    """Return latest SMS messages as JSON."""
    data = fetch_sms_messages()
    if "aaData" in data and data["aaData"]:
        messages = []
        for msg in data["aaData"]:
            messages.append({
                "time": msg[0],
                "number": msg[2],
                "service": msg[3],
                "message": msg[4]
            })
        return {"status": "success", "data": messages}
    else:
        return {"status": "no_data", "data": []}

@app.get("/", tags=["Root"])
def root():
    return {"message": "✅ SMS Fetcher API is running"}

# ================= DASHBOARD =================
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """Show SMS messages in HTML dashboard."""
    data = fetch_sms_messages()
    html = """
    <html>
        <head>
            <title>SMS Fetcher Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f5f6fa; padding: 20px; }
                h1 { color: #2c3e50; }
                table { border-collapse: collapse; width: 100%; background: #fff; }
                th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
                th { background-color: #2c3e50; color: white; }
            </style>
        </head>
        <body>
            <h1>📱 SMS Fetcher Dashboard</h1>
    """

    if "aaData" in data and data["aaData"]:
        html += "<table>"
        html += "<tr><th>Time</th><th>Number</th><th>Service</th><th>Message</th></tr>"
        for msg in data["aaData"]:
            html += f"<tr><td>{msg[0]}</td><td>{msg[2]}</td><td>{msg[3]}</td><td>{msg[4]}</td></tr>"
        html += "</table>"
    else:
        html += "<p>⚠️ No SMS messages available right now.</p>"

    html += "</body></html>"
    return html
