from flask import Flask, Response
import requests
import xml.etree.ElementTree as ET
import random

app = Flask(__name__)

def get_real_tcmb_rate():
    try:
        # TCMB (Merkez Bankası) API'sine İstek At
        url = "https://www.tcmb.gov.tr/kurlar/today.xml"
        response = requests.get(url, timeout=2) # 2 saniye bekle, gelmezse vazgeç
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for currency in root.findall('Currency'):
                if currency.get('CurrencyCode') == "USD":
                    rate = currency.find('ForexSelling').text
                    # KANIT 1: Terminale Yaz
                    print(f"✅ TCMB BAĞLANTISI BAŞARILI! Gerçek Kur: {rate}")
                    return rate
    except Exception as e:
        print(f"⚠️ TCMB Hatası: {e}")
        return None

@app.route('/', methods=['POST', 'GET'])
def soap_service():
    print("\n-----------------------------------------")
    print("📡 SOAP İsteği Geldi (Dolar Kuru Soruluyor)")
    
    # 1. Gerçek Bankayı Dene
    dolar_kuru = get_real_tcmb_rate()
    kaynak = "TCMB (Gerçek)"
    
    # 2. Banka cevap vermezse Rastgele Üret (Yedek Plan)
    if dolar_kuru is None:
        dolar_kuru = round(40.50 + random.random(), 2)
        kaynak = "Simülasyon (Random)"
        print(f"🎲 TCMB Cevap Vermedi, Rastgele Sayı Üretildi: {dolar_kuru}")
    
    soap_response = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <GetCurrencyResponse xmlns="http://wisecart.org/">
          <GetCurrencyResult>{dolar_kuru}</GetCurrencyResult>
        </GetCurrencyResponse>
      </soap:Body>
    </soap:Envelope>"""
    
    return Response(soap_response, mimetype='text/xml')

if __name__ == '__main__':
    print("🌍 SOAP Servisi (TCMB Modu) Çalışıyor: http://localhost:8000")
    app.run(port=8000)