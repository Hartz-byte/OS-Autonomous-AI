const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: './session'
    }),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ]
    }
});

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

client.on('message', async msg => {
    console.log("Incoming message:", msg.body);
    console.log("From:", msg.from);
    console.log("Type:", msg.type);
    console.log("FromMe:", msg.fromMe);

    if (msg.fromMe) return;
    if (msg.type !== 'chat') return;

    try {
        const response = await axios.post(
            "http://openclaw:8000/message",
            { message: msg.body }
        );

        console.log("Agent reply:", response.data.reply);

        await msg.reply(response.data.reply);

    } catch (err) {
        console.error("Axios error:", err.message);
        await msg.reply("Agent error.");
    }
});

client.initialize();
