# 自作LLM スライド台本生成システム

日本で働く外国人向けの講座スライド台本を、定型フォーマット（人間用/Excel用）で高再現に生成するPythonシステムです。

## 🎯 特徴

- **安定した出力形式**: システムプロンプトによる厳格な形式制御
- **構造バリデータ**: 生成後の自動品質チェック
- **用語統一**: 安全用語辞書による専門用語の統一
- **Few-shot学習**: 良い例・悪い例による出力品質向上
- **リトライ機能**: バリデート失敗時の自動修正

## 📁 ファイル構成

```
├── main.py                 # メインスクリプト
├── llm_generator.py        # LLM生成システム
├── validator.py            # 構造バリデータ
├── system_rules_ja.txt     # システムプロンプト（不変ルール）
├── safety_dict.txt         # 安全用語辞書
├── fewshot_samples.txt     # Few-shot学習サンプル
├── requirements.txt        # 依存関係
└── README.md              # このファイル
```

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. LLMモデルの設定

以下のいずれかを選択:

#### A) ollama（推奨・ローカル）
```bash
# ollamaをインストール
curl -fsSL https://ollama.ai/install.sh | sh

# 推奨モデルをダウンロード
ollama pull qwen2.5:32b
```

#### B) OpenAI API
```bash
pip install openai
export OPENAI_API_KEY="your-api-key"
```

#### C) Hugging Face Transformers
```bash
pip install torch transformers accelerate bitsandbytes
```

## 💡 使用方法

### 基本コマンド

```bash
# 基本使用
python main.py --theme "フォークリフト安全" --units 1

# 参考資料付き
python main.py --theme "5S基本" --units 1 --reference "reference.txt"

# モデル指定
python main.py --theme "化学物質取扱" --model "qwen2.5:72b"
```

### 対話モード

```bash
python main.py --interactive
```

### デモモード

```bash
python main.py --demo
```

### バリデートのみ

```bash
python main.py --validate-only "output/slide_human.txt"
```

## 📊 出力フォーマット

### 人間用スライド
```
1. 表紙
フォークリフト安全入門
現場で今日から使える基本
小まとめ：今日の目標を1つ決める

2. ユニット表紙
第1ユニット：基本操作とKYT
安全な作業のために

3. 導入
フォークリフトは便利な機械
でも危険もたくさん
どんな危険があるでしょうか？
```

### Excel用フォーマット
```
1 : 1 : フォークリフト安全入門 : 
1 : 2 : 現場で今日から使える基本 : 
1 : 3 : 小まとめ：今日の目標を1つ決める : 
2 : 1 : 第1ユニット：基本操作とKYT : 
2 : 2 : 安全な作業のために : 
```

## 🔧 カスタマイズ

### 1. LLMバックエンドの変更

`llm_generator.py` の `_call_llm` メソッドを修正:

```python
# ollama使用例
import requests
response = requests.post("http://localhost:11434/api/generate", json={
    "model": self.config.model_name,
    "prompt": prompt,
    "temperature": self.config.temperature,
    "stream": False
})
return response.json()["response"]
```

### 2. 用語辞書の追加

`safety_dict.txt` に新しい用語を追加:

```
新用語: 説明
- 使用例：具体的な使用方法
```

### 3. バリデートルールの調整

`validator.py` の各チェック関数を修正して、独自のバリデートルールを追加できます。

## 📈 推奨モデル

1. **Qwen2.5 32B/72B** - 日本語性能と長文整形が安定
2. **Llama 3.1 70B** - 高い日本語理解力
3. **Mixtral 8×22B** - バランスの取れた性能

## 🛠️ トラブルシューティング

### よくある問題

**Q: 生成が止まらない**
```bash
# タイムアウト設定を調整
config.max_tokens = 2000
```

**Q: バリデートエラーが多い**
- `fewshot_samples.txt` に良い例を追加
- `system_rules_ja.txt` のルールを調整

**Q: 用語が統一されない**
- `safety_dict.txt` に該当用語を追加
- システムプロンプトで用語優先度を強調

## 📝 ライセンス

MIT License - 自由に改変・商用利用可能

## 🤝 コントリビューション

Issue報告やPull Requestを歓迎します。

## 📞 サポート

問題が発生した場合は、以下の情報を含めてIssueを作成してください:
- 使用したコマンド
- エラーメッセージ
- 使用したモデル名
- 入力データのサンプル