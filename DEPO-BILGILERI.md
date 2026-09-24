# developer (ozel-liste)
Bu depo test CloudStream deposudur; yalnızca Türkçe film/dizi eklentilerini ve test seçtiği kaynakları barındırır. Canlı yayın, NSFW ve yabancı dil içerikli eklentiler kullanıcı tercihi gereği listeye alınmamıştır.

## Durum
- **Son doğrulama:** 2026-09-17 · katalog güncellendi; indirilebilir `.cs3` kayıtları hash/boyut doğrulanarak senkronize edilir. `status` dahil kaynak alanları Pure Mirror kuralıyla korunur.
- **Doğrulama kanıtı:** 2026-09-17 · 404 kaynak temizliği ve katalog/registry senkronu tamamlandı; `update.py --check`, `registry.py --check` ve `audit.py --check` ile doğrulandı.
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

## Depo Yapısı
```
ozel-liste/
├── repo.json            → CloudStream'in açtığı depo tanımı
├── plugins.json         → eklenti listesi (45 aktif eklenti)
├── registry.json        → makine-okur kayıt modeli (68 kaynak satırı; 45 aktif, 23 duplicate; Seçim ekseni; Pure Mirror)
├── registry.py          → model araçları (--sync / --check / --render [--write])
├── audit.py             → kaynak repoları tarih bazlı denetler (--check = rapor/varsayılan, --apply = yazar)
├── update.py            → kaynak depolardan güncel verileri senkronize eden script (--check / --purge dahil)
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
- `NivinCNC/CNCVerse-Cloud-Stream-Extension` — `CricifyProvider` (canlı spor) bu kaynaktan geliyordu; kullanıcı canlı spor istemediği için eklenti yok.
- `Kraptor123/Cs-Karma` — `Streamed` için eski kaldırma kararı kullanıcı istisnasıyla geçersiz kılındı; artık aktif ve canlı içerik istisnası olarak korunuyor.
- `Kraptor123/Cs-GizliKeyif` — tamamı +18 NSFW içerikliydi (108 kayıt; NSFW olmayan kayıt yok), hiç eklenmedi.
- `sarapcanagii/*` — `NeonSpor` (canlı) bu kaynaktan gelmişti; kullanıcı istemedi.
- `ByAyzen/AyzenCS3` — `Syncler`, `Torrential` bu kaynaktan geliyordu; kişisel tercihle silindi.
> Not: Kaynakların tamamı `raw.githubusercontent.com` üzerinden `builds/plugins.json` ve/veya tekil `.cs3` dosya adresleriyle çekildi; hiçbir eklenti kopyalanıp yeniden barındırılmadı, adresler kaynak repoya işaret eder.


## Kaynak Seçim Kriteri ve Tablo Bakımı

**1. Kaynak seçimi — SADECE TARİH esastır, versiyon kriter değil:**
- Per-eklenti tarih `git -C <repo> log -1 --format=%cd --date=short --all -- <Eklenti>` ile alınır; repo genel `pushed_at` değil. Aynı eklentinin birden fazla kaynaktan gelen kopyaları arasında en güncel tarihli kayıt otomatik tercih edilir; versiyon numarasının düşük/yüksek olması kararı etkilemez.
- Kaynak kararından önce `audit.py`, her kaynak reposunun bütün dallarını ve dal ağaçlarındaki tüm `.cs3` dosyalarını tarar. `builds` dışı bir dalda `.cs3` bulunursa `ALTERNATİF-DAL .cs3` olarak raporlanır; doğrulanmadan otomatik Aktif yapılmaz. Canonical manifest/artefakt çifti `builds` dalıdır.
- Manifestte kayıtlı her `.cs3` adresi de ayrıca HTTP erişilebilirlik kontrolünden geçer. Manifestte bulunup gerçek dosyası 404 olan kayıt havuza alınmaz; böylece manifest/artefakt ayrışması (ör. `plt-stream`) yanlışlıkla Aktif veya yeni kayıt olamaz.
- Kaynak manifestinde `status: 0` olan kayıtlar devre dışıdır: `plugins.json`'dan silinir, audit havuzuna alınmaz ve sonraki çalıştırmada yeniden eklenmez. Registry tablosunda yalnızca tarih geçmişi için Duplicate adayı olarak görünebilir.
- Örnek: `FilmMakinesi feroxx v58 (2026-08-23)` vs `blackhope01 v1 (2026-08-25)` — `blackhope01 v1` tarih olarak daha güncel olduğu için doğru şekilde tercih edildi; düşük versiyon yüksek versiyonu ezer ve bu beklenen davranıştır.

**1a. Eşit tarihli kaynaklar (tie-breaker) — OTOMATİK, SORU YOK:**
İki veya daha fazla kaynağın aynı güncelleme tarihine sahip olduğu durumlarda repo adına göre alfabetik sıralama yapılır ve HER ZAMAN ilk sıradaki kaynak otomatik seçilir (`audit.py` bu çözümü kendisi uygular; script durup sormaz).
Versiyon numarası bu tie-breaker'da kriter olarak kullanılmaz — ne düşük ne yüksek versiyon tercih nedeni sayılır.

**1b. Tüm dal taraması (2026-09-23):**
Dokuz kaynak repo ve mevcut tüm dalları (`builds` dahil) tarandı. `builds` dışı dallarda `.cs3` artefaktı bulunmadı; bu nedenle dal değişimiyle daha yeni bir kaynak gizlenmiyor. `ilkelkullanici/ilkel-cloudstream` GitHub API'de 404 olduğu için erişilemeyen kaynak olarak bırakıldı. `pltmustafa/plt-stream` içinde `builds/plugins.json` erişilebilir olsa da manifestteki `plt-stream.cs3` 404; `plt-tv.cs3` gerçek ve erişilebilir olduğu için yalnızca `plt-tv` değerlendirildi.

**2. Tablo bakımı — `Tüm Repolar` tüm karşılaştırılan adayları içerir:**
- Yeni adaylar için varsayılan filtre `language == tr` ve `tvTypes ⊆ {Movie, TvSeries, Documentary}` kuralıdır. Filtre dışı adaylar tabloya alınmaz; kalıcı olarak istenmeyen seçilenler Delete-Zone’da tutulur.
- **İstisna — paket (çoklu-kaynak) eklentileri:** `KraptorPlus`, `Sinewix`, `Dizipod` (ve Delete-Zone'da tutulan `Full4kizle`) kaynak metadata'sında `Anime/AsianDrama/Cartoon` etiketi taşır ama **bunlar anime/kategori eklentisi değildir** — bunlar yalnızca kullanıcı onaylı paket istisnalarıdır.
- `Site (domain)` her zaman `[domain](https://domain)` linkli olmalı (tıklanabilir).
- `kadircee/ozel-liste` kaynak değil derleme olduğu için `Tüm Repolar`'da yer almaz.
- `İstenmeyenler` metin + tablo aynı anda tutulmaz; tek tablo yeterlidir, `Silinen Eklentiler` metin listesi sadece not bırakır.
- **Yasaklı sayısı tek doğruluk kaynağıdır:** İstenmeyenler tablosundaki satır sayısı = `audit.py` çıktısındaki `yasakli sayisi` = **50** (2026-09-23). Üçü düzenli karşılaştırılır. Başlık (`## İstenmeyenler ...`) **kendi satırında** olmalıdır; tablo satırına yapıştırılırsa GitHub başlığı render etmez ve `audit.py` yasaklı listesini bulamaz → boş liste tespit edilip **`exit 2` ile durdurulur** (sessiz geçiş yok).

**3. Kayıt durumu — tek eksen (Seçim):**
Model yalnızca `Seçim` ekseninden oluşur: `Aktif` (yarışı kazandı, `plugins.json`'da) / `Duplicate` (kaybetti, dosyada yok) / `İstenmeyen` (hiç yarışa girmedi) (bkz. **Kayıt Durumu Modeli**). `status` bilgisi kaynağa bırakılmıştır — kaynak ne yayınlıyorsa (`1`, `0`, …) `update.py` ile birebir yansıtılır; bu depo site canlılığı takibi yapmaz.
- İkon domaininin ölü görünmesi tek başına karar nedeni değildir (ör. `SinemaCX`: ikon `sinema.cx` ölü görünebilir ama eklenti veriyi başka domainden çekiyor olabilir) — karar tarihe göre verilir.
- Kaynak ilerlediyse `update.py` ile senkronize et, `Bizim Tarih`'i eşitle; `status`'e dokunma, kaynak ne verdiyse o alınır.





## Tarih Takip Kuralı (tek kural)

Tablodaki her satırda iki tarih vardır: **Kaynak Tarih** (kaynak deponun `builds` branch'inde o `.cs3` dosyasına dokunan son commit'in tarihi) ve **Bizim Tarih** (bizim o kaynağı en son benimsediğimiz tarih). Bütün olay bu iki tarihin karşılaştırmasıdır:

- **Kaynak Tarih > Bizim Tarih** → kaynak ilerlemiş demektir. `update.py` ile senkronize et (`status` dahil kaynak ne yayınlıyorsa aynen alınır), sonra satırdaki `Bizim Tarih`'i `Kaynak Tarih`'e eşitle. Versiyon numarasına bakılmaz.
- **Kaynak Tarih == Bizim Tarih** → yapacak iş yok.

`verify.py` 2026-09-05'te kaldırıldı: ağ taraması yavaştı ve ürettiği uyarılar karara dönüşmüyordu. Doğruluk tarih takibine dayanır; `status` kaynağın yayınladığı değerdir, bu depoda manuel `status` takibi yapılmaz.

## Kayıt Durumu Modeli

Her kayıt tek eksene sahiptir:

- **Seçim:** `Aktif` (yarışı kazandı, `plugins.json`'da) / `Duplicate` (kaybetti, dosyada yok) / `İstenmeyen` (hiç yarışa girmedi).

| Seçim | Anlamı | plugins.json |
| Aktif | Kazanan kayıt | var (`status` kaynağın yayınladığı değer) |
| Duplicate | Yarışı kaybetti, dosyada yok | yok |
| İstenmeyen | Hiç değerlendirmeye alınmadı | yok |

**Kararlar (2026-09-16):** (A) Tarih çelişkileri kurala göre uygulanır; eşit tarihli tie'lar repo adı alfabetik ilk kaynak seçilerek otomatik çözülür; flip, hash/boyut doğrulaması gerektirdiği için script ile ayrı adımda yapılır. (B) Aynı normalize isim = aynı grup (mutlak). (C) `Bizim Tarih`, Duplicate satırlarda referans amaçlı dondurulur, tazelenmez. (D) Tablo üretilen bloktur; değişiklik `--sync` → `--render --write` akışıyla yapılır.

**Araçlar:** `python registry.py --sync` (tablolar + `plugins.json` → `registry.json`), `--check` (şema + küme + tarih; ihlalde exit 1), `--render [--write]` (tabloyu üretir). `Seçim` `plugins.json`'dan türetilir (dosyada olan = Aktif); grup başına en fazla 1 Aktif; Aktif kümesi `plugins.json` ile birebir zorunlu. Eklenti alanları (`status`, `version`, `fileSize`, `fileHash`, `description`, `authors`, `language`, `tvTypes`) kaynak `builds/plugins.json`'dan birebir yansıtılır (`update.py`).

## Kaynak Senkronizasyonu (update.py)
```bash
python update.py --check    # yazmadan sadece farkları raporlar (fark varsa exit 1)
python update.py            # farkları uygular, plugins.json'u günceller
```
Kaynak `builds/plugins.json` adresi, listedeki `.cs3` adresinden türetilir (`https://raw.githubusercontent.com/<owner>/<repo>/builds/<Isim>.cs3` → aynı klasördeki `plugins.json`). Senkronize edilen alanlar: `status, version, fileSize, fileHash, description, authors, language, tvTypes` (Pure Mirror — kaynak ne yayınlıyorsa aynen alınır). `iconUrl` bilinçli olarak senkronize **edilmez** — bu depo ikon adreslerini normalize eder (kaynaktaki `%size%` yer tutucuları sabit `sz=128`'e çevrilir) ve kaynak güncellemesi bu düzeltmeyi geri almasın.

> **Not:** Kaynak senkronu GitHub Actions ile otomatik çalışır (`.github/workflows/mirror.yml`: her gün 05:00 UTC ve `workflow_dispatch` ile manuel tetikleme). Akış: `update.py` → `registry.py --sync --render --write --check` → değişiklik varsa otomatik commit+push. Yerelde elle çalıştırmak da mümkündür. Kaynakta bulunamayan kayıt `[SILINDI]` olarak listeden düşer; kaynak manifesti 404 ise audit kaynağı atlar ve aktif katalogda kayıt bırakılmaz.

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
| plt-stream v47→v55 + DiziPalOriginal v84→v86 + DiziMom v56→v58 hash/boyut uyuşmazlığı (2026-09-05) | Kaynak repolar güncellenmiş; listedeki eski hash/boyut CloudStream’te hash mismatch veriyordu | update.py ile senkronlandı, jsDelivr purge 5/5 OK; Dizipod authors trim koruması geri yazıldı |
| 4 kapalı açıldı (DiziBox/DiziMom/DiziPal/FullHDFilmizlesene) + WebteIzle typo-kopyaya geçildi (2026-09-05) | Tarih Takip Kuralı: kaynaklar ilerledi, kullanıcı onayı ile açıldı/değiştirildi | 5 kayıt hash doğrulamalı senkronlandı (status 0→1 açılanlar dahil), jsDelivr purge 6/6 OK; UgurFilm yasaklıya eklendi |
| Full4kizle kaynağın plugins.json’ından düşmüş (.cs3 404) | Cs-Karma tarafında kayıt yok | Güncel kural gereği devre dışı/kayıp artefakt yayın listesine alınmıyor; yalnızca Delete-Zone geçmişi korunuyor |
| 18 eklenti senkronu (2026-09-15: aytzey 12 + feroxx 4 + blackhope 1 + plt 1) + DiziMom v4/Tablo v3 farki kapatildi | Kaynak repolar ilerlemis (aytzey 09-08 domain rewrite mass-bump, feroxx 09-15 rebuild, blackhope 09-07, plt 09-14); DiziFilmORG status:0 korunarak v23'e senkronlandi, Full4kizle kaynakta yok (ATLANDI, status:0 korunuyor) | update.py ile senkronlandi (Dizipod authors trim geri yazildi), jsDelivr purge 19/19 OK; DiziFilmORG kapali tutuldu, Bizim Tarih esitlendi |
| Webteizle-group audit FLIP vermedi (2026-09-05) | blackhope Webteizle (09-03) listedeki feroxx WebteIzle (09-02)’den yeniydi ama case-farki (Izle/izle) gruplari ayirdi + listedeki kaynak grupta olmayinca script sessiz gecti | Liste blackhope’a cevrildi (hash dogrulamali); audit.py’a ORPHAN raporu eklendi, sessiz gecis kapatildi |
| Devre dışı kaynakların temizlenmesi (2026-09-23) | `DiziGom` ve `DiziYo` MRC manifestinde `status: 0` yayınlıyordu | Devre dışı MRC kayıtları `plugins.json`'dan silindi; audit artık `status: 0` kayıtları havuza almadığı için geri eklemiyor. Aynı sitelerin erişilebilir, daha yeni NeO adayları tarih kuralıyla Aktif seçildi |
| Üretilen `Not` hücresindeki `|` (pipe) tabloyu bölüyordu (2026-09-15) | Not metnine ayraç olarak ` \| ` yazılınca markdown hücre bölünüyor, `--sync` idempotent olmuyordu | Ayraç `;` oldu, yazımda pipe kaçışı (`/`) eklendi; idempotency testiyle doğrulandı |
| 9 flip beklemede kalmıştı (2026-09-15 raporu) | Aktif kaynak, Tarih Takip Kuralı'na göre en yeni değildi (blackhope 09-07 tercih edilmişti); paralel oturum hazırlamış ama push etmemişti | 2026-09-16'da kaynak builds'ten hash/boyut/ZIP doğrulamalı uygulandı; 4 aytzey + 5 feroxx; Webteizle → WebteIzle CASE birleşmesi yapıldı; jsDelivr purge 10/10 OK |
| `## İstenmeyenler` başlığı tablo satırının içine yapışmıştı (2026-09-15) | Başlık kendi satırına taşınmadan 87. satırın son hücresine yazılmıştı; GitHub başlığı render etmiyor, satır 7→8 hücreye kayıyordu, delete-zone bölümünün görünür başlığı yoktu | Başlık kendi satırına alındı; `audit.py` yasaklı listesi artık satır içi eşleşme tesadüfüne değil gerçek başlığa dayanıyor |
| `audit.py` içindeki `guard` listesi hiç yazdırılmıyordu (2026-09-15) | Satır 138'de başlatılıp 173'te dolduruluyordu ama rapora basılmıyordu → "yasaklı, kaynakta görüldü ama elendi" sinyali sessizdi (ORPHAN'da kapatılan sessiz geçişin aynısı) | `=== YASAKLI-ELEME ===` bloğu rapora eklendi ve `--check` exit koşuluna dahil edildi |
| `audit.py` Türkçe karakterli `.cs3` adında `'ascii' codec can't encode character '\u0131'` veriyordu (Filmmirasım) | GitHub API adresi percent-encode edilmiyordu; urllib ASCII dışı karakteri taşıyamıyor → eklenti denetim havuzundan **sessizce** düşüyor, tarihi hiç takip edilmiyordu | `percent_encode()` (update.py ile aynı mantık) `api_json`'a eklendi + `import urllib.parse` |

### Önemli Not
Repolar güncellendiğinde (yeni build yayınlandığında (GitHub uzerinden takip edilir)), Kaynak Tarih ilerlediğinde satır Tarih Takip Kuralı'na göre güncellenir: `update.py` ile senkronize edilir (`status` dahil kaynak ne yayınlıyorsa aynen alınır), `Bizim Tarih` eşitlenir.

## Silinen Eklentiler (delete-zone)
Bu eklentiler listeye **eklenmez**; yeniden ekleme kararı yalnızca kullanıcı verir. Listede NSFW (+18) hiç yer almadı; canlı yayın/maç eklentileri istenmedi. Kural: Pure Mirror mantığı gereği, kaynak depo bir eklentiyi kaldırırsa (404), o eklenti bizim listemizden de update.py tarafından OTOMATİK OLARAK SİLİNİR. Bu durumda cihazınızda kurulu kalan bozuk eklentilerin manuel temizlenmesi gerekir. "Site açılmıyor" gerekçesiyle silinenler **geri dönüşlüdür**: site düzelirse tekrar denenebilir.

> **Not:** Ayrıntılı liste `İstenmeyenler (Delete-Zone)` tablosunda alfabetik olarak yer almaktadır.

## Güncelleme
Yeni bir değişiklik yapıldığında:
```bash
python update.py --check    # kaynak farkı var mı bak (exit 1 = var)
python registry.py --check  # model denetimi: sema + kume + tarih (exit 1 = ihlal ya da karar bekleyen)
python update.py                # gerekirse kaynak verilerini senkronize et (status dahil Pure Mirror)
# DEPO-BILGILERI.md: Kaynak Tarih'i ilerleyen satırlarda Bizim Tarih'i eşitle (Tarih Takip Kuralı)
git add plugins.json DEPO-BILGILERI.md registry.json registry.py
git -c user.name="kadircee" -c user.email="kadircee@users.noreply.github.com" \
    commit -m "plugins.json: aciklama"
git push
```
Push sonrası jsDelivr önbelleği için:
```
https://purge.jsdelivr.net/gh/kadircee/ozel-liste@main/plugins.json
```
CloudStream tarafında depo yenilendiğinde yeni liste otomatik çekilir. Kaynak senkronu her gün otomatik koşar (`.github/workflows/mirror.yml`); acil durumda yerelde **elle** de çalıştırılabilir (`python update.py`, ardından `registry.py --sync --render --write --check`). Güncelleme öncesi `update.py --check` ile kontrol etmek iyi alışkanlıktır.

## Tüm Repolar - Alfabetik Liste

Bu bölüm 2026-09-23 tarihinde `registry.json` ve `plugins.json` üzerinden yeniden oluşturuldu. Liste, aktif ve duplicate kaynakları birlikte gösterir; 404 kaynak kayıtları katalogdan çıkarılmıştır.

Aynı normalize ada sahip kayıtlar tek grup olarak değerlendirilir. En güncel kaynak `Aktif`, diğer kaynaklar `Duplicate` olarak gösterilir. `status` alanı kaynak manifestinden Pure Mirror kuralıyla alınır.

Toplam satır: 68 · Aktif: 45 · Duplicate: 23.

<!-- KAYIT-DURUMU:OTOMATIK-BASLANGIC -->
| # | Eklenti | Kaynak | Site (domain) | v | Kaynak Tarih | Bizim Tarih | Seçim | Not |
|---|---|---|---|---|---|---|---|---|
| 1 | Ddizi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [ddizi](https://ddizi.site) | 22 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 2 | DDizi | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [ddizi](https://ddizi.site) | 1 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 3 | DiziBox | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizibox](https://dizibox.site) | 23 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 4 | DiziBox | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [dizibox](https://dizibox.site) | 8 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 5 | DiziGom | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [dizigom.site](https://dizigom.site) | 3 | 2026-09-16 | 2026-09-16 | Duplicate |  |
| 6 | DiziGom | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [dizigom.site](https://dizigom.site) | 1 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 7 | DiziLife | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [dizilife](https://dizilife.site) | 2 | 2026-09-16 | 2026-09-16 | Duplicate |  |
| 8 | DiziLife | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [dizilife.site](https://dizilife.site) | 1 | 2026-09-17 | 2026-09-17 | Aktif |  |
| 9 | Dizilla | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizilla](https://dizilla.site) | 92 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 10 | Dizilla | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [dizilla](https://dizilla.site) | 10 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 11 | DiziMom | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizimom](https://dizimom.site) | 58 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 12 | DiziMom | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [dizimom](https://dizimom.site) | 4 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 13 | DiziPal | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizipal](https://dizipal.site) | 108 | 2026-09-16 | 2026-09-16 | Aktif |  |
| 14 | DiziPal1578 | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [dizipal1578.site](https://dizipal1578.site) | 1 | 2026-08-30 | 2026-08-30 | Aktif |  |
| 15 | DiziPal2121 | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [dizipal2121.site](https://dizipal2121.site) | 1 | 2026-08-30 | 2026-08-30 | Aktif |  |
| 16 | DiziPalOriginal | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizipaloriginal](https://dizipaloriginal.site) | 92 | 2026-09-16 | 2026-09-16 | Aktif |  |
| 17 | DiziPalOrijinal | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [dizipalorijinal.site](https://dizipalorijinal.site) | 4 | 2026-09-16 | 2026-09-16 | Aktif |  |
| 18 | DiziPod | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizipod](https://dizipod.site) | 3 | 2026-09-16 | 2026-09-16 | Aktif |  |
| 19 | DiziWatch | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [diziwatch.site](https://diziwatch.site) | 3 | 2026-09-15 | 2026-09-15 | Duplicate |  |
| 20 | DiziYo | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [diziyo](https://diziyo.site) | 1 | 2026-09-16 | 2026-09-16 | Duplicate |  |
| 21 | DiziYo | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [diziyo.site](https://diziyo.site) | 5 | 2026-09-17 | 2026-09-17 | Duplicate |  |
| 22 | Diziyo | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [diziyo.site](https://diziyo.site) | 1 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 23 | DiziYou | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [diziyou](https://diziyou.site) | 26 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 24 | DiziYou | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [diziyou](https://diziyou.site) | 1 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 25 | FilmEkseni | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [filmekseni](https://filmekseni.site) | 1 | 2026-09-16 | 2026-09-16 | Duplicate |  |
| 26 | FilmEkseni | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [filmekseni.site](https://filmekseni.site) | 1 | 2026-09-17 | 2026-09-17 | Aktif |  |
| 27 | FilmHane | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [filmhane](https://filmhane.site) | 1 | 2026-09-16 | 2026-09-16 | Aktif |  |
| 28 | FilmIzyon | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [filmizyon.site](https://filmizyon.site) | 2 | 2026-09-15 | 2026-09-15 | Aktif |  |
| 29 | FilmMakinesi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [filmmakinesi](https://filmmakinesi.site) | 59 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 30 | FilmMakinesi | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [filmmakinesi](https://filmmakinesi.site) | 5 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 31 | FilmModu | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [filmmodu](https://filmmodu.site) | 19 | 2026-09-16 | 2026-09-16 | Aktif |  |
| 32 | FullHDFilm | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [fullhdfilm](https://fullhdfilm.site) | 36 | 2026-09-16 | 2026-09-16 | Aktif |  |
| 33 | FullHDFilmizlesene | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [fullhdfilmizlesene](https://fullhdfilmizlesene.site) | 33 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 34 | FullHDFilmizlesene | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [fullhdfilmizlesene](https://fullhdfilmizlesene.site) | 1 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 35 | HDFilmCehennemi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [hdfilmcehennemi](https://hdfilmcehennemi.site) | 48 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 36 | HDFilmCehennemi | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [hdfilmcehennemi](https://hdfilmcehennemi.site) | 8 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 37 | HdFilmCehennemi2 | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [hdfilmcehennemi2.site](https://hdfilmcehennemi2.site) | 2 | 2026-09-16 | 2026-09-16 | Aktif |  |
| 38 | HDFilmDelisi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [hdfilmdelisi](https://hdfilmdelisi.site) | 1 | 2026-09-16 | 2026-09-16 | Aktif |  |
| 39 | HDFilmDiziIzle | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [hdfilmdiziizle.site](https://hdfilmdiziizle.site) | 1 | 2026-08-30 | 2026-08-30 | Aktif |  |
| 40 | HDFilmIzle | [Ripplay/cloudstream-repo](https://github.com/Ripplay/cloudstream-repo) | [hdfilmizle.site](https://hdfilmizle.site) | 8 | 2026-08-24 | 2026-08-24 | Duplicate |  |
| 41 | HDFilmizle | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [hdfilmizle.site](https://hdfilmizle.site) | 1 | 2026-08-30 | 2026-08-30 | Aktif |  |
| 42 | InatBox | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [inatbox.site](https://inatbox.site) | 30 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 43 | InatBox | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [inatbox.site](https://inatbox.site) | 2 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 44 | JetFilmizle | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [jetfilmizle](https://jetfilmizle.site) | 47 | 2026-09-16 | 2026-09-16 | Aktif |  |
| 45 | LoveFilm | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [lovefilm](https://lovefilm.site) | 1 | 2026-09-16 | 2026-09-16 | Duplicate |  |
| 46 | LoveFilm | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [lovefilm.site](https://lovefilm.site) | 2 | 2026-09-17 | 2026-09-17 | Aktif |  |
| 47 | OwnedSites | [Ripplay/cloudstream-repo](https://github.com/Ripplay/cloudstream-repo) | [dizibal.com](https://dizibal.com) | 2 | 2026-08-24 | 2026-08-24 | Aktif | Paket sağlayıcı: TrDiziİzle, DiziBal, DiziRella, DiziBol, FilmIzzle, LiderFilmİzle ve DiziFilmİzle |
| 48 | plt-stream | [pltmustafa/plt-stream](https://github.com/pltmustafa/plt-stream) | [plt-stream](https://plt-stream.site) | 58 | 2026-09-16 | 2026-09-16 | Duplicate |  |
| 49 | plt-tv | [pltmustafa/plt-stream](https://github.com/pltmustafa/plt-stream) | [plt-tv](https://github.com/pltmustafa/plt-stream) | 5 | 2026-09-21 | 2026-09-21 | Aktif | M3U/M3U8 çalma listeleri ve canlı TV oynatıcı |
| 50 | SelcukFlix | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [selcukflix](https://selcukflix.site) | 2 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 51 | SelcukFlix | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [selcukflix](https://selcukflix.site) | 2 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 52 | SetFilmIzle | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [setfilmizle](https://setfilmizle.site) | 30 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 53 | SetFilmIzle | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [setfilmizle](https://setfilmizle.site) | 3 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 54 | SezonlukDizi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [sezonlukdizi](https://sezonlukdizi.site) | 9 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 55 | SezonlukDizi | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [sezonlukdizi](https://sezonlukdizi.site) | 1 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 56 | Sinefy | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [sinefy.site](https://sinefy.site) | 1 | 2026-09-15 | 2026-09-15 | Aktif |  |
| 57 | SinemaCX | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [sinemacx](https://sinemacx.site) | 24 | 2026-09-16 | 2026-09-16 | Aktif |  |
| 58 | Sinewix | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [sinewix](https://sinewix.site) | 2 | 2026-09-16 | 2026-09-16 | Aktif |  |
| 59 | Sinezy | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [sinezy.site](https://sinezy.site) | 3 | 2026-09-15 | 2026-09-15 | Aktif |  |
| 60 | Streamed | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [streamed.site](https://streamed.site) | 1 | 2026-09-17 | 2026-09-17 | Aktif |  |
| 61 | TrDiziIzle | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [trdiziizle.site](https://trdiziizle.site) | 1 | 2026-08-30 | 2026-08-30 | Aktif |  |
| 62 | TvDiziler | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [tvdiziler.site](https://tvdiziler.site) | 2 | 2026-09-15 | 2026-09-15 | Duplicate |  |
| 63 | TvDiziler | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [tvdiziler.site](https://tvdiziler.site) | 1 | 2026-09-22 | 2026-09-22 | Aktif |  |
| 64 | UltraFilmizle | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [ultrafilmizle.org](https://ultrafilmizle.org) | 12 | 2026-09-20 | 2026-09-20 | Aktif |  |
| 65 | Webteizle | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [webteizle](https://webteizle.site) | 1 | 2026-09-16 | 2026-09-16 | Duplicate |  |
| 66 | WebteIzle | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [webteizle](https://webteizle.site) | 21 | 2026-09-16 | 2026-09-16 | Aktif |  |
| 67 | YabanciDizi | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [yabancidizi.site](https://yabancidizi.site) | 2 | 2026-09-15 | 2026-09-15 | Duplicate |  |
| 68 | YabanciDizi | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [yabancidizi.site](https://yabancidizi.site) | 1 | 2026-09-22 | 2026-09-22 | Aktif |  |
<!-- KAYIT-DURUMU:OTOMATIK-SON -->

## İstenmeyenler (Delete-Zone) - 50 unique

| Eklenti | Kaynak Ornek | Site | Dil | Tur |
|---------|--------------|------|-----|-----|
| 🟥 AnimeAV | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [animeav1.com](https://animeav1.com) | mx | Anime |
| 🟥 AnimeciX | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [animecix.tv](https://animecix.tv) | tr | Anime |
| 🟥 AnimeWorld | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [www.animeworld.ac](https://www.animeworld.ac) | it | Anime |
| 🟥 AnimeYTX | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [animeyt.cc](https://animeyt.cc) | mx | Anime |
| 🟥 AsyaAnimeleri | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [asyaanimeleri.top](https://asyaanimeleri.top) | tr | Anime |
| 🟥 BelgeselX | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [belgeselx.com](https://belgeselx.com) | tr | Documentary |
| 🟥 CizgiMax | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [cizgimax.online](https://cizgimax.online) | tr | Cartoon,Anime,Movie |
| 🟥 DiziKorea | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizikorea.vip](https://dizikorea.vip) | tr | AsianDrama |
| 🟥 DocumentaryArea | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [documentaryarea.com](https://documentaryarea.com) | en | Documentary |
| 🟥 DoramasLatinoX | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [doramaslatinox.com](https://doramaslatinox.com) | mx | AsianDrama |
| 🟥 DramaDizilerim | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [dramadizilerim.com](https://dramadizilerim.com) | tr | TvSeries |
| 🟥 Dramaizle | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [dramaizle.net](https://dramaizle.net) | tr | AsianDrama |
| 🟥 Dubbindo | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [www.dubbindo.site](https://www.dubbindo.site) | id | AsianDrama |
| 🟥 EnglishW | [ctnkyaumt/cstest](https://github.com/ctnkyaumt/cstest) | [themoviedb.org](https://themoviedb.org) | en | Movie,TvSeries |
| 🟥 Esheaq | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [esk.onl](https://esk.onl) | ar | Movie,TvSeries |
| 🟥 Filmmirasım | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [filmmirasim.ktb.gov.tr](https://filmmirasim.ktb.gov.tr) | tr | Documentary |
| 🟥 Flixlatam | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [flixlatam.com](https://flixlatam.com) | mx | Movie |
| 🟥 FootReplays | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [www.footreplays.com](https://www.footreplays.com) | en | Others |
| 🟥 FullRaces | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [fullraces.com](https://fullraces.com) | en | Movie |
| 🟥 Gnulahd | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [ww3.gnulahd.nu](https://ww3.gnulahd.nu) | mx | Movie,Anime,TvSeries |
| 🟥 Henaojara | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [ww1.henaojara.net](https://ww1.henaojara.net) | mx | Anime,AnimeMovie |
| 🟥 Iwatchtheoffice | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [iwatchtheoffice.cc](https://iwatchtheoffice.cc) | en | Movie |
| 🟥 JPFilms | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [jp-films.com](https://jp-films.com) | en | AsianDrama |
| 🟥 KissKH | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [kisskh.id](https://kisskh.id) | en | AsianDrama |
| 🟥 Krmzy | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [krmzy.org](https://krmzy.org) | ar | TvSeries |
| 🟥 KultFilmler | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [kultfilmler.net](https://kultfilmler.net) | tr | Movie,TvSeries |
| 🟥 Latanime | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [latanime.org](https://latanime.org) | mx | Movie |
| 🟥 LayarKaca | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [tv12.lk21official.cc](https://tv12.lk21official.cc) | id | Movie,TvSeries |
| 🟥 Movix | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [movix.fun](https://movix.fun) | fr | Movie,TvSeries,Anime |
| 🟥 OK | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [ok.ru](https://ok.ru) | ru | Movie,TvSeries |
| 🟥 RareFilmm | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [rarefilmm.com](https://rarefilmm.com) | en | Movie |
| 🟥 RecTV | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [rectv.org.tr](https://rectv.org.tr) | tr | Movie,Live,TvSeries |
| 🟥 Sokuja | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [x6.sokuja.uk](https://x6.sokuja.uk) | id | Anime,AnimeMovie |
| 🟥 Startv | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [startv](https://startv.site) | tr | Movie |
| 🟥 Subsplease | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [subsplease.org](https://subsplease.org) | en | Anime |
| 🟥 Supercartoons | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [i.imgur.com](https://i.imgur.com) | en | Cartoon |
| 🟥 TLCtr | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [tlctv.com.tr](https://tlctv.com.tr) | tr | Movie |
| 🟥 TRasyalog | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [asyalog.co](https://asyalog.co) | tr | TvSeries |
| 🟥 TmdbProvider | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [www.diziyo.so](https://www.diziyo.so) | tr | Movie,TvSeries |
| 🟥 TurkAnime | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [www.turkanime.co](https://www.turkanime.co) | tr | Anime |
| 🟥 TurkishW | [ctnkyaumt/cstest](https://github.com/ctnkyaumt/cstest) | [themoviedb.org](https://themoviedb.org) | tr | Movie,TvSeries,Anime,Live |
| 🟥 UgurFilm | [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | [ugurfilm7.com](https://ugurfilm7.com) | tr | Movie |
| 🟥 Wcoflix | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [www.wcoflix.tv](https://www.wcoflix.tv) | en | Anime,Cartoon |
| 🟥 Yablom | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [yablom.com](https://yablom.com) | fr | Movie |
| 🟥 YoTurkish | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [yoturkish.to](https://yoturkish.to) | en | TvSeries |
| 🟥 KoreFilmizle | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [korefilmizle.com](https://korefilmizle.com) | tr | Movie,TvSeries |
| 🟥 YesilCamTv | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [yesilcamtv.com.tr](https://yesilcamtv.com.tr) | tr | Movie |
| 🟥 AsyaWatch | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [asyawatch.com](https://asyawatch.com) | tr | AsianDrama |
| 🟥 Filmzal | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [filmzal.me](https://filmzal.me) | az | Movie |
| 🟥 WebDramaTurkey | [neoser1984/cloudstream-extensions](https://github.com/neoser1984/cloudstream-extensions) | [webdramaturkey.org](https://webdramaturkey.org) | tr | AsianDrama |
## Yasal Uyarı ve Sorumluluk Reddi (Disclaimer)
Bu depo kişisel arşivleme amacıyla oluşturulmuştur; hiçbir ticari amacı yoktur. Bu depo (ve GitHub sunucuları) hiçbir video, ses dosyası, medya veya telif hakkıyla korunan materyal barındırmaz, kopyalamaz veya dağıtmaz. Bu depo yalnızca internette herkese açık olarak paylaşılan üçüncü taraf eklentilerin (`.cs3`) doğrudan GitHub RAW adreslerini derleyen metin tabanlı bir JSON dizinidir ("Yalnızca Endeks"). Listelenen eklentilerin kodları, işleyişleri veya hangi web sitelerinden veri çektikleri üzerinde bu deponun hiçbir kontrolü, sahipliği veya sorumluluğu yoktur; tüm sorumluluk eklentilerin orijinal geliştiricilerine ve veriyi barındıran kaynak web sitelerine aittir. Bu depo yalnızca bağlantıları listeleyen bir köprü görevi gördüğü için telif hakkı ihlali iddialarının muhatabı değildir; içerik kaldırma talepleri (DMCA) doğrudan içerikleri sunan kaynak web sitelerine veya eklentilerin orijinal GitHub depolarına yapılmalıdır. Bu depo, 5846 sayılı Fikir ve Sanat Eserleri Kanunu ve 5651 sayılı Kanun kapsamında da eser barındırmaz, çoğaltmaz veya iletmez; yalnızca kamuya açık kaynaklardaki `.cs3` dosyalarına bağlantı sağlar. 5651 sayılı Kanunun 4. maddesinin ikinci fıkrası gereği içerik sağlayıcı, bağlantı sağladığı başkasına ait içerikten sorumlu değildir; ancak aynı maddenin istisnası saklıdır: sunuş biçiminden bağlantı verilen içeriğin benimsendiği ve kullanıcının o içeriğe ulaşmasının amaçlandığı açıkça belli ise sorumluluk doğabilir. Bu depo, listedeki hiçbir eklentiyi veya eklentilerin veri çektiği kaynakları benimsemez ve tavsiye etmez; liste salt teknik bir indekstir. Hak sahipleri 5651 sayılı Kanunun 9. maddesi uyarınca uyarı yöntemiyle bildirimde bulunursa ilgili bağlantı derhal kaldırılır.

This repository is created for personal archiving purposes and has no commercial intent. This repository does not host, store, copy, or distribute any video, audio, media files, or copyrighted material; it serves merely as a text-based JSON index containing direct links to third-party `.cs3` plugins already publicly available on the internet ("Index Only"). The owner of this repository does not develop, host, or control any of the listed plugins, their source code, operation, or the websites these plugins scrape; all liability lies strictly with the original plugin developers and the respective websites hosting the media. As this repository only provides a compilation of text-based URLs, it is not liable for copyright infringement; any DMCA takedown requests must be directed to the actual websites hosting the copyrighted content or to the original developers' repositories. Under Turkish law (FSEK No. 5846 and Law No. 5651), this repository does not host, reproduce, or communicate any work; it merely provides links to `.cs3` files publicly available on the internet. Under Article 4/2 of Law No. 5651, a content provider is not liable for third-party content to which it merely provides a link; however, the exception in that provision is reserved: liability may arise where the presentation clearly shows that the linked content is adopted and that users are intended to reach it. This repository does not adopt or recommend any of the listed plugins or the sources they use; the list is a purely technical index. If rights holders send a notice under Article 9 of Law No. 5651, the relevant link will be removed promptly
