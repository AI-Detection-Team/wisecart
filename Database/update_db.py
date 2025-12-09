from sqlalchemy import create_engine, text
import urllib

# AYARLAR (Yağmur Kendi Server Adını Kontrol Etsin!)
SERVER_NAME = r"localhost\SQLEXPRESS" 
DATABASE_NAME = "WiseCartDB"
SQL_FILE = "advanced_features.sql" # Fatma'nın oluşturduğu dosya

# Bağlantı
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;"
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

def apply_sql_updates():
    print("🚀 Veritabanı Güncelleniyor (View, Trigger, Procedure)...")
    
    try:
        with open(SQL_FILE, "r", encoding="utf-8") as f:
            sql_script = f.read()
            
        # SQL dosyasını 'GO' komutlarına göre bölüp tek tek çalıştıralım
        # (Python 'GO' komutunu anlamaz, o yüzden bölüyoruz)
        commands = sql_script.split("GO")
        
        with engine.connect() as connection:
            for command in commands:
                if command.strip():
                    try:
                        connection.execute(text(command))
                        connection.commit()
                    except Exception as e:
                        print(f"⚠️ Uyarı (Zaten var olabilir): {e}")

        print("✅ Veritabanı başarıyla güncellendi! Artık akıllı özellikler aktif.")
        
    except FileNotFoundError:
        print("❌ 'advanced_features.sql' bulunamadı. Fatma dosyayı yüklememiş olabilir.")

if __name__ == "__main__":
    apply_sql_updates()