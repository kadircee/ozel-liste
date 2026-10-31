# developer (ozel-liste)
Bu depo test CloudStream deposudur; yalnızca Türkçe film/dizi eklentilerini ve test seçtiği kaynakları barındırır. Canlı yayın, NSFW ve yabancı dil içerikli eklentiler kullanıcı tercihi gereği listeye alınmamıştır. Bilinçli iki istisna vardır: **Streamed** (`en`, `Live`) ve **Sinewix** (`tvTypes` içinde `Anime` taşır); ikisi de `audit.py` / `registry.py` içindeki `EXCEPTIONS` kümesiyle filtre dışında tutulur.

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
├── .github/
│   └── workflows/mirror.yml → günlük kaynak senkronu + tablo tazeleme
├── repo.json            → CloudStream'in açtığı depo tanımı
├── plugins.json         → eklenti listesi
├── registry.json        → makine-okur kayıt modeli (aday ve durum sayıları aşağıdaki rapor notuna göre değişkendir)
├── registry.py          → model araçları (--sync / --check / --render [--write])
├── audit.py             → kaynak depoları tarih bazında denetler (--check = rapor/varsayılan, --apply = yazar)
├── update.py            → kaynak verilerini ve tablo alanlarını senkronize eder (--check / --purge / --no-table)
└── DEPO-BILGILERI.md    → bu doküman (tablo bloğu registry.json'dan üretilir)
```
> **Rapor sayıları hakkında:** Bu dokümandaki aday, aktif, duplicate, istenmeyen ve kaynak depo sayıları sabit kural değildir; yalnızca üretildiği andaki rapor özetidir. Güncel sayılar için `registry.json`, `plugins.json` ve betik çıktıları esas alınır. Bu sayılar kaynaklar değiştikçe değişebilir.

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

**1. Kaynak seçimi — yalnızca tarih esastır; versiyon ölçüt değildir:**
- Eklenti tarihi yalnızca `builds` dalındaki `.cs3` dosyasına ait son commit'ten alınır; deponun genel `pushed_at` değeri veya başka dallardaki commit tarihleri seçim ölçütü değildir. Aynı eklentinin birden fazla kaynaktaki kopyaları arasından tarihi en yeni olan otomatik seçilir; versiyon numarası kararı etkilemez.
- Kaynak kararı verilmeden önce `audit.py`, her kaynak deposunun tüm dallarını ve dal ağaçlarındaki `.cs3` dosyalarını tarar. `builds` dışındaki bir dalda `.cs3` bulunursa `ALTERNATİF-DAL .cs3` olarak raporlanır; doğrulanmadan otomatik olarak Aktif yapılmaz. Esas manifest ve artefakt çifti `builds` dalındadır.
- Kaynak manifestinde `status: 0` olan kayıtlar devre dışıdır: `plugins.json` dosyasından silinir, denetim havuzuna alınmaz ve sonraki çalıştırmalarda yeniden eklenmez. Registry tablosunda yalnızca tarih geçmişi amacıyla Duplicate adayı olarak görünebilir.

**1a. Eşit tarihli kaynaklar — otomatik seçim:**
İki veya daha fazla kaynağın güncelleme tarihi aynıysa kaynak depoları alfabetik olarak sıralanır ve ilk sıradaki kaynak otomatik seçilir. `audit.py` bu kararı kendisi verir; kullanıcıya soru sormaz. Versiyon numarası eşitlik çözümünde kullanılmaz.

**1b. Tüm dal taraması:**
`audit.py`, registry ve denetim havuzunda bulunan her kaynak deposunu ve mevcut tüm dallarını (`builds` dahil) tarar. Dal sayısı ve kaynak depo sayısı sabit değildir.

**2. Tablo bakımı — `Tüm Repolar` karşılaştırılan tüm adayları içerir:**
- Yeni adaylar için varsayılan filtre `language == tr` ve `tvTypes ⊆ {Movie, TvSeries, Documentary}` kuralıdır. `EXCEPTIONS` kümesindeki adlar (`streamed`, `sinewix`) bu filtreyi bilinçli olarak aşar.
- Gruplama **normalize ada** göre yapılır: aynı adı taşıyan kopyalar (ör. `DiziPal`) tek yarışta birleşir; farklı adlar ayrı kayıt kalır. Ad normalizasyonunda büyük `I` ve noktasız `ı` `i` sayılır (`HDFilmIzle` = `HdFilmIzle`).
- `Site (domain)` her zaman `[domain](https://domain)` linkli olmalı (tıklanabilir); link metni host adıyla aynı olmalıdır. `update.py` bu alanı kaynak manifestindeki site adresinden tazeler (CDN adresleri hariç).
- `kadircee/ozel-liste` bir kaynak deposu değil, derleme deposu olduğu için `Tüm Repolar`da yer almaz.
- `İstenmeyenler` için ayrı bir metin listesi tutulmaz; tek doğruluk kaynağı tablodur.
- İstenmeyenler tablosundaki benzersiz ad sayısı, `audit.py` çıktısındaki `yasakli sayisi` ve `registry.json` içindeki istenmeyen grup sayısıyla eşleşmelidir. Bu sayılar değişebilir; denetim sırasında güncel değerler karşılaştırılır. Başlık (`## İstenmeyenler ...`) **kendi satırında** olmalıdır. Tablo satırına eklenirse GitHub başlığı işleyemez ve `audit.py` yasaklı listesini bulamaz; boş liste tespit edildiğinde **`exit 2` ile durur** (sessiz geçiş yapılmaz).

**3. Kayıt durumu — tek eksen (Seçim):**
Model yalnızca `Seçim` ekseninden oluşur: `Aktif` (yarışı kazandı, `plugins.json` dosyasında) / `Duplicate` (kaybetti, dosyada yok) / `İstenmeyen` (hiç değerlendirmeye alınmadı) (bkz. **Kayıt Durumu Modeli**). `status` bilgisi kaynağa bırakılmıştır; kaynak ne yayımlıyorsa (`1`, `0`, …) `update.py` ile olduğu gibi yansıtılır. Bu depo site canlılığını izlemez.
- İkon domaininin ölü görünmesi tek başına karar nedeni değildir; asıl erişim eklentinin kendi sağlayıcı koduna bağlıdır.
- **Simge/görsel kaynağı:** Her kayıt için `iconUrl`, seçilen kaynak deponun `builds/plugins.json` manifestinden alınır. `%size%` yer tutucusu sabit `sz=128` değerine çevrilir; simge dosyası bu depoya kopyalanmaz ve görsel yeniden barındırılmaz. Kaynak manifestindeki simge değişirse `update.py` ile güncellenir.
- Kaynak ilerlediyse `update.py` ile senkronize et ve `Bizim Tarih`i eşitle; `status` alanına dokunma, kaynakta ne yayımlanıyorsa onu al.

## Tarih Takip Kuralı

Seçim yalnızca `builds` dalındaki `.cs3` dosyasının son commit tarihine göre yapılır; diğer dallar yalnızca alternatif dal raporu içindir.

Tablodaki her satırda eklentiye ait iki tarih vardır: **Kaynak Tarih** (kaynak deponun `builds` dalında o `.cs3` dosyasına dokunan son commit'in tarihi) ve **Bizim Tarih** (kaynak kaydını en son benimsediğimiz tarih). **Bizim Tarih**, bu deponun genel son commit tarihi değildir. İşlem, bu iki tarihin karşılaştırılmasına dayanır:

- **Kaynak Tarih > Bizim Tarih** → kaynak ilerlemiş demektir. `python update.py` senkronu yapar ve satırdaki `v`, `Kaynak Tarih`, `Bizim Tarih` alanlarını canlı veriyle tazeler (Bizim Tarih, Kaynak Tarih'e eşitlenir). `status` dahil kaynak ne yayınlıyorsa aynen alınır. Versiyon numarasına bakılmaz.
- **Kaynak Tarih == Bizim Tarih** → yapacak iş yok.

`update.py` her çalıştırmada tabloyu tazeler: `v` ← kaynak manifesti, `Kaynak Tarih` ← `builds` dalındaki `.cs3` dosyasının son commit tarihi (GitHub API), `Bizim Tarih` ← senkron tarihi, `Site (domain)` ← kaynak simgesindeki site adresi. Kaynakta artık yayınlanmayan satırlar tablodan düşürülür ve sıra numaraları yeniden verilir. `registry.py --check` bu alanları `plugins.json` ile karşılaştırır; tablo `v` değeri veya tarih kuralı tutmuyorsa **exit 1** verir.

## Kayıt Durumu Modeli

Her kayıt tek eksene sahiptir:

- **Seçim:** `Aktif` (yarışı kazandı, `plugins.json`'da) / `Duplicate` (kaybetti, dosyada yok) / `İstenmeyen` (hiç yarışa girmedi).

| Seçim | Anlamı | plugins.json |
| Aktif | Kazanan kayıt | var (`status` kaynağın yayınladığı değer) |
| Duplicate | Yarışı kaybetti, dosyada yok | yok |
| İstenmeyen | Hiç değerlendirmeye alınmadı | yok |


**Araçlar:** `python registry.py --sync` (tablolar + `plugins.json` → `registry.json`), `--check` (şema + küme + tarih + tablo/`plugins.json` tazeliği; ihlalde exit 1), `--render [--write]` (tabloyu üretir). `Seçim`, `plugins.json` dosyasından türetilir (dosyada olan = Aktif); grup başına en fazla 1 Aktif olabilir ve Aktif kümesi `plugins.json` ile birebir aynı olmalıdır. Eklenti alanları (`status`, `version`, `fileSize`, `fileHash`, `description`, `authors`, `language`, `tvTypes`) kaynak `builds/plugins.json` dosyasından olduğu gibi alınır (`update.py`).

## Kaynak Senkronizasyonu (update.py)
```bash
python update.py --check    # yazmadan sadece farkları raporlar (fark varsa exit 1)
python update.py            # farkları uygular, plugins.json + tablo alanlarını günceller
python update.py --purge    # push sonrası jsDelivr önbelleğini temizler
python update.py --no-table # yalnızca plugins.json senkronu (tabloya dokunmaz)
```
Kaynak `builds/plugins.json` adresi, listedeki `.cs3` adresinden türetilir (`https://raw.githubusercontent.com/<owner>/<repo>/builds/<Isim>.cs3` → aynı klasördeki `plugins.json`). Senkronize edilen alanlar: `status, version, fileSize, fileHash, description, authors, language, tvTypes` (Pure Mirror — kaynak ne yayınlıyorsa aynen alınır). Ayrıca `DEPO-BILGILERI.md` tablosundaki `v`, `Kaynak Tarih`, `Bizim Tarih` ve `Site (domain)` alanları tazelenir; kaynakta artık bulunmayan satırlar tablodan düşürülür. Tarih tazeleme için GitHub token gerekir (`GITHUB_TOKEN` ya da `gh auth login`); token yoksa yalnızca tarih alanları atlanır, senkron durmaz.

> **Not:** Kaynak senkronu GitHub Actions ile otomatik çalışır (`.github/workflows/mirror.yml`: her gün 05:00 UTC ve `workflow_dispatch` ile manuel tetikleme). Akış: `update.py` → `registry.py --sync` → `registry.py --render --write` → `registry.py --check` (sert kapı) → commit+push → `update.py --purge` → `audit.py --check` (rapor; hata olsa da commit'i engellemez). Yerelde elle çalıştırmak da mümkündür. Kaynakta bulunamayan veya `status: 0` olan kayıt `[SILINDI]` olarak listeden düşer; kaynak manifesti 404 ise audit kaynağı atlar ve aktif katalogda kayıt bırakılmaz.

## Güncelleme
Yeni bir değişiklik yapıldığında:
```bash
python update.py --check          # kaynak farkı var mı bak (exit 1 = var)
python update.py                  # plugins.json + tablo alanlarını tazele
python registry.py --sync         # tablo + plugins.json -> registry.json
python registry.py --render --write  # tablo bloğunu yeniden üret
python registry.py --check        # model + tazelik denetimi (exit 1 = ihlal)
python audit.py --check           # kaynak karar denetimi (rapor)
git add plugins.json DEPO-BILGILERI.md registry.json registry.py audit.py update.py .github/workflows/mirror.yml
git -c user.name="kadircee" -c user.email="kadircee@users.noreply.github.com" \
    commit -m "plugins.json: aciklama"
git push
python update.py --purge          # push sonrası jsDelivr temizliği
```
Push sonrası jsDelivr önbelleği için:
```
https://purge.jsdelivr.net/gh/kadircee/ozel-liste@main/plugins.json
```
CloudStream tarafında depo yenilendiğinde yeni liste otomatik çekilir. Kaynak senkronu her gün otomatik koşar (`.github/workflows/mirror.yml`); acil durumda yerelde **elle** de çalıştırılabilir (`python update.py`, ardından `python registry.py --sync`, `python registry.py --render --write`, `python registry.py --check` ve `python audit.py --check`). Güncelleme öncesi `update.py --check` ile kontrol etmek iyi alışkanlıktır.

## Tüm Repolar - Alfabetik Liste

Bu bölüm 2026-10-31 tarihinde `registry.json` ve `plugins.json` üzerinden yeniden oluşturuldu. Liste, **40** kayıt satırını (**33 aktif**, **7 duplicate**) ve kaynak karşılaştırmalarını birlikte gösterir; 404 ve `status: 0` kaynak kayıtları katalogdan çıkarılmıştır.

Aynı normalize ada sahip kayıtlar tek grup olarak değerlendirilir. En güncel kaynak `Aktif`, diğer kaynaklar `Duplicate` olarak gösterilir. `status` alanı kaynak manifestinden Pure Mirror kuralıyla alınır.

Toplam satır: 40 · Aktif: 33 · Duplicate: 7.

<!-- KAYIT-DURUMU:OTOMATIK-BASLANGIC -->
| # | Eklenti | Kaynak | Site (domain) | v | Kaynak Tarih | Bizim Tarih | Seçim | Not |
|---|---|---|---|---|---|---|---|---|
| 1 | Ddizi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [ddizi.im](https://ddizi.im) | 24 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 2 | DiziBox | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizibox.live](https://dizibox.live) | 25 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 3 | Dizilla | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizilla.now](https://dizilla.now) | 93 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 4 | Dizilla | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [dizilla.club](https://dizilla.club) | 10 | 2026-09-27 | 2026-09-22 | Duplicate |  |
| 5 | DiziMom | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizimom.plus](https://dizimom.plus) | 64 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 6 | DiziMom | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [dizimom.wiki](https://dizimom.wiki) | 13 | 2026-10-22 | 2026-09-22 | Duplicate |  |
| 7 | DiziPal2 | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [dizipal2142.com](https://dizipal2142.com) | 7 | 2026-10-22 | 2026-10-22 | Aktif |  |
| 8 | DiziPod | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [dizipod.com](https://dizipod.com) | 3 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 9 | DiziYo | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [diziyo.so](https://diziyo.so) | 1 | 2026-09-07 | 2026-10-06 | Aktif |  |
| 10 | DiziYou | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [diziyou.one](https://diziyou.one) | 26 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 11 | FilmEkseni | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [filmekseni.vip](https://filmekseni.vip) | 1 | 2026-09-07 | 2026-09-16 | Duplicate |  |
| 12 | FilmEkseni | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [filmekseni.vip](https://filmekseni.vip) | 4 | 2026-10-22 | 2026-10-22 | Aktif |  |
| 13 | FilmHane | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [filmhane.shop](https://filmhane.shop) | 1 | 2026-09-07 | 2026-09-07 | Aktif |  |
| 14 | FilmIzyon | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [filmizyon.com](https://filmizyon.com) | 8 | 2026-10-22 | 2026-10-22 | Aktif |  |
| 15 | FilmMakinesi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [filmmakinesi.film](https://filmmakinesi.film) | 59 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 16 | FilmMakinesi | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [filmmakinesi.to](https://filmmakinesi.to) | 5 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 17 | FilmModu | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [filmmodu.one](https://filmmodu.one) | 19 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 18 | FullHDFilm | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [hdfilm.us](https://hdfilm.us) | 36 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 19 | FullHDFilmizlesene | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [fullhdfilmizlesene.de](https://fullhdfilmizlesene.de) | 33 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 20 | HDFilmCehennemi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [hdfilmcehennemi.com](https://hdfilmcehennemi.com) | 58 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 21 | HDFilmCehennemi | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [hdfilmcehennemi.nl](https://hdfilmcehennemi.nl) | 8 | 2026-09-22 | 2026-09-22 | Duplicate |  |
| 22 | HdFilmCehennemi2 | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [hdfilmcehennemi2.biz](https://hdfilmcehennemi2.biz) | 5 | 2026-09-20 | 2026-09-20 | Aktif |  |
| 23 | HDFilmDelisi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [hdfilmdelisi.com](https://hdfilmdelisi.com) | 1 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 24 | HDFilmIzle | [Ripplay/cloudstream-repo](https://github.com/Ripplay/cloudstream-repo) | [hdfilmizle.ink](https://hdfilmizle.ink) | 8 | 2026-08-24 | 2026-08-24 | Aktif |  |
| 25 | JetFilmizle | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [jetfilmizle.de](https://jetfilmizle.de) | 48 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 26 | LoveFilm | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [lovefilmizle.net](https://lovefilmizle.net) | 1 | 2026-09-07 | 2026-09-16 | Duplicate |  |
| 27 | LoveFilm | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [lovefilmizle.net](https://lovefilmizle.net) | 6 | 2026-09-27 | 2026-09-27 | Aktif |  |
| 28 | SelcukFlix | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [selcukflix.co](https://selcukflix.co) | 3 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 29 | SetFilmIzle | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [setfilmizle.uk](https://setfilmizle.uk) | 32 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 30 | SezonlukDizi | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [sezonlukdizi6.com](https://sezonlukdizi6.com) | 9 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 31 | Sinefy | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [sinefy3.com](https://sinefy3.com) | 4 | 2026-10-22 | 2026-10-22 | Aktif |  |
| 32 | SinemaCX | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [sinema.cx](https://sinema.cx) | 26 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 33 | Sinewix | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [sinewix.site](https://sinewix.site) | 3 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 34 | Sinezy | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [sinezy.to](https://sinezy.to) | 8 | 2026-10-22 | 2026-10-22 | Aktif |  |
| 35 | Streamed | [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | [streamed.pk](https://streamed.pk) | 29 | 2026-10-15 | 2026-10-15 | Aktif |  |
| 36 | TvDiziler | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [tvdiziler.tv](https://tvdiziler.tv) | 6 | 2026-09-27 | 2026-09-29 | Aktif |  |
| 37 | UltraFilmizle | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [ufilmizle.com](https://ufilmizle.com) | 14 | 2026-09-23 | 2026-09-23 | Aktif |  |
| 38 | Webteizle | [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | [webteizle3.xyz](https://webteizle3.xyz) | 1 | 2026-09-07 | 2026-09-16 | Duplicate |  |
| 39 | WebteIzle | [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | [webteizle3.xyz](https://webteizle3.xyz) | 21 | 2026-10-28 | 2026-10-28 | Aktif |  |
| 40 | YabanciDizi | [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | [yabancidizi.news](https://yabancidizi.news) | 17 | 2026-09-20 | 2026-10-06 | Aktif |  |
<!-- KAYIT-DURUMU:OTOMATIK-SON -->

## Kaynak Depoları ve Güncelleme Tarihleri

Bu bölümde kaynak olarak taranan fiili **5 depo** listelenir. Depo kümesi ve sayısı sabit değildir; yeni veya artık kullanılmayan kaynaklarla değişebilir. Aşağıdaki tarihler **bu deponun güncellenme veya commit tarihleri değildir**; yalnızca ilgili kaynak depoların GitHub API `updated_at` değerleridir.

| Kaynak depo | Kaynak deponun son güncelleme zamanı (GitHub API `updated_at`) |
|---|---|
| [blackhope01/cloudstream-plugins](https://github.com/blackhope01/cloudstream-plugins) | 2026-10-31 06:41:12 UTC | 
| [feroxx/Kekik-cloudstream](https://github.com/feroxx/Kekik-cloudstream) | 2026-10-30 00:16:41 UTC |
| [Kraptor123/Cs-Karma](https://github.com/Kraptor123/Cs-Karma) | 2026-10-27 22:27:50 UTC | 
| [lepotane/MRC-builds](https://github.com/lepotane/MRC-builds) | 2026-10-24 18:46:17 UTC |
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
