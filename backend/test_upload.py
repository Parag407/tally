import requests
import io
import pandas as pd

# Create a dummy excel file
df = pd.DataFrame({"Date": ["01-Apr-24"], "Particulars": ["Opening Balance"], "Vch Type": ["Receipt"], "Debit": [1000], "Credit": [0]})
excel_buffer = io.BytesIO()
df.to_excel(excel_buffer, index=False)
excel_buffer.seek(0)

# Send request
files = {"file": ("test.xlsx", excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
try:
    response = requests.post("http://localhost:8000/api/bank/upload", files=files, params={"use_ai": "false"})
    print("Status Code:", response.status_code)
    print("Response:", response.text[:200])
except Exception as e:
    print("Error:", e)
