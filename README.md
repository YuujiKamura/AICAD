# AICAD - AI支援CADアプリケーション

このプロジェクトは、Pythonで実装されたAI支援CAD（Computer-Aided Design）アプリケーションです。
TkinterベースのGUIを使用して、簡単な図形描画から高度な設計作業までサポートします。

## 主な機能

- 基本図形の描画（線、四角形、円、多角形）
- スナップ機能（端点、中点、交点）
- 寸法線表示
- アンドゥ/リドゥ機能
- PDFエディタ機能

## 必要条件

- Python 3.8以上
- tkinter
- その他の依存パッケージ（requirements.txtを参照）

## インストール方法

1. リポジトリをクローン:
```bash
git clone https://github.com/YuujiKamura/AICAD.git
cd AICAD
```

2. 仮想環境を作成し、有効化:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. 依存パッケージをインストール:
```bash
pip install -r requirements.txt
```

## 使用方法

アプリケーションを起動:
```bash
python app.py
```

## テスト

テストを実行:
```bash
pytest
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。 