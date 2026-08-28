# developer (ozel-liste)
Bu depo test CloudStream deposudur; yalnızca Türkçe film/dizi eklentilerini ve test seçtiği kaynakları barındırır. Canlı yayın, NSFW ve yabancı dil içerikli eklentiler kullanıcı tercihi gereği listeye alınmamıştır.

## Durum
- **Son doğrulama:** 2026-08-28 · **37 eklenti** (32 açık + 5 kapalı (Full4kizle, DiziFilmORG, DiziPal, DiziYo, SetFilmIzle); indirilebilir, hash/boyut doğrulanmış)
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
├── plugins.json         → eklenti listesi (37 eklenti)
├── verify.py            → yapısal + ağ kontrollü doğrulama script'i (--deep ile .cs3 içinden gerçek çekim domaini kontrolü; --health ile ölmüş eklentilere otomatik status:0; sadece standart kütüphane, Python 3)
├── update.py            → kaynak depolardan güncel verileri senkronize eden script (--check rapor modu dahil)
├── backups/            → temizlenmiş CloudStream veri yedeği örneği (kişisel veri yok)
└── DEPO-BILGILERI.md    → bu doküman
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

| Kaynak repo (GitHub) | Eklenti | Adet | Son Guncelleme |
|----------------------|---------|------|----------------|
| [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | LoveFilm | 1 | 2026-08-28 |
| [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | Ddizi, DiziYou, FilmMakinesi, FilmModu, HDFilmCehennemi, SinemaCX, JetFilmizle, SezonlukDizi, DiziPalOriginal, HDFilmDelisi | 10 | 2026-08-27 |
| [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | Full4kizle | 1 | 2026-08-27 |
| [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | DiziBox, DiziFilmORG, Dizigecesi, DiziLife, Dizilla, DiziMom, DiziPal, DiziPalOrijinal, Dizipod, DiziYo, FilmEkseni, FilmHane, HDFilmizle, KraptorPlus, SelcukFlix, SetFilmIzle, Sinezy, Turkdizileri, TvDiziler, WebteIzle, WFilmizle, YabanciDizi | 22 | 2026-08-25 |
| [MRTDEVM/cloudstream-turkce](https://github.com/MRTDEVM/cloudstream-turkce) | FullHDFilmizlesene | 1 | 2026-08-21 |
| [pltmustafa/plt-stream](https://github.com/pltmustafa/plt-stream) | plt-stream | 1 | 2026-08-14 |
| [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | Sinewix | 1 | 2026-06-18 |


Eskiden kullanılan / hiç kullanılmayan kaynaklar:
- `Kraptor123/cs-kraptor` — **KAPANDI.** Depo sıfırlandı, README'de "desteği kesmiş bulunuyorum" ibaresi var; tüm `.cs3` dosyaları 404 veriyor. Bu kaynaktan gelen 29 eklenti listeden çıkarıldı; bazıları Feroxx deposundaki canlı sürümleriyle listede.
- `NivinCNC/CNCVerse-Cloud-Stream-Extension` — `CricifyProvider` (canlı spor) bu kaynaktan geliyordu; kullanıcı canlı spor istemediği için eklenti yok.
- `Kraptor123/Cs-Karma` — `Streamed` (canlı spor) bu kaynaktan geliyordu; kullanıcı istemedi. Kaynaktan yalnızca `Full4kizle` kaldı.
- `Kraptor123/Cs-GizliKeyif` — tamamı +18 NSFW içerikliydi (108 kayıt; NSFW olmayan kayıt yok), hiç eklenmedi.
- `sarapcanagii/*` — `NeonSpor` (canlı) bu kaynaktan gelmişti; kullanıcı istemedi.
- `ByAyzen/AyzenCS3` — `Syncler`, `Torrential` bu kaynaktan geliyordu; kişisel tercihle silindi.
> Not: Kaynakların tamamı `raw.githubusercontent.com` üzerinden `builds/plugins.json` ve/veya tekil `.cs3` dosya adresleriyle çekildi; hiçbir eklenti kopyalanıp yeniden barındırılmadı, adresler kaynak repoya işaret eder.

## Yapısal Kontrol (verify.py)
```bash
python verify.py               # yapısal + ağ kontrolleri (varsayılan)
python verify.py --offline     # yalnızca yapısal kontroller
python verify.py --deep        # + .cs3 içinden gerçek çekim domainlerini çıkarıp test eder (uyarı üretir, karar vermez)
python verify.py --health      # + cekim domainleri TAMAMEN olmus eklentilere status:0 uygular (otomatik karar modu)
```
`verify.py` (yalnızca standart kütüphane, harici bağımlılık yok):

**Yapısal kontroller (her iki modda):**
- JSON syntax geçerliliği ve `repo.json` `pluginLists` varlığı
- `internalName`, `url`, `fileHash` alanlarında yinelenme olmaması
- Zorunlu alanların varlığı ve tip tutarlılığı (`status` 0-3: 0=kapalı, 1=açık, 2=yavaş, 3=sadece beta; `version`, `apiVersion` int; `authors` liste)
- `url` uzantısının `.cs3` olması
- `fileHash`'in `sha256-` + 64 hex formatında olması
- `tvTypes` geçerliliği: `Movie, TvSeries, Anime, Live, AsianDrama, Others, Documentary, AnimeMovie, OVA, Cartoon`
- `language` ISO uyumluluğu, `description`/`name`/yazar boşlukları; `iconUrl` içinde `%size%` yer tutucusu uyarı üretir (bu depo ikonları normalize eder: `%size%` → `sz=128`)

**Ağ kontrolleri (varsayılan modda):**
- Her eklentinin `.cs3` dosyası indirilir; HTTP durumu, `fileSize` ve `fileHash` (SHA-256) uyumu doğrulanır
- `iconUrl` adresine HEAD/GET atılır (HTTP 200 şartı)
- Kaynak depo geçici erişilemezse "atlanabilir" kabul edilir (uyarı); dosya **404** ise hata sayılır

**Derin çekim domain kontrolü (`--deep`, deneysel):**
- Her eklentinin `.cs3` arşivi açılır, `classes.dex` içinden ASCII hostname adayları çıkarılır (bilinen TLD listesi + filtreler)
- Çıkan adaylar DNS + HTTP ile test edilir; `[SITE]` uyarısı üretilir
- İkon domaini **yerine** eklentinin gerçekten veri çektiği domainler izlenir → yanlış alarm riski düşüktür
  (ör. SinemaCX ikon domaini `sinema.cx` DNS'te ölü görünüyordu ama eklenti asıl veriyi canlı olan `sinema.gg`'den çekiyor)
- Eklentinin birden fazla kaynağından en az biri ayaktaysa sorun sayılmaz; hepsi yanıt vermiyorsa uyarı üretilir
- Domainler dinamik üretilen eklentilerde (FilmMakinesi, DiziYou gibi) aday çıkmaz, o eklenti için geçersiz sayılır

Not: **Bu script eklentilerin "çalıştığını" doğrulamaz.** Eklentinin gerçekten film/dizi açıp oynatması yalnızca CloudStream üzerinde kullanıcının testiyle anlaşılır. `--deep` modu site kapanışlarını erken yakalamak için yapılan en derin sunucu tarafı kontrolüdür; bot engelleri ve bölgesel farklar nedeniyle karar için referans alınmaz, yalnızca uyarı üretir.

**Otomatik `status:0` (`--health`):**
- `--deep`'in aksine bu mod **karar verir**: aktif eklentinin `.cs3`'ünden çıkarılan çekim domainlerinin **tamamı** kesin ölü ise eklentiyi `plugins.json`'da `status:0` yapar (CloudStream yenilemede eklentiyi devre dışı bırakır).
- Kesin ölü kriterleri: DNS çözülemiyor, ana sayfa 404/410, TLS hatası (http de ölü), veya sayfa **domain-parking "satılık" sayfası** (title/içerikte `satılıktır`, `for sale`, `Kaynaklar ve Bilgiler`, dan.com/afternic/nicsell vb. işaretler). Bunlar `--deep`'in kör noktasıydı: parking sayfası HTTP 200 döndürdüğü için "ayakta" sanılıyordu (666, FullHD örneği).
- **Yanlış pozitife kapalı:** en az bir domain ayaktaysa veya herhangi bir domain `unknown` (zaman aşımı, bot engeli 403, belirsiz) ise **dokunulmaz**. Dinamik domainli eklentilerde (FilmMakinesi, DiziYou…) domain çıkmadığı için hiçbir zaman otomatik kapatılmaz.
- `status:1`'e (yeniden açma) **asla** otomatik dönülmez — bunu yalnızca kullanıcı yapar. Bu yüzden yanlış kapatma riski düşüktür ve geri dönüşü kolaydır.
- Elle `python verify.py --health` komutuyla çalıştırılır (otomatik çalışmaz).

## Kaynak Senkronizasyonu (update.py)
```bash
python update.py --check    # yazmadan sadece farkları raporlar (fark varsa exit 1)
python update.py            # farkları uygular, plugins.json'u günceller
```
Kaynak `builds/plugins.json` adresi, listedeki `.cs3` adresinden türetilir (`https://raw.githubusercontent.com/<owner>/<repo>/builds/<Isim>.cs3` → aynı klasördeki `plugins.json`). Senkronize edilen alanlar: `version, fileSize, fileHash, description, authors, language, tvTypes`. `iconUrl` bilinçli olarak senkronize **edilmez** — bu depo ikon adreslerini normalize eder (kaynaktaki `%size%` yer tutucuları sabit `sz=128`'e çevrilir) ve kaynak güncellemesi bu düzeltmeyi geri almasın.

> **Not:** Bu depo **otomatik hiçbir şey çalıştırmaz** (GitHub Actions yok). Kaynak senkronu (`update.py`), site sağlık kontrolü (`verify.py --deep`/`--health`) ve status değişiklikleri yalnızca **elle** yapılır. `[ATLANDI]` sayısı, kaynak depo bazında toplu kapanışın (ör. cs-kraptor kapanışı: 29 eklenti tek seferde 404) erken işaretidir.

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
| `git push` çıktısında kırmızı `NativeCommandError` görünüyordu | PowerShell, git'in stderr'e yazdığı ilerleme satırlarını hata sanıyor | Gerçek hata değil — çıktının sonunda `fb7f710..6aea63d main -> main` görülüyorsa push başarılı demektir |
| YAML doğrulama `ModuleNotFoundError: No module named 'yaml'` | Python'da PyYAML kurulu değildi | `python -m pip install pyyaml` ile kuruldu; doğrulama `yaml.safe_load` ile geçti |
| YAML doğrulamada `KeyError: 'on'` | PyYAML YAML 1.1'de `on:` anahtarını bool `True`'ya çevirir (GitHub Actions YAML 1.2 kullanır ve `on`'u string kabul eder) | Gerçek hata değil; GitHub Actions bu dosyayı doğru ayrıştırır (workflow dosyası sorunsuz çalışır) |
| `verify.py --health` yanlış eklenti kapatabilir mi (tasarım) | Eski `--deep` HTTP 200 kontrolü parking sayfasını "ayakta" sanabiliyordu (666/FullHD yanlış pozitifi) | `--health` sayfa içeriği/title ile parking tespiti ekledi, **kesin ölü** (DNS/404/TLS/parking) dışında karar vermiyor; `unknown` veya canlı domain varsa dokunmuyor. Test: 6 parking/legit vaka + gerçek 666filmizle.site `dead` sınıflandı; 13 aktif eklenti tarandı, yanlış kapanma yok |

### Tekrar Kontrol Edilecekler (Dead Link Değildir, repo build güncellendiğinde belki çalışacaktır ?)
| Eklenti | Kaynak | Son Bilinen Domain | Durum |
|---------|--------|-------------------|-------|
| AltiYuzAltmisAltiFilmIzle | feroxx/ilkel | 666filmizle.site | 🟨 Site ölü, tekrar kontrol edilecek |
| FilmBip | ilkel | filmbip.com | 🟨 Site ölü, tekrar kontrol edilecek |
| FullHDFilm | feroxx | fullhdfilm.org | 🟨 Site ölü, tekrar kontrol edilecek |
| Filmatek | Kraptor123/Cs-Karma | filmatek.net | 🟨 Site ölü, tekrar kontrol edilecek |
| Full4kizle | Kraptor123/Cs-Karma | plusizle.net | 🟨 **status:0** — domain plusizle.org'a taşındı, build bekleniyor |
| DiziFilmORG | aytzey/cs-kraptor | dizifilm.org | 🟨 **status:0** — çalışmıyor, repobuild gelince kontrol |
| DiziPal | aytzey/cs-kraptor | dizipal.im | 🟨 **status:0** — çalışmıyor (DiziPalOriginal v84 + DiziPalOrijinal v45 çalışıyor) |
| DiziYo | aytzey/cs-kraptor | diziyo (DiziYo) | 🟨 **status:0** — çalışmıyor (DiziYou v25 çalışıyor) |
| SetFilmIzle | aytzey/cs-kraptor | www.setfilmizle.uk | 🟨 **status:0** — çalışmıyor, repobuild gelince kontrol |

> **Not (2026-08-28):** Yukarıdaki tablodan `DiziBox`, `DiziMom`, `Dizilla`, `WebteIzle` aynı build güncellendiğinde / yeni repolardan farklı domainlerle yeniden eklendiği için çıkarıldı: `aytzey/cs-kraptor`'da `DiziBox (dizibox.de)`, `DiziMom (dizimom.mom)`, `Dizilla (dizilla.to)`, `WebteIzle (webteizle1.xyz)` olarak `plugins.json`'a aktif eklendi ve çalışıyor. `SetFilmIzle` ise aytzey'de **status:0** ile yeniden eklenip bu tabloda izleniyor (repobuild gelince kontrol). Bu mantıkla tablo, sadece hala ölü ve yeni repo/build'de de çalışmayanlar için tutulur.
> **Not:** Bu liste güncellenebilir; aynı build güncellendiğinde veya yeni repolarda yeniden eklendiğinde çalışanlar ana listeye alınır, hala ölü olanlar burada bırakılır.

### Önemli Not
Repolar güncellendiğinde (yeni build yayınlandığında (GitHub uzerinden takip edilir)), bu listedeki ölü siteler otomatik olarak kontrol edilmeli ve çalışıyorsa tekrar eklenebilir.

## Silinen Eklentiler (delete-zone)
Bu eklentiler listeye **eklenmez**; yeniden ekleme kararı yalnızca kullanıcı verir. Listede NSFW (+18) hiç yer almadı; canlı yayın/maç eklentileri istenmedi. Bozuk eklentiler silinmez, `status:0` yapılır (bkz. Kurulum). "Site açılmıyor" gerekçesiyle silinenler **geri dönüşlüdür**: site düzelirse tekrar denenebilir.

**Anime/Asya içerikli (kullanıcı anime istemiyor):** AnimeciX, Animeler, Animely, AnimPow, Anizium, OnePaceTr, OpenAnime, TrAnimeIzle, TurkAnime, AsyaAnimeleri, AsyaFanatiklerim, AsyaWatch, DiziAsia, DiziAsya, DiziKorea, Koredizi, AnimeAV, AnimeWorld, AnimeYTX, Latanime, DramaDizilerim, Dramaizle, AsyaMinik, TRanimaci
**Canlı yayın / maç (kullanıcı hiçbir halükarda istemiyor):** InatBox, NeonSpor, RecTV, Streamed, CricifyProvider, GinikoCanli, KickTR, Youtube, TVGarden, WatchWrestling
**Diğer ("kesinlikle istemiyorum" / kişisel tercih):** Filmmirasım, SeiCode, YTS, YeniKaynak, YesilCamTv, MirrorVerse, Vavoo, WebDramaTurkey, Syncler, Torrential, BelgeselX, CizgiMax, CizgiveDizi, KultFilmler, RareFilmm, TmdbProvider, EnglishW, TurkishW, Cloud-Sync, BasketballReplays, UgurFilm, Watch2Movies, WebdramaTurkey2, TLCtr, TRasyalog
**Türkçe/Türkiye filtresi (yabancı dil içerikli):** Esheaq, Krmzy, YoTurkish, DoramasLatinoX, Dubbindo, Flixlatam, Henaojara, Gnulahd, JPFilms, KissKH, LayarKaca, Movix, OK, Sokuja, Subsplease, Supercartoons, Wcoflix, Yablom, DocumentaryArea, Iwatchtheoffice, FullRaces, FootReplays, Filmzal

## Duplicate / Çakışan Eklentiler

Aynı isim/kökten farklı repo/build'lerde gelen ve yalnızca 1 tanesi listede tutulan eklentiler. Her gruptan sadece 1 tanesi `plugins.json`'da yer alır; diğer(leri) duplicate olarak eklenmez, repobuild güncellendiğinde kontrol edilir.

| Grup | Seçilen (Aktif) | Versiyon | Kaynak | Duplicate (Eklenmedi) | Duplicate Kaynak | Durum / Not |
|------|---------------------|----------|--------|------------------------|------------------|-------------|
| DiziLife | DiziLife | v58 | aytzey/cs-kraptor | DiziLife | blackhope v2 | 🟧 Duplicate, aytzey tercih edildi |
| DiziMom | DiziMom | v61 | aytzey/cs-kraptor | DiziMom | blackhope v3 | 🟧 Duplicate, aytzey tercih edildi |
| FilmEkseni | FilmEkseni | v50 | aytzey/cs-kraptor | FilmEkseni | blackhope v1 | 🟧 Duplicate, aytzey tercih edildi |
| FilmHane | FilmHane | v43 | aytzey/cs-kraptor | FilmHane | blackhope v1 | 🟧 Duplicate, aytzey tercih edildi |
| WebteIzle | WebteIzle | v53 | aytzey/cs-kraptor | Webteizle | blackhope v1 | 🟧 Duplicate, aytzey tercih edildi |

> **Not:** Duplicate tablosu sadece farklı repo/build'lerdeki aynı isimli eklentiler için tutulur; `status:0` olan `DiziFilmORG`, `DiziPal`, `DiziYo`, `SetFilmIzle` ve `Full4kizle` artık **Tekrar Kontrol** tablosunda (yeniden eklenebilirler) izlenir. Her iki tablo da güncellenebilir.


## Güncelleme
Yeni bir değişiklik yapıldığında:
```bash
python verify.py --offline      # önce yapısal doğrula
python update.py --check        # kaynak farkı var mı bak (exit 1 = var)
python update.py                # gerekirse kaynak verilerini senkronize et
python verify.py --health       # ölmüş eklentileri status:0 yap (elle tetikleme)
python verify.py --deep         # senkronizasyon sonrası ağ + gerçek çekim domaini kontrolü
git add plugins.json
git -c user.name="kadircee" -c user.email="kadircee@users.noreply.github.com" \
    commit -m "plugins.json: aciklama"
git push
```
Push sonrası jsDelivr önbelleği için:
```
https://purge.jsdelivr.net/gh/kadircee/ozel-liste@main/plugins.json
```
CloudStream tarafında depo yenilendiğinde yeni liste otomatik çekilir. Kaynak senkronu ve site sağlığı **otomatik değildir** (GitHub Actions yok): kaynak bir eklentiyi güncellediğinde listedeki hash/boyut **elle** `update.py` çalıştırılarak senkronlanır, kaynak site ölürse eklenti **elle** `verify.py --health` (veya `--deep`) çalıştırılarak `status:0` yapılır. `status:1`'e (yeniden açma) otomatik dönülmez; site geri geldiyse `plugins.json`'da ilgili eklentinin `status`'u elle `1` yapılır. Güncelleme öncesi `verify.py --offline` ve `update.py --check` ile kontrol etmek iyi alışkanlıktır.



## Tüm Repolar - Alfabetik Liste

Bu bölüm otomatik üretildi (2026-08-28) — tüm kaynak repolardaki 107 eklenti (Istenmeyenler ve ozel-liste hariç) alfabetik, site domain ve durum bilgisiyle.

Aynı isim/kökten farklı repo/build'lerde gelen ve yalnızca 1 tanesi listede tutulan eklentiler için aynı mantık geçerlidir: Her gruptan sadece 1 tanesi `plugins.json`'da yer alır; diğer(leri) duplicate olarak eklenmez, repobuild güncellendiğinde kontrol edilir. Renkler: 🟩 Çalışan (yeşil), 🟨 Çalışmayan (sarı), 🟧 Duplicate (turuncu), 🟥 İstenmeyen/Ignore (kırmızı), 🟦 Eklenebilir (mavi).
Toplam kayit: 95 (Istenmeyenler ve ozel-liste hariç, sadece kaynak repolar)

| # | Eklenti | Kaynak | Site (domain) | v | Kaynak Tarih | Bizim Tarih | Durum |
|---|---------|--------|---------------|---|---|----------------|---------------|
| 1 | 🟦 AltiYuzAltmisAltiFilmIzle | ilkelkullanici/ilkel-cloudstream | [666filmizle.site](https://666filmizle.site) | 1 | 2026-06-11 | - | 🟨 Çalışmıyor (son ölü: 2026-08-22, ilkel build güncellendiğinde kontrol) |
| 2 | 🟦 CanliTV | feroxx/Kekik-cloudstream | [tr.canlitv.team](https://tr.canlitv.team) | 10 | 2025-08-05 | - | 🟧 Duplicate (ilkelkullanici 2026-06-11 tercih edildi) |
| 3 | 🟦 CanliTV | ilkelkullanici/ilkel-cloudstream | [tr.canlitv.team](https://tr.canlitv.team) | 10 | 2026-06-11 | - | 🟦 Eklenebilir |
| 4 | 🟩 Ddizi | feroxx/Kekik-cloudstream | [www.ddizi.im](https://www.ddizi.im) | 22 | 2026-04-01 | 2026-08-22 | 🟧 Duplicate (aytzey 2026-07-14 tercih edildi) |
| 5 | 🟩 Ddizi | ilkelkullanici/ilkel-cloudstream | [www.ddizi.im](https://www.ddizi.im) | 22 | 2026-06-11 | 2026-08-22 | 🟧 Duplicate (aytzey 2026-07-14 tercih edildi) |
| 6 | 🟩 Ddizi | aytzey/cs-kraptor | [www.ddizi.im](https://www.ddizi.im) | 19 | 2026-07-14 | 2026-08-22 | 🟩 Çalışıyor |
| 7 | 🟩 DiziBox | feroxx/Kekik-cloudstream | [www.dizibox.live](https://www.dizibox.live) | 23 | 2025-10-27 | 2026-08-28 | 🟧 Duplicate (ilkelkullanici 2026-06-11 tercih edildi) |
| 8 | 🟩 DiziBox | ilkelkullanici/ilkel-cloudstream | [www.dizibox.live](https://www.dizibox.live) | 23 | 2026-06-11 | 2026-08-28 | 🟩 Çalışıyor |
| 9 | 🟩 DiziBox | aytzey/cs-kraptor | [www.dizibox.de](https://www.dizibox.de) | 37 | 2025-08-14 | 2026-08-28 | 🟧 Duplicate (ilkelkullanici 2026-06-11 tercih edildi) |
| 10 | 🟨 DiziFilmORG | aytzey/cs-kraptor | [dizifilm.org](https://dizifilm.org) | 22 | 2026-07-24 | 2026-08-28 | 🟨 Çalışmıyor |
| 11 | 🟩 Dizigecesi | aytzey/cs-kraptor | [dizigecesi.com](https://dizigecesi.com) | 4 | 2026-07-15 | 2026-08-28 | 🟩 Çalışıyor |
| 12 | 🟩 DiziLife | blackhope01/cloudstream-plugins | [dizi73.life](https://dizi73.life) | 2 | 2026-08-28 | 2026-08-28 | 🟩 Çalışıyor |
| 13 | 🟩 DiziLife | aytzey/cs-kraptor | [dizi18.life](https://dizi18.life) | 58 | 2026-07-24 | 2026-08-28 | 🟧 Duplicate (blackhope01 2026-08-28 tercih edildi) |
| 14 | 🟩 Dizilla | feroxx/Kekik-cloudstream | [dizilla.club](https://dizilla.club) | 92 | 2026-08-23 | 2026-08-28 | 🟩 Çalışıyor |
| 15 | 🟩 Dizilla | ilkelkullanici/ilkel-cloudstream | [dizilla.club](https://dizilla.club) | 92 | 2026-06-11 | 2026-08-28 | 🟧 Duplicate (feroxx 2026-08-23 tercih edildi) |
| 16 | 🟩 Dizilla | aytzey/cs-kraptor | [dizilla.to](https://dizilla.to) | 111 | 2025-08-14 | 2026-08-28 | 🟧 Duplicate (feroxx 2026-08-23 tercih edildi) |
| 17 | 🟩 DiziMom | feroxx/Kekik-cloudstream | [www.dizimom.plus](https://www.dizimom.plus) | 56 | 2026-08-28 | 2026-08-28 | 🟩 Çalışıyor |
| 18 | 🟩 DiziMom | ilkelkullanici/ilkel-cloudstream | [www.dizimom.plus](https://www.dizimom.plus) | 43 | 2026-08-28 | 2026-08-28 | 🟧 Duplicate (feroxx 2026-08-28 tercih edildi) |
| 19 | 🟩 DiziMom | blackhope01/cloudstream-plugins | [www.dizimom.surf](https://www.dizimom.surf) | 3 | 2026-08-28 | 2026-08-28 | 🟧 Duplicate (feroxx 2026-08-28 tercih edildi) |
| 20 | 🟩 DiziMom | aytzey/cs-kraptor | [www.dizimom.mom](https://www.dizimom.mom) | 61 | 2025-08-14 | 2026-08-28 | 🟧 Duplicate (feroxx 2026-08-28 tercih edildi) |
| 21 | 🟨 DiziPal | feroxx/Kekik-cloudstream | [dizipal1563.com](https://dizipal1563.com) | 104 | 2026-08-22 | 2026-08-28 | 🟧 Duplicate (ilkelkullanici 2026-08-28 tercih edildi) |
| 22 | 🟨 DiziPal | ilkelkullanici/ilkel-cloudstream | [dizipal952.com](https://dizipal952.com) | 90 | 2026-08-28 | 2026-08-28 | 🟨 Çalışmıyor |
| 23 | 🟨 DiziPal | aytzey/cs-kraptor | [dizipal.im](https://dizipal.im) | 89 | 2025-08-14 | 2026-08-28 | 🟧 Duplicate (ilkelkullanici 2026-08-28 tercih edildi) |
| 24 | 🟩 DiziPalOriginal | feroxx/Kekik-cloudstream | [chessplyimages.cfd](https://chessplyimages.cfd) | 84 | 2026-08-28 | 2026-08-28 | 🟩 Çalışıyor |
| 25 | 🟩 DiziPalOriginal | ilkelkullanici/ilkel-cloudstream | [dizipal2036.com](https://dizipal2036.com) | 66 | 2026-08-28 | 2026-08-28 | 🟧 Duplicate (feroxx 2026-08-28 tercih edildi) |
| 26 | 🟩 DiziPalOrijinal | aytzey/cs-kraptor | [dizipal932.com](https://dizipal932.com) | 45 | 2026-08-05 | 2026-08-28 | 🟩 Çalışıyor |
| 27 | 🟩 Dizipod | aytzey/cs-kraptor | [dizipod.com](https://dizipod.com) | 12 | 2026-07-24 | 2026-08-28 | 🟩 Çalışıyor |
| 28 | 🟨 DiziYo | blackhope01/cloudstream-plugins | [www.diziyo.so](https://www.diziyo.so) | 1 | 2026-08-25 | 2026-08-28 | 🟨 Çalışmıyor |
| 29 | 🟨 DiziYo | aytzey/cs-kraptor | [i.imgur.com](https://i.imgur.com) | 74 | 2025-08-14 | 2026-08-28 | 🟧 Duplicate (blackhope01 2026-08-25 tercih edildi) |
| 30 | 🟩 DiziYou | feroxx/Kekik-cloudstream | [cdn.diziyou.one](https://cdn.diziyou.one) | 25 | 2026-07-20 | 2026-08-22 | 🟩 Çalışıyor |
| 31 | 🟩 DiziYou | ilkelkullanici/ilkel-cloudstream | [cdn.diziyou6.com](https://cdn.diziyou6.com) | 25 | 2026-06-11 | 2026-08-22 | 🟧 Duplicate (feroxx 2026-07-20 tercih edildi) |
| 32 | 🟩 DiziYou | aytzey/cs-kraptor | [www.diziyou.co](https://www.diziyou.co) | 49 | 2025-08-14 | 2026-08-22 | 🟧 Duplicate (feroxx 2026-07-20 tercih edildi) |
| 33 | 🟦 F1FullRaces | Kraptor123/Cs-Karma | [i.imgur.com](https://i.imgur.com) | 10 | 2026-06-17 | - | 🟦 Eklenebilir |
| 34 | 🟦 FilmBip | ilkelkullanici/ilkel-cloudstream | [filmbip.com](https://filmbip.com) | 19 | 2026-06-11 | - | 🟦 Eklenebilir |
| 35 | 🟩 FilmEkseni | blackhope01/cloudstream-plugins | [www.filmekseni.vip](https://www.filmekseni.vip) | 1 | 2026-08-25 | 2026-08-28 | 🟩 Çalışıyor |
| 36 | 🟩 FilmEkseni | aytzey/cs-kraptor | [filmekseni.net](https://filmekseni.net) | 50 | 2025-08-14 | 2026-08-28 | 🟧 Duplicate (blackhope01 2026-08-25 tercih edildi) |
| 37 | 🟩 FilmHane | blackhope01/cloudstream-plugins | [www.filmhane.shop](https://www.filmhane.shop) | 1 | 2026-08-25 | 2026-08-28 | 🟩 Çalışıyor |
| 38 | 🟩 FilmHane | aytzey/cs-kraptor | [encrypted-tbn1.gstatic.com](https://encrypted-tbn1.gstatic.com) | 43 | 2025-08-14 | 2026-08-28 | 🟧 Duplicate (blackhope01 2026-08-25 tercih edildi) |
| 39 | 🟩 FilmMakinesi | feroxx/Kekik-cloudstream | [filmmakinesi.film](https://filmmakinesi.film) | 58 | 2026-08-23 | 2026-08-22 | 🟧 Duplicate (blackhope01 2026-08-25 tercih edildi) |
| 40 | 🟩 FilmMakinesi | ilkelkullanici/ilkel-cloudstream | [filmmakinesi.film](https://filmmakinesi.film) | 57 | 2026-06-11 | 2026-08-22 | 🟧 Duplicate (blackhope01 2026-08-25 tercih edildi) |
| 41 | 🟩 FilmMakinesi | MRTDEVM/cloudstream-turkce | [filmmakinesi.to](https://filmmakinesi.to) | 8 | 2026-08-21 | 2026-08-22 | 🟧 Duplicate (blackhope01 2026-08-25 tercih edildi) |
| 42 | 🟩 FilmMakinesi | blackhope01/cloudstream-plugins | [www.filmmakinesi.to](https://www.filmmakinesi.to) | 1 | 2026-08-25 | 2026-08-22 | 🟩 Çalışıyor |
| 43 | 🟩 FilmMakinesi | aytzey/cs-kraptor | [filmmakinesi.tv](https://filmmakinesi.tv) | 70 | 2025-08-14 | 2026-08-22 | 🟧 Duplicate (blackhope01 2026-08-25 tercih edildi) |
| 44 | 🟩 FilmModu | feroxx/Kekik-cloudstream | [www.filmmodu.one](https://www.filmmodu.one) | 19 | 2026-07-20 | 2026-08-22 | 🟩 Çalışıyor |
| 45 | 🟩 FilmModu | ilkelkullanici/ilkel-cloudstream | [www.filmmodu17.com](https://www.filmmodu17.com) | 19 | 2026-06-11 | 2026-08-22 | 🟧 Duplicate (feroxx 2026-07-20 tercih edildi) |
| 46 | 🟩 FilmModu | aytzey/cs-kraptor | [www.filmmodu.one](https://www.filmmodu.one) | 41 | 2025-08-14 | 2026-08-22 | 🟧 Duplicate (feroxx 2026-07-20 tercih edildi) |
| 47 | 🟦 Footballia | Kraptor123/Cs-Karma | [footballia.net](https://footballia.net) | 9 | 2026-06-03 | - | 🟦 Eklenebilir |
| 48 | 🟨 Full4kizle | Kraptor123/Cs-Karma | [plusizle.net](https://plusizle.net) | 20 | 2026-08-27 | 2026-08-22 | 🟨 Çalışmıyor |
| 49 | 🟦 FullHDFilm | feroxx/Kekik-cloudstream | [hdfilm.us](https://hdfilm.us) | 36 | 2026-07-20 | - | 🟩 Çalışıyor (2026-07-20 en güncel) |
| 50 | 🟦 FullHDFilm | ilkelkullanici/ilkel-cloudstream | [fullhdfilm.us](https://fullhdfilm.us) | 36 | 2026-06-11 | - | 🟧 Duplicate (feroxx 2026-07-20 tercih edildi) |
| 51 | 🟩 FullHDFilmizlesene | feroxx/Kekik-cloudstream | [www.fullhdfilmizlesene.de](https://www.fullhdfilmizlesene.de) | 33 | 2026-08-22 | 2026-08-22 | 🟧 Duplicate (ilkelkullanici 2026-08-28 tercih edildi) |
| 52 | 🟩 FullHDFilmizlesene | ilkelkullanici/ilkel-cloudstream | [www.fullhdfilmizlesene.de](https://www.fullhdfilmizlesene.de) | 29 | 2026-08-28 | 2026-08-22 | 🟩 Çalışıyor |
| 53 | 🟩 FullHDFilmizlesene | MRTDEVM/cloudstream-turkce | [www.fullhdfilmizlesene.now](https://www.fullhdfilmizlesene.now) | 8 | 2026-08-21 | 2026-08-22 | 🟧 Duplicate (ilkelkullanici 2026-08-28 tercih edildi) |
| 54 | 🟩 FullHDFilmizlesene | aytzey/cs-kraptor | [www.fullhdfilmizlesene.de](https://www.fullhdfilmizlesene.de) | 72 | 2025-08-14 | 2026-08-22 | 🟧 Duplicate (ilkelkullanici 2026-08-28 tercih edildi) |
| 55 | 🟩 HDFilmCehennemi | feroxx/Kekik-cloudstream | [hdfilmcehennemi.com](https://hdfilmcehennemi.com) | 48 | 2026-07-19 | 2026-08-22 | 🟧 Duplicate (MRTDEVM 2026-08-21 tercih edildi) |
| 56 | 🟩 HDFilmCehennemi | ilkelkullanici/ilkel-cloudstream | [hdfilmcehennemi.com](https://hdfilmcehennemi.com) | 47 | 2026-06-11 | 2026-08-22 | 🟧 Duplicate (MRTDEVM 2026-08-21 tercih edildi) |
| 57 | 🟩 Hdfilmcehennemi | MRTDEVM/cloudstream-turkce | [www.hdfilmcehennemi.nl](https://www.hdfilmcehennemi.nl) | 8 | 2026-08-21 | - | 🟩 Çalışıyor |
| 58 | 🟩 HDFilmCehennemi | aytzey/cs-kraptor | [hdfilmcehennemi.nl](https://hdfilmcehennemi.nl) | 97 | 2025-08-14 | 2026-08-22 | 🟧 Duplicate (MRTDEVM 2026-08-21 tercih edildi) |
| 59 | 🟩 HDFilmDelisi | feroxx/Kekik-cloudstream | [hdfilmdelisi.com](https://hdfilmdelisi.com) | 1 | 2026-08-27 | 2026-08-28 | 🟩 Çalışıyor |
| 60 | 🟩 HDFilmDelisi | aytzey/cs-kraptor | [hdfilmdelisi.one](https://hdfilmdelisi.one) | 18 | 2026-07-15 | 2026-08-28 | 🟧 Duplicate (feroxx 2026-08-27 tercih edildi) |
| 61 | 🟩 HDFilmizle | aytzey/cs-kraptor | [www.hdfilmizle.life](https://www.hdfilmizle.life) | 25 | 2026-08-05 | 2026-08-28 | 🟩 Çalışıyor |
| 62 | 🟩 JetFilmizle | feroxx/Kekik-cloudstream | [jetfilmizle.de](https://jetfilmizle.de) | 47 | 2026-08-23 | 2026-08-22 | 🟧 Duplicate (blackhope01 2026-08-25 tercih edildi) |
| 63 | 🟩 JetFilmizle | ilkelkullanici/ilkel-cloudstream | [jetfilmizle.de](https://jetfilmizle.de) | 47 | 2026-06-11 | 2026-08-22 | 🟧 Duplicate (blackhope01 2026-08-25 tercih edildi) |
| 64 | 🟩 JetFilmizle | blackhope01/cloudstream-plugins | [jetfilmizle.now](https://jetfilmizle.now) | 1 | 2026-08-25 | 2026-08-22 | 🟩 Çalışıyor |
| 65 | 🟩 JetFilmizle | aytzey/cs-kraptor | [jetfilmizle.de](https://jetfilmizle.de) | 62 | 2025-08-14 | 2026-08-22 | 🟧 Duplicate (blackhope01 2026-08-25 tercih edildi) |
| 66 | 🟦 KoreanTurk | ilkelkullanici/ilkel-cloudstream | [koreanturk.com](https://koreanturk.com) | 7 | 2026-06-11 | - | 🟦 Eklenebilir |
| 67 | 🟩 KraptorPlus | aytzey/cs-kraptor | [raw.githubusercontent.com](https://raw.githubusercontent.com) | 86 | 2026-08-04 | 2026-08-28 | 🟩 Çalışıyor |
| 68 | 🟩 LoveFilm | blackhope01/cloudstream-plugins | [lovefilmizle.net](https://lovefilmizle.net) | 1 | 2026-08-25 | 2026-08-28 | 🟩 Çalışıyor |
| 69 | 🟦 OnShort | Kraptor123/Cs-Karma | [onshort.net](https://onshort.net) | 1 | 2026-08-23 | - | 🟦 Eklenebilir |
| 70 | 🟦 plt-party | pltmustafa/plt-stream | [raw.githubusercontent.com](https://raw.githubusercontent.com) | 5 | 2026-08-20 | - | 🟦 Eklenebilir |
| 71 | 🟩 plt-stream | pltmustafa/plt-stream | [raw.githubusercontent.com](https://raw.githubusercontent.com) | 47 | 2026-08-24 | 2026-08-22 | 🟩 Çalışıyor |
| 72 | 🟦 plt-tv | pltmustafa/plt-stream | [raw.githubusercontent.com](https://raw.githubusercontent.com) | 3 | 2026-08-23 | - | 🟦 Eklenebilir |
| 73 | 🟩 SelcukFlix | aytzey/cs-kraptor | [selcukflix.com](https://selcukflix.com) | 49 | 2026-07-15 | 2026-08-28 | 🟩 Çalışıyor |
| 74 | 🟨 SetFilmIzle | feroxx/Kekik-cloudstream | [www.setfilmizle.uk](https://www.setfilmizle.uk) | 30 | 2026-07-22 | 2026-08-28 | 🟨 Çalışmıyor |
| 75 | 🟨 SetFilmIzle | ilkelkullanici/ilkel-cloudstream | [www.setfilmizle.nl](https://www.setfilmizle.nl) | 28 | 2026-06-11 | 2026-08-28 | 🟧 Duplicate (feroxx 2026-07-22 tercih edildi) |
| 76 | 🟨 SetFilmIzle | aytzey/cs-kraptor | [www.setfilmizle.uk](https://www.setfilmizle.uk) | 42 | 2025-08-14 | 2026-08-28 | 🟧 Duplicate (feroxx 2026-07-22 tercih edildi) |
| 77 | 🟩 SezonlukDizi | feroxx/Kekik-cloudstream | [sezonlukdizi6.com](https://sezonlukdizi6.com) | 9 | 2026-07-15 | 2026-08-22 | 🟧 Duplicate (ilkelkullanici 2026-08-28 tercih edildi) |
| 78 | 🟩 SezonlukDizi | ilkelkullanici/ilkel-cloudstream | [sezonlukdizi6.com](https://sezonlukdizi6.com) | 8 | 2026-08-28 | 2026-08-22 | 🟩 Çalışıyor |
| 79 | 🟩 SezonlukDizi | blackhope01/cloudstream-plugins | [sezonlukdizi.cc](https://sezonlukdizi.cc) | 1 | 2026-08-25 | 2026-08-22 | 🟧 Duplicate (ilkelkullanici 2026-08-28 tercih edildi) |
| 80 | 🟩 SezonlukDizi | aytzey/cs-kraptor | [sezonlukdizi6.com](https://sezonlukdizi6.com) | 40 | 2025-08-14 | 2026-08-22 | 🟧 Duplicate (ilkelkullanici 2026-08-28 tercih edildi) |
| 81 | 🟩 SinemaCX | feroxx/Kekik-cloudstream | [www.sinema.cx](https://www.sinema.cx) | 24 | 2026-04-24 | 2026-08-22 | 🟧 Duplicate (ilkelkullanici 2026-06-11 tercih edildi) |
| 82 | 🟩 SinemaCX | ilkelkullanici/ilkel-cloudstream | [www.sinema.cx](https://www.sinema.cx) | 24 | 2026-06-11 | 2026-08-22 | 🟩 Çalışıyor |
| 83 | 🟩 SinemaCX | aytzey/cs-kraptor | [www.sinema.gg](https://www.sinema.gg) | 35 | 2025-08-14 | 2026-08-22 | 🟧 Duplicate (ilkelkullanici 2026-06-11 tercih edildi) |
| 84 | 🟩 Sinewix | feroxx/Kekik-cloudstream | [play-lh.googleusercontent.com](https://play-lh.googleusercontent.com) | 2 | 2026-08-23 | 2026-08-22 | 🟩 Çalışıyor |
| 85 | 🟩 Sinewix | ilkelkullanici/ilkel-cloudstream | [play-lh.googleusercontent.com](https://play-lh.googleusercontent.com) | 2 | 2026-06-11 | 2026-08-22 | 🟧 Duplicate (feroxx 2026-08-23 tercih edildi) |
| 86 | 🟩 SineWix | aytzey/cs-kraptor | [play-lh.googleusercontent.com](https://play-lh.googleusercontent.com) | 33 | 2026-07-15 | - | 🟧 Duplicate (feroxx 2026-08-23 tercih edildi) |
| 87 | 🟩 Sinezy | aytzey/cs-kraptor | [sinezy.fit](https://sinezy.fit) | 40 | 2026-07-14 | 2026-08-28 | 🟩 Çalışıyor |
| 88 | 🟩 Turkdizileri | aytzey/cs-kraptor | [i.imgur.com](https://i.imgur.com) | 33 | 2026-07-15 | 2026-08-28 | 🟩 Çalışıyor |
| 89 | 🟩 TvDiziler | aytzey/cs-kraptor | [tvdiziler.cc](https://tvdiziler.cc) | 18 | 2026-07-15 | 2026-08-28 | 🟩 Çalışıyor |
| 90 | 🟩 WebteIzle | feroxx/Kekik-cloudstream | [webteizle3.xyz](https://webteizle3.xyz) | 20 | 2026-08-27 | 2026-08-28 | 🟩 Çalışıyor |
| 91 | 🟩 WebteIzle | ilkelkullanici/ilkel-cloudstream | [webteizle2.com](https://webteizle2.com) | 17 | 2026-06-11 | 2026-08-28 | 🟧 Duplicate (feroxx 2026-08-27 tercih edildi) |
| 92 | 🟩 Webteizle | blackhope01/cloudstream-plugins | [webteizle3.xyz](https://webteizle3.xyz) | 1 | 2026-08-25 | - | 🟧 Duplicate (feroxx 2026-08-27 tercih edildi) |
| 93 | 🟩 WebteIzle | aytzey/cs-kraptor | [webteizle1.xyz](https://webteizle1.xyz) | 53 | 2025-08-14 | 2026-08-28 | 🟧 Duplicate (feroxx 2026-08-27 tercih edildi) |
| 94 | 🟩 WFilmizle | aytzey/cs-kraptor | [wfilmizle.bar](https://wfilmizle.bar) | 23 | 2026-07-24 | 2026-08-28 | 🟩 Çalışıyor |
| 95 | 🟩 YabanciDizi | aytzey/cs-kraptor | [yabancidizi.so](https://yabancidizi.so) | 18 | 2025-08-14 | 2026-08-28 | 🟩 Çalışıyor |## Istenmeyenler (Delete-Zone) - 74 unique

| Eklenti | Kaynak Ornek | Site | Dil | Tur |
|---------|--------------|------|-----|-----|
| 🟥 AnimeAV | Kraptor123/Cs-Karma | animeav1.com | mx | Anime |
| 🟥 AnimeciX | feroxx/Kekik-cloudstream | animecix.tv | tr | Anime |
| 🟥 Animeler | aytzey/cs-kraptor | animeler.pw | tr | Anime |
| 🟥 Animely | aytzey/cs-kraptor | play-lh.googleusercontent.com | tr | Anime,AnimeMovie,OVA |
| 🟥 AnimeWorld | Kraptor123/Cs-Karma | www.animeworld.ac | it | Anime |
| 🟥 AnimeYTX | Kraptor123/Cs-Karma | animeyt.cc | mx | Anime |
| 🟥 AnimPow | aytzey/cs-kraptor | animpow.com | tr | Anime |
| 🟥 Anizium | aytzey/cs-kraptor | anizium.co | tr | AnimeMovie,Anime |
| 🟥 AsyaAnimeleri | feroxx/Kekik-cloudstream | asyaanimeleri.top | tr | Anime |
| 🟥 AsyaFanatiklerim | aytzey/cs-kraptor | asyafanatiklerim.com | tr | AsianDrama |
| 🟥 AsyaMinik | aytzey/cs-kraptor | asyaminik.com | tr | AsianDrama |
| 🟥 AsyaWatch | aytzey/cs-kraptor | asyawatch.com | tr | AsianDrama |
| 🟥 BelgeselX | feroxx/Kekik-cloudstream | belgeselx.com | tr | Documentary |
| 🟥 CizgiMax | feroxx/Kekik-cloudstream | cizgimax.online | tr | Cartoon,Anime,Movie |
| 🟥 CizgiveDizi | aytzey/cs-kraptor | cizgivedizi.com | tr | Cartoon |
| 🟥 DiziAsia | aytzey/cs-kraptor | diziasia.com | tr | AsianDrama |
| 🟥 DiziAsya | aytzey/cs-kraptor | www.diziasya.com | tr | AsianDrama |
| 🟥 DiziKorea | feroxx/Kekik-cloudstream | dizikorea.vip | tr | AsianDrama |
| 🟥 DocumentaryArea | Kraptor123/Cs-Karma | documentaryarea.com | en | Documentary |
| 🟥 DoramasLatinoX | Kraptor123/Cs-Karma | doramaslatinox.com | mx | AsianDrama |
| 🟥 DramaDizilerim | blackhope01/cloudstream-plugins | dramadizilerim.com | tr | TvSeries |
| 🟥 Dramaizle | Kraptor123/Cs-Karma | dramaizle.net | tr | AsianDrama |
| 🟥 Dubbindo | Kraptor123/Cs-Karma | www.dubbindo.site | id | AsianDrama |
| 🟥 EnglishW | ctnkyaumt/cstest | themoviedb.org | en | Movie,TvSeries |
| 🟥 Esheaq | Kraptor123/Cs-Karma | esk.onl | ar | Movie,TvSeries |
| 🟥 Filmmirasım | Kraptor123/Cs-Karma | filmmirasim.ktb.gov.tr | tr | Documentary |
| 🟥 Filmzal | aytzey/cs-kraptor | filmzal.me | az | Movie |
| 🟥 Flixlatam | Kraptor123/Cs-Karma | flixlatam.com | mx | Movie |
| 🟥 FootReplays | Kraptor123/Cs-Karma | www.footreplays.com | en | Others |
| 🟥 FullRaces | Kraptor123/Cs-Karma | fullraces.com | en | Movie |
| 🟥 GinikoCanli | aytzey/cs-kraptor | www.giniko.com | tr | Live |
| 🟥 Gnulahd | Kraptor123/Cs-Karma | ww3.gnulahd.nu | mx | Movie,Anime,TvSeries |
| 🟥 Henaojara | Kraptor123/Cs-Karma | ww1.henaojara.net | mx | Anime,AnimeMovie |
| 🟥 InatBox | feroxx/Kekik-cloudstream | blogger.googleusercontent.com | tr | Movie,TvSeries,Live |
| 🟥 Iwatchtheoffice | Kraptor123/Cs-Karma | iwatchtheoffice.cc | en | Movie |
| 🟥 JPFilms | Kraptor123/Cs-Karma | jp-films.com | en | AsianDrama |
| 🟥 KickTR | aytzey/cs-kraptor | kick.com | tr | Live |
| 🟥 KissKH | Kraptor123/Cs-Karma | kisskh.id | en | AsianDrama |
| 🟥 Krmzy | Kraptor123/Cs-Karma | krmzy.org | ar | TvSeries |
| 🟥 KultFilmler | feroxx/Kekik-cloudstream | kultfilmler.net | tr | Movie,TvSeries |
| 🟥 Latanime | Kraptor123/Cs-Karma | latanime.org | mx | Movie |
| 🟥 LayarKaca | Kraptor123/Cs-Karma | tv12.lk21official.cc | id | Movie,TvSeries |
| 🟥 MirrorVerse | aytzey/cs-kraptor | raw.githubusercontent.com | tr | Movie,TvSeries |
| 🟥 Movix | Kraptor123/Cs-Karma | movix.fun | fr | Movie,TvSeries,Anime |
| 🟥 OK | Kraptor123/Cs-Karma | ok.ru | ru | Movie,TvSeries |
| 🟥 OnePaceTr | aytzey/cs-kraptor | www.onepacetr.net | tr | Anime |
| 🟥 OpenAnime | aytzey/cs-kraptor | openani.me | tr | Anime,AnimeMovie |
| 🟥 RareFilmm | feroxx/Kekik-cloudstream | rarefilmm.com | en | Movie |
| 🟥 RecTV | feroxx/Kekik-cloudstream | rectv.org.tr | tr | Movie,Live,TvSeries |
| 🟥 SeiCode | aytzey/cs-kraptor | seicode.net | tr | Anime |
| 🟥 Sokuja | Kraptor123/Cs-Karma | x6.sokuja.uk | id | Anime,AnimeMovie |
| 🟥 Streamed | Kraptor123/Cs-Karma | streamed.pk | en | Live |
| 🟥 Subsplease | Kraptor123/Cs-Karma | subsplease.org | en | Anime |
| 🟥 Supercartoons | Kraptor123/Cs-Karma | i.imgur.com | en | Cartoon |
| 🟥 TLCtr | feroxx/Kekik-cloudstream | www.tlctv.com.tr | tr | Movie |
| 🟥 TmdbProvider | blackhope01/cloudstream-plugins | www.diziyo.so | tr | Movie,TvSeries |
| 🟥 TRanimaci | feroxx/Kekik-cloudstream | tranimaci.com | tr | Anime |
| 🟥 TrAnimeIzle | aytzey/cs-kraptor | www.tranimeizle.io | tr | Anime |
| 🟥 TRasyalog | feroxx/Kekik-cloudstream | asyalog.co | tr | TvSeries |
| 🟥 TurkAnime | feroxx/Kekik-cloudstream | www.turkanime.co | tr | Anime |
| 🟥 TurkishW | ctnkyaumt/cstest | themoviedb.org | tr | Movie,TvSeries,Anime,Live |
| 🟥 TVGarden | Kraptor123/Cs-Karma | tv.garden | en | Live |
| 🟥 UgurFilm | ilkelkullanici/ilkel-cloudstream | ugurfilm7.com | tr | Movie |
| 🟥 Watch2Movies | feroxx/Kekik-cloudstream | movies2watch.watch | en | Movie,TvSeries |
| 🟥 WatchWrestling | Kraptor123/Cs-Karma | instapro.ac | en | Live |
| 🟥 Wcoflix | Kraptor123/Cs-Karma | www.wcoflix.tv | en | Anime,Cartoon |
| 🟥 WebDramaTurkey | aytzey/cs-kraptor | webdramaturkey.org | tr | AsianDrama |
| 🟥 WebdramaTurkey2 | feroxx/Kekik-cloudstream | webdramaturkey2.com | tr | AsianDrama,Movie,Anime,Others |
| 🟥 Yablom | Kraptor123/Cs-Karma | yablom.com | fr | Movie |
| 🟥 YeniKaynak | aytzey/cs-kraptor | www.yenikaynak.com | tr | Movie,TvSeries |
| 🟥 YesilCamTv | aytzey/cs-kraptor | yesilcamtv.com.tr | tr | Movie |
| 🟥 YoTurkish | Kraptor123/Cs-Karma | yoturkish.to | en | TvSeries |
| 🟥 Youtube | aytzey/cs-kraptor | www.youtube.com | tr | Movie,Live,Music,TvSeries |
| 🟥 YTS | aytzey/cs-kraptor | en.yts-official.mx | tr | Torrent |

.