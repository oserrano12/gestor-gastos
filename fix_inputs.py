import re

html_path = 'frontend/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix formTransaccion
html = html.replace(
    '<select id="categoria_id" class="mt-1 block w-full rounded border-slate-300 p-2 border"></select>',
    '<input type="text" id="transCategoriaInput" list="listaCategoriasAutocompletar" placeholder="Ej. Alimentación, Transporte..." autocomplete="off" required class="mt-1 block w-full rounded border-slate-300 p-2 border bg-white">'
)

html = html.replace(
    '<input type="number" id="monto_transaccion" step="0.01" required class="mt-1 block w-full rounded border-slate-300 p-2 border">',
    '<input type="text" inputmode="numeric" data-type="currency" id="monto_transaccion" required class="mt-1 block w-full rounded border-slate-300 p-2 border">'
)

# Fix formCredito
html = html.replace(
    '<input type="number" id="monto_total" step="0.01" required class="mt-1 block w-full rounded border-slate-300 p-2 border">',
    '<input type="text" inputmode="numeric" data-type="currency" id="monto_total" required class="mt-1 block w-full rounded border-slate-300 p-2 border">'
)

# Also update the JS to use monto_transaccion instead of transMonto since it's the ID I just set
js_path = 'frontend/app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace("getMonto('transMonto')", "getMonto('monto_transaccion')")

# And in sw.js bump to v5
sw_path = 'frontend/sw.js'
with open(sw_path, 'r', encoding='utf-8') as f:
    sw = f.read()
sw = sw.replace('v4', 'v5')
with open(sw_path, 'w', encoding='utf-8') as f:
    f.write(sw)

html = html.replace('v=4', 'v=5')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("HTML, JS and SW fixed!")
