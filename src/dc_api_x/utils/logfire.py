"""
Logfire API Module.

This module provides direct access to the Logfire package for structured logging.
"""

import os

import logfire

# Configuração inicial do Logfire
service_name = os.environ.get("LOGFIRE_SERVICE_NAME", "dc-api-x")
environment = os.environ.get("LOGFIRE_ENVIRONMENT", "dev")

# Configurar logfire com as configurações do ambiente
logfire.configure(
    service_name=service_name,
    environment=environment,
)

# Exportar funções do pacote logfire para uso direto
debug = logfire.debug
info = logfire.info
warning = logfire.warning
error = logfire.error
critical = logfire.critical
exception = logfire.exception
context = logfire.context
span = logfire.span
bind = logfire.bind
capture = logfire.testing.capture
