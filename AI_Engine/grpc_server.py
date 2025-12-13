import grpc
from concurrent import futures
import time

# Otomatik üretilen dosyaları import et
import server_status_pb2
import server_status_pb2_grpc

class StatusServicer(server_status_pb2_grpc.StatusCheckServicer):
    def GetSystemStatus(self, request, context):
        # C# tarafına gidecek mesaj
        print("📡 gRPC İsteği Geldi!")
        return server_status_pb2.StatusReply(message="Sistem Aktif 🟢 (Python gRPC)")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_status_pb2_grpc.add_StatusCheckServicer_to_server(StatusServicer(), server)
    
    # 50051 Portunda Çalıştır
    server.add_insecure_port('[::]:50051')
    print("🚀 gRPC Sunucusu Başladı: Port 50051")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()