import re

# --- INDEX.HTML ---
html_path = 'frontend/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the select with an input that uses the same datalist!
old_select = """<select id="categoria_suscripcion_id" class="mt-1 block w-full rounded border-slate-300 p-2 border bg-white"></select>"""
new_datalist = """<input type="text" id="categoria_suscripcion_id" list="listaCategoriasAutocompletar" placeholder="Ej. Netflix, Gimnasio..." autocomplete="off" required class="mt-1 block w-full rounded border-slate-300 p-2 border bg-white">"""
html = html.replace(old_select, new_datalist)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# --- APP.JS ---
js_path = 'frontend/app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Fix the bodyTrans bug in guardarSuscripcion
old_guardar_suscrip = """async function guardarSuscripcion(e) {
    e.preventDefault();
    const body = {
        nombre: document.getElementById('nombre_suscripcion').value,
        monto: parseFloat(document.getElementById('monto_suscripcion').value),
        categoria_id: parseInt(document.getElementById('categoria_suscripcion_id').value),
        dia_cobro: parseInt(document.getElementById('dia_cobro').value)
    };
    await fetchAuth(`${API_URL}/suscripciones/`, { method: 'POST', body: JSON.stringify(bodyTrans) });
    e.target.reset();
    actualizarTodo();
}"""

new_guardar_suscrip = """async function guardarSuscripcion(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const original = btn.innerHTML;
    btn.disabled = true; btn.innerHTML = 'Guardando...';

    const nombreCat = document.getElementById('categoria_suscripcion_id').value.trim();
    let catId = null;
    const existe = dataCategorias.find(c => c.nombre.toLowerCase() === nombreCat.toLowerCase() && c.tipo === "Gasto");
    
    if (existe) {
        catId = existe.id;
    } else {
        const resNueva = await fetchAuth(`${API_URL}/categorias/`, {
            method: 'POST',
            body: JSON.stringify({ nombre: nombreCat, tipo: "Gasto" })
        });
        if(resNueva.ok) {
            const nuevaCat = await resNueva.json();
            dataCategorias.push(nuevaCat);
            catId = nuevaCat.id;
        } else {
            alert('Error al crear categoría de suscripción');
            btn.disabled = false; btn.innerHTML = original;
            return;
        }
    }

    const bodyTrans = {
        nombre: document.getElementById('nombre_suscripcion').value,
        monto: parseFloat(document.getElementById('monto_suscripcion').value),
        categoria_id: catId,
        dia_cobro: parseInt(document.getElementById('dia_cobro').value)
    };
    
    await fetchAuth(`${API_URL}/suscripciones/`, { method: 'POST', body: JSON.stringify(bodyTrans) });
    e.target.reset();
    btn.disabled = false; btn.innerHTML = original;
    actualizarTodo();
}"""

js = js.replace(old_guardar_suscrip, new_guardar_suscrip)

# Also remove the selectSusc.innerHTML lines in cargarCategorias
js = re.sub(r"const selectSusc = document\.getElementById\('categoria_suscripcion_id'\);\s*select\.innerHTML = ''; selectSusc\.innerHTML = '';\s*dataCategorias\.forEach\(c => \{\s*select\.innerHTML \+= `<option value=\"\$\{c\.id\}\">\$\{c\.nombre\} \(\$\{c\.tipo\}\)</option>`;\s*if\(c\.tipo === 'Gasto'\) selectSusc\.innerHTML \+= `<option value=\"\$\{c\.id\}\">\$\{c\.nombre\}</option>`;\s*\}\);", 
"// select categories is handled by datalist now", js)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Fix Suscripciones V2 aplicado.")
