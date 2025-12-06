import pandas as pd

# Final dosyasını oku
try:
    df = pd.read_csv("tum_urunler_final.csv")
    print(f"🎉 TOPLAM VERİ SAYINIZ: {len(df)}")
    print(df.groupby("Kategori").count()) # Kategorilere göre dağılımı da gösterir
except FileNotFoundError:
    print("⚠️ 'tum_urunler_final.csv' bulunamadı. Dosya ismini kontrol edin.")