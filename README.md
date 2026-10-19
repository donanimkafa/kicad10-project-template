# KiCad 10 Proje Şablonu

[![KiCad CI](https://github.com/OWNER/REPOSITORY/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/OWNER/REPOSITORY/actions/workflows/ci.yml)

> Rozetin çalışması için `OWNER/REPOSITORY` ifadelerini GitHub kullanıcı/kurum adınız ve depo adınızla değiştirin.

KiCad 10 projeleri için bu şablon, `kicad-cli` ve Python kullanarak şematik/PCB kontrollerini ve üretim belgelerini otomatik oluşturur. GitHub Actions sonuçları ve sürüm paketleri de aynı iş akışından yönetilir.

## Tasarım aşamaları

| Aşama | Üretilenler ve kontrol davranışı |
| --- | --- |
| `draft` | Şematik PDF ve BOM CSV. ERC/DRC ve PCB çıktıları çalıştırılmaz. |
| `preliminary` | ERC/DRC raporları, şematik PDF, BOM, Gerber/Drill ZIP, montaj PDF ve STEP. ERC/DRC bulguları üretimi durdurmaz. |
| `checked` | `draft` dışındaki tüm çıktılar. ERC veya DRC bulgusu varsa iş akışı başarısız olur. Varsayılan aşamadır. |
| `release` | `checked` ile aynı kontroller ve çıktılar. Şematikte `release` seçiliyken `v*` etiketi gönderilirse GitHub Release yayımlanır. |

### Aşamayı şematikte seçme

1. KiCad Schematic Editor'da şematiği açın.
2. **File → Page Settings** menüsünü açın.
3. **Title Block** bölümündeki boş bir **Comment** alanına aşağıdaki değerlerden birini yazın:

   ```text
   PHASE: draft
   ```

   Değeri `draft`, `preliminary`, `checked` veya `release` olarak ayarlayın. Aynı şematikte birden fazla farklı PHASE değeri bırakmayın.
4. Şematiği kaydedin. `scripts/build_docs.py`, `.kicad_sch` dosyasındaki PHASE metnini okur. Metin yoksa `checked` kullanır.

## Proje yapısı

```text
project-root/
├── .github/
│   └── workflows/
│       └── ci.yml
├── lib/
│   ├── symbols/
│   ├── footprints/
│   └── 3dmodels/
├── scripts/
│   ├── build_docs.py
│   └── update_title_block.py
├── manufacturing/             # Betik tarafından oluşturulur
├── CHANGELOG.md
├── README.md
├── Project.kicad_pro
├── Project.kicad_sch
└── Project.kicad_pcb
```

Gerçek KiCad dosyalarının adı `Project` olmak zorunda değildir. Betik proje kökünde tek bir `.kicad_sch` ve (draft dışında) tek bir `.kicad_pcb` bulmayı bekler. Birden fazla dosya varsa `--schematic` ve `--board` seçenekleri kullanılabilir.

## Yerel kullanım

Gereksinimler: KiCad 10 (`kicad-cli` PATH'te olmalı), Python 3 ve proje dosyaları. Başlık bloğu güncellemesi için depo Git deposu olmalı; `CHANGELOG.md` içindeki `Company:` alanını doldurun ve bir sürüm etiketi veya changelog sürümü sağlayın.

Proje kökünde PowerShell:

```powershell
kicad-cli version
python scripts/build_docs.py
```

Betik başlık bloğu alanlarını günceller ve seçilen aşamaya ait dosyaları `manufacturing/` altına yazar. Yerel çalıştırmadan önce KiCad dosyalarını kaydedin; başlık bloğu değişikliklerini GitHub Desktop'ta gözden geçirin.

## GitHub Actions

`ci.yml`, push, pull request ve `v*` etiketlerinde betiği çalıştırır. Aşama `.kicad_sch` dosyasından alınır. `release` seçimi tek başına GitHub Release oluşturmaz; bunun için aynı commit'e `v1.0.0` gibi bir etiket gönderilmelidir.

Başarılı iş akışının `manufacturing/` çıktıları Actions artifact'i olarak saklanır. `release` aşamasıyla tetiklenen `v*` etiketi, seçili üretim dosyalarını GitHub Releases sayfasında yayımlar.

## Üretim çıktıları

```text
manufacturing/
├── reports/       # ERC/DRC raporları ve build.log
├── schematic/     # Şematik PDF
├── assembly/      # Montaj PDF
├── 3d/            # STEP modeli
├── *-bom.csv      # BOM
└── *Gerber-Drill.zip
```

`draft` aşamasında yalnızca `schematic/` PDF'i ve BOM üretilir. Diğer aşamalar PCB çıktıları da üretir.
