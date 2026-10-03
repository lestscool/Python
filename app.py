import os
import sys
import time
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse

# System-Limit für tiefe Rekursionen/Operationen erhöhen
sys.setrecursionlimit(200000)

# Versuche gmpy2 für maximale Performance zu nutzen
TRY_GMPY2 = True
try:
    import gmpy2
    from gmpy2 import mpfr
except ImportError:
    TRY_GMPY2 = False
    from decimal import Decimal, getcontext

app = FastAPI(title="High-Speed Präzisions-Rechner")

# Ordner für Ergebnisse direkt auf dem Desktop anlegen
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
DOWNLOAD_DIR = os.path.join(DESKTOP_PATH, "ergebnisse")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def berechne_pi(stellen: int) -> str:
    if TRY_GMPY2:
        # C-Performance via gmpy2
        gmpy2.get_context().precision = int(stellen * 3.321928) + 50
        pi_val = gmpy2.const_pi()
        return f"{pi_val:.{stellen}f}"
    else:
        # Standard Python Decimal (Chudnovsky-Algorithmus)
        getcontext().prec = stellen + 10
        c = 426880 * Decimal(10005).sqrt()
        l = 13591409
        x = 1
        m = 1
        k = 6
        s = 13591409
        iterations = (stellen // 14) + 1

        for i in range(1, iterations):
            l += 545140134
            x *= -262537412640768000
            m = (m * (k**3 - 16 * k)) // (i**3)
            s += Decimal(m * l) / x
            k += 12

        pi = c / s
        getcontext().prec = stellen
        return str(+pi)


def berechne_wurzel_zwei(stellen: int) -> str:
    if TRY_GMPY2:
        # C-Performance via gmpy2
        gmpy2.get_context().precision = int(stellen * 3.321928) + 50
        w2_val = gmpy2.sqrt(mpfr(2))
        return f"{w2_val:.{stellen}f}"
    else:
        # Standard Python Decimal
        getcontext().prec = stellen
        return str(Decimal(2).sqrt())


def get_html_page(
    pi_selected="", w2_selected="", stellen_val=100000, ergebnis_section=""
):
    engine_info = (
        "⚡ Super-Speed Modus (gmpy2 aktiv)"
        if TRY_GMPY2
        else "⚠️ Normaler Modus (Nutze 'pip install gmpy2' für 100x Speed)"
    )
    return f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>High-Speed Präzisions-Rechner</title>
    <style>
        * {{ box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        body {{ background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }}
        .card {{ background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.5); width: 100%; max-width: 650px; border: 1px solid #334155; }}
        h1 {{ color: #38bdf8; margin-top: 0; text-align: center; }}
        .engine-tag {{ text-align: center; font-size: 13px; color: #94a3b8; margin-bottom: 20px; background: #0f172a; padding: 6px; border-radius: 6px; }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; margin-bottom: 8px; font-weight: bold; color: #cbd5e1; }}
        select, input[type="number"] {{ width: 100%; padding: 12px; border: 1px solid #475569; background: #0f172a; color: white; border-radius: 6px; font-size: 16px; }}
        button {{ width: 100%; background: #0284c7; color: white; padding: 14px; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; transition: background 0.2s; }}
        button:hover {{ background: #0369a1; }}
        .result-box {{ margin-top: 25px; padding: 20px; background: #092e20; border-radius: 8px; border-left: 5px solid #22c55e; }}
        .time-badge {{ display: inline-block; background: #22c55e; color: black; padding: 4px 8px; border-radius: 4px; font-size: 14px; font-weight: bold; margin-bottom: 10px; }}
        .download-btn {{ display: block; width: 100%; text-decoration: none; background: #22c55e; color: black; padding: 12px; border-radius: 6px; font-weight: bold; margin-top: 15px; text-align: center; font-size: 16px; }}
        .download-btn:hover {{ background: #16a34a; }}
        .error-box {{ margin-top: 25px; padding: 15px; background: #450a0a; border-radius: 6px; border-left: 5px solid #ef4444; color: #fca5a5; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Mega-Präzisions-Rechner</h1>
        <div class="engine-tag">{engine_info}</div>
        <form action="/berechnen" method="post">
            <div class="form-group">
                <label for="typ">Was möchtest du berechnen?</label>
                <select id="typ" name="typ">
                    <option value="pi" {pi_selected}>Pi (π)</option>
                    <option value="wurzel2" {w2_selected}>Wurzel aus 2 (√2)</option>
                </select>
            </div>
            <div class="form-group">
                <label for="stellen">Anzahl der Nachkommastellen:</label>
                <input type="number" id="stellen" name="stellen" min="1" max="10000000" value="{stellen_val}" required>
            </div>
            <button type="submit">Berechnung starten</button>
        </form>

        {ergebnis_section}
    </div>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index():
    return get_html_page(pi_selected="selected", stellen_val=100000)


@app.post("/berechnen", response_class=HTMLResponse)
def berechnen(typ: str = Form(...), stellen: int = Form(...)):
    try:
        start_zeit = time.perf_counter()

        if typ == "pi":
            name = "Pi"
            ergebnis = berechne_pi(stellen)
            pi_sel, w2_sel = "selected", ""
        else:
            name = "Wurzel_2"
            ergebnis = berechne_wurzel_zwei(stellen)
            pi_sel, w2_sel = "", "selected"

        dauer = time.perf_counter() - start_zeit

        # Datei lokal im 'ergebnisse'-Ordner auf dem Desktop erstellen
        filename = f"{name.lower()}_{stellen}_stellen.txt"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Berechnung von {name} auf {stellen} Stellen\n")
            f.write(f"Dauer: {dauer:.6f} Sekunden\n")
            f.write("------------------------------------------\n")
            f.write(ergebnis)

        ergebnis_html = f"""
        <div class="result-box">
            <span class="time-badge">Fertig in {dauer:.4f} Sekunden!</span><br>
            <strong>Ergebnis für {name} ({stellen:,} Stellen) berechnet.</strong><br>
            <p style="margin-top: 8px; font-size: 14px; color: #cbd5e1;">
                Die Datei wurde direkt auf deinem Desktop im Ordner <b>'ergebnisse'</b> gespeichert.
            </p>
            <a href="/file/{filename}" class="download-btn">Datei herunterladen ({filename})</a>
        </div>
        """
    except Exception as e:
        pi_sel, w2_sel = ("selected", "") if typ == "pi" else ("", "selected")
        ergebnis_html = f"""
        <div class="error-box">
            <strong>Fehler bei der Berechnung:</strong> {str(e)}
        </div>
        """

    return get_html_page(
        pi_selected=pi_sel,
        w2_selected=w2_sel,
        stellen_val=stellen,
        ergebnis_section=ergebnis_html,
    )


@app.get("/file/{filename}")
def get_file(filename: str):
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(filepath):
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="text/plain",
        )
    return {"error": "Datei nicht gefunden"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
