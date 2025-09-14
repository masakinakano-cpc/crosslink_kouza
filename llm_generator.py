import os
import json
import re
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from validator import SlideValidator

@dataclass
class GenerationConfig:
    """LLM生成の設定クラス"""
    model_name: str = "qwen2.5:32b"  # デフォルトモデル
    temperature: float = 0.3
    max_tokens: int = 4000
    max_retries: int = 3

class LLMSlideGenerator:
    """スライド台本生成システムのメインクラス"""
    
    def __init__(self, config: GenerationConfig = None):
        self.config = config or GenerationConfig()
        self.validator = SlideValidator()
        self.system_prompt = self._load_system_prompt()
        self.fewshot_examples = self._load_fewshot_examples()
        self.safety_dict = self._load_safety_dict()
    
    def _load_system_prompt(self) -> str:
        """システムプロンプトを読み込み"""
        try:
            with open("system_rules_ja.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "システムプロンプトファイルが見つかりません"
    
    def _load_fewshot_examples(self) -> str:
        """Few-shotサンプルを読み込み"""
        try:
            with open("fewshot_samples.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""
    
    def _load_safety_dict(self) -> str:
        """安全用語辞書を読み込み"""
        try:
            with open("safety_dict.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""
    
    def build_prompt(self, user_input: str, context_chunks: List[Dict] = None) -> str:
        """プロンプトを構築"""
        # RAG情報の構築
        rag_content = ""
        if context_chunks:
            rag_items = []
            for chunk in context_chunks:
                title = chunk.get('title', '不明')
                page = chunk.get('page', '不明')
                snippet = chunk.get('snippet', '')
                rag_items.append(f"- {title} p.{page}: {snippet}")
            rag_content = "\n".join(rag_items)
        
        # 完全なプロンプトを構築
        prompt = f"""{self.system_prompt}

[辞書]
{self.safety_dict}

[参考資料 抜粋]
{rag_content}

[ユーザー入力]
{user_input}

[出力要求]
1) 人間用スライド → 2) Excel用。Excelのtext_enは空欄。"""
        
        return prompt
    
    def generate_slides(self, user_input: str, reference_materials: str = "") -> Tuple[str, str, Dict]:
        """スライド台本を生成（メインメソッド）"""
        # コンテキストチャンクの準備（参考資料がある場合）
        context_chunks = []
        if reference_materials:
            # 簡単な分割処理（実際のRAGではより高度な処理が必要）
            paragraphs = reference_materials.split('\n\n')[:5]  # 最初の5段落を使用
            for i, para in enumerate(paragraphs):
                if para.strip():
                    context_chunks.append({
                        'title': f'参考資料{i+1}',
                        'page': str(i+1),
                        'snippet': para.strip()[:200] + ('...' if len(para.strip()) > 200 else '')
                    })
        
        # プロンプト構築
        full_prompt = self.build_prompt(user_input, context_chunks)
        
        # LLM生成（リトライ機能付き）
        for attempt in range(self.config.max_retries):
            try:
                generated_text = self._call_llm(full_prompt)
                human_text, excel_text = self._split_output(generated_text)
                
                # バリデート
                is_valid, errors = self.validator.validate_all(human_text, excel_text)
                
                if is_valid:
                    # 成功時の統計情報
                    stats = {
                        'attempt': attempt + 1,
                        'human_lines': len(human_text.split('\n')),
                        'excel_lines': len(excel_text.split('\n')),
                        'validation_passed': True
                    }
                    return human_text, excel_text, stats
                else:
                    # バリデート失敗時は修正プロンプトで再試行
                    if attempt < self.config.max_retries - 1:
                        correction_prompt = self._build_correction_prompt(errors, generated_text)
                        full_prompt = correction_prompt
                    
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise e
        
        # 最大試行回数に達した場合
        stats = {
            'attempt': self.config.max_retries,
            'validation_passed': False,
            'final_errors': errors if 'errors' in locals() else ['生成に失敗しました']
        }
        return generated_text if 'generated_text' in locals() else "", "", stats
    
    def _call_llm(self, prompt: str) -> str:
        """LLMを呼び出し（実際のLLM API使用）"""
        print(f"[DEBUG] LLMを呼び出し中... (モデル: {self.config.model_name})")
        print(f"[DEBUG] プロンプト長: {len(prompt)} 文字")
        
        # 1. まずOpenAI APIを試行
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and self.config.model_name.startswith("gpt"):
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                print("[DEBUG] OpenAI API使用成功")
                return response.choices[0].message.content
            except Exception as e:
                print(f"[DEBUG] OpenAI API失敗: {e}")
        
        # 2. ollama APIを試行
        try:
            response = requests.post("http://localhost:11434/api/generate", json={
                "model": self.config.model_name.replace("gpt-", "qwen2.5:"),
                "prompt": f"{self.system_prompt}\n\n{prompt}",
                "temperature": self.config.temperature,
                "stream": False
            }, timeout=120)
            
            if response.status_code == 200:
                print("[DEBUG] ollama使用成功")
                return response.json()["response"]
            else:
                print(f"[DEBUG] ollama失敗: {response.status_code}")
        except Exception as e:
            print(f"[DEBUG] ollama接続失敗: {e}")
        
        # 3. フォールバック：デモ用レスポンス
        print("[DEBUG] 実LLMが利用できません。デモ用レスポンスを使用")
        return self._demo_response()
    
    def _demo_response(self) -> str:
        """デモ用の固定レスポンス"""
        return """5重チェック（辞書・構成・対象・数値・安全）完了: ①②③④⑤

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

4. NG[赤]
×　ヘルメットなしで運転
×　急な加速・停止
危険な行動の例です

5. 理由[青]
ヘルメットは頭部を守る
急な動きは荷崩れの原因
PPEと操作が重要です

6. 正解[緑]
○　PPE着用で安全運転
○　ゆっくり確実な操作
正しい手順を覚えましょう

7. 理由[青]
PPEは法律で決まっている
確実な操作が事故を防ぐ
小まとめ：安全第一で作業

Excel:
1 : 1 : フォークリフト安全入門 : 
1 : 2 : 現場で今日から使える基本 : 
1 : 3 : 小まとめ：今日の目標を1つ決める : 
2 : 1 : 第1ユニット：基本操作とKYT : 
2 : 2 : 安全な作業のために : 
3 : 1 : フォークリフトは便利な機械 : 
3 : 2 : でも危険もたくさん : 
3 : 3 : どんな危険があるでしょうか？ : 
4 : 1 : ×　ヘルメットなしで運転 : 
4 : 2 : ×　急な加速・停止 : 
4 : 3 : 危険な行動の例です : 
5 : 1 : ヘルメットは頭部を守る : 
5 : 2 : 急な動きは荷崩れの原因 : 
5 : 3 : PPEと操作が重要です : 
6 : 1 : ○　PPE着用で安全運転 : 
6 : 2 : ○　ゆっくり確実な操作 : 
6 : 3 : 正しい手順を覚えましょう : 
7 : 1 : PPEは法律で決まっている : 
7 : 2 : 確実な操作が事故を防ぐ : 
7 : 3 : 小まとめ：安全第一で作業 : """
    
    def _split_output(self, generated_text: str) -> Tuple[str, str]:
        """生成テキストを人間用とExcel用に分割"""
        # "Excel:" で分割
        if "Excel:" in generated_text:
            parts = generated_text.split("Excel:", 1)
            human_part = parts[0].strip()
            excel_part = parts[1].strip() if len(parts) > 1 else ""
        else:
            # Excel部分がない場合
            human_part = generated_text.strip()
            excel_part = ""
        
        # 5重チェック行を人間用から除去（Excel用には含めない）
        human_lines = human_part.split('\n')
        if human_lines and '5重チェック' in human_lines[0]:
            human_part = '\n'.join(human_lines[1:]).strip()
        
        return human_part, excel_part
    
    def _build_correction_prompt(self, errors: List[str], previous_output: str) -> str:
        """修正用プロンプトを構築"""
        error_summary = "\n".join(f"- {error}" for error in errors)
        
        correction_prompt = f"""{self.system_prompt}

[前回の出力に以下の問題がありました]
{error_summary}

[修正指示]
上記の問題を修正して、正しい形式で再出力してください。

[前回の出力]
{previous_output}

[出力要求]
修正された 1) 人間用スライド → 2) Excel用"""
        
        return correction_prompt
    
    def save_output(self, human_text: str, excel_text: str, output_dir: str = "output") -> Dict[str, str]:
        """生成結果をファイルに保存"""
        os.makedirs(output_dir, exist_ok=True)
        
        # ファイルパス
        human_file = os.path.join(output_dir, "slide_human.txt")
        excel_file = os.path.join(output_dir, "slide_excel.txt")
        
        # 保存
        with open(human_file, "w", encoding="utf-8") as f:
            f.write(human_text)
        
        with open(excel_file, "w", encoding="utf-8") as f:
            f.write(excel_text)
        
        return {
            "human_file": human_file,
            "excel_file": excel_file
        }

# 使用例
if __name__ == "__main__":
    # 設定
    config = GenerationConfig(
        model_name="qwen2.5:32b",
        temperature=0.3,
        max_retries=2
    )
    
    # ジェネレータ初期化
    generator = LLMSlideGenerator(config)
    
    # テスト入力
    test_input = """【テーマ】フォークリフトのKYT入門
【ユニット数】1
【参考資料】フォークリフトは産業車両として多くの現場で使用されています。正しい操作と安全確認が重要です。
【出力】人間用→Excel用の順。比較スライドは日本×自国。
【注意】不足は『要確認』と明示。用語は内蔵辞書を優先。"""
    
    # 生成実行
    try:
        human_output, excel_output, stats = generator.generate_slides(test_input)
        
        print("=== 生成結果 ===")
        print(f"試行回数: {stats.get('attempt', 'N/A')}")
        print(f"バリデート: {'合格' if stats.get('validation_passed') else '不合格'}")
        
        if stats.get('validation_passed'):
            print("\n=== 人間用スライド ===")
            print(human_output)
            print("\n=== Excel用 ===")
            print(excel_output)
            
            # ファイル保存
            file_paths = generator.save_output(human_output, excel_output)
            print(f"\n保存先: {file_paths}")
        else:
            print(f"エラー: {stats.get('final_errors', [])}")
            
    except Exception as e:
        print(f"生成エラー: {e}")