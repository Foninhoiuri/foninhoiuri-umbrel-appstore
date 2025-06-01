# Guia de Auto-Hospedagem do Supabase

## Introdução

Este guia oferece instruções para configurar e instalar uma instância do Supabase auto-hospedada no Umbrel.

## Configuração Inicial Após a Instalação

Após instalar o Supabase pela loja de aplicativos do Umbrel, você precisa configurar as informações de host do servidor:

1. Abra o aplicativo "Arquivos" no painel do Umbrel.
2. Navegue até `apps` → `supabase`.
3. Localize e baixe o arquivo `exports.sh` para o seu computador.
4. Abra o arquivo em um editor de texto e atualize a seguinte linha com o endereço IP do seu Umbrel:

```bash
# Substitua pelo IP ou nome de host do seu Umbrel
export UMBREL_HOST="172.17.0.3" # o seu pode ser diferente
```

5. Salve o arquivo e faça o upload de volta para o mesmo local.
6. Reinicie o aplicativo Supabase pelo painel do Umbrel.