#!/usr/bin/env python3
"""
自作LLM スライド台本生成システム
メインスクリプト
"""

import argparse
import sys
import os
from typing import Optional
from llm_generator import LLMSlideGenerator, GenerationConfig
from validator import SlideValidator

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(
        description="日本で働く外国人向け講座スライド台本生成システム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python main.py --theme "フォークリフト安全" --units 1
  python main.py --theme "5S基本" --units 1 --reference "参考資料.txt"
  python main.py --interactive
  python main.py --demo
        """
    )
    
    parser.add_argument("--theme", type=str, help="講座のテーマ")
    parser.add_argument("--units", type=int, default=1, help="ユニット数（デフォルト: 1）")
    parser.add_argument("--reference", type=str, help="参考資料ファイルパス")
    parser.add_argument("--model", type=str, default="qwen2.5:32b", 
                       help="使用するLLMモデル名（デフォルト: qwen2.5:32b）")
    parser.add_argument("--temperature", type=float, default=0.3,
                       help="生成温度（0.0-1.0、デフォルト: 0.3）")
    parser.add_argument("--output", type=str, default="output",
                       help="出力ディレクトリ（デフォルト: output）")
    parser.add_argument("--interactive", action="store_true",
                       help="対話モードで実行")
    parser.add_argument("--demo", action="store_true",
                       help="デモモードで実行（固定サンプル）")
    parser.add_argument("--validate-only", type=str,
                       help="指定したファイルをバリデートのみ実行")
    
    args = parser.parse_args()
    
    # バリデートのみモード
    if args.validate_only:
        validate_file(args.validate_only)
        return
    
    # デモモード
    if args.demo:
        run_demo()
        return
    
    # 対話モード
    if args.interactive:
        run_interactive()
        return
    
    # コマンドライン引数モード
    if not args.theme:
        print("エラー: --theme が必要です")
        parser.print_help()
        sys.exit(1)
    
    run_generation(
        theme=args.theme,
        units=args.units,
        reference_file=args.reference,
        model_name=args.model,
        temperature=args.temperature,
        output_dir=args.output
    )

def run_generation(theme: str, units: int, reference_file: Optional[str] = None,
                   model_name: str = "qwen2.5:32b", temperature: float = 0.3,
                   output_dir: str = "output") -> None:
    """スライド生成を実行"""
    
    # 参考資料の読み込み
    reference_text = ""
    if reference_file and os.path.exists(reference_file):
        try:
            with open(reference_file, "r", encoding="utf-8") as f:
                reference_text = f.read()
            print(f"参考資料を読み込み: {reference_file}")
        except Exception as e:
            print(f"警告: 参考資料の読み込みに失敗: {e}")
    
    # 入力フォーマット構築
    user_input = f"""【テーマ】{theme}
【ユニット数】{units}
【参考資料】{reference_text if reference_text else '指定なし'}
【出力】人間用→Excel用の順。比較スライドは日本×自国。
【注意】不足は『要確認』と明示。用語は内蔵辞書を優先。"""
    
    # 設定とジェネレータ初期化
    config = GenerationConfig(
        model_name=model_name,
        temperature=temperature,
        max_retries=3
    )
    
    generator = LLMSlideGenerator(config)
    
    print("=== スライド生成開始 ===")
    print(f"テーマ: {theme}")
    print(f"ユニット数: {units}")
    print(f"モデル: {model_name}")
    print(f"温度: {temperature}")
    print()
    
    try:
        # 生成実行
        human_output, excel_output, stats = generator.generate_slides(
            user_input, reference_text
        )
        
        # 結果表示
        print("=== 生成完了 ===")
        print(f"試行回数: {stats.get('attempt', 'N/A')}")
        print(f"バリデート: {'✅ 合格' if stats.get('validation_passed') else '❌ 不合格'}")
        
        if stats.get('validation_passed'):
            # ファイル保存
            file_paths = generator.save_output(human_output, excel_output, output_dir)
            print(f"\n📁 保存先:")
            print(f"  人間用: {file_paths['human_file']}")
            print(f"  Excel用: {file_paths['excel_file']}")
            
            # 統計表示
            print(f"\n📊 統計:")
            human_lines = len(human_output.split('\n'))
            excel_lines = len(excel_output.split('\n'))
            print(f"  人間用行数: {human_lines}")
            print(f"  Excel行数: {excel_lines}")
            
            print(f"\n✅ 生成成功!")
            
        else:
            print(f"\n❌ エラー:")
            for error in stats.get('final_errors', []):
                print(f"  - {error}")
            
    except Exception as e:
        print(f"❌ 生成エラー: {e}")
        sys.exit(1)

def run_interactive():
    """対話モードの実行"""
    print("=== 対話モード ===")
    print("スライド台本生成システムへようこそ！")
    print()
    
    # テーマ入力
    theme = input("📝 テーマを入力してください: ").strip()
    if not theme:
        print("テーマが入力されませんでした。終了します。")
        return
    
    # ユニット数入力
    try:
        units = int(input("📊 ユニット数を入力してください（デフォルト: 1）: ") or "1")
    except ValueError:
        print("無効な数値です。デフォルト値1を使用します。")
        units = 1
    
    # 参考資料ファイル
    ref_file = input("📄 参考資料ファイルパス（オプション）: ").strip()
    if ref_file and not os.path.exists(ref_file):
        print(f"警告: ファイル '{ref_file}' が見つかりません。参考資料なしで続行します。")
        ref_file = None
    
    # モデル選択
    print("\n🤖 利用可能なモデル:")
    models = ["qwen2.5:32b", "qwen2.5:72b", "llama3.1:70b", "mixtral:8x22b", "custom"]
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model}")
    
    try:
        model_choice = int(input("モデルを選択してください（1-5、デフォルト: 1）: ") or "1")
        if 1 <= model_choice <= len(models):
            if models[model_choice-1] == "custom":
                model_name = input("カスタムモデル名を入力: ").strip() or "qwen2.5:32b"
            else:
                model_name = models[model_choice-1]
        else:
            model_name = "qwen2.5:32b"
    except ValueError:
        model_name = "qwen2.5:32b"
    
    print(f"\n🚀 生成を開始します...")
    
    # 生成実行
    run_generation(
        theme=theme,
        units=units,
        reference_file=ref_file,
        model_name=model_name,
        output_dir="output"
    )

def run_demo():
    """デモモードの実行"""
    print("=== デモモード ===")
    print("フォークリフト安全入門のサンプル生成を行います\n")
    
    demo_themes = [
        ("フォークリフト安全入門", 1),
        ("5S基本活動", 1),
        ("化学物質安全取扱", 1),
        ("KYT実践", 1)
    ]
    
    print("利用可能なデモ:")
    for i, (theme, units) in enumerate(demo_themes, 1):
        print(f"  {i}. {theme} ({units}ユニット)")
    
    # デモモードでは自動的に最初のテーマを選択
    theme, units = demo_themes[0]
    
    print(f"\n🎯 '{theme}' のデモ生成を開始...")
    
    # デモ用参考資料
    demo_reference = f"""
{theme}に関する基本的な安全指導内容：
・作業前の安全確認が重要
・適切な保護具（PPE）の着用
・手順通りの作業実施
・危険予知訓練（KYT）の実施
・5S活動による職場環境改善
・法令遵守と安全第一の意識
"""
    
    run_generation(
        theme=theme,
        units=units,
        model_name="qwen2.5:32b",
        output_dir="demo_output"
    )

def validate_file(file_path: str):
    """ファイルバリデートのみ実行"""
    if not os.path.exists(file_path):
        print(f"❌ ファイルが見つかりません: {file_path}")
        sys.exit(1)
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")
        sys.exit(1)
    
    # 人間用とExcel用の分割を試行
    if "Excel:" in content:
        human_part, excel_part = content.split("Excel:", 1)
        human_part = human_part.strip()
        excel_part = excel_part.strip()
    else:
        human_part = content
        excel_part = ""
        print("警告: Excel形式が見つかりません")
    
    # バリデート実行
    validator = SlideValidator()
    report = validator.get_validation_report(human_part, excel_part)
    
    print("=== バリデート結果 ===")
    print(f"ファイル: {file_path}")
    print(f"結果: {'✅ 合格' if report['is_valid'] else '❌ 不合格'}")
    
    if report['errors']:
        print("\n🚨 検出されたエラー:")
        for error in report['errors']:
            print(f"  - {error}")
    
    print(f"\n📊 統計:")
    for key, value in report['stats'].items():
        print(f"  {key}: {value}")
    
    if report['suggestions']:
        print(f"\n💡 修正提案:")
        for suggestion in report['suggestions']:
            print(f"  - {suggestion}")

if __name__ == "__main__":
    main()