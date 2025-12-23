using Microsoft.AspNetCore.Mvc;
using Grpc.Net.Client;
using WiseCart_Web.Protos; // Otomatik oluşan namespace
using System.Threading.Tasks;

namespace WiseCart_Web.ViewComponents
{
    // 📋 İSTER 3: ViewComponent - GrpcStatus ViewComponent (gRPC entegrasyonu ile dinamik içerik)
    public class GrpcStatusViewComponent : ViewComponent
    {
        public async Task<IViewComponentResult> InvokeAsync()
        {
            string statusMessage = "Bağlantı Yok 🔴";
            try
            {
                // Python gRPC sunucusuna (50051) bağlan
                // http://localhost:50051 adresi Pınar'ın sunucusu
                using var channel = GrpcChannel.ForAddress("http://localhost:50051");
                var client = new StatusCheck.StatusCheckClient(channel);
                var reply = await client.GetSystemStatusAsync(new Empty());
                statusMessage = reply.Message;
            }
            catch
            {
                statusMessage = "gRPC Sunucusu Kapalı ⚠️";
            }
            return View("Default", statusMessage);
        }
    }
}