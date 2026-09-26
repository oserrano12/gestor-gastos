import re

html_path = 'frontend/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Cambiar el select de suscripciones por un input list
old_select = """<select id="suscripCategoria" required class="w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 p-2 border bg-slate-50"></select>"""
new_datalist = """<input type="text" id="suscripCategoriaInput" list="listaCategoriasAutocompletar" placeholder="Ej. Entretenimiento, Software..." autocomplete="off" required class="w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 p-2 border bg-slate-50">"""
html = html.replace(old_select, new_datalist)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

js_path = 'frontend/app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# 2. La función de cargar selectores ya no debe poblar `suscripCategoria` porque ya todos usan `listaCategoriasAutocompletar` (que es global).
# Wait, `suscripciones` are ALWAYS expenses ("Gasto"). So the datalist might have "Gasto" categories. But wait! The datalist is populated based on `tipoActivo` which is "Ingreso" or "Gasto" for transactions.
# If they are in the Suscripciones tab, they should see "Gasto" categories.
# We don't need a separate datalist, the same one works as long as it has "Gasto".
# Let's just make `guardarSuscripcion` use the same logic to detect/create the category!

new_guardar_suscrip = """// ================= CATEGORIA DINÁMICA SUSCRIPCIONES =================
    const nombreCat = document.getElementById('suscripCategoriaInput').value.trim();
    let categoriaId = null;
    const existe = dataCategorias.find(c => c.nombre.toLowerCase() === nombreCat.toLowerCase() && c.tipo === "Gasto");
    
    if (existe) {
        categoriaId = existe.id;
    } else {
        const resNueva = await fetchAuth(`${API_URL}/categorias/`, {
            method: 'POST',
            body: JSON.stringify({ nombre: nombreCat, tipo: "Gasto" })
        });
        if(resNueva.ok) {
            const nuevaCat = await resNueva.json();
            dataCategorias.push(nuevaCat);
            categoriaId = nuevaCat.id;
        } else {
            alert('Error al crear nueva categoría para suscripción.');
            btn.disabled = false; btn.innerHTML = original;
            return;
        }
    }

    const bodyTrans = {
        nombre: document.getElementById('suscripNombre').value,
        monto: parseFloat(document.getElementById('suscripMonto').value),
        categoria_id: categoriaId,
        dia_cobro: parseInt(document.getElementById('suscripDia').value)
    };"""

regex_body = re.compile(r"const body = \{\s*nombre: document\.getElementById\('suscripNombre'\)\.value,\s*monto: parseFloat\(document\.getElementById\('suscripMonto'\)\.value\),\s*categoria_id: parseInt\(document\.getElementById\('suscripCategoria'\)\.value\),\s*dia_cobro: parseInt\(document\.getElementById\('suscripDia'\)\.value\)\s*\};", re.DOTALL)
js = regex_body.sub(new_guardar_suscrip, js)

js = js.replace("body: JSON.stringify(body)", "body: JSON.stringify(bodyTrans)")

# Remove the old select population for suscripciones
old_poblar = "document.getElementById('suscripCategoria').innerHTML = catGastos;"
js = js.replace(old_poblar, "// Ya no se usa select, usa datalist")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("Suscripciones fix inyectado")
