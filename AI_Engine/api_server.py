from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

# 1. Modeli ve Veriyi Yükle
try:
    # Bu model artık bir Pipeline (İçinde TF-IDF + Regressor var)
    model = joblib.load("price_model.pkl")
    print("✅ Şampiyon Model Yüklendi.")
except:
    print("⚠️ Model bulunamadı. İstatistik Modu Aktif.")
    model = None

# Veri setini yükle (Öneriler için)
try:
    df = pd.read_csv("tum_urunler_v3.csv")
    # Fiyatı sayıya çevir
    df['Fiyat'] = df['Fiyat'].astype(str).str.replace("TL","").str.replace(".","").str.replace(",",".")
    df['Fiyat'] = pd.to_numeric(df['Fiyat'], errors='coerce')
    print(f"✅ Veri Seti Hazır: {len(df)} ürün.")
except:
    df = pd.DataFrame()

# Para Formatı
def format_money(value):
    try: return "{:,.0f}".format(value).replace(",", ".")
    except: return str(value)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        # Gelen veriler
        fiyat = float(data.get('Fiyat', 0))
        marka = data.get('Marka', '')
        kategori = data.get('Kategori', '')
        urun_adi = data.get('Model', '') # YENİ: Ürün ismini de alıyoruz

        # --- A. YAPAY ZEKA TAHMİNİ ---
        tahmin = 0
        if model:
            try:
                # Modelin beklediği formatta DataFrame oluştur
                # Sütun isimleri eğitimdekiyle (train_model.py) AYNI olmalı
                input_df = pd.DataFrame([{
                    'Model': urun_adi, 
                    'Marka': marka, 
                    'Kategori': kategori
                }])
                
                # Pipeline her şeyi (Encoding, TF-IDF) kendi halleder
                tahmin = model.predict(input_df)[0]
            except Exception as e:
                print(f"Model Hatası: {e}")
                tahmin = 0 # Model çalışmazsa istatistiğe düş

        # --- B. İSTATİSTİK YEDEĞİ (Model Hata Verirse) ---
        if tahmin == 0:
            if not df.empty:
                benzerler = df[(df['Kategori'] == kategori) & (df['Marka'] == marka)]
                if len(benzerler) > 0: tahmin = benzerler['Fiyat'].mean()
                else: tahmin = fiyat
            else:
                tahmin = fiyat

        # --- C. DURUM ANALİZİ ---
        fark_yuzdesi = ((fiyat - tahmin) / tahmin) * 100
        tahmin_str = format_money(tahmin)
        
        if fark_yuzdesi > 15:
            durum = "Pahalı 🔴"
            mesaj = f"Yapay Zeka analizine göre bu ürün, özelliklerine kıyasla %{int(fark_yuzdesi)} daha pahalı."
        elif fark_yuzdesi < -15:
            durum = "Ucuz (Fırsat) 🟢"
            mesaj = f"Bu ürün piyasa değerinin %{int(abs(fark_yuzdesi))} altında! Fırsat olabilir."
        else:
            durum = "Adil Fiyat 🟡"
            mesaj = "Fiyat, ürünün özelliklerine ve piyasa koşullarına uygun."

        # --- D. ÖNERİLER ---
        oneriler = []
        if not df.empty:
            alternatifler = df[
                (df['Kategori'] == kategori) & 
                (df['Fiyat'] < fiyat) & 
                (df['Fiyat'] > fiyat * 0.5) 
            ].sort_values(by='Fiyat').head(3)
            
            for _, row in alternatifler.iterrows():
                img = row.get('Resim', '')
                if pd.isna(img) or str(img) == "nan" or img == "": 
                    img = "https://via.placeholder.com/150?text=Resim+Yok"
                
                oneriler.append({
                    "ad": row['Model'],
                    "fiyat": format_money(row['Fiyat']), 
                    "link": row['Link'],
                    "resim": img
                })

        return jsonify({
            "tahmin": tahmin_str,
            "durum": durum,
            "mesaj": mesaj,
            "oneriler": oneriler
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Akıllı API (v2) Başladı...")
    app.run(port=5000)