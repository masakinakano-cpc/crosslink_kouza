# 知識ファイル格納ディレクトリ

このディレクトリには以下の知識ファイルを格納してください：

## 📚 推奨ファイル構成

```
knowledge/
├── safety/                    # 安全関連
│   ├── forklift_safety.txt    # フォークリフト安全
│   ├── chemical_safety.txt    # 化学物質安全
│   ├── ppe_guide.txt          # PPE着用ガイド
│   └── emergency_procedures.txt # 緊急時対応
│
├── quality/                   # 品質管理
│   ├── 5s_activities.txt      # 5S活動
│   ├── kyt_procedures.txt     # KYT手順
│   └── quality_control.txt    # 品質管理
│
├── regulations/               # 法令・規則
│   ├── labor_safety_law.txt   # 労働安全衛生法
│   ├── company_rules.txt      # 社内規則
│   └── industry_standards.txt # 業界基準
│
├── training/                  # 研修資料
│   ├── newcomer_guide.txt     # 新人向けガイド
│   ├── supervisor_manual.txt  # 監督者向けマニュアル
│   └── certification_info.txt # 資格情報
│
└── cultural/                  # 文化・マナー
    ├── workplace_culture.txt  # 職場文化
    ├── communication_style.txt # コミュニケーション
    └── japanese_business.txt   # 日本のビジネスマナー
```

## 📝 ファイル形式

- **テキスト形式** (.txt): プレーンテキスト、最も推奨
- **Markdown形式** (.md): 構造化されたドキュメント
- **PDF形式** (.pdf): 既存文書（要変換）

## 🔍 使用方法

```bash
# 参考資料を指定して生成
python3 main.py --theme "フォークリフト安全" --reference "knowledge/safety/forklift_safety.txt"

# 複数ファイルの場合は結合
cat knowledge/safety/forklift_safety.txt knowledge/safety/ppe_guide.txt > combined_reference.txt
python3 main.py --theme "総合安全" --reference "combined_reference.txt"
```

## ⚡ 自動RAG機能（将来対応）

今後のバージョンでは以下の機能を追加予定：
- ディレクトリ全体の自動検索
- ベクトル検索による関連文書の自動抽出
- 複数ファイルの自動統合