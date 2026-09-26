import re

js_path = 'frontend/app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

new_cred = """async function guardarCredito(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const original = btn ? btn.innerHTML : 'Generar';
    if(btn) { btn.disabled = true; btn.innerHTML = 'Generando...'; }

    try {
        let tasaStr = document.getElementById('tasa_interes').value.replace(',', '.');
        let tasa = parseFloat(tasaStr) / 100.0;
        const bodyCredito = {
            entidad_id: parseInt(document.getElementById('entidad_id').value),
            concepto: document.getElementById('concepto').value,
            monto_total: getMonto('monto_total'),
            tasa_interes: tasa,
            tipo_tasa: document.getElementById('tipo_tasa').value,
            numero_cuotas: parseInt(document.getElementById('numero_cuotas').value),
            fecha_compra: document.getElementById('fecha_compra').value
        };
        
        const resCred = await fetchAuth(`${API_URL}/creditos/`, { method: 'POST', body: JSON.stringify(bodyCredito) });
        if(!resCred.ok) {
            const errDat = await resCred.json();
            alert('Error backend: ' + errDat.detail);
            if(btn){btn.disabled=false; btn.innerHTML=original;}
            return;
        }
        e.target.reset();
        document.getElementById('fecha_compra').valueAsDate = new Date();
        if(btn) { btn.disabled = false; btn.innerHTML = original; }
        actualizarTodo();
    } catch(error) {
        alert("Error de JS al generar crédito: " + error.message);
        if(btn) { btn.disabled = false; btn.innerHTML = original; }
    }
}"""

regex2 = re.compile(r"async function guardarCredito\(e\) \{.*?\}\n\nasync function guardarSuscripcion", re.DOTALL)
js = regex2.sub(new_cred + "\n\nasync function guardarSuscripcion", js)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("guardarCredito debugged!")
