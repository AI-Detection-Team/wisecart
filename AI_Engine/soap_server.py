from flask import Flask, Response, request

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def soap_service():
    # C# Loglarında görünmesi için yazdır
    print("📡 SOAP İsteği Alındı (Döviz Kuru Soruluyor...)")
    
    # Standart SOAP XML Cevabı
    soap_response = """<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <GetCurrencyResponse xmlns="http://wisecart.org/">
          <GetCurrencyResult>34.50</GetCurrencyResult>
        </GetCurrencyResponse>
      </soap:Body>
    </soap:Envelope>"""
    
    return Response(soap_response, mimetype='text/xml')

if __name__ == '__main__':
    print("🌍 SOAP Servisi Çalışıyor: http://localhost:8000")
    app.run(port=8000)