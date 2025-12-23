#!/bin/bash
# n11.com'dan görselleri çekme scripti
# Güvenli çalıştırma için batch'ler halinde çalışır

cd "$(dirname "$0")"

echo "🚀 n11.com Görsel Çekme İşlemi Başlıyor..."
echo "⚠️  Bu işlem uzun sürebilir (7000+ ürün için ~4-6 saat)"
echo ""
read -p "Devam etmek istiyor musunuz? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ İşlem iptal edildi"
    exit 1
fi

echo "✅ İşlem başlatılıyor..."
echo "💡 İlerlemeyi görmek için: tail -f /tmp/n11_image_fetch.log"
echo ""

# Scripti arka planda çalıştır ve log'la
python3 fetch_images_from_n11.py 2>&1 | tee /tmp/n11_image_fetch.log

echo ""
echo "✅ İşlem tamamlandı! Log dosyası: /tmp/n11_image_fetch.log"






