# KiCad 10 Proje Şablonu

[![KiCad CI](https://github.com/OWNER/REPOSITORY/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/OWNER/REPOSITORY/actions/workflows/ci.yml)

> **Rozeti etkinleştirme:** `OWNER/REPOSITORY` bölümünü GitHub kullanıcı/kurum adınız ve depo adınızla değiştirin. Rozet, `main` dalındaki **KiCad 10 Design Lifecycle** iş akışının son durumunu gösterir.

KiCad 10 projeleri için bu şablon; ERC/DRC denetimlerini, dokümantasyon üretimini, üretim dosyalarını ve GitHub Actions üzerinden sürüm yayınlamayı otomatikleştirir. Çıktılar `manufacturing/` klasörüne yazılır.

## Tasarım yaşam döngüsü

| Aşama | Davranış |
| --- | --- |
| `draft` | Şematik PDF ve BOM CSV üretir. ERC/DRC veya PCB çıktısı üretmez. |
| `preliminary` | ERC/DRC bulgularını raporlar ve üretime devam eder; şematik PDF, BOM, ön Gerber/Drill ZIP, montaj PDF ve STEP üretir. |
| `checked` | ERC ve DRC bulgusu varsa derlemeyi durdurur. Temel dokümantasyon ve üretim çıktılarının tamamını üretir. Varsayılan aşamadır. |
| `release` | `v*` Git etiketiyle çalışır. ERC/DRC temiz olmalı; onaylı dosyalar GitHub Release’e yüklenir. |

Normal push ve `main` için açılan pull request işlemleri `checked` aşamasını çalıştırır. GitHub Actions sayfasından elle çalıştırmada `draft`, `preliminary` veya `checked` seçilebilir. Örnek yerel komutlar:

```powershell
python scripts/build_docs.py --phase draft
python scripts/build_docs.py --phase preliminary
python scripts/build_docs.py --phase checked
```

`release` aşaması CI’da `v1.0.0` gibi bir etiket gönderildiğinde seçilir. Gerçek bir sürümü yayınlamadan önce etiketin doğru commit üzerinde olduğundan emin olun.

## Gereksinimler ve yerel geliştirme

- KiCad 10 ve `kicad-cli` bilgisayarda kurulu ve PATH üzerinden erişilebilir olmalıdır.
- Python 3.10 veya üzeri gerekir.
- Başlık bloğu otomasyonu için proje bir Git deposu olmalı; `CHANGELOG.md` içindeki `Company:` alanı gerçek şirket adıyla doldurulmalıdır.
- `draft` için kök dizinde bir `.kicad_sch`; diğer aşamalar için hem `.kicad_sch` hem `.kicad_pcb` gerekir.

Depo kökünde PowerShell ile:

```powershell
kicad-cli version
python scripts/update_title_block.py
python scripts/build_docs.py --phase draft
```

Başlık bloğu güncellemesi `.kicad_sch` ve `.kicad_pcb` dosyalarını yerinde değiştirir. KiCad’de açmadan önce dosyaları kaydedin; sonucu GitHub Desktop’taki değişiklikler arasında kontrol edebilirsiniz. Farklı proje dosyaları varsa `--schematic` ve `--board` seçenekleriyle dosya yollarını belirtin.

## Proje yapısı

```text
project-root/
├── .github/
│   └── workflows/
│       └── ci.yml
├── lib/
│   ├── symbols/
│   ├── footprints/
│   │   └── ProjectParts.pretty/
│   └── 3dmodels/
├── scripts/
│   ├── build_docs.py
│   └── update_title_block.py
├── manufacturing/             # Otomatik üretilir
├── CHANGELOG.md
├── README.md
├── sym-lib-table               # Projeye özel sembol kütüphaneleri
├── fp-lib-table                # Projeye özel footprint kütüphaneleri
├── Project.kicad_pro
├── Project.kicad_sch
└── Project.kicad_pcb
```

Gerçek proje dosyalarının adları projeye göre değişebilir. `manufacturing/` içeriği betik tarafından yeniden üretildiğinden, genellikle kaynak dosya olarak commit edilmesi gerekmez; CI çıktıları Actions artifact ve sürüm etiketlerinde saklanır.

## Yerel kütüphane ve taşınabilir yollar

- Sembol dosyalarını `lib/symbols/` altında tutun. Sembol kütüphanesini KiCad’in **Project Specific Libraries** tablosuna ekleyin ve proje kökündeki `sym-lib-table` dosyasını depoya commit edin. Tablo yolu `${KIPRJMOD}/lib/symbols/YourLibrary.kicad_sym` biçiminde olmalıdır.
- Footprint’ler `.pretty` uzantılı kütüphane klasörlerinde bulunur; örneğin `lib/footprints/ProjectParts.pretty/Part.kicad_mod`. Projeye özel `fp-lib-table` içindeki URI `${KIPRJMOD}/lib/footprints/ProjectParts.pretty` biçiminde olmalıdır.
- STEP/WRL modellerini `lib/3dmodels/` altında saklayın. Footprint’in 3D model alanında `${KIPRJMOD}/lib/3dmodels/Model.step` veya `.wrl` kullanın.
- Bilgisayara özel `C:\...`, `/home/...` gibi mutlak yollar kullanmayın. `${KIPRJMOD}`, KiCad’de mevcut proje klasörüne açılır ve projeyi başka bilgisayara taşırken yolların korunmasını sağlar.
- `sym-lib-table`, `fp-lib-table`, footprint `.pretty` klasörleri ve 3D model dosyaları Git’e eklenmelidir. Her geliştirme bilgisayarında kütüphaneleri global tabloya yeniden tanımlamak yerine proje tablolarını kullanın.
- Footprint kütüphane takma adları ve sembol kimlikleri şematik/PCB içindeki referanslarla eşleşmelidir. Kütüphane veya takma ad değiştirirken tasarımları KiCad’de yeniden kontrol edin.

KiCad, `${KIPRJMOD}` değişkenini geçerli proje klasörüne çözer. Sembol/footprint tabloları proje özelinde tutulabilir; böylece mutlak bilgisayar yollarına bağlı kalmazlar. [KiCad 10 path variable belgeleri](https://docs.kicad.org/10.0/en/kicad/kicad.html) · [Şematik sembol kütüphaneleri](https://docs.kicad.org/10.0/en/eeschema/eeschema.html) · [PCB footprint kütüphaneleri](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html)

## CI çıktıları

`manufacturing/` altında aşamaya göre şematik PDF, BOM CSV, ERC/DRC raporları, Gerber ve Drill ZIP, montaj PDF ve 3D STEP dosyaları oluşturulur. Başarılı tag build’inde üretim paketi GitHub Release’e yüklenir.
