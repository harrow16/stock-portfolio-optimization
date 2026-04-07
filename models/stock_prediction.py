"""
株価予測モデル
LightGBMを使用して各銘柄の5営業日後の収益率を予測
"""

import pandas as pd
import numpy as np
from lightgbm import LGBMRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')


class StockPredictor:
    """株価予測クラス"""
    
    def __init__(self, data_path='../data/sampledata.csv'):
        """
        初期化
        
        Args:
            data_path: データファイルのパス
        """
        self.data_path = data_path
        self.df = None
        self.models = {}
        self.feature_cols = []
        
    def load_data(self):
        """データの読み込み"""
        print("データを読み込んでいます...")
        self.df = pd.read_csv(self.data_path)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df = self.df.sort_values(['Ticker', 'Date']).reset_index(drop=True)
        
        # MinLotSizeカラムを追加（要件では100固定）
        self.df['MinLotSize'] = 100
        
        print(f"データ読み込み完了: {len(self.df)}行, {len(self.df['Ticker'].unique())}銘柄")
        print(f"期間: {self.df['Date'].min()} ～ {self.df['Date'].max()}")
        
    def create_features(self):
        """特徴量の作成"""
        print("\n特徴量を作成しています...")
        
        # 銘柄ごとに特徴量を作成
        feature_dfs = []
        
        for ticker in self.df['Ticker'].unique():
            ticker_df = self.df[self.df['Ticker'] == ticker].copy()
            
            # 基本的な特徴量
            ticker_df['Return_1d'] = ticker_df['Close'].pct_change(1)  # 1日リターン
            ticker_df['Return_5d'] = ticker_df['Close'].pct_change(5)  # 5日リターン
            ticker_df['Return_10d'] = ticker_df['Close'].pct_change(10)  # 10日リターン
            ticker_df['Return_20d'] = ticker_df['Close'].pct_change(20)  # 20日リターン
            
            # 移動平均
            ticker_df['MA_5'] = ticker_df['Close'].rolling(window=5).mean()
            ticker_df['MA_10'] = ticker_df['Close'].rolling(window=10).mean()
            ticker_df['MA_20'] = ticker_df['Close'].rolling(window=20).mean()
            
            # 移動平均からの乖離率
            ticker_df['MA_5_ratio'] = ticker_df['Close'] / ticker_df['MA_5'] - 1
            ticker_df['MA_10_ratio'] = ticker_df['Close'] / ticker_df['MA_10'] - 1
            ticker_df['MA_20_ratio'] = ticker_df['Close'] / ticker_df['MA_20'] - 1
            
            # ボラティリティ（標準偏差）
            ticker_df['Volatility_5'] = ticker_df['Return_1d'].rolling(window=5).std()
            ticker_df['Volatility_10'] = ticker_df['Return_1d'].rolling(window=10).std()
            ticker_df['Volatility_20'] = ticker_df['Return_1d'].rolling(window=20).std()
            
            # 出来高関連
            ticker_df['Volume_MA_5'] = ticker_df['Volume'].rolling(window=5).mean()
            ticker_df['Volume_ratio'] = ticker_df['Volume'] / ticker_df['Volume_MA_5']
            
            # 高値・安値（過去5日、10日、20日）
            ticker_df['High_5'] = ticker_df['Close'].rolling(window=5).max()
            ticker_df['Low_5'] = ticker_df['Close'].rolling(window=5).min()
            ticker_df['High_10'] = ticker_df['Close'].rolling(window=10).max()
            ticker_df['Low_10'] = ticker_df['Close'].rolling(window=10).min()
            ticker_df['High_20'] = ticker_df['Close'].rolling(window=20).max()
            ticker_df['Low_20'] = ticker_df['Close'].rolling(window=20).min()
            
            # 高値・安値からの位置
            ticker_df['Position_5'] = (ticker_df['Close'] - ticker_df['Low_5']) / (ticker_df['High_5'] - ticker_df['Low_5'])
            ticker_df['Position_10'] = (ticker_df['Close'] - ticker_df['Low_10']) / (ticker_df['High_10'] - ticker_df['Low_10'])
            ticker_df['Position_20'] = (ticker_df['Close'] - ticker_df['Low_20']) / (ticker_df['High_20'] - ticker_df['Low_20'])
            
            # ターゲット: 5営業日後の収益率
            ticker_df['Target_Return_5d'] = ticker_df['Close'].pct_change(5).shift(-5)
            
            feature_dfs.append(ticker_df)
        
        self.df = pd.concat(feature_dfs, ignore_index=True)
        
        # 特徴量カラムのリスト
        self.feature_cols = [
            'Return_1d', 'Return_5d', 'Return_10d', 'Return_20d',
            'MA_5_ratio', 'MA_10_ratio', 'MA_20_ratio',
            'Volatility_5', 'Volatility_10', 'Volatility_20',
            'Volume_ratio',
            'Position_5', 'Position_10', 'Position_20'
        ]
        
        print(f"特徴量作成完了: {len(self.feature_cols)}個の特徴量")
        
    def train_model(self):
        """モデルの訓練"""
        print("\nモデルを訓練しています...")
        
        # 欠損値を除去
        train_df = self.df.dropna(subset=self.feature_cols + ['Target_Return_5d'])
        
        # 最新5営業日のデータは予測対象なので訓練データから除外
        latest_date = train_df['Date'].max()
        train_df = train_df[train_df['Date'] < latest_date - pd.Timedelta(days=3)]
        
        X = train_df[self.feature_cols]
        y = train_df['Target_Return_5d']
        
        # 訓練データとテストデータに分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # LightGBMモデルの訓練
        model = LGBMRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            num_leaves=31,
            random_state=42,
            verbose=-1
        )
        
        model.fit(X_train, y_train)
        
        # モデルの評価
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"\nモデル評価:")
        print(f"  MSE: {mse:.6f}")
        print(f"  MAE: {mae:.6f}")
        print(f"  R2: {r2:.6f}")
        
        # 特徴量の重要度
        feature_importance = pd.DataFrame({
            'feature': self.feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n特徴量の重要度 (Top 5):")
        print(feature_importance.head())
        
        self.models['main'] = model
        
    def predict_latest(self):
        """最新データに対する予測"""
        print("\n最新データに対して予測を実行しています...")
        
        # 最新の日付を取得
        latest_date = self.df['Date'].max()
        print(f"最新日付: {latest_date}")
        
        # 各銘柄の最新データを取得
        latest_df = self.df[self.df['Date'] == latest_date].copy()
        
        # 予測に必要な特徴量が揃っているデータのみ
        prediction_df = latest_df.dropna(subset=self.feature_cols)
        
        if len(prediction_df) == 0:
            print("警告: 予測可能なデータがありません")
            return None
        
        # 予測実行
        X_pred = prediction_df[self.feature_cols]
        predictions = self.models['main'].predict(X_pred)
        
        # 結果をまとめる
        result_df = pd.DataFrame({
            'Ticker': prediction_df['Ticker'].values,
            'Current_Price': prediction_df['Close'].values,
            'Predicted_Return': predictions,
            'Sector': prediction_df['Sector'].values,
            'MinLotSize': prediction_df['MinLotSize'].values,
            'Name': prediction_df['Name'].values
        })
        
        # 予測収益率でソート（降順）
        result_df = result_df.sort_values('Predicted_Return', ascending=False)
        
        print(f"\n予測完了: {len(result_df)}銘柄")
        print("\n予測結果 (Top 10):")
        print(result_df.head(10).to_string(index=False))
        
        return result_df
    
    def save_predictions(self, result_df, output_path='../data/prediction_results.csv'):
        """予測結果の保存"""
        if result_df is None:
            print("保存する予測結果がありません")
            return
        
        result_df.to_csv(output_path, index=False)
        print(f"\n予測結果を保存しました: {output_path}")
        print(f"保存された銘柄数: {len(result_df)}")
        
    def run(self):
        """予測パイプライン全体を実行"""
        print("=" * 60)
        print("株価予測モデル実行開始")
        print("=" * 60)
        
        # データ読み込み
        self.load_data()
        
        # 特徴量作成
        self.create_features()
        
        # モデル訓練
        self.train_model()
        
        # 予測実行
        result_df = self.predict_latest()
        
        # 結果保存
        if result_df is not None:
            self.save_predictions(result_df)
        
        print("\n" + "=" * 60)
        print("株価予測モデル実行完了")
        print("=" * 60)
        
        return result_df


def main():
    """メイン関数"""
    import os
    
    # カレントディレクトリをスクリプトの場所に変更
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 予測実行
    predictor = StockPredictor()
    predictor.run()


if __name__ == '__main__':
    main()

# Made with Bob
