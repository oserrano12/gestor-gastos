import re

js_path = 'frontend/app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Fix cuenta_id
js = js.replace(
    "cuenta_id: parseInt(document.getElementById('transCuenta').value)",
    "cuenta_id: document.getElementById('transCuenta') ? parseInt(document.getElementById('transCuenta').value) : null"
)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("transCuenta safe!")
