from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import random

app = Flask(__name__)
CORS(app) # Web sitesinin (localhost:5133) erişebilmesi için gerekli!

# Modeli Yükle
try:
    model = joblib.load("price_model.pkl")
    print("✅ Gerçek Model Yüklendi")
except:
    print("⚠️ Model bulunamadı. Test (Mock) Modu Aktif.")
    model = None

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    print(f"📩 İstek Geldi: {data}")
    
    # Gelen Fiyatı Kontrol Et (10.725 sorunu burada da olabilir)
    fiyat = data.get('Fiyat', 0)
    
    # Yapay Zeka Tahmini (Simülasyon veya Gerçek)
    if model:
        # Gerçek model entegrasyonu (Sonra yapacağız)
        tahmin = fiyat * 0.95 # Örnek: %5 daha ucuz olmalı
    else:
        # Test Cevabı
        tahmin = fiyat * (random.uniform(0.9, 1.1)) 

    analiz_sonucu = "Normal"
    if tahmin < fiyat: analiz_sonucu = "Pahalı 🔴"
    else: analiz_sonucu = "Ucuz (Fırsat) 🟢"

    return jsonify({
        "tahmin": int(tahmin),
        "durum": analiz_sonucu,
        "mesaj": f"Bu ürünün adil değeri {int(tahmin)} TL olmalıdır."
    })

if __name__ == '__main__':
    print("🚀 AI Servisi Başladı: http://localhost:5000")
    app.run(port=5000)