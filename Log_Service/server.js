const express = require('express');
const cors = require('cors');
const fs = require('fs'); // Dosya işlemleri için
const app = express();
const PORT = 4000; // Servis 4000 portunda çalışacak

app.use(cors()); // Herkes erişebilsin
app.use(express.json()); // JSON verilerini anla

// --- LOGLAMA ENDPOINT'İ ---
// Web sitesi buraya "POST" isteği atacak
app.post('/api/log', (req, res) => {
    const { user, action, details } = req.body;
    const timestamp = new Date().toLocaleString('tr-TR');
    
    // Log Formatı: [Tarih] KULLANICI | İŞLEM | DETAY
    const logEntry = `[${timestamp}] KULLANICI: ${user} | İŞLEM: ${action} | DETAY: ${details}\n`;
    
    // 1. Konsola Yaz (Anlık görmek için)
    console.log("📝 YENİ LOG:", logEntry.trim());

    // 2. Dosyaya Kaydet (Kalıcı olması için 'system_logs.txt' dosyasına yazar)
    fs.appendFile('system_logs.txt', logEntry, (err) => {
        if (err) {
            console.error("Dosya hatası:", err);
            return res.status(500).json({ error: "Log dosyaya yazılamadı." });
        }
        res.json({ message: "Log başarıyla kaydedildi." });
    });
});

// Çalışıyor mu testi için Ana Sayfa
app.get('/', (req, res) => {
    res.send("🟢 WiseCart Node.js Log Servisi Aktif!");
});

// Sunucuyu Başlat
app.listen(PORT, () => {
    console.log(`🚀 Node.js Servisi Başladı: http://localhost:${PORT}`);
});