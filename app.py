"""Financial Statements & Ratio Analyzer - Streamlit app (blue & gold theme)."""

import pandas as pd
import streamlit as st

from finance import BalanceSheet, IncomeStatement, compute_ratios, fmt_ratio, money

NAVY = "#0B2A5B"
BLUE = "#1D4ED8"
LIGHT_BLUE = "#EEF3FB"
GOLD = "#C9A227"
LIGHT_GOLD = "#FBF4DC"

st.set_page_config(page_title="Financial Statements Analyzer", page_icon="📊", layout="wide")

# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------
st.markdown(
    f"""
<style>
.block-container {{ padding-top: 1.5rem; max-width: 1200px; }}
.hero {{
    background: linear-gradient(135deg, {NAVY} 0%, {BLUE} 100%);
    border-bottom: 5px solid {GOLD};
    border-radius: 12px; padding: 1.6rem 2rem; margin-bottom: 1.2rem;
}}
.hero h1 {{ color: #fff; margin: 0; font-size: 2rem; }}
.hero p  {{ color: {GOLD}; margin: .3rem 0 0 0; font-weight: 600; letter-spacing: .5px; }}
h2, h3 {{ color: {NAVY}; }}
div[data-testid="stMetric"] {{
    background: {LIGHT_BLUE}; border-left: 5px solid {GOLD};
    border-radius: 8px; padding: .8rem 1rem;
}}
div[data-testid="stMetricValue"] {{ color: {NAVY}; }}
div[data-testid="stMetricLabel"] p {{ color: {BLUE}; font-weight: 600; }}
button[data-baseweb="tab"] {{ font-weight: 600; }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: {NAVY}; }}
div[data-baseweb="tab-highlight"] {{ background-color: {GOLD} !important; }}
section[data-testid="stSidebar"] {{ background: {NAVY}; }}
section[data-testid="stSidebar"] * {{ color: #fff !important; }}
section[data-testid="stSidebar"] input {{ color: {NAVY} !important; }}
section[data-testid="stSidebar"] button, section[data-testid="stSidebar"] button * {{ color: {NAVY} !important; }}
section[data-testid="stSidebar"] button {{ border: 1px solid {GOLD}; }}
section[data-testid="stSidebar"] hr {{ border-color: {GOLD}; }}

table.stmt {{ width: 100%; border-collapse: collapse; font-size: 0.97rem; }}
table.stmt td {{ padding: .38rem .8rem; }}
table.stmt td.num {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
table.stmt tr.title td {{
    background: {NAVY}; color: #fff; text-align: center; padding: .9rem;
    font-size: 1.15rem; font-weight: 700; border-bottom: 3px solid {GOLD};
}}
table.stmt tr.sub td {{ background: {NAVY}; color: {GOLD}; text-align: center; font-size: .9rem; padding: .4rem; }}
table.stmt tr.section td {{ background: {LIGHT_BLUE}; color: {BLUE}; font-weight: 700; letter-spacing: .5px; }}
table.stmt tr.item td {{ color: #222; border-bottom: 1px solid #e4e9f2; }}
table.stmt tr.item td:first-child {{ padding-left: 2rem; }}
table.stmt tr.total td {{ font-weight: 700; color: {NAVY}; border-top: 1px solid {NAVY}; background: #f8faff; }}
table.stmt tr.grand td {{
    font-weight: 800; color: {NAVY}; background: {LIGHT_GOLD};
    border-top: 2px solid {GOLD}; border-bottom: 3px double {GOLD};
}}
table.ratio {{ width: 100%; border-collapse: collapse; margin-bottom: 1rem; }}
table.ratio th {{ background: {NAVY}; color: {GOLD}; text-align: left; padding: .5rem .8rem; }}
table.ratio td {{ padding: .45rem .8rem; border-bottom: 1px solid #e4e9f2; }}
table.ratio td.val {{ font-weight: 700; color: {BLUE}; text-align: right; white-space: nowrap; }}
table.ratio td.formula {{ color: #667; font-size: .88rem; }}
</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Input definitions & session state
# --------------------------------------------------------------------------
INCOME_FIELDS = [
    ("revenue", "Net sales / revenue"),
    ("cogs", "Cost of goods sold"),
    ("selling_admin", "Selling, general & admin expenses"),
    ("depreciation", "Depreciation & amortization"),
    ("other_operating", "Other operating expenses"),
    ("other_income", "Other income (non-operating)"),
    ("interest_expense", "Interest expense"),
]
ASSET_FIELDS = [
    ("cash", "Cash & equivalents"),
    ("receivables", "Accounts receivable"),
    ("inventory", "Inventory"),
    ("other_current_assets", "Other current assets"),
    ("ppe_net", "Property, plant & equipment (net)"),
    ("intangibles", "Intangible assets"),
    ("other_noncurrent_assets", "Other non-current assets"),
]
LIAB_FIELDS = [
    ("payables", "Accounts payable"),
    ("short_term_debt", "Short-term debt / current portion of LTD"),
    ("other_current_liabilities", "Other current liabilities"),
    ("long_term_debt", "Long-term debt"),
    ("other_noncurrent_liabilities", "Other non-current liabilities"),
]
EQUITY_FIELDS = [
    ("share_capital", "Share capital (incl. share premium)"),
    ("retained_earnings", "Retained earnings (can be negative)"),
]
ALL_KEYS = [k for k, _ in INCOME_FIELDS + ASSET_FIELDS + LIAB_FIELDS + EQUITY_FIELDS]

SAMPLE = dict(
    revenue=1_500_000, cogs=900_000, selling_admin=250_000, depreciation=50_000,
    other_operating=20_000, other_income=10_000, interest_expense=30_000,
    cash=120_000, receivables=180_000, inventory=200_000, other_current_assets=20_000,
    ppe_net=600_000, intangibles=50_000, other_noncurrent_assets=30_000,
    payables=130_000, short_term_debt=70_000, other_current_liabilities=30_000,
    long_term_debt=300_000, other_noncurrent_liabilities=20_000,
    share_capital=400_000, retained_earnings=250_000,
    tax_rate=30.0, shares=100_000.0,
)

for k in ALL_KEYS:
    st.session_state.setdefault(k, 0.0)
st.session_state.setdefault("tax_rate", 30.0)
st.session_state.setdefault("shares", 0.0)
st.session_state.setdefault("company", "My Company")


def load_sample():
    for k, v in SAMPLE.items():
        st.session_state[k] = float(v)
    st.session_state["company"] = "Demo Company Ltd"


def clear_all():
    for k in ALL_KEYS:
        st.session_state[k] = 0.0
    st.session_state["shares"] = 0.0


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Company details")
    company = st.text_input("Company name", key="company")
    period = st.text_input("Income statement period", value="Year ended 31 Dec 2025")
    as_at = st.text_input("Balance sheet date", value="31 Dec 2025")
    cur = st.text_input("Currency symbol", value="$", max_chars=4)
    st.markdown("---")
    st.number_input("Income tax rate (%)", min_value=0.0, max_value=100.0, step=1.0, key="tax_rate")
    st.number_input("Shares outstanding (0 skips EPS)", min_value=0.0, step=1000.0, key="shares")
    st.markdown("---")
    st.button("Load sample data", on_click=load_sample, use_container_width=True)
    st.button("Clear all inputs", on_click=clear_all, use_container_width=True)

st.markdown(
    '<div class="hero"><h1>Financial Statements Analyzer</h1>'
    "<p>Income statement · Balance sheet · Financial ratios</p></div>",
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# Build models from state
# --------------------------------------------------------------------------
def val(key):
    return float(st.session_state[key])


def build_models():
    inc = IncomeStatement(
        revenue=val("revenue"), cogs=val("cogs"), selling_admin=val("selling_admin"),
        depreciation=val("depreciation"), other_operating=val("other_operating"),
        other_income=val("other_income"), interest_expense=val("interest_expense"),
        tax_rate=val("tax_rate"), shares_outstanding=val("shares"),
    )
    bs = BalanceSheet(**{k: val(k) for k, _ in ASSET_FIELDS + LIAB_FIELDS + EQUITY_FIELDS})
    return inc, bs


# --------------------------------------------------------------------------
# HTML helpers
# --------------------------------------------------------------------------
def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def statement_html(title, subtitle, rows, cur):
    out = [
        '<table class="stmt">',
        f'<tr class="title"><td colspan="2">{esc(title)}</td></tr>',
        f'<tr class="sub"><td colspan="2">{esc(subtitle)}</td></tr>',
    ]
    for kind, label, value in rows:
        if kind == "section":
            out.append(f'<tr class="section"><td colspan="2">{esc(label)}</td></tr>')
        else:
            out.append(
                f'<tr class="{kind}"><td>{esc(label)}</td><td class="num">{money(value, cur)}</td></tr>'
            )
    out.append("</table>")
    return "".join(out)


def ratio_html(items, cur):
    out = ['<table class="ratio"><tr><th>Ratio</th><th style="text-align:right">Value</th><th>Formula</th></tr>']
    for name, value, kind, formula in items:
        out.append(
            f'<tr><td>{esc(name)}</td><td class="val">{esc(fmt_ratio(value, kind, cur))}</td>'
            f'<td class="formula">{esc(formula)}</td></tr>'
        )
    out.append("</table>")
    return "".join(out)


# --------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------
tab_in, tab_is, tab_bs, tab_ratio = st.tabs(
    ["📝 Inputs", "📈 Income Statement", "🏦 Balance Sheet", "🧮 Ratios"]
)

with tab_in:
    st.caption("Enter every amount as a positive number, expenses included. Use 'Load sample data' in the sidebar to see how it works.")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Income statement")
        for key, label in INCOME_FIELDS:
            st.number_input(label, min_value=0.0, step=1000.0, format="%.2f", key=key)
    with c2:
        st.subheader("Balance sheet")
        st.markdown(f"**Assets**")
        for key, label in ASSET_FIELDS:
            st.number_input(label, min_value=0.0, step=1000.0, format="%.2f", key=key)
        st.markdown("**Liabilities**")
        for key, label in LIAB_FIELDS:
            st.number_input(label, min_value=0.0, step=1000.0, format="%.2f", key=key)
        st.markdown("**Shareholders' equity**")
        st.number_input(EQUITY_FIELDS[0][1], min_value=0.0, step=1000.0, format="%.2f", key="share_capital")
        st.number_input(EQUITY_FIELDS[1][1], step=1000.0, format="%.2f", key="retained_earnings")

inc, bs = build_models()
ratios = compute_ratios(inc, bs)

with tab_is:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Revenue", money(inc.revenue, cur))
    m2.metric("Gross profit", money(inc.gross_profit, cur))
    m3.metric("Operating income (EBIT)", money(inc.operating_income, cur))
    m4.metric("Net income", money(inc.net_income, cur))

    rows = [
        ("item", "Net sales / revenue", inc.revenue),
        ("item", "Cost of goods sold", -inc.cogs),
        ("total", "GROSS PROFIT", inc.gross_profit),
        ("section", "Operating expenses", None),
        ("item", "Selling, general & admin", inc.selling_admin),
        ("item", "Depreciation & amortization", inc.depreciation),
        ("item", "Other operating expenses", inc.other_operating),
        ("total", "Total operating expenses", -inc.total_operating_expenses),
        ("total", "OPERATING INCOME (EBIT)", inc.operating_income),
        ("section", "Non-operating items", None),
        ("item", "Other income", inc.other_income),
        ("item", "Interest expense", -inc.interest_expense),
        ("total", "INCOME BEFORE TAX", inc.pretax_income),
        ("item", f"Income tax ({inc.tax_rate:g}%)", -inc.tax_expense),
        ("grand", "NET INCOME", inc.net_income),
    ]
    if inc.eps is not None:
        rows.append(("item", "Earnings per share (EPS)", inc.eps))
    st.markdown(statement_html(company.upper(), f"INCOME STATEMENT · {period}", rows, cur), unsafe_allow_html=True)

    st.markdown("#### Profit breakdown")
    chart_df = pd.DataFrame(
        {
            "Amount": [inc.revenue, inc.gross_profit, inc.operating_income, inc.pretax_income, inc.net_income]
        },
        index=["Revenue", "Gross profit", "EBIT", "Pre-tax income", "Net income"],
    )
    st.bar_chart(chart_df, color=GOLD)

with tab_bs:
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Total assets", money(bs.total_assets, cur))
    b2.metric("Total liabilities", money(bs.total_liabilities, cur))
    b3.metric("Total equity", money(bs.total_equity, cur))
    b4.metric("Working capital", money(bs.total_current_assets - bs.total_current_liabilities, cur))

    rows = [
        ("section", "ASSETS - Current assets", None),
        ("item", "Cash & equivalents", bs.cash),
        ("item", "Accounts receivable", bs.receivables),
        ("item", "Inventory", bs.inventory),
        ("item", "Other current assets", bs.other_current_assets),
        ("total", "Total current assets", bs.total_current_assets),
        ("section", "ASSETS - Non-current assets", None),
        ("item", "Property, plant & equipment (net)", bs.ppe_net),
        ("item", "Intangible assets", bs.intangibles),
        ("item", "Other non-current assets", bs.other_noncurrent_assets),
        ("total", "Total non-current assets", bs.total_noncurrent_assets),
        ("grand", "TOTAL ASSETS", bs.total_assets),
        ("section", "LIABILITIES - Current liabilities", None),
        ("item", "Accounts payable", bs.payables),
        ("item", "Short-term debt", bs.short_term_debt),
        ("item", "Other current liabilities", bs.other_current_liabilities),
        ("total", "Total current liabilities", bs.total_current_liabilities),
        ("section", "LIABILITIES - Non-current liabilities", None),
        ("item", "Long-term debt", bs.long_term_debt),
        ("item", "Other non-current liabilities", bs.other_noncurrent_liabilities),
        ("total", "Total non-current liabilities", bs.total_noncurrent_liabilities),
        ("total", "TOTAL LIABILITIES", bs.total_liabilities),
        ("section", "SHAREHOLDERS' EQUITY", None),
        ("item", "Share capital", bs.share_capital),
        ("item", "Retained earnings", bs.retained_earnings),
        ("total", "TOTAL EQUITY", bs.total_equity),
        ("grand", "TOTAL LIABILITIES & EQUITY", bs.total_liabilities_and_equity),
    ]
    st.markdown(statement_html(company.upper(), f"BALANCE SHEET · As at {as_at}", rows, cur), unsafe_allow_html=True)

    st.write("")
    if abs(bs.imbalance) < 0.005:
        st.success("Balance sheet balances: Assets = Liabilities + Equity.")
    else:
        st.error(
            f"Balance sheet is out of balance by {money(bs.imbalance, cur)}. "
            "Assets minus (Liabilities + Equity) should be zero, so please re-check your inputs."
        )

    st.markdown("#### Capital structure")
    struct_df = pd.DataFrame(
        {"Amount": [bs.total_assets, bs.total_liabilities, bs.total_equity]},
        index=["Total assets", "Total liabilities", "Total equity"],
    )
    st.bar_chart(struct_df, color=BLUE)

with tab_ratio:
    d = {name: value for items in ratios.values() for name, value, _, _ in items}
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Current ratio", fmt_ratio(d["Current ratio"], "x"))
    r2.metric("Net profit margin", fmt_ratio(d["Net profit margin"], "pct"))
    r3.metric("Return on equity", fmt_ratio(d["Return on equity (ROE)"], "pct"))
    r4.metric("Debt-to-equity", fmt_ratio(d["Debt-to-equity"], "x"))

    st.caption(
        "Ratios use year-end balances (not averages). Turnover and day-count ratios assume "
        "the income statement covers 12 months."
    )
    for group, items in ratios.items():
        st.subheader(group)
        st.markdown(ratio_html(items, cur), unsafe_allow_html=True)

    export = pd.DataFrame(
        [
            {"Category": g, "Ratio": n, "Value": fmt_ratio(v, k, cur), "Formula": f}
            for g, items in ratios.items()
            for n, v, k, f in items
        ]
    )
    st.download_button(
        "Download ratios (CSV)",
        export.to_csv(index=False).encode("utf-8"),
        file_name=f"{company.replace(' ', '_')}_ratios.csv",
        mime="text/csv",
    )
