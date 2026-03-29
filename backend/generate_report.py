import markdown2

with open("PROJECT_REPORT.md", "r", encoding="utf-8") as f:
    content = f.read()

html = markdown2.markdown(content, extras=["tables", "fenced-code-blocks"])

css = """
body {
    font-family: Calibri, sans-serif;
    margin: 2cm;
    max-width: 800px;
    font-size: 11pt;
    line-height: 1.5;
    color: #111;
}
h1 { font-size: 16pt; border-bottom: 2px solid #333; padding-bottom: 6px; }
h2 { font-size: 13pt; margin-top: 20px; color: #1a1a2e; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
th { background: #1a1a2e; color: white; padding: 8px; text-align: left; }
td { border: 1px solid #ccc; padding: 6px 8px; }
tr:nth-child(even) { background: #f5f5f5; }
code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 10pt; }
pre { background: #f0f0f0; padding: 12px; border-radius: 6px; font-size: 10pt; }
blockquote { border-left: 4px solid #1a1a2e; margin: 0; padding-left: 12px; color: #555; }
"""

full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{css}</style>
</head>
<body>
{html}
</body>
</html>"""

with open("PROJECT_REPORT.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("HTML report created successfully!")
print("Open PROJECT_REPORT.html in browser")
print("Then press Ctrl+P and Save as PDF")
