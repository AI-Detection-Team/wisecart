using Microsoft.AspNetCore.Mvc;
using System.Net.Http;
using System.Threading.Tasks;
using System.Xml.Linq; // XML okumak için

namespace WiseCart_Web.ViewComponents
{
    // 📋 İSTER 3: ViewComponent - Currency ViewComponent (SOAP entegrasyonu ile dinamik içerik)
    public class CurrencyViewComponent : ViewComponent
    {
        public async Task<IViewComponentResult> InvokeAsync()
        {
            string dollarRate = "0.00";

            try
            {
                // 1. SOAP XML İsteği Hazırla
                string soapEnvelope = @"<?xml version=""1.0"" encoding=""utf-8""?>
                <soap:Envelope xmlns:xsi=""http://www.w3.org/2001/XMLSchema-instance"" xmlns:xsd=""http://www.w3.org/2001/XMLSchema"" xmlns:soap=""http://schemas.xmlsoap.org/soap/envelope/"">
                  <soap:Body>
                    <GetCurrency xmlns=""http://wisecart.org/"">
                      <CurrencyCode>USD</CurrencyCode>
                    </GetCurrency>
                  </soap:Body>
                </soap:Envelope>";

                // 2. Python Servisine Gönder (Port 8000)
                using (var client = new HttpClient())
                {
                    var content = new StringContent(soapEnvelope, System.Text.Encoding.UTF8, "text/xml");
                    var response = await client.PostAsync("http://localhost:8000", content);
                    
                    if (response.IsSuccessStatusCode)
                    {
                        // 3. Gelen XML Cevabını Oku
                        string xmlResponse = await response.Content.ReadAsStringAsync();
                        
                        // Basitçe XML içinden sayıyı cımbızla çekiyoruz
                        // <GetCurrencyResult>34.50</GetCurrencyResult>
                        int start = xmlResponse.IndexOf("<GetCurrencyResult>") + 19;
                        int end = xmlResponse.IndexOf("</GetCurrencyResult>");
                        
                        if (start > 19 && end > start)
                        {
                            dollarRate = xmlResponse.Substring(start, end - start);
                        }
                    }
                }
            }
            catch
            {
                dollarRate = "---"; // Hata olursa çizgi göster
            }

            // Veriyi View'a gönder
            return View("Default", dollarRate);
        }
    }
}