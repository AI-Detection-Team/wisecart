from flask import Flask, Response, request

app = Flask(__name__)

# SOAP Servisi XML ile konuşur
@app.route('/', methods=['POST', 'GET'])
def soap_service():
    # 1. Gelen isteği al (Logla)
    print("📡 SOAP İsteği Alındı!")
    
    # 2. SOAP XML Cevabı Hazırla
    # Bu XML formatı standart bir SOAP cevabıdır.
    soap_response = """<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <GetCurrencyResponse xmlns="http://wisecart.org/">
          <GetCurrencyResult>34.50</GetCurrencyResult>
        </GetCurrencyResponse>
      </soap:Body>
    </soap:Envelope>"""
    
    # 3. Cevabı XML olarak gönder
    return Response(soap_response, mimetype='text/xml')

if __name__ == '__main__':
    print("🌍 SOAP Servisi Çalışıyor: http://localhost:8000")
    # Flask'ı 8000 portunda çalıştırıyoruz (Diğerleriyle çakışmasın)
    app.run(port=8000) 