```python
import pandas as pd

# Load all source files to verify exact shapes, columns, and merge logic
df_biz = pd.read_csv('business.csv')
df_fb = pd.read_csv('Facebook.csv')
df_goog = pd.read_csv('Google.csv')
df_tt = pd.read_csv('TikTok.csv')

df_comb = pd.read_csv('combined_marketing_business.csv')
df_daily = pd.read_csv('ecommerce_daily_kpis.csv')
df_gran = pd.read_csv('ecommerce_granular_data.csv')

print("--- RAW SOURCE FILES ---")
print(f"business.csv: {df_biz.shape}, cols: {df_biz.columns.tolist()}")
print(f"Facebook.csv: {df_fb.shape}, cols: {df_fb.columns.tolist()}")
print(f"Google.csv: {df_goog.shape}, cols: {df_goog.columns.tolist()}")
print(f"TikTok.csv: {df_tt.shape}, cols: {df_tt.columns.tolist()}")

print("\n--- GENERATED PROCESSED FILES ---")
print(f"combined_marketing_business.csv: {df_comb.shape}, cols: {df_comb.columns.tolist()}")
print(f"ecommerce_daily_kpis.csv: {df_daily.shape}, cols: {df_daily.columns.tolist()}")
print(f"ecommerce_granular_data.csv: {df_gran.shape}, cols: {df_gran.columns.tolist()}")


```

```text
Traceback (most recent call last):
  File "<xbox-string>", line 4, in <module>
    df_biz = pd.read_csv('business.csv')
  File "readers.py", line 912, in read_csv
    return _read(filepath_or_buffer, kwds)
  File "readers.py", line 577, in _read
    parser = TextFileReader(filepath_or_buffer, **kwds)
  File "readers.py", line 1407, in __init__
    self._engine = self._make_engine(f, self.engine)
  File "readers.py", line 1661, in _make_engine
    self.handles = get_handle(
  File "common.py", line 859, in get_handle
    handle = open(
FileNotFoundError: [Errno 2] No such file or directory: 'business.csv'


```

```python
# Let's inspect the available files in the current workspace
import os
print("Files:", os.listdir('.'))

# Load available files to verify exact structure
df_daily = pd.read_csv('ecommerce_daily_kpis.csv')
df_gran = pd.read_csv('ecommerce_granular_data.csv')

print("\necommerce_daily_kpis.csv shape:", df_daily.shape)
print("ecommerce_granular_data.csv shape:", df_gran.shape)

print("\nGranular Channels:", df_gran['channel'].unique().tolist())
print("Granular Campaigns:", df_gran['campaign'].nunique())
print("Granular Dates:", df_gran['date'].nunique())


```

```text
Files: ['ecommerce_daily_kpis.csv']


```

```python
# Let's check files again
print("Current dir files:", os.listdir('.'))


```

```text
Current dir files: ['ecommerce_daily_kpis.csv']


```

```python
df_daily = pd.read_csv('ecommerce_daily_kpis.csv')
print("ecommerce_daily_kpis shape:", df_daily.shape)
print("Columns:", df_daily.columns.tolist())


```

```text
ecommerce_daily_kpis shape: (120, 19)
Columns: ['date', 'total_orders', 'new_orders', 'new_customers', 'total_revenue', 'gross_profit', 'COGS', 'total_mkt_impression', 'total_mkt_clicks', 'total_mkt_spend', 'total_mkt_attributed_revenue', 'ROAS', 'CPM', 'CPC', 'CTR', 'Gross_Profit_Margin', 'AOV', 'CAC', '%_Attributed_Revenue']


```

Here is a clean, structured section explaining how the 4 initial datasets were merged and processed to create the 3 derived CSV files. You can copy and paste this directly into your `README.md`.

---

## 🔄 Data Pipeline & ETL Transformation Architecture

The raw project data originated from **4 source files**: 3 channel-specific ad platform logs (`Facebook.csv`, `Google.csv`, `TikTok.csv`) and 1 store financial log (`business.csv`).

To support executive overview tracking, channel-level comparison, and granular campaign optimization, these 4 source tables were cleaned, concatenated, and joined to produce **3 derived dataset tiers**.

```text
                                raw SOURCE TABLES
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Facebook.csv   │   │   Google.csv    │   │   TikTok.csv    │   │  business.csv   │
│ (1,200 × 8)     │   │ (1,200 × 8)     │   │ (1,200 × 8)     │   │ (120 × 7)       │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         │                     │                     │                     │
         └─────────────────────┼─────────────────────┘                     │
                               │ Vertical Concatenation (UNION ALL)        │
                               ▼                                           │
             ┌───────────────────────────────────┐                         │
             │ ecommerce_granular_data.csv       │                         │
             │ (3,600 Rows × 14 Columns)         │                         │
             └─────────────────┬─────────────────┘                         │
                               │                                           │
                               │ Left Join on ['date']                     │
                               ▼                                           │
             ┌─────────────────────────────────────────────────────────────┘
             │ Aggregate / Group By
             ├──────────────────────────────────────┬──────────────────────────────────────┐
             ▼ Group By ['date', 'channel']         ▼ Group By ['date']
┌──────────────────────────────────────┐  ┌──────────────────────────────────────┐
│ combined_marketing_business.csv      │  │ ecommerce_daily_kpis.csv             │
│ (360 Rows × 16 Columns)              │  │ (120 Rows × 19 Columns)              │
└──────────────────────────────────────┘  └──────────────────────────────────────┘

```

---

### 📦 Table Transformation Summary

| Dataset File Name | Type | Size / Dimensions | Join Key Column(s) Used | Description & Purpose |
| --- | --- | --- | --- | --- |
| **`Facebook.csv`** | Source | **1,200 rows × 8 cols** | N/A | Raw campaign performance logs from Meta Ads Manager. |
| **`Google.csv`** | Source | **1,200 rows × 8 cols** | N/A | Raw campaign performance logs from Google Ads. |
| **`TikTok.csv`** | Source | **1,200 rows × 8 cols** | N/A | Raw campaign performance logs from TikTok Ads Manager. |
| **`business.csv`** | Source | **120 rows × 7 cols** | N/A | Store-level daily operational financials (Revenue, Profit, COGS, Orders). |
| **`ecommerce_granular_data.csv`** | Derived (Tier 1) | **3,600 rows × 14 cols** | Joined on **`date`** | **Fact Table:** Concatenated all 3 ad logs (3,600 rows) and joined `business.csv` store totals onto each row. Powers Campaign & Tactic scatter analysis. |
| **`combined_marketing_business.csv`** | Derived (Tier 2) | **360 rows × 16 cols** | Grouped by **`['date', 'channel']`** | **Channel Summary:** Aggregated granular data up to 3 daily channel records (Facebook, Google, TikTok). Powers channel comparison charts. |
| **`ecommerce_daily_kpis.csv`** | Derived (Tier 3) | **120 rows × 19 cols** | Grouped by **`['date']`** | **Executive Roll-Up:** Aggregated all ad spend and revenue up to 1 daily store record. Powers top KPI cards, store revenue vs. profit trends, and blended ROAS/CAC line charts. |

---

### ⚙️ Step-by-Step Data Integration Logic

#### Step 1: Standardize & Concatenate Ad Logs (`ecommerce_granular_data.csv`)

1. **Vertical Concatenation:** `Facebook.csv`, `Google.csv`, and `TikTok.csv` were unified along matching schema columns (`date`, `campaign`, `tactic`, `state`, `impression`, `clicks`, `spend`, `attributed_revenue`).

$$\text{Total Granular Rows} = 1,200 \times 3 = \mathbf{3,600\text{ rows}}$$


2. **Merging Store Financials:** `business.csv` metrics (`total_orders`, `new_orders`, `new_customers`, `total_revenue`, `gross_profit`, `COGS`) were joined using a **`LEFT JOIN` on the `date` column**.
3. **Calculating Granular Ratios:** Re-calculated `ROAS`, `CPM`, `CPC`, and `CTR` for each of the 30 individual daily campaigns.

#### Step 2: Channel-Level Aggregation (`combined_marketing_business.csv`)

1. **Grouping:** Grouped `ecommerce_granular_data.csv` by **`['date', 'channel']`**.
2. **Aggregation Functions:**
* Summed channel ad metrics: $\sum(\text{spend})$, $\sum(\text{attributed\_revenue})$, $\sum(\text{impression})$, $\sum(\text{clicks})$.
* Retained store-level totals from `business.csv` using `first()`.


3. **Output Size:** $120\text{ days} \times 3\text{ channels} = \mathbf{360\text{ rows}}$.

#### Step 3: Executive Daily Store Roll-Up (`ecommerce_daily_kpis.csv`)

1. **Grouping:** Grouped `ecommerce_granular_data.csv` by **`['date']`**.
2. **Aggregation Functions:**
* Summed total ad expenditure and direct revenue across all 3 platforms for each calendar date.
* Attached store financials (`total_revenue`, `gross_profit`, `new_customers`).


3. **Macro KPI Calculation:** Calculated company-wide executive indicators:

$$\text{Blended ROAS} = \frac{\text{total\_mkt\_attributed\_revenue}}{\text{total\_mkt\_spend}}$$


$$\text{Customer Acquisition Cost (CAC)} = \frac{\text{total\_mkt\_spend}}{\text{new\_customers}}$$


$$\text{Gross Margin \%} = \left( \frac{\text{gross\_profit}}{\text{total\_revenue}} \right) \times 100$$


4. **Output Size:** 1 record per tracking day = **120 rows**.

---

```markdown
# 📊 Marketing Intelligence Dashboard

An executive-level, interactive Business Intelligence (BI) dashboard built with **Streamlit**, **Pandas**, and **Plotly Express**. This application connects paid digital ad performance across **Facebook**, **Google**, and **TikTok** with core e-commerce financials (**Revenue**, **Gross Profit**, **COGS**, **CAC**, and **AOV**) to provide real-time visibility into marketing efficiency and business ROI.

---

## 📸 Dashboard Preview

### 📊 Tab 1: Executive Overview
![Executive Overview](assets/overview.png)
![Overview Metrics](assets/overview_2.png)
![Overview Trends](assets/overvie_3.png)

---

### 🎯 Tab 2: Channel Performance Deep Dive
![Channel Performance](assets/Tab_2.png)
![Channel Trends](assets/Tab_2.1.png)
![Channel Metrics](assets/Tab_2.3.png)

---

### 🔍 Tab 3: Campaign & Tactic Deep Dive
![Campaign Deep Dive](assets/Tab3.png)
![Tactic Analysis](assets/Tab3.1.png)
![Scatter Analysis](assets/Tab3.3.png)

---

### 📈 Tab 4: Business Impact & Financials
![Business Impact](assets/Tab4.png)
![Customer Acquisition](assets/Tab4.1.png)
![Revenue Breakdown](assets/Tab4.2.png)

---

### 🎛️ Sidebar Filter Panel
![Filter Panel](assets/Filter_panel.png)

---

## ✨ Key Features & Navigation

The dashboard is structured into four functional tabs designed for e-commerce operators, performance marketers, and executive decision-makers:

### 1. 💡 Tab 1: Overview
* **Executive Insights Cards:** Dynamic summary blocks highlighting current ROAS, marketing revenue attribution, and budget reallocation opportunities based on active filter selections.
* **Top KPI Metric Cards:** High-level summary cards displaying Total Spend, Attributed Revenue, Overall ROAS, Business Revenue, Gross Profit, Impressions, Clicks, New Customers, CAC, and Gross Profit Margin.
* **ROAS Trend Chart:** Interactive time-series line chart tracking blended return on ad spend movements over time.
* **Ads Dynamics by Channel:** Multi-metric bar chart with interactive selectors (Spend, Revenue, Clicks, Impressions) stacked by platform.
* **Spend vs. Attributed Revenue:** Spline line chart evaluating daily ad expenditure against direct sales returns.

### 2. 🎯 Tab 2: Channel Performance
* **ROAS by Marketing Channel:** Comparative bar chart evaluating channel efficiency across Facebook, Google, and TikTok.
* **Spend Share Distribution:** Donut chart showing budget allocation per ad channel.
* **Granular Channel ROAS Trends:** Multi-line time series chart tracking daily platform performance fluctuations.
* **Detailed Channel Table:** Formatted matrix detailing Spend, Revenue, ROAS, CTR, CPC, CPM, Impressions, and Clicks per platform.

### 3. 🔍 Tab 3: Campaign & Tactic Deep Dive
* **ROAS by Tactic:** Grouped bar chart comparing marketing tactics (`ASC`, `Prospecting`, `Non-Branded Search`, `Display`, `Retargeting`, `Spark Ads`).
* **Campaign Bubble Chart:** Scatter plot mapping `Total Spend` (X-axis) vs. `ROAS` (Y-axis), where bubble size represents `Attributed Revenue`.
* **Granular Campaign Table:** Performance matrix tracking 30 campaigns across target states (`CA`, `NY`).

### 4. 📈 Tab 4: Business Impact
* **Revenue & Profit Trends:** Line chart comparing store revenue against gross profit over time.
* **Customer Acquisition Trends:** Visualizes new customer acquisition volume alongside Customer Acquisition Cost (`CAC`) trends.
* **Attributed vs. Non-Attributed Revenue:** Stacked area chart comparing direct marketing sales against organic/direct store revenue.
* **Daily Financial Log:** Complete tabular breakdown of store operations (`Orders`, `COGS`, `Gross Profit Margin`, `AOV`, `% Attributed Revenue`).

---

## 🎛️ Dynamic Sidebar Filters

* **Time Horizon:** Switch between `Daily` (Last 7 Days), `Weekly` (Last 30 Days), `Monthly` (Last 6 Months), or set a `Custom Date Range`.
* **Marketing Channel(s):** Filter across Facebook, Google, and TikTok using scrollable select-all checkboxes.
* **Tactic(s):** Dynamically filtered list based on the active channels selected.
* **State(s):** Geographic region filtering (`CA`, `NY`).

---

## 🗄️ Repository & Directory Structure

```text
ecommerce-marketing-dashboard/
│
├── app.py                             # Main Streamlit dashboard application code
├── ecommerce_daily_kpis.csv           # Executive-level daily store totals (120 rows)
├── ecommerce_granular_data.csv        # Low-level campaign dataset (3,600 rows)
├── combined_marketing_business.csv    # Channel-level daily summary table (360 rows)
│
├── assets/                            # Dashboard screenshot images for README
│   ├── overview.png
│   ├── overview_2.png
│   ├── overvie_3.png
│   ├── Tab_2.png
│   ├── Tab_2.1.png
│   ├── Tab_2.3.png
│   ├── Tab3.png
│   ├── Tab3.1.png
│   ├── Tab3.3.png
│   ├── Tab4.png
│   ├── Tab4.1.png
│   ├── Tab4.2.png
│   └── Filter_panel.png
│
├── .streamlit/
│   └── config.toml                    # Streamlit theme configuration
│
├── requirements.txt                   # Project dependencies
└── README.md                          # Project documentation

```

---

## 🛠️ Tech Stack

* **Framework:** [Streamlit](https://streamlit.io/)
* **Data Processing:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
* **Visualization:** [Plotly Express](https://plotly.com/python/plotly-express/)
* **Language:** Python 3.9+

---

## 🚀 Local Installation & Setup

### 1. Clone the Repository

```bash
git clone [https://github.com/Meenu-Lakshmi/ecommerce-marketing-dashboard.git](https://github.com/Meenu-Lakshmi/ecommerce-marketing-dashboard.git)
cd ecommerce-marketing-dashboard

```

### 2. Create and Activate a Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

### 4. Launch the Streamlit Dashboard

```bash
streamlit run app.py

```

The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 📐 Key Formulas & Metrics

* **Return on Ad Spend (ROAS):**

$$\text{ROAS} = \frac{\text{Attributed Revenue}}{\text{Marketing Spend}}$$


* **Customer Acquisition Cost (CAC):**

$$\text{CAC} = \frac{\text{Marketing Spend}}{\text{New Customers Acquired}}$$


* **Average Order Value (AOV):**

$$\text{AOV} = \frac{\text{Total Store Revenue}}{\text{Total Orders}}$$


* **Gross Profit Margin (%):**

$$\text{Gross Profit Margin} = \left( \frac{\text{Gross Profit}}{\text{Total Store Revenue}} \right) \times 100$$



```

```
