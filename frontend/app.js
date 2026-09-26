const API_URL = 'http://localhost:8000/api';
const money = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 });

let dataCategorias = [];
let totalIngresosMonto = 0;
let totalGastosMonto = 0;

document.addEventListener('DOMContentLoaded', async () => {
    // Inicializar Fechas por defecto
    document.getElementById('fecha_transaccion').valueAsDate = new Date();
    document.getElementById('fecha_compra').valueAsDate = new Date();

    await inicializarBaseDeDatos();
    await cargarCategorias();
    await actualizarDashboard();

    document.getElementById('formTransaccion').addEventListener('submit', guardarTransaccion);
    document.getElementById('formCredito').addEventListener('submit', guardarCredito);
});

// --- Pestañas ---
function switchTab(tab) {
    document.getElementById('vistaBalance').classList.toggle('hidden', tab !== 'balance');
    document.getElementById('vistaCreditos').classList.toggle('hidden', tab !== 'creditos');
    document.getElementById('vistaSuscripciones').classList.toggle('hidden', tab !== 'suscripciones');
    
    document.getElementById('btnTabBalance').className = tab === 'balance' ? 'bg-blue-900 px-4 py-2 rounded shadow font-semibold hover:bg-blue-700 transition' : 'bg-blue-700 px-4 py-2 rounded font-semibold hover:bg-blue-600 transition';
    document.getElementById('btnTabCreditos').className = tab === 'creditos' ? 'bg-blue-900 px-4 py-2 rounded shadow font-semibold hover:bg-blue-700 transition' : 'bg-blue-700 px-4 py-2 rounded font-semibold hover:bg-blue-600 transition';
    document.getElementById('btnTabSuscripciones').className = tab === 'suscripciones' ? 'bg-blue-900 px-4 py-2 rounded shadow font-semibold hover:bg-blue-700 transition' : 'bg-blue-700 px-4 py-2 rounded font-semibold hover:bg-blue-600 transition';
}

// --- Setup Base ---
async function inicializarBaseDeDatos() {
    try {
        // 1. Asegurar banco
        const resE = await fetch(`${API_URL}/entidades/`);
        const entidades = await resE.json();
        if (entidades.length === 0) {
            const nueva = await fetch(`${API_URL}/entidades/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ nombre: "Mi Tarjeta Principal", dia_corte: 15, dia_limite_pago: 5 }) });
            const data = await nueva.json();
            document.getElementById('entidad_id').value = data.id;
        } else {
            document.getElementById('entidad_id').value = entidades[0].id;
        }

        // 2. Asegurar categorias
        const resC = await fetch(`${API_URL}/categorias/`);
        const cats = await resC.json();
        if (cats.length === 0) {
            await fetch(`${API_URL}/categorias/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ nombre: "Salario", tipo: "Ingreso" }) });
            await fetch(`${API_URL}/categorias/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ nombre: "Comida", tipo: "Gasto" }) });
            await fetch(`${API_URL}/categorias/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ nombre: "Transporte", tipo: "Gasto" }) });
        }
    } catch (e) {
        console.error("Error inicializando BD local", e);
    }
}

async function cargarCategorias() {
    try {
        const res = await fetch(`${API_URL}/categorias/`);
        dataCategorias = await res.json();
        const select = document.getElementById('categoria_id');
        const selectSusc = document.getElementById('categoria_suscripcion_id');
        if(select) select.innerHTML = '';
        if(selectSusc) selectSusc.innerHTML = '';
        
        dataCategorias.forEach(c => {
            if(select) select.innerHTML += `<option value="${c.id}">${c.nombre} (${c.tipo})</option>`;
            if(selectSusc && c.tipo === 'Gasto') selectSusc.innerHTML += `<option value="${c.id}">${c.nombre}</option>`;
        });
    } catch (e) { console.error(e); }
}

// --- Funciones Principales ---
async function actualizarDashboard() {
    await cargarTransacciones();
    await cargarCuotas();
    await cargarSuscripciones();
    
    // Calcular Balance Total
    const balance = totalIngresosMonto - totalGastosMonto;
    document.getElementById('totalIngresos').innerText = money.format(totalIngresosMonto);
    document.getElementById('totalGastos').innerText = money.format(totalGastosMonto);
    document.getElementById('balanceTotal').innerText = money.format(balance);
}

async function cargarTransacciones() {
    const tbody = document.getElementById('tablaTransacciones');
    totalIngresosMonto = 0;
    totalGastosMonto = 0;

    try {
        const res = await fetch(`${API_URL}/transacciones/`);
        const transacciones = await res.json();
        tbody.innerHTML = '';

        if (transacciones.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="px-4 py-8 text-center text-slate-500">No hay movimientos aún.</td></tr>`;
            return;
        }

        // Ordenar más recientes primero
        transacciones.reverse().forEach(t => {
            const esIngreso = t.categoria.tipo === 'Ingreso';
            if (esIngreso) totalIngresosMonto += parseFloat(t.monto);
            else totalGastosMonto += parseFloat(t.monto);

            const color = esIngreso ? 'text-green-600' : 'text-red-600';
            const signo = esIngreso ? '+' : '-';

            tbody.innerHTML += `
                <tr class="hover:bg-slate-50">
                    <td class="px-4 py-3 whitespace-nowrap text-slate-600">${t.fecha}</td>
                    <td class="px-4 py-3 whitespace-nowrap"><span class="px-2 py-1 text-xs rounded bg-slate-100 border text-slate-600">${t.categoria.nombre}</span></td>
                    <td class="px-4 py-3 whitespace-nowrap text-slate-700">${t.descripcion || '-'}</td>
                    <td class="px-4 py-3 whitespace-nowrap text-right font-bold ${color}">${signo}${money.format(t.monto)}</td>
                </tr>
            `;
        });
    } catch (e) {}
}

async function cargarCuotas() {
    const tbody = document.getElementById('tablaCuotas');
    try {
        const res = await fetch(`${API_URL}/cuotas/pendientes/`);
        const cuotas = await res.json();
        tbody.innerHTML = '';

        if (cuotas.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="px-4 py-8 text-center text-slate-500">No tienes deudas activas 🎉</td></tr>`;
            return;
        }

        let totalCuotasMes = 0;
        cuotas.forEach(c => {
            totalCuotasMes += parseFloat(c.cuota_total);
            const vencida = new Date(c.fecha_vencimiento) < new Date();
            const badge = vencida ? "bg-red-100 text-red-700" : "bg-blue-50 text-blue-700";

            tbody.innerHTML += `
                <tr class="hover:bg-slate-50">
                    <td class="px-4 py-3"><span class="px-2 py-1 text-xs rounded border ${badge}">${c.fecha_vencimiento}</span></td>
                    <td class="px-4 py-3 text-slate-700">Cuota ${c.numero_cuota}</td>
                    <td class="px-4 py-3 text-right text-slate-500">${money.format(c.capital)}</td>
                    <td class="px-4 py-3 text-right text-slate-500">${money.format(c.interes)}</td>
                    <td class="px-4 py-3 text-right font-bold text-slate-800">${money.format(c.cuota_total)}</td>
                </tr>
            `;
        });
        
        // Sumamos las cuotas a los gastos totales (porque también salen de tu bolsillo)
        totalGastosMonto += totalCuotasMes;

    } catch (e) {}
}

// ... (cargarTransacciones and cargarCuotas remains)
async function cargarSuscripciones() {
    const tbody = document.getElementById('tablaSuscripciones');
    try {
        const res = await fetch(`${API_URL}/suscripciones/`);
        const suscripciones = await res.json();
        
        if(tbody) tbody.innerHTML = '';

        if (suscripciones.length === 0) {
            if(tbody) tbody.innerHTML = `<tr><td colspan="4" class="px-4 py-8 text-center text-slate-500">No hay suscripciones activas.</td></tr>`;
            return;
        }

        let totalSuscripcionesMes = 0;
        suscripciones.forEach(s => {
            totalSuscripcionesMes += parseFloat(s.monto);
            if(tbody) {
                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50">
                        <td class="px-4 py-3 font-medium text-slate-700">${s.nombre}</td>
                        <td class="px-4 py-3 text-center text-slate-600">Día ${s.dia_cobro}</td>
                        <td class="px-4 py-3 text-right font-bold text-red-600">-${money.format(s.monto)}</td>
                        <td class="px-4 py-3 text-center"><span class="px-2 py-1 text-xs rounded bg-green-100 text-green-700">Activa</span></td>
                    </tr>
                `;
            }
        });
        
        // Sumamos al gasto mensual proyectado
        totalGastosMonto += totalSuscripcionesMes;
    } catch (e) {}
}

async function guardarTransaccion(e) {
    e.preventDefault();
    const body = {
        categoria_id: parseInt(document.getElementById('categoria_id').value),
        monto: parseFloat(document.getElementById('monto_transaccion').value),
        fecha: document.getElementById('fecha_transaccion').value,
        descripcion: document.getElementById('desc_transaccion').value
    };
    await fetch(`${API_URL}/transacciones/`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body) });
    e.target.reset();
    document.getElementById('fecha_transaccion').valueAsDate = new Date();
    actualizarDashboard();
}

async function guardarCredito(e) {
    e.preventDefault();
    let tasa = parseFloat(document.getElementById('tasa_interes').value) / 100.0;
    const body = {
        entidad_id: parseInt(document.getElementById('entidad_id').value),
        concepto: document.getElementById('concepto').value,
        monto_total: parseFloat(document.getElementById('monto_total').value),
        tasa_interes: tasa,
        tipo_tasa: document.getElementById('tipo_tasa').value,
        numero_cuotas: parseInt(document.getElementById('numero_cuotas').value),
        fecha_compra: document.getElementById('fecha_compra').value
    };
    await fetch(`${API_URL}/creditos/`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body) });
    e.target.reset();
    document.getElementById('fecha_compra').valueAsDate = new Date();
    actualizarDashboard();
}

async function guardarSuscripcion(e) {
    e.preventDefault();
    const body = {
        nombre: document.getElementById('nombre_suscripcion').value,
        monto: parseFloat(document.getElementById('monto_suscripcion').value),
        categoria_id: parseInt(document.getElementById('categoria_suscripcion_id').value),
        dia_cobro: parseInt(document.getElementById('dia_cobro').value)
    };
    await fetch(`${API_URL}/suscripciones/`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body) });
    e.target.reset();
    actualizarDashboard();
}

document.addEventListener('DOMContentLoaded', () => {
    const formSuscripcion = document.getElementById('formSuscripcion');
    if(formSuscripcion) formSuscripcion.addEventListener('submit', guardarSuscripcion);
});

