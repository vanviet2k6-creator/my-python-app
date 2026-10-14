# Jenkins + SonarQube + triển khai tự động

Pipeline chạy trên Linux agent có Docker CLI, Compose và curl. Jenkins trong stack `cicd-portal` dùng Docker của máy host. Compile/test/package chạy trong container Python, không cần cài Python vào Jenkins.

## Jenkins

Plugins: Pipeline, Git, SonarQube Scanner, JUnit, Timestamper, Stage View.
Tool `sonar-scanner`; server `SonarQube` dùng URL `http://sonarqube:9000`, credential Secret text `sonar-token`.
Job Pipeline from SCM dùng repo GitHub này, branch cần triển khai và Script Path `Jenkinsfile`. Repo public không cần credential Git; repo private cần tài khoản/token có quyền đọc repo.

## SonarQube

Project key `my-python-app`. Báo cáo coverage: `reports/coverage.xml`; báo cáo test: `reports/junit.xml`.
Quality Gate được cấu hình trên SonarQube: coverage toàn bộ ít nhất 80%, reliability và security rating A, không có issue mới. Pipeline chỉ đi tiếp khi Gate trả `OK`; thiếu báo cáo hoặc test lỗi đều dừng.
Webhook: `http://jenkins:8080/sonarqube-webhook/` (có dấu `/` cuối).

## Luồng thực thi

1. Checkout sạch từ GitHub, tạo phiên bản image `<commit>-<build-number>`.
2. Build test image và compile mã Python.
3. Chạy pytest; sinh báo cáo JUnit và coverage XML; đóng gói wheel/sdist khi test đạt.
4. Lưu báo cáo và package trong trang build.
5. Quét SonarQube, chờ kết quả Quality Gate tối đa 5 phút.
6. Nếu `DEPLOY=true`, build runtime image rồi deploy đúng tag đó, không rebuild/pull ở bước deploy.
7. Compose chờ container healthy. Smoke test yêu cầu `/health` trả HTTP 200 và API cộng 2 + 3 trả 5.

Poll SCM `H/2 * * * *` tự kiểm tra commit mới khoảng mỗi 2 phút, có hiệu lực sau build đầu tiên. Máy chạy Jenkins cần đang bật và có Internet; GitHub không cần truy cập được vào localhost của máy. Job chỉ theo dõi branch đã cấu hình trong SCM.

## Ứng dụng và deploy

Thư viện `Calculator` được giữ nguyên. Flask bổ sung giao diện và API; Gunicorn chạy ứng dụng trong container với user không phải root. Runtime image không có pytest hay build tool. Port mặc định 8000; chỉnh `APP_PORT` trong Jenkinsfile khi cần.

Chạy Docker thủ công:

```bash
APP_VERSION=local docker compose build web
APP_VERSION=local docker compose up -d --no-build --wait web
```

Kiểm tra tại http://localhost:8000 và http://localhost:8000/health. Pipeline chưa tự rollback nếu lỗi xuất hiện sau deploy; xem stage Deploy/Smoke test và log container để xử lý.

## Nghiệm thu

- Build bình thường: test đạt, báo cáo coverage được nhập vào SonarQube, Gate `OK`, container healthy, giao diện/API chạy.
- Test thất bại: pipeline dừng trước SonarQube/build runtime/deploy; phiên bản đang chạy giữ nguyên.
- Gate thất bại: runtime build/deploy/smoke test bị bỏ qua; phiên bản đang chạy giữ nguyên.
- Commit mới vào branch đang theo dõi: Poll SCM tự kích hoạt build và triển khai nếu mọi kiểm tra đạt.

Tham khảo: [SonarQube Python coverage](https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/test-coverage/python-test-coverage), [Jenkins Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/).
