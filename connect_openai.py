#!/usr/bin/env python3
"""
OpenAI API（ChatGPT）接続用のサンプルコード
"""

import os
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

def test_openai_connection():
    """OpenAI APIの接続テスト"""
    if not OPENAI_AVAILABLE:
        print("❌ openaiライブラリがインストールされていません")
        print("インストール方法: pip install openai")
        return False
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEYが設定されていません")
        print("設定方法: export OPENAI_API_KEY='your-api-key'")
        return False
    
    try:
        client = openai.OpenAI(api_key=api_key)
        # 簡単なテストリクエスト
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✅ OpenAI API接続成功!")
        return True
    except Exception as e:
        print(f"❌ OpenAI API接続失敗: {e}")
        return False

def call_openai(prompt, model="gpt-3.5-turbo"):
    """OpenAI APIでテキスト生成"""
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "あなたは日本語で回答する安全教育の専門家です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"生成エラー: {e}"

if __name__ == "__main__":
    print("=== OpenAI API接続テスト ===")
    
    if test_openai_connection():
        print("\n=== テスト生成 ===")
        test_prompt = "フォークリフト安全について3行で説明してください。"
        result = call_openai(test_prompt)
        print("生成結果:")
        print(result)
    else:
        print("\n📋 OpenAI APIセットアップ手順:")
        print("1. https://platform.openai.com でアカウント作成")
        print("2. APIキーを取得")
        print("3. pip install openai")
        print("4. export OPENAI_API_KEY='your-api-key'")
        print("5. python3 connect_openai.py  # 再テスト")