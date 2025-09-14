#!/usr/bin/env python3
"""
実際のLLM接続を行うスクリプト
llm_generator.pyの_call_llmメソッドを置き換えます
"""

import requests
import json
import os

def create_ollama_version():
    """ollama版の_call_llmメソッドを生成"""
    ollama_code = '''    def _call_llm(self, prompt: str) -> str:
        """ollama（ローカルAI）を呼び出し"""
        try:
            response = requests.post("http://localhost:11434/api/generate", json={
                "model": self.config.model_name,
                "prompt": prompt,
                "temperature": self.config.temperature,
                "stream": False
            }, timeout=120)
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                raise Exception(f"ollama APIエラー: {response.status_code}")
                
        except Exception as e:
            print(f"LLM呼び出しエラー: {e}")
            # エラー時はデモ用レスポンスにフォールバック
            return self._demo_response()'''
    
    return ollama_code

def create_openai_version():
    """OpenAI版の_call_llmメソッドを生成"""
    openai_code = '''    def _call_llm(self, prompt: str) -> str:
        """OpenAI APIを呼び出し"""
        try:
            import openai
            client = openai.OpenAI()
            
            response = client.chat.completions.create(
                model=self.config.model_name or "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"LLM呼び出しエラー: {e}")
            # エラー時はデモ用レスポンスにフォールバック
            return self._demo_response()'''
    
    return openai_code

def backup_original():
    """元のファイルをバックアップ"""
    import shutil
    shutil.copy("llm_generator.py", "llm_generator.py.backup")
    print("✅ 元のファイルをバックアップしました: llm_generator.py.backup")

def replace_llm_method(method_type="ollama"):
    """_call_llmメソッドを実際のLLM呼び出しに置き換え"""
    
    # バックアップ作成
    backup_original()
    
    # ファイル読み込み
    with open("llm_generator.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 置き換えるコードを選択
    if method_type == "ollama":
        new_method = create_ollama_version()
        import_line = "import requests"
    elif method_type == "openai":
        new_method = create_openai_version()
        import_line = "import openai"
    else:
        print("❌ 未対応のmethod_type")
        return False
    
    # importの追加
    if import_line not in content:
        content = content.replace("import os", f"import os\n{import_line}")
    
    # デモ用_call_llmメソッドを探して置き換え
    start_marker = '    def _call_llm(self, prompt: str) -> str:'
    end_marker = '        return self._demo_response()'
    
    start_pos = content.find(start_marker)
    if start_pos == -1:
        print("❌ _call_llmメソッドが見つかりません")
        return False
    
    # end_markerの次の行までを見つける
    end_pos = content.find(end_marker, start_pos)
    if end_pos == -1:
        print("❌ メソッドの終了位置が見つかりません")
        return False
    
    end_pos = content.find('\n', end_pos) + 1
    
    # 置き換え実行
    new_content = content[:start_pos] + new_method + content[end_pos:]
    
    # ファイル保存
    with open("llm_generator.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"✅ {method_type}版のLLM呼び出しに置き換えました")
    return True

def test_connection(method_type="ollama"):
    """接続テスト"""
    if method_type == "ollama":
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ ollama接続確認")
                return True
            else:
                print("❌ ollama接続失敗")
                return False
        except:
            print("❌ ollamaが起動していません")
            return False
            
    elif method_type == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print("✅ OpenAI APIキー確認")
            return True
        else:
            print("❌ OPENAI_API_KEYが設定されていません")
            return False

def main():
    """メイン処理"""
    print("=== LLM接続セットアップ ===")
    print("1. ollama（ローカルAI、無料）")
    print("2. OpenAI（ChatGPT、有料）")
    print("3. キャンセル")
    
    choice = input("選択してください (1-3): ").strip()
    
    if choice == "1":
        method = "ollama"
        print("\nollamaセットアップを選択")
        if not test_connection("ollama"):
            print("⚠️  ollamaが起動していません")
            print("セットアップ手順:")
            print("1. https://ollama.ai からollamaをインストール")
            print("2. ollama pull qwen2.5:7b")
            print("3. ollama serve")
            print("4. 再度このスクリプトを実行")
            return
            
    elif choice == "2":
        method = "openai"
        print("\nOpenAI APIセットアップを選択")
        if not test_connection("openai"):
            print("⚠️  OpenAI APIキーが設定されていません")
            print("セットアップ手順:")
            print("1. https://platform.openai.com でAPIキー取得")
            print("2. export OPENAI_API_KEY='your-api-key'")
            print("3. pip install openai")
            print("4. 再度このスクリプトを実行")
            return
    else:
        print("キャンセルしました")
        return
    
    # 実際の置き換え実行
    if replace_llm_method(method):
        print(f"\n🎉 {method}版への接続完了!")
        print("\n次のステップ:")
        print("python3 main.py --demo  # テスト実行")
        print("python3 main.py --theme '安全教育'  # 実際の生成")

if __name__ == "__main__":
    main()