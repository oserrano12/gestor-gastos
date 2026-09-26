const API_URL = 'https://gestor-gastos-ro0g.onrender.com/api';
const money = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 });

let dataCategorias = [];
let totalIngresosMonto = 0;
let totalGastosMonto = 0;

document.addEventListener('DOMContentLoaded', () => {
    // Listeners de Auth
    document.getElementById('formLogin').addEventListener('submit', loginUsuario);
    document.getElementById('formRegistro').addEventListener('submit', registrarUsuario);
    
    // Listeners de App
    document.getElementById('formTransaccion').addEventListener('submit', guardarTransaccion);
    document.getElementById('formCredito').addEventListener('submit', guardarCredito);
    document.getElementById('formSuscripcion').addEventListener('submit', guardarSuscripcion);

    verificarSesion();
});

// ================= AUTENTICACIÓN =================
function toggleAuth(modo) {
    document.getElementById('formLogin').classList.toggle('hidden', modo !== 'login');
    document.getElementById('formRegistro').classList.toggle('hidden', modo !== 'registro');
    document.getElementById('formRecuperar').classList.toggle('hidden', modo !== 'recuperar');
}

let resetTokenTemporal = null;

async function buscarCorreoRecuperacion() {
    const email = document.getElementById('recupEmail').value;
    if(!email) return alert('Ingresa un correo');
    
    try {
        const res = await fetch(`${API_URL}/usuarios/recuperar`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email})
        });
        if(res.ok) {
            const data = await res.json();
            resetTokenTemporal = data.reset_token;
            document.getElementById('recupEmail').disabled = true;
            document.getElementById('divNuevaClave').classList.remove('hidden');
            document.getElementById('btnBuscarCorreo').classList.add('hidden');
            document.getElementById('btnGuardarClave').classList.remove('hidden');
            alert('Cuenta encontrada. Ingresa tu nueva contraseña abajo.');
        } else {
            alert('Ese correo no existe en el sistema.');
        }
    } catch(e) { alert('Error de conexión'); }
}

async function guardarNuevaClave() {
    const new_password = document.getElementById('recupPassword').value;
    if(new_password.length < 4) return alert('La contraseña es muy corta');
    
    try {
        const res = await fetch(`${API_URL}/usuarios/resetear`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({token: resetTokenTemporal, new_password})
        });
        if(res.ok) {
            alert('¡Contraseña cambiada exitosamente! Ya puedes iniciar sesión.');
            document.getElementById('recupEmail').disabled = false;
            document.getElementById('recupEmail').value = '';
            document.getElementById('recupPassword').value = '';
            document.getElementById('divNuevaClave').classList.add('hidden');
            document.getElementById('btnBuscarCorreo').classList.remove('hidden');
            document.getElementById('btnGuardarClave').classList.add('hidden');
            toggleAuth('login');
        } else {
            alert('Error al cambiar la contraseña. Intenta de nuevo.');
        }
    } catch(e) { alert('Error de conexión'); }
}

function togglePassword(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

async function loginUsuario(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Conectando...';

    const formData = new URLSearchParams();
    formData.append('username', document.getElementById('loginEmail').value);
    formData.append('password', document.getElementById('loginPassword').value);

    try {
        const res = await fetch(`${API_URL}/usuarios/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('token', data.access_token);
            verificarSesion();
        } else {
            alert('Correo o contraseña incorrectos');
        }
    } catch (err) { alert('Error conectando al servidor'); }
    finally { btn.disabled = false; btn.innerHTML = originalText; }
}

async function registrarUsuario(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creando...';

    const body = {
        nombre: document.getElementById('regNombre').value,
        email: document.getElementById('regEmail').value,
        password: document.getElementById('regPassword').value
    };

    try {
        const res = await fetch(`${API_URL}/usuarios/registro`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        if (res.ok) {
            alert('¡Cuenta creada! Ahora inicia sesión.');
            toggleAuth('login');
        } else {
            const error = await res.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (err) { alert('Error conectando al servidor'); }
    finally { btn.disabled = false; btn.innerHTML = originalText; }
}

function cerrarSesion() {
    localStorage.removeItem('token');
    verificarSesion();
}

// Wrapper para Fetch Autorizado
async function fetchAuth(url, options = {}) {
    const token = localStorage.getItem('token');
    const headers = { ...options.headers };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (!headers['Content-Type']) headers['Content-Type'] = 'application/json';

    const res = await fetch(url, { ...options, headers });
    if (res.status === 401) {
        cerrarSesion();
        throw new Error('Sesión expirada');
    }
    return res;
}

// ================= APLICACIÓN PRINCIPAL =================
async function verificarSesion() {
    const token = localStorage.getItem('token');
    if (!token) {
        document.getElementById('vistaAuth').classList.remove('hidden');
        document.getElementById('appPrincipal').classList.add('hidden');
    } else {
        document.getElementById('vistaAuth').classList.add('hidden');
        document.getElementById('appPrincipal').classList.remove('hidden');
        document.getElementById('saludoUsuario').innerText = 'Hola, bienvenido de nuevo';
        
        document.getElementById('fecha_transaccion').valueAsDate = new Date();
        document.getElementById('fecha_compra').valueAsDate = new Date();
        
        await inicializarBaseDeDatos();
        await cargarCategorias();
        await actualizarTodo();
    }
}

// --- Pestañas ---
const tabs = ['inicio', 'movimientos', 'creditos', 'suscripciones'];
function switchTab(tabSeleccionado) {
    tabs.forEach(t => {
        document.getElementById(`vista${t.charAt(0).toUpperCase() + t.slice(1)}`).classList.toggle('hidden', t !== tabSeleccionado);
        const btn = document.getElementById(`btnTab${t.charAt(0).toUpperCase() + t.slice(1)}`);
        if(btn) {
            btn.className = t === tabSeleccionado 
                ? 'bg-blue-900 px-4 py-2 rounded shadow font-semibold hover:bg-blue-700 transition whitespace-nowrap' 
                : 'bg-blue-700 px-4 py-2 rounded font-semibold hover:bg-blue-600 transition whitespace-nowrap';
        }
    });
}

// --- Setup ---
async function inicializarBaseDeDatos() {
    try {
        const resE = await fetchAuth(`${API_URL}/entidades/`);
        const entidades = await resE.json();
        if (entidades.length === 0) {
            const nueva = await fetchAuth(`${API_URL}/entidades/`, { method: 'POST', body: JSON.stringify({ nombre: "Mi Tarjeta Principal", dia_corte: 15, dia_limite_pago: 5 }) });
            const data = await nueva.json();
            document.getElementById('entidad_id').value = data.id;
        } else {
            document.getElementById('entidad_id').value = entidades[0].id;
        }

        const resC = await fetchAuth(`${API_URL}/categorias/`);
        const cats = await resC.json();
        if (cats.length === 0) {
            await fetchAuth(`${API_URL}/categorias/`, { method: 'POST', body: JSON.stringify({ nombre: "Salario", tipo: "Ingreso" }) });
            await fetchAuth(`${API_URL}/categorias/`, { method: 'POST', body: JSON.stringify({ nombre: "Comida", tipo: "Gasto" }) });
            await fetchAuth(`${API_URL}/categorias/`, { method: 'POST', body: JSON.stringify({ nombre: "Transporte", tipo: "Gasto" }) });
        }
    } catch (e) { console.error(e); }
}

async function cargarCategorias() {
    try {
        const res = await fetchAuth(`${API_URL}/categorias/`);
        dataCategorias = await res.json();
        const select = document.getElementById('categoria_id');
        const selectSusc = document.getElementById('categoria_suscripcion_id');
        select.innerHTML = ''; selectSusc.innerHTML = '';
        dataCategorias.forEach(c => {
            select.innerHTML += `<option value="${c.id}">${c.nombre} (${c.tipo})</option>`;
            if(c.tipo === 'Gasto') selectSusc.innerHTML += `<option value="${c.id}">${c.nombre}</option>`;
        });
    } catch (e) { console.error(e); }
}

// --- Lógica Principal ---
async function actualizarTodo() {
    totalIngresosMonto = 0;
    totalGastosMonto = 0;
    
    await cargarTransacciones();
    await cargarCuotasYSuscripciones();
    
    const balance = totalIngresosMonto - totalGastosMonto;
    document.getElementById('dashIngresos').innerText = money.format(totalIngresosMonto);
    document.getElementById('dashGastos').innerText = money.format(totalGastosMonto);
    document.getElementById('dashBalance').innerText = money.format(balance);

    actualizarGrafico(totalIngresosMonto, totalGastosMonto);
}

// --- Gráfico Chart.js ---
let miGrafico = null;
function actualizarGrafico(ingresos, gastos) {
    const ctx = document.getElementById('graficoFinanzas').getContext('2d');
    
    if (miGrafico) {
        miGrafico.destroy();
    }

    if (ingresos === 0 && gastos === 0) return; // No dibujar si no hay datos

    miGrafico = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Ingresos Totales', 'Gastos y Deudas'],
            datasets: [{
                data: [ingresos, gastos],
                backgroundColor: ['#22c55e', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

// --- Exportar a Excel ---
function exportarExcel(idTabla, nombreArchivo) {
    const tabla = document.getElementById(idTabla);
    if (!tabla || tabla.innerText.includes('No hay') || tabla.innerText.includes('Aún no')) {
        alert("No hay datos para exportar");
        return;
    }
    
    // Subimos un nivel para agarrar el <table> completo y no solo el <tbody>
    const tablaElement = tabla.parentElement;
    
    const wb = XLSX.utils.table_to_book(tablaElement, {sheet: "Reporte"});
    XLSX.writeFile(wb, `${nombreArchivo}_${new Date().toISOString().split('T')[0]}.xlsx`);
}

async function cargarTransacciones() {
    const tbodyFull = document.getElementById('tablaTransacciones');
    const tbodyDash = document.getElementById('dashTablaMovimientos');
    try {
        const res = await fetchAuth(`${API_URL}/transacciones/`);
        const txs = await res.json();
        tbodyFull.innerHTML = ''; tbodyDash.innerHTML = '';

        if (txs.length === 0) {
            tbodyFull.innerHTML = `<tr><td colspan="4" class="px-4 py-8 text-center text-slate-500">No hay movimientos.</td></tr>`;
            tbodyDash.innerHTML = `<tr><td class="py-4 text-slate-500 text-center">Aún no hay movimientos.</td></tr>`;
            return;
        }

        const txsReversadas = [...txs].reverse();
        txsReversadas.forEach((t, i) => {
            const esIngreso = t.categoria.tipo === 'Ingreso';
            if (esIngreso) totalIngresosMonto += parseFloat(t.monto);
            else totalGastosMonto += parseFloat(t.monto);

            const color = esIngreso ? 'text-green-600' : 'text-red-600';
            const signo = esIngreso ? '+' : '-';

            tbodyFull.innerHTML += `
                <tr class="hover:bg-slate-50">
                    <td class="px-4 py-3 whitespace-nowrap text-slate-600">${t.fecha}</td>
                    <td class="px-4 py-3 whitespace-nowrap"><span class="px-2 py-1 text-xs rounded bg-slate-100 border text-slate-600">${t.categoria.nombre}</span></td>
                    <td class="px-4 py-3 text-slate-700">${t.descripcion || '-'}</td>
                    <td class="px-4 py-3 whitespace-nowrap text-right font-bold ${color}">${signo}${money.format(t.monto)}</td>
                </tr>
            `;

            if (i < 5) {
                tbodyDash.innerHTML += `
                    <tr class="border-b border-slate-50 last:border-0">
                        <td class="py-2 text-slate-600 font-medium">${t.descripcion || t.categoria.nombre}</td>
                        <td class="py-2 text-xs text-slate-400">${t.fecha}</td>
                        <td class="py-2 text-right font-bold ${color}">${signo}${money.format(t.monto)}</td>
                    </tr>
                `;
            }
        });
    } catch (e) {}
}

async function cargarCuotasYSuscripciones() {
    const tbodyCuotas = document.getElementById('tablaCuotas');
    const tbodySusc = document.getElementById('tablaSuscripciones');
    const tbodyDashPagos = document.getElementById('dashTablaPagos');
    
    let proximosPagos = [];

    try {
        const resC = await fetchAuth(`${API_URL}/cuotas/pendientes/`);
        const cuotas = await resC.json();
        tbodyCuotas.innerHTML = '';
        if (cuotas.length === 0) {
            tbodyCuotas.innerHTML = `<tr><td colspan="5" class="px-4 py-8 text-center text-slate-500">No tienes deudas activas.</td></tr>`;
        } else {
            cuotas.forEach(c => {
                totalGastosMonto += parseFloat(c.cuota_total);
                proximosPagos.push({ tipo: 'Cuota Crédito', nombre: `Cuota ${c.numero_cuota}`, monto: parseFloat(c.cuota_total), vencimiento: c.fecha_vencimiento });

                const vencida = new Date(c.fecha_vencimiento) < new Date();
                const badge = vencida ? "bg-red-100 text-red-700" : "bg-blue-50 text-blue-700";
                tbodyCuotas.innerHTML += `
                    <tr class="hover:bg-slate-50">
                        <td class="px-4 py-3"><span class="px-2 py-1 text-xs rounded border ${badge}">${c.fecha_vencimiento}</span></td>
                        <td class="px-4 py-3 text-slate-700">Cuota ${c.numero_cuota}</td>
                        <td class="px-4 py-3 text-right text-slate-500">${money.format(c.capital)}</td>
                        <td class="px-4 py-3 text-right text-slate-500">${money.format(c.interes)}</td>
                        <td class="px-4 py-3 text-right font-bold text-slate-800">${money.format(c.cuota_total)}</td>
                    </tr>
                `;
            });
        }

        const resS = await fetchAuth(`${API_URL}/suscripciones/`);
        const suscripciones = await resS.json();
        tbodySusc.innerHTML = '';
        if (suscripciones.length === 0) {
            tbodySusc.innerHTML = `<tr><td colspan="4" class="px-4 py-8 text-center text-slate-500">No tienes suscripciones.</td></tr>`;
        } else {
            suscripciones.forEach(s => {
                totalGastosMonto += parseFloat(s.monto);
                const hoy = new Date();
                let fechaCobro = new Date(hoy.getFullYear(), hoy.getMonth(), s.dia_cobro);
                if (fechaCobro < hoy) fechaCobro.setMonth(fechaCobro.getMonth() + 1);
                const fStr = fechaCobro.toISOString().split('T')[0];

                proximosPagos.push({ tipo: 'Suscripción', nombre: s.nombre, monto: parseFloat(s.monto), vencimiento: fStr });

                tbodySusc.innerHTML += `
                    <tr class="hover:bg-slate-50">
                        <td class="px-4 py-3 font-medium text-slate-700">${s.nombre}</td>
                        <td class="px-4 py-3 text-center text-slate-600">Día ${s.dia_cobro}</td>
                        <td class="px-4 py-3 text-right font-bold text-red-600">-${money.format(s.monto)}</td>
                        <td class="px-4 py-3 text-center"><span class="px-2 py-1 text-xs rounded bg-green-100 text-green-700">Activa</span></td>
                    </tr>
                `;
            });
        }

        tbodyDashPagos.innerHTML = '';
        if (proximosPagos.length === 0) {
            tbodyDashPagos.innerHTML = `<tr><td class="py-4 text-slate-500 text-center">Nada que pagar pronto.</td></tr>`;
        } else {
            proximosPagos.sort((a,b) => new Date(a.vencimiento) - new Date(b.vencimiento));
            proximosPagos.slice(0, 6).forEach(p => {
                const badge = p.tipo === 'Suscripción' ? 'bg-purple-100 text-purple-700' : 'bg-orange-100 text-orange-700';
                tbodyDashPagos.innerHTML += `
                    <tr class="border-b border-slate-50 last:border-0">
                        <td class="py-2 text-slate-700 font-medium">${p.nombre}</td>
                        <td class="py-2"><span class="px-2 py-0.5 text-xs rounded ${badge}">${p.tipo}</span></td>
                        <td class="py-2 text-xs text-slate-500">${p.vencimiento}</td>
                        <td class="py-2 text-right font-bold text-red-600">-${money.format(p.monto)}</td>
                    </tr>
                `;
            });
        }
    } catch (e) { console.error(e); }
}

async function guardarTransaccion(e) {
    e.preventDefault();
    const body = {
        categoria_id: parseInt(document.getElementById('categoria_id').value),
        monto: parseFloat(document.getElementById('monto_transaccion').value),
        fecha: document.getElementById('fecha_transaccion').value,
        descripcion: document.getElementById('desc_transaccion').value
    };
    await fetchAuth(`${API_URL}/transacciones/`, { method: 'POST', body: JSON.stringify(body) });
    e.target.reset();
    document.getElementById('fecha_transaccion').valueAsDate = new Date();
    actualizarTodo();
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
    await fetchAuth(`${API_URL}/creditos/`, { method: 'POST', body: JSON.stringify(body) });
    e.target.reset();
    document.getElementById('fecha_compra').valueAsDate = new Date();
    actualizarTodo();
}

async function guardarSuscripcion(e) {
    e.preventDefault();
    const body = {
        nombre: document.getElementById('nombre_suscripcion').value,
        monto: parseFloat(document.getElementById('monto_suscripcion').value),
        categoria_id: parseInt(document.getElementById('categoria_suscripcion_id').value),
        dia_cobro: parseInt(document.getElementById('dia_cobro').value)
    };
    await fetchAuth(`${API_URL}/suscripciones/`, { method: 'POST', body: JSON.stringify(body) });
    e.target.reset();
    actualizarTodo();
}

// Registro PWA
if ('serviceWorker' in navigator) { window.addEventListener('load', () => { navigator.serviceWorker.register('/sw.js'); }); }
