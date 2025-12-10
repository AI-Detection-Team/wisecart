import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# --- 1. VERİYİ YÜKLE ---
print("⏳ Veri Yükleniyor...")
try:
    df = pd.read_csv("tum_urunler_tam.csv")
except:
    try: df = pd.read_csv("cleaned_data.csv")
    except: 
        print("❌ Veri bulunamadı!"); exit()

# --- 2. AGRESİF FİYAT TEMİZLİĞİ (Hatayı Düzelten Kısım) ---
def ultra_clean_price(price):
    if pd.isna(price): return None
    s = str(price).strip().replace("TL", "").replace(" ", "")
    
    # Noktalama Karmaşasını Çöz:
    # Türkiye standardı: 1.250,50 (Binlik nokta, Kuruş virgül)
    if "," in s:
        s = s.replace(".", "")  # Binlik noktasını at (1.250 -> 1250)
        s = s.replace(",", ".") # Virgülü nokta yap (.50)
    else:
        # Sadece nokta varsa (1.250 veya 10.500) -> Binliktir, sil.
        # Ama (10.5) ise ondalıktır.
        parts = s.split(".")
        if len(parts) > 1 and len(parts[-1]) == 3: # Virgülden sonra 3 hane varsa binliktir
            s = s.replace(".", "")
            
    try:
        val = float(s)
        # Mantık Filtresi: 500 TL altı (kılıf) ve 1 Milyon TL üstü (hatalı) veriyi at
        if val < 500 or val > 1000000: return None
        return val
    except: return None

df['Fiyat'] = df['Fiyat'].apply(ultra_clean_price)
df.dropna(subset=['Fiyat', 'Model', 'Marka', 'Kategori'], inplace=True)

print(f"✅ Temiz Veri Sayısı: {len(df)}")
print(f"📊 Ortalama Fiyat: {df['Fiyat'].mean():.2f} TL (Bu sayı mantıklı mı kontrol et)")

# --- 3. ÖZELLİK MÜHENDİSLİĞİ (GİZLİ SİLAH: TF-IDF) ---
# Sadece Marka yetmez, Ürün İsmindeki "RTX", "i7", "128GB" kelimelerini de öğrensin.

X = df[['Model', 'Marka', 'Kategori']]
y = df['Fiyat']

# Pipeline Kurulumu
preprocessor = ColumnTransformer(
    transformers=[
        # Ürün ismindeki en önemli 1000 kelimeyi sayıya çevir
        ('text', TfidfVectorizer(max_features=1000), 'Model'),
        # Marka ve Kategoriyi 0-1 koduna çevir
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['Marka', 'Kategori'])
    ]
)

# --- 4. MODELLERİ TANIMLA ---
models = {
    "Ridge Regression": Ridge(), # Linear'in daha iyisi
    "Random Forest": RandomForestRegressor(n_estimators=150, random_state=42),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=150, random_state=42)
}

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\n🏁 MODELLER YARIŞIYOR (Bu biraz sürebilir)...\n" + "="*50)
best_score = -np.inf
best_pipeline = None
best_name = ""

for name, model in models.items():
    pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
    
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    print(f"🔹 {name:20} -> R2: {r2:.4f} (%{r2*100:.1f}) | Hata: {int(mae)} TL")
    
    if r2 > best_score:
        best_score = r2
        best_pipeline = pipeline
        best_name = name

print("="*50)
print(f"🏆 ŞAMPİYON: {best_name} (Başarı: %{best_score*100:.1f})")

# --- 5. KAYDET ---
joblib.dump(best_pipeline, "price_model.pkl")
# API için sütun isimleri (Gerekli olmasa da dursun)
# Not: Pipeline kullandığımız için API tarafında kod değişecek!
print("💾 Model kaydedildi. Şimdi API kodunu güncellemen gerekecek.")