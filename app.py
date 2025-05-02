from flask import Flask, render_template, request
from datetime import datetime, timedelta
import re

app = Flask(__name__)

@app.route('/')
def home():
    try:
        with open("visits.txt", "r") as f:
            count = int(f.read().strip())
    except:
        count = 0
    count += 1
    with open("visits.txt", "w") as f:
        f.write(str(count))
    return render_template('index.html', visit_count=count)

@app.route('/generate', methods=['POST'])
def generate():
    station = request.form.get('station').upper()
    amd = request.form.get('amd')
    amd_str = f"{amd} " if amd else ""
    timegroup = request.form.get('timegroup').upper().rstrip('Z') + 'Z'
    start_hour = request.form.get('start_hour')

    try:
        base = datetime.strptime(start_hour, "%d%H")
        end = base + timedelta(hours=30)
        full_period = f"{start_hour}/{end.strftime('%d%H')}"
    except:
        full_period = "0000/0000"

    types = ["INITIAL"] + request.form.getlist("type[]")
    periods = [full_period] + request.form.getlist("period[]")
    winds = [w.upper().rstrip('KT') + 'KT' if w else '' for w in request.form.getlist("wind[]")]
    visibilities = [
        v.upper() + "SM" if v and not v.upper().endswith("SM") else v.upper()
        for v in request.form.getlist("vis[]")
    ]
    wxs = request.form.getlist("wx[]")
    clouds = request.form.getlist("clouds[]")
    alt_raw = request.form.getlist("altimeter[]")
    icing_types = request.form.getlist("icing_type[]")
    icing_parts = request.form.getlist("icing[]")
    turb_types = request.form.getlist("turbulence_type[]")
    turb_parts = request.form.getlist("turbulence[]")
    max_temp = request.form.get("maxtemp")
    min_temp = request.form.get("mintemp")

    def encode_layer(t, bp, prefix):
        if t and bp and len(bp) >= 4:
            base = bp[:3]
            depth = bp[3:]
            if base.isdigit() and depth.isdigit():
                return f"{prefix}{t}{base}{depth}"
        return ""

    alts = ['QNH' + a.replace('QNH', '').replace('INS', '') + 'INS' if a else '' for a in alt_raw]
    icings = [encode_layer(t, p, "6") for t, p in zip(icing_types, icing_parts)]
    turbs = [encode_layer(t, p, "5") for t, p in zip(turb_types, turb_parts)]

    taf = ""
    for i in range(len(types)):
        if i >= len(periods): continue
        line = ""
        if types[i] == "INITIAL":
            line = f"TAF {amd_str}{station} {timegroup} {periods[i]}"
        else:
            line = f"{types[i]} {periods[i]}"
            if types[i] != "TEMPO":
                if not all([
                    i < len(winds) and winds[i],
                    i < len(visibilities) and visibilities[i],
                    i < len(clouds) and clouds[i],
                    i < len(alts) and alts[i]
                ]):
                    return f"<pre>Error: All core fields (wind, vis, clouds, altimeter) are required for BECMG line {i}</pre><a href='/'>Back</a>"

        if i < len(winds) and winds[i]:
            wind = winds[i]
            if "G" in wind:
                if not re.fullmatch(r"\d{5}G\d{2}KT", wind):
                    return f"<pre>Error: Invalid gusting wind format at line {i}: {wind}</pre><a href='/'>Back</a>"
            else:
                if not re.fullmatch(r"\d{5}KT", wind):
                    return f"<pre>Error: Invalid steady wind format at line {i}: {wind}</pre><a href='/'>Back</a>"
            line += f" {wind}"

        if i < len(visibilities) and visibilities[i]: line += f" {visibilities[i]}"
        if types[i] == "TEMPO":
            if i < len(wxs) and wxs[i]: line += f" {wxs[i]}"
            if i < len(clouds) and clouds[i]: line += f" {clouds[i]}"
            if i < len(alts) and alts[i]: line += f" {alts[i]}"
        else:
            if i < len(wxs): line += f" {wxs[i]}"
            if i < len(clouds): line += f" {clouds[i]}"
            if i < len(alts): line += f" {alts[i]}"
        if i < len(icings) and icings[i]: line += f" {icings[i]}"
        if i < len(turbs) and turbs[i]: line += f" {turbs[i]}"
        if i == len(types) - 1 and max_temp and min_temp:
            line += f" TX{max_temp.rstrip('Z')}Z TN{min_temp.rstrip('Z')}Z"
        taf += " ".join(line.strip().split()) + "\n"

    return f"<pre>{taf}</pre><a href='/'>Back</a>"

if __name__ == "__main__":
    app.run(debug=True)
