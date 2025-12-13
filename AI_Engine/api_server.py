from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
# Tüm kaynaklardan gelen isteklere izin ver (CORS Hatasını Çözer)
CORS(app, resources={r"/*": {"origins": "*"}})

print("🔥 API Sunucusu (Akıllı Mantık v3) Başlatılıyor...")

# 1. Modeli Yükle
model = None
try:
    model = joblib.load("price_model.pkl")
    print("✅ Model Yüklendi.")
except:
    print("⚠️ Model Yok, Tamamen İstatistik Modunda Çalışacak.")

# 2. Veri Setini Yükle (Karşılaştırma İçin Şart)
df = pd.DataFrame()
try:
    df = pd.read_csv("tum_urunler_v3.csv")
    # Fiyatı Temizle (TL, nokta, virgül karmaşasını çöz)
    df['Fiyat'] = df['Fiyat'].astype(str).str.replace("TL", "").str.replace(" ", "")
    # Binlik ayırıcı noktaları sil, kuruş virgülünü nokta yap
    df['Fiyat'] = df['Fiyat'].apply(lambda x: x.replace(".", "") if x.count(".") > 0 and "," in x else x) 
    df['Fiyat'] = df['Fiyat'].str.replace(",", ".")
    df['Fiyat'] = pd.to_numeric(df['Fiyat'], errors='coerce')
    
    print(f"✅ Veri Seti Hazır: {len(df)} ürün hafızada.")
except Exception as e:
    print(f"❌ Veri Seti Hatası: {e}")

# Para Formatlayıcı
def format_money(value):
    return "{:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    try:
        data = request.json
        print(f"📩 İstek: {data.get('Model')} - {data.get('Fiyat')} TL")

        # Gelen veriler
        gelen_fiyat = float(data.get('Fiyat', 0))
        marka = data.get('Marka', '')
        kategori = data.get('Kategori', '')
        urun_adi = data.get('Model', '')

        # --- 1. MANTIKLI TAHMİN MOTORU ---
        tahmin = 0
        kaynak = "Yapay Zeka"

        # A. Önce Modelden Tahmin İste
        if model:
            try:
                input_df = pd.DataFrame([{'Model': urun_adi, 'Marka': marka, 'Kategori': kategori}])
                tahmin = model.predict(input_df)[0]
            except: pass
        
        # B. Veritabanı Ortalamasını Bul (Referans Noktası)
        ortalama_fiyat = gelen_fiyat
        if not df.empty:
            # Aynı kategorideki ve markadaki ürünlerin ortalaması
            benzerler = df[(df['Kategori'] == kategori) & (df['Marka'] == marka)]
            if len(benzerler) > 5:
                ortalama_fiyat = benzerler['Fiyat'].mean()
            else:
                # Marka verisi azsa sadece kategoriye bak
                genel_benzerler = df[df['Kategori'] == kategori]
                if not genel_benzerler.empty:
                    ortalama_fiyat = genel_benzerler['Fiyat'].mean()

        # C. SAÇMALAMA KONTROLÜ (Outlier Detection)
        # Eğer modelin tahmini, piyasa ortalamasından veya fiyattan 3 kat fazlaysa modele güvenme.
        if tahmin > (ortalama_fiyat * 3) or tahmin < (ortalama_fiyat / 3) or tahmin == 0:
            print(f"⚠️ Model saçmaladı ({tahmin:.0f}). İstatistiğe dönülüyor.")
            tahmin = ortalama_fiyat
            kaynak = "Piyasa Verisi"

        # --- 2. DURUM ANALİZİ ---
        # Kullanıcının fiyatı ile Olması Gereken (Tahmin) arasındaki fark
        fark_yuzdesi = ((gelen_fiyat - tahmin) / tahmin) * 100
        
        durum = "Adil Fiyat 🟡"
        mesaj = f"{marka} markasının {kategori} piyasasına göre fiyatı normal görünüyor."

        if fark_yuzdesi > 20: 
            durum = "Pahalı 🔴"
            mesaj = f"Dikkat! {kaynak} analizine göre bu ürün piyasa ortalamasından %{int(fark_yuzdesi)} daha pahalı."
        elif fark_yuzdesi < -20:
            durum = "Ucuz (Fırsat) 🟢"
            mesaj = f"Harika! Bu ürün özellikleri dikkate alındığında piyasa değerinden %{int(abs(fark_yuzdesi))} daha uygun."

        # --- 3. ÖNERİ MOTORU (Daha Ucuz Alternatifler) ---
        oneriler = []
        if not df.empty:
            # Aynı kategoride olup, şu anki fiyattan DAHA UCUZ olanları getir
            alternatifler = df[
                (df['Kategori'] == kategori) & 
                (df['Fiyat'] < gelen_fiyat) &      # Daha ucuz olsun
                (df['Fiyat'] > gelen_fiyat * 0.3)  # Ama çok da kalitesiz olmasın (%30'undan ucuz olmasın)
            ].sort_values(by='Fiyat', ascending=True).head(4) # En ucuz 4 tanesi

            for _, row in alternatifler.iterrows():
                # Resim Kontrolü
                img = row.get('Resim', '')
                if pd.isna(img) or str(img).strip() == "" or "http" not in str(img):
                    img = "https://via.placeholder.com/60?text=Urun" # Varsayılan Resim
                
                oneriler.append({
                    "ad": str(row['Model']),
                    "fiyat": format_money(row['Fiyat']),
                    "link": str(row['Link']),
                    "resim": img
                })

        # Cevap Hazırla
        response = jsonify({
            "tahmin": format_money(tahmin),
            "durum": durum,
            "mesaj": mesaj,
            "oneriler": oneriler
        })
        return _build_cors_actual_response(response)

    except Exception as e:
        print(f"❌ HATA: {e}")
        return jsonify({"error": str(e)}), 500

def _build_cors_preflight_response():
    response = jsonify({})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

def _build_cors_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == '__main__':
    app.run(port=5000, debug=True)