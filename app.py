import streamlit as st
import pandas as pd
import altair as alt

# ---------------------------
#  Global Settings
# ---------------------------

CURRENCY_SYMBOL = "PKR"

st.set_page_config(
    page_title="Bridge Financing Calculator",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Minimal, safe CSS
st.markdown(
    """
    <style>
    html, body, [class*="css"], .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif !important;
        color: #111111 !important;
    }

    .stApp {
        background-color: #f5f5f5 !important;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        margin: 0 auto;
    }

    h1 {
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #111111 !important;
        margin-bottom: 0.3rem;
    }

    .subtitle {
        font-size: 0.98rem;
        color: #4b5563;
        margin-bottom: 1.8rem;
    }

    label, div[data-testid="stWidgetLabel"] p {
        color: #111111 !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
    }

    div[data-baseweb="input"] input {
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        caret-color: #111111 !important;
        background-color: #ffffff !important;
        border-radius: 4px !important;
        border: 1px solid #d1d5db !important;
        padding: 0.35rem 0.5rem !important;
        font-size: 0.9rem !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #111111 !important;
        box-shadow: none !important;
    }

    /* hide +/- steppers so boxes look like plain numeric fields */
    div[data-testid="stNumberInput"] button {
        display: none !important;
    }

    .section-title {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #4b5563;
        margin-bottom: 0.75rem;
    }

    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #6b7280;
        margin-bottom: 0.35rem;
    }

    .metric-value {
        font-size: 1.6rem;
        font-weight: 600;
        margin-bottom: 0.1rem;
    }

    .metric-value.positive { color: #16a34a; }   /* green */
    .metric-value.negative { color: #dc2626; }   /* red */
    .metric-value.neutral  { color: #2563eb; }   /* blue */

    .metric-sub {
        font-size: 0.9rem;
        color: #4b5563;
    }

    /* custom table for breakdown */
    table.bf-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
        margin-top: 0.4rem;
    }
    .bf-table th {
        text-align: left;
        padding: 6px 4px;
        border-bottom: 1px solid #e5e7eb;
        color: #374151;
        font-weight: 600;
    }
    .bf-table td {
        padding: 6px 4px;
        border-bottom: 1px solid #f3f4f6;
        color: #111111;
    }
    .bf-table tr:last-child td {
        border-bottom: none;
    }

    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
#  Calculation Function
# ---------------------------

def calculate_bridge_financing(
    annual_interest_rate_pct: float,
    invoice_amount: float,
    days_outstanding: int,
    margin_pct: float,
    advance_rate_pct: float = 80.0,
    arrangement_fee_pct: float = 0.0,
    fixed_fee: float = 0.0,
) -> dict:
    """Calculate the economics of bridge financing against an invoice."""

    annual_rate = annual_interest_rate_pct / 100.0
    margin_rate = margin_pct / 100.0
    advance_rate = advance_rate_pct / 100.0
    arrangement_fee_rate = arrangement_fee_pct / 100.0

    principal_borrowed = invoice_amount * advance_rate
    gross_margin_value = invoice_amount * margin_rate

    if days_outstanding <= 0:
        interest_cost = 0.0
    else:
        interest_cost = principal_borrowed * annual_rate * (days_outstanding / 365.0)

    arrangement_fee_value = invoice_amount * arrangement_fee_rate
    total_fees = arrangement_fee_value + fixed_fee

    total_financing_cost = interest_cost + total_fees
    net_margin_after_financing = gross_margin_value - total_financing_cost

    margin_eaten_value = total_financing_cost
    margin_eaten_pct_of_margin = (
        (margin_eaten_value / gross_margin_value) * 100.0 if gross_margin_value > 0 else 0.0
    )

    financing_cost_pct_of_invoice = (total_financing_cost / invoice_amount) * 100.0

    if days_outstanding > 0:
        effective_annualized_cost_pct = financing_cost_pct_of_invoice * (365.0 / days_outstanding)
    else:
        effective_annualized_cost_pct = 0.0

    return {
        "invoice_amount": invoice_amount,
        "annual_interest_rate_pct": annual_interest_rate_pct,
        "days_outstanding": days_outstanding,
        "margin_pct": margin_pct,
        "advance_rate_pct": advance_rate_pct,
        "arrangement_fee_pct": arrangement_fee_pct,
        "fixed_fee": fixed_fee,
        "principal_borrowed": principal_borrowed,
        "gross_margin_value": gross_margin_value,
        "interest_cost": interest_cost,
        "total_fees": total_fees,
        "total_financing_cost": total_financing_cost,
        "net_margin_after_financing": net_margin_after_financing,
        "margin_eaten_value": margin_eaten_value,
        "margin_eaten_pct_of_margin": margin_eaten_pct_of_margin,
        "financing_cost_pct_of_invoice": financing_cost_pct_of_invoice,
        "effective_annualized_cost_pct": effective_annualized_cost_pct,
    }


# ===========================
#  LAYOUT
# ===========================

st.title("Bridge Financing Calculator")
st.markdown(
    '<div class="subtitle">Analyze the impact of short-term financing costs on your deal margins.</div>',
    unsafe_allow_html=True,
)

# ---------- Inputs ----------
with st.container(border=True):
    st.markdown('<div class="section-title">Deal parameters</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        invoice_amount = st.number_input(
            f"Invoice amount ({CURRENCY_SYMBOL})",
            min_value=0.0,
            value=10000.0,
            step=1000.0,
            format="%.2f",
        )
        days_outstanding = st.number_input(
            "Days outstanding",
            min_value=1,
            value=60,
            step=1,
        )

    with c2:
        margin_pct = st.number_input(
            "Gross margin (%)",
            min_value=0.0,
            value=25.0,
            step=0.5,
            format="%.2f",
        )
        advance_rate_pct = st.number_input(
            "Advance rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=80.0,
            step=1.0,
            format="%.2f",
        )

    with c3:
        annual_interest_rate_pct = st.number_input(
            "Annual interest rate (%)",
            min_value=0.0,
            value=18.0,
            step=0.25,
            format="%.2f",
        )
        arrangement_fee_pct = st.number_input(
            "Arrangement fee (%)",
            min_value=0.0,
            value=1.0,
            step=0.1,
            format="%.2f",
        )

    fixed_fee = st.number_input(
        f"Fixed fees ({CURRENCY_SYMBOL})",
        min_value=0.0,
        value=0.0,
        step=100.0,
        format="%.2f",
    )

st.markdown("")

# ---------- Outputs ----------
if invoice_amount <= 0:
    st.info(f"Enter a positive invoice amount ({CURRENCY_SYMBOL}) to generate calculations.")
else:
    result = calculate_bridge_financing(
        annual_interest_rate_pct=annual_interest_rate_pct,
        invoice_amount=invoice_amount,
        days_outstanding=int(days_outstanding),
        margin_pct=margin_pct,
        advance_rate_pct=advance_rate_pct,
        arrangement_fee_pct=arrangement_fee_pct,
        fixed_fee=fixed_fee,
    )

    gross_margin = result["gross_margin_value"]
    net_margin = result["net_margin_after_financing"]
    margin_eaten_val = result["margin_eaten_value"]
    margin_eaten_pct = result["margin_eaten_pct_of_margin"]

    # --- Summary box ---
    with st.container(border=True):
        st.markdown('<div class="section-title">Summary</div>', unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.markdown('<div class="metric-label">Net margin (after financing)</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="metric-value positive">{CURRENCY_SYMBOL} {net_margin:,.0f}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="metric-sub">Gross margin: {CURRENCY_SYMBOL} {gross_margin:,.0f}</div>',
                unsafe_allow_html=True,
            )

        with k2:
            st.markdown('<div class="metric-label">Cost of financing</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="metric-value negative">{CURRENCY_SYMBOL} {margin_eaten_val:,.0f}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="metric-sub">Interest: {CURRENCY_SYMBOL} {result["interest_cost"]:,.0f} '
                f'| Fees: {CURRENCY_SYMBOL} {result["total_fees"]:,.0f}</div>',
                unsafe_allow_html=True,
            )

        with k3:
            st.markdown('<div class="metric-label">Margin erosion</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="metric-value negative">{margin_eaten_pct:.1f}%</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="metric-sub">Percentage of gross margin lost to financing</div>',
                unsafe_allow_html=True,
            )

        with k4:
            st.markdown('<div class="metric-label">Effective annualized cost</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="metric-value neutral">{result["effective_annualized_cost_pct"]:.2f}%</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="metric-sub">Based on {int(days_outstanding)} days outstanding</div>',
                unsafe_allow_html=True,
            )

    st.markdown("")

    # --- Chart + Breakdown ---
    col_chart, col_table = st.columns([1.4, 1])

    with col_chart:
        with st.container(border=True):
            st.markdown('<div class="section-title">Margin before and after financing</div>', unsafe_allow_html=True)

            chart_data = pd.DataFrame(
                [
                    {"Category": "Gross margin", "Amount": gross_margin, "Type": "Initial"},
                    {"Category": "Financing cost", "Amount": margin_eaten_val, "Type": "Cost"},
                    {"Category": "Net margin", "Amount": net_margin, "Type": "Final"},
                ]
            )

            chart = (
                alt.Chart(chart_data)
                .mark_bar(size=40)
                .encode(
                    x=alt.X(
                        "Category",
                        sort=["Gross margin", "Financing cost", "Net margin"],
                        axis=alt.Axis(labelAngle=0, title=None, grid=False),
                    ),
                    y=alt.Y(
                        "Amount",
                        axis=alt.Axis(format=",", title=f"Amount ({CURRENCY_SYMBOL})", grid=True),
                    ),
                    color=alt.Color(
                        "Type",
                        scale=alt.Scale(
                            domain=["Initial", "Cost", "Final"],
                            range=["#9ca3af", "#ef4444", "#10b981"],
                        ),
                        legend=None,
                    ),
                    tooltip=[
                        "Category",
                        alt.Tooltip("Amount", format=",.2f", title=f"Amount ({CURRENCY_SYMBOL})"),
                    ],
                )
                .properties(height=280, background="transparent")
                .configure_view(strokeWidth=0)
                .configure_axis(
                    labelColor="#111111",
                    titleColor="#111111",
                    gridColor="#e5e7eb",
                )
            )

            st.altair_chart(chart, use_container_width=True)

    with col_table:
        with st.container(border=True):
            st.markdown('<div class="section-title">Detailed breakdown</div>', unsafe_allow_html=True)

            breakdown_df = pd.DataFrame(
                {
                    "Metric": [
                        "Principal borrowed",
                        "Interest cost",
                        "Arrangement + fixed fees",
                        "Total financing cost",
                        "Financing cost (% of invoice)",
                    ],
                    "Value": [
                        f"{CURRENCY_SYMBOL} {result['principal_borrowed']:,.2f}",
                        f"{CURRENCY_SYMBOL} {result['interest_cost']:,.2f}",
                        f"{CURRENCY_SYMBOL} {result['total_fees']:,.2f}",
                        f"{CURRENCY_SYMBOL} {result['total_financing_cost']:,.2f}",
                        f"{result['financing_cost_pct_of_invoice']:.2f}%",
                    ],
                }
            )

            html_table = breakdown_df.to_html(index=False, classes="bf-table", border=0)
            st.markdown(html_table, unsafe_allow_html=True)
