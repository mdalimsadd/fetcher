from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import logging
from datetime import datetime

# ================= CONFIG =================
PHPSESSID = "rho4rkfi9ipdf9b1sqj8tioun3"

# ================= SETUP =================
app = FastAPI(title="OTP Fetcher API")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ================= HELPERS =================
def get_today_range():
    today = datetime.now().strftime("%Y-%m-%d")
    return f"{today} 00:00:00", f"{today} 23:59:59"

def fetch_latest_otp():
    """Fetch latest OTP data from source server."""
    start, end = get_today_range()
    url = "http://51.83.103.80/ints/agent/res/data_smscdr.php"

    cookies = {"PHPSESSID": PHPSESSID}
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10) Chrome/137.0.0.0 Safari/537.36",
    }

    params = {
        "fdate1": start,
        "fdate2": end,
        "fg": "0",
        "sEcho": "1",
        "iColumns": "9",
        "iDisplayLength": "1",
        "iDisplayStart": "0",
    }

    try:
        response = requests.get(url, cookies=cookies, headers=headers, params=params, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"❌ OTP fetch failed: {e}")
        return {"error": str(e)}

# ================= HTML PAGE =================
@app.get("/", response_class=HTMLResponse)
def home_page():
    """Display latest OTP data in HTML."""
    data = fetch_latest_otp()
    html = """
    <html>
        <head>
            <title>OTP Fetcher Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f5f6fa; padding: 30px; }
                h1 { color: #2c3e50; }
                .otp-box {
                    background: #fff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    max-width: 600px;
                }
                .label { font-weight: bold; color: #555; }
                .value { color: #2c3e50; font-size: 1.1em; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <h1>📱 OTP Fetcher Dashboard</h1>
    """

    if "aaData" in data and data["aaData"]:
        latest = data["aaData"][0]
        result = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "number": latest[2],
            "message": latest[5],
            "service": latest[3],
        }

        html += f"""
            <div class="otp-box">
                <p><span class="label">🕒 Time:</span> <span class="value">{result['time']}</span></p>
                <p><span class="label">📞 Number:</span> <span class="value">{result['number']}</span></p>
                <p><span class="label">💬 Message:</span> <span class="value">{result['message']}</span></p>
                <p><span class="label">🔧 Service:</span> <span class="value">{result['service']}</span></p>
            </div>
        """
    else:
        html += """<p class="error">⚠️ No OTP data available right now.</p>"""

    html += """
        </body>
    </html>
    """
    return html
