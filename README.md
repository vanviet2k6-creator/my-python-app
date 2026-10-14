# my-python-app

Ứng dụng máy tính Python cho bài thực hành CI/CD:
GitHub → Jenkins → compile → pytest + coverage → package → SonarQube → Quality Gate → Docker deploy → smoke test.

Ứng dụng sau deploy: http://localhost:8000. API health: `/health`; API tính toán: `POST /api/calculate`.
Hướng dẫn cấu hình và nghiệm thu: [CICD.md](CICD.md).

## Cấu trúc

```
my-python-app/
├── src/myapp/
│   ├── __init__.py
│   └── calculator.py      # lớp xử lý nghiệp vụ
├── tests/
│   ├── __init__.py
│   └── test_calculator.py # unit test
├── requirements.txt
├── setup.py
├── Jenkinsfile
└── README.md
```

## Cách đẩy lên GitHub

1. Tạo repo rỗng trên GitHub (không tick "Add a README").
2. Chạy trong thư mục này:

```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/<username>/<ten-repo>.git
git push -u origin main
```

Khi git hỏi xác thực: dùng username GitHub + dán Personal Access Token (không dùng mật khẩu GitHub thật).

## Chạy thử ở local (tùy chọn, để kiểm tra trước khi build trên Jenkins)

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements-dev.txt
export PYTHONPATH=src
pytest tests/
```

Chạy web cục bộ: đặt `PYTHONPATH=src` và `APP_SECRET_KEY` là khóa ngẫu nhiên, rồi chạy `flask --app myapp.web:create_app run`.
