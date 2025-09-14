#!/usr/bin/env python3
"""
ollama（ローカルAI）接続用のサンプルコード
"""

import requests
import json

def test_ollama_connection():
    """ollamaの接続テスト"""
    try:
        # ollamaが起動しているかチェック
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ ollama接続成功!")
            print("利用可能なモデル:")
            for model in models.get('models', []):
                print(f"  - {model['name']}")
            return True
        else:
            print("❌ ollama接続失敗")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ ollamaが起動していません")
        print("起動方法: ollama serve")
        return False

def call_ollama(prompt, model="qwen2.5:7b"):
    """ollamaでテキスト生成"""
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": model,
            "prompt": prompt,
            "temperature": 0.3,
            "stream": False
        }, timeout=60)
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"エラー: {response.status_code}"
            
    except Exception as e:
        return f"接続エラー: {e}"

if __name__ == "__main__":
    print("=== ollama接続テスト ===")
    
    if test_ollama_connection():
        print("\n=== テスト生成 ===")
        test_prompt = "フォークリフト安全について3行で説明してください。"
        result = call_ollama(test_prompt)
        print("生成結果:")
        print(result)
    else:
        print("\n📋 ollamaセットアップ手順:")
        print("1. https://ollama.ai からollamaをインストール")
        print("2. ollama pull qwen2.5:7b  # モデルダウンロード")
        print("3. ollama serve  # サーバー起動")
        print("4. python3 connect_ollama.py  # 再テスト")