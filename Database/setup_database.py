from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import urllib

# --- AYARLAR (KENDİ SUNUCU ADINI YAZ!) ---
SERVER_NAME = r"localhost\SQLEXPRESS"  # Veya 'localhost'
DATABASE_NAME = "WiseCartDB"

# MSSQL Bağlantı Stringi (Windows Authentication ile)
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;"
)
DB_URL = f"mssql+pyodbc:///?odbc_connect={params}"

Base = declarative_base()

# --- TABLO TANIMLARI (7 ADET) ---

class Role(Base):
    __tablename__ = 'Roles'
    Id = Column(Integer, primary_key=True)
    Name = Column(String(50), nullable=False) # Admin, User

class User(Base):
    __tablename__ = 'Users'
    Id = Column(Integer, primary_key=True)
    Username = Column(String(50), nullable=False)
    Email = Column(String(100), nullable=False)
    PasswordHash = Column(String(255), nullable=False)
    RoleId = Column(Integer, ForeignKey('Roles.Id'))
    CreatedAt = Column(DateTime, default=datetime.datetime.utcnow)

class Category(Base):
    __tablename__ = 'Categories'
    Id = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False)
    products = relationship("Product", back_populates="category")

class Brand(Base):
    __tablename__ = 'Brands'
    Id = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False)
    products = relationship("Product", back_populates="brand")

class Product(Base):
    __tablename__ = 'Products'
    Id = Column(Integer, primary_key=True)
    Name = Column(String(500), nullable=False)
    Model = Column(String(255))
    CurrentPrice = Column(Float)
    ReviewCount = Column(Integer, default=0)
    Url = Column(String(1000))
    ImageUrl = Column(String(1000))
    
    CategoryId = Column(Integer, ForeignKey('Categories.Id'))
    BrandId = Column(Integer, ForeignKey('Brands.Id'))
    
    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    price_history = relationship("PriceHistory", back_populates="product")

class PriceHistory(Base):
    __tablename__ = 'PriceHistory'
    Id = Column(Integer, primary_key=True)
    Price = Column(Float, nullable=False)
    Date = Column(DateTime, default=datetime.datetime.utcnow)
    ProductId = Column(Integer, ForeignKey('Products.Id'))
    product = relationship("Product", back_populates="price_history")

class SystemLog(Base):
    __tablename__ = 'SystemLogs'
    Id = Column(Integer, primary_key=True)
    Level = Column(String(50)) # Info, Error
    Message = Column(Text)
    Date = Column(DateTime, default=datetime.datetime.utcnow)

# --- ÇALIŞTIRMA ---
# ÖNEMLİ: Bu kod veritabanını oluşturmaz, tabloları oluşturur.
# Önce SSMS'den 'WiseCartDB' adında boş bir veritabanı açılmalıdır!
if __name__ == "__main__":
    try:
        engine = create_engine(DB_URL)
        Base.metadata.create_all(engine)
        print("✅ MSSQL Tabloları Başarıyla Oluşturuldu!")
    except Exception as e:
        print(f"❌ Hata: {e}")
        print("Çözüm: SSMS'ten 'WiseCartDB' veritabanını oluşturduğuna ve Server Adının doğru olduğuna emin ol.")