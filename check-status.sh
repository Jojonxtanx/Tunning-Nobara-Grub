#!/bin/bash

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Verificando estado del repositorio Git${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

cd "$(dirname "$0")" || exit 1

# Verificar configuración
echo -e "${GREEN}✓ Configuración del repositorio:${NC}"
git remote -v
echo ""

# Verificar rama actual
echo -e "${GREEN}✓ Rama actual:${NC}"
git branch
echo ""

# Últimos commits
echo -e "${GREEN}✓ Últimos commits:${NC}"
git log --oneline -3
echo ""

# Estado de la rama
echo -e "${GREEN}✓ Estado actual:${NC}"
git status
echo ""

# Contar archivos
echo -e "${GREEN}✓ Archivos en el repositorio:${NC}"
FILE_COUNT=$(git ls-files | wc -l)
echo "   Total: $FILE_COUNT archivos"
echo ""

# Verificar sí está todo sincronizado
echo -e "${GREEN}✓ Verificando sincronización:${NC}"
git fetch origin 2>/dev/null
STATUS=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main 2>/dev/null)

if [ "$STATUS" = "$REMOTE" ]; then
    echo -e "   ${GREEN}✅ Repositorio sincronizado con GitHub${NC}"
else
    echo -e "   ${RED}⚠️  Falta hacer push al repositorio${NC}"
    echo ""
    echo -e "${BLUE}Ejecuta:${NC}"
    echo "   git push -u origin main"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Para visitar el repositorio:${NC}"
echo "   https://github.com/Jojonxtanx/Tunning-Nobara-Grub"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
