#!/bin/bash

# Este arquivo define as variáveis de ambiente para o seu aplicativo Evolution API.
# É crucial que este arquivo NÃO seja incluído em repositórios públicos
# se contiver chaves ou senhas sensíveis.

# Variáveis de autenticação
export AUTHENTICATION_ENABLED="true"
# Para gerar uma AUTHENTICATION_API_KEY segura:
# 1. Acesse o site: https://strpwdgen.pages.dev/
# 2. Desative a caixa "Include Special Symbols" (para evitar caracteres que possam causar problemas em alguns ambientes).
# 3. Aumente o "Length" para 32 (para garantir uma chave longa e robusta).
# 4. Clique em "Regenerate" para gerar uma nova chave.
# 5. Clique em "Copy to clipboard" para copiar a chave gerada.
# 6. Cole a chave copiada abaixo, substituindo "sua_chave_secreta_aqui".
export AUTHENTICATION_API_KEY="sua_chave_secreta_aqui" # MUDE ESTA CHAVE!
export CONFIG_SESSION_PHONE_VERSION="2.3000.1020885143" #versao do whatsapp , vai no web configuraçoes > ajuda > versao

# Configurações do Redis (garanta que o serviço 'redis' esteja disponível)
export CACHE_REDIS_ENABLED="true"
export CACHE_REDIS_URI="redis://redis:6379" # Já é referenciado pelo serviço 'redis' no docker-compose
export CACHE_REDIS_HOST="redis"
export CACHE_REDIS_PORT="6379"
export CACHE_REDIS_URL="redis://redis:6379/0"
export CACHE_REDIS_PREFIX_KEY="evolution"
export CACHE_REDIS_TTL="604800"
export CACHE_REDIS_SAVE_INSTANCES="true"
export CACHE_DRIVER="redis"

# Configurações do Banco de Dados (garanta que o serviço 'postgres' esteja disponível)
export DATABASE_ENABLED="true"
export DATABASE_PROVIDER="postgresql"
export DATABASE_SAVE_DATA_INSTANCE="true"
# Formato: postgresql://<user>:<password>@<host>:<port>/<database>
export DATABASE_CONNECTION_URI="postgresql://default:default@postgres:5432/evolutionapi" # MUDE ISSO!

# Configurações de Log
export LOG_LEVEL="ERROR,WARN,DEBUG,INFO,LOG,VERBOSE,DARK,WEBHOOKS,WEBSOCKET,REDIS,BAILEYS"
export LOG_COLOR="true"
export LOG_BAILEYS="trace"
# SERVER_URL (DEVICE_DOMAIN_NAME) é injetado pelo Umbrel OS, não precisa ser exportado aqui
export TZ="America/Sao_Paulo" # Fuso horário, ajuste se necessário
