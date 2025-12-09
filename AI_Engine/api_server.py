from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

# 1. Modeli ve Veriyi Yükle
try:
    model = joblib.load("price_model.pkl")
    print("✅ Model Yüklendi.")
except:
    print("⚠️ Model bulunamadı. İstatistik Modu Aktif.")
    model = None

# Veri setini hafızaya al (Ortalama hesaplamak için şart)
try:
    df = pd.read_csv("tum_urunler_v3.csv")
    # Fiyatı sayıya çevir (Garanti temizlik)
    df['Fiyat'] = df['Fiyat'].astype(str).str.replace("TL","").str.replace(".","").str.replace(",",".")
    df['Fiyat'] = pd.to_numeric(df['Fiyat'], errors='coerce')
    print(f"✅ Veri Seti Hazır: {len(df)} ürün.")
except:
    df = pd.DataFrame()
    print("❌ Veri seti okunamadı! İstatistikler çalışmayabilir.")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        fiyat = float(data.get('Fiyat', 0))
        marka = data.get('Marka', '')
        kategori = data.get('Kategori', '')
        
        # --- TAHMİN MEKANİZMASI ---
        tahmin = 0
        
        # Yöntem 1: Varsa Veri Setinden Ortalamayı Al (En Gerçekçi Yöntem)
        if not df.empty:
            # Aynı marka ve kategorideki ürünlerin ortalaması
            benzer_urunler = df[(df['Kategori'] == kategori) & (df['Marka'] == marka)]
            
            if len(benzer_urunler) > 0:
                tahmin = benzer_urunler['Fiyat'].mean()
            else:
                # Marka yoksa sadece kategori ortalaması
                kategori_urunleri = df[df['Kategori'] == kategori]
                if len(kategori_urunleri) > 0:
                    tahmin = kategori_urunleri['Fiyat'].mean()
                else:
                    tahmin = fiyat # Hiç veri yoksa fiyatın kendisi kabul edilir (Normal)
        
        # Eğer veri setinden sonuç çıkmadıysa fiyatın kendisini baz al
        if tahmin == 0: tahmin = fiyat

        # --- DURUM ANALİZİ ---
        # %20'den fazla fark varsa uyarı ver, yoksa Normal de.
        fark_yuzdesi = ((fiyat - tahmin) / tahmin) * 100
        
        if fark_yuzdesi > 20:
            durum = "Pahalı 🔴"
            mesaj = f"Bu ürün, {marka} ortalamasından %{int(fark_yuzdesi)} daha pahalı."
        elif fark_yuzdesi < -20:
            durum = "Ucuz (Fırsat) 🟢"
            mesaj = f"Bu ürün piyasa ortalamasının %{int(abs(fark_yuzdesi))} altında!"
        else:
            durum = "Normal (Adil Fiyat) 🟡"
            mesaj = "Fiyat, piyasa koşullarına uygun görünüyor."

        # --- ÖNERİLER (RESİMLİ) ---
        oneriler = []
        if not df.empty:
            # Daha ucuz alternatifleri bul
            alternatifler = df[
                (df['Kategori'] == kategori) & 
                (df['Fiyat'] < fiyat) & 
                (df['Fiyat'] > fiyat * 0.5) # Çok ucuzları (kılıf vs) ele
            ].sort_values(by='Fiyat').head(3)
            
            for _, row in alternatifler.iterrows():
                img = row.get('Resim', '')
                if pd.isna(img) or str(img) == "nan" or img == "": 
                    img = "https://via.placeholder.com/150?text=Resim+Yok"
                
                oneriler.append({
                    "ad": row['Model'],
                    "fiyat": row['Fiyat'],
                    "link": row['Link'],
                    "resim": img
                })

        return jsonify({
            "tahmin": int(tahmin),
            "durum": durum,
            "mesaj": mesaj,
            "oneriler": oneriler
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)