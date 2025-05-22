#!/bin/bash
#==============================================================================
# AUTO LINT FIX - CICLO AUTOMÁTICO
#==============================================================================
# DESCRIÇÃO:
#   Script para execução automatizada de verificações de lint e correções
#   no projeto dc-api-x. O script continua executando ciclos de lint e 
#   correção até que todos os problemas sejam resolvidos ou até atingir
#   o número máximo de tentativas.
#
# USO:
#   cd dc-api-x
#   ./scripts/auto_lint_fix.sh
#
# OPÇÕES:
#   DEBUG=1     # Define nível de log detalhado
#   MAX_CYCLES=n # Define o número máximo de ciclos (padrão: 10)
#
# EXEMPLOS:
#   ./scripts/auto_lint_fix.sh                 # Executa o ciclo completo
#   DEBUG=1 ./scripts/auto_lint_fix.sh         # Executa com logs detalhados
#   MAX_CYCLES=5 ./scripts/auto_lint_fix.sh    # Define máximo de 5 ciclos
#
# NOTAS:
#   - Este script deve ser executado a partir da raiz do projeto
#   - Requer que 'make lint', 'make lint-fix' e 'make format' estejam configurados
#   - Os arquivos são modificados automaticamente durante o processo
#==============================================================================

set -e

# Configurações
MAX_CYCLES=${MAX_CYCLES:-10}
CYCLES=0
DEBUG=${DEBUG:-0}

# Cores para saída
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Banner inicial
echo -e "${BLUE}${BOLD}================================================================${NC}"
echo -e "${BLUE}${BOLD}                AUTO LINT FIX - CICLO AUTOMÁTICO                ${NC}"
echo -e "${BLUE}${BOLD}================================================================${NC}"
echo -e "${BOLD}Este script executa automaticamente ciclos de:${NC}"
echo -e " 1. ${YELLOW}Verificação de lint${NC} (make lint)"
echo -e " 2. ${YELLOW}Correção automática${NC} (make lint-fix)"
echo -e " 3. ${YELLOW}Formatação de código${NC} (make format)"
echo -e 
echo -e "${BOLD}O ciclo continua até que:${NC}"
echo -e " - Não sejam encontrados problemas de lint, OU"
echo -e " - O número máximo de $MAX_CYCLES ciclos seja atingido"
echo -e 
echo -e "${BOLD}Os arquivos serão modificados automaticamente!${NC}"
echo

# Verifica se estamos na raiz do projeto
if [ ! -f "Makefile" ]; then
    echo -e "${RED}ERRO: Este script deve ser executado da raiz do projeto.${NC}"
    echo -e "${YELLOW}Use: cd \$(git rev-parse --show-toplevel) && ./scripts/auto_lint_fix.sh${NC}"
    exit 1
fi

PROJECT_ROOT=$(pwd)
echo -e "${BOLD}Diretório do projeto:${NC} $PROJECT_ROOT"
echo

# Função de debug
debug() {
    if [ "$DEBUG" = "1" ]; then
        echo -e "${YELLOW}[DEBUG] $1${NC}"
    fi
}

# Função para executar verificação de lint
function run_lint() {
    echo -e "${YELLOW}[Ciclo $CYCLES] Executando verificação de lint...${NC}"
    # Salva a saída do comando para análise
    if make lint 2>&1 | tee /tmp/lint_output.log; then
        debug "Comando 'make lint' executado com sucesso"
        return 0
    else
        debug "Comando 'make lint' encontrou problemas"
        return 1
    fi
}

# Função para aplicar correções automáticas
function run_fix() {
    echo -e "${YELLOW}[Ciclo $CYCLES] Aplicando correções automáticas...${NC}"
    debug "Executando 'make lint-fix'"
    make lint-fix
    
    echo -e "${YELLOW}[Ciclo $CYCLES] Formatando código...${NC}"
    debug "Executando 'make format'"
    make format
}

# Ciclo principal
while [ $CYCLES -lt $MAX_CYCLES ]; do
    CYCLES=$((CYCLES + 1))
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}${BOLD}                     CICLO $CYCLES DE $MAX_CYCLES${NC}"
    echo -e "${BLUE}================================================================${NC}"
    
    if run_lint; then
        echo -e "${GREEN}${BOLD}✓ Nenhum problema de lint encontrado!${NC}"
        echo -e "${GREEN}${BOLD}✓ Ciclo completo em $CYCLES tentativas.${NC}"
        exit 0
    else
        ERRORS=$(grep -ci "error\|warning\|issue" /tmp/lint_output.log || echo "0")
        echo -e "${RED}✗ Encontrados problemas de lint. Tentando correção automática...${NC}"
        echo -e "${RED}  Aproximadamente $ERRORS problemas encontrados.${NC}"
        
        # Lista os tipos de problemas mais comuns (só no modo debug)
        if [ "$DEBUG" = "1" ]; then
            echo -e "${YELLOW}[DEBUG] Tipos de problemas mais comuns:${NC}"
            grep -o "E[0-9]\+\|F[0-9]\+\|W[0-9]\+" /tmp/lint_output.log | sort | uniq -c | sort -nr | head -5
        fi
        
        run_fix
        
        echo -e "${YELLOW}Verificando resultados após correção automática...${NC}"
    fi
    
    # Pequena pausa para dar tempo aos processos de concluírem
    sleep 1
done

# Ciclo máximo atingido sem resolução completa
echo -e "${RED}================================================================${NC}"
echo -e "${RED}${BOLD}X Não foi possível corrigir todos os problemas após $MAX_CYCLES ciclos.${NC}"
echo -e "${RED}${BOLD}X Alguns problemas podem precisar de correção manual.${NC}"
echo -e "${RED}================================================================${NC}"
echo -e "${YELLOW}Executando uma última verificação para mostrar os problemas restantes:${NC}"
make lint

echo
echo -e "${BOLD}Próximos passos recomendados:${NC}"
echo -e " 1. Corrija manualmente os problemas restantes"
echo -e " 2. Execute 'make lint' para verificar novamente"
echo -e " 3. Execute 'make fix' para aplicar todas as correções possíveis"
echo -e " 4. Execute este script novamente se necessário"

exit 1 
