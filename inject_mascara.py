import re

js_path = 'frontend/app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

mask_logic = """
// ================= FORMATO MONEDA EN INPUTS =================
function aplicarMascaraMoneda(event) {
    let input = event.target;
    // Eliminar todo lo que no sea número
    let valor = input.value.replace(/\\D/g, "");
    if (valor === "") {
        input.dataset.raw_value = "";
        input.value = "";
        return;
    }
    // Guardar el valor matemático real en un atributo data-raw_value
    input.dataset.raw_value = valor;
    
    // Formatear con puntos de miles
    input.value = new Intl.NumberFormat('es-CO').format(valor);
}

document.querySelectorAll('input[data-type="currency"]').forEach(input => {
    input.addEventListener('input', aplicarMascaraMoneda);
});

// Función auxiliar para leer el valor numérico real de los inputs
function getMonto(id) {
    const input = document.getElementById(id);
    if (input.dataset.raw_value) {
        return parseFloat(input.dataset.raw_value);
    }
    return parseFloat(input.value) || 0;
}
"""

js = js + "\n" + mask_logic

# Replace `parseFloat(document.getElementById('...').value)` with `getMonto('...')`
js = js.replace("parseFloat(document.getElementById('transMonto').value)", "getMonto('transMonto')")
js = js.replace("parseFloat(document.getElementById('monto_total').value)", "getMonto('monto_total')")
js = js.replace("parseFloat(document.getElementById('monto_suscripcion').value)", "getMonto('monto_suscripcion')")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

# --- INDEX.HTML ---
html_path = 'frontend/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Transacciones
html = html.replace('<input type="number" step="0.01" id="transMonto" required', '<input type="text" inputmode="numeric" data-type="currency" id="transMonto" required')
# Creditos
html = html.replace('<input type="number" step="0.01" id="monto_total" required', '<input type="text" inputmode="numeric" data-type="currency" id="monto_total" required')
# Suscripciones
html = html.replace('<input type="number" id="monto_suscripcion" step="0.01" required', '<input type="text" inputmode="numeric" data-type="currency" id="monto_suscripcion" required')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Mascara instalada")
