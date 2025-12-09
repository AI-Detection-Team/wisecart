import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# --- 1. VERİYİ YÜKLE ---
print("⏳ Veri Yükleniyor...")
try:
    df = pd.read_csv("tum_urunler_tam.csv")
except:
    df = pd.read_csv("cleaned_data.csv")

print(f"   -> Ham Veri Sayısı: {len(df)}")

# --- 2. AKILLI FİYAT TEMİZLİĞİ ---
def clean_price_smart(price):
    if pd.isna(price): return None
    if isinstance(price, (int, float)): return float(price)
    
    s = str(price).strip().replace("TL", "").replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        parts = s.split(".")
        if len(parts) > 1 and len(parts[-1]) == 3:
            s = s.replace(".", "")
            
    try:
        val = float(s)
        if val < 500 or val > 900000: return None # Uçuk değerleri at
        return val
    except: return None

df['Fiyat'] = df['Fiyat'].apply(clean_price_smart)
df.dropna(subset=['Fiyat', 'Model', 'Marka', 'Kategori'], inplace=True)

# --- 3. IQR İLE AYKIRI DEĞER TEMİZLİĞİ (Kategori Bazlı) ---
# Fiyatı bozan aşırı uç değerleri (Outliers) atalım
df_clean = pd.DataFrame()
for cat in df['Kategori'].unique():
    cat_df = df[df['Kategori'] == cat]
    Q1 = cat_df['Fiyat'].quantile(0.25)
    Q3 = cat_df['Fiyat'].quantile(0.75)
    IQR = Q3 - Q1
    # Çok katı olmayan bir filtre (1.5 yerine 2.0 katı aldık ki veriyi çok kırmasın)
    filtered = cat_df[(cat_df['Fiyat'] >= Q1 - 2.0 * IQR) & (cat_df['Fiyat'] <= Q3 + 2.0 * IQR)]
    df_clean = pd.concat([df_clean, filtered])

print(f"   -> Temizlik Sonrası Veri: {len(df_clean)}")

# --- 4. MODEL HAZIRLIĞI (TF-IDF + OneHot) ---
print("⚙️ Özellik Mühendisliği (Feature Engineering) Yapılıyor...")

# Girdiler: Model İsmi (Metin) + Marka + Kategori
X = df_clean[['Model', 'Marka', 'Kategori']]
y = df_clean['Fiyat']

# Pipeline Oluşturma:
# 1. 'Model' sütunundaki kelimeleri (i7, 16gb, pro...) sayısal vektöre çevir (TF-IDF)
# 2. 'Marka' ve 'Kategori'yi One-Hot Encoding yap
preprocessor = ColumnTransformer(
    transformers=[
        ('text', TfidfVectorizer(max_features=500), 'Model'), # En önemli 500 kelimeyi öğren
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['Marka', 'Kategori'])
    ]
)

# Model Zinciri
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])

# Eğitim/Test Bölme
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- 5. EĞİTİM ---
print("🧠 Model Eğitiliyor (Bu işlem ürün ismindeki kelimeleri analiz ettiği için 1-2 dk sürebilir)...")
model_pipeline.fit(X_train, y_train)

# --- 6. SONUÇLAR ---
y_pred = model_pipeline.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("-" * 30)
print(f"✅ EĞİTİM BAŞARILI! (PRO SÜRÜM)")
print(f"📉 Ortalama Hata Payı (MAE): {mae:.2f} TL")
print(f"📊 Başarı Skoru (R2): {r2:.2f}")
print("-" * 30)

# --- 7. KAYDET ---
# Pipeline kullandığımız için tek dosya yeterli, vectorizer içine gömülü.
joblib.dump(model_pipeline, "price_model.pkl")
print("💾 'price_model.pkl' kaydedildi. (API'ye hazırdır!)")