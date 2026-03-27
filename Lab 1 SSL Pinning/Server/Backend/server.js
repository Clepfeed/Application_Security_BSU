const express = require('express');
const https = require('https');
const fs = require('fs');
const path = require('path');
const tls = require('tls');

const app = express();
const PORT = 4433;

const validKeyName = "server";
const invalidKeyName = "invalid";

app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));


const dataDir = path.join(__dirname, 'Data');
if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir);
    console.log("Data created");
}

const certsDir = path.join(__dirname, 'certificate');

// tls создаёт контексты безопасности. Создаём правильный и неправильный 
const validContext = tls.createSecureContext({
    key: fs.readFileSync(path.join(certsDir, `${validKeyName}.key`)),
    cert: fs.readFileSync(path.join(certsDir, `${validKeyName}.crt`))
});

const invalidContext = tls.createSecureContext({
    key: fs.readFileSync(path.join(certsDir, `${invalidKeyName}.key`)),
    cert: fs.readFileSync(path.join(certsDir, `${invalidKeyName}.crt`))
});

// Загрузка данных с формы
app.post('/api/match', (req, res) => {
    const { date, team, players } = req.body;
    
    if (!date || !team) {
        return res.status(400).json({ error: 'Fill in the required fields' });
    }

    const fileName = `${date}_${team}.json`;
    const filePath = path.join(dataDir, fileName);

    fs.writeFile(filePath, JSON.stringify(req.body, null, 2), (err) => {
        if (err) {
            console.error('file save error', err);
            return res.status(500).json({ error: 'server error on save file' });
        }
        console.log(`[DATA] data saved ${fileName}`);
        res.json({ message: 'Data saved' });
    });
});

// Получение данных матча клиентом
app.get('/api/match', (req, res) => {
    const { date, team } = req.query; // Ожидаем параметры в URL: ?date=...&team=...
    
    if (!date || !team) {
        return res.status(400).json({ error: 'Specify  date и team in request' });
    }

    const fileName = `${date}_${team}.json`;
    const filePath = path.join(dataDir, fileName);

    if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: 'Roster not found' });
    }

    res.sendFile(filePath);
});

// Смена сертификата
app.post('/api/dev/switch-cert', (req, res) => {
    const { useValidCert } = req.body;

    if (useValidCert) {
        httpsServer.setSecureContext(validContext);
        console.log('[SSL] Valid certificate');
    } else {
        httpsServer.setSecureContext(invalidContext);
        console.log('[SSL] INvalid certificate');
    }
    
    res.json({ success: true, message: 'TLS Updated' });
});

// Настройки при запуске
const httpsOptions = {
    key: fs.readFileSync(path.join(certsDir, `${validKeyName}.key`)),
    cert: fs.readFileSync(path.join(certsDir, `${validKeyName}.crt`))
};

const httpsServer = https.createServer(httpsOptions, app);

httpsServer.listen(PORT, () => {
    console.log(`Сервер запущен на https://localhost:${PORT}`);
});