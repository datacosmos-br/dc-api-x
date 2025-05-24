# Guia de Uso do MonkeyType no DC-API-X

Este guia explica como utilizar o MonkeyType para coletar tipos em tempo de execução durante os testes e aplicá-los ao código-fonte do DC-API-X, melhorando as anotações de tipo para mypy e pydantic.

## O que é o MonkeyType?

MonkeyType é uma ferramenta que coleta tipos em tempo de execução durante a execução dos testes e gera anotações de tipo baseadas nessas informações. Isto permite:

1. Descobrir tipos em código existente não tipado
2. Gerar tipos de campo para modelos Pydantic com base no uso real
3. Melhorar a cobertura do mypy com esforço mínimo
4. Encontrar inconsistências de tipo no código

## Pré-requisitos

O MonkeyType já está configurado como dependência de desenvolvimento do projeto:

```bash
# Para garantir que o MonkeyType está instalado
poetry install --with dev
```

## Workflow Básico

O fluxo de trabalho para adicionar tipos com o MonkeyType é:

1. Execute os testes com o MonkeyType para coletar tipos
2. Liste os módulos que possuem informações de tipo coletadas
3. Aplique os tipos a um módulo específico
4. Verifique e refine os tipos manualmente, se necessário
5. Execute o mypy para verificar a consistência de tipos

## Comandos Disponíveis

O projeto inclui comandos no Makefile para facilitar o uso do MonkeyType:

```bash
# Executar todos os testes com MonkeyType para coletar tipos
make monkeytype-run

# Executar um teste específico com MonkeyType
make monkeytype-run TEST_PATH=tests/test_config.py

# Listar módulos com informações de tipo coletadas
make monkeytype-list

# Aplicar tipos coletados a um módulo específico
make monkeytype-apply MODULE=dc_api_x.config

# Gerar stub com tipos coletados para um módulo
make monkeytype-stub MODULE=dc_api_x.models
```

## Uso Avançado com o Script Standalone

Você também pode usar o script `scripts/monkeytype_runner.py` diretamente para casos mais específicos:

```bash
# Executar todos os testes com MonkeyType
python scripts/monkeytype_runner.py run

# Executar um teste específico
python scripts/monkeytype_runner.py run --test-path tests/test_config.py

# Listar módulos com informações de tipo
python scripts/monkeytype_runner.py list

# Aplicar tipos a um módulo
python scripts/monkeytype_runner.py apply --module dc_api_x.config

# Gerar stub para um módulo
python scripts/monkeytype_runner.py stub --module dc_api_x.models
```

## Integração com Pydantic

Para classes Pydantic, o MonkeyType gera anotações de tipo padrão Python. Você precisará convertê-las para a sintaxe de campos do Pydantic:

**Antes de aplicar os tipos:**
```python
class Config:
    def __init__(self, api_url, timeout=None):
        self.api_url = api_url
        self.timeout = timeout or 30
```

**Depois de aplicar os tipos com MonkeyType:**
```python
class Config:
    def __init__(self, api_url: str, timeout: Optional[int] = None) -> None:
        self.api_url = api_url
        self.timeout = timeout or 30
```

**Convertido para Pydantic:**
```python
class Config(BaseModel):
    api_url: str
    timeout: Optional[int] = 30
```

## Melhores Práticas

1. **Testes Abrangentes**: Certifique-se de que seus testes exercitem a maior parte possível das funcionalidades para coletar tipos precisos.

2. **Revisar os Tipos Aplicados**: Sempre revise os tipos aplicados pelo MonkeyType e refine-os quando necessário. O MonkeyType só pode inferir os tipos que vê durante a execução.

3. **Tipos Opcionais**: O MonkeyType detecta quando valores podem ser `None`, mas pode ser necessário refinar tipos opcionais complexos.

4. **Verificar com mypy**: Depois de aplicar tipos, execute o mypy para verificar se as anotações estão corretas e consistentes.

5. **Processo Iterativo**: A coleta e aplicação de tipos é um processo iterativo. Você pode precisar executar o MonkeyType várias vezes com diferentes testes para obter uma cobertura abrangente.

## Fluxo de Trabalho Recomendado para Adicionar Tipos ao DC-API-X

1. Identifique um módulo que precisa de anotações de tipo
2. Execute testes abrangentes com MonkeyType que exercitem esse módulo
   ```bash
   make monkeytype-run TEST_PATH=tests/test_module_related.py
   ```
3. Verifique se os tipos foram coletados
   ```bash
   make monkeytype-list
   ```
4. Aplique os tipos ao módulo
   ```bash
   make monkeytype-apply MODULE=dc_api_x.module_name
   ```
5. Revise e refine os tipos manualmente, especialmente para:
   - Modelos Pydantic
   - Tipos genéricos complexos
   - Tipos de retorno em métodos abstratos
   - Parâmetros com valores padrão
6. Verifique a conformidade dos tipos com mypy
   ```bash
   python -m mypy src/dc_api_x/module_name.py
   ```
7. Repita com outros módulos conforme necessário

## Limitações

- O MonkeyType só pode detectar tipos que são realmente usados durante a execução dos testes
- Alguns tipos complexos (genéricos, unions) podem precisar de refinamento manual
- Recursos específicos do Pydantic (Field, validator, etc.) precisam ser adicionados manualmente
- Tipos para funções ou métodos nunca chamados nos testes não serão coletados
- Os testes devem exercitar caminhos de código com diferentes tipos para detectar unions corretamente

## Exemplos

### Exemplo 1: Aplicar tipos ao módulo de configuração

```bash
# Executar os testes de configuração com MonkeyType
make monkeytype-run TEST_PATH=tests/test_config.py

# Verificar módulos com tipos coletados
make monkeytype-list

# Aplicar tipos ao módulo de configuração
make monkeytype-apply MODULE=dc_api_x.config
```

### Exemplo 2: Converter tipos para modelos Pydantic

Depois de aplicar os tipos com MonkeyType, você precisará adaptar para o estilo Pydantic:

```python
# Original sem tipos
class User:
    def __init__(self, name, email, age=None, is_active=True):
        self.name = name
        self.email = email
        self.age = age
        self.is_active = is_active

# Após MonkeyType
class User:
    def __init__(self, name: str, email: str, age: Optional[int] = None, is_active: bool = True) -> None:
        self.name = name
        self.email = email
        self.age = age
        self.is_active = is_active
        
# Convertido para Pydantic
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class User(BaseModel):
    name: str
    email: EmailStr  # Refinado manualmente para EmailStr
    age: Optional[int] = None
    is_active: bool = True 
