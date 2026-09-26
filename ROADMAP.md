# 🗺️ Roadmap de Gestor Financiero

Este documento mantiene un registro de las futuras implementaciones y mejoras planeadas para la aplicación.

## 🔐 Seguridad y Autenticación
- [ ] **Recuperación de Contraseñas Segura:** Reemplazar el sistema de recuperación de contraseña directo por un flujo seguro usando envío de correos electrónicos (requiere integración con `fastapi-mail` y SMTP de Gmail o SendGrid).

## 📱 Despliegue y Empaquetado
- [ ] **Empaquetado Nativo Móvil (.apk):** Firmar digitalmente el APK generado por PWABuilder (actualmente lanza error de "paquete no válido" por ser `unsigned`) o compilarlo localmente con Capacitor/Android Studio para su distribución oficial.
- [ ] **Empaquetado Nativo Escritorio (.exe):** Convertir el frontend web en un programa de Windows utilizando Electron o Tauri.

## 📊 Funcionalidades Premium (Ideas)
- [ ] Filtros avanzados por fechas en la vista de movimientos.
- [ ] Soporte multimoneda o conversor de divisas.
- [ ] Alertas y notificaciones push para recordatorios de pago de cuotas y suscripciones.
