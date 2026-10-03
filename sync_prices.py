import json
import re
import subprocess
import sys

API = r"C:\Users\ArchvizNotebook\AppData\Local\hermes\skills\productivity\google-workspace\scripts\google_api.py"
SID = "1_YSq8fh9erDR7l8WCrpSWixxVAdvdFD7SJVokQ5PyBU"
INDEX = r"C:\Users\ArchvizNotebook\AppData\Local\hermes\cache\scratch\andes-site\index.html"

# Метаданные ног в порядке строк таблицы (строки 3–10, без заголовка и строки «Москва»)
LEGS = [
    {"a":"sao","b":"lim","type":"Перелёт","route":"Сан-Паулу → Лима","airline":"Sky Airline / JetSMART",
     "avia":"https://www.aviasales.ru/search/GRULIM","ostro":"https://avia.ostrovok.ru/?origin=GRU&destination=LIM"},
    {"a":"lim","b":"cus","type":"Перелёт","route":"Лима → Куско","airline":"JetSMART / Sky Airline",
     "avia":"https://www.aviasales.ru/search/LIMCUZ","ostro":"https://avia.ostrovok.ru/?origin=LIM&destination=CUZ"},
    {"a":"cus","b":"pun","type":"Автобус","route":"Куско → Пуно (оз. Титикака)","airline":"Turismo Mer / Cruz del Sur",
     "bus":"https://www.busbud.com/en/bus-schedules/cusco-puno"},
    {"a":"pun","b":"lap","type":"Автобус","route":"Пуно → Ла-Пас (+ граница)","airline":"Bolivia Hop",
     "bus":"https://www.boliviahop.com/"},
    {"a":"lap","b":"uyu","type":"Перелёт","route":"Ла-Пас → Уюни","airline":"Boliviana de Aviación",
     "avia":"https://www.aviasales.ru/search/LPBUYU","ostro":"https://avia.ostrovok.ru/?origin=LPB&destination=UYU"},
    {"a":"uyu","b":"spd","type":"Джип-тур","route":"Уюни → Сан-Педро-де-Атакама","airline":"местные агентства"},
    {"a":"spd","b":"scl","type":"Перелёт","route":"Калама (CJC) → Сантьяго","airline":"JetSMART / Sky Airline",
     "avia":"https://www.aviasales.ru/search/CJCSCL","ostro":"https://avia.ostrovok.ru/?origin=CJC&destination=SCL"},
    {"a":"scl","b":"sao","type":"Перелёт","route":"Сантьяго → Сан-Паулу","airline":"Sky Airline / LATAM",
     "avia":"https://www.aviasales.ru/search/SCLGRU","ostro":"https://avia.ostrovok.ru/?origin=SCL&destination=GRU"},
]

r = subprocess.run([sys.executable, API, "sheets", "get", SID, "A1:F10"],
                   capture_output=True, text=True, timeout=180)
if r.returncode != 0:
    print("ERR:", r.stderr[-400:]); sys.exit(1)
rows = json.loads(r.stdout)
assert len(rows) == 10, "ожидалось 10 строк, получено %d" % len(rows)
sheet_legs = rows[2:]  # строки 3–10
assert len(sheet_legs) == len(LEGS), "число строк таблицы не совпало с ногами"

for i, (row, leg) in enumerate(zip(sheet_legs, LEGS)):
    price = (row[3] or "").strip()
    airline = (row[2] or "").strip()
    if price in ("", "—", "-"):
        price = "цена не указана"
    leg["price"] = price
    if airline and airline != "любая (искать мультигородом)":
        leg["airline"] = airline
    print(f"{leg['route']:36s} | {leg['airline'][:34]:34s} | {price}")

lines = []
for leg in LEGS:
    extra = ""
    for k in ("avia", "ostro", "bus"):
        if k in leg:
            extra += ', %s:"%s"' % (k, leg[k])
    lines.append('  {a:"%s", b:"%s", type:"%s", route:"%s", airline:"%s", price:"%s"%s},' % (
        leg["a"], leg["b"], leg["type"], leg["route"], leg["airline"], leg["price"], extra))
block = "const legs = [\n" + "\n".join(lines) + "\n];"

with open(INDEX, encoding="utf-8") as f:
    html = f.read()
html, n = re.subn(r"const legs = \[.*?\n\];", block, html, count=1, flags=re.S)
assert n == 1, "блок legs не найден/неоднозначен"
with open(INDEX, "w", encoding="utf-8") as f:
    f.write(html)
print("index.html обновлён (цены из таблицы)")
