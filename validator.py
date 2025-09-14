import re
from typing import Tuple, List, Dict

class SlideValidator:
    """スライド台本の構造と形式をバリデートするクラス"""
    
    def __init__(self):
        self.errors = []
        
    def validate_all(self, human_text: str, excel_text: str) -> Tuple[bool, List[str]]:
        """人間用とExcel用の両方をバリデート"""
        self.errors = []
        
        # 人間用テキストのバリデート
        self._validate_human_format(human_text)
        
        # Excel用テキストのバリデート
        self._validate_excel_format(excel_text)
        
        return len(self.errors) == 0, self.errors
    
    def _validate_human_format(self, text: str) -> None:
        """人間用テキストの形式をチェック"""
        lines = text.split('\n')
        
        # ページ番号の開始チェック
        if not re.search(r'^1\s*\.', text, re.M):
            self.errors.append("1ページから開始していない")
        
        # 文字数制限チェック（50字以下）
        for line_num, line in enumerate(lines, 1):
            if line.strip() and len(line.strip()) > 50:
                self.errors.append(f"行{line_num}: 50字を超える行があります ({len(line.strip())}字)")
        
        # 必須スライド構成チェック
        required_slides = ['表紙', 'ユニット', '導入', 'NG', '理由', '正解']
        for req in required_slides:
            if req not in text:
                self.errors.append(f"必須スライド '{req}' が見つかりません")
        
        # 問いかけ・小まとめの存在チェック
        if not (re.search(r'問いかけ|小まとめ|どう思いますか？|いかがでしょうか？', text)):
            self.errors.append("問いかけまたは小まとめが見つかりません")
        
        # ページ番号の連続性チェック
        page_numbers = re.findall(r'^(\d+)\s*\.', text, re.M)
        if page_numbers:
            for i, page_str in enumerate(page_numbers):
                expected = i + 1
                actual = int(page_str)
                if actual != expected:
                    self.errors.append(f"ページ番号が飛んでいます: {expected}を期待、{actual}が検出")
    
    def _validate_excel_format(self, text: str) -> None:
        """Excel用テキストの形式をチェック"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Excel形式の行チェック（page : line : text_ja : text_en）
        excel_pattern = r'^\d+\s*:\s*\d+\s*:\s*.+\s*:\s*$'
        
        for line_num, line in enumerate(lines, 1):
            if not re.match(excel_pattern, line):
                self.errors.append(f"Excel行{line_num}: 不正な形式 (page:line:text_ja:text_en が必要)")
        
        # text_en列が空欄かチェック
        for line_num, line in enumerate(lines, 1):
            parts = line.split(':')
            if len(parts) == 4 and parts[3].strip():
                self.errors.append(f"Excel行{line_num}: text_en列は空欄である必要があります")
    
    def validate_content_quality(self, text: str) -> None:
        """コンテンツ品質のチェック"""
        # 専門用語の統一チェック
        required_terms = ['PPE', 'LOTO', 'KYT', '5S', '指差呼称', 'SDS']
        used_terms = []
        
        for term in required_terms:
            if term in text:
                used_terms.append(term)
        
        # 数値・日付フォーマットチェック
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        dates = re.findall(date_pattern, text)
        
        # タイトル文字数チェック（20字以下）
        titles = re.findall(r'^\d+\s*\.\s*(.+?)$', text, re.M)
        for title in titles:
            if len(title.strip()) > 20:
                self.errors.append(f"タイトル文字数超過: '{title.strip()}' ({len(title.strip())}字)")
    
    def get_validation_report(self, human_text: str, excel_text: str) -> Dict[str, any]:
        """バリデート結果の詳細レポートを生成"""
        is_valid, errors = self.validate_all(human_text, excel_text)
        
        # 統計情報
        human_lines = len([line for line in human_text.split('\n') if line.strip()])
        excel_lines = len([line for line in excel_text.split('\n') if line.strip()])
        
        pages = len(re.findall(r'^\d+\s*\.', human_text, re.M))
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'stats': {
                'human_lines': human_lines,
                'excel_lines': excel_lines,
                'total_pages': pages,
            },
            'suggestions': self._generate_suggestions(errors)
        }
    
    def _generate_suggestions(self, errors: List[str]) -> List[str]:
        """エラーに基づく修正提案を生成"""
        suggestions = []
        
        if any('ページ番号' in error for error in errors):
            suggestions.append("ページ番号を1から順番に振り直してください")
        
        if any('50字' in error for error in errors):
            suggestions.append("長い文章を短く分割してください")
        
        if any('問いかけ' in error for error in errors):
            suggestions.append("各スライドの最後に問いかけまたは小まとめを追加してください")
        
        if any('Excel' in error for error in errors):
            suggestions.append("Excel形式を 'page:line:text_ja:' の形式に修正してください")
        
        return suggestions

# 使用例とテスト
if __name__ == "__main__":
    validator = SlideValidator()
    
    # テストケース
    test_human = """1. 表紙
フォークリフト安全入門
現場で今日から使える基本
小まとめ：今日の目標を1つ決める

2. ユニット表紙
第1ユニット：基本操作とKYT
安全な作業のために

3. 導入
フォークリフトは便利な機械
でも危険もたくさん
どんな危険があるでしょうか？"""

    test_excel = """1 : 1 : フォークリフト安全入門 : 
1 : 2 : 現場で今日から使える基本 : 
1 : 3 : 小まとめ：今日の目標を1つ決める : 
2 : 1 : 第1ユニット：基本操作とKYT : 
2 : 2 : 安全な作業のために : """
    
    report = validator.get_validation_report(test_human, test_excel)
    print(f"バリデート結果: {report['is_valid']}")
    if report['errors']:
        print("エラー:")
        for error in report['errors']:
            print(f"  - {error}")
    
    print(f"\n統計:")
    print(f"  人間用行数: {report['stats']['human_lines']}")
    print(f"  Excel行数: {report['stats']['excel_lines']}")
    print(f"  総ページ数: {report['stats']['total_pages']}")