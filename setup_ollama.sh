#!/bin/bash
# ollama自動セットアップスクリプト

echo "=== ollama自動セットアップ ==="

# 1. ollamaのインストール確認
if command -v ollama >/dev/null 2>&1; then
    echo "✅ ollama は既にインストールされています"
else
    echo "📦 ollamaをインストール中..."
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if [ $? -eq 0 ]; then
        echo "✅ ollamaインストール完了"
    else
        echo "❌ ollamaインストールに失敗しました"
        exit 1
    fi
fi

# 2. ollama起動
echo "🚀 ollama起動中..."
ollama serve &
OLLAMA_PID=$!
sleep 3

# 3. 軽量モデルのダウンロード
echo "📥 軽量モデル（qwen2.5:7b）ダウンロード中..."
ollama pull qwen2.5:7b

if [ $? -eq 0 ]; then
    echo "✅ モデルダウンロード完了"
else
    echo "❌ モデルダウンロードに失敗しました"
fi

# 4. 接続テスト
echo "🔍 接続テスト中..."
sleep 2

cd "/Users/apple/Desktop/クロスラーニング講座作成自作LLM"
python3 -c "
import requests
try:
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    if response.status_code == 200:
        print('✅ ollama接続成功!')
    else:
        print('❌ ollama接続失敗')
except:
    print('❌ ollama起動を待機中...')
"

echo ""
echo "🎉 セットアップ完了!"
echo ""
echo "📋 テスト実行コマンド:"
echo "python3 main.py --theme 'フォークリフト安全' --model 'qwen2.5:7b'"
echo ""
echo "🛑 ollama停止コマンド:"
echo "kill $OLLAMA_PID"