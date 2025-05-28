#!/bin/bash

if [ -z "$AUTHENTICATION_API_KEY" ]; then
  echo "ERRO: A variável AUTHENTICATION_API_KEY não foi fornecida pelo usuário."
  exit 1
fi

echo "Chave de autenticação recebida com sucesso."
