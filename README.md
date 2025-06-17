# Atatürk Söz Yapıcı

Bu yazılım, Atatürk'ün ilham veren sözlerini görsel olarak tasarlamanızı ve paylaşmanızı sağlar. Kullanıcı dostu arayüzü ile metinleri, görselleri ve arka planları kolayca özelleştirebilirsiniz. Kendi resimlerinizi yükleme ve öğeleri sürükle-bırak ile konumlandırma imkanı sunar.

## Özellikler:

* **Metin Özelleştirme:** Font boyutu, rengi ve içeriği üzerinde tam kontrol.
* **Görsel Seçimi:** Uygulama içi Atatürk görselleri veya kendi yüklediğiniz görselleri kullanın.
* **Arka Plan Ayarları:** Renk seçimi veya özel arka plan görseli yükleme.
* **Sürükle-Bırak:** Görsel ve imza konumlarını kolayca düzenleyin.
* **Anlık Önizleme:** Yaptığınız değişiklikleri gerçek zamanlı görün.
* **PNG Kayıt:** Oluşturduğunuz görselleri yüksek kalitede PNG olarak kaydedin.

## Kurulum ve Çalıştırma:

1.  Depoyu klonlayın veya indirin.
2.  Gerekli kütüphaneleri yükleyin: `pip install Pillow pyinstaller`
3.  Uygulamayı çalıştırın: `python main.py`
4.  .EXE oluşturmak için (Windows): `pyinstaller --noconfirm --onefile --windowed --add-data "images;images" main.py` komutunu kullanın. (Çıktı `dist` klasöründe olacaktır.)

**Not:** `images` klasörünün `main.py` ile aynı dizinde ve gerekli resim dosyalarını (`ataturk1.png` vb., `imza.png`) içerdiğinden emin olun.

## Katkıda Bulunma:

Geri bildirimleriniz ve katkılarınız değerlidir!
