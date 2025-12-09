from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import random

app = Flask(__name__)
CORS(app)

# 1. Modeli Yükle
try:
    model = joblib.load("price_model.pkl")
    print("✅ Model Yüklendi")
except:
    model = None

# 2. Veri Setini Yükle (Öneriler için veriyi bilmemiz lazım)
try:
    df_products = pd.read_csv("tum_urunler_v3.csv") # veya cleaned_data.csv
    # Fiyat temizliği (Garanti olsun)
    df_products['Fiyat'] = pd.to_numeric(df_products['Fiyat'].astype(str).str.replace(".","").str.replace(",","."), errors='coerce')
    print(f"✅ Ürün Verisi Yüklendi: {len(df_products)} satır")
except:
    print("⚠️ Ürün verisi bulunamadı, öneri sistemi çalışmayacak.")
    df_products = pd.DataFrame()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        fiyat = float(data.get('Fiyat', 0))
        marka = data.get('Marka', '')
        kategori = data.get('Kategori', '')
        
        # 1. Fiyat Tahmini
        if model: tahmin = model.predict([[fiyat]])[0] # Basit örnek
        else: tahmin = fiyat * 0.95
        
        # Durum Belirleme
        durum = "Normal"
        if tahmin < fiyat * 0.90: durum = "Pahalı 🔴"
        elif tahmin > fiyat * 1.05: durum = "Ucuz 🟢"

        # 2. ALTERNATİF ÖNERİLER (Sizin İstediğiniz Özellik)
        oneriler = []
        if not df_products.empty and durum.startswith("Pahalı"):
            # Aynı Kategori, Aynı Marka ama Daha Ucuz olanları bul
            alternatifler = df_products[
                (df_products['Kategori'] == kategori) & 
                (df_products['Marka'] == marka) & 
                (df_products['Fiyat'] < fiyat)
            ].sort_values(by='Fiyat').head(3) # En ucuz 3 tanesini al
            
            for _, row in alternatifler.iterrows():
                oneriler.append({
                    "ad": row['Model'],
                    "fiyat": row['Fiyat'],
                    "link": row['Link'],
                    "resim": row.get('Resim', 'https://via.placeholder.com/150')
                })

        return jsonify({
            "tahmin": int(tahmin),
            "durum": durum,
            "oneriler": oneriler # Listeyi web sitesine gönderiyoruz
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 AI + Öneri Servisi Başladı: http://localhost:5000")
    app.run(port=5000)