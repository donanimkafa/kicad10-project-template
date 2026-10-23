# KiCad 10 Proje Şablonu

[![KiCad CI](https://github.com/donanimkafa/kicad10-project-template/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/donanimkafa/kicad10-project-template/actions/workflows/ci.yml)

> Bu repo bir **şablondur**. Gerçek projeler için **Use this template** düğmesiyle yeni bir repo türetin ve çalışmayı o repoda yapın. Türetilen repoda rozet ve changelog bağlantılarındaki `donanimkafa/kicad10-project-template` ifadesini kendi kullanıcı/kurum ve depo adınızla değiştirin.

KiCad 10 projeleri için bu şablon iki şeyi bir arada sunar:

1. **Teknik otomasyon:** `kicad-cli` ve Python ile ERC/DRC kontrolleri ve üretim belgeleri (şematik PDF, BOM, Gerber/Drill, montaj PDF, STEP).
2. **Çalışma akışı:** Gereksinimden teste kadar işleri Issue formları, PR kontrol listesi, etiketler ve proje panosuyla kayıt altına alan bir süreç.

## İçindekiler

- [Hızlı başlangıç](#hızlı-başlangıç)
- [Çalışma akışı](#çalışma-akışı)
- [Tasarım aşamaları](#tasarım-aşamaları)
- [Proje yapısı](#proje-yapısı)
- [Şematik hiyerarşisi ve proje ayarları](#şematik-hiyerarşisi-ve-proje-ayarları)
- [Yerel kullanım](#yerel-kullanım)
- [GitHub Actions](#github-actions)
- [Üretim çıktıları](#üretim-çıktıları)
- [Commit mesajı kuralı](#commit-mesajı-kuralı)

## Hızlı başlangıç

1. Bu sayfada **Use this template → Create a new repository** ile yeni proje reposunu oluşturun.
2. Repoyu klonlayın ve KiCad Proje Yöneticisi'nde `hardware/kicad10-project-template.kicad_pro` dosyasını açın. Alt sayfaları kök şematik üzerinden kullanın.
3. `CHANGELOG.md` içindeki `Company:` alanını ve proje Text Variables alanındaki kart adı, tasarımcı ve proje kodunu kendinize göre düzenleyin. Başlangıç aşaması `DRAFT` olarak ayarlıdır.
4. GitHub'da **Actions → Etiketleri Kur → Run workflow** ile süreç etiketlerini oluşturun (bkz. [Etiketler](#etiketler)).
5. **Issues → New issue → 01 · Yeni kart talebi** ile ilk kartınızın gereksinimlerini yazın.

## Çalışma akışı

Temel akış: **Issue → çalışma dalı → PR → main → sürüm etiketi**.

Her iş bir Issue ile başlar. Güncel `main` üzerinden o işe özel kısa ömürlü bir dal açılır; değişiklikler `main` hedefli bir Pull Request ile incelenir. Sürekli açık bir `dev` dalı gerekmez.

### Bir işi baştan sona yürütme

1. Gereksinimi veya sorunu Issue'da tanımlayın; kabul kriterlerini yazın.
2. Güncel `main` üzerinden örneğin `feat/12-power-input` veya `fix/18-usb-esd` adlı bir çalışma dalı açın. Sayı ilgili Issue numarasıdır.
3. Tasarımı ve CHANGELOG'u güncelleyin. Çalışma dalını gönderip `main` hedefli bir Draft PR açın; otomatik çıktıları geliştirme sırasında da inceleyin.
4. Tasarımın durumuna göre `PHASE` seçin. PR'da CI sonucunu ve üretilen belgeleri inceleyin; inceleme tamamlandığında PR'ı `main` ile birleştirin ve çalışma dalını silin.
5. Üretim sürümü hazırlarken hedef revizyon ve tarih ile CHANGELOG'u tamamlayın, `PHASE: release` seçin ve bu değişiklikleri de PR üzerinden birleştirin. Etiket oluşturulmadan önce başlık revizyonu önceki Git etiketini gösterebilir; etiket derlemesi yeni sürümü uygular.
6. `main` üzerindeki onaylı sürüm commit'ine `v1.0.1` gibi bir etiket gönderin. Etiket derlemesinin kontrolleri geçmesiyle üretim dosyaları GitHub Release'e eklenir. Gelen kartın test sonuçlarını bring-up Issue'sunda kaydedin.

`main`, incelenmiş çalışmaların birleştiği daldır; üretime gönderilecek belirli sürüm, etiketi ve Release çıktılarıyla tanımlanır. Her PR için sürüm etiketi oluşturmak gerekmez. PR zorunluluğu için GitHub depo kurallarını ayrıca yapılandırın; şablon bu kuralı kendiliğinden etkinleştirmez. Sürüm etiketlerini `main` üzerinden oluşturmak bu çalışma akışının kuralıdır; mevcut CI etiketin hangi dalda olduğunu ayrıca doğrulamaz.

| # | Aşama | Kayıt yeri | Etiket |
|---|---|---|---|
| 0 | Gereksinim | Issue formu **01 · Yeni kart talebi** | `stage:requirements`, `type:board` |
| 1 | Araştırma / parça seçimi | Issue formu **02 · Parça seçimi / araştırma** | `stage:research`, `type:research` |
| 2 | Şematik | Branch + Pull Request | `PHASE: draft` |
| 3 | Layout | Aynı Pull Request | `PHASE: preliminary` |
| 4 | İnceleme | PR kontrol listesi | |
| 5 | Onay | CI yeşil, `PHASE: checked` | |
| 6 | Release | `v*` etiketi, `PHASE: release` | |
| 9 | Test / bring-up | Issue formu **03 · Bring-up / test raporu** | `stage:bringup`, `type:test` |

### Issue formları

Issue açarken **New issue** sayfasındaki formlar kullanılır (`.github/ISSUE_TEMPLATE/`). Boş Issue açma kapalıdır; böylece her kayıt aynı yapıda toplanır.

### Pull Request kontrol listesi

PR açıldığında açıklama kutusu `.github/pull_request_template.md` ile dolu gelir. Şematik, layout ve `checked`/`release` geçişi için ayrı kontrol listeleri vardır. Maddeleri gerçekten işaretleyin; tek başına çalışırken bu sizin "ikinci göz" kontrolünüzdür.

### Etiketler

Etiketler şablondan türeyen repolara **kopyalanmaz**, her yeni repoda oluşturulması gerekir. Bunun için depodaki [Etiketleri Kur iş akışını](.github/workflows/setup-labels.yml) kullanın:

1. Yeni reponuzda **Actions** sekmesini açın; Actions kapalıysa etkinleştirin.
2. **Etiketleri Kur** iş akışını seçin.
3. **Run workflow** menüsünde varsayılan dalı seçip çalıştırın.
4. Çalışma başarıyla tamamlandığında etiketleri **Issues → Labels** sayfasından kontrol edin.

İş akışı süreç, tür ve disiplin etiketlerini oluşturur. Yeniden çalıştırıldığında aynı adlı etiketlerin renk ve açıklamalarını iş akışındaki değerlere göre günceller. Etiket tanımlarını değiştirmek için `.github/workflows/setup-labels.yml` dosyasını düzenleyin. Elle kurulum tercih ederseniz aynı tanımları **Issues → Labels** üzerinden de oluşturabilirsiniz.

Issue formlarının kullandığı etiketler:

| Etiket | Renk | Açıklama |
|---|---|---|
| `stage:requirements` | `1D76DB` | Aşama 0: gereksinim |
| `type:board` | `C5DEF5` | Kart talebi |
| `stage:research` | `5319E7` | Aşama 1: araştırma / parça seçimi |
| `type:research` | `D4C5F9` | Araştırma |
| `stage:bringup` | `B60205` | Aşama 9: test ve bring-up |
| `type:test` | `F9D0C4` | Test raporu |

Etiketler yoksa formlar yine açılır, sadece etiket atanmaz.

### Proje panosu

İşlerin hangi aşamada olduğunu görmek için GitHub Projects üzerinde bir Kanban panosu kullanılır:

`Gereksinim → Araştırma → Şematik → Layout → İnceleme → Release → Test → Done`

Kartlar sütunlar arasında elle sürüklenir; aşama geçişi bilinçli bir karardır. Pano hesap/kurum düzeyinde olduğundan birden fazla reponun kartını tek yerde toplayabilir.

### Günlük kurallar

1. Her iş bir Issue ile başlar, bir PR ile biter.
2. Karar gerektiren seçimlerin gerekçesi Issue'da yazılır.
3. Issue'yu kısmen ilerleten PR'larda `Refs #N`, ilgili Issue'nun kabul kriterlerini tamamlayan PR'da `Closes #N` kullanın. Kartın üretimi ve testi ayrı Issue'larla takip edilebilir.
4. PR'ı açtıktan sonra bir gün ara verip taze gözle yeniden bakın.
5. `PHASE` değerini bilinçli yükseltin; CI'ın sıkılığı buna bağlıdır.

## Tasarım aşamaları

| Aşama | Üretilenler ve kontrol davranışı |
| ----- | -------------------------------- |
| `draft` | Şematik PDF ve BOM CSV. ERC/DRC ve PCB çıktıları çalıştırılmaz. |
| `preliminary` | ERC/DRC raporları, şematik PDF, BOM, Gerber/Drill ZIP, montaj PDF ve STEP. ERC/DRC bulguları üretimi durdurmaz. |
| `checked` | `draft` dışındaki tüm çıktılar. ERC veya DRC bulgusu varsa iş akışı başarısız olur. Varsayılan aşamadır. |
| `release` | `checked` ile aynı kontroller ve çıktılar. Şematikte `release` seçiliyken `v*` etiketi gönderilirse GitHub Release yayımlanır. |

### Aşamayı seçme

Bu şablonda `.kicad_pro` içindeki `PHASE` text variable'ı zaten tanımlıdır.
**Schematic Setup → Project → Text Variables** üzerinden bu değeri değiştirin.
`DRAFT` gibi büyük harfli değerler de kabul edilir. Kapaktaki aşama alanı aynı
değişkeni kullanır. Farklı aşamayı ikinci bir yere eklemek yerine mevcut değeri düzenleyin.

Alternatif olarak şematik yorum alanı kullanılabilir:

1. KiCad Schematic Editor'da şematiği açın.
2. **File → Page Settings** menüsünü açın.
3. **Title Block** bölümündeki boş bir **Comment** alanına aşağıdaki değerlerden birini yazın:

   ```
   PHASE: draft
   ```

   Değeri `draft`, `preliminary`, `checked` veya `release` olarak ayarlayın. Aynı şematikte birden fazla farklı PHASE değeri bırakmayın.

4. Şematiği kaydedin. `scripts/build_docs.py`, kök `.kicad_sch` içindeki PHASE metnini ve `.kicad_pro` içindeki PHASE text variable'ını kontrol eder. İkisi de varsa aynı değerde olmalıdır; çelişki derlemeyi durdurur. Hiçbiri yoksa `checked` kullanılır. Alt sayfalardaki PHASE metinleri aşama seçiminde taranmaz.

## Proje yapısı

```
project-root/
├── .github/
│   ├── ISSUE_TEMPLATE/          # 01, 02, 03 formları ve config.yml
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── setup-labels.yml     # Süreç etiketlerini oluşturur/günceller
│   └── pull_request_template.md
├── hardware/                    # KiCad dosyaları burada
│   ├── kicad10-project-template.kicad_pro
│   ├── kicad10-project-template.kicad_sch  # Kök / kapak
│   ├── kicad10-project-template.kicad_pcb
│   ├── Block Diagram.kicad_sch
│   ├── Power - Sequencing.kicad_sch
│   ├── Project Architecture.kicad_sch
│   ├── Revision History.kicad_sch
│   ├── Sayfa1.kicad_sch
│   ├── untitled.kicad_sch
│   └── sheet/                   # A2, A3, A4 sayfa çerçeveleri
├── scripts/
│   ├── build_docs.py
│   ├── update_title_block.py
│   └── build_kicad_template.py
├── templates/                   # KiCad paket tanımı ve kullanım notu
│   ├── meta/info.html
│   └── USAGE.md
├── tests/                       # Girdi seçimi testleri
├── manufacturing/               # Betik tarafından üretilir, commit'lenmez
├── CHANGELOG.md
└── README.md
```

Gerçek KiCad dosyalarının adı `Project` olmak zorunda değildir. `hardware/` içinde birden fazla şematik varsa, tek bir `.kicad_pro` dosyası bulunması halinde onunla aynı adlı şematik kök olarak seçilir. Böylece hiyerarşik alt sayfalar aynı klasörde bulunabilir; KiCad çıktıları kök şematik üzerinden üretir. Tek proje dosyası yoksa veya onunla eşleşen kök bulunamazsa `--schematic` ile açık seçim gerekir. Klasör adına göre seçim yapılmaz. Birden fazla PCB varsa `draft` dahil tüm aşamalarda `--board` ile açık seçim gerekir.

> **Kütüphane yolları:** KiCad dosyaları `hardware/` altında, `lib/` ise kökte olduğundan `sym-lib-table` ve `fp-lib-table` içindeki yollar `${KIPRJMOD}/../lib/...` biçiminde olmalıdır.

`lib/` mevcut depoda bulunmaz; özel kütüphaneler gerektiğinde oluşturulabilir.

## Şematik hiyerarşisi ve proje ayarları

Mevcut tasarım yedi sayfadan oluşur:

```text
Kapak / kök şematik (1)
├── Block Diagram (2)
├── Power - Sequencing (3)
├── Project Architecture (4)
│   ├── Sayfa 1 — Sayfa1.kicad_sch (6)
│   └── Sayfa 2 — untitled.kicad_sch (7)
└── Revision History (5)
```

Sayfa adlarını ve numaralarını Şematik Editörü'ndeki hiyerarşiden yönetin.
Dosya adı değişirse üst sayfadaki `Sheetfile` bağlantısını da güncelleyin.
Kök şematik üzerinden alınan PDF, bağlı alt sayfaları içerir.

### Kapak ve ortak bilgiler

**Schematic Setup → Project → Text Variables** bölümündeki alanlar:

| Alan | Kullanım |
|---|---|
| `BOARD_NAME` | Kart adı; mevcut değeri boş, yeni projede doldurun |
| `PROJECT_CODE` | Proje kodu |
| `PROJECT_DESCRIPTION` | Projenin amaç ve kapsam açıklaması |
| `DESIGNER`, `REVIEWER` | Tasarımcı ve kontrol eden |
| `PHASE` | Otomasyonun aşaması |
| `SHEET_NAME_1` … `SHEET_NAME_19` | Kapak ve sayfa başlıklarında kullanılan, elle yönetilen sayfa adları |
| `KICAD_VERSION` | Özel sürüm alanı; üretim betiği bu değişkeni doldurmaz |

`SHEET_NAME_n` değerleri hiyerarşiden otomatik hesaplanmaz. Sayfa eklerken,
yeniden adlandırırken veya numara değiştirirken ilgili değişkenleri de güncelleyin.
`Revision History` sayfası da CHANGELOG ile otomatik eşitlenmez.

### Bileşen alanları, net sınıfları ve bus alias

`Manufacturer`, `MPN` ve `Notes` sembol alanı şablonları tanımlıdır; şematikte
görünürlükleri kapalıdır. Değerleri parça seçimi sırasında doldurun. Bunlar BOM'a
otomatik olarak sütun eklemez; mevcut BOM ayarlarında bu üç sütun seçili değildir.
Özel BOM ve biçim preset listeleri henüz boştur.

Mevcut net sınıfları: `Default`, `ANALOG`, `CAN_BUS`, `CLOCK`, `CONTROL`, `GND`,
`POWER_HIGH_CURRENT`, `Power`, `RF_50R`, `RS485_BUS`, `SWITCH_NODE`, `USB2_DATA`.
PCB ölçülerini üretici, akım ve katman yapısına göre gözden geçirin; sınıf adları
tek başına akım taşıma veya empedans uygunluğunu garanti etmez.

I²C, SPI, UART, SWD, JTAG, USB2, CAN ve RS-485 için bus alias tanımları vardır.
Örneğin `I2C1{I2C}`, `I2C1.SCL` ve `I2C1.SDA` üyelerini temsil eder.
Mevcut ayarlarda `CLK CMD D[0..3]` üyelerini içeren adı boş bir alias da bulunur;
kullanmadan önce adlandırın veya kaldırın.

### Proje ağacında alt sayfaların görünmesi

KiCad Git entegrasyonu etkin olduğunda değişiklikleri izleyebilmek için alt
şematik dosyalarını da Proje Yöneticisi'nde gösterir. Yalnızca kök şematiği
görmek için proje bağlam menüsünden **Version Control → Disable Git Integration**
seçilebilir. Bu, Git deposunu veya geçmişini silmez; diğer Git araçları çalışmaya
devam eder. Şematik Editörü'ndeki hiyerarşi korunur.
[KiCad Git entegrasyonu belgesi](https://docs.kicad.org/10.0/en/kicad/kicad.html#_git_integration).

## Yerel kullanım

### KiCad kullanıcı şablonu kurulumu

Paketleme betiği kök şematikten başlayarak tüm `Sheetfile` bağlantılarını izler;
iç içe alt sayfaları dizin yapısını koruyarak pakete ekler. Mevcut proje için
toplam yedi şematik paketlenir. Bağlı olmayan şematikler alınmaz. Eksik dosya,
döngüsel bağlantı, mutlak/değişkenli yol veya `hardware/` dışına çıkan bağlantı
varsa paketleme hata verir. Taşınabilirlik için göreli `Sheetfile` yolları kullanın.

`python scripts/build_kicad_template.py` komutu, mevcut kapak tasarımını
`manufacturing/templates/kicad10-project-template.zip` olarak paketler.

1. KiCad'de **Preferences → Configure Paths** ekranında
   `KICAD_USER_TEMPLATE_DIR` klasörünü bulun.
2. ZIP içindeki `kicad10-project-template` klasörünü bu klasörün altına çıkarın.
   Sonuç `<kullanıcı şablonları>/kicad10-project-template/meta/info.html` olmalıdır.
3. Proje oluşturma ekranını yeniden açıp kullanıcı şablonları listesinden
   **Donanimkafa - A3 Proje Kapagi** öğesini seçin.
4. Yeni proje adı ve konumunu belirleyin. Oluşturulan projedeki `USAGE.md`
   dosyası, kapak alanlarının nasıl düzenleneceğini açıklar.

Paket yalnızca KiCad dosyalarını, sayfa çerçevelerini ve kullanım notunu içerir;
yerel yedekler ve kilit dosyaları dahil edilmez. GitHub otomasyonu için
**Use this template** ana başlangıç yoludur; KiCad paketi CI/Issue dosyalarını içermez.

### A3 kapak sayfası

Ana şematik, düzenlenebilir içindekiler alanı, üst/alt PCB görsel
alanları, proje açıklaması ve tasarım notları içeren bir A3 kapaktır.
`BOARD_NAME`, `PROJECT_DESCRIPTION`, `PROJECT_CODE` ve `PHASE` proje text
variable alanlarından düzenlenir. Tarih ve revizyon başlık bloğundan alınır.
İçindekilerdeki adlar `SHEET_NAME_n` değişkenleriyle elle yönetilir; boş satırlar gerçek alt sayfa oluşturmaz.
PCB görselleri elle eklenir; KiBot görsel veya içindekiler otomasyonu eklenmemiştir.
Kapak metinleri ve çizgileri Şematik Editörü'nde doğrudan düzenlenebilir.

### Üretim betiğini çalıştırma

Gereksinimler: KiCad 10, Python 3.10 veya üzeri ve Git. Betik `kicad-cli` aracını PATH'te ve yaygın kurulum konumlarında arar; gerekirse `--kicad-cli` ile yol verin. `CHANGELOG.md` içindeki `Company:` alanını doldurun ve bir sürüm etiketi veya changelog sürümü sağlayın.

Proje kökünde PowerShell:

```powershell
kicad-cli version
python scripts/build_docs.py
```

Betik başlık bloğu alanlarını günceller ve seçilen aşamaya ait dosyaları `manufacturing/` altına yazar. Yerel çalıştırmadan önce KiCad dosyalarını kaydedin; başlık bloğu değişikliklerini commit etmeden önce gözden geçirin.

Revizyon önce Git etiketinden, etiket yoksa CHANGELOG'daki ilk sürümden alınır.
Tarih son commit tarihidir; okunamazsa changelog sürüm tarihine dönülür.
Başlık güncellemesi kök şematik ve seçili PCB'ye uygulanır; alt sayfaların başlık
blokları ayrı ayrı güncellenmez. CLI kullanılabilirliği dosyalar değiştirilmeden kontrol edilir.

Üretim başlamadan önce seçili çıktı klasöründeki önceki BOM, Gerber/Drill ZIP,
şematik/montaj PDF, STEP ve ERC/DRC raporları ile `build.log` temizlenir.
Eski sürümlerin `fabrication/*-fabrication.pdf` ve `fabrication/*_Gerbers.zip` çıktıları da temizlenir.
Bu işlem tüm proje adlarını ve preliminary ZIP dosyalarını kapsar; böylece aşama
veya proje adı değiştiğinde eski üretim dosyaları güncel çıktılarla karışmaz.
Diğer dosyalar korunur. `--output-dir` için üretime ayrılmış bir klasör kullanın;
saklamak istediğiniz önceki üretimleri bu klasörün dışında arşivleyin.

### Sık kullanılan seçenekler

| Seçenek | Açıklama |
|---|---|
| `--hardware-dir <klasör>` | KiCad dosyalarının klasörü. Varsayılan: `hardware`. Klasör yoksa proje köküne geri düşer |
| `--schematic <yol>` | Şematik dosyası; göreli yol proje köküne göredir |
| `--board <yol>` | PCB dosyası; göreli yol proje köküne göredir |
| `--output-dir <klasör>` | Çıktı klasörü. Varsayılan: `manufacturing` |
| `--kicad-cli <yol>` | `kicad-cli` çalıştırılabilir dosyasının yolu |
| `--timeout <sn>` | Her `kicad-cli` komutu için süre sınırı (varsayılan 300) |

## GitHub Actions

`ci.yml`, `main` dalına gönderimde, `main` hedefli PR'larda ve `v*` etiketlerinde betiği çalıştırır. Çalışma dalındaki otomatik kontroller için Draft PR'ı erken açın; PR açıldıktan sonraki gönderimler de kontrol edilir. Aşama şematikteki PHASE metninden veya `.kicad_pro` içindeki PHASE text variable'ından alınır. `release` seçimi tek başına GitHub Release oluşturmaz; bunun için onaylı `main` commit'ine `v1.0.0` gibi bir etiket gönderilmelidir.

İş akışı hata durumunda da oluşmuş rapor ve çıktıları artifact olarak yüklemeyi dener. Actions çalışmasındaki `KiCad-10-Manufacturing-Outputs` artifact'ini indirerek sonuçları inceleyin; başarısız çalışmanın dosyaları tamamlanmış üretim paketi sayılmaz. `release` aşamasıyla tetiklenen `v*` etiketi, kontroller başarılıysa seçili üretim dosyalarını GitHub Releases sayfasında yayımlar. CI mevcut haliyle testleri ve KiCad şablon paketleme betiğini çalıştırmaz.

## Üretim çıktıları

```
manufacturing/
├── reports/       # ERC/DRC raporları ve build.log
├── schematic/     # Şematik PDF
├── assembly/      # Montaj PDF
├── 3d/            # STEP modeli
├── *-bom.csv      # BOM
└── *Gerber-Drill.zip
```

`draft` aşamasında yalnızca `schematic/` PDF'i ve BOM üretilir. Diğer aşamalar PCB çıktıları da üretir.

Her çalışmada `reports/build.log` da yazılır. `preliminary` Gerber paketi
`*-preliminary-Gerber-Drill.zip` adıyla oluşturulur. KiCad kullanıcı şablon ZIP'i
ayrı paketleme komutuyla `manufacturing/templates/` altında üretilir.

Girdi seçimi testlerini çalıştırmak için: `python -B -m unittest discover -s tests -v`.

## Commit mesajı kuralı

Commit başlığı `tür(kapsam): kısa açıklama` biçimindedir; ayrıntı ikinci satırda yazılır.

| Tür | Kullanım |
|---|---|
| `feat` | Yeni özellik veya dosya |
| `fix` | Hata düzeltmesi |
| `docs` | Yalnızca doküman |
| `ci` | CI / otomasyon değişikliği |
| `chore` | Bakım, temizlik |

Örnek: `feat(power): ters polarite koruması eklendi`
