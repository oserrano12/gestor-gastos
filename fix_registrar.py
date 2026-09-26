import re

js_path = 'frontend/app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

correct_registrar = """async function registrarUsuario(e) {
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
            document.getElementById('vistaAuth').classList.remove('hidden');
            document.getElementById('appPrincipal').classList.add('hidden');
            e.target.reset();
        } else {
            const data = await res.json();
            alert('Error: ' + (data.detail || 'No se pudo crear la cuenta'));
        }
    } catch(err) {
        console.error(err);
    } finally {
        if(btn) {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }
}"""

# Use regex to find async function registrarUsuario(e) { ... }
# The regex should capture everything until the NEXT async function or standard function
regex = re.compile(r"async function registrarUsuario\(e\) \{.*?\}\n\nasync function", re.DOTALL)
js = regex.sub(correct_registrar + "\n\nasync function", js)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("registrarUsuario fixed!")
