import re

js_path = 'frontend/app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

new_trans = """async function guardarTransaccion(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = 'Guardando...';
    }

    const nombreCat = document.getElementById('transCategoriaInput').value.trim();
    let categoriaId = null;
    const tipoActivo = document.getElementById('btnTipoGasto').classList.contains('bg-red-600') ? 'Gasto' : 'Ingreso';
    
    const existe = dataCategorias.find(c => c.nombre.toLowerCase() === nombreCat.toLowerCase() && c.tipo === tipoActivo);
    
    if (existe) {
        categoriaId = existe.id;
    } else {
        const resNueva = await fetchAuth(`${API_URL}/categorias/`, {
            method: 'POST',
            body: JSON.stringify({ nombre: nombreCat, tipo: tipoActivo })
        });
        if(resNueva.ok) {
            const nuevaCat = await resNueva.json();
            dataCategorias.push(nuevaCat);
            categoriaId = nuevaCat.id;
        } else {
            alert('Error al crear nueva categoría');
            if (btn) { btn.disabled = false; btn.innerHTML = 'Guardar'; }
            return;
        }
    }

    const bodyTrans = {
        monto: getMonto('monto_transaccion'),
        fecha: document.getElementById('transFecha').value,
        categoria_id: categoriaId,
        cuenta_id: parseInt(document.getElementById('transCuenta').value),
        descripcion: document.getElementById('transDescripcion').value
    };
    
    await fetchAuth(`${API_URL}/transacciones/`, { method: 'POST', body: JSON.stringify(bodyTrans) });
    e.target.reset();
    document.getElementById('transFecha').valueAsDate = new Date();
    if (btn) { btn.disabled = false; btn.innerHTML = 'Guardar'; }
    actualizarTodo();
}"""

regex = re.compile(r"async function guardarTransaccion\(e\) \{.*?\}\n\nasync function guardarCredito", re.DOTALL)
js = regex.sub(new_trans + "\n\nasync function guardarCredito", js)

# And fix guardarCredito for monto_total bug:
new_cred = """async function guardarCredito(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const original = btn ? btn.innerHTML : 'Generar';
    if(btn) { btn.disabled = true; btn.innerHTML = 'Generando...'; }

    let tasa = parseFloat(document.getElementById('tasa_interes').value.replace(',', '.')) / 100.0;
    const bodyCredito = {
        entidad_id: parseInt(document.getElementById('entidad_id').value),
        concepto: document.getElementById('concepto').value,
        monto_total: getMonto('monto_total'),
        tasa_interes: tasa,
        tipo_tasa: document.getElementById('tipo_tasa').value,
        numero_cuotas: parseInt(document.getElementById('numero_cuotas').value),
        fecha_compra: document.getElementById('fecha_compra').value
    };
    
    await fetchAuth(`${API_URL}/creditos/`, { method: 'POST', body: JSON.stringify(bodyCredito) });
    e.target.reset();
    document.getElementById('fecha_compra').valueAsDate = new Date();
    if(btn) { btn.disabled = false; btn.innerHTML = original; }
    actualizarTodo();
}"""

regex2 = re.compile(r"async function guardarCredito\(e\) \{.*?\}\n\nasync function guardarSuscripcion", re.DOTALL)
js = regex2.sub(new_cred + "\n\nasync function guardarSuscripcion", js)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("guardarTransaccion and guardarCredito fixed!")
