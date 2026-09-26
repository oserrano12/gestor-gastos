import re

# --- INDEX.HTML ---
html_path = 'frontend/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Reemplazar el select de categorias por un input list (Buscador inteligente)
old_select = """<select id="transCategoria" required class="w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 p-2 border bg-slate-50"></select>"""
new_datalist = """<input type="text" id="transCategoriaInput" list="listaCategoriasAutocompletar" placeholder="Escribe o selecciona..." autocomplete="off" required class="w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 p-2 border bg-slate-50">
                                <datalist id="listaCategoriasAutocompletar"></datalist>"""
html = html.replace(old_select, new_datalist)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# --- APP.JS ---
js_path = 'frontend/app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Cuando renderizamos las opciones, en vez de poblar el select, poblamos el datalist
old_poblar = """        // Poblar Selects
        const select = document.getElementById('transCategoria');
        select.innerHTML = dataCategorias.filter(c => c.tipo === tipoActivo).map(c => `<option value="${c.id}">${c.nombre}</option>`).join('');"""

new_poblar = """        // Poblar Datalist Inteligente
        const datalist = document.getElementById('listaCategoriasAutocompletar');
        document.getElementById('transCategoriaInput').value = ''; // limpiar al cambiar pestaña
        datalist.innerHTML = dataCategorias.filter(c => c.tipo === tipoActivo).map(c => `<option value="${c.nombre}">`).join('');"""
js = js.replace(old_poblar, new_poblar)

# 2. En guardarTransaccion, interceptar el nombre, buscar id, si no existe CREARLA
old_guardar_trans = """        monto: parseFloat(document.getElementById('transMonto').value),
        fecha: document.getElementById('transFecha').value,
        categoria_id: parseInt(document.getElementById('transCategoria').value),
        cuenta_id: parseInt(document.getElementById('transCuenta').value),
        tipo: tipo"""

new_guardar_trans = """// ================= CATEGORIA DINÁMICA =================
    const nombreCat = document.getElementById('transCategoriaInput').value.trim();
    let categoriaId = null;
    const existe = dataCategorias.find(c => c.nombre.toLowerCase() === nombreCat.toLowerCase() && c.tipo === tipo);
    
    if (existe) {
        categoriaId = existe.id;
    } else {
        // Crear categoría al vuelo
        const resNueva = await fetchAuth(`${API_URL}/categorias/`, {
            method: 'POST',
            body: JSON.stringify({ nombre: nombreCat, tipo: tipo })
        });
        if(resNueva.ok) {
            const nuevaCat = await resNueva.json();
            dataCategorias.push(nuevaCat);
            categoriaId = nuevaCat.id;
        } else {
            alert('Error al crear nueva categoría automáticamente.');
            btn.disabled = false; btn.innerHTML = original;
            return;
        }
    }

    const bodyTrans = {
        monto: parseFloat(document.getElementById('transMonto').value),
        fecha: document.getElementById('transFecha').value,
        categoria_id: categoriaId,
        cuenta_id: parseInt(document.getElementById('transCuenta').value),
        tipo: tipo
    };"""

# Debo reemplazar la declaración "const body = {" y su contenido, hasta antes de fetchAuth
# Usaré expresiones regulares para reemplazarlo limpiamente.
regex_body = re.compile(r"const body = \{(.*?)\};", re.DOTALL)
js = regex_body.sub(new_guardar_trans, js, count=1) # solo el primero que es guardarTransaccion

# Tambien debo actualizar la llamada de fetchAuth en guardarTransaccion para que use bodyTrans
js = js.replace("body: JSON.stringify(body)", "body: JSON.stringify(bodyTrans)", 1)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Autocomplete injectado")
