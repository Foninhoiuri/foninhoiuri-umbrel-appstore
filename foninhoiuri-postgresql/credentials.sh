# Este arquivo define as variáveis de ambiente sensíveis para o seu aplicativo.
# É uma boa prática não commitar este arquivo em repositórios públicos.


# usado no DATABASE_CONNECTION_URI do Evolution API entre outros
export POSTGRES_USER="default" # Altere para um usuário forte
export POSTGRES_PASSWORD="default" # Altere para uma senha forte
export POSTGRES_DB="default" # Altere para o nome do seu banco de dados


export TZ="America/Sao_Paulo" # Fuso horário, ajuste se necessário

echo "Variáveis de ambiente carregadas!"
