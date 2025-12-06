import pandas as pd
import os
import glob

def merge_all_data():
    print("🔄 BÜTÜN VERİLER BİRLEŞTİRİLİYOR...")
    
    # Klasördeki "urunler" kelimesi geçen tüm CSV dosyalarını bul
    # (tum_urunler.csv, tum_urunler_mega.csv, tum_urunler_final.csv, vb.)
    csv_files = glob.glob("*urunler*.csv")
    
    if not csv_files:
        print("❌ Hiç CSV dosyası bulunamadı! Lütfen önce scraper'ları çalıştırın.")
        return

    print(f"📂 Bulunan Dosyalar: {csv_files}")
    
    df_list = []
    
    for filename in csv_files:
        try:
            df = pd.read_csv(filename)
            df_list.append(df)
            print(f"   -> '{filename}' okundu: {len(df)} satır.")
        except Exception as e:
            print(f"   ⚠️ Hata ({filename}): {e}")

    if not df_list:
        print("❌ Birleştirilecek veri yok.")
        return

    # Hepsini alt alta ekle
    df_total = pd.concat(df_list, ignore_index=True)
    
    print(f"\n📊 Birleştirme Öncesi Toplam: {len(df_total)} satır")
    
    # --- TEMİZLİK VE DEDUPLICATION (AYNI ÜRÜNLERİ SİL) ---
    # 'Link' sütunu aynı olanları sil (En güvenilir yöntem budur)
    df_total.drop_duplicates(subset=['Link'], keep='first', inplace=True)
    
    # Fiyatı temizle (Garanti olsun)
    try:
        df_total['Fiyat'] = df_total['Fiyat'].astype(str).str.replace(" TL", "").str.replace("TL", "")
        df_total['Fiyat'] = df_total['Fiyat'].str.replace(".", "").str.replace(",", ".")
        # Sadece sayısal fiyatı olanları tut
        df_total = df_total[pd.to_numeric(df_total['Fiyat'], errors='coerce').notnull()]
    except: pass

    print(f"✅ TEMİZLİK SONRASI NET VERİ: {len(df_total)} satır")
    print("-" * 40)
    print(df_total.groupby("Kategori").count())
    print("-" * 40)

    # --- FİNAL DOSYAYI KAYDET ---
    # Bu dosya artık projenin TEK GERÇEĞİ olacak.
    df_total.to_csv("tum_urunler_tam.csv", index=False)
    print("💾 'tum_urunler_tam.csv' dosyası oluşturuldu.")
    print("🚀 EDA ve Veritabanı aşamasına bu dosya ile geçebilirsiniz!")

if __name__ == "__main__":
    merge_all_data()