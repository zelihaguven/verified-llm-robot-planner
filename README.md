# Doğrulanmış Görev Planlamalı, Doğal Dil Rehberli Servis Robotu

Bu depo, bir robotik dersi grup projesi için belge ve klasör iskeletidir. Uygulama kodu henüz yoktur. Amaç, kapsam, yöntem ve deney metinleri ilk taslaktır; grup içinde güncellenecektir.

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
| Zeliha Ilgın Güven | [zelihaguven](https://github.com/zelihaguven) | `cv/` altına `Ad_Soyad_CV.pdf` kuralına göre eklenecek |
| Neslihan Özdemir | [eklenecek] | `cv/` altına `Ad_Soyad_CV.pdf` kuralına göre eklenecek |
| Tuğba Önen | [eklenecek] | `cv/` altına `Ad_Soyad_CV.pdf` kuralına göre eklenecek |
| Buse Yılmaz | [eklenecek] | `cv/` altına `Ad_Soyad_CV.pdf` kuralına göre eklenecek |

GitHub kullanıcı adları ve CV'ler daha sonra eklenecektir.

## 02 Amaç, problem tanımı ve proje kapsamı

Bu bölüm bir ilk taslaktır.

### Amaç

Ofis veya ev benzeri bir ortamda çalışan bir servis robotunun, doğal dille verilen çok adımlı görevleri yerine getirmesini sağlamak. Robot, komutu yalnızca dilsel olarak makul bir plana çevirmekle kalmaz; yorumu görsel kanıt, semantik bilgi ve fiziksel yeteneklerle tutarlı hale getirir.

### Problem tanımı

Kullanıcı komutları eksik, muğlak veya ortamla çelişkili olabilir. Dil modelinin ürettiği görev yorumu dilsel olarak doğru görünse bile fiziksel olarak uygulanamaz olabilir. Sistemin şu durumlarda açıklama istemesi, planı uyarlaması veya güvenli duruma geçmesi gerekir:

- yanlış nesne
- engellenmiş hedef
- ortam değişikliği
- güvensiz veya yerine getirilemeyen komut

Aynı amacın farklı ifadelerle (parafrazlarla) verilmesi de incelenecektir.

### Proje kapsamı (taslak iş paketleri)

1. Literatür taraması: dil modelleri, görsel-dil modelleri, language grounding, görev planlama, Behavior Tree, HTN, plan doğrulama ve hayal ürünü çıktı (hallucination) riskleri.
2. Simülasyon ortamının seçimi ve kurulumu.
3. Dil katmanı: doğal dil komutunun görev yorumuna çevrilmesi.
4. Algılama ve görsel-dil ile grounding.
5. Planlama, plan doğrulama ve deterministik yürütme (Behavior Tree).
6. Açıklama isteme, plan uyarlama ve güvenli durum davranışları.
7. Deney senaryoları, ölçütler, sonuçların derlenmesi ve rapor.

Kapsam dışı (taslak): gerçek robot üzerinde deney, yeni bir temel model eğitimi ve simülasyon kararı verilmeden somut kurulum talimatı.

### Taslak araştırma soruları

- Dil modelinin görev yorumu, görsel kanıt, semantik bilgi ve robotun fiziksel yetenekleriyle nasıl tutarlı hale getirilir?
- Eksik, muğlak veya ortamla çelişen komutlarda sistem ne zaman açıklama istemeli, planı uyarlamalı veya güvenli duruma geçmelidir?
- Hangi iş dil modeline, hangisi algılamaya, hangisi deterministik robot mantığına bırakılmalıdır?
- Aynı hedefin farklı ifadeleri karşısında plan ve davranış ne kadar tutarlı kalır?
- Plan doğrulama, hayal ürünü veya uygulanamaz adımları ne ölçüde azaltabilir?

## 03 Kullanılacak yöntemler ve algoritmalar

Bu bölüm bir ilk taslaktır. Kesin yöntem seçimi henüz yapılmamıştır.

- **Büyük dil modeli (LLM):** Kullanıcı komutunu görev yorumuna ve aday plan adımlarına çevirmek.
- **Görsel-dil modeli (VLM) ve language grounding:** Dilsel nesne ve konum iddialarını görsel kanıtla ilişkilendirmek.
- **Görev planlama:** Çok adımlı komutu sıralı veya hiyerarşik bir plana dökmek. Aday biçimler Behavior Tree ve HTN'dir.
- **Plan doğrulama:** Üretilen planın yetenekler, semantik bilgi ve ortam durumuyla çelişip çelişmediğini denetlemek.
- **Deterministik yürütme:** Onaylanan planı Behavior Tree ile çalıştırmak; düşük seviye kontrolü dil modeline bırakmamak.
- **Hata ve belirsizlik yönetimi:** Yanlış nesne, engel, ortam değişikliği ve güvensiz komutlarda açıklama, uyarlama veya güvenli durum.

Araştırılacak ayrım: dil modeli semantik yorum ve aday plan üretebilir; algılama ortam kanıtını sağlar; uygulanabilirlik denetimi ve yürütme deterministik robot mantığında kalmalıdır. Dilsel olarak makul bir plan, doğrulamadan geçmeden yürütülmemelidir.

## 04 Yöntem seçim gerekçeleri ve alternatifler

Bu karşılaştırmalar taslaktır. Grup, literatür taraması ve erken denemelerden sonra seçimleri gerekçelendirecektir.

| Yaklaşım | Ne işe yarar | Sınır ve gerekçe (taslak) |
| --- | --- | --- |
| Yalnızca dil modeli ile planlama | Komutu hızlıca adımlara böler | Ortam ve yeteneklerle bağ kurulmazsa uygulanamaz veya güvensiz plan çıkabilir |
| Behavior Tree (BT) | Onaylı planı belirgin, tekrar edilebilir bir ağaç olarak yürütür | Tek başına doğal dil yorumu ve görsel grounding üretmez; yürütme katmanı olarak uygundur |
| HTN | Görevi hiyerarşik alt görevlere ayırır | Alan bilgisi ve yöntem tanımları ister; dil katmanı ile nasıl bağlanacağı netleştirilecektir |
| Dil modeli + doğrulama + deterministik yürütme (taslak yönelim) | Yorumu LLM üretir, uygulanabilirlik denetlenir, yürütme BT ile yapılır | Doğrulama kuralları ve yetenek modeli tasarlanmalıdır; bu projenin ana hipotezidir |

Simülasyon ortamı henüz seçilmedi (`Karar verilmedi`). Ortam alternatifleri ve artı/eksi tablosu [06](#06-geliştirme-araçları--simülasyon-ortamı) bölümündedir.

## 05 Sistem mimarisi ve temel çalışma akışı

Taslak mimari [docs/architecture.md](docs/architecture.md) dosyasındadır. Özet akış:

1. Kullanıcı doğal dil komutu verir.
2. Dil katmanı komutu görev yorumuna ve aday plana çevirir.
3. Doğrulama ve grounding katmanı bu yorumu algılama (VLM), semantik bilgi ve yetenek modeli ile karşılaştırır.
4. Plan uygulanabilirse deterministik yürütme (Behavior Tree) devreye girer.
5. Komut eksik veya muğlaksa sistem açıklama ister.
6. Yanlış nesne, engel, ortam değişikliği veya güvensiz/uygulanamaz komutta plan uyarlanır veya güvenli duruma geçilir.

Bu ayrım taslaktır; uygulama kodu henüz yazılmamıştır.

## 06 Geliştirme araçları / simülasyon ortamı

**Karar verilmedi.**

Kurulum, robot modeli ve sahne seçimi bu karara bağlıdır. Aşağıdaki karşılaştırma geneldir; ölçülmüş performans sayısı içermez.

| Ortam | Artıları | Eksileri |
| --- | --- | --- |
| ROS 2 + Gazebo + Nav2 | Açık kaynak ve derslerde yaygındır. Nav2 ile gezinme yığını hazırdır. ROS ekosistemiyle bütünleşir. | Görsel gerçekçilik çoğu zaman daha sınırlıdır. Kurulum ve paket yönetimi ağır olabilir. VLM ve zengin algılama için ek entegrasyon gerekir. |
| Isaac Sim | Yüksek görsel gerçekçilik sunar. GPU ile hızlandırılır. ROS 2 köprüsü vardır. Algılama ve VLM denemeleri için elverişli olabilir. | NVIDIA GPU ister. Kurulum daha ağırdır. Donanım ve platform kısıtları vardır. |
| Habitat | Embodied AI araştırmasında yaygındır. Benzetim görece hızlıdır. Dil koşullu gezinme görevlerine uygundur. | Klasik robot ara katmanı (ROS) ile bağ kurmak ek iş ister. Tam manipülasyon ve kontrol yığını her zaman hazır olmayabilir. |
| AI2-THOR | Etkileşimli iç mekan sahneleri ve nesne etkileşimi sunar. Ev tipi görevler için kullanışlıdır. | Oyun motoru tabanlıdır. Fizik ve robot modelleri daha soyut olabilir. ROS benzeri tam bir kontrol yığınına daha uzaktır. |

Geliştirme dili olarak Python öngörülmektedir. Somut paket listesi `requirements.txt` içinde, simülasyon kararı sonrası doldurulacaktır.

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

Bu bölüm bir ilk taslaktır. Sonuç satırları boş bırakılmıştır; uydurma sayı yazılmamıştır. Çıktılar [results/](results/) altına konacaktır.

### Taslak deney senaryoları

- Çok adımlı ofis veya ev komutu
- Eksik veya muğlak komut
- Ortamla çelişen komut
- Yanlış nesne
- Engellenmiş hedef
- Görev sırasında ortam değişikliği
- Güvensiz veya uygulanamaz komut
- Aynı hedefin farklı ifadelerle (parafrazlarla) verilmesi

### Taslak ölçütler

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

### Yol haritası (taslak)

1. Literatür taramasını derinleştirmek ve kaynak listesini genişletmek
2. Simülasyon ortamını seçmek ve kurulum adımlarını yazmak
3. Dil, algılama, doğrulama ve Behavior Tree katmanlarının arayüzlerini netleştirmek
4. Deney senaryolarını ve ölçütleri sahneye göre somutlaştırmak
5. Deneyleri koşup sonuçları ve raporu doldurmak

### İlerleme Günlüğü

| TARİH | YAPILAN ÇALIŞMA | MEVCUT DURUM / SORUN | SONRAKİ ADIM |
| --- | --- | --- | --- |
| 2026-11-11 | Repo kuruldu, konu seçildi | Simülasyon ortamı kararı bekleniyor | Simülasyon ortamı seçimi ve literatür taraması |

## 10 Araştırma kaynakları ve referanslar

Tam künyeler ve bağlantılar [references/README.md](references/README.md) dosyasındadır. Aşağıda doğrulanmış başlangıç listesinin özeti vardır. Uydurma kaynak eklenmemiştir.

1. Ahn, M. ve diğerleri (2022). *Do As I Can, Not As I Say: Grounding Language in Robotic Affordances* (SayCan). arXiv:2204.01691. <https://arxiv.org/abs/2204.01691>
2. Huang, W., Xia, F., Xiao, T. ve diğerleri (2022). *Inner Monologue: Embodied Reasoning through Planning with Language Models*. arXiv:2207.05608. <https://arxiv.org/abs/2207.05608>
3. Liang, J., Huang, W., Xia, F. ve diğerleri (2022). *Code as Policies: Language Model Programs for Embodied Control*. arXiv:2209.07753. <https://arxiv.org/abs/2209.07753>
4. Singh, I., Blukis, V., Mousavian, A. ve diğerleri (2022). *ProgPrompt: Generating Situated Robot Task Plans using Large Language Models*. arXiv:2209.11302. <https://arxiv.org/abs/2209.11302>
5. Liu, B., Jiang, Y., Zhang, X., Liu, Q., Zhang, S., Biswas, J. ve Stone, P. (2023). *LLM+P: Empowering Large Language Models with Optimal Planning Proficiency*. arXiv:2304.11477. <https://arxiv.org/abs/2304.11477>
