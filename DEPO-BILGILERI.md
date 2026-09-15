# developer (ozel-liste)
Bu depo test CloudStream deposudur; yalnızca Türkçe film/dizi eklentilerini ve test seçtiği kaynakları barındırır. Canlı yayın, NSFW ve yabancı dil içerikli eklentiler kullanıcı tercihi gereği listeye alınmamıştır.

## Durum
- **Son doğrulama:** 2026-09-15 · **40 eklenti** (34 açık + 6 kapalı (AltiYuzAltmisAltiFilmIzle, DiziFilmORG, FilmBip, Full4kizle, FullHDFilm, SetFilmIzle)); indirilebilir, hash/boyut doğrulanmış
- **Doğrulama kanıtı (2026-09-15):** 40 `.cs3` tek tek indirildi → **39/40 SHA-256 + boyut + ZIP bütünlüğü doğrulandı**; yalnız `Full4kizle` kaynakta 404 (`status:0` — silme yok kuralı gereği kayıt korunuyor). `plugins.json` ↔ `Tüm Repolar` tablosu (34 açık kayıt) kaynak repo bazında birebir uyumlu; `Tüm Repolar` 87 satır.
- **Kural:** bozuk eklenti silinmez, `status:0` yapılır (bkz. Kurulum)
- **Delete-zone:** silinen eklentiler yeniden eklenmez (bkz. Silinen Eklentiler)

## Kurulum
CloudStream → Ayarlar → Uzantılar → Depo Ekle:
```
https://raw.githubusercontent.com/kadircee/ozel-liste/main/repo.json
```
**Tek tıkla kurulum (derin link):** CloudStream kurulu bir cihazda aşağıdaki bağlantıya tıklanınca depo otomatik eklenir (`cloudstreamrepo://` şeması uygulama tarafından çözülür):
```
cloudstreamrepo://raw.githubusercontent.com/kadircee/ozel-liste/main/repo.json
```
**Shortcode (kısayol):** CloudStream, "Depo Ekle" alanına kısa bir kod yazınca onu bir kısaltma servisinden çözer (redirect `Location` başlığından okunur):
- **`!ozel45`** → `py.md/ozel45` → `repo.json` (Türkiye'de çalışır; **önerilen**). "Depo Ekle" alanına sadece `!ozel45` yazman yeterli.
Kısa kod yalnızca harf/rakam/`!_-` içerebilir; `!` ile başlayanlar `py.md` servisine gider. Kişisel depo için zorunlu değil — tam URL de çalışır.
**İpucu — jsDelivr proxy:** CloudStream'de Ayarlar → Uzantılar bölümünde jsDelivr proxy'si açıksa (otomatik CDN dönüşümü), `raw.githubusercontent.com` adresleri hem `repo.json` hem eklenti indirmelerinde otomatik `cdn.jsdelivr.net` üzerinden çekilir. GitHub/raw Türkiye'de engellenirse bu ayar erişimi kurtarır. Uzantı hâlâ yüklenmiyorsa VPN deneyin.
**Kural — bozuk eklentiyi silme, `status:0` yap (kod kanıtıyla):** Bir eklentinin kaynak sitesi ölürse kaydı `plugins.json`'dan **silme**, `status`'ünü `0`'a çek (kayıt listede kalır). Kod kanıtı (`recloudstream/cloudstream` → `app/src/main/java/com/lagradost/cloudstream3/plugins/PluginManager.kt`):
- `isDisabled = plugin.status == PROVIDER_STATUS_DOWN` (satır 231) → güncelleme döngüsünde `if (pluginData.isDisabled) { unloadPlugin(...) }` (satır 306) → uygulama, repo yenilendiğinde eklentiyi **otomatik kaldırır**.
- Kaydı tamamen silersen uygulama yerel kopyayla eşleşecek kayıt bulamaz → eski kurulu eklenti **yüklü ve bozuk kalır** (cihazda manuel silme dışında temizlenmez).
- Büyük repolar bu kuralı uygular: `hexated/cloudstream-extensions-hexated` listede 5 eklentiyi `status:0` ile tutuyor (Anifreakz, Anizm, GomunimeProvider, IdlixProvider, Loklok).
- Site düzelince `status`'ü `1`'e çevir ve `version`'ı bir artır (güncelleme tetiklenir).
- `status` değerleri: `0` = kapalı, `1` = açık, `2` = yavaş, `3` = sadece beta.
> **Not (ilerisi için):** Bir eklenti bozulduğunda bu kural uygulanacak: silme yok, `status:0`. Zorunlu silme gerekiyorsa (ör. yasal istek, gerçekten kaybolan kaynak) önce kullanıcıya cihazda manuel silmesi gerektiği hatırlatılmalı.

## Depo Yapısı
```
ozel-liste/
├── repo.json            → CloudStream'in açtığı depo tanımı
├── plugins.json         → eklenti listesi (40 eklenti)
├── registry.json        → makine-okur kayıt modeli (Seçim + Sağlık eksenleri)
├── registry.py          → model araçları (--sync / --check / --render [--write])
├── update.py            → kaynak depolardan güncel verileri senkronize eden script (--check rapor modu dahil)
├── backups/            → temizlenmiş CloudStream veri yedeği örneği (kişisel veri yok)
└── DEPO-BILGILERI.md    → bu doküman (tablo bloğu registry.json'dan üretilir)
```

## CloudStream Veri Yedeği (backups/)
`backups/CS3_Backup_2026_08_18_20_14_TEMIZ.txt` — CloudStream'in **Ayarlar → Güncellemeler ve Yedek → Veri Yedeği** ile ürettiği yedeğin **kişisel veriden arındırılmış** temiz örneğidir. Restore edilebilir bir referans/template dosyasıdır. Aynı içerik `backups/CS3_Backup_2026_08_18_20_14_TEMIZ.json` olarak da saklanır (aynı klasörde; uygulama/cihaza göre uzantı `.json` → `.txt` yeniden adlandırılarak kullanılabilir).
Yedek iki bloktan oluşur: `datastore` (uygulama DataStore tercihleri) ve `settings` (SharedPreferences). Bu örnekte:

**Çıkarılanlar (kişisel/önemsiz):**
- `REPOSITORIES_KEY` — ekli depolar (repo artık `!ozel45` ile ekleniyor, yedekte taşınmasına gerek yok)
- İzleme geçmişi ve kaldığın yerler: `0/result_dub/*`, `0/result_episode/*`, `0/result_season/*`, `0/video_pos_dur/*`, `0/result_resume_watching_2/*`
- Arama geçmişi + arama tercihleri: `0/search_history/*`, `0/search_pref_providers`, `0/search_pref_tags`
- İndirme önbellekleri: `download_header_cache/*`, `BACKUP_download_header_cache/*`
- Bu repoda olmayan eklentilerin ayarları: `KraptorPlus*`, `Torrentio*`, `persistent_program_ids`
- Ana sayfa API'si (`0/home_api_used` — listede olmayan eklentiye işaret ediyordu)

**Korunanlar (tercihler):**
- Oynatıcı: kalite/kaynak öncelikleri, `playback_speed`, `preferred_audio_language: tr`, `resize_mode`, `duration_mode`, video profiller
- Altyazı: `subtitle_settings`, `subs_auto_download: tr`
- `settings` bloğu bütün: `auto_update: true`, `auto_update_plugins`, jsDelivr proxy, DNS, swipe/pip/rotate, `provider_lang: tr` vb.
- Kurulum bayrakları: `VERSION_NAME`, `HAS_DONE_SETUP`, `FILES_TO_DELETE_KEY`

**Önemli değerler (kullanıcı tercihi, kaynak kod ile doğrulandı):**
- `jsdelivr_proxy_key: true` — tüm raw GitHub URL'leri jsDelivr CDN üzerinden gider (`RepositoryManager.kt` `convertRawGitUrl`); GitHub raw engelli/sorunlu ağlarda **CloudStream istemci tarafında** açılması gereken ayardır (`repo.json` yine `raw.githubusercontent.com` adresini verir — dönüşüm depo tarafında değil, uygulama tarafında yapılır). `false` = doğrudan raw GitHub, null = uygulama açılışta otomatik tespit (MainActivity.kt:1327).
- `prerelease_update: true` — uygulama artık prerelease sürümden (4.8.0-PRE) çalışıyor; güncelleme kontrolü prerelease build'leri de kapsar.
- `enable_nsfw_on_providers_key: true` — NSFW içerik destekleyen eklentilerde yetişkin içerik gösterimi açık.

**Kaynak (player) öncelikleri — semantik ve sıralama (kaynak kod ile doğrulandı):**
- Semantik: `sortLinks` → `sortedBy { -it.priority }` (`PlayerGeneratorViewModel.kt`) → **büyük sayı listede üstte**; toplam öncelik = `qualityPriority + sourcePriority`, kaynak varsayılanı = 1, negatif toplam yalnız `hide_negative_sources` açıksa gizlenir (varsayılan kapalı).
- Dublaj grubu (5-8) altyazı grubunun (0-4) üstünde tutuldu: kullanıcı Türkçe dublajı önce seçiyor (`preferred_audio_language: tr`, altyazı yedek).
- Hoster sıralaması (en iyi → en kötü): **Filemoon** (CDN + HLS, 1080p+, en sağlam) > **VidMoly** (global CDN, çoklu kalite) > **DzenRu** (dzen.ru, 1080p) > **Odnoklassniki/Okru** (ok.ru, 720p-1080p, bazen yavaş) > **Pixel** (PixelDrain, dosya hostu — 60 gün sonra bağlantılar ölebilir) > **Sibnet** (sibnet.ru, **en fazla 720p**).
- Profil 1 değerleri: Dublaj: FileMoonSx=8, Dzen=7, Odnoklassniki=6, Pixel=5 · AltYazı: Filemoon=4, VidMoly=3, Dzen=2, Odnoklassniki=1, Okru=1, Sibnet=0, Pixel=0.
> Not: Yedek dosyası repo'da referans amaçlıdır; CloudStream restore ederken repo/shortcode gerektirmez, repo yine `!ozel45` ile eklenir.

`repo.json` içeriği:
```json
{
  "name": "developer",
  "description": "Kisisel CloudStream deposu - Turkce film ve dizi eklentileri",
  "manifestVersion": 1,
  "pluginLists": [
    "https://raw.githubusercontent.com/kadircee/ozel-liste/main/plugins.json"
  ]
}
```
Her `plugins.json` kaydı: `.cs3` dosya adresi, SHA-256 `fileHash`, `fileSize`, `language`, `tvTypes`, sürüm ve durum içerir.

> **Not:** Kaynak repo bazında dağılım için bkz. **'Tüm Repolar - Alfabetik Liste'** tablosu (en güncel, tek kaynak). Bu özet tablo çift bakım yükü ve tutarsızlık riski nedeniyle kaldırıldı.

Eskiden kullanılan / hiç kullanılmayan kaynaklar:
- `Kraptor123/cs-kraptor` — **KAPANDI.** Depo sıfırlandı, README'de "desteği kesmiş bulunuyorum" ibaresi var; tüm `.cs3` dosyaları 404 veriyor. Bu kaynaktan gelen 29 eklenti listeden çıkarıldı; bazıları Feroxx deposundaki canlı sürümleriyle listede.
- `NivinCNC/CNCVerse-Cloud-Stream-Extension` — `CricifyProvider` (canlı spor) bu kaynaktan geliyordu; kullanıcı canlı spor istemediği için eklenti yok.
- `Kraptor123/Cs-Karma` — `Streamed` (canlı spor) bu kaynaktan geliyordu; kullanıcı istemedi. Kaynaktan yalnızca `Full4kizle` kaldı.
- `Kraptor123/Cs-GizliKeyif` — tamamı +18 NSFW içerikliydi (108 kayıt; NSFW olmayan kayıt yok), hiç eklenmedi.
- `sarapcanagii/*` — `NeonSpor` (canlı) bu kaynaktan gelmişti; kullanıcı istemedi.
- `ByAyzen/AyzenCS3` — `Syncler`, `Torrential` bu kaynaktan geliyordu; kişisel tercihle silindi.
> Not: Kaynakların tamamı `raw.githubusercontent.com` üzerinden `builds/plugins.json` ve/veya tekil `.cs3` dosya adresleriyle çekildi; hiçbir eklenti kopyalanıp yeniden barındırılmadı, adresler kaynak repoya işaret eder.


## Kaynak Seçim Kriteri ve Tablo Bakımı

**1. Kaynak seçimi — SADECE TARİH esastır, versiyon kriter değil:**
- Per-eklenti tarih `git -C <repo> log -1 --format=%cd --date=short --all -- <Eklenti>` ile alınır; repo genel `pushed_at` değil. Aynı eklentinin birden fazla kaynaktan gelen kopyaları arasında en güncel tarihli kayıt otomatik tercih edilir; versiyon numarasının düşük/yüksek olması kararı etkilemez.
- Örnek: `FilmMakinesi feroxx v58 (2026-08-23)` vs `blackhope01 v1 (2026-08-25)` — `blackhope01 v1` tarih olarak daha güncel olduğu için doğru şekilde tercih edildi; düşük versiyon yüksek versiyonu ezer ve bu beklenen davranıştır.

**1a. Eşit tarihli kaynaklar (tie-breaker) — VERSİYON NUMARASI HİÇBİR AŞAMADA KULLANILMAZ:**
İki veya daha fazla kaynağın aynı güncelleme tarihine sahip olduğu durumlarda sırasıyla şu kriterler uygulanır:
1. Site canlılığı elle kontrol edilir (site açılıyor mu?); açılmayan elenir.
2. Hâlâ eşitse kullanıcıya sorulur, otomatik karar verilmez.
Versiyon numarası bu tie-breaker'ın HİÇBİR adımında kriter olarak kullanılmaz — ne düşük ne yüksek versiyon tercih nedeni sayılır.

**2. Tablo bakımı — `Tüm Repolar` sadece `tr` + `Movie/TvSeries/Documentary` içerir:**
- `lang != tr` veya `tvTypes` içinde `Live/Anime/Cartoon/All/AsianDrama` olanlar otomatik `İstenmeyenler`'e gider; `Dil`/`Tur` kolonları bu yüzden kaldırıldı.
- **İstisna — paket (çoklu-kaynak) eklentileri:** `KraptorPlus`, `Sinewix`, `Dizipod` (ve kapalı `Full4kizle`) kaynak metadata'sında `Anime/AsianDrama/Cartoon` etiketi taşır ama **bunlar anime/kategori eklentisi değildir** — bunlar sadece **bizim istisnamız** (çoklu-kaynak/paket yapısı, kullanıcı onaylı) olarak listede tutulur. Kural **yalnızca yeni adaylara** uygulanır; bu kayıtlar zaten listede olduğu için `audit.py` filtresine takılmaz ve `İstenmeyenler`'e taşınmaz.
- `Site (domain)` her zaman `[domain](https://domain)` linkli olmalı (tıklanabilir).
- `kadircee/ozel-liste` kaynak değil derleme olduğu için `Tüm Repolar`'da yer almaz.
- `İstenmeyenler` metin + tablo aynı anda tutulmaz; tek tablo yeterlidir, `Silinen Eklentiler` metin listesi sadece not bırakır.
- **Yasaklı sayısı tek doğruluk kaynağıdır:** tablodaki `🟥` satır sayısı = başlıkta yazan sayı = `audit.py` çıktısındaki `yasakli sayisi` (2026-09-15: **69**). Üçü elle eşitlenir. Başlık (`## İstenmeyenler ...`) **kendi satırında** olmalıdır; tablo satırına yapıştırılırsa GitHub başlığı render etmez ve `audit.py` yasaklı listesini bulamaz → boş liste tespit edilip **`exit 2` ile durdurulur** (sessiz geçiş yok).

**3. Kayıt durumu — iki bağımsız eksen (Seçim + Sağlık):**
Tek `Durum` sütunu kaldırıldı; yerine `Seçim` (Aktif/Duplicate) + `Sağlık` (Çalışıyor/Çalışmıyor/`-`) sütunları geldi (bkz. **Kayıt Durumu Veri Modeli**). Tek sütun hem "yarışı kazandı mı" hem "çalışıyor mu" sorusunu taşıyamıyordu.
- İkon domaininin ölü görünmesi tek başına karar nedeni değildir (ör. `SinemaCX`: ikon `sinema.cx` ölü görünebilir ama eklenti veriyi başka domainden çekiyor olabilir) — karar tarihe + kullanıcı testine göre verilir.
- GitHub markdown `style` strip ettiği için renkler `span` değil emoji ile verilir; emoji artık **türetilmiştir**: `Seçim=Aktif`+`Sağlık=Çalışıyor` → 🟩, `Aktif`+`Çalışmıyor` → 🟨, `Seçim=Duplicate` → 🟧, `Seçim=İstenmeyen` → 🟥. `Eklenti` kolonuna da eklenir.
- `status:0` silme değil; tarihi izlenir; kaynak ilerlediyse kullanıcıya sorulur, "kapalı kalsın" derse Bizim Tarih yine eşitlenir, otomatik açılış yok.
- **`🟦 Eklenebilir` (geçici durum):** Yalnizca `plugins.json`'da **hic kaydi olmayan** adaylar icin kullanilir. Kaydi olan bir eklenti (or. `AltiYuzAltmisAltiFilmIzle`, `status:0`) modelde her zaman **Aktif + Çalışmıyor**'dur (emoji: 🟨); ona mavi denmez.





## Tarih Takip Kuralı (tek kural)

Tablodaki her satırda iki tarih vardır: **Kaynak Tarih** (kaynak deponun `builds` branch'inde o `.cs3` dosyasına dokunan son commit'in tarihi) ve **Bizim Tarih** (bizim o kaynağı en son benimsediğimiz tarih). Bütün olay bu iki tarihin karşılaştırmasıdır:

- **Kaynak Tarih > Bizim Tarih** → kaynak ilerlemiş demektir. `update.py` ile senkronize et, sonra satırdaki `Bizim Tarih`'i `Kaynak Tarih`'e eşitle. Versiyon numarasına bakılmaz.
- **Kaynak Tarih == Bizim Tarih** → yapacak iş yok.
- **Kapalı satırlar (`status:0`)**: `Kaynak Tarih` izlenmeye devam eder. Kaynak Tarih Bizim Tarih'i geçmişse kullanıcıya sorulur (kaynak düzelmiş olabilir). Kullanıcı "kapalı kalsın" derse `status` değişmez AMA `Bizim Tarih` yine de `Kaynak Tarih`'e eşitlenir — ki aynı soru her seferinde tekrar sorulmasın; kaynak bir kez daha ilerleyene kadar o satır susar. `status:1`'e dönüş her zaman manueldir.

**Sağlık durumu** tarihten + kullanıcı bildiriminden çıkar (çalışmıyor bildirimi kullanıcıdan gelir; `registry.py` yalnızca modeli ve tutarlılığı denetler):
- 🟩 Çalışıyor: `Kaynak Tarih == Bizim Tarih` ve kullanıcıdan "çalışmıyor" bildirimi yok.
- 🟨 Çalışıyor: kullanici "çalışmıyor" dedi.
- Renkler türetilmiştir: `Aktif`+`Çalışıyor` → 🟩, `Aktif`+`Çalışmıyor` → 🟨, `Duplicate` → 🟧, `İstenmeyen` → 🟥. `🟦 Eklenebilir` = geçici aday durumu (ayrı, bkz. model).

`verify.py` 2026-09-05'te kaldırıldı: ağ taraması yavaştı ve ürettiği uyarılar karara dönüşmüyordu. Doğruluk artık iki şeye dayanır: tarih takibi + kullanıcının cihazdaki gerçek testi.

## Kayıt Durumu Veri Modeli (Seçim + Sağlık)

Tek `Durum` sutunu kaldirildi. Her kayit iki bagimsiz eksene sahiptir:

- **Seçim:** `Aktif` (yarışı kazandı, `plugins.json`'da) / `Duplicate` (kaybetti, dosyada yok) / `İstenmeyen` (hiç yarışa girmedi).
- **Sağlık:** `Çalışıyor` / `Çalışmıyor` / `-` (yalnızca `Aktif` kayıtlarda tanımlı; digerlerinde **zorunlu `None`**).

| Seçim | Sağlık | Anlami | Renk | plugins.json |
|---|---|---|---|---|
| Aktif | Çalışıyor | Kazanan, sorunsuz kayit | 🟩 | var, `status:1` |
| Aktif | Çalışmıyor | Kazanan ama sitesi olu | 🟨 | var, `status:0` |
| Duplicate | `-` | Yarisi kaybetti, dosyada yok | 🟧 | yok |
| İstenmeyen | `-` | Hic degerlendirmeye alinmadi | 🟥 | yok |

`🟦 Eklenebilir` ayrı, GECICI bir durumdur: `plugins.json`'da hic kaydi olmayan adaylar icindir. Kaydi olan bir eklenti asla Eklenebilir olamaz.

**Kararlar (2026-09-15):** (A) Otomatik flip yok - tarih celiskileri `--check` raporunda karar bekler; flip, hash/boyut dogrulamasi gerektirdigi icin `update.py` ile ayrı adimda yapilir. (B) Ayni normalize isim = ayni grup (mutlak). (C) `Bizim Tarih`, Duplicate satirlarda referans amacli dondurulur, tazelenmez. (D) Tablo uretilen bloktur; degisiklik `--sync` → `--render --write` akisiyla yapilir.

**Araclar:** `python registry.py --sync` (tablolar + `plugins.json` → `registry.json`), `--check` (sema + kume + tarih; ihlalde exit 1), `--render [--write]` (tabloyu uretir). `Seçim` `plugins.json`'dan turetilir (dosyada olan = Aktif; `Sağlık` = `status`'tan); grup basina en fazla 1 Aktif; Aktif kumesi `plugins.json` ile birebir zorunlu.

## Kaynak Senkronizasyonu (update.py)
```bash
python update.py --check    # yazmadan sadece farkları raporlar (fark varsa exit 1)
python update.py            # farkları uygular, plugins.json'u günceller
```
Kaynak `builds/plugins.json` adresi, listedeki `.cs3` adresinden türetilir (`https://raw.githubusercontent.com/<owner>/<repo>/builds/<Isim>.cs3` → aynı klasördeki `plugins.json`). Senkronize edilen alanlar: `version, fileSize, fileHash, description, authors, language, tvTypes`. `iconUrl` bilinçli olarak senkronize **edilmez** — bu depo ikon adreslerini normalize eder (kaynaktaki `%size%` yer tutucuları sabit `sz=128`'e çevrilir) ve kaynak güncellemesi bu düzeltmeyi geri almasın.

> **Not:** Bu depo **otomatik hiçbir şey çalıştırmaz** — repoda `.github/workflows` **yoktur** (GitHub Actions hiç kurulmadı; ne `cron` ne manuel `workflow_dispatch` tetikleyicisi vardır). Kaynak senkronu (`update.py`) ve status değişiklikleri yalnızca **elle** yapılır. `[ATLANDI]` sayısı, kaynak depo bazında toplu kapanışın (ör. cs-kraptor kapanışı: 29 eklenti tek seferde 404) erken işaretidir.

## Karşılaşılan Hatalar ve Çözümleri
| Hata | Neden | Çözüm |
|------|-------|-------|
| Eklentilerin çoğu repo listesinde görünmüyordu | CloudStream önbelleği eski listeyi tutuyordu | Uygulamada "Verileri temizle" → depo yeniden eklendi |
| `.cs3` dosyaları "format hatası" gösterdi | Sorun dosyada değildi; istemci önbelleği eski listeyi gösteriyordu | Uygulamada "Verileri temizle" → depo yeniden eklendi, sorun çözüldü |
| `Filmmirasım` JSON'da eşleşmiyordu | Dosya adındaki noktasız `ı` (U+0131) karakteri shell'de bozuldu | Python'da `\u0131` escape'iyle yazılarak halledildi |
| PowerShell ile JSON düzenlemekte bozulma | `ConvertFrom/ConvertTo-Json` dizi yapısını bozuyordu | Tüm JSON işlemleri Python (`utf-8`, `ensure_ascii=False`) ile yapıldı |
| jsDelivr hâlâ eski listeyi gösteriyordu | CDN önbelleği | `purge.jsdelivr.net` üzerinden önbellek temizlendi |
| `FullRaces` simgesi yüklenmiyordu | `iconUrl` içinde `%size%` yer tutucusu kalmıştı | `sz=128` olarak düzeltildi |
| `Disney-Plus` kaynağı görünüyordu | MirrorVerse eklentisinin içindeki kaynak adı | Eklenti listeden kaldırıldı |
| 30 eklenti indirilemiyordu (hata yazıyordu) | `cs-kraptor` deposu kapanmıştı; 29 `.cs3` dosyası 404 veriyordu, 1 eklenti de (JPFilms) hash'i güncellenmediği için uyuşmuyordu | Kaynak kapandığı için 29 eklenti listeden çıkarıldı; JPFilms dahil yabancı eklentiler Türkçe filtresiyle kaldırıldı. Kalan 4 eklenti tek tek indirilip hash/boyut doğrulandı |
| `JPFilms` indirilemiyordu | Kaynakta v6 → v7 güncellenmiş, hash ve boyut değişmişti; listede eski hash duruyordu | Yeni hash/boyut kaynağından alındı; ancak daha sonra Türkçe filtreyle eklenti listeden çıkarıldığı için push edilmedi |
| `plt-stream` hash uyuşmazlığı | Kaynak v38 → v39 güncellenmiş; listede eski hash (411831 byte) vardı, gerçek dosya değişmişti (413103 byte) | Kaynağın `builds/plugins.json`'ından güncel `version/fileSize/fileHash/description` alındı, kayıt senkronlandı |
| `İnfluencerChicks` indirilemiyordu | Eklenti adındaki `İ` (U+0130) karakteri raw URL'de HTTP isteğini ascii encode hatasıyla patlatıyordu | URL'deki `İ` → `%C4%B0` percent-encode edildi (CloudStream de benzer sorun yaşamaması için) |
| Makoto2 eklentilerinde `fileHash` yoktu | Depo eski CloudStream formatı kullanıyor (hash alanı olmadan) | `fileHash` kontrolü atlanıp yalnızca indirilebilirlik doğrulandı; bu depodan eklenti alınmadı |
| `Kanal 7` eklentisi indirilemiyordu | URL'de boşluk karakteri vardı (`.../Kanal 7.cs3`), GitHub raw'da geçersiz | Depodan eklenti kullanılmadı |
| `cagatayrepo` ve `AyzenCS3` 404 | Bu depoların `plugins.json`'ı erişilemezdi | Katalogda listelenmesine rağmen kullanılmadı |
| GitHub API rate limit | `api.github.com` istek limiti doluyordu | Ham `raw.githubusercontent.com` fetch'leri ve websearch ile aşıldı |
| `plt-stream` yine bozulmuştu (v42 → v44) | Kaynak repo v44'e güncellenmiş; listede v42/eski hash/421535 byte duruyordu, gerçek dosya 428931 byte idi. CloudStream hash doğrulaması "Extension hash mismatch" fırlatıyordu | `update.py` ile kaynaktan senkronlandı (v44, yeni hash) |
| jsDelivr proxy `.cs3` 404/400 veriyordu (araştırma) | İlk istekte jsDelivr önbelleği soğuk olduğu için 404; `@branch` sözdizimi ve tarayıcı UA ile 200 dönüyor | Sorun değil; jsDelivr önbelleği ısınınca tüm `.cs3`'ler doğru hash'le iniyor (plt-stream hariç kaynak güncel olduğu için o da senkronlanınca düzeldi) |
| jsDelivr dönüşüm formatı karışıyordu | Doğru format `cdn.jsdelivr.net/gh/<owner>/<repo>@<branch>/<path>` — `@` **repo adından sonra** gelir (branch'ten önce); `repo@branch` yazılmadığında 404 alınıyordu | Format netleştirildi: `https://cdn.jsdelivr.net/gh/kadircee/ozel-liste@main/plugins.json`; purge de aynı biçimi kullanır |
| `git push` çıktısında kırmızı `NativeCommandError` görünüyordu | PowerShell, git'in stderr'e yazdığı ilerleme satırlarını hata sanıyor | Gerçek hata değil — çıktının sonunda `fb7f710..6aea63d main → main` görülüyorsa push başarılı demektir |
| YAML doğrulama `ModuleNotFoundError: No module named 'yaml'` | Python'da PyYAML kurulu değildi | `python -m pip install pyyaml` ile kuruldu; doğrulama `yaml.safe_load` ile geçti |
| YAML doğrulamada `KeyError: 'on'` | PyYAML YAML 1.1'de `on:` anahtarını bool `True`'ya çevirir (GitHub Actions YAML 1.2 kullanır ve `on`'u string kabul eder) | Gerçek hata değil; GitHub Actions bu dosyayı doğru ayrıştırır. **Not (2026-09-15):** bu kayıt geçmişe aittir — ilgili workflow dosyası bugün depoda **yoktur**, `.github/workflows` hiç commitlenmemiştir |
| plt-stream v47→v55 + DiziPalOriginal v84→v86 + DiziMom v56→v58 hash/boyut uyuşmazlığı (2026-09-05) | Kaynak repolar güncellenmiş; listedeki eski hash/boyut CloudStream’te hash mismatch veriyordu | update.py ile senkronlandı, jsDelivr purge 5/5 OK; Dizipod authors trim koruması geri yazıldı |
| 4 kapalı açıldı (DiziBox/DiziMom/DiziPal/FullHDFilmizlesene) + WebteIzle typo-kopyaya geçildi (2026-09-05) | Tarih Takip Kuralı: kaynaklar ilerledi, kullanıcı onayı ile açıldı/değiştirildi | 5 kayıt hash doğrulamalı senkronlandı (status 0→1 açılanlar dahil), jsDelivr purge 6/6 OK; UgurFilm yasaklıya eklendi |
| Full4kizle kaynağın plugins.json’ından düşmüş (.cs3 404) | Cs-Karma tarafında kayıt yok | Silme yok kuralı: kayıt status:0 ile korunuyor; kaynakta yeniden belirirse update.py yakalar |
| 18 eklenti senkronu (2026-09-15: aytzey 12 + feroxx 4 + blackhope 1 + plt 1) + DiziMom v4/Tablo v3 farki kapatildi | Kaynak repolar ilerlemis (aytzey 09-08 domain rewrite mass-bump, feroxx 09-15 rebuild, blackhope 09-07, plt 09-14); DiziFilmORG status:0 korunarak v23'e senkronlandi, Full4kizle kaynakta yok (ATLANDI, status:0 korunuyor) | update.py ile senkronlandi (Dizipod authors trim geri yazildi), jsDelivr purge 19/19 OK; DiziFilmORG kapali tutuldu, Bizim Tarih esitlendi |
| Webteizle-group audit FLIP vermedi (2026-09-05) | blackhope Webteizle (09-03) listedeki feroxx WebteIzle (09-02)’den yeniydi ama case-farki (Izle/izle) gruplari ayirdi + listedeki kaynak grupta olmayinca script sessiz gecti | Liste blackhope’a cevrildi (hash dogrulamali); audit.py’a ORPHAN raporu eklendi, sessiz gecis kapatildi |
| Kayıt Durumu modeli gecisi (2026-09-15): 3 satir otomatik `Duplicate`'a cekildi (FullHDFilm ilkel, SetFilmIzle ilkel/aytzey) | Bu kayitlarin `plugins.json`'da karsiligi yoktu ama `Çalışmıyor` isareti tasiyordu (secim+saglik tek hucrede karismisti) | `registry.py` `Seçim`'i `plugins.json`'dan turetiyor; 3 satir Duplicate/`-` oldu; `aktif == plugins.json (40)` zorunlu |
| Uretilen `Not` hucresindeki `|` (pipe) tabloyu boluyordu (2026-09-15) | Not metnine ayrac olarak ` \| ` yazilinca markdown hucre bolunuyor, `--sync` idempotent olmuyordu | Ayrac `;` oldu, yazimda pipe kacisi (`/`) eklendi; idempotency testiyle dogrulandi |
| `## İstenmeyenler` başlığı tablo satırının içine yapışmıştı (2026-09-15) | Başlık kendi satırına taşınmadan 87. satırın son hücresine yazılmıştı; GitHub başlığı render etmiyor, satır 7→8 hücreye kayıyordu, delete-zone bölümünün görünür başlığı yoktu | Başlık kendi satırına alındı; `audit.py` yasaklı listesi artık satır içi eşleşme tesadüfüne değil gerçek başlığa dayanıyor |
| `audit.py` içindeki `guard` listesi hiç yazdırılmıyordu (2026-09-15) | Satır 138'de başlatılıp 173'te dolduruluyordu ama rapora basılmıyordu → "yasaklı, kaynakta görüldü ama elendi" sinyali sessizdi (ORPHAN'da kapatılan sessiz geçişin aynısı) | `=== YASAKLI-ELEME ===` bloğu rapora eklendi ve `--check` exit koşuluna dahil edildi |
| `audit.py` Türkçe karakterli `.cs3` adında `'ascii' codec can't encode character '\u0131'` veriyordu (Filmmirasım) | GitHub API adresi percent-encode edilmiyordu; urllib ASCII dışı karakteri taşıyamıyor → eklenti denetim havuzundan **sessizce** düşüyor, tarihi hiç takip edilmiyordu | `percent_encode()` (update.py ile aynı mantık) `api_json`'a eklendi + `import urllib.parse` |
| Delete-zone sayısı üç yerde üç farklıydı: tablo başlığı `79 unique`, "Tablo bakımı" maddesi `71→74`, gerçek `69` (2026-09-15) | Sayı elle yazılıyordu ve `audit.py` çıktısıyla karşılaştırılmıyordu | İkisi de **69**'a çekildi; kural eklendi: başlıktaki sayı = kırmızı (🟥) satır sayısı = `audit.py` `yasakli sayisi` |

### Önemli Not
Repolar güncellendiğinde (yeni build yayınlandığında (GitHub uzerinden takip edilir)), Kaynak Tarih ilerlediğinde satır Tarih Takip Kuralı'na göre güncellenir; kapalı (status:0) satırda kaynak ilerlediyse kullanıcıya sorulur, otomatik açılış yapılmaz.

## Silinen Eklentiler (delete-zone)
Bu eklentiler listeye **eklenmez**; yeniden ekleme kararı yalnızca kullanıcı verir. Listede NSFW (+18) hiç yer almadı; canlı yayın/maç eklentileri istenmedi. Bozuk eklentiler silinmez, `status:0` yapılır (bkz. Kurulum). "Site açılmıyor" gerekçesiyle silinenler **geri dönüşlüdür**: site düzelirse tekrar denenebilir.

> **Not:** Ayrıntılı liste `İstenmeyenler (Delete-Zone)` tablosunda alfabetik olarak yer almaktadır.

## Güncelleme
Yeni bir değişiklik yapıldığında:
```bash
python update.py --check    # kaynak farkı var mı bak (exit 1 = var)
python registry.py --check  # model denetimi: sema + kume + tarih (exit 1 = ihlal ya da karar bekleyen)
python update.py                # gerekirse kaynak verilerini senkronize et
# DEPO-BILGILERI.md: Kaynak Tarih'i ilerleyen satırlarda Bizim Tarih'i eşitle (Tarih Takip Kuralı)
# status:0 status'una dokunma; kaynak ilerlediyse sor, "kapalı kalsın" derse Bizim Tarih'i yine eşitle
git add plugins.json DEPO-BILGILERI.md
git -c user.name="kadircee" -c user.email="kadircee@users.noreply.github.com" \
    commit -m "plugins.json: aciklama"
git push
```
Push sonrası jsDelivr önbelleği için:
```
https://purge.jsdelivr.net/gh/kadircee/ozel-liste@main/plugins.json
```
CloudStream tarafında depo yenilendiğinde yeni liste otomatik çekilir. Kaynak senkronu ve site sağlığı **otomatik değildir** (workflow dosyası yalnızca manuel tetikleme içindir, cron kapalı): kaynak bir eklentiyi güncellediğinde listedeki hash/boyut **elle** `update.py` çalıştırılarak senkronlanır, eklenti çalışmıyorsa kullanıcı bildirir, `status` elle `0` yapılır. `status:1`'e (yeniden açma) otomatik dönülmez; site geri geldiyse `plugins.json`'da ilgili eklentinin `status`'u elle `1` yapılır. Güncelleme öncesi `update.py --check` ile kontrol etmek iyi alışkanlıktır.

## Tüm Repolar - Alfabetik Liste

Bu bölüm 2026-08-28’de üretildi; 2026-09-05’te 45 satırın Kaynak/Bizim Tarih’i Tarih Takip Kuralı’na göre güncellendi; 2026-09-15’te 18 eklenti senkronize edildi (aytzey 09-08 domain-rewrite bump, feroxx 09-15 rebuild, blackhope 09-07 build, plt-stream 09-14), tum feroxx/aytzey/blackhope/plt satirlarinin Kaynak/Bizim Tarih’i esitlendi — tüm kaynak repolardaki 87 eklenti (İstenmeyenler ve ozel-liste hariç) alfabetik, site domain ve durum bilgisiyle.

Aynı isim/kökten farkli kaynaklarda gelen kayitlar `Seçim`/`Sağlık` sütunlarında izlenir: her gruptan 1 tanesi `plugins.json`'da yer alır (`Aktif`); digerleri `Duplicate`tir, `Sağlık` `-` olur. Renkler: 🟩 Çalışan, 🟨 Çalışmayan, 🟧 Duplicate, 🟥 İstenmeyen, 🟦 Eklenebilir (geçici aday).
Toplam kayit: 87. Tablo `registry.json`'dan uretilir (`<!-- KAYIT-DURUMU:OTOMATIK-BASLANGIC -->` arasi; elle duzenleme) - degisiklik `--sync` → `--render --write` ile yapilir.

<!-- KAYIT-DURUMU:OTOMATIK-BASLANGIC -->
| # | Eklenti | Kaynak | Site (domain) | v | Kaynak Tarih | Bizim Tarih | Seçim | Sağlık | Not |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 🟨 AltiYuzAltmisAltiFilmIzle | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [666filmizle.site](https://666filmizle.site) | 1 | 2026-06-11 | 2026-08-28 | Aktif | Çalışmıyor | (son ölü: 2026-08-22, bu build veya başka build güncellendiğinde kontrol) |
| 2 | 🟩 Ddizi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [www.ddizi.im](https://www.ddizi.im) | 22 | 2026-09-15 | 2026-09-15 | Aktif | Çalışıyor |  |
| 3 | 🟧 Ddizi | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [www.ddizi.im](https://www.ddizi.im) | 22 | 2026-06-11 | 2026-08-28 | Duplicate | - | (feroxx 2026-09-02 tercih edildi) |
| 4 | 🟧 Ddizi | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.ddizi.im](https://www.ddizi.im) | 19 | 2026-09-08 | 2026-09-15 | Duplicate | - | (feroxx 2026-09-15 tercih edildi) |
| 5 | 🟩 DiziBox | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [www.dizibox.live](https://www.dizibox.live) | 23 | 2026-09-15 | 2026-09-15 | Aktif | Çalışıyor |  |
| 6 | 🟧 DiziBox | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [www.dizibox.live](https://www.dizibox.live) | 23 | 2026-06-11 | 2026-08-28 | Duplicate | - | (feroxx 2026-09-02 tercih edildi) |
| 7 | 🟧 DiziBox | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.dizibox.de](https://www.dizibox.de) | 37 | 2026-09-08 | 2026-09-15 | Duplicate | - | (feroxx 2026-09-15 tercih edildi) |
| 8 | 🟨 DiziFilmORG | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [dizifilm.org](https://dizifilm.org) | 23 | 2026-09-08 | 2026-09-15 | Aktif | Çalışmıyor | (son ölü: 2026-08-22, bu build veya başka build güncellendiğinde kontrol) |
| 9 | 🟩 Dizigecesi | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [dizigecesi.com](https://dizigecesi.com) | 5 | 2026-09-08 | 2026-09-15 | Aktif | Çalışıyor |  |
| 10 | 🟩 DiziLife | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [dizi73.life](https://dizi73.life) | 2 | 2026-09-07 | 2026-09-15 | Aktif | Çalışıyor |  |
| 11 | 🟧 DiziLife | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [dizi18.life](https://dizi18.life) | 58 | 2026-09-08 | 2026-09-15 | Duplicate | - | (blackhope01 2026-09-07 tercih edildi) |
| 12 | 🟩 Dizilla | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizilla.club](https://dizilla.club) | 92 | 2026-09-15 | 2026-09-15 | Aktif | Çalışıyor |  |
| 13 | 🟧 Dizilla | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [dizilla.club](https://dizilla.club) | 92 | 2026-06-11 | 2026-08-28 | Duplicate | - | (feroxx 2026-09-02 tercih edildi) |
| 14 | 🟧 Dizilla | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [dizilla.to](https://dizilla.to) | 111 | 2026-09-08 | 2026-09-15 | Duplicate | - | (feroxx 2026-09-15 tercih edildi) |
| 15 | 🟧 DiziMom | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [www.dizimom.plus](https://www.dizimom.plus) | 58 | 2026-09-15 | 2026-09-15 | Duplicate | - | (blackhope01 2026-09-07 tercih edildi) |
| 16 | 🟧 DiziMom | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [www.dizimom.plus](https://www.dizimom.plus) | 43 | 2026-08-28 | 2026-08-28 | Duplicate | - | (blackhope01 2026-09-03 tercih edildi) |
| 17 | 🟩 DiziMom | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [www.dizimom.surf](https://www.dizimom.surf) | 4 | 2026-09-07 | 2026-09-15 | Aktif | Çalışıyor |  |
| 18 | 🟧 DiziMom | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.dizimom.mom](https://www.dizimom.mom) | 61 | 2026-09-08 | 2026-09-15 | Duplicate | - | (blackhope01 2026-09-07 tercih edildi) |
| 19 | 🟩 DiziPal | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizipal1563.com](https://dizipal1563.com) | 107 | 2026-09-15 | 2026-09-15 | Aktif | Çalışıyor |  |
| 20 | 🟧 DiziPal | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [dizipal952.com](https://dizipal952.com) | 90 | 2026-08-28 | 2026-08-28 | Duplicate | - | (feroxx 2026-09-02 tercih edildi) |
| 21 | 🟧 DiziPal | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [dizipal.im](https://dizipal.im) | 89 | 2026-09-08 | 2026-09-15 | Duplicate | - | (feroxx 2026-09-15 tercih edildi) |
| 22 | 🟩 DiziPalOriginal | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [chessplyimages.cfd](https://chessplyimages.cfd) | 91 | 2026-09-15 | 2026-09-15 | Aktif | Çalışıyor |  |
| 23 | 🟧 DiziPalOriginal | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [dizipal2036.com](https://dizipal2036.com) | 66 | 2026-08-28 | 2026-08-28 | Duplicate | - | (feroxx 2026-09-02 tercih edildi) |
| 24 | 🟩 DiziPalOrijinal | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [dizipal932.com](https://dizipal932.com) | 46 | 2026-09-08 | 2026-09-15 | Aktif | Çalışıyor |  |
| 25 | 🟩 Dizipod | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [dizipod.com](https://dizipod.com) | 13 | 2026-09-08 | 2026-09-15 | Aktif | Çalışıyor |  |
| 26 | 🟩 DiziYo | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [www.diziyo.so](https://www.diziyo.so) | 1 | 2026-09-07 | 2026-09-15 | Aktif | Çalışıyor | (geçici — tekrar değerlendirilecek, son ölü: 2026-08-22) |
| 27 | 🟧 DiziYo | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [diziyo.so](https://diziyo.so) | 74 | 2026-09-08 | 2026-09-15 | Duplicate | - | (blackhope01 2026-09-07 tercih edildi) |
| 28 | 🟩 DiziYou | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [cdn.diziyou.one](https://cdn.diziyou.one) | 26 | 2026-09-15 | 2026-09-15 | Aktif | Çalışıyor |  |
| 29 | 🟧 DiziYou | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [cdn.diziyou6.com](https://cdn.diziyou6.com) | 25 | 2026-06-11 | 2026-08-22 | Duplicate | - | (feroxx 2026-09-02 tercih edildi) |
| 30 | 🟧 DiziYou | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.diziyou.co](https://www.diziyou.co) | 49 | 2026-09-08 | 2026-09-15 | Duplicate | - | (feroxx 2026-09-15 tercih edildi) |
| 31 | 🟨 FilmBip | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [filmbip.com](https://filmbip.com) | 19 | 2026-06-11 | 2026-08-28 | Aktif | Çalışmıyor | (son ölü: 2026-08-22, bu build veya başka build güncellendiğinde kontrol) |
| 32 | 🟩 FilmEkseni | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [www.filmekseni.vip](https://www.filmekseni.vip) | 1 | 2026-09-07 | 2026-09-15 | Aktif | Çalışıyor |  |
| 33 | 🟧 FilmEkseni | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [filmekseni.net](https://filmekseni.net) | 50 | 2026-09-08 | 2026-09-15 | Duplicate | - | (blackhope01 2026-09-07 tercih edildi) |
| 34 | 🟩 FilmHane | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [www.filmhane.shop](https://www.filmhane.shop) | 1 | 2026-09-07 | 2026-09-15 | Aktif | Çalışıyor |  |
| 35 | 🟧 FilmHane | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [filmhane.shop](https://filmhane.shop) | 43 | 2026-09-08 | 2026-09-15 | Duplicate | - | (blackhope01 2026-09-07 tercih edildi) |
| 36 | 🟧 FilmMakinesi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [filmmakinesi.film](https://filmmakinesi.film) | 58 | 2026-09-15 | 2026-09-15 | Duplicate | - | (blackhope01 2026-09-07 tercih edildi) |
| 37 | 🟧 FilmMakinesi | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [filmmakinesi.film](https://filmmakinesi.film) | 57 | 2026-06-11 | 2026-08-28 | Duplicate | - | (blackhope01 2026-09-03 tercih edildi) |
| 38 | 🟧 FilmMakinesi | [MRTDEVM/cloudstream-turkce](https://github.com/MRTDEVM/cloudstream-turkce) | [filmmakinesi.to](https://filmmakinesi.to) | 8 | 2026-08-21 | 2026-08-28 | Duplicate | - | (blackhope01 2026-09-03 tercih edildi) |
| 39 | 🟩 FilmMakinesi | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [www.filmmakinesi.to](https://www.filmmakinesi.to) | 2 | 2026-09-07 | 2026-09-15 | Aktif | Çalışıyor |  |
| 40 | 🟧 FilmMakinesi | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [filmmakinesi.tv](https://filmmakinesi.tv) | 70 | 2026-09-08 | 2026-09-15 | Duplicate | - | (blackhope01 2026-09-07 tercih edildi) |
| 41 | 🟩 FilmModu | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [www.filmmodu.one](https://www.filmmodu.one) | 19 | 2026-09-15 | 2026-09-15 | Aktif | Çalışıyor |  |
| 42 | 🟧 FilmModu | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [www.filmmodu17.com](https://www.filmmodu17.com) | 19 | 2026-06-11 | 2026-08-22 | Duplicate | - | (feroxx 2026-09-02 tercih edildi) |
| 43 | 🟧 FilmModu | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.filmmodu.one](https://www.filmmodu.one) | 41 | 2026-09-08 | 2026-09-15 | Duplicate | - | (feroxx 2026-09-15 tercih edildi) |
| 44 | 🟨 Full4kizle | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [plusizle.net](https://plusizle.net) | 20 | 2026-08-27 | 2026-08-22 | Aktif | Çalışmıyor | (son ölü: 2026-08-22, bu build veya başka build güncellendiğinde kontrol) |
| 45 | 🟨 FullHDFilm | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [hdfilm.us](https://hdfilm.us) | 36 | 2026-09-15 | 2026-09-15 | Aktif | Çalışmıyor | (geçici — tekrar değerlendirilecek, son ölü: 2026-08-22) |
| 46 | 🟧 FullHDFilm | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [fullhdfilm.us](https://fullhdfilm.us) | 36 | 2026-06-11 | - | Duplicate | - | (son ölü: 2026-08-22, bu build veya başka build güncellendiğinde kontrol) |
| 47 | 🟩 FullHDFilmizlesene | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [www.fullhdfilmizlesene.de](https://www.fullhdfilmizlesene.de) | 33 | 2026-09-15 | 2026-09-15 | Aktif | Çalışıyor |  |
| 48 | 🟧 FullHDFilmizlesene | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [www.fullhdfilmizlesene.de](https://www.fullhdfilmizlesene.de) | 29 | 2026-08-28 | 2026-08-28 | Duplicate | - | (feroxx 2026-09-02 tercih edildi) |
| 49 | 🟧 FullHDFilmizlesene | [MRTDEVM/cloudstream-turkce](https://github.com/MRTDEVM/cloudstream-turkce) | [www.fullhdfilmizlesene.now](https://www.fullhdfilmizlesene.now) | 8 | 2026-08-21 | 2026-08-28 | Duplicate | - | (feroxx 2026-09-02 tercih edildi) |
| 50 | 🟧 FullHDFilmizlesene | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.fullhdfilmizlesene.de](https://www.fullhdfilmizlesene.de) | 72 | 2026-09-08 | 2026-09-15 | Duplicate | - | (feroxx 2026-09-15 tercih edildi) |
| 51 | 🟩 HDFilmCehennemi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [hdfilmcehennemi.com](https://hdfilmcehennemi.com) | 48 | 2026-09-15 | 2026-09-15 | Aktif | Çalışıyor |  |
| 52 | 🟧 HDFilmCehennemi | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [hdfilmcehennemi.com](https://hdfilmcehennemi.com) | 47 | 2026-06-11 | 2026-08-28 | Duplicate | - | (feroxx 2026-09-02 tercih edildi) |
| 53 | 🟧 HDFilmCehennemi | [MRTDEVM/cloudstream-turkce](https://github.com/MRTDEVM/cloudstream-turkce) | [www.hdfilmcehennemi.nl](https://www.hdfilmcehennemi.nl) | 8 | 2026-08-21 | 2026-08-28 | Duplicate | - | (feroxx 2026-09-02 tercih edildi) |
| 54 | 🟧 HDFilmCehennemi | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [hdfilmcehennemi.nl](https://hdfilmcehennemi.nl) | 97 | 2026-09-08 | 2026-09-15 | Duplicate | - | (feroxx 2026-09-15 tercih edildi) |
| 55 | 🟩 HDFilmDelisi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [hdfilmdelisi.com](https://hdfilmdelisi.com) | 1 | 2026-09-15 | 2026-09-15 | Aktif | Çalışıyor |  |
| 56 | 🟧 HDFilmDelisi | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [hdfilmdelisi.one](https://hdfilmdelisi.one) | 18 | 2026-09-08 | 2026-09-15 | Duplicate | - | (feroxx 2026-09-15 tercih edildi) |
| 57 | 🟩 HDFilmizle | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.hdfilmizle.life](https://www.hdfilmizle.life) | 26 | 2026-09-08 | 2026-09-15 | Aktif | Çalışıyor |  |
| 58 | 🟧 JetFilmizle | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [jetfilmizle.de](https://jetfilmizle.de) | 47 | 2026-09-15 | 2026-09-15 | Duplicate | - | (blackhope01 2026-09-07 tercih edildi) |
| 59 | 🟧 JetFilmizle | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [jetfilmizle.de](https://jetfilmizle.de) | 47 | 2026-06-11 | 2026-08-28 | Duplicate | - | (blackhope01 2026-09-03 tercih edildi) |
| 60 | 🟩 JetFilmizle | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [jetfilmizle.now](https://jetfilmizle.now) | 1 | 2026-09-07 | 2026-09-15 | Aktif | Çalışıyor |  |
| 61 | 🟧 JetFilmizle | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [jetfilmizle.de](https://jetfilmizle.de) | 62 | 2026-09-08 | 2026-09-15 | Duplicate | - | (blackhope01 2026-09-07 tercih edildi) |
| 62 | 🟩 KraptorPlus | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [github.com/aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | 87 | 2026-09-08 | 2026-09-15 | Aktif | Çalışıyor |  |
| 63 | 🟩 LoveFilm | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [lovefilmizle.net](https://lovefilmizle.net) | 1 | 2026-09-07 | 2026-09-15 | Aktif | Çalışıyor |  |
| 64 | 🟩 plt-stream | [pltmustafa/plt-stream](https://github.com/pltmustafa/plt-stream) | [github.com/pltmustafa/plt-stream](https://github.com/pltmustafa/plt-stream) | 57 | 2026-09-14 | 2026-09-15 | Aktif | Çalışıyor |  |
| 65 | 🟩 SelcukFlix | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [selcukflix.com](https://selcukflix.com) | 50 | 2026-09-08 | 2026-09-15 | Aktif | Çalışıyor |  |
| 66 | 🟨 SetFilmIzle | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [www.setfilmizle.uk](https://www.setfilmizle.uk) | 30 | 2026-09-15 | 2026-09-15 | Aktif | Çalışmıyor | (son ölü: 2026-08-22, bu build veya başka build güncellendiğinde kontrol) |
| 67 | 🟧 SetFilmIzle | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [www.setfilmizle.nl](https://www.setfilmizle.nl) | 28 | 2026-06-11 | 2026-08-28 | Duplicate | - | (son ölü: 2026-08-22, bu build veya başka build güncellendiğinde kontrol) |
| 68 | 🟧 SetFilmIzle | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.setfilmizle.uk](https://www.setfilmizle.uk) | 42 | 2026-09-08 | 2026-09-15 | Duplicate | - | (son ölü: 2026-08-22, bu build veya başka build güncellendiğinde kontrol) |
| 69 | 🟧 SezonlukDizi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [sezonlukdizi6.com](https://sezonlukdizi6.com) | 9 | 2026-09-15 | 2026-09-15 | Duplicate | - | (blackhope01 2026-09-07 tercih edildi) |
| 70 | 🟧 SezonlukDizi | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [sezonlukdizi6.com](https://sezonlukdizi6.com) | 8 | 2026-08-28 | 2026-08-28 | Duplicate | - | (blackhope01 2026-09-03 tercih edildi) |
| 71 | 🟩 SezonlukDizi | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [sezonlukdizi.cc](https://sezonlukdizi.cc) | 1 | 2026-09-07 | 2026-09-15 | Aktif | Çalışıyor |  |
| 72 | 🟧 SezonlukDizi | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [sezonlukdizi6.com](https://sezonlukdizi6.com) | 40 | 2026-09-08 | 2026-09-15 | Duplicate | - | (blackhope01 2026-09-07 tercih edildi) |
| 73 | 🟩 SinemaCX | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [www.sinema.cx](https://www.sinema.cx) | 24 | 2026-09-15 | 2026-09-15 | Aktif | Çalışıyor |  |
| 74 | 🟧 SinemaCX | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [www.sinema.cx](https://www.sinema.cx) | 24 | 2026-06-11 | 2026-08-28 | Duplicate | - | (feroxx 2026-09-02 tercih edildi) |
| 75 | 🟧 SinemaCX | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.sinema.gg](https://www.sinema.gg) | 35 | 2026-09-08 | 2026-09-15 | Duplicate | - | (feroxx 2026-09-15 tercih edildi) |
| 76 | 🟩 Sinewix | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [sinewix.com](https://sinewix.com) | 2 | 2026-09-15 | 2026-09-15 | Aktif | Çalışıyor |  |
| 77 | 🟧 Sinewix | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [sinewix.com](https://sinewix.com) | 2 | 2026-06-11 | 2026-08-28 | Duplicate | - | (feroxx 2026-09-02 tercih edildi) |
| 78 | 🟧 Sinewix | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [sinewix.com](https://sinewix.com) | 33 | 2026-09-08 | 2026-09-15 | Duplicate | - | (feroxx 2026-09-15 tercih edildi) |
| 79 | 🟩 Sinezy | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [sinezy.fit](https://sinezy.fit) | 41 | 2026-09-08 | 2026-09-15 | Aktif | Çalışıyor |  |
| 80 | 🟩 Turkdizileri | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [turkdizileri.cc](https://turkdizileri.cc) | 34 | 2026-09-08 | 2026-09-15 | Aktif | Çalışıyor |  |
| 81 | 🟩 TvDiziler | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [tvdiziler.cc](https://tvdiziler.cc) | 19 | 2026-09-08 | 2026-09-15 | Aktif | Çalışıyor |  |
| 82 | 🟧 Webteizle | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [webteizle3.xyz](https://webteizle3.xyz) | 20 | 2026-09-15 | 2026-09-15 | Duplicate | - | (blackhope 2026-09-07 tercih edildi) |
| 83 | 🟧 Webteizle | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [webteizle2.com](https://webteizle2.com) | 17 | 2026-06-11 | 2026-08-28 | Duplicate | - | (blackhope 2026-09-03 tercih edildi) |
| 84 | 🟩 Webteizle | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [webteizle3.xyz](https://webteizle3.xyz) | 1 | 2026-09-07 | 2026-09-15 | Aktif | Çalışıyor |  |
| 85 | 🟧 Webteizle | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [webteizle1.xyz](https://webteizle1.xyz) | 53 | 2026-09-08 | 2026-09-15 | Duplicate | - | (blackhope 2026-09-07 tercih edildi) |
| 86 | 🟩 WFilmizle | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [wfilmizle.bar](https://wfilmizle.bar) | 24 | 2026-09-08 | 2026-09-15 | Aktif | Çalışıyor |  |
| 87 | 🟩 YabanciDizi | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [yabancidizi.so](https://yabancidizi.so) | 19 | 2026-09-08 | 2026-09-15 | Aktif | Çalışıyor |  |
<!-- KAYIT-DURUMU:OTOMATIK-SON -->

## Istenmeyenler (Delete-Zone) - 69 unique

| Eklenti | Kaynak Ornek | Site | Dil | Tur |
|---------|--------------|------|-----|-----|
| 🟥 AnimeAV | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [animeav1.com](https://animeav1.com) | mx | Anime |
| 🟥 AnimeciX | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [animecix.tv](https://animecix.tv) | tr | Anime |
| 🟥 Animeler | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [animeler.pw](https://animeler.pw) | tr | Anime |
| 🟥 Animely | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [play-lh.googleusercontent.com](https://play-lh.googleusercontent.com) | tr | Anime,AnimeMovie,OVA |
| 🟥 AnimeWorld | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [www.animeworld.ac](https://www.animeworld.ac) | it | Anime |
| 🟥 AnimeYTX | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [animeyt.cc](https://animeyt.cc) | mx | Anime |
| 🟥 AnimPow | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [animpow.com](https://animpow.com) | tr | Anime |
| 🟥 Anizium | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [anizium.co](https://anizium.co) | tr | AnimeMovie,Anime |
| 🟥 AsyaAnimeleri | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [asyaanimeleri.top](https://asyaanimeleri.top) | tr | Anime |
| 🟥 AsyaFanatiklerim | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [asyafanatiklerim.com](https://asyafanatiklerim.com) | tr | AsianDrama |
| 🟥 AsyaMinik | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [asyaminik.com](https://asyaminik.com) | tr | AsianDrama |
| 🟥 AsyaWatch | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [asyawatch.com](https://asyawatch.com) | tr | AsianDrama |
| 🟥 BelgeselX | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [belgeselx.com](https://belgeselx.com) | tr | Documentary |
| 🟥 CizgiMax | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [cizgimax.online](https://cizgimax.online) | tr | Cartoon,Anime,Movie |
| 🟥 CizgiveDizi | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [cizgivedizi.com](https://cizgivedizi.com) | tr | Cartoon |
| 🟥 DiziAsia | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [diziasia.com](https://diziasia.com) | tr | AsianDrama |
| 🟥 DiziAsya | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.diziasya.com](https://www.diziasya.com) | tr | AsianDrama |
| 🟥 DiziKorea | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizikorea.vip](https://dizikorea.vip) | tr | AsianDrama |
| 🟥 DocumentaryArea | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [documentaryarea.com](https://documentaryarea.com) | en | Documentary |
| 🟥 DoramasLatinoX | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [doramaslatinox.com](https://doramaslatinox.com) | mx | AsianDrama |
| 🟥 DramaDizilerim | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [dramadizilerim.com](https://dramadizilerim.com) | tr | TvSeries |
| 🟥 Dramaizle | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [dramaizle.net](https://dramaizle.net) | tr | AsianDrama |
| 🟥 Dubbindo | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [www.dubbindo.site](https://www.dubbindo.site) | id | AsianDrama |
| 🟥 EnglishW | [ctnkyaumt/cstest](https://github.com/ctnkyaumt/cstest) | [themoviedb.org](https://themoviedb.org) | en | Movie,TvSeries |
| 🟥 Esheaq | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [esk.onl](https://esk.onl) | ar | Movie,TvSeries |
| 🟥 Filmmirasım | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [filmmirasim.ktb.gov.tr](https://filmmirasim.ktb.gov.tr) | tr | Documentary |
| 🟥 Filmzal | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [filmzal.me](https://filmzal.me) | az | Movie |
| 🟥 Flixlatam | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [flixlatam.com](https://flixlatam.com) | mx | Movie |
| 🟥 FootReplays | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [www.footreplays.com](https://www.footreplays.com) | en | Others |
| 🟥 FullRaces | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [fullraces.com](https://fullraces.com) | en | Movie |
| 🟥 GinikoCanli | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.giniko.com](https://www.giniko.com) | tr | Live |
| 🟥 Gnulahd | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [ww3.gnulahd.nu](https://ww3.gnulahd.nu) | mx | Movie,Anime,TvSeries |
| 🟥 Henaojara | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [ww1.henaojara.net](https://ww1.henaojara.net) | mx | Anime,AnimeMovie |
| 🟥 InatBox | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [blogger.googleusercontent.com](https://blogger.googleusercontent.com) | tr | Movie,TvSeries,Live |
| 🟥 Iwatchtheoffice | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [iwatchtheoffice.cc](https://iwatchtheoffice.cc) | en | Movie |
| 🟥 JPFilms | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [jp-films.com](https://jp-films.com) | en | AsianDrama |
| 🟥 KickTR | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [kick.com](https://kick.com) | tr | Live |
| 🟥 KissKH | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [kisskh.id](https://kisskh.id) | en | AsianDrama |
| 🟥 Krmzy | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [krmzy.org](https://krmzy.org) | ar | TvSeries |
| 🟥 KultFilmler | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [kultfilmler.net](https://kultfilmler.net) | tr | Movie,TvSeries |
| 🟥 Latanime | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [latanime.org](https://latanime.org) | mx | Movie |
| 🟥 LayarKaca | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [tv12.lk21official.cc](https://tv12.lk21official.cc) | id | Movie,TvSeries |
| 🟥 MirrorVerse | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [raw.githubusercontent.com](https://raw.githubusercontent.com) | tr | Movie,TvSeries |
| 🟥 Movix | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [movix.fun](https://movix.fun) | fr | Movie,TvSeries,Anime |
| 🟥 OK | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [ok.ru](https://ok.ru) | ru | Movie,TvSeries |
| 🟥 OnePaceTr | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.onepacetr.net](https://www.onepacetr.net) | tr | Anime |
| 🟥 OpenAnime | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [openani.me](https://openani.me) | tr | Anime,AnimeMovie |
| 🟥 RareFilmm | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [rarefilmm.com](https://rarefilmm.com) | en | Movie |
| 🟥 RecTV | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [rectv.org.tr](https://rectv.org.tr) | tr | Movie,Live,TvSeries |
| 🟥 SeiCode | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [seicode.net](https://seicode.net) | tr | Anime |
| 🟥 Sokuja | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [x6.sokuja.uk](https://x6.sokuja.uk) | id | Anime,AnimeMovie |
| 🟥 Streamed | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [streamed.pk](https://streamed.pk) | en | Live |
| 🟥 Subsplease | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [subsplease.org](https://subsplease.org) | en | Anime |
| 🟥 Supercartoons | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [i.imgur.com](https://i.imgur.com) | en | Cartoon |
| 🟥 TLCtr | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [tlctv.com.tr](https://tlctv.com.tr) | tr | Movie |
| 🟥 TRasyalog | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [asyalog.co](https://asyalog.co) | tr | TvSeries |
| 🟥 TmdbProvider | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [www.diziyo.so](https://www.diziyo.so) | tr | Movie,TvSeries |
| 🟥 TrAnimeIzle | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.tranimeizle.io](https://www.tranimeizle.io) | tr | Anime |
| 🟥 TurkAnime | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [www.turkanime.co](https://www.turkanime.co) | tr | Anime |
| 🟥 TurkishW | [ctnkyaumt/cstest](https://github.com/ctnkyaumt/cstest) | [themoviedb.org](https://themoviedb.org) | tr | Movie,TvSeries,Anime,Live |
| 🟥 UgurFilm | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [ugurfilm7.com](https://ugurfilm7.com) | tr | Movie |
| 🟥 Wcoflix | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [www.wcoflix.tv](https://www.wcoflix.tv) | en | Anime,Cartoon |
| 🟥 WebDramaTurkey | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [webdramaturkey.org](https://webdramaturkey.org) | tr | AsianDrama |
| 🟥 Yablom | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [yablom.com](https://yablom.com) | fr | Movie |
| 🟥 YeniKaynak | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.yenikaynak.com](https://www.yenikaynak.com) | tr | Movie,TvSeries |
| 🟥 YesilCamTv | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [yesilcamtv.com.tr](https://yesilcamtv.com.tr) | tr | Movie |
| 🟥 YoTurkish | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [yoturkish.to](https://yoturkish.to) | en | TvSeries |
| 🟥 Youtube | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [www.youtube.com](https://www.youtube.com) | tr | Movie,Live,Music,TvSeries |
| 🟥 YTS | [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | [en.yts-official.mx](https://en.yts-official.mx) | tr | Torrent |
## Yasal Uyarı ve Sorumluluk Reddi (Disclaimer)
Bu depo kişisel arşivleme amacıyla oluşturulmuştur; hiçbir ticari amacı yoktur. Bu depo (ve GitHub sunucuları) hiçbir video, ses dosyası, medya veya telif hakkıyla korunan materyal barındırmaz, kopyalamaz veya dağıtmaz. Bu depo yalnızca internette herkese açık olarak paylaşılan üçüncü taraf eklentilerin (`.cs3`) doğrudan GitHub RAW adreslerini derleyen metin tabanlı bir JSON dizinidir ("Yalnızca Endeks"). Listelenen eklentilerin kodları, işleyişleri veya hangi web sitelerinden veri çektikleri üzerinde bu deponun hiçbir kontrolü, sahipliği veya sorumluluğu yoktur; tüm sorumluluk eklentilerin orijinal geliştiricilerine ve veriyi barındıran kaynak web sitelerine aittir. Bu depo yalnızca bağlantıları listeleyen bir köprü görevi gördüğü için telif hakkı ihlali iddialarının muhatabı değildir; içerik kaldırma talepleri (DMCA) doğrudan içerikleri sunan kaynak web sitelerine veya eklentilerin orijinal GitHub depolarına yapılmalıdır. Bu depo, 5846 sayılı Fikir ve Sanat Eserleri Kanunu ve 5651 sayılı Kanun kapsamında da eser barındırmaz, çoğaltmaz veya iletmez; yalnızca kamuya açık kaynaklardaki `.cs3` dosyalarına bağlantı sağlar. 5651 sayılı Kanunun 4. maddesinin ikinci fıkrası gereği içerik sağlayıcı, bağlantı sağladığı başkasına ait içerikten sorumlu değildir; ancak aynı maddenin istisnası saklıdır: sunuş biçiminden bağlantı verilen içeriğin benimsendiği ve kullanıcının o içeriğe ulaşmasının amaçlandığı açıkça belli ise sorumluluk doğabilir. Bu depo, listedeki hiçbir eklentiyi veya eklentilerin veri çektiği kaynakları benimsemez ve tavsiye etmez; liste salt teknik bir indekstir. Hak sahipleri 5651 sayılı Kanunun 9. maddesi uyarınca uyarı yöntemiyle bildirimde bulunursa ilgili bağlantı derhal kaldırılır.

This repository is created for personal archiving purposes and has no commercial intent. This repository does not host, store, copy, or distribute any video, audio, media files, or copyrighted material; it serves merely as a text-based JSON index containing direct links to third-party `.cs3` plugins already publicly available on the internet ("Index Only"). The owner of this repository does not develop, host, or control any of the listed plugins, their source code, operation, or the websites these plugins scrape; all liability lies strictly with the original plugin developers and the respective websites hosting the media. As this repository only provides a compilation of text-based URLs, it is not liable for copyright infringement; any DMCA takedown requests must be directed to the actual websites hosting the copyrighted content or to the original developers' repositories. Under Turkish law (FSEK No. 5846 and Law No. 5651), this repository does not host, reproduce, or communicate any work; it merely provides links to `.cs3` files publicly available on the internet. Under Article 4/2 of Law No. 5651, a content provider is not liable for third-party content to which it merely provides a link; however, the exception in that provision is reserved: liability may arise where the presentation clearly shows that the linked content is adopted and that users are intended to reach it. This repository does not adopt or recommend any of the listed plugins or the sources they use; the list is a purely technical index. If rights holders send a notice under Article 9 of Law No. 5651, the relevant link will be removed promptly
