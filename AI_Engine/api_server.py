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

try:
    df = pd.read_csv("tum_urunler_v3.csv")
    # Fiyatı sayıya çevir (Garanti olsun)
    df['Fiyat'] = df['Fiyat'].astype(str).str.replace("TL","").str.replace(".","").str.replace(",",".")
    df['Fiyat'] = pd.to_numeric(df['Fiyat'], errors='coerce')
    print(f"✅ Veri Seti Hazır: {len(df)} ürün.")
except Exception as e:
    print(f"❌ Veri seti yüklenemedi: {e}")
    df = pd.DataFrame()

# --- PARA FORMATI FONKSİYONU ---
def format_money(value):
    """Sayıyı 25.000 formatına çevirir"""
    try:
        # Binlik ayracı olarak nokta kullan
        return "{:,.0f}".format(value).replace(",", ".")
    except:
        return str(value)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        fiyat = float(data.get('Fiyat', 0))
        marka = data.get('Marka', '')
        kategori = data.get('Kategori', '')
        
        # --- TAHMİN MEKANİZMASI ---
        tahmin = 0
        
        if not df.empty:
            # Marka ve Kategori ortalaması
            benzer_urunler = df[(df['Kategori'] == kategori) & (df['Marka'] == marka)]
            
            if len(benzer_urunler) > 0:
                tahmin = benzer_urunler['Fiyat'].mean()
            else:
                kategori_urunleri = df[df['Kategori'] == kategori]
                if len(kategori_urunleri) > 0:
                    tahmin = kategori_urunleri['Fiyat'].mean()
                else:
                    tahmin = fiyat 
        
        if tahmin == 0: tahmin = fiyat

        # --- DURUM ANALİZİ ---
        fark_yuzdesi = ((fiyat - tahmin) / tahmin) * 100
        
        # Tahmin Edilen Fiyatı Formatla (Örn: 25.000)
        tahmin_str = format_money(tahmin)
        
        if fark_yuzdesi > 20:
            durum = "Pahalı 🔴"
            mesaj = f"Bu ürün, {marka} ortalamasından %{int(fark_yuzdesi)} daha pahalı."
        elif fark_yuzdesi < -20:
            durum = "Ucuz (Fırsat) 🟢"
            mesaj = f"Bu ürün piyasa ortalamasının %{int(abs(fark_yuzdesi))} altında!"
        else:
            durum = "Normal (Adil Fiyat) 🟡"
            mesaj = "Fiyat, piyasa koşullarına uygun görünüyor."

        # --- ÖNERİLER (DÜZELTİLDİ) ---
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
                
                # BURASI DÜZELDİ: Fiyatı formatlayarak listeye ekliyoruz
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
    app.run(port=5000)