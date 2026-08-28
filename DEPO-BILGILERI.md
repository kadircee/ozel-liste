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

## Kaynak GitHub depoları

Şu anki 37 eklentinin geldiği kaynaklar (`.cs3` adreslerinden çıkarıldı; ileride hangi kaynaktan geldiği lazım olursa buradan bakılabilir):
| Kaynak repo (GitHub) | Eklenti | Adet |
|----------------------|---------|------|
| [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | Full4kizle | 1 |
| [pltmustafa/plt-stream](https://github.com/pltmustafa/plt-stream) | plt-stream | 1 |
| [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | Ddizi, DiziYou, FilmMakinesi, FilmModu, HDFilmCehennemi, SinemaCX, JetFilmizle, SezonlukDizi, DiziPalOriginal, HDFilmDelisi | 10 |
| [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | Sinewix | 1 |
| [MRTDEVM/cloudstream-turkce](https://github.com/MRTDEVM/cloudstream-turkce) | FullHDFilmizlesene | 1 |
| [aytzey/cs-kraptor](https://github.com/aytzey/cs-kraptor) | DiziBox, DiziFilmORG, Dizigecesi, DiziLife, Dizilla, DiziMom, DiziPal, DiziPalOrijinal, Dizipod, DiziYo, FilmEkseni, FilmHane, HDFilmizle, KraptorPlus, SelcukFlix, SetFilmIzle, Sinezy, Turkdizileri, TvDiziler, WebteIzle, WFilmizle, YabanciDizi | 22 |
| [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | LoveFilm | 1 |

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
| AltiYuzAltmisAltiFilmIzle | feroxx/ilkel | 666filmizle.site | Site ölü, tekrar kontrol edilecek |
| FilmBip | ilkel | filmbip.com | Site ölü, tekrar kontrol edilecek |
| FullHDFilm | feroxx | fullhdfilm.org | Site ölü, tekrar kontrol edilecek |
| Filmatek | Kraptor123/Cs-Karma | filmatek.net | Site ölü, tekrar kontrol edilecek |
| Full4kizle | Kraptor123/Cs-Karma | plusizle.net | **status:0** — domain plusizle.org'a taşındı, build bekleniyor |
| DiziFilmORG | aytzey/cs-kraptor | dizifilm.org | **status:0** — çalışmıyor, repobuild gelince kontrol |
| DiziPal | aytzey/cs-kraptor | dizipal.im | **status:0** — çalışmıyor (DiziPalOriginal v84 + DiziPalOrijinal v45 çalışıyor) |
| DiziYo | aytzey/cs-kraptor | diziyo (DiziYo) | **status:0** — çalışmıyor (DiziYou v25 çalışıyor) |
| SetFilmIzle | aytzey/cs-kraptor | www.setfilmizle.uk | **status:0** — çalışmıyor, repobuild gelince kontrol |

> **Not (2026-08-28):** Yukarıdaki tablodan `DiziBox`, `DiziMom`, `Dizilla`, `WebteIzle` aynı build güncellendiğinde / yeni repolardan farklı domainlerle yeniden eklendiği için çıkarıldı: `aytzey/cs-kraptor`'da `DiziBox (dizibox.de)`, `DiziMom (dizimom.mom)`, `Dizilla (dizilla.to)`, `WebteIzle (webteizle1.xyz)` olarak `plugins.json`'a aktif eklendi ve çalışıyor. `SetFilmIzle` ise aytzey'de **status:0** ile yeniden eklenip bu tabloda izleniyor (repobuild gelince kontrol). Bu mantıkla tablo, sadece hala ölü ve yeni repo/build'de de çalışmayanlar için tutulur.
> **Not:** Bu liste güncellenebilir; aynı build güncellendiğinde veya yeni repolarda yeniden eklendiğinde çalışanlar ana listeye alınır, hala ölü olanlar burada bırakılır.

### Önemli Not
Repolar güncellendiğinde (yeni build yayınlandığında (GitHub uzerinden takip edilir)), bu listedeki ölü siteler otomatik olarak kontrol edilmeli ve çalışıyorsa tekrar eklenebilir.

## Silinen Eklentiler (delete-zone)
Bu eklentiler listeye **eklenmez**; yeniden ekleme kararı yalnızca kullanıcı verir. Listede NSFW (+18) hiç yer almadı; canlı yayın/maç eklentileri istenmedi. Bozuk eklentiler silinmez, `status:0` yapılır (bkz. Kurulum). "Site açılmıyor" gerekçesiyle silinenler **geri dönüşlüdür**: site düzelirse tekrar denenebilir.

**Anime/Asya içerikli (kullanıcı anime istemiyor):** AnimeciX, Animeler, Animely, AnimPow, Anizium, OnePaceTr, OpenAnime, TrAnimeIzle, TurkAnime, AsyaAnimeleri, AsyaFanatiklerim, AsyaWatch, DiziAsia, DiziAsya, DiziKorea, Koredizi, AnimeAV, AnimeWorld, AnimeYTX, Latanime, DramaDizilerim, Dramaizle, AsyaMinik
**Canlı yayın / maç (kullanıcı hiçbir halükarda istemiyor):** InatBox, NeonSpor, RecTV, Streamed, CricifyProvider, GinikoCanli, KickTR, Youtube
**Diğer ("kesinlikle istemiyorum" / kişisel tercih):** Filmmirasım, SeiCode, YTS, YeniKaynak, YesilCamTv, MirrorVerse, Vavoo, WebDramaTurkey, Syncler, Torrential, BelgeselX, CizgiMax, CizgiveDizi, KultFilmler, RareFilmm, TmdbProvider, EnglishW, TurkishW
**Türkçe/Türkiye filtresi (yabancı dil içerikli):** Esheaq, Krmzy, YoTurkish, DoramasLatinoX, Dubbindo, Flixlatam, Henaojara, Gnulahd, JPFilms, KissKH, LayarKaca, Movix, OK, Sokuja, Subsplease, Supercartoons, Wcoflix, Yablom, DocumentaryArea, Iwatchtheoffice, FullRaces, FootReplays, Filmzal

## Duplicate / Çakışan Eklentiler

Aynı isim/kökten farklı repo/build'lerde gelen ve yalnızca 1 tanesi listede tutulan eklentiler. Her gruptan sadece 1 tanesi `plugins.json`'da yer alır; diğer(leri) duplicate olarak eklenmez, repobuild güncellendiğinde kontrol edilir.

| Grup | Seçilen (Aktif) | Versiyon | Kaynak | Duplicate (Eklenmedi) | Duplicate Kaynak | Durum / Not |
|------|---------------------|----------|--------|------------------------|------------------|-------------|
| DiziLife | DiziLife | v58 | aytzey/cs-kraptor | DiziLife | blackhope v2 | Duplicate, aytzey tercih edildi |
| DiziMom | DiziMom | v61 | aytzey/cs-kraptor | DiziMom | blackhope v3 | Duplicate, aytzey tercih edildi |
| FilmEkseni | FilmEkseni | v50 | aytzey/cs-kraptor | FilmEkseni | blackhope v1 | Duplicate, aytzey tercih edildi |
| FilmHane | FilmHane | v43 | aytzey/cs-kraptor | FilmHane | blackhope v1 | Duplicate, aytzey tercih edildi |
| WebteIzle | WebteIzle | v53 | aytzey/cs-kraptor | Webteizle | blackhope v1 | Duplicate, aytzey tercih edildi |

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

Bu bölüm otomatik üretildi (2026-08-28) — tüm kaynak repolardaki 234 eklenti alfabetik, site domain ve durum bilgisiyle.
Toplam kayit: 234 (tum kaynaklardaki toplam eklenti sayisi, duplicate icerir)

| # | Eklenti | Kaynak | Site (domain) | Dil | Tur | v | Durum |
|---|---------|--------|---------------|-----|-----|---|-------|
| 1 | AltiYuzAltmisAltiFilmIzle | ilkelkullanici/ilkel-cloudstream | 666filmizle.site | tr | Movie | 1 | Eklenebilir / Incelenmeli |
| 2 | AnimeAV | Kraptor123/Cs-Karma | animeav1.com | mx | Anime | 17 | Istenmeyen (delete-zone) |
| 3 | AnimeciX | feroxx/Kekik-cloudstream | animecix.tv | tr | Anime | 21 | Istenmeyen (delete-zone) |
| 4 | AnimeciX | ilkelkullanici/ilkel-cloudstream | anm.cx | tr | Anime | 21 | Istenmeyen (delete-zone) |
| 5 | AnimeciX | aytzey/cs-kraptor | animecix.net | tr | Anime | 88 | Istenmeyen (delete-zone) |
| 6 | Animeler | aytzey/cs-kraptor | animeler.pw | tr | Anime | 41 | Istenmeyen (delete-zone) |
| 7 | Animely | aytzey/cs-kraptor | play-lh.googleusercontent.com | tr | Anime,AnimeMovie,OVA | 4 | Istenmeyen (delete-zone) |
| 8 | AnimeWorld | Kraptor123/Cs-Karma | www.animeworld.ac | it | Anime | 5 | Istenmeyen (delete-zone) |
| 9 | AnimeYTX | Kraptor123/Cs-Karma | animeyt.cc | mx | Anime | 7 | Istenmeyen (delete-zone) |
| 10 | AnimPow | aytzey/cs-kraptor | animpow.com | tr | Anime | 7 | Istenmeyen (delete-zone) |
| 11 | Anizium | aytzey/cs-kraptor | anizium.co | tr | AnimeMovie,Anime | 25 | Istenmeyen (delete-zone) |
| 12 | AsyaAnimeleri | feroxx/Kekik-cloudstream | asyaanimeleri.top | tr | Anime | 1 | Istenmeyen (delete-zone) |
| 13 | AsyaAnimeleri | ilkelkullanici/ilkel-cloudstream | asyaanimeleri.top | tr | Anime | 1 | Istenmeyen (delete-zone) |
| 14 | AsyaAnimeleri | aytzey/cs-kraptor | asyaanimeleri.top | tr | Anime | 24 | Istenmeyen (delete-zone) |
| 15 | AsyaFanatiklerim | aytzey/cs-kraptor | asyafanatiklerim.com | tr | AsianDrama | 22 | Istenmeyen (delete-zone) |
| 16 | AsyaMinik | aytzey/cs-kraptor | asyaminik.com | tr | AsianDrama | 17 | Istenmeyen (delete-zone) |
| 17 | AsyaWatch | aytzey/cs-kraptor | asyawatch.com | tr | AsianDrama | 41 | Istenmeyen (delete-zone) |
| 18 | BasketballReplays | Kraptor123/Cs-Karma | basketballreplays.net | en | Live | 4 | Eklenebilir / Incelenmeli |
| 19 | BelgeselX | feroxx/Kekik-cloudstream | belgeselx.com | tr | Documentary | 17 | Istenmeyen (delete-zone) |
| 20 | BelgeselX | ilkelkullanici/ilkel-cloudstream | belgeselx.com | tr | Documentary | 14 | Istenmeyen (delete-zone) |
| 21 | BelgeselX | aytzey/cs-kraptor | belgeselx.com | tr | Documentary | 41 | Istenmeyen (delete-zone) |
| 22 | CanliTV | feroxx/Kekik-cloudstream | tr.canlitv.team | tr | Live | 10 | Eklenebilir / Incelenmeli |
| 23 | CanliTV | ilkelkullanici/ilkel-cloudstream | tr.canlitv.team | tr | Live | 10 | Eklenebilir / Incelenmeli |
| 24 | CizgiMax | feroxx/Kekik-cloudstream | cizgimax.online | tr | Cartoon,Anime,Movie | 16 | Istenmeyen (delete-zone) |
| 25 | CizgiMax | ilkelkullanici/ilkel-cloudstream | cizgimax.online | tr | Cartoon | 8 | Istenmeyen (delete-zone) |
| 26 | CizgiMax | aytzey/cs-kraptor | cizgimax.online | tr | Cartoon | 36 | Istenmeyen (delete-zone) |
| 27 | CizgiveDizi | aytzey/cs-kraptor | cizgivedizi.com | tr | Cartoon | 50 | Istenmeyen (delete-zone) |
| 28 | Cloud-Sync | pltmustafa/plt-stream | img.icons8.com | tr | All | 12 | Eklenebilir / Incelenmeli |
| 29 | Ddizi | feroxx/Kekik-cloudstream | www.ddizi.im | tr | TvSeries | 22 | Sende Var |
| 30 | Ddizi | ilkelkullanici/ilkel-cloudstream | www.ddizi.im | tr | TvSeries | 22 | Sende Var |
| 31 | Ddizi | aytzey/cs-kraptor | www.ddizi.im | tr | TvSeries | 19 | Sende Var |
| 32 | Ddizi | kadircee/ozel-liste | www.ddizi.im | tr | TvSeries | 22 | Sende Var |
| 33 | DiziAsia | aytzey/cs-kraptor | diziasia.com | tr | AsianDrama | 20 | Istenmeyen (delete-zone) |
| 34 | DiziAsya | aytzey/cs-kraptor | www.diziasya.com | tr | AsianDrama | 27 | Istenmeyen (delete-zone) |
| 35 | DiziBox | feroxx/Kekik-cloudstream | www.dizibox.live | tr | TvSeries | 23 | Sende Var |
| 36 | DiziBox | ilkelkullanici/ilkel-cloudstream | www.dizibox.live | tr | TvSeries | 23 | Sende Var |
| 37 | DiziBox | aytzey/cs-kraptor | www.dizibox.de | tr | TvSeries | 37 | Sende Var |
| 38 | DiziBox | kadircee/ozel-liste | www.dizibox.de | tr | TvSeries | 37 | Sende Var |
| 39 | DiziFilmORG | aytzey/cs-kraptor | dizifilm.org | tr | Movie,TvSeries | 22 | Sende Var |
| 40 | DiziFilmORG | kadircee/ozel-liste | dizifilm.org | tr | Movie,TvSeries | 22 | Sende Var |
| 41 | Dizigecesi | aytzey/cs-kraptor | dizigecesi.com | tr | Movie,TvSeries | 4 | Sende Var |
| 42 | Dizigecesi | kadircee/ozel-liste | dizigecesi.com | tr | Movie,TvSeries | 4 | Sende Var |
| 43 | DiziKorea | feroxx/Kekik-cloudstream | dizikorea.vip | tr | AsianDrama | 41 | Istenmeyen (delete-zone) |
| 44 | DiziKorea | ilkelkullanici/ilkel-cloudstream | dizikorea.vip | tr | AsianDrama | 35 | Istenmeyen (delete-zone) |
| 45 | DiziKorea | aytzey/cs-kraptor | dizikorea.pw | tr | AsianDrama | 35 | Istenmeyen (delete-zone) |
| 46 | DiziLife | blackhope01/cloudstream-plugins | dizi73.life | tr | Movie,TvSeries | 2 | Sende Var |
| 47 | DiziLife | aytzey/cs-kraptor | dizi18.life | tr | Movie,TvSeries | 58 | Sende Var |
| 48 | DiziLife | kadircee/ozel-liste | dizi18.life | tr | Movie,TvSeries | 58 | Sende Var |
| 49 | Dizilla | feroxx/Kekik-cloudstream | dizilla.club | tr | TvSeries | 92 | Sende Var |
| 50 | Dizilla | ilkelkullanici/ilkel-cloudstream | dizilla.club | tr | TvSeries | 92 | Sende Var |
| 51 | Dizilla | aytzey/cs-kraptor | dizilla.to | tr | TvSeries | 111 | Sende Var |
| 52 | Dizilla | kadircee/ozel-liste | dizilla.to | tr | TvSeries | 111 | Sende Var |
| 53 | DiziMom | feroxx/Kekik-cloudstream | www.dizimom.plus | tr | TvSeries | 56 | Sende Var |
| 54 | DiziMom | ilkelkullanici/ilkel-cloudstream | www.dizimom.plus | tr | TvSeries | 43 | Sende Var |
| 55 | DiziMom | blackhope01/cloudstream-plugins | www.dizimom.surf | tr | Movie,TvSeries | 3 | Sende Var |
| 56 | DiziMom | aytzey/cs-kraptor | www.dizimom.mom | tr | TvSeries | 61 | Sende Var |
| 57 | DiziMom | kadircee/ozel-liste | www.dizimom.mom | tr | TvSeries | 61 | Sende Var |
| 58 | DiziPal | feroxx/Kekik-cloudstream | dizipal1563.com | tr | TvSeries,Movie | 104 | Sende Var |
| 59 | DiziPal | ilkelkullanici/ilkel-cloudstream | dizipal952.com | tr | TvSeries,Movie | 90 | Sende Var |
| 60 | DiziPal | aytzey/cs-kraptor | dizipal.im | tr | Movie,TvSeries | 89 | Sende Var |
| 61 | DiziPal | kadircee/ozel-liste | dizipal.im | tr | Movie,TvSeries | 89 | Sende Var |
| 62 | DiziPalOriginal | feroxx/Kekik-cloudstream | chessplyimages.cfd | tr | TvSeries,Movie | 84 | Sende Var |
| 63 | DiziPalOriginal | ilkelkullanici/ilkel-cloudstream | dizipal2036.com | tr | TvSeries,Movie | 66 | Sende Var |
| 64 | DiziPalOriginal | kadircee/ozel-liste | chessplyimages.cfd | tr | TvSeries,Movie | 84 | Sende Var |
| 65 | DiziPalOrijinal | aytzey/cs-kraptor | dizipal932.com | tr | TvSeries | 45 | Sende Var |
| 66 | DiziPalOrijinal | kadircee/ozel-liste | dizipal932.com | tr | TvSeries | 45 | Sende Var |
| 67 | Dizipod | aytzey/cs-kraptor | dizipod.com | tr | Movie,TvSeries,AsianDrama | 12 | Sende Var |
| 68 | Dizipod | kadircee/ozel-liste | dizipod.com | tr | Movie,TvSeries,AsianDrama | 12 | Sende Var |
| 69 | DiziYo | blackhope01/cloudstream-plugins | www.diziyo.so | tr | Movie,TvSeries | 1 | Sende Var |
| 70 | DiziYo | aytzey/cs-kraptor | i.imgur.com | tr | TvSeries | 74 | Sende Var |
| 71 | DiziYo | kadircee/ozel-liste | i.imgur.com | tr | TvSeries | 74 | Sende Var |
| 72 | DiziYou | feroxx/Kekik-cloudstream | cdn.diziyou.one | tr | TvSeries | 25 | Sende Var |
| 73 | DiziYou | ilkelkullanici/ilkel-cloudstream | cdn.diziyou6.com | tr | TvSeries | 25 | Sende Var |
| 74 | DiziYou | aytzey/cs-kraptor | www.diziyou.co | tr | TvSeries | 49 | Sende Var |
| 75 | DiziYou | kadircee/ozel-liste | cdn.diziyou.one | tr | TvSeries | 25 | Sende Var |
| 76 | DocumentaryArea | Kraptor123/Cs-Karma | documentaryarea.com | en | Documentary | 2 | Istenmeyen (delete-zone) |
| 77 | DoramasLatinoX | Kraptor123/Cs-Karma | doramaslatinox.com | mx | AsianDrama | 7 | Istenmeyen (delete-zone) |
| 78 | DramaDizilerim | blackhope01/cloudstream-plugins | dramadizilerim.com | tr | TvSeries | 2 | Istenmeyen (delete-zone) |
| 79 | DramaDizilerim | aytzey/cs-kraptor | dramadizilerim.com | tr | AsianDrama | 3 | Istenmeyen (delete-zone) |
| 80 | Dramaizle | Kraptor123/Cs-Karma | dramaizle.net | tr | AsianDrama | 11 | Istenmeyen (delete-zone) |
| 81 | Dubbindo | Kraptor123/Cs-Karma | www.dubbindo.site | id | AsianDrama | 2 | Istenmeyen (delete-zone) |
| 82 | EnglishW | ctnkyaumt/cstest | themoviedb.org | en | Movie,TvSeries | 10 | Istenmeyen (delete-zone) |
| 83 | Esheaq | Kraptor123/Cs-Karma | esk.onl | ar | Movie,TvSeries | 18 | Istenmeyen (delete-zone) |
| 84 | F1FullRaces | Kraptor123/Cs-Karma | i.imgur.com | en | Live | 10 | Eklenebilir / Incelenmeli |
| 85 | FilmBip | ilkelkullanici/ilkel-cloudstream | filmbip.com | tr | Movie | 19 | Eklenebilir / Incelenmeli |
| 86 | FilmEkseni | blackhope01/cloudstream-plugins | www.filmekseni.vip | tr | Movie,TvSeries | 1 | Sende Var |
| 87 | FilmEkseni | aytzey/cs-kraptor | filmekseni.net | tr | Movie | 50 | Sende Var |
| 88 | FilmEkseni | kadircee/ozel-liste | filmekseni.net | tr | Movie | 50 | Sende Var |
| 89 | FilmHane | blackhope01/cloudstream-plugins | www.filmhane.shop | tr | Movie,TvSeries | 1 | Sende Var |
| 90 | FilmHane | aytzey/cs-kraptor | encrypted-tbn1.gstatic.com | tr | Movie | 43 | Sende Var |
| 91 | FilmHane | kadircee/ozel-liste | encrypted-tbn1.gstatic.com | tr | Movie | 43 | Sende Var |
| 92 | FilmMakinesi | feroxx/Kekik-cloudstream | filmmakinesi.film | tr | Movie | 58 | Sende Var |
| 93 | FilmMakinesi | ilkelkullanici/ilkel-cloudstream | filmmakinesi.film | tr | Movie | 57 | Sende Var |
| 94 | FilmMakinesi | MRTDEVM/cloudstream-turkce | filmmakinesi.to | tr | Movie,TvSeries | 8 | Sende Var |
| 95 | FilmMakinesi | blackhope01/cloudstream-plugins | www.filmmakinesi.to | tr | Movie,TvSeries | 1 | Sende Var |
| 96 | FilmMakinesi | aytzey/cs-kraptor | filmmakinesi.tv | tr | Movie,TvSeries | 70 | Sende Var |
| 97 | FilmMakinesi | kadircee/ozel-liste | filmmakinesi.film | tr | Movie | 58 | Sende Var |
| 98 | Filmmirasım | Kraptor123/Cs-Karma | filmmirasim.ktb.gov.tr | tr | Documentary | 4 | Istenmeyen (delete-zone) |
| 99 | Filmmirasım | ctnkyaumt/cstest | filmmirasim.ktb.gov.tr | tr | Documentary | 4 | Istenmeyen (delete-zone) |
| 100 | FilmModu | feroxx/Kekik-cloudstream | www.filmmodu.one | tr | Movie | 19 | Sende Var |
| 101 | FilmModu | ilkelkullanici/ilkel-cloudstream | www.filmmodu17.com | tr | Movie | 19 | Sende Var |
| 102 | FilmModu | aytzey/cs-kraptor | www.filmmodu.one | tr | Movie | 41 | Sende Var |
| 103 | FilmModu | kadircee/ozel-liste | www.filmmodu.one | tr | Movie | 19 | Sende Var |
| 104 | Filmzal | aytzey/cs-kraptor | filmzal.me | az | Movie | 16 | Istenmeyen (delete-zone) |
| 105 | Flixlatam | Kraptor123/Cs-Karma | flixlatam.com | mx | Movie | 8 | Istenmeyen (delete-zone) |
| 106 | Footballia | Kraptor123/Cs-Karma | footballia.net | en | Live | 9 | Eklenebilir / Incelenmeli |
| 107 | FootReplays | Kraptor123/Cs-Karma | www.footreplays.com | en | Others | 1 | Istenmeyen (delete-zone) |
| 108 | Full4kizle | Kraptor123/Cs-Karma | plusizle.net | tr | Movie,AsianDrama | 20 | Sende Var |
| 109 | Full4kizle | kadircee/ozel-liste | plusizle.net | tr | Movie,AsianDrama | 20 | Sende Var |
| 110 | FullHDFilm | feroxx/Kekik-cloudstream | hdfilm.us | tr | Movie,TvSeries | 36 | Eklenebilir / Incelenmeli |
| 111 | FullHDFilm | ilkelkullanici/ilkel-cloudstream | fullhdfilm.us | tr | Movie,TvSeries | 36 | Eklenebilir / Incelenmeli |
| 112 | FullHDFilmizlesene | feroxx/Kekik-cloudstream | www.fullhdfilmizlesene.de | tr | Movie | 33 | Sende Var |
| 113 | FullHDFilmizlesene | ilkelkullanici/ilkel-cloudstream | www.fullhdfilmizlesene.de | tr | Movie | 29 | Sende Var |
| 114 | FullHDFilmizlesene | MRTDEVM/cloudstream-turkce | www.fullhdfilmizlesene.now | tr | Movie | 8 | Sende Var |
| 115 | FullHDFilmizlesene | aytzey/cs-kraptor | www.fullhdfilmizlesene.de | tr | Movie | 72 | Sende Var |
| 116 | FullHDFilmizlesene | kadircee/ozel-liste | www.fullhdfilmizlesene.now | tr | Movie | 8 | Sende Var |
| 117 | FullRaces | Kraptor123/Cs-Karma | fullraces.com | en | Movie | 6 | Istenmeyen (delete-zone) |
| 118 | GinikoCanli | aytzey/cs-kraptor | www.giniko.com | tr | Live | 15 | Istenmeyen (delete-zone) |
| 119 | Gnulahd | Kraptor123/Cs-Karma | ww3.gnulahd.nu | mx | Movie,Anime,TvSeries | 8 | Istenmeyen (delete-zone) |
| 120 | HDFilmCehennemi | feroxx/Kekik-cloudstream | hdfilmcehennemi.com | tr | Movie,TvSeries | 48 | Sende Var |
| 121 | HDFilmCehennemi | ilkelkullanici/ilkel-cloudstream | hdfilmcehennemi.com | tr | Movie,TvSeries | 47 | Sende Var |
| 122 | Hdfilmcehennemi | MRTDEVM/cloudstream-turkce | www.hdfilmcehennemi.nl | tr | Movie,TvSeries | 8 | Sende Var |
| 123 | HDFilmCehennemi | aytzey/cs-kraptor | hdfilmcehennemi.nl | tr | Movie,TvSeries | 97 | Sende Var |
| 124 | HDFilmCehennemi | kadircee/ozel-liste | hdfilmcehennemi.com | tr | Movie,TvSeries | 48 | Sende Var |
| 125 | HDFilmDelisi | feroxx/Kekik-cloudstream | hdfilmdelisi.com | tr | Movie,TvSeries | 1 | Sende Var |
| 126 | HDFilmDelisi | aytzey/cs-kraptor | hdfilmdelisi.one | tr | Movie | 18 | Sende Var |
| 127 | HDFilmDelisi | kadircee/ozel-liste | hdfilmdelisi.com | tr | Movie,TvSeries | 1 | Sende Var |
| 128 | HDFilmizle | aytzey/cs-kraptor | www.hdfilmizle.life | tr | Movie | 25 | Sende Var |
| 129 | HDFilmizle | kadircee/ozel-liste | www.hdfilmizle.life | tr | Movie | 25 | Sende Var |
| 130 | Henaojara | Kraptor123/Cs-Karma | ww1.henaojara.net | mx | Anime,AnimeMovie | 3 | Istenmeyen (delete-zone) |
| 131 | InatBox | feroxx/Kekik-cloudstream | blogger.googleusercontent.com | tr | Movie,TvSeries,Live | 30 | Istenmeyen (delete-zone) |
| 132 | InatBox | ilkelkullanici/ilkel-cloudstream | blogger.googleusercontent.com | tr | Movie,TvSeries,Live | 28 | Istenmeyen (delete-zone) |
| 133 | InatBox | aytzey/cs-kraptor | blogger.googleusercontent.com | tr | Movie,TvSeries,Live | 57 | Istenmeyen (delete-zone) |
| 134 | Iwatchtheoffice | Kraptor123/Cs-Karma | iwatchtheoffice.cc | en | Movie | 3 | Istenmeyen (delete-zone) |
| 135 | JetFilmizle | feroxx/Kekik-cloudstream | jetfilmizle.de | tr | Movie | 47 | Sende Var |
| 136 | JetFilmizle | ilkelkullanici/ilkel-cloudstream | jetfilmizle.de | tr | Movie | 47 | Sende Var |
| 137 | JetFilmizle | blackhope01/cloudstream-plugins | jetfilmizle.now | tr | Movie,TvSeries | 1 | Sende Var |
| 138 | JetFilmizle | aytzey/cs-kraptor | jetfilmizle.de | tr | Movie | 62 | Sende Var |
| 139 | JetFilmizle | kadircee/ozel-liste | jetfilmizle.de | tr | Movie | 47 | Sende Var |
| 140 | JPFilms | Kraptor123/Cs-Karma | jp-films.com | en | AsianDrama | 7 | Istenmeyen (delete-zone) |
| 141 | KickTR | aytzey/cs-kraptor | kick.com | tr | Live | 17 | Istenmeyen (delete-zone) |
| 142 | KissKH | Kraptor123/Cs-Karma | kisskh.id | en | AsianDrama | 4 | Istenmeyen (delete-zone) |
| 143 | KoreanTurk | ilkelkullanici/ilkel-cloudstream | koreanturk.com | tr | AsianDrama | 7 | Eklenebilir / Incelenmeli |
| 144 | KraptorPlus | aytzey/cs-kraptor | raw.githubusercontent.com | tr | TvSeries,Movie,Anime,Cartoon,AsianDrama,AnimeMovie | 86 | Sende Var |
| 145 | KraptorPlus | kadircee/ozel-liste | raw.githubusercontent.com | tr | TvSeries,Movie,Anime,Cartoon,AsianDrama,AnimeMovie | 86 | Sende Var |
| 146 | Krmzy | Kraptor123/Cs-Karma | krmzy.org | ar | TvSeries | 2 | Istenmeyen (delete-zone) |
| 147 | KultFilmler | feroxx/Kekik-cloudstream | kultfilmler.net | tr | Movie,TvSeries | 16 | Istenmeyen (delete-zone) |
| 148 | KultFilmler | ilkelkullanici/ilkel-cloudstream | kultfilmler.net | tr | Movie,TvSeries | 15 | Istenmeyen (delete-zone) |
| 149 | KultFilmler | aytzey/cs-kraptor | kultfilmler.net | tr | Movie,TvSeries | 31 | Istenmeyen (delete-zone) |
| 150 | Latanime | Kraptor123/Cs-Karma | latanime.org | mx | Movie | 8 | Istenmeyen (delete-zone) |
| 151 | LayarKaca | Kraptor123/Cs-Karma | tv12.lk21official.cc | id | Movie,TvSeries | 13 | Istenmeyen (delete-zone) |
| 152 | LoveFilm | blackhope01/cloudstream-plugins | lovefilmizle.net | tr | Movie,TvSeries | 1 | Sende Var |
| 153 | LoveFilm | kadircee/ozel-liste | lovefilmizle.net | tr | Movie,TvSeries | 1 | Sende Var |
| 154 | MirrorVerse | aytzey/cs-kraptor | raw.githubusercontent.com | tr | Movie,TvSeries | 38 | Istenmeyen (delete-zone) |
| 155 | Movix | Kraptor123/Cs-Karma | movix.fun | fr | Movie,TvSeries,Anime | 29 | Istenmeyen (delete-zone) |
| 156 | OK | Kraptor123/Cs-Karma | ok.ru | ru | Movie,TvSeries | 4 | Istenmeyen (delete-zone) |
| 157 | OnePaceTr | aytzey/cs-kraptor | www.onepacetr.net | tr | Anime | 13 | Istenmeyen (delete-zone) |
| 158 | OnShort | Kraptor123/Cs-Karma | onshort.net | en | TvSeries | 1 | Eklenebilir / Incelenmeli |
| 159 | OpenAnime | aytzey/cs-kraptor | openani.me | tr | Anime,AnimeMovie | 28 | Istenmeyen (delete-zone) |
| 160 | plt-party | pltmustafa/plt-stream | raw.githubusercontent.com | tr | All | 5 | Eklenebilir / Incelenmeli |
| 161 | plt-stream | pltmustafa/plt-stream | raw.githubusercontent.com | tr | TvSeries,Movie,Documentary | 47 | Sende Var |
| 162 | plt-stream | kadircee/ozel-liste | raw.githubusercontent.com | tr | TvSeries,Movie,Documentary | 47 | Sende Var |
| 163 | plt-tv | pltmustafa/plt-stream | raw.githubusercontent.com | tr | Live | 3 | Eklenebilir / Incelenmeli |
| 164 | RareFilmm | feroxx/Kekik-cloudstream | rarefilmm.com | en | Movie | 3 | Istenmeyen (delete-zone) |
| 165 | RareFilmm | ilkelkullanici/ilkel-cloudstream | rarefilmm.com | en | Movie | 3 | Istenmeyen (delete-zone) |
| 166 | RareFilmm | aytzey/cs-kraptor | rarefilmm.com | en | Movie | 20 | Istenmeyen (delete-zone) |
| 167 | RecTV | feroxx/Kekik-cloudstream | rectv.org.tr | tr | Movie,Live,TvSeries | 110 | Istenmeyen (delete-zone) |
| 168 | RecTV | ilkelkullanici/ilkel-cloudstream | rectvapp.com.tr | tr | Movie,Live,TvSeries | 103 | Istenmeyen (delete-zone) |
| 169 | RecTV | aytzey/cs-kraptor | rectvapk.cc | tr | Movie,Live,TvSeries | 43 | Istenmeyen (delete-zone) |
| 170 | SeiCode | aytzey/cs-kraptor | seicode.net | tr | Anime | 25 | Istenmeyen (delete-zone) |
| 171 | SelcukFlix | aytzey/cs-kraptor | selcukflix.com | tr | Movie,TvSeries | 49 | Sende Var |
| 172 | SelcukFlix | kadircee/ozel-liste | selcukflix.com | tr | Movie,TvSeries | 49 | Sende Var |
| 173 | SetFilmIzle | feroxx/Kekik-cloudstream | www.setfilmizle.uk | tr | Movie,TvSeries | 30 | Sende Var |
| 174 | SetFilmIzle | ilkelkullanici/ilkel-cloudstream | www.setfilmizle.nl | tr | Movie,TvSeries | 28 | Sende Var |
| 175 | SetFilmIzle | aytzey/cs-kraptor | www.setfilmizle.uk | tr | Movie | 42 | Sende Var |
| 176 | SetFilmIzle | kadircee/ozel-liste | www.setfilmizle.uk | tr | Movie | 42 | Sende Var |
| 177 | SezonlukDizi | feroxx/Kekik-cloudstream | sezonlukdizi6.com | tr | TvSeries | 9 | Sende Var |
| 178 | SezonlukDizi | ilkelkullanici/ilkel-cloudstream | sezonlukdizi6.com | tr | TvSeries | 8 | Sende Var |
| 179 | SezonlukDizi | blackhope01/cloudstream-plugins | sezonlukdizi.cc | tr | TvSeries | 1 | Sende Var |
| 180 | SezonlukDizi | aytzey/cs-kraptor | sezonlukdizi6.com | tr | TvSeries | 40 | Sende Var |
| 181 | SezonlukDizi | kadircee/ozel-liste | sezonlukdizi6.com | tr | TvSeries | 9 | Sende Var |
| 182 | SinemaCX | feroxx/Kekik-cloudstream | www.sinema.cx | tr | Movie | 24 | Sende Var |
| 183 | SinemaCX | ilkelkullanici/ilkel-cloudstream | www.sinema.cx | tr | Movie | 24 | Sende Var |
| 184 | SinemaCX | aytzey/cs-kraptor | www.sinema.gg | tr | Movie | 35 | Sende Var |
| 185 | SinemaCX | kadircee/ozel-liste | www.sinema.cx | tr | Movie | 24 | Sende Var |
| 186 | Sinewix | feroxx/Kekik-cloudstream | play-lh.googleusercontent.com | tr | Movie,TvSeries,Anime | 2 | Sende Var |
| 187 | Sinewix | ilkelkullanici/ilkel-cloudstream | play-lh.googleusercontent.com | tr | Movie,TvSeries,Anime | 2 | Sende Var |
| 188 | SineWix | aytzey/cs-kraptor | play-lh.googleusercontent.com | tr | Movie,TvSeries,Anime,AsianDrama,Cartoon | 33 | Sende Var |
| 189 | Sinewix | kadircee/ozel-liste | play-lh.googleusercontent.com | tr | Movie,TvSeries,Anime | 2 | Sende Var |
| 190 | Sinezy | aytzey/cs-kraptor | sinezy.fit | tr | Movie | 40 | Sende Var |
| 191 | Sinezy | kadircee/ozel-liste | sinezy.fit | tr | Movie | 40 | Sende Var |
| 192 | Sokuja | Kraptor123/Cs-Karma | x6.sokuja.uk | id | Anime,AnimeMovie | 3 | Istenmeyen (delete-zone) |
| 193 | Streamed | Kraptor123/Cs-Karma | streamed.pk | en | Live | 27 | Istenmeyen (delete-zone) |
| 194 | Subsplease | Kraptor123/Cs-Karma | subsplease.org | en | Anime | 4 | Istenmeyen (delete-zone) |
| 195 | Supercartoons | Kraptor123/Cs-Karma | i.imgur.com | en | Cartoon | 2 | Istenmeyen (delete-zone) |
| 196 | TLCtr | feroxx/Kekik-cloudstream | www.tlctv.com.tr | tr | Movie | 19 | Eklenebilir / Incelenmeli |
| 197 | TLCtr | ilkelkullanici/ilkel-cloudstream | www.tlctv.com.tr | tr | Movie | 19 | Eklenebilir / Incelenmeli |
| 198 | TmdbProvider | blackhope01/cloudstream-plugins | www.diziyo.so | tr | Movie,TvSeries | 1 | Istenmeyen (delete-zone) |
| 199 | TRanimaci | feroxx/Kekik-cloudstream | tranimaci.com | tr | Anime | 17 | Eklenebilir / Incelenmeli |
| 200 | TRanimaci | ilkelkullanici/ilkel-cloudstream | tranimaci.com | tr | Anime | 17 | Eklenebilir / Incelenmeli |
| 201 | TrAnimeIzle | aytzey/cs-kraptor | www.tranimeizle.io | tr | Anime | 15 | Istenmeyen (delete-zone) |
| 202 | TRasyalog | feroxx/Kekik-cloudstream | asyalog.co | tr | TvSeries | 65 | Eklenebilir / Incelenmeli |
| 203 | TRasyalog | ilkelkullanici/ilkel-cloudstream | asyalog.com | tr | TvSeries | 64 | Eklenebilir / Incelenmeli |
| 204 | TurkAnime | feroxx/Kekik-cloudstream | www.turkanime.co | tr | Anime | 14 | Istenmeyen (delete-zone) |
| 205 | TurkAnime | ilkelkullanici/ilkel-cloudstream | www.turkanime.co | tr | Anime | 14 | Istenmeyen (delete-zone) |
| 206 | TurkAnime | aytzey/cs-kraptor | www.turkanime.co | tr | Anime,AnimeMovie | 34 | Istenmeyen (delete-zone) |
| 207 | Turkdizileri | aytzey/cs-kraptor | i.imgur.com | tr | Movie | 33 | Sende Var |
| 208 | Turkdizileri | kadircee/ozel-liste | i.imgur.com | tr | Movie | 33 | Sende Var |
| 209 | TurkishW | ctnkyaumt/cstest | themoviedb.org | tr | Movie,TvSeries,Anime,Live | 9 | Istenmeyen (delete-zone) |
| 210 | TvDiziler | aytzey/cs-kraptor | tvdiziler.cc | tr | TvSeries | 18 | Sende Var |
| 211 | TvDiziler | kadircee/ozel-liste | tvdiziler.cc | tr | TvSeries | 18 | Sende Var |
| 212 | TVGarden | Kraptor123/Cs-Karma | tv.garden | en | Live | 11 | Eklenebilir / Incelenmeli |
| 213 | UgurFilm | ilkelkullanici/ilkel-cloudstream | ugurfilm7.com | tr | Movie | 13 | Eklenebilir / Incelenmeli |
| 214 | Watch2Movies | feroxx/Kekik-cloudstream | movies2watch.watch | en | Movie,TvSeries | 6 | Eklenebilir / Incelenmeli |
| 215 | Watch2Movies | ilkelkullanici/ilkel-cloudstream | watch2movies.net | en | Movie | 5 | Eklenebilir / Incelenmeli |
| 216 | WatchWrestling | Kraptor123/Cs-Karma | instapro.ac | en | Live | 17 | Eklenebilir / Incelenmeli |
| 217 | Wcoflix | Kraptor123/Cs-Karma | www.wcoflix.tv | en | Anime,Cartoon | 9 | Istenmeyen (delete-zone) |
| 218 | WebDramaTurkey | aytzey/cs-kraptor | webdramaturkey.org | tr | AsianDrama | 39 | Istenmeyen (delete-zone) |
| 219 | WebdramaTurkey2 | feroxx/Kekik-cloudstream | webdramaturkey2.com | tr | AsianDrama,Movie,Anime,Others | 1 | Eklenebilir / Incelenmeli |
| 220 | WebteIzle | feroxx/Kekik-cloudstream | webteizle3.xyz | tr | Movie | 20 | Sende Var |
| 221 | WebteIzle | ilkelkullanici/ilkel-cloudstream | webteizle2.com | tr | Movie | 17 | Sende Var |
| 222 | Webteizle | blackhope01/cloudstream-plugins | webteizle3.xyz | tr | Movie,TvSeries | 1 | Sende Var |
| 223 | WebteIzle | aytzey/cs-kraptor | webteizle1.xyz | tr | Movie | 53 | Sende Var |
| 224 | WebteIzle | kadircee/ozel-liste | webteizle1.xyz | tr | Movie | 53 | Sende Var |
| 225 | WFilmizle | aytzey/cs-kraptor | wfilmizle.bar | tr | Movie | 23 | Sende Var |
| 226 | WFilmizle | kadircee/ozel-liste | wfilmizle.bar | tr | Movie | 23 | Sende Var |
| 227 | YabanciDizi | aytzey/cs-kraptor | yabancidizi.so | tr | TvSeries | 18 | Sende Var |
| 228 | YabanciDizi | kadircee/ozel-liste | yabancidizi.so | tr | TvSeries | 18 | Sende Var |
| 229 | Yablom | Kraptor123/Cs-Karma | yablom.com | fr | Movie | 4 | Istenmeyen (delete-zone) |
| 230 | YeniKaynak | aytzey/cs-kraptor | www.yenikaynak.com | tr | Movie,TvSeries | 11 | Istenmeyen (delete-zone) |
| 231 | YesilCamTv | aytzey/cs-kraptor | yesilcamtv.com.tr | tr | Movie | 9 | Istenmeyen (delete-zone) |
| 232 | YoTurkish | Kraptor123/Cs-Karma | yoturkish.to | en | TvSeries | 4 | Istenmeyen (delete-zone) |
| 233 | Youtube | aytzey/cs-kraptor | www.youtube.com | tr | Movie,Live,Music,TvSeries | 39 | Istenmeyen (delete-zone) |
| 234 | YTS | aytzey/cs-kraptor | en.yts-official.mx | tr | Torrent | 42 | Istenmeyen (delete-zone) |


## Istenmeyenler (Delete-Zone) - 66 unique

| Eklenti | Kaynak Ornek | Site | Dil | Tur |
|---------|--------------|------|-----|-----|
| AnimeAV | Kraptor123/Cs-Karma | animeav1.com | mx | Anime |
| AnimeciX | feroxx/Kekik-cloudstream | animecix.tv | tr | Anime |
| Animeler | aytzey/cs-kraptor | animeler.pw | tr | Anime |
| Animely | aytzey/cs-kraptor | play-lh.googleusercontent.com | tr | Anime,AnimeMovie,OVA |
| AnimeWorld | Kraptor123/Cs-Karma | www.animeworld.ac | it | Anime |
| AnimeYTX | Kraptor123/Cs-Karma | animeyt.cc | mx | Anime |
| AnimPow | aytzey/cs-kraptor | animpow.com | tr | Anime |
| Anizium | aytzey/cs-kraptor | anizium.co | tr | AnimeMovie,Anime |
| AsyaAnimeleri | feroxx/Kekik-cloudstream | asyaanimeleri.top | tr | Anime |
| AsyaFanatiklerim | aytzey/cs-kraptor | asyafanatiklerim.com | tr | AsianDrama |
| AsyaMinik | aytzey/cs-kraptor | asyaminik.com | tr | AsianDrama |
| AsyaWatch | aytzey/cs-kraptor | asyawatch.com | tr | AsianDrama |
| BelgeselX | feroxx/Kekik-cloudstream | belgeselx.com | tr | Documentary |
| CizgiMax | feroxx/Kekik-cloudstream | cizgimax.online | tr | Cartoon,Anime,Movie |
| CizgiveDizi | aytzey/cs-kraptor | cizgivedizi.com | tr | Cartoon |
| DiziAsia | aytzey/cs-kraptor | diziasia.com | tr | AsianDrama |
| DiziAsya | aytzey/cs-kraptor | www.diziasya.com | tr | AsianDrama |
| DiziKorea | feroxx/Kekik-cloudstream | dizikorea.vip | tr | AsianDrama |
| DocumentaryArea | Kraptor123/Cs-Karma | documentaryarea.com | en | Documentary |
| DoramasLatinoX | Kraptor123/Cs-Karma | doramaslatinox.com | mx | AsianDrama |
| DramaDizilerim | blackhope01/cloudstream-plugins | dramadizilerim.com | tr | TvSeries |
| Dramaizle | Kraptor123/Cs-Karma | dramaizle.net | tr | AsianDrama |
| Dubbindo | Kraptor123/Cs-Karma | www.dubbindo.site | id | AsianDrama |
| EnglishW | ctnkyaumt/cstest | themoviedb.org | en | Movie,TvSeries |
| Esheaq | Kraptor123/Cs-Karma | esk.onl | ar | Movie,TvSeries |
| Filmmirasım | Kraptor123/Cs-Karma | filmmirasim.ktb.gov.tr | tr | Documentary |
| Filmzal | aytzey/cs-kraptor | filmzal.me | az | Movie |
| Flixlatam | Kraptor123/Cs-Karma | flixlatam.com | mx | Movie |
| FootReplays | Kraptor123/Cs-Karma | www.footreplays.com | en | Others |
| FullRaces | Kraptor123/Cs-Karma | fullraces.com | en | Movie |
| GinikoCanli | aytzey/cs-kraptor | www.giniko.com | tr | Live |
| Gnulahd | Kraptor123/Cs-Karma | ww3.gnulahd.nu | mx | Movie,Anime,TvSeries |
| Henaojara | Kraptor123/Cs-Karma | ww1.henaojara.net | mx | Anime,AnimeMovie |
| InatBox | feroxx/Kekik-cloudstream | blogger.googleusercontent.com | tr | Movie,TvSeries,Live |
| Iwatchtheoffice | Kraptor123/Cs-Karma | iwatchtheoffice.cc | en | Movie |
| JPFilms | Kraptor123/Cs-Karma | jp-films.com | en | AsianDrama |
| KickTR | aytzey/cs-kraptor | kick.com | tr | Live |
| KissKH | Kraptor123/Cs-Karma | kisskh.id | en | AsianDrama |
| Krmzy | Kraptor123/Cs-Karma | krmzy.org | ar | TvSeries |
| KultFilmler | feroxx/Kekik-cloudstream | kultfilmler.net | tr | Movie,TvSeries |
| Latanime | Kraptor123/Cs-Karma | latanime.org | mx | Movie |
| LayarKaca | Kraptor123/Cs-Karma | tv12.lk21official.cc | id | Movie,TvSeries |
| MirrorVerse | aytzey/cs-kraptor | raw.githubusercontent.com | tr | Movie,TvSeries |
| Movix | Kraptor123/Cs-Karma | movix.fun | fr | Movie,TvSeries,Anime |
| OK | Kraptor123/Cs-Karma | ok.ru | ru | Movie,TvSeries |
| OnePaceTr | aytzey/cs-kraptor | www.onepacetr.net | tr | Anime |
| OpenAnime | aytzey/cs-kraptor | openani.me | tr | Anime,AnimeMovie |
| RareFilmm | feroxx/Kekik-cloudstream | rarefilmm.com | en | Movie |
| RecTV | feroxx/Kekik-cloudstream | rectv.org.tr | tr | Movie,Live,TvSeries |
| SeiCode | aytzey/cs-kraptor | seicode.net | tr | Anime |
| Sokuja | Kraptor123/Cs-Karma | x6.sokuja.uk | id | Anime,AnimeMovie |
| Streamed | Kraptor123/Cs-Karma | streamed.pk | en | Live |
| Subsplease | Kraptor123/Cs-Karma | subsplease.org | en | Anime |
| Supercartoons | Kraptor123/Cs-Karma | i.imgur.com | en | Cartoon |
| TmdbProvider | blackhope01/cloudstream-plugins | www.diziyo.so | tr | Movie,TvSeries |
| TrAnimeIzle | aytzey/cs-kraptor | www.tranimeizle.io | tr | Anime |
| TurkAnime | feroxx/Kekik-cloudstream | www.turkanime.co | tr | Anime |
| TurkishW | ctnkyaumt/cstest | themoviedb.org | tr | Movie,TvSeries,Anime,Live |
| Wcoflix | Kraptor123/Cs-Karma | www.wcoflix.tv | en | Anime,Cartoon |
| WebDramaTurkey | aytzey/cs-kraptor | webdramaturkey.org | tr | AsianDrama |
| Yablom | Kraptor123/Cs-Karma | yablom.com | fr | Movie |
| YeniKaynak | aytzey/cs-kraptor | www.yenikaynak.com | tr | Movie,TvSeries |
| YesilCamTv | aytzey/cs-kraptor | yesilcamtv.com.tr | tr | Movie |
| YoTurkish | Kraptor123/Cs-Karma | yoturkish.to | en | TvSeries |
| Youtube | aytzey/cs-kraptor | www.youtube.com | tr | Movie,Live,Music,TvSeries |
| YTS | aytzey/cs-kraptor | en.yts-official.mx | tr | Torrent |


## Yasal Uyarı ve Sorumluluk Reddi (Disclaimer)
Bu depo kişisel arşivleme amacıyla oluşturulmuştur; hiçbir ticari amacı yoktur. Bu depo (ve GitHub sunucuları) hiçbir video, ses dosyası, medya veya telif hakkıyla korunan materyal barındırmaz, kopyalamaz veya dağıtmaz. Bu depo yalnızca internette herkese açık olarak paylaşılan üçüncü taraf eklentilerin (`.cs3`) doğrudan GitHub RAW adreslerini derleyen metin tabanlı bir JSON dizinidir ("Yalnızca Endeks"). Listelenen eklentilerin kodları, işleyişleri veya hangi web sitelerinden veri çektikleri üzerinde bu deponun hiçbir kontrolü, sahipliği veya sorumluluğu yoktur; tüm sorumluluk eklentilerin orijinal geliştiricilerine ve veriyi barındıran kaynak web sitelerine aittir. Bu depo yalnızca bağlantıları listeleyen bir köprü görevi gördüğü için telif hakkı ihlali iddialarının muhatabı değildir; içerik kaldırma talepleri (DMCA) doğrudan içerikleri sunan kaynak web sitelerine veya eklentilerin orijinal GitHub depolarına yapılmalıdır. Bu depo, 5846 sayılı Fikir ve Sanat Eserleri Kanunu ve 5651 sayılı Kanun kapsamında da eser barındırmaz, çoğaltmaz veya iletmez; yalnızca kamuya açık kaynaklardaki `.cs3` dosyalarına bağlantı sağlar. 5651 sayılı Kanunun 4. maddesinin ikinci fıkrası gereği içerik sağlayıcı, bağlantı sağladığı başkasına ait içerikten sorumlu değildir; ancak aynı maddenin istisnası saklıdır: sunuş biçiminden bağlantı verilen içeriğin benimsendiği ve kullanıcının o içeriğe ulaşmasının amaçlandığı açıkça belli ise sorumluluk doğabilir. Bu depo, listedeki hiçbir eklentiyi veya eklentilerin veri çektiği kaynakları benimsemez ve tavsiye etmez; liste salt teknik bir indekstir. Hak sahipleri 5651 sayılı Kanunun 9. maddesi uyarınca uyarı yöntemiyle bildirimde bulunursa ilgili bağlantı derhal kaldırılır.

This repository is created for personal archiving purposes and has no commercial intent. This repository does not host, store, copy, or distribute any video, audio, media files, or copyrighted material; it serves merely as a text-based JSON index containing direct links to third-party `.cs3` plugins already publicly available on the internet ("Index Only"). The owner of this repository does not develop, host, or control any of the listed plugins, their source code, operation, or the websites these plugins scrape; all liability lies strictly with the original plugin developers and the respective websites hosting the media. As this repository only provides a compilation of text-based URLs, it is not liable for copyright infringement; any DMCA takedown requests must be directed to the actual websites hosting the copyrighted content or to the original developers' repositories. Under Turkish law (FSEK No. 5846 and Law No. 5651), this repository does not host, reproduce, or communicate any work; it merely provides links to `.cs3` files publicly available on the internet. Under Article 4/2 of Law No. 5651, a content provider is not liable for third-party content to which it merely provides a link; however, the exception in that provision is reserved: liability may arise where the presentation clearly shows that the linked content is adopted and that users are intended to reach it. This repository does not adopt or recommend any of the listed plugins or the sources they use; the list is a purely technical index. If rights holders send a notice under Article 9 of Law No. 5651, the relevant link will be removed promptly.