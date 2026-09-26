import re

html_path = 'frontend/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

vista_cuentas = """
            <!-- VISTA: CUENTAS -->
            <div id="vistaCuentas" class="hidden space-y-6">
                <h2 class="text-2xl font-bold text-slate-700 border-b pb-2">Gestión de Cuentas</h2>
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
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

        </div>
"""

# Insert before the closing tags
html = html.replace('        </div>\n    </div>\n\n    <script src="app.js?v=2"></script>', vista_cuentas + '\    </div>\n\n    <script src="app.js?v=3"></script>')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("formCuenta injected")
