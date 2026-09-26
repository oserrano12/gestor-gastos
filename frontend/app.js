const API_URL = 'http://localhost:8000/api';

// Inicialización de la App
document.addEventListener('DOMContentLoaded', async () => {
    // 1. Configurar PWA y Service Worker
    setupPWA();
    
    // 2. Asegurar que exista al menos una Entidad Crediticia (Banco)
    await inicializarEntidad();

    // 3. Cargar las cuotas pendientes
    cargarCuotas();

    // 4. Configurar el formulario
    document.getElementById('formCredito').addEventListener('submit', guardarCredito);
});

// --- PWA Setup ---
let promptInstalacion;
function setupPWA() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .catch(error => console.log('SW falló:', error));
    }

    const btnInstalar = document.getElementById('btnInstalar');
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        promptInstalacion = e;
        btnInstalar.classList.remove('hidden');
    });

    btnInstalar.addEventListener('click', async () => {
        if (!promptInstalacion) return;
        promptInstalacion.prompt();
        const { outcome } = await promptInstalacion.userChoice;
        if (outcome === 'accepted') btnInstalar.classList.add('hidden');
        promptInstalacion = null;
    });
}

// --- Lógica Financiera / API ---

// Auto-crear un banco para que no falle el registro si la BD está vacía
async function inicializarEntidad() {
    try {
        const res = await fetch(`${API_URL}/entidades/`);
        const entidades = await res.json();
        
        if (entidades.length === 0) {
            console.log("Creando entidad por defecto...");
            const nueva = await fetch(`${API_URL}/entidades/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nombre: "Mi Tarjeta Principal",
                    dia_corte: 15,
                    dia_limite_pago: 5
                })
            });
            const data = await nueva.json();
            document.getElementById('entidad_id').value = data.id;
        } else {
            document.getElementById('entidad_id').value = entidades[0].id;
        }
    } catch (e) {
        console.error("No se pudo conectar a la API. ¿Está encendido el servidor?", e);
    }
}

// Guardar el crédito
async function guardarCredito(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Guardando...';

    // El usuario ingresa 2.15%, lo dividimos entre 100 para enviar 0.0215
    let tasa = parseFloat(document.getElementById('tasa_interes').value);
    tasa = tasa / 100.0;

    const bodyData = {
        entidad_id: parseInt(document.getElementById('entidad_id').value),
        concepto: document.getElementById('concepto').value,
        monto_total: parseFloat(document.getElementById('monto_total').value),
        tasa_interes: tasa,
        tipo_tasa: document.getElementById('tipo_tasa').value,
        numero_cuotas: parseInt(document.getElementById('numero_cuotas').value),
        fecha_compra: document.getElementById('fecha_compra').value
    };

    try {
        const res = await fetch(`${API_URL}/creditos/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bodyData)
        });

        if (res.ok) {
            alert('¡Crédito y tabla de amortización generados con éxito!');
            e.target.reset();
            cargarCuotas(); // Recargar la tabla
        } else {
            const err = await res.json();
            alert(`Error: ${JSON.stringify(err)}`);
        }
    } catch (error) {
        alert('Error de red. ¿Está el backend encendido?');
    } finally {
        btn.disabled = false;
        btn.innerText = 'Calcular y Guardar';
    }
}

// Cargar Cuotas
async function cargarCuotas() {
    const tbody = document.getElementById('tablaCuotas');
    try {
        const res = await fetch(`${API_URL}/cuotas/pendientes/`);
        const cuotas = await res.json();

        tbody.innerHTML = '';

        if (cuotas.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="px-4 py-8 text-center text-slate-500">No hay cuotas pendientes 🎉</td></tr>`;
            return;
        }

        // Formateador de moneda
        const money = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 });

        cuotas.forEach(cuota => {
            const tr = document.createElement('tr');
            tr.className = "hover:bg-slate-50 transition-colors";
            
            // Ver si la cuota está vencida
            const hoy = new Date();
            const vencimiento = new Date(cuota.fecha_vencimiento);
            const vencida = vencimiento < hoy;
            const badgeClase = vencida ? "bg-red-100 text-red-700 border-red-200" : "bg-blue-50 text-blue-700 border-blue-200";

            tr.innerHTML = `
                <td class="px-4 py-3 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs rounded border ${badgeClase}">
                        ${cuota.fecha_vencimiento}
                    </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap font-medium text-slate-700">Cuota ${cuota.numero_cuota}</td>
                <td class="px-4 py-3 whitespace-nowrap text-right text-slate-500">${money.format(cuota.capital)}</td>
                <td class="px-4 py-3 whitespace-nowrap text-right text-slate-500">${money.format(cuota.interes)}</td>
                <td class="px-4 py-3 whitespace-nowrap text-right font-bold text-slate-800">${money.format(cuota.cuota_total)}</td>
                <td class="px-4 py-3 whitespace-nowrap text-center">
                    <button class="bg-green-100 hover:bg-green-200 text-green-700 px-3 py-1 rounded text-xs font-semibold transition-colors" onclick="pagarCuota(${cuota.id})">
                        <i class="fa-solid fa-check"></i> Pagar
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="6" class="px-4 py-8 text-center text-red-500">Error al cargar datos. Verifica el backend.</td></tr>`;
    }
}

// Pagar cuota (simulado por ahora, solo para UI, requiere endpoint PUT en el backend)
function pagarCuota(id) {
    alert(`Funcionalidad de pago para la cuota ${id} se implementará en la próxima actualización.`);
}
