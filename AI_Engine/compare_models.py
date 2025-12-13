import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
import joblib

# 1. VERİYİ YÜKLE
print("⏳ Veri Yükleniyor...")
try:
    df = pd.read_csv("tum_urunler_v3.csv")
except:
    print("❌ Veri dosyası (tum_urunler_v3.csv) bulunamadı!")
    exit()

# 2. TEMİZLİK
def clean_price(price):
    if pd.isna(price): return None
    s = str(price).strip().replace("TL", "").replace(" ", "")
    # Noktalama temizliği
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif "." in s:
        if len(s.split(".")[-1]) == 3: s = s.replace(".", "") # 10.500 -> 10500
        
    try:
        val = float(s)
        if val < 100 or val > 1500000: return None # Uçuk fiyatları at
        return val
    except: return None

df['Fiyat'] = df['Fiyat'].apply(clean_price)
df.dropna(subset=['Fiyat', 'Model', 'Marka', 'Kategori'], inplace=True)
print(f"✅ Temiz Veri Sayısı: {len(df)}")

# 3. EĞİTİM (Pipeline)
X = df[['Model', 'Marka', 'Kategori']]
y = df['Fiyat']

preprocessor = ColumnTransformer(
    transformers=[
        ('text', TfidfVectorizer(max_features=1000), 'Model'),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['Marka', 'Kategori'])
    ]
)

# Random Forest kullanıyoruz (En iyisi buydu)
pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                           ('model', RandomForestRegressor(n_estimators=100, random_state=42))])

print("🧠 Model Eğitiliyor (Bu işlem 30-60 saniye sürebilir)...")
pipeline.fit(X, y)

# 4. KAYDET
joblib.dump(pipeline, "price_model.pkl")
print("💾 Model Başarıyla Kaydedildi! (price_model.pkl)")