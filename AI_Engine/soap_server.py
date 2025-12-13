from flask import Flask, Response
import random # Rastgele sayı üretmek için

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def soap_service():
    # 1. Kanıt: İsteğin geldiğini terminale yaz
    print("📡 SOAP İsteği Geldi: C# Sitesi kuru sordu!")
    
    # 2. İşlem: 42 ile 43 arasında rastgele sayı üret
    # Bu sayede sayfayı her yenilediğinizde sayı değişir
    canli_kur = round(42.00 + random.random(), 2)
    
    # 3. Cevap: XML oluştur
    soap_response = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <GetCurrencyResponse xmlns="http://wisecart.org/">
          <GetCurrencyResult>{canli_kur}</GetCurrencyResult>
        </GetCurrencyResponse>
      </soap:Body>
    </soap:Envelope>"""
    
    return Response(soap_response, mimetype='text/xml')

if __name__ == '__main__':
    print("🌍 SOAP Servisi (Canlı Mod) Çalışıyor: http://localhost:8000")
    app.run(port=8000)