---
name: Simulator Build Strategy
overview: Lộ trình xây simulator 4 ngã tư theo từng mốc nhỏ, chỉ tập trung module mô phỏng (không build controller trung tâm), ưu tiên dễ test và mở rộng.
todos:
  - id: freeze-architecture
    content: Chốt cấu trúc module simulator (entities/engine/scenarios) và chuẩn hóa SimulationState + update phases.
    status: pending
  - id: build-core-traffic
    content: Triển khai lần lượt multi-vehicle, car-following, queue at lights, route-turning, lane-change safety.
    status: pending
  - id: add-intersection-safety
    content: Thêm conflict-point arbitration trong giao lộ và cơ chế tránh deadlock cơ bản.
    status: pending
  - id: integrate-divider
    content: Tích hợp dynamic divider lane_shift theo transition an toàn, không gây collision.
    status: pending
  - id: instrument-and-validate
    content: Bổ sung metrics/replay/headless tests và stress test để xác thực hiệu năng + ổn định.
    status: pending
isProject: false
---

# Chiến lược build simulator theo từng bước

## Mục tiêu
Xây `simulator` ổn định cho 4 ngã tư, nhiều xe, tuân thủ đèn, tránh va chạm, chuyển làn/rẽ, và giữ kiến trúc dễ test theo từng module độc lập.

## Nguyên tắc triển khai
- Đi từ **deterministic trước** (kịch bản cố định, seed cố định), rồi mới thêm ngẫu nhiên.
- Mỗi bước chỉ thêm **1 năng lực lớn** và có **test/metrics rõ ràng**.
- Tách 3 lớp: `world model` (trạng thái), `behavior` (quy tắc lái), `render` (hiển thị).
- Giữ `SimulationController` chỉ làm điều phối, không nhồi hết logic hành vi.

## Kiến trúc đề xuất (bám đặc tả hiện có)
- [main.py](/Users/mac/Documents/Documents/Nam3/Ki2/iOt/4ngatu/main.py): chỉ bootstrapping và main loop.
- `simulation/entities/`: `Vehicle`, `TrafficLight/Intersection`, `Road/DynamicDivider`.
- `simulation/engine/` (mới):
  - `spawner.py`: sinh xe theo lane, route, spawn policy.
  - `routing.py`: chọn hướng đi thẳng/rẽ trái/rẽ phải theo xác suất.
  - `car_following.py`: giữ khoảng cách, phanh mượt.
  - `lane_change.py`: điều kiện đổi làn + kiểm tra an toàn.
  - `intersection_rules.py`: stop line, right-of-way, conflict points.
  - `metrics.py`: throughput, wait time, queue length, collision count.
- `simulation/scenarios/` (mới): profile lưu lượng để replay/test.

## Lộ trình 8 mốc (MVP -> nâng cao)
1. **Mốc 0 - Refactor nền tảng**
   - Chuẩn hóa update loop theo pha: `sense -> decide -> act -> cleanup`.
   - Tạo `SimulationState` gom danh sách xe, lane occupancy, đèn, thời gian mô phỏng.
   - Thêm `seed` trong config để replay cùng kết quả.

2. **Mốc 1 - Multi-vehicle an toàn cùng làn**
   - Bật spawn nhiều xe/làn, có `headway` tối thiểu khi spawn.
   - Car-following đơn giản (IDM rút gọn hoặc gap-speed rule).
   - Tiêu chí pass: 0 va chạm khi chạy 10 phút giả lập lưu lượng thấp-vừa.

3. **Mốc 2 - Hàng chờ đèn đỏ chuẩn**
   - Xe dừng đúng stop-line, xả hàng chờ khi xanh, không xuyên đuôi xe.
   - Có trạng thái xe: `CRUISE`, `BRAKE_FOR_LIGHT`, `QUEUED`, `ACCELERATE`.
   - Tiêu chí pass: queue length tăng/giảm hợp lý theo pha đèn.

4. **Mốc 3 - Route và rẽ tại ngã tư**
   - Gán `route plan` cho từng xe (thẳng/trái/phải), quyết định tại điểm vào nút.
   - Tách lane hợp lệ theo hướng rẽ (ví dụ làn trong cho trái, làn ngoài cho phải).
   - Tiêu chí pass: không rẽ từ lane sai luật đã khai báo.

5. **Mốc 4 - Lane change trên đoạn thẳng**
   - Điều kiện đổi làn: lane hiện tại tắc hơn, lane đích hợp lệ cho route, đủ gap trước/sau.
   - Có cooldown đổi làn để tránh zig-zag.
   - Tiêu chí pass: giảm thời gian chờ trung bình so với không đổi làn.

6. **Mốc 5 - Conflict handling trong giao lộ**
   - Mô hình conflict points trong hộp giao lộ, cấp quyền vào nút theo thứ tự an toàn.
   - Chặn deadlock cơ bản bằng timeout + ưu tiên vòng.
   - Tiêu chí pass: 0 collision trong nút ở lưu lượng vừa-cao.

7. **Mốc 6 - Dynamic divider integration (chỉ phía simulator)**
   - Áp dụng lệnh `lane_shift` vào lane availability theo thời gian chuyển tiếp.
   - Xe đang chạy không bị “teleport”; chỉ chặn spawn/đi vào lane bị đóng.
   - Tiêu chí pass: chuyển tỉ lệ 2:2 -> 3:1 không phát sinh collision.

8. **Mốc 7 - Metrics + replay + stress test**
   - Log CSV/JSON cho: throughput, avg wait, max queue, near-miss.
   - Replay scenario cố định để regression test.
   - Tiêu chí pass: FPS >= 60, không memory leak trong chạy dài.

## Bộ test tối thiểu theo từng mốc
- Unit test:
  - `car_following`: khoảng cách không âm, không vượt xe trước trong cùng lane.
  - `lane_change`: chỉ đổi khi gap đạt ngưỡng.
  - `intersection_rules`: red -> stop, green -> proceed theo route hợp lệ.
- Integration test (headless):
  - 4 ngã tư, lưu lượng profile thấp/vừa/cao.
  - assert `collision_count == 0` với profile thấp/vừa.
- Visual debug overlay:
  - Vẽ bounding box, lane id, state xe, queue index, conflict point occupancy.

## Prompt mẫu để build từng bước (copy dùng ngay)

### Prompt 1 - Refactor loop + state
"Trong project Pygame simulator 4 ngã tư, hãy refactor vòng lặp thành các pha `sense -> decide -> act -> cleanup`, tạo class `SimulationState` chứa vehicles, lights, roads, sim_time, rng_seed. Không đổi behavior hiện tại. Viết code rõ ràng, thêm type hints, và thêm 2 test cơ bản cho state update." 

### Prompt 2 - Multi-vehicle + car-following
"Hãy thêm khả năng spawn nhiều xe trên mỗi lane với khoảng cách spawn tối thiểu. Implement car-following đơn giản để xe không đâm nhau trong cùng lane. Không xử lý lane change ở bước này. Thêm test chứng minh 2000 steps không có collision cùng lane." 

### Prompt 3 - Stop-line & queue
"Implement logic dừng trước đèn đỏ/vàng tại stop line, hình thành hàng chờ và xả hàng khi đèn xanh. Thêm state machine cho Vehicle (`CRUISE`, `BRAKE_FOR_LIGHT`, `QUEUED`, `ACCELERATE`). Viết test cho 1 lane có 5 xe và chu kỳ đèn." 

### Prompt 4 - Route + turning
"Thêm route planning cho mỗi xe (thẳng/trái/phải theo tỷ lệ cấu hình), enforce lane hợp lệ theo hướng rẽ trước khi vào ngã tư. Không thêm lane change tự do ngoài đoạn chuẩn bị rẽ. Viết test để đảm bảo xe không rẽ sai lane." 

### Prompt 5 - Lane change safety
"Thêm lane-change model với điều kiện: lane đích hợp lệ cho route, đủ gap trước/sau, có cooldown đổi làn. Ghi lại số lần đổi làn và từ chối đổi làn do không an toàn. Thêm test cho các điều kiện chấp nhận/từ chối." 

### Prompt 6 - Conflict points
"Mô hình hóa conflict points trong hộp giao lộ để tránh va chạm giữa các hướng rẽ/cắt nhau. Xe chỉ vào nút khi conflict points cần thiết đang rảnh. Thêm deadlock prevention đơn giản. Viết integration test low/medium traffic." 

### Prompt 7 - Dynamic divider
"Tích hợp lệnh `lane_shift` vào simulator: cập nhật lane availability theo ratio mới (ví dụ 3:1), có transition an toàn, không ảnh hưởng xe đã ở lane đóng ngoài việc không cho xe mới vào. Thêm test chuyển tỷ lệ nhiều lần." 

### Prompt 8 - Metrics + replay
"Thêm metrics logger (throughput, average_wait_time, max_queue_length, collision_count, near_miss_count) và replay mode theo seed/scenario file. Xuất CSV mỗi 1s mô phỏng. Thêm script stress test 10 phút giả lập." 

## Definition of Done cho simulator
- Nhiều xe chạy ổn định, tuân thủ đèn, không đâm nhau ở profile thấp-vừa.
- Có rẽ + đổi làn an toàn theo quy tắc cấu hình.
- Hỗ trợ `traffic_light` và `lane_shift` từ network listener.
- Có replay + metrics để debug và benchmark tiến độ.
- Giữ FPS mục tiêu theo cấu hình (ưu tiên >=60).