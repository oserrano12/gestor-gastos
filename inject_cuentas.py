import re

# --- INDEX.HTML ---
html_path = 'frontend/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Cuentas Tab Button
tab_cuentas = """
                    <button id="btnTabSuscripciones" onclick="cambiarTab('vistaSuscripciones')" class="tab-btn w-full text-left md:w-auto px-4 py-3 rounded-lg font-semibold text-slate-500 hover:text-blue-600 hover:bg-blue-50 transition-colors">
                        <i class="fa-solid fa-repeat w-5"></i> Suscripciones
                    </button>
                    <!-- NUEVO TAB -->
                    <button id="btnTabCuentas" onclick="cambiarTab('vistaCuentas')" class="tab-btn w-full text-left md:w-auto px-4 py-3 rounded-lg font-semibold text-slate-500 hover:text-blue-600 hover:bg-blue-50 transition-colors">
                        <i class="fa-solid fa-wallet w-5"></i> Cuentas
                    </button>
"""
html = html.replace("""
                    <button id="btnTabSuscripciones" onclick="cambiarTab('vistaSuscripciones')" class="tab-btn w-full text-left md:w-auto px-4 py-3 rounded-lg font-semibold text-slate-500 hover:text-blue-600 hover:bg-blue-50 transition-colors">
                        <i class="fa-solid fa-repeat w-5"></i> Suscripciones
                    </button>
""", tab_cuentas)

# 2. Add Cuentas Select to Transaction Form
select_cuenta = """
                            <div>
                                <label class="block text-sm font-semibold text-slate-600 mb-1">Categoría</label>
                                <select id="transCategoria" required class="w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 p-2 border bg-slate-50"></select>
                            </div>
                            <!-- NUEVO SELECT -->
                            <div>
                                <label class="block text-sm font-semibold text-slate-600 mb-1">Cuenta/Billetera</label>
                                <select id="transCuenta" required class="w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 p-2 border bg-slate-50"></select>
                            </div>
"""
html = html.replace("""
                            <div>
                                <label class="block text-sm font-semibold text-slate-600 mb-1">Categoría</label>
                                <select id="transCategoria" required class="w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 p-2 border bg-slate-50"></select>
                            </div>
""", select_cuenta)

# 3. Add Cuentas View Section
vista_cuentas = """
            <!-- VISTA CUENTAS -->
            <div id="vistaCuentas" class="tab-content hidden space-y-6">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="lg:col-span-1 bg-white rounded-xl shadow-md p-6 h-fit border-t-4 border-blue-500">
                        <h2 class="text-lg font-bold mb-4 text-slate-700 border-b pb-2"><i class="fa-solid fa-plus text-blue-500 mr-2"></i> Nueva Cuenta</h2>
                        <form id="formCuenta" class="space-y-4">
                            <div>
                                <label class="block text-sm font-semibold text-slate-600 mb-1">Nombre de la Cuenta</label>
                                <input type="text" id="cuentaNombre" placeholder="Ej. Bancolombia, Nequi..." required class="w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 p-2 border bg-slate-50">
                            </div>
                            <div>
                                <label class="block text-sm font-semibold text-slate-600 mb-1">Color (Opcional)</label>
                                <input type="color" id="cuentaColor" value="#3b82f6" class="w-full h-10 rounded cursor-pointer border-slate-300">
                            </div>
                            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg shadow transition-colors">
                                Crear Cuenta
                            </button>
                        </form>
                    </div>
                    <div class="lg:col-span-2 bg-white rounded-xl shadow-md p-6">
                        <h2 class="text-lg font-bold mb-4 text-slate-700 border-b pb-2"><i class="fa-solid fa-wallet text-blue-500 mr-2"></i> Mis Cuentas y Saldos</h2>
                        <div id="listaCuentas" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <!-- Cards de cuentas -->
                        </div>
                    </div>
                </div>
            </div>
            
        </main>
"""
html = html.replace("        </main>", vista_cuentas)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)


# --- APP.JS ---
js_path = 'frontend/app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Globals & Setup
js = js.replace("let dataCategorias = [];", "let dataCategorias = [];\nlet dataCuentas = [];")

# 2. Add form listener
js = js.replace("document.getElementById('formCredito').addEventListener('submit', guardarCredito);", "document.getElementById('formCredito').addEventListener('submit', guardarCredito);\n    document.getElementById('formCuenta').addEventListener('submit', crearCuenta);")

# 3. Add Cuentas to actualizarTodo
actualizar = """
    try {
        const resCat = await fetchAuth(`${API_URL}/categorias/`);
        dataCategorias = await resCat.json();
        const resCue = await fetchAuth(`${API_URL}/cuentas/`);
        dataCuentas = await resCue.json();
"""
js = js.replace("""
    try {
        const resCat = await fetchAuth(`${API_URL}/categorias/`);
        dataCategorias = await resCat.json();
""", actualizar)

# 4. Render Cuentas & fill selects
render_cuentas = """
        // Poblar Select de Cuentas
        const selectCuenta = document.getElementById('transCuenta');
        selectCuenta.innerHTML = dataCuentas.map(c => `<option value="${c.id}">${c.nombre}</option>`).join('');

        renderizarCuentas();
"""
js = js.replace("        renderizarSuscripciones(dataSus);", "        renderizarSuscripciones(dataSus);\n" + render_cuentas)

# 5. Modify renderResumen to sum accounts instead of calculating from transactions
# Wait, currently the backend doesn't calculate saldo in the Cuenta model automatically.
# We will just sum all Incomes and Expenses globally for now, or sum by account.
# Let's keep renderResumen intact, it already calculates correctly.

# 6. Guardar Transaccion includes cuenta_id
guardar_trans = """
        monto: parseFloat(document.getElementById('transMonto').value),
        fecha: document.getElementById('transFecha').value,
        categoria_id: parseInt(document.getElementById('transCategoria').value),
        cuenta_id: parseInt(document.getElementById('transCuenta').value),
        tipo: tipo
"""
js = js.replace("""
        monto: parseFloat(document.getElementById('transMonto').value),
        fecha: document.getElementById('transFecha').value,
        categoria_id: parseInt(document.getElementById('transCategoria').value),
        tipo: tipo
""", guardar_trans)

# 7. Add crearCuenta and renderizarCuentas logic
logica_cuentas = """
// ================= CUENTAS =================
async function crearCuenta(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const original = btn.innerHTML;
    btn.disabled = true; btn.innerHTML = 'Creando...';
    
    const body = {
        nombre: document.getElementById('cuentaNombre').value,
        color: document.getElementById('cuentaColor').value
    };
    
    try {
        const res = await fetchAuth(`${API_URL}/cuentas/`, {
            method: 'POST',
            body: JSON.stringify(body)
        });
        if(res.ok) {
            e.target.reset();
            actualizarTodo();
        } else {
            alert('Error al crear cuenta');
        }
    } catch(err) { console.error(err); }
    finally { btn.disabled = false; btn.innerHTML = original; }
}

function renderizarCuentas() {
    const contenedor = document.getElementById('listaCuentas');
    if (dataCuentas.length === 0) {
        contenedor.innerHTML = '<p class="text-slate-500 text-sm">No tienes cuentas. Crea la primera arriba.</p>';
        return;
    }
    
    contenedor.innerHTML = dataCuentas.map(c => `
        <div class="border rounded-xl p-4 flex items-center shadow-sm" style="border-left: 4px solid ${c.color}">
            <div class="w-12 h-12 rounded-full flex items-center justify-center text-white mr-4" style="background-color: ${c.color}">
                <i class="fa-solid fa-wallet text-xl"></i>
            </div>
            <div>
                <p class="text-sm font-bold text-slate-500">${c.nombre}</p>
                <p class="text-xl font-bold text-slate-800">${money.format(c.saldo || 0)}</p>
            </div>
        </div>
    `).join('');
}
"""
js = js + "\n" + logica_cuentas

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Archivos modificados.")
