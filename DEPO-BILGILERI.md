# developer (ozel-liste)
Bu depo test CloudStream deposudur; yalnÄ±zca TÃ¼rkÃ§e film/dizi eklentilerini ve test seÃ§tiÄŸi kaynaklarÄ± barÄ±ndÄ±rÄ±r. CanlÄ± yayÄ±n, NSFW ve yabancÄ± dil iÃ§erikli eklentiler kullanÄ±cÄ± tercihi gereÄŸi listeye alÄ±nmamÄ±ÅŸtÄ±r.

## Durum
- **Son doÄŸrulama:** 2026-08-22 Â· **16 eklenti** (12 aÃ§Ä±k, 4 devre dÄ±ÅŸÄ±; indirilebilir, hash/boyut doÄŸrulanmÄ±ÅŸ)
- **Kural:** bozuk eklenti silinmez, `status:0` yapÄ±lÄ±r (bkz. Kurulum)
- **Delete-zone:** silinen eklentiler yeniden eklenmez (bkz. Silinen Eklentiler)

## Kurulum
CloudStream â†’ Ayarlar â†’ UzantÄ±lar â†’ Depo Ekle:
```
https://raw.githubusercontent.com/kadircee/ozel-liste/main/repo.json
```
**Tek tÄ±kla kurulum (derin link):** CloudStream kurulu bir cihazda aÅŸaÄŸÄ±daki baÄŸlantÄ±ya tÄ±klanÄ±nca depo otomatik eklenir (`cloudstreamrepo://` ÅŸemasÄ± uygulama tarafÄ±ndan Ã§Ã¶zÃ¼lÃ¼r):
```
cloudstreamrepo://raw.githubusercontent.com/kadircee/ozel-liste/main/repo.json
```
**Shortcode (kÄ±sayol):** CloudStream, "Depo Ekle" alanÄ±na kÄ±sa bir kod yazÄ±nca onu bir kÄ±saltma servisinden Ã§Ã¶zer (redirect `Location` baÅŸlÄ±ÄŸÄ±ndan okunur):
- **`!ozel45`** â†’ `py.md/ozel45` â†’ `repo.json` (TÃ¼rkiye'de Ã§alÄ±ÅŸÄ±r; **Ã¶nerilen**). "Depo Ekle" alanÄ±na sadece `!ozel45` yazman yeterli.
KÄ±sa kod yalnÄ±zca harf/rakam/`!_-` iÃ§erebilir; `!` ile baÅŸlayanlar `py.md` servisine gider. KiÅŸisel depo iÃ§in zorunlu deÄŸil â€” tam URL de Ã§alÄ±ÅŸÄ±r.
**Ä°pucu â€” jsDelivr proxy:** CloudStream'de Ayarlar â†’ UzantÄ±lar bÃ¶lÃ¼mÃ¼nde jsDelivr proxy'si aÃ§Ä±ksa (otomatik CDN dÃ¶nÃ¼ÅŸÃ¼mÃ¼), `raw.githubusercontent.com` adresleri hem `repo.json` hem eklenti indirmelerinde otomatik `cdn.jsdelivr.net` Ã¼zerinden Ã§ekilir. GitHub/raw TÃ¼rkiye'de engellenirse bu ayar eriÅŸimi kurtarÄ±r. UzantÄ± hÃ¢lÃ¢ yÃ¼klenmiyorsa VPN deneyin.
**Kural â€” bozuk eklentiyi silme, `status:0` yap (kod kanÄ±tÄ±yla):** Bir eklentinin kaynak sitesi Ã¶lÃ¼rse kaydÄ± `plugins.json`'dan **silme**, `status`'Ã¼nÃ¼ `0`'a Ã§ek (kayÄ±t listede kalÄ±r). Kod kanÄ±tÄ± (`recloudstream/cloudstream` â†’ `app/src/main/java/com/lagradost/cloudstream3/plugins/PluginManager.kt`):
- `isDisabled = plugin.status == PROVIDER_STATUS_DOWN` (satÄ±r 231) â†’ gÃ¼ncelleme dÃ¶ngÃ¼sÃ¼nde `if (pluginData.isDisabled) { unloadPlugin(...) }` (satÄ±r 306) â†’ uygulama, repo yenilendiÄŸinde eklentiyi **otomatik kaldÄ±rÄ±r**.
- KaydÄ± tamamen silersen uygulama yerel kopyayla eÅŸleÅŸecek kayÄ±t bulamaz â†’ eski kurulu eklenti **yÃ¼klÃ¼ ve bozuk kalÄ±r** (cihazda manuel silme dÄ±ÅŸÄ±nda temizlenmez).
- BÃ¼yÃ¼k repolar bu kuralÄ± uygular: `hexated/cloudstream-extensions-hexated` listede 5 eklentiyi `status:0` ile tutuyor (Anifreakz, Anizm, GomunimeProvider, IdlixProvider, Loklok).
- Site dÃ¼zelince `status`'Ã¼ `1`'e Ã§evir ve `version`'Ä± bir artÄ±r (gÃ¼ncelleme tetiklenir).
- `status` deÄŸerleri: `0` = kapalÄ±, `1` = aÃ§Ä±k, `2` = yavaÅŸ, `3` = sadece beta.
> **Not (ilerisi iÃ§in):** Bir eklenti bozulduÄŸunda bu kural uygulanacak: silme yok, `status:0`. Zorunlu silme gerekiyorsa (Ã¶r. yasal istek, gerÃ§ekten kaybolan kaynak) Ã¶nce kullanÄ±cÄ±ya cihazda manuel silmesi gerektiÄŸi hatÄ±rlatÄ±lmalÄ±.

## Depo YapÄ±sÄ±
```
ozel-liste/
â”œâ”€â”€ repo.json            â†’ CloudStream'in aÃ§tÄ±ÄŸÄ± depo tanÄ±mÄ±
â”œâ”€â”€ plugins.json         â†’ eklenti listesi (16 eklenti)
â”œâ”€â”€ verify.py            â†’ yapÄ±sal + aÄŸ kontrollÃ¼ doÄŸrulama script'i (--deep ile .cs3 iÃ§inden gerÃ§ek Ã§ekim domaini kontrolÃ¼; --health ile Ã¶lmÃ¼ÅŸ eklentilere otomatik status:0; sadece standart kÃ¼tÃ¼phane, Python 3)
â”œâ”€â”€ update.py            â†’ kaynak depolardan gÃ¼ncel verileri senkronize eden script (--check rapor modu dahil)
â”œâ”€â”€ backups/            â†’ temizlenmiÅŸ CloudStream veri yedeÄŸi Ã¶rneÄŸi (kiÅŸisel veri yok)
â””â”€â”€ DEPO-BILGILERI.md    â†’ bu dokÃ¼man
```

## CloudStream Veri YedeÄŸi (backups/)
`backups/CS3_Backup_2026_08_18_20_14_TEMIZ.txt` â€” CloudStream'in **Ayarlar â†’ GÃ¼ncellemeler ve Yedek â†’ Veri YedeÄŸi** ile Ã¼rettiÄŸi yedeÄŸin **kiÅŸisel veriden arÄ±ndÄ±rÄ±lmÄ±ÅŸ** temiz Ã¶rneÄŸidir. Restore edilebilir bir referans/template dosyasÄ±dÄ±r. AynÄ± iÃ§erik `backups/CS3_Backup_2026_08_18_20_14_TEMIZ.json` olarak da saklanÄ±r (aynÄ± klasÃ¶rde; uygulama/cihaza gÃ¶re uzantÄ± `.json` â†’ `.txt` yeniden adlandÄ±rÄ±larak kullanÄ±labilir).
Yedek iki bloktan oluÅŸur: `datastore` (uygulama DataStore tercihleri) ve `settings` (SharedPreferences). Bu Ã¶rnekte:

**Ã‡Ä±karÄ±lanlar (kiÅŸisel/Ã¶nemsiz):**
- `REPOSITORIES_KEY` â€” ekli depolar (repo artÄ±k `!ozel45` ile ekleniyor, yedekte taÅŸÄ±nmasÄ±na gerek yok)
- Ä°zleme geÃ§miÅŸi ve kaldÄ±ÄŸÄ±n yerler: `0/result_dub/*`, `0/result_episode/*`, `0/result_season/*`, `0/video_pos_dur/*`, `0/result_resume_watching_2/*`
- Arama geÃ§miÅŸi + arama tercihleri: `0/search_history/*`, `0/search_pref_providers`, `0/search_pref_tags`
- Ä°ndirme Ã¶nbellekleri: `download_header_cache/*`, `BACKUP_download_header_cache/*`
- Bu repoda olmayan eklentilerin ayarlarÄ±: `KraptorPlus*`, `Torrentio*`, `persistent_program_ids`
- Ana sayfa API'si (`0/home_api_used` â€” listede olmayan eklentiye iÅŸaret ediyordu)

**Korunanlar (tercihler):**
- OynatÄ±cÄ±: kalite/kaynak Ã¶ncelikleri, `playback_speed`, `preferred_audio_language: tr`, `resize_mode`, `duration_mode`, video profiller
- AltyazÄ±: `subtitle_settings`, `subs_auto_download: tr`
- `settings` bloÄŸu bÃ¼tÃ¼n: `auto_update: true`, `auto_update_plugins`, jsDelivr proxy, DNS, swipe/pip/rotate, `provider_lang: tr` vb.
- Kurulum bayraklarÄ±: `VERSION_NAME`, `HAS_DONE_SETUP`, `FILES_TO_DELETE_KEY`

**Ã–nemli deÄŸerler (kullanÄ±cÄ± tercihi, kaynak kod ile doÄŸrulandÄ±):**
- `jsdelivr_proxy_key: true` â€” tÃ¼m raw GitHub URL'leri jsDelivr CDN Ã¼zerinden gider (`RepositoryManager.kt` `convertRawGitUrl`); GitHub raw engelli/sorunlu aÄŸlarda **CloudStream istemci tarafÄ±nda** aÃ§Ä±lmasÄ± gereken ayardÄ±r (`repo.json` yine `raw.githubusercontent.com` adresini verir â€” dÃ¶nÃ¼ÅŸÃ¼m depo tarafÄ±nda deÄŸil, uygulama tarafÄ±nda yapÄ±lÄ±r). `false` = doÄŸrudan raw GitHub, null = uygulama aÃ§Ä±lÄ±ÅŸta otomatik tespit (MainActivity.kt:1327).
- `prerelease_update: true` â€” uygulama artÄ±k prerelease sÃ¼rÃ¼mden (4.8.0-PRE) Ã§alÄ±ÅŸÄ±yor; gÃ¼ncelleme kontrolÃ¼ prerelease build'leri de kapsar.
- `enable_nsfw_on_providers_key: true` â€” NSFW iÃ§erik destekleyen eklentilerde yetiÅŸkin iÃ§erik gÃ¶sterimi aÃ§Ä±k.

**Kaynak (player) Ã¶ncelikleri â€” semantik ve sÄ±ralama (kaynak kod ile doÄŸrulandÄ±):**
- Semantik: `sortLinks` â†’ `sortedBy { -it.priority }` (`PlayerGeneratorViewModel.kt`) â†’ **bÃ¼yÃ¼k sayÄ± listede Ã¼stte**; toplam Ã¶ncelik = `qualityPriority + sourcePriority`, kaynak varsayÄ±lanÄ± = 1, negatif toplam yalnÄ±z `hide_negative_sources` aÃ§Ä±ksa gizlenir (varsayÄ±lan kapalÄ±).
- Dublaj grubu (5-8) altyazÄ± grubunun (0-4) Ã¼stÃ¼nde tutuldu: kullanÄ±cÄ± TÃ¼rkÃ§e dublajÄ± Ã¶nce seÃ§iyor (`preferred_audio_language: tr`, altyazÄ± yedek).
- Hoster sÄ±ralamasÄ± (en iyi â†’ en kÃ¶tÃ¼): **Filemoon** (CDN + HLS, 1080p+, en saÄŸlam) > **VidMoly** (global CDN, Ã§oklu kalite) > **DzenRu** (dzen.ru, 1080p) > **Odnoklassniki/Okru** (ok.ru, 720p-1080p, bazen yavaÅŸ) > **Pixel** (PixelDrain, dosya hostu â€” 60 gÃ¼n sonra baÄŸlantÄ±lar Ã¶lebilir) > **Sibnet** (sibnet.ru, **en fazla 720p**).
- Profil 1 deÄŸerleri: Dublaj: FileMoonSx=8, Dzen=7, Odnoklassniki=6, Pixel=5 Â· AltYazÄ±: Filemoon=4, VidMoly=3, Dzen=2, Odnoklassniki=1, Okru=1, Sibnet=0, Pixel=0.
> Not: Yedek dosyasÄ± repo'da referans amaÃ§lÄ±dÄ±r; CloudStream restore ederken repo/shortcode gerektirmez, repo yine `!ozel45` ile eklenir.

`repo.json` iÃ§eriÄŸi:
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
Her `plugins.json` kaydÄ±: `.cs3` dosya adresi, SHA-256 `fileHash`, `fileSize`, `language`, `tvTypes`, sÃ¼rÃ¼m ve durum iÃ§erir.

## Kaynak GitHub depolarÄ±

Åu anki 16 eklentinin geldiÄŸi kaynaklar (`.cs3` adreslerinden Ã§Ä±karÄ±ldÄ±; ileride hangi kaynaktan geldiÄŸi lazÄ±m olursa buradan bakÄ±labilir):
| Kaynak repo (GitHub) | Eklenti | Adet |
|----------------------|---------|------|
| [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | Full4kizle | 1 |
| [pltmustafa/plt-stream](https://github.com/pltmustafa/plt-stream) | plt-stream | 1 |
| [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | Ddizi, DiziYou, DiziBox, Dizilla, DiziMom, FilmMakinesi, FilmModu, HDFilmCehennemi, SinemaCX, JetFilmizle, SezonlukDizi, WebteIzle | 12 |
| [ilkelkullanici/ilkel-cloudstream](https://github.com/ilkelkullanici/ilkel-cloudstream) | Sinewix | 1 |
| [MRTDEVM/cloudstream-turkce](https://github.com/MRTDEVM/cloudstream-turkce) | FullHDFilmizlesene | 1 |

Eskiden kullanÄ±lan / hiÃ§ kullanÄ±lmayan kaynaklar:
- `Kraptor123/cs-kraptor` â€” **KAPANDI.** Depo sÄ±fÄ±rlandÄ±, README'de "desteÄŸi kesmiÅŸ bulunuyorum" ibaresi var; tÃ¼m `.cs3` dosyalarÄ± 404 veriyor. Bu kaynaktan gelen 29 eklenti listeden Ã§Ä±karÄ±ldÄ±; bazÄ±larÄ± Feroxx deposundaki canlÄ± sÃ¼rÃ¼mleriyle listede.
- `NivinCNC/CNCVerse-Cloud-Stream-Extension` â€” `CricifyProvider` (canlÄ± spor) bu kaynaktan geliyordu; kullanÄ±cÄ± canlÄ± spor istemediÄŸi iÃ§in eklenti yok.
- `Kraptor123/Cs-Karma` â€” `Streamed` (canlÄ± spor) bu kaynaktan geliyordu; kullanÄ±cÄ± istemedi. Kaynaktan yalnÄ±zca `Full4kizle` kaldÄ±.
- `Kraptor123/Cs-GizliKeyif` â€” tamamÄ± +18 NSFW iÃ§erikliydi (108 kayÄ±t; NSFW olmayan kayÄ±t yok), hiÃ§ eklenmedi.
- `sarapcanagii/*` â€” `NeonSpor` (canlÄ±) bu kaynaktan gelmiÅŸti; kullanÄ±cÄ± istemedi.
- `ByAyzen/AyzenCS3` â€” `Syncler`, `Torrential` bu kaynaktan geliyordu; kiÅŸisel tercihle silindi.
> Not: KaynaklarÄ±n tamamÄ± `raw.githubusercontent.com` Ã¼zerinden `builds/plugins.json` ve/veya tekil `.cs3` dosya adresleriyle Ã§ekildi; hiÃ§bir eklenti kopyalanÄ±p yeniden barÄ±ndÄ±rÄ±lmadÄ±, adresler kaynak repoya iÅŸaret eder.

## YapÄ±sal Kontrol (verify.py)
```bash
python verify.py               # yapÄ±sal + aÄŸ kontrolleri (varsayÄ±lan)
python verify.py --offline     # yalnÄ±zca yapÄ±sal kontroller
python verify.py --deep        # + .cs3 iÃ§inden gerÃ§ek Ã§ekim domainlerini Ã§Ä±karÄ±p test eder (uyarÄ± Ã¼retir, karar vermez)
python verify.py --health      # + cekim domainleri TAMAMEN olmus eklentilere status:0 uygular (otomatik karar modu)
```
`verify.py` (yalnÄ±zca standart kÃ¼tÃ¼phane, harici baÄŸÄ±mlÄ±lÄ±k yok):

**YapÄ±sal kontroller (her iki modda):**
- JSON syntax geÃ§erliliÄŸi ve `repo.json` `pluginLists` varlÄ±ÄŸÄ±
- `internalName`, `url`, `fileHash` alanlarÄ±nda yinelenme olmamasÄ±
- Zorunlu alanlarÄ±n varlÄ±ÄŸÄ± ve tip tutarlÄ±lÄ±ÄŸÄ± (`status` 0-3: 0=kapalÄ±, 1=aÃ§Ä±k, 2=yavaÅŸ, 3=sadece beta; `version`, `apiVersion` int; `authors` liste)
- `url` uzantÄ±sÄ±nÄ±n `.cs3` olmasÄ±
- `fileHash`'in `sha256-` + 64 hex formatÄ±nda olmasÄ±
- `tvTypes` geÃ§erliliÄŸi: `Movie, TvSeries, Anime, Live, AsianDrama, Others, Documentary, AnimeMovie, OVA, Cartoon`
- `language` ISO uyumluluÄŸu, `description`/`name`/yazar boÅŸluklarÄ±; `iconUrl` iÃ§inde `%size%` yer tutucusu uyarÄ± Ã¼retir (bu depo ikonlarÄ± normalize eder: `%size%` â†’ `sz=128`)

**AÄŸ kontrolleri (varsayÄ±lan modda):**
- Her eklentinin `.cs3` dosyasÄ± indirilir; HTTP durumu, `fileSize` ve `fileHash` (SHA-256) uyumu doÄŸrulanÄ±r
- `iconUrl` adresine HEAD/GET atÄ±lÄ±r (HTTP 200 ÅŸartÄ±)
- Kaynak depo geÃ§ici eriÅŸilemezse "atlanabilir" kabul edilir (uyarÄ±); dosya **404** ise hata sayÄ±lÄ±r

**Derin Ã§ekim domain kontrolÃ¼ (`--deep`, deneysel):**
- Her eklentinin `.cs3` arÅŸivi aÃ§Ä±lÄ±r, `classes.dex` iÃ§inden ASCII hostname adaylarÄ± Ã§Ä±karÄ±lÄ±r (bilinen TLD listesi + filtreler)
- Ã‡Ä±kan adaylar DNS + HTTP ile test edilir; `[SITE]` uyarÄ±sÄ± Ã¼retilir
- Ä°kon domaini **yerine** eklentinin gerÃ§ekten veri Ã§ektiÄŸi domainler izlenir â†’ yanlÄ±ÅŸ alarm riski dÃ¼ÅŸÃ¼ktÃ¼r
  (Ã¶r. SinemaCX ikon domaini `sinema.cx` DNS'te Ã¶lÃ¼ gÃ¶rÃ¼nÃ¼yordu ama eklenti asÄ±l veriyi canlÄ± olan `sinema.gg`'den Ã§ekiyor)
- Eklentinin birden fazla kaynaÄŸÄ±ndan en az biri ayaktaysa sorun sayÄ±lmaz; hepsi yanÄ±t vermiyorsa uyarÄ± Ã¼retilir
- Domainler dinamik Ã¼retilen eklentilerde (FilmMakinesi, DiziYou gibi) aday Ã§Ä±kmaz, o eklenti iÃ§in geÃ§ersiz sayÄ±lÄ±r

Not: **Bu script eklentilerin "Ã§alÄ±ÅŸtÄ±ÄŸÄ±nÄ±" doÄŸrulamaz.** Eklentinin gerÃ§ekten film/dizi aÃ§Ä±p oynatmasÄ± yalnÄ±zca CloudStream Ã¼zerinde kullanÄ±cÄ±nÄ±n testiyle anlaÅŸÄ±lÄ±r. `--deep` modu site kapanÄ±ÅŸlarÄ±nÄ± erken yakalamak iÃ§in yapÄ±lan en derin sunucu tarafÄ± kontrolÃ¼dÃ¼r; bot engelleri ve bÃ¶lgesel farklar nedeniyle karar iÃ§in referans alÄ±nmaz, yalnÄ±zca uyarÄ± Ã¼retir.

**Otomatik `status:0` (`--health`):**
- `--deep`'in aksine bu mod **karar verir**: aktif eklentinin `.cs3`'Ã¼nden Ã§Ä±karÄ±lan Ã§ekim domainlerinin **tamamÄ±** kesin Ã¶lÃ¼ ise eklentiyi `plugins.json`'da `status:0` yapar (CloudStream yenilemede eklentiyi devre dÄ±ÅŸÄ± bÄ±rakÄ±r).
- Kesin Ã¶lÃ¼ kriterleri: DNS Ã§Ã¶zÃ¼lemiyor, ana sayfa 404/410, TLS hatasÄ± (http de Ã¶lÃ¼), veya sayfa **domain-parking "satÄ±lÄ±k" sayfasÄ±** (title/iÃ§erikte `satÄ±lÄ±ktÄ±r`, `for sale`, `Kaynaklar ve Bilgiler`, dan.com/afternic/nicsell vb. iÅŸaretler). Bunlar `--deep`'in kÃ¶r noktasÄ±ydÄ±: parking sayfasÄ± HTTP 200 dÃ¶ndÃ¼rdÃ¼ÄŸÃ¼ iÃ§in "ayakta" sanÄ±lÄ±yordu (666, FullHD Ã¶rneÄŸi).
- **YanlÄ±ÅŸ pozitife kapalÄ±:** en az bir domain ayaktaysa veya herhangi bir domain `unknown` (zaman aÅŸÄ±mÄ±, bot engeli 403, belirsiz) ise **dokunulmaz**. Dinamik domainli eklentilerde (FilmMakinesi, DiziYouâ€¦) domain Ã§Ä±kmadÄ±ÄŸÄ± iÃ§in hiÃ§bir zaman otomatik kapatÄ±lmaz.
- `status:1`'e (yeniden aÃ§ma) **asla** otomatik dÃ¶nÃ¼lmez â€” bunu yalnÄ±zca kullanÄ±cÄ± yapar. Bu yÃ¼zden yanlÄ±ÅŸ kapatma riski dÃ¼ÅŸÃ¼ktÃ¼r ve geri dÃ¶nÃ¼ÅŸÃ¼ kolaydÄ±r.
- Elle `python verify.py --health` komutuyla Ã§alÄ±ÅŸtÄ±rÄ±lÄ±r (otomatik Ã§alÄ±ÅŸmaz).

## Kaynak Senkronizasyonu (update.py)
```bash
python update.py --check    # yazmadan sadece farklarÄ± raporlar (fark varsa exit 1)
python update.py            # farklarÄ± uygular, plugins.json'u gÃ¼nceller
```
Kaynak `builds/plugins.json` adresi, listedeki `.cs3` adresinden tÃ¼retilir (`https://raw.githubusercontent.com/<owner>/<repo>/builds/<Isim>.cs3` â†’ aynÄ± klasÃ¶rdeki `plugins.json`). Senkronize edilen alanlar: `version, fileSize, fileHash, description, authors, language, tvTypes`. `iconUrl` bilinÃ§li olarak senkronize **edilmez** â€” bu depo ikon adreslerini normalize eder (kaynaktaki `%size%` yer tutucularÄ± sabit `sz=128`'e Ã§evrilir) ve kaynak gÃ¼ncellemesi bu dÃ¼zeltmeyi geri almasÄ±n.

> **Not:** Bu depo **otomatik hiÃ§bir ÅŸey Ã§alÄ±ÅŸtÄ±rmaz** (GitHub Actions yok). Kaynak senkronu (`update.py`), site saÄŸlÄ±k kontrolÃ¼ (`verify.py --deep`/`--health`) ve status deÄŸiÅŸiklikleri yalnÄ±zca **elle** yapÄ±lÄ±r. `[ATLANDI]` sayÄ±sÄ±, kaynak depo bazÄ±nda toplu kapanÄ±ÅŸÄ±n (Ã¶r. cs-kraptor kapanÄ±ÅŸÄ±: 29 eklenti tek seferde 404) erken iÅŸaretidir.

## KarÅŸÄ±laÅŸÄ±lan Hatalar ve Ã‡Ã¶zÃ¼mleri
| Hata | Neden | Ã‡Ã¶zÃ¼m |
|------|-------|-------|
| Eklentilerin Ã§oÄŸu repo listesinde gÃ¶rÃ¼nmÃ¼yordu | CloudStream Ã¶nbelleÄŸi eski listeyi tutuyordu | Uygulamada "Verileri temizle" â†’ depo yeniden eklendi |
| `.cs3` dosyalarÄ± "format hatasÄ±" gÃ¶sterdi | Sorun dosyada deÄŸildi; istemci Ã¶nbelleÄŸi eski listeyi gÃ¶steriyordu | Uygulamada "Verileri temizle" â†’ depo yeniden eklendi, sorun Ã§Ã¶zÃ¼ldÃ¼ |
| `FilmmirasÄ±m` JSON'da eÅŸleÅŸmiyordu | Dosya adÄ±ndaki noktasÄ±z `Ä±` (U+0131) karakteri shell'de bozuldu | Python'da `\u0131` escape'iyle yazÄ±larak halledildi |
| PowerShell ile JSON dÃ¼zenlemekte bozulma | `ConvertFrom/ConvertTo-Json` dizi yapÄ±sÄ±nÄ± bozuyordu | TÃ¼m JSON iÅŸlemleri Python (`utf-8`, `ensure_ascii=False`) ile yapÄ±ldÄ± |
| jsDelivr hÃ¢lÃ¢ eski listeyi gÃ¶steriyordu | CDN Ã¶nbelleÄŸi | `purge.jsdelivr.net` Ã¼zerinden Ã¶nbellek temizlendi |
| `FullRaces` simgesi yÃ¼klenmiyordu | `iconUrl` iÃ§inde `%size%` yer tutucusu kalmÄ±ÅŸtÄ± | `sz=128` olarak dÃ¼zeltildi |
| `Disney-Plus` kaynaÄŸÄ± gÃ¶rÃ¼nÃ¼yordu | MirrorVerse eklentisinin iÃ§indeki kaynak adÄ± | Eklenti listeden kaldÄ±rÄ±ldÄ± |
| 30 eklenti indirilemiyordu (hata yazÄ±yordu) | `cs-kraptor` deposu kapanmÄ±ÅŸtÄ±; 29 `.cs3` dosyasÄ± 404 veriyordu, 1 eklenti de (JPFilms) hash'i gÃ¼ncellenmediÄŸi iÃ§in uyuÅŸmuyordu | Kaynak kapandÄ±ÄŸÄ± iÃ§in 29 eklenti listeden Ã§Ä±karÄ±ldÄ±; JPFilms dahil yabancÄ± eklentiler TÃ¼rkÃ§e filtresiyle kaldÄ±rÄ±ldÄ±. Kalan 4 eklenti tek tek indirilip hash/boyut doÄŸrulandÄ± |
| `JPFilms` indirilemiyordu | Kaynakta v6 â†’ v7 gÃ¼ncellenmiÅŸ, hash ve boyut deÄŸiÅŸmiÅŸti; listede eski hash duruyordu | Yeni hash/boyut kaynaÄŸÄ±ndan alÄ±ndÄ±; ancak daha sonra TÃ¼rkÃ§e filtreyle eklenti listeden Ã§Ä±karÄ±ldÄ±ÄŸÄ± iÃ§in push edilmedi |
| `plt-stream` hash uyuÅŸmazlÄ±ÄŸÄ± | Kaynak v38 â†’ v39 gÃ¼ncellenmiÅŸ; listede eski hash (411831 byte) vardÄ±, gerÃ§ek dosya deÄŸiÅŸmiÅŸti (413103 byte) | KaynaÄŸÄ±n `builds/plugins.json`'Ä±ndan gÃ¼ncel `version/fileSize/fileHash/description` alÄ±ndÄ±, kayÄ±t senkronlandÄ± |
| `Ä°nfluencerChicks` indirilemiyordu | Eklenti adÄ±ndaki `Ä°` (U+0130) karakteri raw URL'de HTTP isteÄŸini ascii encode hatasÄ±yla patlatÄ±yordu | URL'deki `Ä°` â†’ `%C4%B0` percent-encode edildi (CloudStream de benzer sorun yaÅŸamamasÄ± iÃ§in) |
| Makoto2 eklentilerinde `fileHash` yoktu | Depo eski CloudStream formatÄ± kullanÄ±yor (hash alanÄ± olmadan) | `fileHash` kontrolÃ¼ atlanÄ±p yalnÄ±zca indirilebilirlik doÄŸrulandÄ±; bu depodan eklenti alÄ±nmadÄ± |
| `Kanal 7` eklentisi indirilemiyordu | URL'de boÅŸluk karakteri vardÄ± (`.../Kanal 7.cs3`), GitHub raw'da geÃ§ersiz | Depodan eklenti kullanÄ±lmadÄ± |
| `cagatayrepo` ve `AyzenCS3` 404 | Bu depolarÄ±n `plugins.json`'Ä± eriÅŸilemezdi | Katalogda listelenmesine raÄŸmen kullanÄ±lmadÄ± |
| GitHub API rate limit | `api.github.com` istek limiti doluyordu | Ham `raw.githubusercontent.com` fetch'leri ve websearch ile aÅŸÄ±ldÄ± |
| `plt-stream` yine bozulmuÅŸtu (v42 â†’ v44) | Kaynak repo v44'e gÃ¼ncellenmiÅŸ; listede v42/eski hash/421535 byte duruyordu, gerÃ§ek dosya 428931 byte idi. CloudStream hash doÄŸrulamasÄ± "Extension hash mismatch" fÄ±rlatÄ±yordu | `update.py` ile kaynaktan senkronlandÄ± (v44, yeni hash) |
| jsDelivr proxy `.cs3` 404/400 veriyordu (araÅŸtÄ±rma) | Ä°lk istekte jsDelivr Ã¶nbelleÄŸi soÄŸuk olduÄŸu iÃ§in 404; `@branch` sÃ¶zdizimi ve tarayÄ±cÄ± UA ile 200 dÃ¶nÃ¼yor | Sorun deÄŸil; jsDelivr Ã¶nbelleÄŸi Ä±sÄ±nÄ±nca tÃ¼m `.cs3`'ler doÄŸru hash'le iniyor (plt-stream hariÃ§ kaynak gÃ¼ncel olduÄŸu iÃ§in o da senkronlanÄ±nca dÃ¼zeldi) |
| jsDelivr dÃ¶nÃ¼ÅŸÃ¼m formatÄ± karÄ±ÅŸÄ±yordu | DoÄŸru format `cdn.jsdelivr.net/gh/<owner>/<repo>@<branch>/<path>` â€” `@` **repo adÄ±ndan sonra** gelir (branch'ten Ã¶nce); `repo@branch` yazÄ±lmadÄ±ÄŸÄ±nda 404 alÄ±nÄ±yordu | Format netleÅŸtirildi: `https://cdn.jsdelivr.net/gh/kadircee/ozel-liste@main/plugins.json`; purge de aynÄ± biÃ§imi kullanÄ±r |
| `git push` Ã§Ä±ktÄ±sÄ±nda kÄ±rmÄ±zÄ± `NativeCommandError` gÃ¶rÃ¼nÃ¼yordu | PowerShell, git'in stderr'e yazdÄ±ÄŸÄ± ilerleme satÄ±rlarÄ±nÄ± hata sanÄ±yor | GerÃ§ek hata deÄŸil â€” Ã§Ä±ktÄ±nÄ±n sonunda `fb7f710..6aea63d main -> main` gÃ¶rÃ¼lÃ¼yorsa push baÅŸarÄ±lÄ± demektir |
| YAML doÄŸrulama `ModuleNotFoundError: No module named 'yaml'` | Python'da PyYAML kurulu deÄŸildi | `python -m pip install pyyaml` ile kuruldu; doÄŸrulama `yaml.safe_load` ile geÃ§ti |
| YAML doÄŸrulamada `KeyError: 'on'` | PyYAML YAML 1.1'de `on:` anahtarÄ±nÄ± bool `True`'ya Ã§evirir (GitHub Actions YAML 1.2 kullanÄ±r ve `on`'u string kabul eder) | GerÃ§ek hata deÄŸil; GitHub Actions bu dosyayÄ± doÄŸru ayrÄ±ÅŸtÄ±rÄ±r (workflow dosyasÄ± sorunsuz Ã§alÄ±ÅŸÄ±r) |
| `verify.py --health` yanlÄ±ÅŸ eklenti kapatabilir mi (tasarÄ±m) | Eski `--deep` HTTP 200 kontrolÃ¼ parking sayfasÄ±nÄ± "ayakta" sanabiliyordu (666/FullHD yanlÄ±ÅŸ pozitifi) | `--health` sayfa iÃ§eriÄŸi/title ile parking tespiti ekledi, **kesin Ã¶lÃ¼** (DNS/404/TLS/parking) dÄ±ÅŸÄ±nda karar vermiyor; `unknown` veya canlÄ± domain varsa dokunmuyor. Test: 6 parking/legit vaka + gerÃ§ek 666filmizle.site `dead` sÄ±nÄ±flandÄ±; 13 aktif eklenti tarandÄ±, yanlÄ±ÅŸ kapanma yok |

### Tekrar Kontrol Edilecekler (Dead Link DeÄŸildir, repo build gÃ¼ncellendiÄŸinde belki Ã§alÄ±ÅŸacaktÄ±r ?)
| Eklenti | Kaynak | Son Bilinen Domain | Durum |
|---------|--------|-------------------|-------|
| SetFilmIzle | feroxx/ilkel | setfilmizle.uk | Site Ã¶lÃ¼, tekrar kontrol edilecek |
| AltiYuzAltmisAltiFilmIzle | feroxx/ilkel | 666filmizle.site | Site Ã¶lÃ¼, tekrar kontrol edilecek |
| FilmBip | ilkel | filmbip.com | Site Ã¶lÃ¼, tekrar kontrol edilecek |
| FullHDFilm | feroxx | fullhdfilm.org | Site Ã¶lÃ¼, tekrar kontrol edilecek |
| Filmatek | Kraptor123/Cs-Karma | filmatek.net | Site Ã¶lÃ¼, tekrar kontrol edilecek |
| DiziBox | feroxx/Kekik-cloudstream | dizibox.com | Site Ã¶lÃ¼, tekrar kontrol edilecek |
| DiziMom | feroxx/Kekik-cloudstream | dizimom.com | Site Ã¶lÃ¼, tekrar kontrol edilecek |
| Dizilla | feroxx/Kekik-cloudstream | dizilla.com | Site Ã¶lÃ¼, tekrar kontrol edilecek |
| WebteIzle | feroxx/Kekik-cloudstream | webteizle3.xyz | Site Ã¶lÃ¼, tekrar kontrol edilecek |

### Ã–nemli Not
Repolar gÃ¼ncellendiÄŸinde (yeni build yayÄ±nlandÄ±ÄŸÄ±nda (GitHub uzerinden takip edilir)), bu listedeki Ã¶lÃ¼ siteler otomatik olarak kontrol edilmeli ve Ã§alÄ±ÅŸÄ±yorsa tekrar eklenebilir.

## Silinen Eklentiler (delete-zone)
Bu eklentiler listeye **eklenmez**; yeniden ekleme kararÄ± yalnÄ±zca kullanÄ±cÄ± verir. Listede NSFW (+18) hiÃ§ yer almadÄ±; canlÄ± yayÄ±n/maÃ§ eklentileri istenmedi. Bozuk eklentiler silinmez, `status:0` yapÄ±lÄ±r (bkz. Kurulum). "Site aÃ§Ä±lmÄ±yor" gerekÃ§esiyle silinenler **geri dÃ¶nÃ¼ÅŸlÃ¼dÃ¼r**: site dÃ¼zelirse tekrar denenebilir.

**Anime/Asya iÃ§erikli (kullanÄ±cÄ± anime istemiyor):** AnimeciX, Animeler, Animely, AnimPow, Anizium, OnePaceTr, OpenAnime, TrAnimeIzle, TurkAnime, AsyaAnimeleri, AsyaFanatiklerim, AsyaWatch, DiziAsia, DiziAsya, DiziKorea, Koredizi, AnimeAV, AnimeWorld, AnimeYTX, Latanime, DramaDizilerim, Dramaizle
**CanlÄ± yayÄ±n / maÃ§ (kullanÄ±cÄ± hiÃ§bir halÃ¼karda istemiyor):** InatBox, NeonSpor, RecTV, Streamed, CricifyProvider
**DiÄŸer ("kesinlikle istemiyorum" / kiÅŸisel tercih):** FilmmirasÄ±m, SeiCode, YTS, YeniKaynak, YesilCamTv, MirrorVerse, Vavoo, WebDramaTurkey, Syncler, Torrential, BelgeselX, CizgiMax, CizgiveDizi, DiziPal, DiziPalOriginal, KultFilmler, RareFilmm
**TÃ¼rkÃ§e/TÃ¼rkiye filtresi (yabancÄ± dil iÃ§erikli):** Esheaq, Krmzy, YoTurkish, DoramasLatinoX, Dubbindo, Flixlatam, Henaojara, Gnulahd, JPFilms, KissKH, LayarKaca, Movix, OK, Sokuja, Subsplease, Supercartoons, Wcoflix, Yablom, DocumentaryArea, Iwatchtheoffice, FullRaces, FootReplays

## GÃ¼ncelleme
Yeni bir deÄŸiÅŸiklik yapÄ±ldÄ±ÄŸÄ±nda:
```bash
python verify.py --offline      # Ã¶nce yapÄ±sal doÄŸrula
python update.py --check        # kaynak farkÄ± var mÄ± bak (exit 1 = var)
python update.py                # gerekirse kaynak verilerini senkronize et
python verify.py --health       # Ã¶lmÃ¼ÅŸ eklentileri status:0 yap (elle tetikleme)
python verify.py --deep         # senkronizasyon sonrasÄ± aÄŸ + gerÃ§ek Ã§ekim domaini kontrolÃ¼
git add plugins.json
git -c user.name="kadircee" -c user.email="kadircee@users.noreply.github.com" \
    commit -m "plugins.json: aciklama"
git push
```
Push sonrasÄ± jsDelivr Ã¶nbelleÄŸi iÃ§in:
```
https://purge.jsdelivr.net/gh/kadircee/ozel-liste@main/plugins.json
```
CloudStream tarafÄ±nda depo yenilendiÄŸinde yeni liste otomatik Ã§ekilir. Kaynak senkronu ve site saÄŸlÄ±ÄŸÄ± **otomatik deÄŸildir** (GitHub Actions yok): kaynak bir eklentiyi gÃ¼ncellediÄŸinde listedeki hash/boyut **elle** `update.py` Ã§alÄ±ÅŸtÄ±rÄ±larak senkronlanÄ±r, kaynak site Ã¶lÃ¼rse eklenti **elle** `verify.py --health` (veya `--deep`) Ã§alÄ±ÅŸtÄ±rÄ±larak `status:0` yapÄ±lÄ±r. `status:1`'e (yeniden aÃ§ma) otomatik dÃ¶nÃ¼lmez; site geri geldiyse `plugins.json`'da ilgili eklentinin `status`'u elle `1` yapÄ±lÄ±r. GÃ¼ncelleme Ã¶ncesi `verify.py --offline` ve `update.py --check` ile kontrol etmek iyi alÄ±ÅŸkanlÄ±ktÄ±r.

## Yasal UyarÄ± ve Sorumluluk Reddi (Disclaimer)
Bu depo kiÅŸisel arÅŸivleme amacÄ±yla oluÅŸturulmuÅŸtur; hiÃ§bir ticari amacÄ± yoktur. Bu depo (ve GitHub sunucularÄ±) hiÃ§bir video, ses dosyasÄ±, medya veya telif hakkÄ±yla korunan materyal barÄ±ndÄ±rmaz, kopyalamaz veya daÄŸÄ±tmaz. Bu depo yalnÄ±zca internette herkese aÃ§Ä±k olarak paylaÅŸÄ±lan Ã¼Ã§Ã¼ncÃ¼ taraf eklentilerin (`.cs3`) doÄŸrudan GitHub RAW adreslerini derleyen metin tabanlÄ± bir JSON dizinidir ("YalnÄ±zca Endeks"). Listelenen eklentilerin kodlarÄ±, iÅŸleyiÅŸleri veya hangi web sitelerinden veri Ã§ektikleri Ã¼zerinde bu deponun hiÃ§bir kontrolÃ¼, sahipliÄŸi veya sorumluluÄŸu yoktur; tÃ¼m sorumluluk eklentilerin orijinal geliÅŸtiricilerine ve veriyi barÄ±ndÄ±ran kaynak web sitelerine aittir. Bu depo yalnÄ±zca baÄŸlantÄ±larÄ± listeleyen bir kÃ¶prÃ¼ gÃ¶revi gÃ¶rdÃ¼ÄŸÃ¼ iÃ§in telif hakkÄ± ihlali iddialarÄ±nÄ±n muhatabÄ± deÄŸildir; iÃ§erik kaldÄ±rma talepleri (DMCA) doÄŸrudan iÃ§erikleri sunan kaynak web sitelerine veya eklentilerin orijinal GitHub depolarÄ±na yapÄ±lmalÄ±dÄ±r. Bu depo, 5846 sayÄ±lÄ± Fikir ve Sanat Eserleri Kanunu ve 5651 sayÄ±lÄ± Kanun kapsamÄ±nda da eser barÄ±ndÄ±rmaz, Ã§oÄŸaltmaz veya iletmez; yalnÄ±zca kamuya aÃ§Ä±k kaynaklardaki `.cs3` dosyalarÄ±na baÄŸlantÄ± saÄŸlar. 5651 sayÄ±lÄ± Kanunun 4. maddesinin ikinci fÄ±krasÄ± gereÄŸi iÃ§erik saÄŸlayÄ±cÄ±, baÄŸlantÄ± saÄŸladÄ±ÄŸÄ± baÅŸkasÄ±na ait iÃ§erikten sorumlu deÄŸildir; ancak aynÄ± maddenin istisnasÄ± saklÄ±dÄ±r: sunuÅŸ biÃ§iminden baÄŸlantÄ± verilen iÃ§eriÄŸin benimsendiÄŸi ve kullanÄ±cÄ±nÄ±n o iÃ§eriÄŸe ulaÅŸmasÄ±nÄ±n amaÃ§landÄ±ÄŸÄ± aÃ§Ä±kÃ§a belli ise sorumluluk doÄŸabilir. Bu depo, listedeki hiÃ§bir eklentiyi veya eklentilerin veri Ã§ektiÄŸi kaynaklarÄ± benimsemez ve tavsiye etmez; liste salt teknik bir indekstir. Hak sahipleri 5651 sayÄ±lÄ± Kanunun 9. maddesi uyarÄ±nca uyarÄ± yÃ¶ntemiyle bildirimde bulunursa ilgili baÄŸlantÄ± derhal kaldÄ±rÄ±lÄ±r.

This repository is created for personal archiving purposes and has no commercial intent. This repository does not host, store, copy, or distribute any video, audio, media files, or copyrighted material; it serves merely as a text-based JSON index containing direct links to third-party `.cs3` plugins already publicly available on the internet ("Index Only"). The owner of this repository does not develop, host, or control any of the listed plugins, their source code, operation, or the websites these plugins scrape; all liability lies strictly with the original plugin developers and the respective websites hosting the media. As this repository only provides a compilation of text-based URLs, it is not liable for copyright infringement; any DMCA takedown requests must be directed to the actual websites hosting the copyrighted content or to the original developers' repositories. Under Turkish law (FSEK No. 5846 and Law No. 5651), this repository does not host, reproduce, or communicate any work; it merely provides links to `.cs3` files publicly available on the internet. Under Article 4/2 of Law No. 5651, a content provider is not liable for third-party content to which it merely provides a link; however, the exception in that provision is reserved: liability may arise where the presentation clearly shows that the linked content is adopted and that users are intended to reach it. This repository does not adopt or recommend any of the listed plugins or the sources they use; the list is a purely technical index. If rights holders send a notice under Article 9 of Law No. 5651, the relevant link will be removed promptly.
