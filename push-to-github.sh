#!/bin/bash
# Script para subir el proyecto a GitHub
# Ejecutar desde: bash push-to-github.sh

echo "🚀 Configurando repositorio para GitHub..."

# Cambiar a rama main
git branch -M main

# Agregar remote (si no existe)
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/Jojonxtanx/Tunning-Nobara-Grub.git

echo "✅ Remote configurado: $(git remote get-url origin)"

# Mostrar status
echo ""
echo "📊 Estado del repositorio:"
git log --oneline | head -3

echo ""
echo "🔗 Para hacer push a GitHub, ejecuta:"
echo "   git push -u origin main"
echo ""
echo "⚠️  Necesitarás autenticarte con GitHub (Personal Access Token o SSH)."
echo "   Si no tienes acceso configurado, Git te pedirá credenciales."
