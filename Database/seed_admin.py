from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_database import Base, User, Role
import urllib
import hashlib

# AYARLAR
SERVER_NAME = r"localhost\SQLEXPRESS" 
DATABASE_NAME = "WiseCartDB"

# Bağlantı
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;"
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
Session = sessionmaker(bind=engine)
session = Session()

def create_admin():
    print("👤 Admin Kullanıcısı Oluşturuluyor...")

    # 1. Admin Rolü Var mı? Yoksa Ekle.
    admin_role = session.query(Role).filter_by(Name="Admin").first()
    if not admin_role:
        admin_role = Role(Name="Admin")
        session.add(admin_role)
        session.commit()
        print("-> 'Admin' rolü oluşturuldu.")

    # 2. Admin Kullanıcısı Var mı?
    if session.query(User).filter_by(Username="admin").first():
        print("⚠️ Admin kullanıcısı zaten var! İşlem yapılmadı.")
        return

    # 3. Şifreyi Hashle (MD5 - C# Koduyla Uyumlu)
    # 123456'nın MD5 karşılığı: e10adc3949ba59abbe56e057f20f883e
    password_raw = "123456"
    password_hash = hashlib.md5(password_raw.encode()).hexdigest()

    # 4. Kullanıcıyı Kaydet
    new_admin = User(
        Username="admin",
        Email="admin@wisecart.com",
        PasswordHash=password_hash, # Şifrelenmiş hali gidiyor
        RoleId=admin_role.Id
    )
    
    session.add(new_admin)
    session.commit()
    print(f"✅ Admin Başarıyla Eklendi!")
    print(f"-> Kullanıcı Adı: admin")
    print(f"-> Şifre: {password_raw}")

if __name__ == "__main__":
    create_admin()