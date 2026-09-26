import re

js_path = 'frontend/app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Add trash icon to Transacciones
old_trans_row = """<td class="px-4 py-3 whitespace-nowrap"><span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${colorClase} bg-opacity-20">${t.categoria.nombre}</span></td>"""
new_trans_row = """<td class="px-4 py-3 whitespace-nowrap"><span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${colorClase} bg-opacity-20">${t.categoria.nombre}</span></td>
<td class="px-4 py-3 whitespace-nowrap text-center">
    <button onclick="eliminarTransaccion(${t.id})" class="text-red-500 hover:text-red-700 transition" title="Eliminar"><i class="fa-solid fa-trash"></i></button>
</td>"""
js = js.replace(old_trans_row, new_trans_row)

# 2. Add trash icon to Suscripciones
old_susc_row = """<td class="px-4 py-3 whitespace-nowrap text-center"><span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Activa</span></td>"""
new_susc_row = """<td class="px-4 py-3 whitespace-nowrap text-center"><span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Activa</span></td>
<td class="px-4 py-3 whitespace-nowrap text-center">
    <button onclick="eliminarSuscripcion(${s.id})" class="text-red-500 hover:text-red-700 transition" title="Eliminar"><i class="fa-solid fa-trash"></i></button>
</td>"""
js = js.replace(old_susc_row, new_susc_row)

# 3. Add logic functions
logica_eliminar = """
// ================= ELIMINAR REGISTROS =================
async function eliminarTransaccion(id) {
    if(!confirm('¿Estás seguro de eliminar este movimiento? (Esto actualizará el saldo de tu cuenta)')) return;
    try {
        const res = await fetchAuth(`${API_URL}/transacciones/${id}`, { method: 'DELETE' });
        if(res.ok) actualizarTodo();
        else alert('Error al eliminar');
    } catch(e) { console.error(e); }
}

async function eliminarSuscripcion(id) {
    if(!confirm('¿Estás seguro de eliminar esta suscripción?')) return;
    try {
        const res = await fetchAuth(`${API_URL}/suscripciones/${id}`, { method: 'DELETE' });
        if(res.ok) actualizarTodo();
        else alert('Error al eliminar');
    } catch(e) { console.error(e); }
}
"""
js = js + "\n" + logica_eliminar

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

# --- INDEX.HTML ---
html_path = 'frontend/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add empty th for the trash icon column in both tables
html = html.replace('<th class="px-4 py-3 text-left">Categoría</th>\n                                    </tr>', '<th class="px-4 py-3 text-left">Categoría</th>\n                                        <th class="px-4 py-3 text-center">Acciones</th>\n                                    </tr>')
html = html.replace('<th class="px-4 py-3 text-center">Estado</th>\n                                    </tr>', '<th class="px-4 py-3 text-center">Estado</th>\n                                        <th class="px-4 py-3 text-center">Acciones</th>\n                                    </tr>')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Eliminar injectado")
