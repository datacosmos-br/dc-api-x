# Instruções para Adicionar Workflows do GitHub

Os arquivos de workflow do GitHub foram configurados, mas não puderam ser enviados diretamente devido a restrições de permissão do OAuth. Siga estas instruções para adicioná-los:

## Arquivos e Localizações

Os arquivos de workflow estão localizados em:
- `/home/marlonsc/pyauto/temp_workflows/`

## Opções para Adicionar Workflows

### Opção 1: Interface Web do GitHub

1. Navegue até [o repositório no GitHub](https://github.com/datacosmos-br/dc-api-x)
2. Vá para a guia "Actions"
3. Você pode selecionar um workflow sugerido ou criar um novo:
   - Clique em "New workflow" ou "Set up a workflow yourself"
   - Para cada arquivo, nomeie-o adequadamente (ex: `python-workflow.yml`)
   - Copie e cole o conteúdo do arquivo correspondente de `/home/marlonsc/pyauto/temp_workflows/`
   - Clique em "Start commit" e depois "Commit new file"

### Opção 2: Criar um Token com Escopo de Workflow

1. Acesse [Configurações de Tokens](https://github.com/settings/tokens)
2. Crie um novo token com escopo `workflow`
3. Use este token para autenticação Git:

```bash
git config --local credential.helper store
echo "https://SEU_USUARIO:SEU_TOKEN@github.com" > ~/.git-credentials
git checkout main
git pull
mkdir -p .github/workflows
cp /home/marlonsc/pyauto/temp_workflows/* .github/workflows/
git add .github/workflows
git commit -m "Adicionar arquivos de workflow do GitHub"
git push origin main
```

## Lista de Workflows

Os seguintes workflows devem ser adicionados:

1. `python-workflow.yml` - Pipeline principal de CI/CD
2. `security-scans.yml` - Verificações de segurança
3. `release.yml` - Automação de release
4. `docs.yml` - Criação e publicação de documentação
5. `stale.yml` - Gerenciamento de issues inativas
6. `greetings.yml` - Mensagens de boas-vindas
7. `label.yml` - Rotulação automática
8. `summary.yml` - Resumo de issues 
