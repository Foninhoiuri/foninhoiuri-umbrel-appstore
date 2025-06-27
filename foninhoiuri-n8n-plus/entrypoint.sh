#!/bin/bash

# Detecta o hostname de acesso (ex: se definido em /etc/hosts ou via domínio)
if [[ "$HOSTNAME" == *"umbrel"* ]]; then
  export N8N_HOST=umbrel.local
  export N8N_PROTOCOL=http
  export N8N_PORT=5678
else
  export N8N_HOST=n8n.igoriurialves.com.br
  export N8N_PROTOCOL=https
  export N8N_PORT=443
fi

exec tini -- /docker-entrypoint.sh "$@"
