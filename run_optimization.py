"""
株価予測とポートフォリオ最適化の自動実行スクリプト

このスクリプトは以下を自動的に実行します：
1. 株価予測モデルの実行（LightGBM）
2. 予測結果の保存
3. CPLEXによるポートフォリオ最適化の実行
4. 結果の表示と保存
"""

import os
import sys
import subprocess
from datetime import datetime

# Windows環境での文字エンコーディング問題を回避
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def print_section(title):
    """セクションタイトルを表示"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def run_stock_prediction():
    """株価予測モデルを実行"""
    print_section("ステップ1: 株価予測モデルの実行")
    
    # modelsディレクトリに移動
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    prediction_script = os.path.join(models_dir, 'stock_prediction.py')
    
    if not os.path.exists(prediction_script):
        print(f"エラー: {prediction_script} が見つかりません")
        return False
    
    try:
        # Pythonスクリプトを実行
        result = subprocess.run(
            [sys.executable, prediction_script],
            cwd=models_dir,
            capture_output=True,
            text=True
        )
        
        # 出力を表示
        print(result.stdout)
        
        if result.returncode != 0:
            print("エラー: 株価予測モデルの実行に失敗しました")
            print(result.stderr)
            return False
        
        print("[OK] 株価予測モデルの実行が完了しました")
        return True
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        return False


def run_cplex_optimization():
    """CPLEXによるポートフォリオ最適化を実行"""
    print_section("ステップ2: ポートフォリオ最適化の実行")
    
    # CPLEXのコマンドラインツールのパスを探す
    cplex_paths = [
        r"C:\Program Files\IBM\ILOG\CPLEX_Studio2212\opl\bin\x64_win64\oplrun.exe",
        r"C:\Program Files\IBM\ILOG\CPLEX_Studio_Community2212\opl\bin\x64_win64\oplrun.exe",
        r"C:\Program Files\IBM\ILOG\CPLEX_Studio_Community2211\opl\bin\x64_win64\oplrun.exe",
        r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\opl\bin\x64_win64\oplrun.exe",
        r"C:\Program Files\IBM\ILOG\CPLEX_Studio_Community221\opl\bin\x64_win64\oplrun.exe",
        r"C:\Program Files\IBM\ILOG\CPLEX_Studio221\opl\bin\x64_win64\oplrun.exe",
    ]
    
    oplrun_path = None
    for path in cplex_paths:
        if os.path.exists(path):
            oplrun_path = path
            break
    
    if oplrun_path is None:
        print("警告: CPLEXのコマンドラインツール(oplrun.exe)が見つかりません")
        print("\n以下の方法で最適化を実行してください:")
        print("1. IBM CPLEX Optimization Studio を起動")
        print("2. optimization/portfolio.mod を開く")
        print("3. 右クリック → 'Run This' を選択")
        print("\nまたは、oplrun.exeのパスを手動で指定してください")
        return False
    
    # 最適化モデルのパス
    optimization_dir = os.path.join(os.path.dirname(__file__), 'optimization')
    model_file = os.path.join(optimization_dir, 'portfolio.mod')
    data_file = os.path.join(optimization_dir, 'portfolio.dat')
    
    if not os.path.exists(model_file):
        print(f"エラー: {model_file} が見つかりません")
        return False
    
    if not os.path.exists(data_file):
        print(f"エラー: {data_file} が見つかりません")
        return False
    
    try:
        print(f"CPLEXを実行中: {oplrun_path}")
        print(f"モデル: {model_file}")
        print(f"データ: {data_file}\n")
        
        # CPLEXを実行
        result = subprocess.run(
            [oplrun_path, model_file, data_file],
            cwd=optimization_dir,
            capture_output=True,
            text=True
        )
        
        # 出力を表示
        print(result.stdout)
        
        if result.returncode != 0:
            print("エラー: CPLEX最適化の実行に失敗しました")
            print(result.stderr)
            return False
        
        print("[OK] ポートフォリオ最適化が完了しました")
        
        # 結果をファイルに保存
        save_results(result.stdout)
        
        return True
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        return False


def save_results(output):
    """最適化結果をファイルに保存"""
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = os.path.join(results_dir, f'optimization_result_{timestamp}.txt')
    
    try:
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\n結果を保存しました: {result_file}")
    except Exception as e:
        print(f"警告: 結果の保存に失敗しました: {str(e)}")


def main():
    """メイン処理"""
    print("\n" + "=" * 70)
    print("  株式ポートフォリオ最適化システム - 自動実行")
    print("=" * 70)
    print(f"\n実行開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ステップ1: 株価予測
    if not run_stock_prediction():
        print("\n[ERROR] 株価予測モデルの実行に失敗しました")
        print("処理を中断します")
        return 1
    
    # ステップ2: ポートフォリオ最適化
    if not run_cplex_optimization():
        print("\n[WARNING] CPLEX最適化の自動実行に失敗しました")
        print("手動でCPLEX IDEから実行してください")
        return 1
    
    # 完了
    print_section("すべての処理が完了しました")
    print("[OK] 株価予測モデルの実行")
    print("[OK] ポートフォリオ最適化の実行")
    print("[OK] 結果の保存")
    print(f"\n実行完了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

# Made with Bob
