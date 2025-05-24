# Estrutura de Testes do dc-api-x

Este diretório contém testes automatizados para o projeto dc-api-x. A estrutura foi organizada para facilitar a manutenção, execução e compreensão dos diferentes tipos de testes.

## Organização

Os testes estão organizados nas seguintes categorias:

- **Unit (`/unit`)**: Testes unitários que validam componentes individuais isoladamente
- **Functional (`/functional`)**: Testes funcionais que validam o comportamento da API como um todo
- **Integration (`/integration`)**: Testes de integração com sistemas externos
- **Performance (`/performance`)**: Testes de desempenho e benchmarks
- **Security (`/security`)**: Testes de segurança e vulnerabilidades

## Execução

Para executar os testes, utilize o comando pytest com os modificadores apropriados:

```bash
# Executar todos os testes
python -m pytest

# Executar testes unitários
python -m pytest tests/unit

# Executar testes funcionais
python -m pytest tests/functional

# Executar testes de integração
python -m pytest tests/integration

# Executar testes de performance
python -m pytest tests/performance

# Executar testes de segurança
python -m pytest tests/security

# Executar testes com Logfire habilitado
python -m pytest --logfire
```

## Marcadores (Markers)

Os testes utilizam marcadores para categorização:

- `@pytest.mark.unit`: Testes unitários
- `@pytest.mark.functional`: Testes funcionais
- `@pytest.mark.integration`: Testes de integração
- `@pytest.mark.performance`: Testes de performance
- `@pytest.mark.security`: Testes de segurança
- `@pytest.mark.slow`: Testes lentos que podem ser ignorados em CI
- `@pytest.mark.plugins`: Testes relacionados ao sistema de plugins
- `@pytest.mark.logfire`: Testes que utilizam ou dependem de Logfire

Exemplo de execução utilizando marcadores:

```bash
# Executar testes marcados como 'unit'
python -m pytest -m unit

# Ignorar testes lentos
python -m pytest -m "not slow"

# Executar testes que usam Logfire
python -m pytest -m logfire
```

## Fixtures

As fixtures estão definidas no arquivo `conftest.py` e estão organizadas nas seguintes categorias:

- **Auxiliares**: Fixtures utilitárias básicas
- **Logging**: Fixtures relacionadas a captura e configuração de logs
- **HTTP/API**: Fixtures para testes de API e HTTP
- **Autenticação**: Fixtures para autenticação
- **Banco de Dados**: Fixtures para testes com banco de dados
- **Modelos**: Fixtures para testes com modelos de dados
- **Arquivos**: Fixtures para manipulação de arquivos de teste

## Configuração do Ambiente

A configuração do ambiente de testes é feita automaticamente pelo `conftest.py`, que configura as variáveis de ambiente necessárias e prepara o ambiente para os testes.

## Geração de Relatórios

Os relatórios de testes são gerados nos seguintes formatos:

- **HTML**: Relatório detalhado em HTML (`reports/pytest/report.html`)
- **XML**: Relatório XML para integração com CI (`junit/test-results.xml`)
- **Cobertura**: Relatório de cobertura de código (`reports/coverage/`)

## Logging Estruturado com Logfire

Para testes que utilizam logging estruturado com Logfire, foi implementado um padrão de uso que funciona mesmo quando a biblioteca Logfire não está disponível. Consulte o documento [README-LOGFIRE-TESTING.md](./README-LOGFIRE-TESTING.md) para detalhes sobre:

- Como importar e utilizar as funções de logging nos testes
- O decorador `@requires_logfire` para testes que dependem de Logfire
- A fixture `logfire_testing` para captura e verificação de logs
- Padrões para testar redação de dados sensíveis
- Boas práticas para testes com logging estruturado

### Exemplo básico de uso:

```python
from tests import info, requires_logfire

@requires_logfire
def test_example(logfire_testing):
    """Test that logs structured data."""
    info("Test message", value=42)

    # Use helper method to find logs
    log = logfire_testing.find_log(message="Test message")

    # Use attribute access for cleaner assertions
    assert log is not None
    assert log.value == 42
```

### Recursos avançados:

- `LogEntry` - Wrapper para entradas de log que permite acesso por atributos
- `find_logs()` - Método para encontrar logs por critérios
- `find_log()` - Método para encontrar o primeiro log que atenda aos critérios
- `test_context()` - Helper para adicionar contexto de teste aos logs
- `requires_logfire(strict=False)` - Opção para executar testes mesmo sem Logfire

### Contexto automático:

A fixture `logfire_testing` adiciona automaticamente metadados úteis a todos os logs:

```python
# Este contexto é adicionado automaticamente a todos os logs
with test_context(
    test_name="nome_do_teste",
    test_module="nome_do_módulo",
    test_class="nome_da_classe",
    test_file="arquivo_de_teste.py"
):
    # Seus logs aqui terão o contexto acima
    info("Log de teste")
```
