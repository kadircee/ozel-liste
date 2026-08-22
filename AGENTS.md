# AGENTS.md

- Bu deponun yapısı, kuralları, kurulumu ve güncel durumu için önce `DEPO-BILGILERI.md` dosyasını oku. Liste değişikliği yapmadan önce şu kurallara uy: bozuk eklenti silinmez (`status:0` yapılır); delete-zone'daki eklentiler yeniden eklenmez.
- Geriye dönük uyumluluğu korumayın. Uyumluluk katmanları, geri dönüş (fallback) mekanizmaları veya geçiş (migration) betikleri eklemek yerine, kullanılmayan kod yollarını kaldırın.
- Mevcut gereksinimleri tam olarak karşılayan en basit uygulamayı seçin. Spekülatif soyutlamalardan, gereksiz yapılandırmadan ve dolaylı katmanlardan kaçının.
- Sistemi katman katman büyütün. Uçtan uca çalışan en küçük sürümle başlayın; her yeni özelliği halihazırda çalışan bir ürünün üzerine ekleyin. Çalışan bir ürünü bitmemiş karmaşıklık uğruna asla feda etmeyin.
- Bileşenleri modüler tutun ve sorumlulukları net biçimde ayrıştırın.
- Genel karmaşıklığı azalttıklarında veya güvenilirliği artırdıklarında yerleşik, iyi bakımı yapılan kütüphaneleri tercih edin. Açık bir neden olmadan yaygın işlevselliği yeniden yazmayın.
- Kendi uygulamanızı yazmadan veya yeni paket eklemeden önce projedeki mevcut bağımlılıklardan yararlanın. Dokümantasyonunu ve tür tanımlarını kontrol etmeden bir kütüphanenin bir özellikten yoksun olduğunu varsaymayın.
- Mimari kararları uzun vadeli verin. Yalnızca şimdilik çalışan ve sonradan değiştirilmesi gereken geçici çözümleri kabul etmeyin.