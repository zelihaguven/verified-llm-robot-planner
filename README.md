# Doğrulanmış Görev Planlamalı, Doğal Dil Rehberli Servis Robotu

Bu depo, bir robotik dersi grup projesidir. Sembolik simülasyon dünyası ve Behavior Tree yürütücüsü uygulandı (bkz. [07](#07-kurulum-ve-projeyi-çalıştırma-adımları)); dil, algılama ve doğrulama katmanları geliştirme aşamasındadır. Deney bölümleri grup içinde güncellenecektir.

## Depo yapısı

| Yol | Açıklama |
| --- | --- |
| [README.md](README.md) | Proje tanıtımı ve takip |
| [src/](src/) | Kaynak kodlar |
| [simulation/](simulation/) | Çalışan simülasyon |
| [docs/](docs/) | Rapor ve diyagramlar |
| [results/](results/) | Test çıktıları |
| [cv/](cv/) | Tüm grup üyelerinin CV'leri |
| [requirements.txt](requirements.txt) | Yazılım bağımlılıkları |
| [assets/](assets/) | Görseller ve veri kaynakları |
| [references/](references/) | Araştırma kaynakları ve referanslar |

Düzenli ilerleme kaydının asıl yeri bu dosyanın [09](#ilerleme) bölümüdür. Daha uzun haftalık notlar için [updates/TEMPLATE.md](updates/TEMPLATE.md) kullanılabilir.

## 01 Proje adı, konu numarası ve grup üyeleri

**Proje adı:** Natural Language-Guided Service Robot with Grounded Task Planning

**Konu numarası:** 02 VLM, VLA & LLM Integration

### Grup üyeleri

| Ad | GitHub | CV |
| --- | --- | --- |
| Zeliha Ilgın Güven | [zelihaguven](https://github.com/zelihaguven) | [Zeliha_Ilgin_Guven_CV.pdf](cv/Zeliha_Ilgin_Guven_CV.pdf) |
| Neslihan Özdemir | [eklenecek] | `cv/` altına `Ad_Soyad_CV.pdf` kuralına göre eklenecek |
| Tuğba Önen | [eklenecek] | `cv/` altına `Ad_Soyad_CV.pdf` kuralına göre eklenecek |
| Buse Yılmaz | [eklenecek] | `cv/` altına `Ad_Soyad_CV.pdf` kuralına göre eklenecek |

Diğer üyelerin GitHub kullanıcı adları ve CV'leri eklenecektir.

## 02 Amaç, problem tanımı ve proje kapsamı

### Amaç

Ofis veya ev benzeri bir ortamda çalışan bir servis robotunun, doğal dille verilen çok adımlı görevleri yerine getirmesini sağlamak. Robot, komutu yalnızca dilsel olarak makul bir plana çevirmekle kalmaz; yorumu görsel kanıt, semantik bilgi ve fiziksel yeteneklerle tutarlı hale getirir.

### Problem tanımı

Kullanıcı komutları eksik, muğlak veya ortamla çelişkili olabilir. Dil modelinin ürettiği görev yorumu dilsel olarak doğru görünse bile fiziksel olarak uygulanamaz olabilir. Sistemin şu durumlarda açıklama istemesi, planı uyarlaması veya güvenli duruma geçmesi gerekir:

- yanlış nesne
- engellenmiş hedef
- ortam değişikliği
- güvensiz veya yerine getirilemeyen komut

Aynı amacın farklı ifadelerle (parafrazlarla) verilmesi de incelenecektir.

### Proje kapsamı (iş paketleri)

1. Literatür taraması: dil modelleri, görsel-dil modelleri, language grounding, görev planlama, Behavior Tree, HTN, plan doğrulama ve hayal ürünü çıktı (hallucination) riskleri.
2. Simülasyon ortamının seçimi ve kurulumu.
3. Dil katmanı: doğal dil komutunun görev yorumuna çevrilmesi.
4. Algılama ve görsel-dil ile grounding.
5. Planlama, plan doğrulama ve deterministik yürütme (Behavior Tree).
6. Açıklama isteme, plan uyarlama ve güvenli durum davranışları.
7. Deney senaryoları, ölçütler, sonuçların derlenmesi ve rapor.

Kapsam dışı: gerçek robot üzerinde deney, yeni bir model eğitimi veya ince ayarı, düşük seviye (eklem ve motor) kontrol ve ücretli API kullanımı.

### Araştırma soruları

- Dil modelinin görev yorumu, görsel kanıt, semantik bilgi ve robotun fiziksel yetenekleriyle nasıl tutarlı hale getirilir?
- Eksik, muğlak veya ortamla çelişen komutlarda sistem ne zaman açıklama istemeli, planı uyarlamalı veya güvenli duruma geçmelidir?
- Hangi iş dil modeline, hangisi algılamaya, hangisi deterministik robot mantığına bırakılmalıdır?
- Aynı hedefin farklı ifadeleri karşısında plan ve davranış ne kadar tutarlı kalır?
- Plan doğrulama, hayal ürünü veya uygulanamaz adımları ne ölçüde azaltabilir?

## 03 Kullanılacak yöntemler ve algoritmalar

Seçilen yöntemlerin gerekçeleri ve alternatifleri 04. bölümdedir.

- **Büyük dil modeli (LLM):** Kullanıcı komutunu görev yorumuna ve aday plan adımlarına çevirmek.
- **Görsel-dil modeli (VLM) ve language grounding:** Dilsel nesne ve konum iddialarını görsel kanıtla ilişkilendirmek.
- **Görev planlama:** Çok adımlı komutu sıralı bir plana (JSON adım listesi) dökmek. HTN değerlendirildi, kullanılmıyor (bkz. 04).
- **Plan doğrulama:** Üretilen planın yetenekler, semantik bilgi ve ortam durumuyla çelişip çelişmediğini denetlemek.
- **Deterministik yürütme:** Onaylanan planı Behavior Tree ile çalıştırmak; düşük seviye kontrolü dil modeline bırakmamak.
- **Hata ve belirsizlik yönetimi:** Yanlış nesne, engel, ortam değişikliği ve güvensiz komutlarda açıklama, uyarlama veya güvenli durum.

Temel ilke: dil modeli semantik yorum ve aday plan üretebilir; algılama ortam kanıtını sağlar; uygulanabilirlik denetimi ve yürütme deterministik robot mantığında kalmalıdır. Dilsel olarak makul bir plan, doğrulamadan geçmeden yürütülmemelidir.

## 04 Yöntem seçim gerekçeleri ve alternatifler

Seçimler literatür taramasından sonra gerekçelendirildi. Atıf yapılan kaynakların tam künyeleri [10](#10-araştırma-kaynakları-ve-referanslar) bölümündedir.

| Karar | Seçim | Gerekçe | Alternatif ve neden seçilmedi |
| --- | --- | --- | --- |
| LLM'in rolü | LLM yalnızca aday plan üretir, plan dış bir doğrulayıcıdan geçer | LLM'ler tek başına güvenilir, uygulanabilir plan üretemez ve kendi planlarını doğrulayamaz; dış doğrulayıcıdan geri bildirim alındığında başarı belirgin biçimde artar (Kambhampati vd., 2024, LLM-Modulo) | Yalnızca LLM ile planlama: deneylerde karşılaştırma koşulu (baseline) olarak kullanılacak |
| Yürütme | Behavior Tree (`py_trees`) | Geri beslemeli (kapalı çevrim) yürütme: başarısız adımdan sonra sıradaki körü körüne çalışmaz; modülerlik ve açıklanabilirlik (Ögren & Sprague, 2022; Iovino & Smith, 2023) | Düz döngü: açık çevrim, başarısızlığa tepki vermez. Sonlu durum makinesi (FSM): geçiş sayısı modül sayısının karesiyle büyür (Ögren & Sprague, 2022) |
| LLM çıktısının biçimi | Düz plan (JSON); BT bu plandan kodla, deterministik olarak kurulur | LLM'e doğrudan BT ürettirmek sözdizimi ve kontrol akışı hatalarına yol açıyor; büyük modeller bile her görevde doğru BT üretemiyor (Izzo vd., 2024, BTGenBot) | LLM'in BT veya robot kodu üretmesi (BTGenBot; Code as Policies) |
| Planlama biçimi | Sıralı adım listesi | Ev/ofis görevleri kısa; uygulanabilirlik kural tabanlı ön koşul kontrolüyle denetlenebiliyor | HTN ve PDDL planlayıcı (LLM+P): alan modeli yazma maliyeti yüksek; tartışma bölümünde ele alınacak |
| Doğrulama | Yetenek modeli (ön koşul ve etki) ve güvenlik kuralları | Eylemlere ön ve son koşul eklemek BT literatüründe yerleşik bir fikir (Iovino vd., 2022, extended BT) | Doğrulamayı LLM'e yaptırmak: LLM'ler kendi planlarını güvenilir biçimde doğrulayamıyor (Kambhampati vd., 2024) |
| BT tasarımı | Her adım "zaten sağlandı mı? → değilse yap" kalıbıyla sarılır; kök hafızalı Sequence | "Make sure X" kalıbı (Ögren & Sprague, 2022). Hafızasız kök, plandaki ara hedefleri sonradan tekrar çalıştırdığı için testlerde başarısız oldu; sapmada sonuç doğrulamaya döner ve plan uyarlanır | Hafızasız kök Sequence (Iovino vd., 2022'nin tepkisellik önerisi) |

Simülasyon ortamı kararı ve gerekçesi [06](#06-geliştirme-araçları--simülasyon-ortamı) bölümündedir.

## 05 Sistem mimarisi ve temel çalışma akışı

Mimari diyagram [docs/architecture.md](docs/architecture.md) dosyasındadır. Modüller birbirine `src/interfaces/schemas.py` içindeki ortak veri formatlarıyla bağlanır. Özet akış:

1. Kullanıcı doğal dil komutu verir.
2. Dil katmanı komutu görev yorumuna ve aday plana çevirir.
3. Doğrulama ve grounding katmanı bu yorumu algılama (VLM), semantik bilgi ve yetenek modeli ile karşılaştırır.
4. Doğrulama dört karardan birini verir: yürüt, sor, uyarla veya güvenli dur. Plan uygulanabilirse deterministik yürütme (Behavior Tree) devreye girer.
5. Yürütme sırasında bir adım başarısız olursa sonuç doğrulama katmanına döner ve plan uyarlanır.
6. Komut eksik veya muğlaksa sistem açıklama ister.
7. Yanlış nesne, engel, ortam değişikliği veya güvensiz/uygulanamaz komutta plan uyarlanır veya güvenli duruma geçilir.

Sembolik dünya ve Behavior Tree yürütücüsü uygulandı (bkz. 07); dil, algılama ve doğrulama katmanları henüz yazılmadı.

## 06 Geliştirme araçları / simülasyon ortamı

**Karar: katmanlı simülasyon.** Sistem `World` arayüzü (`src/interfaces/world.py`) sayesinde simülatörden bağımsızdır.

- **Seviye 1, sembolik dünya** (`simulation/symbolic/`): JSON sahne üzerinde çalışır, her bilgisayarda kurulumsuz çalışır. Deneyler tekrarlanabilirlik için burada koşulur.
- **Seviye 2, AI2-THOR:** Görsel kanıt (kamera görüntüsü) ve demo için. Hazır ev sahneleri, durumu değiştirilebilir nesneler ve yüksek seviye "aç, al, bırak" eylemleri sunar; her eylemden sonra nesne konum ve durumlarını döndürür (Kolve vd., 2017). macOS'ta test edilecek; çalışmazsa PyBullet kullanılacak.
- **Seviye 3 (opsiyonel):** ROS 2 + Gazebo veya Isaac Sim ile taşınabilirlik denemesi.

Gerekçe: Ekipte macOS ve Windows bilgisayarlar var ve NVIDIA GPU garantisi yok. Projenin katkısı dil, doğrulama ve yürütme zinciri olduğu için fizik gerçekçiliği ikincil. Benzer şekilde, BT literatüründe davranış önce fiziği hesaba katmayan basit bir simülatörde geliştirilip sonra fizikli simülatörde doğrulanıyor (Iovino & Smith, 2023).

Ortamların genel karşılaştırması (ölçülmüş performans sayısı içermez):

| Ortam | Artıları | Eksileri |
| --- | --- | --- |
| ROS 2 + Gazebo + Nav2 | Açık kaynak ve derslerde yaygındır. Nav2 ile gezinme yığını hazırdır. ROS ekosistemiyle bütünleşir. | Görsel gerçekçilik çoğu zaman daha sınırlıdır. Kurulum ve paket yönetimi ağır olabilir. VLM ve zengin algılama için ek entegrasyon gerekir. |
| Isaac Sim | Yüksek görsel gerçekçilik sunar. GPU ile hızlandırılır. ROS 2 köprüsü vardır. Algılama ve VLM denemeleri için elverişli olabilir. | NVIDIA GPU ister. Kurulum daha ağırdır. Donanım ve platform kısıtları vardır. |
| Habitat | Embodied AI araştırmasında yaygındır. Benzetim görece hızlıdır. Dil koşullu gezinme görevlerine uygundur. | Klasik robot ara katmanı (ROS) ile bağ kurmak ek iş ister. Tam manipülasyon ve kontrol yığını her zaman hazır olmayabilir. |
| AI2-THOR | Etkileşimli iç mekan sahneleri ve nesne etkileşimi sunar. Ev tipi görevler için kullanışlıdır. | Oyun motoru tabanlıdır. Fizik ve robot modelleri daha soyut olabilir. ROS benzeri tam bir kontrol yığınına daha uzaktır. |

### Kullanılan araçlar ve sürümler

Rapordaki sonuçların tekrarlanabilmesi için sürümler burada tutulur; bir sürüm değiştiğinde aynı PR'da güncellenir.

| Bileşen | Sürüm / model | Not |
| --- | --- | --- |
| Python | 3.11 | 3.12 ile de test edildi |
| pydantic | 2.14.3 | Arayüz şemaları |
| py_trees | 2.6.0 | Behavior Tree yürütme |
| google-genai | 3.2.0 | Gemini API istemcisi |
| python-dotenv | 1.2.4 | API anahtarı `.env` dosyasından okunur |
| pytest | 9.2.0 | Testler |
| LLM ve VLM | Gemini API, ücretsiz katman: model henüz seçilmedi | Seçilince tam model adı, erişim tarihi ve `temperature` değeri yazılacak |
| Seviye 2 simülatör | AI2-THOR: sürüm macOS testinden sonra yazılacak | Yedek: PyBullet |

## 07 Kurulum ve projeyi çalıştırma adımları

Şu an Seviye 1 sembolik dünya ve Behavior Tree yürütücüsü çalışıyor. Dil (LLM), algılama (VLM) ve doğrulama modülleri henüz eklenmedi; AI2-THOR (Seviye 2) macOS'ta test edilecek.

### Çalışan parçalar

| Dosya | Ne yapar |
| --- | --- |
| `src/interfaces/schemas.py` | Modüller arası veri formatları: sahne, plan, grounding, doğrulama kararı, yürütme sonucu |
| `src/interfaces/world.py` | Her simülatörün uyguladığı `World` arayüzü |
| `simulation/symbolic/world.py` | Sembolik dünya: `navigate`, `pick`, `place`, `open`, `close`. Ön koşul sağlanmazsa sahne değişmez ve nedeni döner (ör. `robot_not_at_object`, `hand_full`, `door_closed`) |
| `simulation/symbolic/scenes/` | Üç sahne: `home_office`, `apartment`, `office` |
| `src/execution/bt_executor.py` | Planı `py_trees` ile yürütür. Her adım "zaten sağlandı mı? → değilse yap" kalıbıyla sarılır; ilk başarısız adımda durur ve ağacı terminalde çizer |
| `tests/` | Tüm modüllerin testleri |

### Sahneler

| Sahne | İçerik | Kapsadığı senaryolar |
| --- | --- | --- |
| `home_office` | Mutfak ve ofis; kırmızı ve mavi kupa, dizüstü bilgisayar, çekmece | Çok adımlı görev, muğlak komut ("kupayı getir") |
| `apartment` | Mutfak, oturma odası, koridor, kapısı kapalı yatak odası; sıcak kahve, dizüstü bilgisayar, kırmızı ve mavi kitap | Engellenmiş hedef (kapalı kapı), yanlış nesne, güvensiz komut, ortamla çelişen komut (elma yok) |
| `office` | Resepsiyon, toplantı odası, koridor, kapısı kapalı depo, ulaşılamayan balkon; iki aynı beyaz bardak | Muğlak komut, engellenmiş hedef |

### Gereksinimler

Python 3.11 (3.12 ile de test edildi) ve Git. GPU gerekmez.

### Kurulum

macOS:

```bash
git clone https://github.com/zelihaguven/verified-llm-robot-planner.git
cd verified-llm-robot-planner
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
git clone https://github.com/zelihaguven/verified-llm-robot-planner.git
cd verified-llm-robot-planner
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Testleri çalıştırma

```bash
pytest -v
```

Tüm testlerin `PASSED` görünmesi gerekir.

### Örnek: bir planı Behavior Tree ile çalıştırma

Terminalde `python` yazıp `>>>` satırına aşağıdakini yapıştırın. Robot kapalı kapı yüzünden önce başarısız olur, ikinci planda kapıyı açıp kitabı alır:

```python
from simulation.symbolic.world import SymbolicWorld
from src.execution.bt_executor import execute
from src.interfaces import PlanStep
plan = [PlanStep(id=1, action="navigate", args={"target": "bedroom_nightstand"}), PlanStep(id=2, action="pick", args={"object": "book_1"})]
print(execute(plan, SymbolicWorld("apartment"), on_tick=print))
plan = [PlanStep(id=1, action="navigate", args={"target": "hallway"}), PlanStep(id=2, action="open", args={"object": "door_bedroom"}), PlanStep(id=3, action="navigate", args={"target": "bedroom_nightstand"}), PlanStep(id=4, action="pick", args={"object": "book_1"})]
print(execute(plan, SymbolicWorld("apartment"), on_tick=print))
```

Ağaçta ✓ başarılı, ✕ başarısız, `-` hiç çalışmamış demektir. "zaten sağlandı mı?" satırındaki ✕ hata değildir: adımın hedefi henüz gerçekleşmediği için eylemin yapılması gerektiğini gösterir.

## 08 Test, deney, metrik ve örnek çıktılar

Deneyler henüz koşulmadı; sonuç satırları boş bırakılmıştır, uydurma sayı yazılmamıştır. Çıktılar [results/](results/) altına konacaktır.

**Deney düzeni:** Her komut iki koşulda çalıştırılır ve sonuçlar yan yana konur: A) yalnızca LLM (plan doğrulanmadan yürütülür) ve B) LLM + doğrulama. Her koşul üç kez, `temperature=0` ile koşulur. Deneyler sembolik dünyanın üç sahnesinde yapılır (bkz. 07).

### Deney senaryoları

- Çok adımlı ofis veya ev komutu
- Eksik veya muğlak komut
- Ortamla çelişen komut
- Yanlış nesne
- Engellenmiş hedef
- Görev sırasında ortam değişikliği
- Güvensiz veya uygulanamaz komut
- Aynı hedefin farklı ifadelerle (parafrazlarla) verilmesi

### Ölçütler

| Ölçüt | Açıklama | Sonuç |
| --- | --- | --- |
| Plan başarı oranı | Üretilen planın görev hedefiyle uyumu |  |
| Yürütme başarı oranı | Planın simülasyonda tamamlanması |  |
| Uygulanabilirlik | Doğrulama sonrası planın fiziksel olarak yürütülebilir olması |  |
| Açıklama isteme | Gerektiğinde kullanıcıya soru sorulması |  |
| Güvenli durum | Güvensiz veya uygulanamaz komutta güvenli duruma geçiş |  |
| Parafraz tutarlılığı | Aynı hedefin farklı ifadelerinde davranışın tutarlılığı |  |
| Geçersiz veya hayal ürünü adım oranı | Ortamda olmayan nesne veya yetenek dışı eylem |  |

### Örnek çıktılar

Henüz deney çalıştırılmadığı için örnek çıktı yoktur. Log, ekran görüntüsü ve tablo dosyaları `results/` klasöründe toplanacaktır.

<a id="ilerleme"></a>
## 09 Yol haritası ve düzenli İlerleme Günlüğü

### Yol haritası

Proje 16 Kasım – 20 Aralık 2026 arasında beş haftada tamamlanır.

| Hafta | Tarih | Odak | Durum |
| --- | --- | --- | --- |
| 1 | 16–22 Kasım | Kurulum, ortak arayüzler, simülasyon kararı | Arayüzler ve sembolik dünya hazır (PR incelemede); AI2-THOR testi bekliyor |
| 2 | 23–29 Kasım | Modüller (sahte veriyle) | Sembolik dünya (3 sahne) ve BT yürütücü hazır |
| 3 | 30 Kasım – 6 Aralık | Entegrasyon: uçtan uca görev | Başlamadı |
| 4 | 7–13 Aralık | Deneyler ve demo | Başlamadı |
| 5 | 14–20 Aralık | Rapor ve teslim | Başlamadı |

### İlerleme Günlüğü

| TARİH | YAPILAN ÇALIŞMA | MEVCUT DURUM / SORUN | SONRAKİ ADIM |
| --- | --- | --- | --- |
| 2026-11-11 | Repo kuruldu, konu seçildi | Simülasyon ortamı kararı bekleniyor | Simülasyon ortamı seçimi ve literatür taraması |
| 2026-11-12 | Proje planı ve 5 haftalık iş planı hazırlandı. Repo düzenlendi. Ortak veri formatları (`src/interfaces/`) ve sembolik dünya (`simulation/symbolic/`) yazıldı. | Simülasyon kararı katmanlı yapı olarak verildi (bkz. 06). Kod `interfaces-v1` PR'ında ekip incelemesini bekliyor. | Literatür taraması, Behavior Tree yürütücüsü |
| 2026-11-13 | Behavior Tree ve simülasyon üzerine 6 kaynak okundu (bkz. 10). BT yürütücüsü (`src/execution/`) yazıldı. İki yeni sahne ve kapı kuralı eklendi. README güncellendi. 32 test geçiyor. | Testler, hafızasız kök Sequence'in tamamlanmış ara adımları tekrar çalıştırdığını gösterdi; kök hafızalı yapıldı (bkz. 04). AI2-THOR macOS testi yapılmadı. | AI2-THOR testi, PR'ın ekip onayıyla birleştirilmesi |

## 10 Araştırma kaynakları ve referanslar

Tam künyeler ve bağlantılar [references/README.md](references/README.md) dosyasındadır. Aşağıdaki kaynakların hepsi açık kaynaktan doğrulanmıştır; uydurma kaynak eklenmemiştir.

1. Ahn, M. ve diğerleri (2022). *Do As I Can, Not As I Say: Grounding Language in Robotic Affordances* (SayCan). arXiv:2204.01691. <https://arxiv.org/abs/2204.01691>
2. Huang, W., Xia, F., Xiao, T. ve diğerleri (2022). *Inner Monologue: Embodied Reasoning through Planning with Language Models*. arXiv:2207.05608. <https://arxiv.org/abs/2207.05608>
3. Liang, J., Huang, W., Xia, F. ve diğerleri (2022). *Code as Policies: Language Model Programs for Embodied Control*. arXiv:2209.07753. <https://arxiv.org/abs/2209.07753>
4. Singh, I., Blukis, V., Mousavian, A. ve diğerleri (2022). *ProgPrompt: Generating Situated Robot Task Plans using Large Language Models*. arXiv:2209.11302. <https://arxiv.org/abs/2209.11302>
5. Liu, B., Jiang, Y., Zhang, X., Liu, Q., Zhang, S., Biswas, J. ve Stone, P. (2023). *LLM+P: Empowering Large Language Models with Optimal Planning Proficiency*. arXiv:2304.11477. <https://arxiv.org/abs/2304.11477>
6. Iovino, M., Scukins, E., Styrud, J., Ögren, P. ve Smith, C. (2022). *A Survey of Behavior Trees in Robotics and AI*. Robotics and Autonomous Systems, 154, 104096. arXiv:2005.05842. <https://arxiv.org/abs/2005.05842>
7. Ögren, P. ve Sprague, C. I. (2022). *Behavior Trees in Robot Control Systems*. Annual Review of Control, Robotics, and Autonomous Systems, 5, 81–107. arXiv:2203.13083. <https://arxiv.org/abs/2203.13083>
8. Iovino, M. ve Smith, C. (2023). *Behavior Trees for Robust Task Level Control in Robotic Applications*. arXiv:2301.06434. <https://arxiv.org/abs/2301.06434>
9. Izzo, R. A., Bardaro, G. ve Matteucci, M. (2024). *BTGenBot: Behavior Tree Generation for Robotic Tasks with Lightweight LLMs*. IROS 2024. arXiv:2403.12761. <https://arxiv.org/abs/2403.12761>
10. Kambhampati, S. ve diğerleri (2024). *Position: LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks*. ICML 2024, PMLR 235. arXiv:2402.01817. <https://arxiv.org/abs/2402.01817>
11. Kolve, E. ve diğerleri (2017). *AI2-THOR: An Interactive 3D Environment for Visual AI*. arXiv:1712.05474. <https://arxiv.org/abs/1712.05474>
