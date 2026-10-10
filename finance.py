"""Core financial logic: statement models and ratio calculations."""

from dataclasses import dataclass


# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------
@dataclass
class IncomeStatement:
    revenue: float
    cogs: float
    selling_admin: float
    depreciation: float
    other_operating: float
    other_income: float
    interest_expense: float
    tax_rate: float  # percent, e.g. 30 for 30%
    shares_outstanding: float = 0.0

    @property
    def gross_profit(self):
        return self.revenue - self.cogs

    @property
    def total_operating_expenses(self):
        return self.selling_admin + self.depreciation + self.other_operating

    @property
    def operating_income(self):  # EBIT
        return self.gross_profit - self.total_operating_expenses

    @property
    def pretax_income(self):
        return self.operating_income + self.other_income - self.interest_expense

    @property
    def tax_expense(self):
        # No tax benefit is booked on a loss.
        return max(self.pretax_income, 0) * self.tax_rate / 100

    @property
    def net_income(self):
        return self.pretax_income - self.tax_expense

    @property
    def eps(self):
        return self.net_income / self.shares_outstanding if self.shares_outstanding else None


@dataclass
class BalanceSheet:
    # Current assets
    cash: float
    receivables: float
    inventory: float
    other_current_assets: float
    # Non-current assets
    ppe_net: float
    intangibles: float
    other_noncurrent_assets: float
    # Current liabilities
    payables: float
    short_term_debt: float
    other_current_liabilities: float
    # Non-current liabilities
    long_term_debt: float
    other_noncurrent_liabilities: float
    # Equity
    share_capital: float
    retained_earnings: float

    @property
    def total_current_assets(self):
        return self.cash + self.receivables + self.inventory + self.other_current_assets

    @property
    def total_noncurrent_assets(self):
        return self.ppe_net + self.intangibles + self.other_noncurrent_assets

    @property
    def total_assets(self):
        return self.total_current_assets + self.total_noncurrent_assets

    @property
    def total_current_liabilities(self):
        return self.payables + self.short_term_debt + self.other_current_liabilities

    @property
    def total_noncurrent_liabilities(self):
        return self.long_term_debt + self.other_noncurrent_liabilities

    @property
    def total_liabilities(self):
        return self.total_current_liabilities + self.total_noncurrent_liabilities

    @property
    def total_equity(self):
        return self.share_capital + self.retained_earnings

    @property
    def total_liabilities_and_equity(self):
        return self.total_liabilities + self.total_equity

    @property
    def total_debt(self):
        return self.short_term_debt + self.long_term_debt

    @property
    def imbalance(self):
        return self.total_assets - self.total_liabilities_and_equity


# --------------------------------------------------------------------------
# Formatting
# --------------------------------------------------------------------------
def money(value, cur="$"):
    """Thousands separators; negatives in parentheses."""
    text = f"{cur}{abs(value):,.2f}"
    return f"({text})" if value < 0 else text


def fmt_ratio(value, kind, cur="$"):
    if value is None:
        return "n/a"
    if kind == "pct":
        return f"{value * 100:,.2f}%"
    if kind == "x":
        return f"{value:,.2f}x"
    if kind == "days":
        return f"{value:,.1f} days"
    if kind == "money":
        return money(value, cur)
    return f"{value:,.2f}"


# --------------------------------------------------------------------------
# Ratios
# --------------------------------------------------------------------------
def safe_div(num, den):
    return num / den if den else None


def compute_ratios(inc, bs):
    """Return {group: [(name, value, kind, formula), ...]}."""
    r = {}
    r["Liquidity"] = [
        ("Current ratio", safe_div(bs.total_current_assets, bs.total_current_liabilities), "x",
         "Current assets / current liabilities"),
        ("Quick ratio", safe_div(bs.total_current_assets - bs.inventory, bs.total_current_liabilities), "x",
         "(Current assets - inventory) / current liabilities"),
        ("Cash ratio", safe_div(bs.cash, bs.total_current_liabilities), "x",
         "Cash / current liabilities"),
        ("Working capital", bs.total_current_assets - bs.total_current_liabilities, "money",
         "Current assets - current liabilities"),
    ]
    r["Profitability"] = [
        ("Gross profit margin", safe_div(inc.gross_profit, inc.revenue), "pct", "Gross profit / revenue"),
        ("Operating margin", safe_div(inc.operating_income, inc.revenue), "pct", "EBIT / revenue"),
        ("Net profit margin", safe_div(inc.net_income, inc.revenue), "pct", "Net income / revenue"),
        ("Return on assets (ROA)", safe_div(inc.net_income, bs.total_assets), "pct",
         "Net income / total assets"),
        ("Return on equity (ROE)", safe_div(inc.net_income, bs.total_equity), "pct",
         "Net income / total equity"),
    ]
    r["Leverage / Solvency"] = [
        ("Debt ratio", safe_div(bs.total_liabilities, bs.total_assets), "pct",
         "Total liabilities / total assets"),
        ("Debt-to-equity", safe_div(bs.total_liabilities, bs.total_equity), "x",
         "Total liabilities / total equity"),
        ("Interest-bearing debt / equity", safe_div(bs.total_debt, bs.total_equity), "x",
         "(Short + long-term debt) / total equity"),
        ("Equity multiplier", safe_div(bs.total_assets, bs.total_equity), "x",
         "Total assets / total equity"),
        ("Interest coverage", safe_div(inc.operating_income, inc.interest_expense), "x",
         "EBIT / interest expense"),
    ]
    inv_turn = safe_div(inc.cogs, bs.inventory)
    rec_turn = safe_div(inc.revenue, bs.receivables)
    pay_turn = safe_div(inc.cogs, bs.payables)
    dio = safe_div(365, inv_turn)
    dso = safe_div(365, rec_turn)
    dpo = safe_div(365, pay_turn)
    ccc = (dio + dso - dpo) if None not in (dio, dso, dpo) else None
    r["Efficiency"] = [
        ("Asset turnover", safe_div(inc.revenue, bs.total_assets), "x", "Revenue / total assets"),
        ("Inventory turnover", inv_turn, "x", "COGS / inventory"),
        ("Receivables turnover", rec_turn, "x", "Revenue / accounts receivable"),
        ("Days inventory outstanding", dio, "days", "365 / inventory turnover"),
        ("Days sales outstanding", dso, "days", "365 / receivables turnover"),
        ("Days payables outstanding", dpo, "days", "365 / (COGS / payables)"),
        ("Cash conversion cycle", ccc, "days", "DIO + DSO - DPO"),
    ]
    return r
