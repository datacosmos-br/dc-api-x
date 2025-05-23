# GitHub Configuration

Este diretório contém arquivos de configuração para recursos do GitHub usados neste repositório.

## Estrutura

- **CODEOWNERS**: Define regras de propriedade para o conteúdo do repositório
- **PULL_REQUEST_TEMPLATE.md**: Template usado ao criar novos pull requests
- **dependabot.yml**: Configuração para atualizações automatizadas de dependências via Dependabot
- **labeler.yml**: Configuração para rotulação automática de PRs com base em caminhos de arquivos

### Diretórios

- **ISSUE_TEMPLATE/**: Templates usados ao criar novas issues
  - `bug_report.md`: Template para reportar bugs
  - `feature_request.md`: Template para solicitar novos recursos
- **workflows/**: Definições de workflows do GitHub Actions
  - `python-workflow.yml`: Pipeline principal de CI/CD para linting, testes e verificação de dependências
  - `security-scans.yml`: Ferramentas abrangentes de verificação de segurança (CodeQL, Bandit, OSV, Pyre)
  - `stale.yml`: Gerencia automaticamente issues e pull requests obsoletos
  - `greetings.yml`: Dá boas-vindas a novos colaboradores
  - `label.yml`: Aplica rótulos aos PRs com base nos caminhos dos arquivos modificados
  - `summary.yml`: Cria resumos gerados por IA para novas issues
  - `release.yml`: Automatiza o processo de release quando uma tag de versão é enviada
  - `docs.yml`: Constrói e implanta documentação no GitHub Pages

## Workflows

### CI/CD Python (`python-workflow.yml`)

Executa em push para main, PRs para main e execuções agendadas semanalmente:

1. **Lint**: Verifica o estilo do código com ruff, black e verificação de tipo com mypy
2. **Test**: Executa pytest com relatórios de cobertura em várias versões do Python
3. **Security**: Verifica vulnerabilidades de segurança no código com bandit
4. **Dependency Review**: Revisa dependências em PRs para vulnerabilidades

### Verificações de Segurança (`security-scans.yml`)

Executa em push para main, PRs para main e semanalmente:

1. **CodeQL**: Análise estática avançada para vulnerabilidades de segurança
2. **Bandit**: Linter de segurança específico para Python
3. **OSV Scanner**: Verifica dependências no banco de dados de vulnerabilidades
4. **Pyre**: Verificador de tipo estático para Python

### Gerenciamento de Issues Obsoletas (`stale.yml`)

Executa diariamente para marcar e fechar issues e PRs obsoletos:

- Issues/PRs inativos por 30 dias são marcados como obsoletos
- Se não houver atividade após serem marcados como obsoletos por 14 dias, são fechados
- Rótulos importantes isentam issues/PRs de serem marcados como obsoletos

### Primeira Interação (`greetings.yml`)

Responde automaticamente aos colaboradores de primeira viagem quando eles:

- Abrem sua primeira issue
- Enviam seu primeiro pull request

### Rotulador Automático (`label.yml`)

Rotula PRs com base nos arquivos alterados, usando regras de `labeler.yml`.

### Resumo de Issues (`summary.yml`)

Usa IA para gerar um resumo conciso de novas issues e publica como um comentário.

### Automação de Release (`release.yml`)

Acionado quando uma tag de versão (v*.*.*) é enviada:

1. **Build**: Constrói artefatos do pacote Python
2. **Publish**: 
   - Cria um GitHub Release com assets
   - Publica no PyPI (versões estáveis) ou TestPyPI (pré-lançamentos)
   - Cria uma GitHub Discussion anunciando o release

### Documentação (`docs.yml`)

Constrói e implanta documentação:

1. **Build**: Constrói documentação MkDocs em alterações nos arquivos de documentação
2. **Deploy**: Implanta no GitHub Pages
3. **Gatilho Manual**: Pode ser acionado manualmente via workflow_dispatch 
