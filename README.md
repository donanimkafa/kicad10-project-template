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
- [Yerel kullanım](#yerel-kullanım)
- [GitHub Actions](#github-actions)
- [Üretim çıktıları](#üretim-çıktıları)
- [Commit mesajı kuralı](#commit-mesajı-kuralı)

## Hızlı başlangıç

1. Bu sayfada **Use this template → Create a new repository** ile yeni proje reposunu oluşturun.
2. Repoyu klonlayın ve KiCad dosyalarını `hardware/` klasöründe açın.
3. `CHANGELOG.md` içindeki `Company:` alanını kendi şirket/ekip adınızla değiştirin.
4. GitHub'da **Issues → Labels** sayfasından süreç etiketlerini oluşturun (bkz. [Etiketler](#etiketler)).
5. **Issues → New issue → 01 · Yeni kart talebi** ile ilk kartınızın gereksinimlerini yazın.

## Çalışma akışı

Her iş bir **Issue** ile başlar ve bir **Pull Request** ile ilerler. Kararlar ve değişiklikler GitHub'da kayıt altında kalır.

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

Etiketler şablondan türeyen repolara **kopyalanmaz**, her yeni repoda oluşturulması gerekir. Formların kullandığı etiketler:

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
3. Ara PR'larda `Refs #N`, kartın gerçekten bittiği PR'da `Closes #N` kullanın.
4. PR'ı açtıktan sonra bir gün ara verip taze gözle yeniden bakın.
5. `PHASE` değerini bilinçli yükseltin; CI'ın sıkılığı buna bağlıdır.

## Tasarım aşamaları

| Aşama | Üretilenler ve kontrol davranışı |
| ----- | -------------------------------- |
| `draft` | Şematik PDF ve BOM CSV. ERC/DRC ve PCB çıktıları çalıştırılmaz. |
| `preliminary` | ERC/DRC raporları, şematik PDF, BOM, Gerber/Drill ZIP, montaj PDF ve STEP. ERC/DRC bulguları üretimi durdurmaz. |
| `checked` | `draft` dışındaki tüm çıktılar. ERC veya DRC bulgusu varsa iş akışı başarısız olur. Varsayılan aşamadır. |
| `release` | `checked` ile aynı kontroller ve çıktılar. Şematikte `release` seçiliyken `v*` etiketi gönderilirse GitHub Release yayımlanır. |

### Aşamayı şematikte seçme

1. KiCad Schematic Editor'da şematiği açın.
2. **File → Page Settings** menüsünü açın.
3. **Title Block** bölümündeki boş bir **Comment** alanına aşağıdaki değerlerden birini yazın:

   ```
   PHASE: draft
   ```

   Değeri `draft`, `preliminary`, `checked` veya `release` olarak ayarlayın. Aynı şematikte birden fazla farklı PHASE değeri bırakmayın.

4. Şematiği kaydedin. `scripts/build_docs.py`, `.kicad_sch` dosyasındaki PHASE metnini okur. Alternatif olarak `.kicad_pro` içindeki `PHASE` text variable'ı da kullanılabilir. Hiçbiri yoksa `checked` kullanılır.

## Proje yapısı

```
project-root/
├── .github/
│   ├── ISSUE_TEMPLATE/          # 01, 02, 03 formları ve config.yml
│   ├── workflows/
│   │   └── ci.yml
│   └── pull_request_template.md
├── hardware/                    # KiCad dosyaları burada
│   ├── Project.kicad_pro
│   ├── Project.kicad_sch
│   └── Project.kicad_pcb
├── lib/                         # İsteğe bağlı: ortak sembol/footprint/3D
│   ├── symbols/
│   ├── footprints/
│   └── 3dmodels/
├── scripts/
│   ├── build_docs.py
│   └── update_title_block.py
├── manufacturing/               # Betik tarafından üretilir, commit'lenmez
├── CHANGELOG.md
└── README.md
```

Gerçek KiCad dosyalarının adı `Project` olmak zorunda değildir. Betik `hardware/` içinde tek bir `.kicad_sch` ve (draft dışında) tek bir `.kicad_pcb` bulmayı bekler. Birden fazla dosya varsa `--schematic` ve `--board` seçenekleri kullanılabilir.

> **Kütüphane yolları:** KiCad dosyaları `hardware/` altında, `lib/` ise kökte olduğundan `sym-lib-table` ve `fp-lib-table` içindeki yollar `${KIPRJMOD}/../lib/...` biçiminde olmalıdır.

## Yerel kullanım

Gereksinimler: KiCad 10 (`kicad-cli` PATH'te olmalı), Python 3 ve proje dosyaları. Başlık bloğu güncellemesi için depo Git deposu olmalı; `CHANGELOG.md` içindeki `Company:` alanını doldurun ve bir sürüm etiketi veya changelog sürümü sağlayın.

Proje kökünde PowerShell:

```powershell
kicad-cli version
python scripts/build_docs.py
```

Betik başlık bloğu alanlarını günceller ve seçilen aşamaya ait dosyaları `manufacturing/` altına yazar. Yerel çalıştırmadan önce KiCad dosyalarını kaydedin; başlık bloğu değişikliklerini commit etmeden önce gözden geçirin.

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

`ci.yml`, push, pull request ve `v*` etiketlerinde betiği çalıştırır. Aşama `.kicad_sch` dosyasından alınır. `release` seçimi tek başına GitHub Release oluşturmaz; bunun için aynı commit'e `v1.0.0` gibi bir etiket gönderilmelidir.

Başarılı iş akışının `manufacturing/` çıktıları Actions artifact'i olarak saklanır. `release` aşamasıyla tetiklenen `v*` etiketi, seçili üretim dosyalarını GitHub Releases sayfasında yayımlar.

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
