import pandas as pd
import re

# =========================
# Read chat file
# =========================
with open("C:/Users/bwlau/Downloads/_chat.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

# =========================
# Keywords to detect
# =========================
keywords = (
    r'\blevy|levies\b'
    r'|\bdmo\b'
    r'|\bexport(?:s)?\b'
    r'|\bwar(?:s)?\b'
    r'|\bbiodiesel(?:s)?\b'
    r'|\brumou?r(?:s)?\b'
    r'|\bimport\s+tax(?:es)?\b'
    r'|\bindia\b'
    r'|\bchina\b'
    r'|\bindonesia\b'
    r'|\bargentina\b'
    r'|\bbrazil\b'
    r'|\busda\b'
    r'|\bsoyoil(?:s)?\b'
    r'|\blarangan\b'
    r'|\bekspor\b'
    r'|\bpungutan\b'
    r'|\bvessel(?:s)?\b'
    r'|\btariff(?:s)?\b'
    r'|\bproduction(?:s)?\b'
    r'|\bshipment(?:s)?\b'
    r'|\bstock(?:s)?\b'
    r'|\breference\s+price(?:s)?\b'
    r'|\bsuspension(?:s)?\b'
    r'|\bforecast(?:s|ed|ing)?\b'
    r'|\ballocation(?:s)?\b'
    r'|\bgapki\b'
)

# =========================
# Blacklist words
# =========================
blacklist = (
    r'\bimage omitted\b'
    r'|\bcontact card\b'
    r'|\bok\b'
    r'|\bnp\b'
    r'|\bokays\b'
    r'|\bhaha\b'
    r'|\bfyi\b'
    r'|\bthx\b'
    r'|\bleh\b'
    r'|\bmc\b'
    r'|\bi\b'
    r'|\byou\b'
    r'|\bwe\b'
    r'|\bme\b'
    r'|\bmy\b'
    r'|\bmine\b'
    r'|\bomnibus\b'
    r'|\bu\b'
    r'|\bhang\s+flower\b'
    r'|\bsultan\s+ismail\b'
    r'|\bdafaq\b'
    r'|\bmeh\b'
)

# =========================
# Message start pattern
# =========================
msg_start = re.compile(
    r'^\[(\d{1,2}/\d{1,2}/\d{4}),\s+(\d{1,2}:\d{2}(?::\d{2})?\s?[APMapm]{0,2})\]\s*(.*?):\s*(.*)'
)

# =========================
# Parse chat
# =========================
messages = []
current_msg = None

for line in lines:
    line = line.replace('\u200e', '').replace('\xa0', ' ').strip()
    match = msg_start.match(line)

    if match:
        if current_msg:
            messages.append(current_msg)
        current_msg = {
            "Date": match.group(1),
            "Time": match.group(2),
            "Message": match.group(4)
        }
    else:
        if current_msg:
            current_msg["Message"] += " " + line

if current_msg:
    messages.append(current_msg)

# =========================
# Helpers
# =========================
def word_count_ok(text, min_words=5):
    return len([w for w in str(text).split() if w.strip()]) >= min_words

# =========================
# Main filtering
# =========================
data_passed = []
data_removed = []

for i, msg in enumerate(messages):
    text = msg["Message"].strip()

    bl_hits = [m.group(0) for m in re.finditer(blacklist, text, re.IGNORECASE)]
    if bl_hits:
        data_removed.append([
            msg["Date"], msg["Time"], text,
            f"Removed: Blacklisted word ({', '.join(bl_hits)})"
        ])
        continue

    if not word_count_ok(text):
        data_removed.append([
            msg["Date"], msg["Time"], text,
            "Removed: Too few words (<5)"
        ])
        continue

    kw_hits = [m.group(0) for m in re.finditer(keywords, text, re.IGNORECASE)]

    if kw_hits:
        if re.search(r'\brumou?r(?:s)?\b', text, re.IGNORECASE):
            for j in [i - 1, i + 1]:
                if 0 <= j < len(messages):
                    ctx = messages[j]["Message"].strip()
                    if re.search(blacklist, ctx, re.IGNORECASE) or not word_count_ok(ctx):
                        data_removed.append([
                            messages[j]["Date"], messages[j]["Time"], ctx,
                            "Removed: Context around rumour failed filter"
                        ])
                    else:
                        data_passed.append([
                            messages[j]["Date"], messages[j]["Time"], ctx,
                            "Context around rumour"
                        ])

            data_passed.append([
                msg["Date"], msg["Time"], text,
                f"Keyword detected: {', '.join(kw_hits)}"
            ])
        else:
            data_passed.append([
                msg["Date"], msg["Time"], text,
                f"Keyword detected: {', '.join(kw_hits)}"
            ])

# =========================
# FINAL rumour context validation
# =========================
final_passed = []

for row in data_passed:
    date, time, text, reason = row

    if reason == "Context around rumour":
        if (re.search(blacklist, text, re.IGNORECASE)
            or not word_count_ok(text)
            or not re.search(keywords, text, re.IGNORECASE)):
            data_removed.append([
                date, time, text,
                "Removed: Context around rumour failed final validation"
            ])
            continue

    final_passed.append(row)

# =========================
#  Survey extraction
# =========================
pattern = re.compile(
    r'\b\b.*\bProduction\s+Survey\b',
    re.IGNORECASE
)

final_filtered = []
rows = []

for row in final_passed:
    if pattern.search(row[2]):
        rows.append([
            row[0], row[1], row[2],
            "Moved: Production Survey"
        ])
    else:
        final_filtered.append(row)

# =========================
# Save to Excel (3 sheets)
# =========================
with pd.ExcelWriter("keywords_messages_filtered_final.xlsx") as writer:
    pd.DataFrame(
        final_filtered,
        columns=["Date", "Time", "Message", "Reason"]
    ).to_excel(writer, sheet_name="Filtered Messages", index=False)

    pd.DataFrame(
        data_removed,
        columns=["Date", "Time", "Message", "Reason"]
    ).to_excel(writer, sheet_name="Removed Messages", index=False)

    pd.DataFrame(
        rows,
        columns=["Date", "Time", "Message", "Reason"]
    ).to_excel(writer, sheet_name=" Production Survey", index=False)

print("✅ Extraction completed successfully")
print("✅ Filters + rumour logic + broker survey extraction applied")
