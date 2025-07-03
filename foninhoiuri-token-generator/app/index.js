const express = require('express');
const { JWT } = require('google-auth-library');
const fs = require('fs');

const app = express();
const PORT = 3000;

let credenciaisRaw = fs.readFileSync('./credenciais.json', 'utf8');
let credenciais = JSON.parse(credenciaisRaw);

// Substitui '\n' literais por quebras de linha reais no private_key
credenciais.private_key = credenciais.private_key.replace(/\\n/g, '\n');

app.get('/google-token', async (req, res) => {
  try {
    const client = new JWT({
      email: credenciais.client_email,
      key: credenciais.private_key,
      scopes: ['https://www.googleapis.com/auth/drive.readonly'],
    });

    const { access_token, expiry_date } = await client.authorize();
    res.json({ access_token, expiry_date });
  } catch (err) {
    console.error('Erro ao gerar token:', err.response?.data || err.message || err);
    res.status(500).json({ error: 'Erro ao gerar token' });
  }
});

app.listen(PORT, () => {
  console.log(`✅ Token Generator rodando em http://localhost:${PORT}`);
});
