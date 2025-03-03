# app/Dockerfile

# ベースイメージとして公式のPythonイメージを使用
FROM python:3.9-slim

# 環境変数の設定（Pythonの出力をバッファリングしない）
ENV PYTHONUNBUFFERED=1

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.txt .
# COPY index.html .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt
RUN pip3 install influxdb-client
RUN pip install numpy
# RUN apt install python-is-python3
# RUN apt install python3-pip


# アプリケーションコードをコピー
COPY middleware.py .

# ポートの公開
EXPOSE 3001

# アプリケーションの実行
# CMD ["python", "middleware.py"]
