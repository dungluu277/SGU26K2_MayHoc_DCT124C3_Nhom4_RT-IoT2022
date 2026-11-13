# BÁO CÁO TỔNG HỢP EDA — RT_IOT2022

**Giai đoạn:** Exploratory Data Analysis (EDA)  
**Dữ liệu khảo sát:** `data/raw/RT_IOT2022.csv`  
**Bài toán:** Phân loại lưu lượng mạng IoT theo 12 nhãn `Attack_type`  
**Ngày tổng hợp:** 12/11/2026  
**Trạng thái:** Hoàn thành khảo sát EDA, **chưa làm sạch, biến đổi, chia tập hay huấn luyện mô hình**.

> **Mục tiêu báo cáo:** Ghi nhận **vấn đề phát hiện từ dữ liệu**, đưa ra bằng chứng và hình thành **giả thuyết cần kiểm chứng** trong các giai đoạn tiếp theo. EDA không nhằm chọn biểu đồ “đẹp nhất”, cũng không chứng minh một phương pháp tiền xử lý là tối ưu.

---

## 1. Phạm vi và phương pháp khảo sát

01_Data_Overview.ipynb: Cấu trúc, kiểu dữ liệu, chất lượng, thống kê, nhãn | Dữ liệu trùng, cột hằng, mất cân bằng 
02_Data_Distribution.ipynb: Skewness, Histogram, KDE, `proto`, `service`, Phân phối lệch, nhiều giá trị 0, giá trị phân loại áp đảo
03_Outliers_Correlation.ipynb: IQR, Boxplot, Pearson, Spearman, Heatmap, Giới hạn của IQR, giá trị ngoại lệ, đặc trưng dư thừa
04_Feature_Target_Analysis.ipynb: Phân tích đặc trưng theo nhãn, cổng mạng, MI khảo sát,Phụ thuộc nhãn, nguy cơ học đặc điểm riêng của tập dữ liệu

## 2. Tổng quan dataset

| Chỉ tiêu | Kết quả |
|---|---:|
| Số bản ghi | **123.117** |
| Tổng số cột | **85** |
| Số cột kiểu số | **82** (bao gồm `Unnamed: 0`) |
| Số cột kiểu object | **3** (`proto`, `service`, `Attack_type`) |
| Số đặc trưng số khi không tính `Unnamed: 0` | **81** |
| Nhãn mục tiêu | `Attack_type` |
| Số lớp mục tiêu | **12** |
| Giá trị thiếu (NaN) | **0** |
| Giá trị vô hạn (Inf) trong cột số | **0** |

**Nhận xét:** Dữ liệu không có NaN/Inf ở trạng thái khảo sát, nhưng **không có nghĩa là đã sạch**: còn trùng lặp, cột hằng, phân phối bất thường và chênh lệch lớp rất lớn. `Unnamed: 0` có dấu hiệu là cột chỉ số khi xuất CSV; cần xác nhận vai trò trước khi xây dựng tập đầu vào.

## 3. Vấn đề 1 — Dữ liệu trùng lặp và khả năng mâu thuẫn nhãn

| Kiểm tra | Kết quả |
|---|---:|
| Dòng trùng khi xét đủ 85 cột | 0 |
| Dòng trùng khi bỏ `Unnamed: 0` nhưng vẫn xét nhãn | **5.195** |
| Nhóm có toàn bộ đặc trưng đầu vào giống nhau nhưng mang nhiều hơn một nhãn | **6 nhóm** |
| Tổng số dòng nằm trong 6 nhóm đó | **128 dòng** |

**Vấn đề phát hiện:** Cột `Unnamed: 0` làm phép kiểm tra trùng toàn bộ dòng bỏ sót nhiều trường hợp. Ngoài ra, có một số nhóm bản ghi có thông số đầu vào giống nhau nhưng nhãn `Attack_type` không đồng nhất. **128 dòng liên quan không đồng nghĩa 128 nhãn đều sai**; cần xem trực tiếp từng nhóm và đối chiếu nguồn gốc dữ liệu.

**Nguy cơ:** Nếu các bản ghi giống nhau xuất hiện đồng thời trong Train và Validation thì điểm đánh giá có thể lạc quan; những mẫu có đặc trưng giống nhau nhưng nhãn trái nhau cũng gây khó cho mô hình.

**Đề xuất cần kiểm chứng:**

- Kiểm tra nguồn gốc và ý nghĩa của cột `Unnamed: 0`.
- Kiểm tra và xác định quy tắc xử lý trùng lặp **trước khi chia tập**, ghi rõ số dòng còn lại theo từng nhãn.
- Phân tích riêng 6 nhóm mâu thuẫn nhãn, không tự động chọn một nhãn tùy ý.
- Sau khi chia, kiểm tra mức độ trùng lặp giữa Train và Validation; không sử dụng tập Test trong các thực nghiệm hiện tại.

## 4. Vấn đề 2 — Thuộc tính hằng và đặc trưng gần như luôn bằng 0

- **1 thuộc tính hằng:** `bwd_URG_flag_count` (100% giá trị bằng 0).
- **16 đặc trưng số** (không tính `Unnamed: 0`) có **ít nhất 95% giá trị bằng 0**.
- Ví dụ: `flow_CWR_flag_count` **99,942%**, `fwd_bulk_bytes` **99,800%**, `bwd_bulk_bytes` **99,101%**, `active.std` **98,627%** giá trị bằng 0.

**Vấn đề phát hiện:** Một số cột rất thưa hoặc không có sự biến thiên. Tuy nhiên, các sự kiện hiếm với giá trị khác 0 vẫn có thể đặc biệt hữu ích trong nhận diện tấn công.

**Đề xuất:** Xem xét loại cột hằng khỏi đầu vào; phân tích tỷ lệ giá trị khác 0 theo từng lớp **trước khi** quyết định loại các cột nhiều số 0. Không loại cột chỉ vì có tỷ lệ số 0 cao.

## 5. Vấn đề 3 — Phân phối lệch và thang đo không đồng nhất

- **65 đặc trưng số** có `|Skewness| > 3` (không tính cột chỉ số; cột hằng không có Skewness xác định).
- Các ví dụ lệch mạnh:

| Đặc trưng | Skewness xấp xỉ |
|---|---:|
| `bwd_bulk_bytes` | 340,50 |
| `bwd_bulk_packets` | 340,49 |
| `active.std` | 287,99 |
| `bwd_pkts_payload.tot` | 280,81 |
| `flow_pkts_payload.tot` | 271,97 |
| `bwd_pkts_tot` | 249,91 |

**Vấn đề phát hiện:** Phân phối nhiều cột tập trung gần giá trị thấp nhưng có đuôi phải dài. Các cột có thang đo khác nhau có thể làm việc tối ưu hóa MLP khó hơn nếu đưa trực tiếp vào mô hình. Histogram ở thang gốc cũng có thể bị giá trị cực lớn che khuất.

**Đề xuất:** Khảo sát riêng các cột có Skewness cao và nhiều số 0; trong phần thực nghiệm có thể so sánh **StandardScaler**, **RobustScaler**, hoặc **`log1p` cho cột không âm phù hợp**. Phải đánh giá trên Validation; không áp dụng đồng loạt trước khi kiểm chứng.

## 6. Vấn đề 4 — Mất cân bằng 12 lớp mục tiêu

| Nhãn `Attack_type` | Số mẫu |
|---|---:|
| `DOS_SYN_Hping` | 94.659 |
| `Thing_Speak` | 8.108 |
| `ARP_poisioning` | 7.750 |
| `MQTT_Publish` | 4.146 |
| `NMAP_UDP_SCAN` | 2.590 |
| `NMAP_XMAS_TREE_SCAN` | 2.010 |
| `NMAP_OS_DETECTION` | 2.000 |
| `NMAP_TCP_scan` | 1.002 |
| `DDOS_Slowloris` | 534 |
| `Wipro_bulb` | 253 |
| `Metasploit_Brute_Force_SSH` | 37 |
| `NMAP_FIN_SCAN` | 28 |

- `DOS_SYN_Hping` chiếm khoảng **76,89%** dữ liệu.
- Tỷ lệ số mẫu lớp lớn nhất so với nhỏ nhất: khoảng **3.380,68 : 1**.

**Vấn đề phát hiện:** Chênh lệch số mẫu rất lớn. Accuracy có thể cao dù mô hình dự đoán kém các lớp hiếm; các lớp chỉ có vài chục mẫu khiến kết quả đánh giá dễ dao động.

**Đề xuất:** Dùng **Macro-F1** làm chỉ số trọng tâm, đồng thời báo cáo **Precision, Recall, F1-score từng lớp** và Confusion Matrix. Có thể thử RandomOverSampler hoặc điều chỉnh trọng số lớp **chỉ trên Train**, tuyệt đối không cân bằng Validation để làm đẹp điểm đánh giá.

## 7. Vấn đề 5 — Quy tắc IQR không phù hợp đồng đều cho mọi cột

- **66/81** đặc trưng số có **IQR = 0**; chỉ **15/81** có IQR > 0.
- Trong những cột có IQR > 0, các số lượng giá trị ngoài ngưỡng 1,5 × IQR cao nhất gồm:

| Đặc trưng | Số giá trị nằm ngoài ngưỡng |
|---|---:|
| `flow_iat.max` | 19.180 |
| `flow_iat.tot` | 19.180 |
| `flow_iat.avg` | 19.180 |
| `flow_duration` | 19.171 |
| `active.max` | 19.165 |

**Quan sát đặc biệt theo nhãn:** Khi dùng ngưỡng IQR **toàn cục** cho `flow_duration`, tỷ lệ bị đánh dấu ngoại lệ xấp xỉ **99,83% ở `MQTT_Publish`**, **99,44% ở `DDOS_Slowloris`**, **97,83% ở `Thing_Speak`**, nhưng chỉ **0,15% ở `DOS_SYN_Hping`**.

**Vấn đề phát hiện:** Ngưỡng ngoại lệ toàn cục có thể chịu ảnh hưởng của lớp chiếm đa số. Nhiều giá trị nằm ngoài IQR thuộc các lớp hợp lệ khác và có thể mang tín hiệu phân biệt tấn công.

**Đề xuất:** **Không tự động xóa tất cả mẫu ngoại lệ**. Phân tích thêm theo nhãn và thử các phép biến đổi bền vững với đuôi dài thay vì mặc định coi ngoại lệ là lỗi.

## 8. Vấn đề 6 — Tương quan rất cao giữa các đặc trưng

Sau khi loại cột hằng khỏi **phép tính tương quan** (không xóa khỏi CSV gốc), còn 80 đặc trưng số có biến thiên:

- **52 cặp** có `|Pearson| >= 0,95`.
- **180 cặp** có `|Spearman| >= 0,95`.
- `flow_duration` và `flow_iat.tot` có Pearson khoảng **0,99999998**.
- Một số cặp khác: `bwd_pkts_per_sec`–`flow_pkts_per_sec`; `fwd_pkts_per_sec`–`flow_pkts_per_sec`; `bwd_bulk_bytes`–`bwd_bulk_packets`.

**Vấn đề phát hiện:** Nhiều đặc trưng có khả năng truyền tải thông tin rất giống nhau, làm tăng số chiều và mức độ dư thừa đầu vào. **Tương quan cao không đồng nghĩa có Data Leakage**, và không chứng minh rằng giảm đặc trưng chắc chắn tăng Macro-F1.

**Đề xuất:** Thử nghiệm Correlation Filter với một hoặc nhiều ngưỡng hợp lý; danh sách cột cần giữ/bỏ phải **được xác định từ Train**, sau đó áp dụng nguyên trạng cho Validation. So sánh số chiều, Macro-F1 từng lớp và chi phí huấn luyện.

## 9. Vấn đề 7 — Phụ thuộc vào giao thức, dịch vụ và cổng mạng

**Phân bố thuộc tính phân loại:**

- `proto`: `tcp` **110.427** mẫu (89,69%), `udp` **12.633**, `icmp` **57**.
- `service`: `-` **102.861** mẫu (83,55%), `dns` **9.753**, `mqtt` **4.132**, `http` **3.464**, cùng một số giá trị hiếm khác.
- Ký hiệu `-` trong `service` **chưa được xác nhận là giá trị thiếu**, không tự động thay bằng NaN.

**Quan hệ với nhãn:**

| Nhãn | Dấu hiệu |
|---|---|
| `DOS_SYN_Hping` | 100% mẫu có `service = "-"`, `proto = "tcp"` và `id.resp_p = 21` |
| `MQTT_Publish` | ~99,66% mẫu có `service = "mqtt"`; ~99,90% có `id.resp_p = 1883` |
| `DDOS_Slowloris` | ~97,94% mẫu có `service = "http"`; ~99,06% có `id.resp_p = 80` |

**Vấn đề phát hiện:** Một số lớp được nhận diện rất dễ qua service hoặc cổng đích. Đây có thể là thông tin thực sự hữu ích, **nhưng cũng có nguy cơ mô hình học bối cảnh thu thập dữ liệu** thay vì học đặc trưng hành vi có thể khái quát sang môi trường mới. **Chưa đủ bằng chứng kết luận Data Leakage.**

**Đề xuất:** So sánh MLP khi giữ và bỏ `id.orig_p`, `id.resp_p`; có thể kiểm tra riêng ảnh hưởng của `proto`/`service`. Cần giữ nguyên mọi yếu tố khác để so sánh công bằng. Nếu có mã nhóm hoặc phiên thu thập đáng tin cậy, xem xét cách chia dữ liệu tách nhóm để đánh giá tính khái quát; dataset hiện tại chưa được xác nhận có mã nhóm phù hợp.

## 10. Bảng tổng hợp vấn đề và ưu tiên xử lý

| Ưu tiên | Vấn đề | Bằng chứng chính | Bước nghiên cứu tiếp theo |
|---|---|---|---|
| **Cao** | Trùng lặp, khả năng nhãn mâu thuẫn | 5.195 dòng trùng; 6 nhóm đầu vào giống nhau khác nhãn | Kiểm tra nguồn dữ liệu; quy tắc làm sạch trước chia tập |
| **Cao** | Mất cân bằng lớp | Lớp lớn nhất/nhỏ nhất ~3.380,68:1 | Chiến lược chia tập; Macro-F1; thử cân bằng Train |
| **Cao** | Nguy cơ học đặc điểm thu thập | Một số lớp gần như gắn với một cổng hoặc dịch vụ | Thực nghiệm giữ/bỏ cổng; kiểm tra độ vững |
| **Cao** | Loại ngoại lệ có thể xóa gần hết lớp | ~99,83% `MQTT_Publish` ngoài IQR toàn cục của `flow_duration` | Không lọc ngoại lệ máy móc |
| Trung bình | Phân phối lệch, nhiều số 0 | 65 cột lệch; 16 cột >=95% số 0 | Thử biến đổi và chuẩn hóa có kiểm soát |
| Trung bình | Đặc trưng tương quan cao | 52 cặp Pearson >=0,95 | Thử CorrFilter fit trên Train |
| Trung bình | Cột hằng/cột chỉ số | `bwd_URG_flag_count`, `Unnamed: 0` | Xác định và loại khỏi đầu vào phù hợp |

## 11. Kế hoạch công việc sau EDA

1. **Data Cleaning:** Kiểm tra trùng lặp và nhóm mâu thuẫn nhãn; xác nhận cột chỉ số và cột hằng; ghi nhận số mẫu trước/sau từng bước. Không sửa file `data/raw/RT_IOT2022.csv`.
2. **Splitting:** Xây dựng phương án Train/Validation phù hợp với 12 lớp; bảo đảm mẫu trùng không lọt sang cả hai tập; giữ nguyên quy định **không đụng đến tập Test** trong giai đoạn thực nghiệm.
3. **Baseline MLP:** Chỉ fit encoder/scaler trên Train, transform Validation; đánh giá Macro-F1 và chỉ số theo lớp.
4. **Thực nghiệm có kiểm soát:** Lần lượt thử scaler, `log1p`, CorrFilter, cân bằng lớp, loại cổng; **chỉ thay đổi một yếu tố chính mỗi lần** khi muốn kết luận tác động của yếu tố đó.
5. **Tổng hợp kết quả:** Lưu experiment log, kết quả từng lớp, nhận xét cải thiện/suy giảm và chi phí huấn luyện; chỉ chọn mô hình bằng kết quả Validation.

## 12. Kết luận cuối giai đoạn EDA

Bộ dữ liệu RT_IOT2022 có nhiều đặc điểm có thể ảnh hưởng đáng kể đến chất lượng phân loại bằng MLP: **trùng lặp và nhãn có khả năng mâu thuẫn, mất cân bằng lớp nghiêm trọng, nhiều cột phân phối lệch hoặc có tỷ lệ số 0 cao, quy tắc ngoại lệ IQR không ổn định với dữ liệu tập trung, và tương quan cao giữa các đặc trưng**. Đặc biệt, sự liên hệ mạnh giữa cổng mạng/dịch vụ và nhãn cần được kiểm tra để tránh đánh giá quá lạc quan.
