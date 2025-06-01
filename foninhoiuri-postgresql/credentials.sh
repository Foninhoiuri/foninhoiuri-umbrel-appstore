# Este arquivo define as variáveis de ambiente sensíveis para o seu aplicativo.
# É uma boa prática não commitar este arquivo em repositórios públicos.


# usado no DATABASE_CONNECTION_URI do Evolution API entre outros
export POSTGRES_USER="seu_usuario_seguro" # Altere para um usuário forte
export POSTGRES_PASSWORD="sua_senha_muito_segura" # Altere para uma senha forte
export POSTGRES_DB="seu_banco_de_dados" # Altere para o nome do seu banco de dados


export TZ="America/Sao_Paulo" # Fuso horário, ajuste se necessário

echo "Variáveis de ambiente carregadas!"
