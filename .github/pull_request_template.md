## Özet
<!-- Bu PR ne değiştiriyor ve neden? İlgili Issue: Closes #__ -->


## Değişiklik türü
- [ ] Şematik
- [ ] Layout
- [ ] Kütüphane / footprint
- [ ] CI / script / altyapı
- [ ] Dokümantasyon

## Tasarım aşaması (`PHASE:`)
<!-- Şematikteki mevcut değer ve bu PR sonrası hedef -->
`PHASE:` ______

---

## Kontrol listesi

### Her PR için
- [ ] CI yeşil (ERC/DRC dahil, aşama gerektiriyorsa)
- [ ] Bu PR tek bir konuya odaklı
- [ ] CHANGELOG.md güncellendi

### Şematik değiştiyse
- [ ] ERC temiz; kalan uyarılar gerekçelendirildi
- [ ] Yeni parçalarda MPN, üretici ve datasheet alanları dolu
- [ ] Güç bütçesi ve akım kapasiteleri gözden geçirildi
- [ ] Decoupling, ESD ve ters polarite korumaları kontrol edildi
- [ ] Test noktaları ve programlama/debug konnektörü var

### Layout değiştiyse
- [ ] DRC temiz
- [ ] Kritik sinyaller (güç, diferansiyel çift, yüksek hızlı) gözden geçirildi
- [ ] Üretici kuralları (min iz/aralık, via, delik) karşılanıyor
- [ ] Mekanik uyum: delikler, konnektör konumları, yükseklik sınırları
- [ ] Silkscreen: polarite, pin 1, revizyon bilgisi okunabilir

### `checked` veya `release` aşamasına geçişte
- [ ] Tüm parçalar stokta, EOL/NRND değil
- [ ] BOM üreticiye gidecek biçimde doğrulandı
- [ ] Kabul kriterleri (ilgili Issue) tek tek karşılandı
- [ ] Bir gün ara verip taze gözle yeniden bakıldı

## Notlar / bilinen riskler
<!-- İncelemecinin özellikle bakmasını istediğin yerler -->