# my-python-app

Project mẫu phục vụ bài thực hành Jenkins Pipeline (Checkout → Compile → Unit Test → Package).

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
pip install -r requirements.txt
export PYTHONPATH=src
pytest tests/
```
