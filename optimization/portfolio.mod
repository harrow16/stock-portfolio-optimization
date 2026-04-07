/*********************************************
 * ポートフォリオ最適化モデル
 * 
 * 目的: 予測収益率を基に最適なポートフォリオを構築
 * 制約:
 *   - 予算: 100万円以内（手数料込み）
 *   - 銘柄数: 最大5銘柄
 *   - 業界分散: 同一セクターから最大1銘柄
 *   - 購入単位: 100株の整数倍
 *********************************************/

// データ構造の定義
tuple Stock {
    string Ticker;           // 銘柄コード
    float Current_Price;     // 現在の株価
    float Predicted_Return;  // 予測収益率
    string Sector;           // 業界
    string Name;             // 企業名
}

// パラメータ
{Stock} Stocks = ...;                    // 銘柄データ
float Budget = 1000000;                  // 予算（100万円）
float CommissionRate = 0.001;            // 手数料率（0.1%）
int MaxStocks = 5;                       // 最大銘柄数
int LotSize = 100;                       // 購入単位（100株固定）
{string} Sectors = {s.Sector | s in Stocks};  // 業界の集合

// 決定変数
dvar int+ units[Stocks];                 // 各銘柄の購入単元数（100株単位）
dvar boolean selected[Stocks];           // 銘柄を選択するか（0 or 1）

// 目的関数: 期待収益を最大化
// 期待収益 = Σ(株価 × 収益率 × 購入株数) - 手数料
dexpr float TotalInvestment = sum(s in Stocks) s.Current_Price * units[s] * LotSize;
dexpr float Commission = TotalInvestment * CommissionRate;
dexpr float ExpectedReturn = sum(s in Stocks) s.Current_Price * s.Predicted_Return * units[s] * LotSize;
dexpr float NetReturn = ExpectedReturn - Commission;

maximize NetReturn;

// 制約条件
subject to {
    // 1. 予算制約: 投資総額 + 手数料 <= 100万円
    ctBudget:
        TotalInvestment + Commission <= Budget;
    
    // 2. 銘柄数制約: 選択する銘柄は最大5銘柄
    ctMaxStocks:
        sum(s in Stocks) selected[s] <= MaxStocks;
    
    // 3. 業界分散制約: 同じセクターからは最大1銘柄
    forall(sector in Sectors)
        ctSectorDiversity:
            sum(s in Stocks: s.Sector == sector) selected[s] <= 1;
    
    // 4. 購入単位制約: 銘柄を選択した場合のみ購入可能
    forall(s in Stocks)
        ctSelection:
            units[s] <= 10000 * selected[s];  // 十分大きな数（Big-M法）
    
    // 5. 最小購入制約: 選択した銘柄は最低1単元購入
    forall(s in Stocks)
        ctMinPurchase:
            units[s] >= selected[s];
}

// 実行後の処理
execute DISPLAY {
    writeln();
    writeln("========================================================================");
    writeln("           Portfolio Optimization Result - Investment Report           ");
    writeln("========================================================================");
    writeln();
    
    var totalCost = 0;
    var totalShares = 0;
    var selectedCount = 0;
    var totalExpectedProfit = 0;
    
    writeln("[ Selected Stocks ]");
    writeln("------------------------------------------------------------------------");
    writeln();
    
    var rank = 1;
    for(var s in Stocks) {
        if(selected[s] == 1) {
            var shares = units[s] * LotSize;
            var cost = s.Current_Price * shares;
            var expectedProfit = cost * s.Predicted_Return;
            totalCost += cost;
            totalShares += shares;
            totalExpectedProfit += expectedProfit;
            selectedCount++;
            
            writeln("[ Stock #" + rank + " ]");
            writeln("  Company Name      : " + s.Name);
            writeln("  Ticker Code       : " + s.Ticker);
            writeln("  Sector            : " + s.Sector);
            writeln("  Current Price     : " + Opl.round(s.Current_Price * 100) / 100 + " JPY");
            writeln("  Units to Buy      : " + units[s] + " units");
            writeln("  Shares to Buy     : " + shares + " shares");
            writeln("  Investment Amount : " + Opl.round(cost) + " JPY");
            writeln("  Expected Return   : " + Opl.round(s.Predicted_Return * 10000) / 100 + " %");
            writeln("  Expected Profit   : " + Opl.round(expectedProfit) + " JPY");
            writeln("  Portfolio Weight  : " + Opl.round((cost / totalCost) * 10000) / 100 + " %");
            writeln();
            rank++;
        }
    }
    
    writeln("------------------------------------------------------------------------");
    writeln();
    writeln("[ Portfolio Summary ]");
    writeln("------------------------------------------------------------------------");
    writeln();
    writeln("  Selected Stocks         : " + selectedCount + " stocks");
    writeln("  Total Shares            : " + totalShares + " shares");
    writeln();
    writeln("[ Investment Breakdown ]");
    writeln("  Principal Investment    : " + Opl.round(totalCost) + " JPY");
    writeln("  Trading Fee (0.1%)      : " + Opl.round(totalCost * CommissionRate) + " JPY");
    writeln("  ------------------------------------------------");
    writeln("  Total Cost              : " + Opl.round(totalCost * (1 + CommissionRate)) + " JPY");
    writeln("  Budget Remaining        : " + Opl.round(Budget - totalCost * (1 + CommissionRate)) + " JPY");
    writeln();
    writeln("[ Expected Returns (5 Trading Days) ]");
    writeln("  Expected Total Profit   : " + Opl.round(totalExpectedProfit) + " JPY");
    writeln("  Net Profit (after fee)  : " + Opl.round(NetReturn) + " JPY");
    writeln("  ------------------------------------------------");
    writeln("  Expected Return Rate    : " + Opl.round((NetReturn / totalCost) * 10000) / 100 + " %");
    writeln();
    writeln("[ Risk Diversification ]");
    writeln("  Number of Stocks        : " + selectedCount + " stocks");
    writeln("  Sector Diversification  : Each stock from different sector");
    writeln("  Diversification Effect  : Minimized sector-specific risk");
    writeln();
    writeln("------------------------------------------------------------------------");
    writeln();
    writeln("[ Constraint Satisfaction ]");
    writeln("  [OK] Budget constraint satisfied (within 1,000,000 JPY)");
    writeln("  [OK] Stock limit satisfied (max 5 stocks)");
    writeln("  [OK] Sector diversity satisfied (max 1 stock per sector)");
    writeln("  [OK] Lot size constraint satisfied (100 shares unit)");
    writeln();
    writeln("[ Disclaimer ]");
    writeln("  * This result is based on machine learning predictions");
    writeln("  * Investment decisions should be made at your own risk");
    writeln("  * Past performance does not guarantee future results");
    writeln();
    writeln("========================================================================");
    writeln("                    Optimization Completed                              ");
    writeln("========================================================================");
    writeln();
}

// Made with Bob
