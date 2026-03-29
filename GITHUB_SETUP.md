#!/bin/bash
# Instrucciones finales para subir el proyecto a GitHub

cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║                  📤 INSTRUCCIONES PARA SUBIR A GITHUB                      ║
╚════════════════════════════════════════════════════════════════════════════╝

El proyecto está listo para ser subido a GitHub. Sigue estos pasos:

1️⃣  PRIMERA VEZ: Configura tu credencial de GitHub

   Opción A - Usar Personal Access Token (HTTPS - Recomendado):
   ─────────────────────────────────────────────────────────────
   
   a) Ve a: https://github.com/settings/tokens/new
   b) Crea un nuevo token con estos permisos:
      ✓ repo (full control of private repositories)
      ✓ write:packages
   c) Copia el token (aparece una sola vez)
   d) Guarda en lugar seguro
   
   e) Configura Git para usar el token:
      $ git config --global credential.helper store
   
   f) Haz push (te pedirá contraseña, pega el token):
      $ git push -u origin main
      
      Username: tu_usuario_github
      Password: tu_token_generado

   Opción B - Usar SSH (Más seguro, requiere config):
   ──────────────────────────────────────────────────
   
   a) Genera clave SSH (si no tienes):
      $ ssh-keygen -t ed25519 -C "tu_email@example.com"
   
   b) Agrega la clave pública a GitHub:
      https://github.com/settings/keys
   
   c) Prueba conexión:
      $ ssh -T git@github.com
   
   d) Cambia remote a SSH:
      $ git remote remove origin
      $ git remote add origin git@github.com:Jojonxtanx/Tunning-Nobara-Grub.git
   
   e) Haz push:
      $ git push -u origin main


2️⃣  HACER PUSH DEL CÓDIGO

   $ cd "Tunning-Nobara-Grub"
   $ git push -u origin main


3️⃣  VERIFICAR EN GITHUB

   ✅ Ve a: https://github.com/Jojonxtanx/Tunning-Nobara-Grub
   ✅ Verifica que todos los archivos aparezcan
   ✅ README.md se mostrará automáticamente


4️⃣  (OPCIONAL) CREAR RELEASE

   Haz clic en "Releases" → "Create a new release"
   
   Tag: v2.0.0
   Title: Nobara GRUB Tuner v2.0.0 - GTK4/Adwaita Edition
   Description: 
   
   ✨ Initial Release
   
   Features:
   - Modern GTK4/Adwaita interface
   - 3-layer security validation
   - Multi-distribution support
   - Persistent logging system
   - Configuration versioning
   - 30+ unit tests
   - Responsive UI with threading


5️⃣  DESPUÉS DE HACER PUSH

   Comparte el repositorio:
   - https://github.com/Jojonxtanx/Tunning-Nobara-Grub
   
   Anúncialo en:
   - Discusiones de Nobara
   - Reddit r/NobaraLinux
   - Foros de Linux

═══════════════════════════════════════════════════════════════════════════════

📊 ESTADO ACTUAL:

EOF

cd "$(dirname "$0")"

echo "📁 Archivos listos para push:"
git ls-files | wc -l
echo "   archivos"

echo ""
echo "📝 Último commit:"
git log -1 --pretty=format:"%h - %s - %an"

echo ""
echo ""
echo "🚀 Para hacer push AHORA, ejecuta:"
echo ""
echo "   cd '$(pwd)'"
echo "   git push -u origin main"
echo ""

EOF
