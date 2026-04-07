# 株式ポートフォリオ最適化システム

機械学習（LightGBM）と数理最適化（IBM CPLEX）を組み合わせた、包括的な株式ポートフォリオ最適化システムです。

## 📋 概要

このプロジェクトは、2段階のアプローチでポートフォリオ最適化を実現します：
1. **株価予測**: LightGBMを使用して119銘柄の5営業日後の収益率を予測
2. **ポートフォリオ最適化**: IBM CPLEXを使用して、制約条件下で最適なポートフォリオを選択

## 🎯 主な機能

- **機械学習による予測**
  - LightGBMベースの回帰モデル
  - 14種類のテクニカル指標を特徴量として使用
  - 5営業日後の収益率を予測
  - 日本株119銘柄に対応

- **数理最適化**
  - 予算制約: 100万円以内
  - 最大5銘柄まで選択
  - 業界分散（同一セクターから最大1銘柄）
  - 購入単位制約（100株単位）
  - 手数料控除後の期待収益を最大化

## 📁 プロジェクト構造

```
C:/Bob/20260420/
├── data/
│   ├── sampledata.csv              # 株価時系列データ（119銘柄）
│   └── prediction_results.csv      # 機械学習による予測結果
├── models/
│   └── stock_prediction.py         # LightGBM予測モデル
├── optimization/
│   ├── portfolio.mod               # CPLEX最適化モデル
│   └── portfolio.dat               # 最適化用データ（119銘柄全データ）
├── results/                        # 結果出力ディレクトリ
├── .gitignore                      # Git除外設定
└── README.md                       # このファイル
```

## 🚀 使い方

### 必要な環境

**株価予測用:**
- Python 3.8以上
- pandas
- numpy
- lightgbm
- scikit-learn

**ポートフォリオ最適化用:**
- IBM CPLEX Optimization Studio

### インストール

1. **リポジトリのクローン**
```bash
git clone https://github.com/yourusername/stock-portfolio-optimization.git
cd stock-portfolio-optimization
```

2. **Pythonパッケージのインストール**
```bash
pip install pandas numpy lightgbm scikit-learn
```

3. **IBM CPLEXのインストール**
   - [IBM CPLEX公式サイト](https://www.ibm.com/products/ilog-cplex-optimization-studio)からダウンロード
   - インストール手順に従ってセットアップ

## 📊 実行方法

### ステップ1: 株価予測の実行

```bash
cd models
python stock_prediction.py
```

**出力**: `data/prediction_results.csv` に全銘柄の予測収益率が保存されます

**コンソール出力例:**
```
============================================================
株価予測モデル実行開始
============================================================
データを読み込んでいます...
データ読み込み完了: 29036行, 119銘柄
期間: 2025-03-27 ～ 2026-03-26

特徴量を作成しています...
特徴量作成完了: 14個の特徴量

モデルを訓練しています...

モデル評価:
  MSE: 0.002287
  MAE: 0.033692
  R2: 0.033891

特徴量の重要度 (Top 5):
         feature  importance
9  Volatility_20         272
3     Return_20d         241
...

予測完了: 119銘柄

予測結果を保存しました: ../data/prediction_results.csv
============================================================
```

### ステップ2: ポートフォリオ最適化の実行

1. IBM CPLEX Optimization Studioを起動
2. `optimization/portfolio.mod` を開く
3. 右クリック → **Run This** を選択

**出力例:**
```
========================================================================
           Portfolio Optimization Result - Investment Report           
========================================================================

[ Selected Stocks ]
------------------------------------------------------------------------

[ Stock #1 ]
  Company Name      : Taiyo Yuden Co., Ltd.
  Ticker Code       : 6976.T
  Sector            : Technology
  Current Price     : 4160 JPY
  Units to Buy      : 2 units
  Shares to Buy     : 200 shares
  Investment Amount : 832000 JPY
  Expected Return   : 2.99 %
  Expected Profit   : 24877 JPY
  Portfolio Weight  : 41.5 %

...

[ Portfolio Summary ]
------------------------------------------------------------------------
  Selected Stocks         : 5 stocks
  Total Shares            : 1000 shares

[ Investment Breakdown ]
  Principal Investment    : 980000 JPY
  Trading Fee (0.1%)      : 980 JPY
  Total Cost              : 980980 JPY
  Budget Remaining        : 19020 JPY

[ Expected Returns (5 Trading Days) ]
  Expected Total Profit   : 25000 JPY
  Net Profit (after fee)  : 24020 JPY
  Expected Return Rate    : 2.45 %
========================================================================
```

## 🔧 技術詳細

### 機械学習モデル

**アルゴリズム**: LightGBM（勾配ブースティング）

**特徴量**（14種類のテクニカル指標）:
- リターン: 1日、5日、10日、20日
- 移動平均乖離率: 5日、10日、20日
- ボラティリティ: 5日、10日、20日
- 出来高比率
- 価格位置: 5日、10日、20日

**予測対象**: 5営業日後の収益率

**モデルパラメータ**:
```python
LGBMRegressor(
    n_estimators=100,      # ツリーの数
    learning_rate=0.05,    # 学習率
    max_depth=5,           # ツリーの深さ
    num_leaves=31,         # 葉の数
    random_state=42
)
```

### 最適化モデル

**目的関数**:
```
最大化: 期待収益 - 取引手数料
```

**決定変数**:
- `units[s]`: 銘柄sの購入単元数（整数）
- `selected[s]`: 銘柄sを選択するか（0 or 1）

**制約条件**:
1. **予算制約**: 総コスト + 手数料 ≤ 100万円
2. **銘柄数制約**: 最大5銘柄
3. **業界分散制約**: 同一セクターから最大1銘柄
4. **購入単位制約**: 100株単位で購入
5. **最小購入制約**: 選択した銘柄は最低1単元購入

## 📈 データ

### 対象銘柄
- **日本株119銘柄**（主要指数構成銘柄）
- **セクター**: テクノロジー、エネルギー、公益事業、素材、資本財、金融サービス、ヘルスケア、生活必需品、一般消費財、通信サービス、不動産

### 予測収益率上位10銘柄
1. 太陽誘電 (6976.T) - Technology - 2.99%
2. INPEX (1605.T) - Energy - 2.77%
3. 東京電力HD (9501.T) - Utilities - 2.73%
4. 住友化学 (4005.T) - Basic Materials - 2.71%
5. 住友金属鉱山 (5713.T) - Basic Materials - 2.67%
6. DOWAホールディングス (5714.T) - Basic Materials - 2.47%
7. 三井物産 (8031.T) - Industrials - 2.47%
8. 丸紅 (8002.T) - Industrials - 2.34%
9. 関西電力 (9503.T) - Utilities - 2.33%
10. ENEOSホールディングス (5020.T) - Energy - 2.24%

## ⚠️ 免責事項

**重要**: このプロジェクトは教育・研究目的のみです。

- 予測は過去データと機械学習モデルに基づいています
- 過去のパフォーマンスは将来の結果を保証しません
- これは投資助言ではありません
- 投資判断は必ずご自身で調査の上、行ってください
- 専門の金融アドバイザーにご相談ください
- 作者は金銭的損失について一切の責任を負いません

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細はLICENSEファイルをご覧ください。

## 🤝 貢献

プルリクエストを歓迎します！お気軽にご提案ください。

## 📧 お問い合わせ

質問やフィードバックは、GitHubのIssueでお願いします。

## 🙏 謝辞

- LightGBMチーム - 優れた勾配ブースティングフレームワーク
- IBM - CPLEX Optimization Studio
- 金融データプロバイダー

---

**Made with Bob** 🤖