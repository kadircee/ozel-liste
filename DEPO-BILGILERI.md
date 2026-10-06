# developer (ozel-liste)
Bu depo test CloudStream deposudur; yalnızca Türkçe film/dizi eklentilerini ve test seçtiği kaynakları barındırır. Canlı yayın, NSFW ve yabancı dil içerikli eklentiler kullanıcı tercihi gereği listeye alınmamıştır.

## Kurulum
CloudStream → Ayarlar → Uzantılar → Depo Ekle:
```
https://raw.githubusercontent.com/kadircee/ozel-liste/main/repo.json
```
**Shortcode (kısayol):** CloudStream, "Depo Ekle" alanına kısa bir kod yazınca onu bir kısaltma servisinden çözer (redirect `Location` başlığından okunur):
- **`!ozel45`** → `py.md/ozel45` → `repo.json` (Türkiye'de çalışır; **önerilen**). "Depo Ekle" alanına sadece `!ozel45` yazman yeterli.
Kısa kod yalnızca harf/rakam/`!_-` içerebilir; `!` ile başlayanlar `py.md` servisine gider. Kişisel depo için zorunlu değil — tam URL de çalışır.

## Depo Yapısı
```
ozel-liste/
├── repo.json            → CloudStream'in açtığı depo tanımı
├── plugins.json         → eklenti listesi (33 aktif eklenti)
├── registry.json        → makine-okur kayıt modeli (94 aday; 33 aktif, 9 duplicate, 52 istenmeyen; Seçim ekseni; Pure Mirror)
├── registry.py          → model araçları (--sync / --check / --render [--write])
├── audit.py             → kaynak repoları tarih bazlı denetler (--check = rapor/varsayılan, --apply = yazar)
├── update.py            → kaynak depolardan güncel verileri senkronize eden script (--check / --purge dahil)
└── DEPO-BILGILERI.md    → bu doküman (tablo bloğu registry.json'dan üretilir)
```
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
## Kaynak Seçim Kriteri ve Tablo Bakımı

**1. Kaynak seçimi — SADECE TARİH esastır, versiyon kriter değil:**
- Per-eklenti tarih `git -C <repo> log -1 --format=%cd --date=short --all -- <Eklenti>` ile alınır; repo genel `pushed_at` değil. Aynı eklentinin birden fazla kaynaktan gelen kopyaları arasında en güncel tarihli kayıt otomatik tercih edilir; versiyon numarasının düşük/yüksek olması kararı etkilemez.
- Kaynak kararından önce `audit.py`, her kaynak reposunun bütün dallarını ve dal ağaçlarındaki tüm `.cs3` dosyalarını tarar. `builds` dışı bir dalda `.cs3` bulunursa `ALTERNATİF-DAL .cs3` olarak raporlanır; doğrulanmadan otomatik Aktif yapılmaz. Canonical manifest/artefakt çifti `builds` dalıdır.
- Kaynak manifestinde `status: 0` olan kayıtlar devre dışıdır: `plugins.json`'dan silinir, audit havuzuna alınmaz ve sonraki çalıştırmada yeniden eklenmez. Registry tablosunda yalnızca tarih geçmişi için Duplicate adayı olarak görünebilir.

**1a. Eşit tarihli kaynaklar (tie-breaker) — OTOMATİK, SORU YOK:**
İki veya daha fazla kaynağın aynı güncelleme tarihine sahip olduğu durumlarda repo adına göre alfabetik sıralama yapılır ve HER ZAMAN ilk sıradaki kaynak otomatik seçilir (`audit.py` bu çözümü kendisi uygular; script durup sormaz).
Versiyon numarası bu tie-breaker'da kriter olarak kullanılmaz — ne düşük ne yüksek versiyon tercih nedeni sayılır.

**1b. Tüm dal taraması (2026-09-29):**
Yedi kaynak repo ve mevcut tüm dalları (`builds` dahil) taranır.

**2. Tablo bakımı — `Tüm Repolar` tüm karşılaştırılan adayları içerir:**
- Yeni adaylar için varsayılan filtre `language == tr` ve `tvTypes ⊆ {Movie, TvSeries, Documentary}` kuralıdır. 
- `Site (domain)` her zaman `[domain](https://domain)` linkli olmalı (tıklanabilir).
- `kadircee/ozel-liste` kaynak değil derleme olduğu için `Tüm Repolar`'da yer almaz.
- `İstenmeyenler` metin + tablo aynı anda tutulmaz; tek tablo yeterlidir, `Silinen Eklentiler` metin listesi sadece not bırakır.
- **Yasaklı sayısı tek doğruluk kaynağıdır:** İstenmeyenler tablosundaki benzersiz ad sayısı = `audit.py` çıktısındaki `yasakli sayisi` = **55** (2026-09-29). `registry.json` içinde kaynak örnekleriyle birlikte **56** istenmeyen aday bulunur. Üçü düzenli karşılaştırılır. Başlık (`## İstenmeyenler ...`) **kendi satırında** olmalıdır; tablo satırına yapıştırılırsa GitHub başlığı render etmez ve `audit.py` yasaklı listesini bulamaz → boş liste tespit edilip **`exit 2` ile durdurulur** (sessiz geçiş yok).

**3. Kayıt durumu — tek eksen (Seçim):**
Model yalnızca `Seçim` ekseninden oluşur: `Aktif` (yarışı kazandı, `plugins.json`'da) / `Duplicate` (kaybetti, dosyada yok) / `İstenmeyen` (hiç yarışa girmedi) (bkz. **Kayıt Durumu Modeli**). `status` bilgisi kaynağa bırakılmıştır — kaynak ne yayınlıyorsa (`1`, `0`, …) `update.py` ile birebir yansıtılır; bu depo site canlılığı takibi yapmaz.
- İkon domaininin ölü görünmesi tek başına karar nedeni değildir; asıl erişim eklentinin kendi sağlayıcı koduna bağlıdır.
- **Simge/görsel kaynağı:** Her kayıt için `iconUrl`, seçilen kaynak deponun `builds/plugins.json` manifestinden alınır. `%size%` yer tutucusu sabit `sz=128` değerine çevrilir; simge dosyası bu depoya kopyalanmaz ve görsel yeniden barındırılmaz. Kaynak manifestindeki simge değişirse `update.py` ile güncellenir.
- Kaynak ilerlediyse `update.py` ile senkronize et, `Bizim Tarih`'i eşitle; `status`'e dokunma, kaynak ne verdiyse o alınır.

## Tarih Takip Kuralı (tek kural - aslında kural 1'i anlatmaktadır.)

Tablodaki her satırda iki tarih vardır: **Kaynak Tarih** (kaynak deponun `builds` branch'inde o `.cs3` dosyasına dokunan son commit'in tarihi) ve **Bizim Tarih** (bizim o kaynağı en son benimsediğimiz tarih). Bütün olay bu iki tarihin karşılaştırmasıdır:

- **Kaynak Tarih > Bizim Tarih** → kaynak ilerlemiş demektir. `update.py` ile senkronize et (`status` dahil kaynak ne yayınlıyorsa aynen alınır), sonra satırdaki `Bizim Tarih`'i `Kaynak Tarih`'e eşitle. Versiyon numarasına bakılmaz.
- **Kaynak Tarih == Bizim Tarih** → yapacak iş yok.

## Kayıt Durumu Modeli

Her kayıt tek eksene sahiptir:

- **Seçim:** `Aktif` (yarışı kazandı, `plugins.json`'da) / `Duplicate` (kaybetti, dosyada yok) / `İstenmeyen` (hiç yarışa girmedi).

| Seçim | Anlamı | plugins.json |
| Aktif | Kazanan kayıt | var (`status` kaynağın yayınladığı değer) |
| Duplicate | Yarışı kaybetti, dosyada yok | yok |
| İstenmeyen | Hiç değerlendirmeye alınmadı | yok |


**Araçlar:** `python registry.py --sync` (tablolar + `plugins.json` → `registry.json`), `--check` (şema + küme + tarih; ihlalde exit 1), `--render [--write]` (tabloyu üretir). `Seçim` `plugins.json`'dan türetilir (dosyada olan = Aktif); grup başına en fazla 1 Aktif; Aktif kümesi `plugins.json` ile birebir zorunlu. Eklenti alanları (`status`, `version`, `fileSize`, `fileHash`, `description`, `authors`, `language`, `tvTypes`) kaynak `builds/plugins.json`'dan birebir yansıtılır (`update.py`).

## Kaynak Senkronizasyonu (update.py)
```bash
python update.py --check    # yazmadan sadece farkları raporlar (fark varsa exit 1)
python update.py            # farkları uygular, plugins.json'u günceller
```
Kaynak `builds/plugins.json` adresi, listedeki `.cs3` adresinden türetilir (`https://raw.githubusercontent.com/<owner>/<repo>/builds/<Isim>.cs3` → aynı klasördeki `plugins.json`). Senkronize edilen alanlar: `status, version, fileSize, fileHash, description, authors, language, tvTypes` (Pure Mirror — kaynak ne yayınlıyorsa aynen alınır). 

> **Not:** Kaynak senkronu GitHub Actions ile otomatik çalışır (`.github/workflows/mirror.yml`: her gün 05:00 UTC ve `workflow_dispatch` ile manuel tetikleme). Akış: `update.py` → `registry.py --sync` → `registry.py --render --write` → `registry.py --check` → `audit.py --check` → değişiklik varsa otomatik commit+push. Yerelde elle çalıştırmak da mümkündür. Kaynakta bulunamayan veya `status: 0` olan kayıt `[SILINDI]` olarak listeden düşer; kaynak manifesti 404 ise audit kaynağı atlar ve aktif katalogda kayıt bırakılmaz.

## Silinen Eklentiler (delete-zone)
Bu eklentiler listeye **eklenmez**; yeniden ekleme kararı yalnızca kullanıcı verir. 

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
CloudStream tarafında depo yenilendiğinde yeni liste otomatik çekilir. Kaynak senkronu her gün otomatik koşar (`.github/workflows/mirror.yml`); acil durumda yerelde **elle** de çalıştırılabilir (`python update.py`, ardından `python registry.py --sync`, `python registry.py --render --write`, `python registry.py --check` ve `python audit.py --check`). Güncelleme öncesi `update.py --check` ile kontrol etmek iyi alışkanlıktır.

## Tüm Repolar - Alfabetik Liste

Bu bölüm 2026-10-06 tarihinde `registry.json` ve `plugins.json` üzerinden yeniden oluşturuldu. Liste, **42** kayıt satırını (**33 aktif**, **9 duplicate**) ve kaynak karşılaştırmalarını birlikte gösterir; 404 ve `status: 0` kaynak kayıtları katalogdan çıkarılmıştır.

Aynı normalize ada sahip kayıtlar tek grup olarak değerlendirilir. En güncel kaynak `Aktif`, diğer kaynaklar `Duplicate` olarak gösterilir. `status` alanı kaynak manifestinden Pure Mirror kuralıyla alınır.

Toplam satır: 42 · Aktif: 33 · Duplicate: 9.

<!-- KAYIT-DURUMU:OTOMATIK-BASLANGIC -->
| # | Eklenti | Kaynak | Site (domain) | v | Kaynak Tarih | Bizim Tarih | Seçim | Not |
|---|---|---|---|---|---|---|---|---|
| 1 | Ddizi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [ddizi](https://ddizi.site) | 22 | 2026-09-29 | 2026-09-22 | Aktif |  |
| 2 | DiziBox | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizibox.live](https://dizibox.live) | 23 | 2026-10-04 | 2026-10-04 | Aktif |  |
| 3 | Dizilla | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizilla](https://dizilla.site) | 92 | 2026-09-29 | 2026-09-22 | Aktif |  |
| 4 | Dizilla | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [dizilla](https://dizilla.site) | 10 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 5 | DiziMom | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizimom](https://dizimom.site) | 58 | 2026-09-29 | 2026-09-22 | Aktif |  |
| 6 | DiziMom | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [dizimom](https://dizimom.site) | 4 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 7 | DiziPal2 | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [dizipal2135.com](https://dizipal2135.com) | 2 | 2026-10-02 | 2026-10-02 | Aktif |  |
| 8 | DiziPod | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizipod](https://dizipod.site) | 3 | 2026-09-29 | 2026-09-16 | Aktif |  |
| 9 | DiziWatch | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [diziwatch.site](https://diziwatch.site) | 3 | 2026-09-15 | 2026-09-15 | Duplicate |  |
| 10 | DiziYo | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [diziyo](https://diziyo.site) | 1 | 2026-09-07 | 2026-10-06 | Aktif |  |
| 11 | DiziYo | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [diziyo.site](https://diziyo.site) | 5 | 2026-09-17 | 2026-09-17 | Duplicate |  |
| 12 | DiziYou | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [diziyou](https://diziyou.site) | 26 | 2026-09-29 | 2026-09-22 | Aktif |  |
| 13 | FilmEkseni | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [filmekseni](https://filmekseni.site) | 1 | 2026-09-16 | 2026-09-16 | Duplicate |  |
| 14 | FilmEkseni | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [filmekseni.site](https://filmekseni.site) | 1 | 2026-09-20 | 2026-09-17 | Aktif |  |
| 15 | FilmHane | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [filmhane.shop](https://filmhane.shop) | 1 | 2026-09-07 | 2026-09-07 | Aktif |  |
| 16 | FilmMakinesi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [filmmakinesi](https://filmmakinesi.site) | 59 | 2026-09-29 | 2026-09-22 | Aktif |  |
| 17 | FilmMakinesi | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [filmmakinesi](https://filmmakinesi.site) | 5 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 18 | FilmModu | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [filmmodu](https://filmmodu.site) | 19 | 2026-09-29 | 2026-09-16 | Aktif |  |
| 19 | FilmIzyon | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [filmizyon.site](https://filmizyon.site) | 2 | 2026-09-27 | 2026-09-15 | Aktif |  |
| 20 | FullHDFilm | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [hdfilm.us](https://hdfilm.us) | 36 | 2026-10-04 | 2026-10-04 | Aktif |  |
| 21 | FullHDFilmizlesene | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [fullhdfilmizlesene](https://fullhdfilmizlesene.site) | 33 | 2026-09-29 | 2026-09-22 | Aktif |  |
| 22 | HDFilmCehennemi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [hdfilmcehennemi](https://hdfilmcehennemi.site) | 48 | 2026-09-29 | 2026-09-22 | Aktif |  |
| 23 | HDFilmCehennemi | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [hdfilmcehennemi](https://hdfilmcehennemi.site) | 8 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 24 | HdFilmCehennemi2 | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [hdfilmcehennemi2.site](https://hdfilmcehennemi2.site) | 2 | 2026-09-20 | 2026-09-16 | Aktif |  |
| 25 | HDFilmDelisi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [hdfilmdelisi](https://hdfilmdelisi.site) | 1 | 2026-09-29 | 2026-09-16 | Aktif |  |
| 26 | HDFilmIzle | [Ripplay/cloudstream-repo](https://github.com/Ripplay/cloudstream-repo) | [hdfilmizle.site](https://hdfilmizle.site) | 8 | 2026-08-24 | 2026-08-24 | Aktif |  |
| 27 | JetFilmizle | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [jetfilmizle](https://jetfilmizle.site) | 47 | 2026-09-29 | 2026-09-16 | Aktif |  |
| 28 | LoveFilm | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [lovefilm](https://lovefilm.site) | 1 | 2026-09-16 | 2026-09-16 | Duplicate |  |
| 29 | LoveFilm | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [lovefilm.site](https://lovefilm.site) | 2 | 2026-09-27 | 2026-09-17 | Aktif |  |
| 30 | SelcukFlix | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [selcukflix](https://selcukflix.site) | 2 | 2026-09-29 | 2026-09-22 | Aktif |  |
| 31 | SetFilmIzle | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [setfilmizle.uk](https://setfilmizle.uk) | 32 | 2026-10-04 | 2026-10-04 | Aktif |  |
| 32 | SezonlukDizi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [sezonlukdizi](https://sezonlukdizi.site) | 9 | 2026-09-29 | 2026-09-22 | Aktif |  |
| 33 | Sinefy | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [sinefy.site](https://sinefy.site) | 1 | 2026-09-20 | 2026-09-15 | Aktif |  |
| 34 | SinemaCX | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [sinema.cx](https://sinema.cx) | 25 | 2026-10-04 | 2026-10-04 | Aktif |  |
| 35 | Sinewix | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [sinewix](https://sinewix.site) | 2 | 2026-09-29 | 2026-09-16 | Aktif |  |
| 36 | Sinezy | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [sinezy.site](https://sinezy.site) | 3 | 2026-09-29 | 2026-09-15 | Aktif |  |
| 37 | Streamed | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [streamed.site](https://streamed.site) | 29 | 2026-10-05 | 2026-10-06 | Aktif |  |
| 38 | TvDiziler | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [tvdiziler.site](https://tvdiziler.site) | 2 | 2026-09-27 | 2026-09-29 | Aktif |  |
| 39 | UltraFilmizle | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [ultrafilmizle.org](https://ultrafilmizle.org) | 12 | 2026-09-23 | 2026-09-20 | Aktif |  |
| 40 | Webteizle | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [webteizle](https://webteizle.site) | 1 | 2026-09-16 | 2026-09-16 | Duplicate |  |
| 41 | WebteIzle | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [webteizle](https://webteizle.site) | 21 | 2026-09-29 | 2026-09-16 | Aktif |  |
| 42 | YabanciDizi | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [yabancidizi.site](https://yabancidizi.site) | 17 | 2026-09-20 | 2026-10-06 | Aktif |  |
<!-- KAYIT-DURUMU:OTOMATIK-SON -->

## Kaynak Repoları, Kullanılan Siteler ve GitHub Güncelleme Tarihleri

Bu bölümde kaynak olarak taranan **6 repo** tek tek gösterilir. `Repo son güncelleme`, bizim depomuzun değil, ilgili kaynak GitHub reposunun GitHub API `updated_at` değeridir. Site sütununda yalnızca bu depoda listelenen kayıtlar bulunur; `—` olan repo tarama havuzunda bulunmasına rağmen aktif/duplicate katalog kaydı olarak kullanılmıyor.

| Kaynak repo | Repo son güncelleme (GitHub) 
|---|---|---|
| [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | 2026-10-05 19:34:18 UTC | 
| [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | 2026-10-05 19:34:08 UTC |
| [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | 2026-10-05 19:33:02 UTC | 
| [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | 2026-10-05 19:53:27 UTC |
| [Ripplay/cloudstream-repo](https://github.com/Ripplay/cloudstream-repo) | 2026-09-18 21:27:51 UTC |

## İstenmeyenler (Delete-Zone) - 70 unique

| Eklenti | Kaynak Ornek | Site | Dil | Tur |
|---------|--------------|------|-----|-----|
| 🟥 AnimeAV | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [animeav1.com](https://animeav1.com) | mx | Anime |
| 🟥 AnimeciX | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [animecix.tv](https://animecix.tv) | tr | Anime |
| 🟥 Animejara | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | — | mx | Anime |
| 🟥 AnimeWorld | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [www.animeworld.ac](https://www.animeworld.ac) | it | Anime |
| 🟥 AnimeYTX | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [animeyt.cc](https://animeyt.cc) | mx | Anime |
| 🟥 Anizium | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [anizium.co](https://anizium.co) | tr | Anime,Movie |
| 🟥 Anizm | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | — | tr | Anime |
| 🟥 AsyaAnimeleri | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [asyaanimeleri.top](https://asyaanimeleri.top) | tr | Anime |
| 🟥 AsyaWatch | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [asyawatch.com](https://asyawatch.com) | tr | AsianDrama |
| 🟥 Atv | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [atv.com.tr](https://atv.com.tr) | tr | Live,TvSeries |
| 🟥 AyzenTv | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | — | tr |  |
| 🟥 BasketballReplays | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | — | en | Live |
| 🟥 BelgeselX | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [belgeselx.com](https://belgeselx.com) | tr | Documentary |
| 🟥 BirAsyaDizi | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | — | tr | AsianDrama |
| 🟥 CizgiMax | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [cizgimax.online](https://cizgimax.online) | tr | Cartoon,Anime,Movie |
| 🟥 CizgiVeDizi | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [cizgivedizi.net](https://cizgivedizi.net) | tr |  |
| 🟥 DiziKorea | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizikorea.vip](https://dizikorea.vip) | tr | AsianDrama |
| 🟥 DMax | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [dmax.com.tr](https://dmax.com.tr) | tr | Documentary,Live |
| 🟥 DoramasLatinoX | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [doramaslatinox.com](https://doramaslatinox.com) | mx | AsianDrama |
| 🟥 DramaDizilerim | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [dramadizilerim.com](https://dramadizilerim.com) | tr | TvSeries |
| 🟥 Dubbindo | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [www.dubbindo.site](https://www.dubbindo.site) | id | AsianDrama |
| 🟥 EnglishW | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [themoviedb.org](https://themoviedb.org) | en | Movie,TvSeries |
| 🟥 Esheaq | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [esk.onl](https://esk.onl) | ar | Movie,TvSeries |
| 🟥 Filmmirasım | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [filmmirasim.ktb.gov.tr](https://filmmirasim.ktb.gov.tr) | tr | Documentary |
| 🟥 Flixlatam | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [flixlatam.com](https://flixlatam.com) | mx | Movie |
| 🟥 Footballia | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | — | en | Live |
| 🟥 FootReplays | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [www.footreplays.com](https://www.footreplays.com) | en | Others |
| 🟥 FsTv | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | — | tr |  |
| 🟥 FullRaces | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [fullraces.com](https://fullraces.com) | en | Movie |
| 🟥 FullReplays | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [fullreplays.com](https://fullreplays.com) | en |  |
| 🟥 Gnulahd | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [ww3.gnulahd.nu](https://ww3.gnulahd.nu) | mx | Movie,Anime,TvSeries |
| 🟥 Iwatchtheoffice | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [iwatchtheoffice.cc](https://iwatchtheoffice.cc) | en | Movie |
| 🟥 JPFilms | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [jp-films.com](https://jp-films.com) | en | AsianDrama |
| 🟥 KanalD | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [kanald.com.tr](https://kanald.com.tr) | tr | TvSeries,Live |
| 🟥 KissKH | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [kisskh.id](https://kisskh.id) | en | AsianDrama |
| 🟥 Krmzy | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [krmzy.org](https://krmzy.org) | ar | TvSeries |
| 🟥 KultFilmler | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [kultfilmler.net](https://kultfilmler.net) | tr | Movie,TvSeries |
| 🟥 Latanime | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [latanime.org](https://latanime.org) | mx | Movie |
| 🟥 LayarKaca | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [tv12.lk21official.cc](https://tv12.lk21official.cc) | id | Movie,TvSeries |
| 🟥 Movix | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [movix.fun](https://movix.fun) | fr | Movie,TvSeries,Anime |
| 🟥 MRC-Live | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | — | tr | Live |
| 🟥 MRC-Naughty | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | — | tr |  |
| 🟥 MRC-Plus | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | — | tr |  |
| 🟥 Nekokun | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | — | id | Anime |
| 🟥 OK | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [ok.ru](https://ok.ru) | ru | Movie,TvSeries |
| 🟥 OnShort | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [onshort.net](https://onshort.net) | en | AsianDrama |
| 🟥 OpenAnime | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [openani.me](https://openani.me) | tr | Anime |
| 🟥 OwnedSites | [Ripplay/cloudstream-repo](https://github.com/Ripplay/cloudstream-repo) | [dizibal.com](https://dizibal.com) | tr | Movie,TvSeries |
| 🟥 RareFilmm | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [rarefilmm.com](https://rarefilmm.com) | en | Movie |
| 🟥 RecTV | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | — | tr | Movie,Live,TvSeries |
| 🟥 RecTVBC | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | — | tr | Movie,Live,TvSeries |
| 🟥 Showtv | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [showtv.com.tr](https://showtv.com.tr) | tr | Live,TvSeries |
| 🟥 Sokuja | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [x6.sokuja.uk](https://x6.sokuja.uk) | id | Anime,AnimeMovie |
| 🟥 Startv | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [startv.com.tr](https://startv.com.tr) | tr | Movie |
| 🟥 Subsplease | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [subsplease.org](https://subsplease.org) | en | Anime |
| 🟥 Supercartoons | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [i.imgur.com](https://i.imgur.com) | en | Cartoon |
| 🟥 TLC | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [tlctv.com.tr](https://tlctv.com.tr) | tr |  |
| 🟥 TLCtr | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [tlctv.com.tr](https://tlctv.com.tr) | tr | Movie |
| 🟥 TRanimaci | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [tranimaci.com](https://tranimaci.com) | tr | Anime |
| 🟥 TRasyalog | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [asyalog.co](https://asyalog.co) | tr | TvSeries |
| 🟥 TurkAnime | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [www.turkanime.co](https://www.turkanime.co) | tr | Anime |
| 🟥 TurkishW | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [themoviedb.org](https://themoviedb.org) | tr | Movie,TvSeries |
| 🟥 Tv8 | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [tv8.com.tr](https://tv8.com.tr) | tr | Live,TvSeries |
| 🟥 TVGarden | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | — | en | Live |
| 🟥 Watch2Movies | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [movies2watch.watch](https://movies2watch.watch) | en | Movie,TvSeries |
| 🟥 WatchWrestling | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | — | en | Live |
| 🟥 Wcoflix | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [www.wcoflix.tv](https://www.wcoflix.tv) | en | Anime,Cartoon |
| 🟥 Yablom | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [yablom.com](https://yablom.com) | fr | Movie |
| 🟥 YesilCamTv | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [yesilcamtv.com.tr](https://yesilcamtv.com.tr) | tr | Movie |
| 🟥 YoTurkish | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [yoturkish.to](https://yoturkish.to) | en | TvSeries |

## Yasal Uyarı ve Sorumluluk Reddi (Disclaimer)
Bu depo kişisel arşivleme amacıyla oluşturulmuştur; hiçbir ticari amacı yoktur. Bu depo (ve GitHub sunucuları) hiçbir video, ses dosyası, medya veya telif hakkıyla korunan materyal barındırmaz, kopyalamaz veya dağıtmaz. Bu depo yalnızca internette herkese açık olarak paylaşılan üçüncü taraf eklentilerin (`.cs3`) doğrudan GitHub RAW adreslerini derleyen metin tabanlı bir JSON dizinidir ("Yalnızca Endeks"). Listelenen eklentilerin kodları, işleyişleri veya hangi web sitelerinden veri çektikleri üzerinde bu deponun hiçbir kontrolü, sahipliği veya sorumluluğu yoktur; tüm sorumluluk eklentilerin orijinal geliştiricilerine ve veriyi barındıran kaynak web sitelerine aittir. Bu depo yalnızca bağlantıları listeleyen bir köprü görevi gördüğü için telif hakkı ihlali iddialarının muhatabı değildir; içerik kaldırma talepleri (DMCA) doğrudan içerikleri sunan kaynak web sitelerine veya eklentilerin orijinal GitHub depolarına yapılmalıdır. Bu depo, 5846 sayılı Fikir ve Sanat Eserleri Kanunu ve 5651 sayılı Kanun kapsamında da eser barındırmaz, çoğaltmaz veya iletmez; yalnızca kamuya açık kaynaklardaki `.cs3` dosyalarına bağlantı sağlar. 5651 sayılı Kanunun 4. maddesinin ikinci fıkrası gereği içerik sağlayıcı, bağlantı sağladığı başkasına ait içerikten sorumlu değildir; ancak aynı maddenin istisnası saklıdır: sunuş biçiminden bağlantı verilen içeriğin benimsendiği ve kullanıcının o içeriğe ulaşmasının amaçlandığı açıkça belli ise sorumluluk doğabilir. Bu depo, listedeki hiçbir eklentiyi veya eklentilerin veri çektiği kaynakları benimsemez ve tavsiye etmez; liste salt teknik bir indekstir. Hak sahipleri 5651 sayılı Kanunun 9. maddesi uyarınca uyarı yöntemiyle bildirimde bulunursa ilgili bağlantı derhal kaldırılır.

This repository is created for personal archiving purposes and has no commercial intent. This repository does not host, store, copy, or distribute any video, audio, media files, or copyrighted material; it serves merely as a text-based JSON index containing direct links to third-party `.cs3` plugins already publicly available on the internet ("Index Only"). The owner of this repository does not develop, host, or control any of the listed plugins, their source code, operation, or the websites these plugins scrape; all liability lies strictly with the original plugin developers and the respective websites hosting the media. As this repository only provides a compilation of text-based URLs, it is not liable for copyright infringement; any DMCA takedown requests must be directed to the actual websites hosting the copyrighted content or to the original developers' repositories. Under Turkish law (FSEK No. 5846 and Law No. 5651), this repository does not host, reproduce, or communicate any work; it merely provides links to `.cs3` files publicly available on the internet. Under Article 4/2 of Law No. 5651, a content provider is not liable for third-party content to which it merely provides a link; however, the exception in that provision is reserved: liability may arise where the presentation clearly shows that the linked content is adopted and that users are intended to reach it. This repository does not adopt or recommend any of the listed plugins or the sources they use; the list is a purely technical index. If rights holders send a notice under Article 9 of Law No. 5651, the relevant link will be removed promptly
