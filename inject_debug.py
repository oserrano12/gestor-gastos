import re

js_path = 'frontend/app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Modify fetchAuth to alert 401 reason
new_fetch_auth = """async function fetchAuth(url, options = {}) {
    const token = localStorage.getItem('token');
    const headers = { ...options.headers };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (!headers['Content-Type']) headers['Content-Type'] = 'application/json';

    try {
        const res = await fetch(url, { ...options, headers });
        if (res.status === 401) {
            const data = await res.json().catch(() => ({}));
            alert(`Fallo de Seguridad 401 en: ${url}\\nRazón: ${data.detail || 'Sesión expirada'}`);
            cerrarSesion();
            throw new Error('Sesión expirada');
        }
        return res;
    } catch(err) {
        console.error("FetchAuth Error:", err);
        throw err;
    }
}"""

# Replace old fetchAuth
js = re.sub(r"async function fetchAuth\(url, options = \{\}\) \{[\s\S]*?return res;\n\}", new_fetch_auth, js)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("FetchAuth debug added")
