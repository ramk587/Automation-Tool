from flask import Flask, render_template, request, send_file
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/amazon", methods=["GET", "POST"])
def amazon():
    if request.method == "POST":
        file = request.files['file']
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        result = os.path.join(OUTPUT_FOLDER, "result.txt")
        with open(result, "w") as f:
            f.write("Voucher processed successfully!")

        return send_file(result, as_attachment=True)

    return render_template("amazon.html")

from flask import Flask, render_template, request, send_file
import pandas as pd
import re
import os

app = Flask(__name__)

OUTPUT_FOLDER = "outputs"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route("/")
def home():
    return render_template("index.html")


from datetime import datetime
@app.route("/gmail", methods=["GET", "POST"])
def gmail():
    table_data = []
    file_ready = False
    total_vouchers = 0
    file_path = ""

    if request.method == "POST":
        text = request.form.get("gmail_data")

        amounts = re.findall(r'₹\s?([\d,]+\.?\d*)', text)
        expiries = re.findall(r'Expiry date\s*:\s*([0-9A-Za-z\-]+)', text)
        codes = re.findall(r'Gift Card Code:\s*([A-Z0-9\-]+)', text)
        refs = re.findall(r'Reference ID\s*([0-9]+)', text)

        for i in range(len(codes)):
            table_data.append({
                "Amount": amounts[i] if i < len(amounts) else "",
                "Expiry": expiries[i] if i < len(expiries) else "",
                "Code": codes[i],
                "Ref": refs[i] if i < len(refs) else ""
            })
        total_vouchers = len(table_data)
        # 📁 Folder create
        now = datetime.now()
        year = str(now.year)
        month = now.strftime("%m-%B")

        folder = f"outputs/{year}/{month}"
        os.makedirs(folder, exist_ok=True)

        filename = f"gmail_{now.strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = f"{folder}/{filename}"

        df = pd.DataFrame(table_data)
        df.to_excel(file_path, index=False)

        file_ready = True

    return render_template(
        "gmail.html",
        table_data=table_data,
        file_ready=file_ready,
        file_path=file_path,
        total_vouchers=total_vouchers
    )


@app.route("/download")
def download():
    path = request.args.get("file")
    return send_file(path, as_attachment=True)

@app.route("/amazon-check", methods=["GET", "POST"])
def amazon_check():
    gift_code = ""

    if request.method == "POST":
        gift_code = request.form.get("gift_code")

    return render_template(
        "amazon_check.html",
        gift_code=gift_code
    )

@app.route("/amazon-bulk", methods=["GET", "POST"])
def amazon_bulk():
    code = ref = ""
    if request.method == "POST":
        code = request.form.get("code")
        ref = request.form.get("ref")

    return render_template("amazon_bulk.html", code=code, ref=ref)
@app.route("/save-result", methods=["POST"])
def save_result():
    code = request.form["code"]
    ref = request.form["ref"]
    result = request.form["result"]

    file = "outputs/amazon_results.xlsx"

    if os.path.exists(file):
        df = pd.read_excel(file)
    else:
        df = pd.DataFrame(columns=["Code", "Reference", "Result"])

    df.loc[len(df)] = [code, ref, result]
    df.to_excel(file, index=False)

    return "✅ Result saved successfully!"


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
