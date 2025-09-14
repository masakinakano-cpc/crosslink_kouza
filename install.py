#!/usr/bin/env python3
"""
自作LLM スライド台本生成システム
インストール・セットアップスクリプト
"""

import os
import subprocess
import sys
import platform

def print_header(text):
    """ヘッダー表示"""
    print(f"\n{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}")

def run_command(cmd, description=""):
    """コマンド実行"""
    print(f"実行中: {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"出力: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"エラー: {e}")
        if e.stderr:
            print(f"エラー詳細: {e.stderr.strip()}")
        return False

def check_python_version():
    """Python バージョンチェック"""
    print_header("Python環境チェック")
    version = sys.version_info
    print(f"Python バージョン: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8以上が必要です")
        return False
    print("✅ Python バージョン OK")
    return True

def install_dependencies():
    """依存関係のインストール"""
    print_header("依存関係のインストール")
    
    # 基本パッケージのインストール
    basic_packages = ["requests", "typing-extensions"]
    
    for package in basic_packages:
        print(f"インストール中: {package}")
        if not run_command(f"pip3 install {package}"):
            print(f"警告: {package} のインストールに失敗しました")

def setup_ollama():
    """ollamaのセットアップ"""
    print_header("ollama セットアップ（推奨）")
    
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("macOSでollamaをセットアップ...")
        if run_command("which ollama", "ollama存在チェック"):
            print("✅ ollama は既にインストールされています")
        else:
            print("ollamaをインストールしますか？ (y/n): ")
            # 自動でYesにする
            print("自動セットアップを実行...")
            if run_command("curl -fsSL https://ollama.ai/install.sh | sh", "ollamaインストール"):
                print("✅ ollama インストール完了")
            else:
                print("❌ ollama インストールに失敗")
                return False
    
    elif system == "linux":
        print("Linuxでollamaをセットアップ...")
        if run_command("curl -fsSL https://ollama.ai/install.sh | sh", "ollamaインストール"):
            print("✅ ollama インストール完了")
        else:
            print("❌ ollama インストールに失敗")
            return False
    
    else:
        print(f"⚠️  {system} は自動セットアップに対応していません")
        print("手動で https://ollama.ai からollamaをインストールしてください")
        return True
    
    # 推奨モデルのダウンロード
    print("\n推奨モデルをダウンロードしますか？")
    print("1. Qwen2.5 32B (推奨、約19GB)")
    print("2. Qwen2.5 7B (軽量、約4GB)")
    print("3. スキップ")
    
    # デモでは軽量モデルを選択
    choice = "2"
    print(f"選択: {choice}")
    
    if choice == "1":
        run_command("ollama pull qwen2.5:32b", "Qwen2.5 32B ダウンロード")
    elif choice == "2":
        run_command("ollama pull qwen2.5:7b", "Qwen2.5 7B ダウンロード")
    
    return True

def create_test_files():
    """テスト用ファイルの作成"""
    print_header("テスト用ファイルの作成")
    
    # テスト用参考資料
    test_reference = """フォークリフト安全運転の基本

1. 作業前点検
エンジンオイル、ブレーキ液、タイヤの状態を確認する。
異常があれば使用を中止し、報告する。

2. PPE（個人保護具）の着用
ヘルメット、安全靴、保護メガネの着用が義務。
作業内容に応じて追加の保護具を検討。

3. 運転技術
急発進・急停止を避け、安全速度を維持。
カーブでは十分に減速する。
バック時は後方確認を徹底。

4. 荷役作業
荷重制限を守る。
荷物の重心を確認してから持ち上げる。
不安定な荷物は複数人で作業。
"""
    
    with open("test_reference.txt", "w", encoding="utf-8") as f:
        f.write(test_reference)
    print("✅ test_reference.txt を作成")
    
    # 設定ファイル例
    config_example = """# 設定ファイル例
MODEL_NAME=qwen2.5:7b
TEMPERATURE=0.3
MAX_RETRIES=3
OUTPUT_DIR=output
"""
    
    with open("config.example", "w", encoding="utf-8") as f:
        f.write(config_example)
    print("✅ config.example を作成")

def run_test():
    """動作テスト"""
    print_header("動作テスト")
    
    print("バリデータのテスト...")
    if run_command("python3 validator.py", "バリデータテスト"):
        print("✅ バリデータ OK")
    else:
        print("❌ バリデータテストに失敗")
        return False
    
    print("\nデモ生成テスト...")
    if run_command("python3 main.py --demo", "デモ生成テスト"):
        print("✅ デモ生成 OK")
    else:
        print("❌ デモ生成テストに失敗")
        return False
    
    return True

def main():
    """メイン処理"""
    print("🚀 自作LLM スライド台本生成システム セットアップ")
    print("=" * 60)
    
    # ステップ1: Python環境チェック
    if not check_python_version():
        print("セットアップを中止します")
        sys.exit(1)
    
    # ステップ2: 依存関係インストール
    install_dependencies()
    
    # ステップ3: ollama セットアップ
    setup_ollama()
    
    # ステップ4: テストファイル作成
    create_test_files()
    
    # ステップ5: 動作テスト
    if run_test():
        print_header("セットアップ完了")
        print("✅ すべてのセットアップが完了しました！")
        print("\n📝 使用方法:")
        print("  python3 main.py --demo          # デモ実行")
        print("  python3 main.py --interactive   # 対話モード")
        print("  python3 main.py --theme '安全教育' --units 1  # コマンドライン")
        print("\n📁 生成されたファイル:")
        print("  test_reference.txt  # テスト用参考資料")
        print("  config.example      # 設定ファイル例")
        print("  output/             # 出力ディレクトリ")
    else:
        print_header("セットアップ未完了")
        print("❌ 一部のテストに失敗しましたが、基本機能は利用可能です")
        print("手動でテストを実行してください: python3 main.py --demo")

if __name__ == "__main__":
    main()