import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import time

# 1. VERİYİ YÜKLE
print("⏳ Veri Yükleniyor...")
try:
    df = pd.read_csv("tum_urunler_v3.csv")
except:
    try:
        df = pd.read_csv("cleaned_data.csv")
    except:
        print("❌ Veri dosyası bulunamadı! (tum_urunler_v3.csv veya cleaned_data.csv)")
        exit()

# 2. TEMİZLİK
def clean_price(price):
    if pd.isna(price): return None
    if isinstance(price, (int, float)): return float(price)
    
    s = str(price).strip().replace("TL", "").replace(" ", "")
    # Noktalama temizliği
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif "." in s:
        if len(s.split(".")[-1]) == 3: s = s.replace(".", "") # 10.500 -> 10500
        
    try:
        val = float(s)
        if val < 500 or val > 900000: return None # Uçuk fiyatları at
        return val
    except: return None

df['Fiyat'] = df['Fiyat'].apply(clean_price)
df.dropna(subset=['Fiyat', 'Model', 'Marka', 'Kategori'], inplace=True)
print(f"✅ Temiz Veri Sayısı: {len(df)}")

# 3. VERİ HAZIRLIĞI
X = df[['Model', 'Marka', 'Kategori']]
y = df['Fiyat']

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"📊 Eğitim Seti: {len(X_train)} | Test Seti: {len(X_test)}")

# Preprocessor (Tüm modeller için ortak)
preprocessor = ColumnTransformer(
    transformers=[
        ('text', TfidfVectorizer(max_features=500), 'Model'),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['Marka', 'Kategori'])
    ]
)

# 4. MODELLERİ TANIMLA
models = {
    'Linear Regression': LinearRegression(),
    'Decision Tree': DecisionTreeRegressor(random_state=42),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42)
}

# 5. MODELLERİ EĞİT VE KARŞILAŞTIR
print("\n" + "="*70)
print("🔬 MODEL KARŞILAŞTIRMASI BAŞLIYOR...")
print("="*70)

results = []

for model_name, model in models.items():
    print(f"\n🧠 {model_name} eğitiliyor...")
    
    # Pipeline oluştur
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', model)
    ])
    
    # Eğitim süresini ölç
    start_time = time.time()
    pipeline.fit(X_train, y_train)
    train_time = time.time() - start_time
    
    # Tahmin yap
    start_time = time.time()
    y_pred = pipeline.predict(X_test)
    predict_time = time.time() - start_time
    
    # Metrikleri hesapla
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    results.append({
        'Model': model_name,
        'MAE (TL)': round(mae, 2),
        'R² Score': round(r2, 4),
        'RMSE (TL)': round(rmse, 2),
        'Eğitim Süresi (sn)': round(train_time, 2),
        'Tahmin Süresi (ms)': round(predict_time * 1000, 2)
    })
    
    print(f"   ✅ MAE: {mae:.2f} TL | R²: {r2:.4f} | RMSE: {rmse:.2f} TL")

# 6. SONUÇLARI GÖSTER
print("\n" + "="*70)
print("🏆 MODEL KARŞILAŞTIRMA SONUÇLARI")
print("="*70)
print()

# Tablo formatında göster
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

print("\n" + "="*70)
print("📊 ÖZET:")
print("="*70)

# En iyi modeli bul
best_mae = results_df.loc[results_df['MAE (TL)'].idxmin()]
best_r2 = results_df.loc[results_df['R² Score'].idxmax()]

print(f"🏅 En Düşük Hata (MAE): {best_mae['Model']} - {best_mae['MAE (TL)']} TL")
print(f"🏅 En Yüksek R²: {best_r2['Model']} - {best_r2['R² Score']}")
print(f"⚡ En Hızlı Eğitim: {results_df.loc[results_df['Eğitim Süresi (sn)'].idxmin(), 'Model']}")
print("="*70)