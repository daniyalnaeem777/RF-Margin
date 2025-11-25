import streamlit as st
import pandas as pd
import altair as alt

# ---------------------------
#  Core Calculation Function
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
    """
    Calculate the economics of bridge financing against an invoice.
    """

    # Convert percents to decimals
    annual_rate = annual_interest_rate_pct / 100.0
    margin_rate = margin_pct / 100.0
    advance_rate = advance_rate_pct / 100.0
    arrangement_fee_rate = arrangement_fee_pct / 100.0

    # Basic quantities
    principal_borrowed = invoice_amount * advance_rate           # Amount you actually borrow
    gross_margin_value = invoice_amount * margin_rate            # Profit before financing

    # Interest cost (simple interest for the bridge period)
    interest_cost = principal_borrowed * annual_rate * (days_outstanding / 365.0)

    # Up-front / additional fees
    arrangement_fee_value = invoice_amount * arrangement_fee_rate
    total_fees = arrangement_fee_value + fixed_fee

    # Total cost of financing
    total_financing_cost = interest_cost + total_fees

    # Margin after financing
    net_margin_after_financing = gross_margin_value - total_financing_cost

    # How much margin is eaten
    margin_eaten_value = total_financing_cost
    margin_eaten_pct_of_margin = (
        (margin_eaten_value / gross_margin_value) * 100.0
        if gross_margin_value > 0
        else 0.0
    )

    # Financing cost as % of invoice
    financing_cost_pct_of_invoice = (total_financing_cost / invoice_amount) * 100.0

    # Effective annualized cost on the invoice amount
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


# ---------------------------
#  Streamlit UI
# ---------------------------

st.set_page_config(
    page_title="Bridge Financing Margin Calculator",
    layout="wide",
)

# Global styling
st.markdown(
    """
    <style>
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
    }

    .stApp {
        background: #f3f4f6;
    }

    .main-block {
        max-width: 1150px;
        margin: 0 auto;
        padding-bottom: 3rem;
    }

    .app-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 650;
        color: #111827;
        margin-top: 1.5rem;
        margin-bottom: 0.4rem;
    }

    .app-subtitle {
        text-align: center;
        color: #4b5563;
        font-size: 0.96rem;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #6b7280;
        margin-bottom: 0.85rem;
        margin-top: 0.4rem;
    }

    .section-title-light {
        color: #d1d5db;
    }

    .card {
        padding: 1.4rem 1.5rem 1.1rem 1.5rem;
        border-radius: 14px;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 16px 36px rgba(15, 23, 42, 0.06);
    }

    .input-card {
        margin-bottom: 1.5rem;
    }

    .summary-wrapper {
        border-radius: 16px;
        padding: 1.6rem 1.5rem 1.4rem 1.5rem;
        background: #111827;
        box-shadow: 0 18px 40px rgba(0,0,0,0.35);
        margin-bottom: 2rem;
    }

    .summary-inner-card {
        padding: 1.1rem 1.2rem;
        border-radius: 12px;
        border: 1px solid #374151;
        background: #111827;
    }

    .metric-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #9ca3af;
        margin-bottom: 0.2rem;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #f9fafb;
    }

    .metric-sub {
        font-size: 0.84rem;
        color: #9ca3af;
        margin-top: 0.25rem;
    }

    /* Numeric inputs */
    label {
        color: #6b7280 !important;
        font-size: 0.85rem !important;
        margin-bottom: 0.15rem !important;
    }

    div[data-baseweb="input"] input {
        border-radius: 8px !important;
        border: 1px solid #d1d5db !important;
        background-color: #ffffff !important;
        padding: 0.38rem 0.55rem !important;
        font-size: 0.9rem !important;
    }

    div[data-baseweb="input"] input:focus {
        outline: none !important;
        border-color: #111827 !important;
        box-shadow: 0 0 0 1px #11182733 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-block">', unsafe_allow_html=True)

# Title centered
st.markdown('<div class="app-title">Bridge Financing Margin Calculator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">'
    'Quickly see how much of your margin is consumed by short-term bank financing on an invoice.'
    '</div>',
    unsafe_allow_html=True,
)

# ----------------
# Inputs inside one rectangular card
# ----------------

st.markdown('<div class="card input-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Inputs</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

with col1:
    invoice_amount = st.number_input(
        "Invoice amount",
        min_value=0.0,
        value=10000.0,
        step=1000.0,
        format="%.2f",
    )

with col2:
    margin_pct = st.number_input(
        "Gross margin on invoice (%)",
        min_value=0.0,
        value=25.0,
        step=0.5,
        format="%.2f",
    )

with col3:
    annual_interest_rate_pct = st.number_input(
        "Annual interest rate charged by bank (%)",
        min_value=0.0,
        value=18.0,
        step=0.25,
        format="%.2f",
    )

with col4:
    days_outstanding = st.number_input(
        "Days until repayment",
        min_value=1,
        value=60,
        step=1,
    )

with col5:
    advance_rate_pct = st.number_input(
        "Advance rate (% of invoice borrowed)",
        min_value=0.0,
        max_value=100.0,
        value=80.0,
        step=1.0,
        format="%.2f",
    )

with col6:
    arrangement_fee_pct = st.number_input(
        "Arrangement fee (% of invoice)",
        min_value=0.0,
        value=1.0,
        step=0.1,
        format="%.2f",
    )

st.markdown("")  # spacing
fixed_fee = st.number_input(
    "Fixed fees (legal / processing)",
    min_value=0.0,
    value=0.0,
    step=100.0,
    format="%.2f",
)

st.markdown('</div>', unsafe_allow_html=True)  # close input card

st.markdown("")  # small gap

# ----------------
# Calculations & Results
# ----------------

if invoice_amount <= 0:
    st.warning("Enter a positive invoice amount to see the financing impact.")
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
    margin_eaten_pct_of_margin = result["margin_eaten_pct_of_margin"]
    financing_cost_pct_of_invoice = result["financing_cost_pct_of_invoice"]
    effective_annualized_cost_pct = result["effective_annualized_cost_pct"]

    # ---- Summary in a black box ----
    st.markdown('<div class="summary-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="section-title section-title-light">Summary</div>', unsafe_allow_html=True)

    top1, top2, top3 = st.columns(3)

    with top1:
        st.markdown('<div class="summary-inner-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Invoice overview</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{result["invoice_amount"]:,.0f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="metric-sub">Principal borrowed (advance): {result["principal_borrowed"]:,.0f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with top2:
        st.markdown('<div class="summary-inner-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Margin after financing</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{net_margin:,.0f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="metric-sub">Gross margin before financing: {gross_margin:,.0f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with top3:
        st.markdown('<div class="summary-inner-card">', unsafe_allow_html=True)
        st.markmarkdown('<div class="metric-label">Margin eaten by financing</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{margin_eaten_val:,.0f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="metric-sub">{margin_eaten_pct_of_margin:.1f}% of your margin is lost to financing</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")
    mid1, mid2, mid3 = st.columns(3)

    with mid1:
        st.markdown('<div class="summary-inner-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Financing cost vs invoice</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{financing_cost_pct_of_invoice:.2f}%</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="metric-sub">Total financing cost: {result["total_financing_cost"]:,.0f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with mid2:
        st.markdown('<div class="summary-inner-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Effective annualized cost</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{effective_annualized_cost_pct:.1f}%</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="metric-sub">Based on {int(days_outstanding)} days outstanding</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with mid3:
        st.markdown('<div class="summary-inner-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Interest vs fees split</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{result["interest_cost"]:,.0f} / {result["total_fees"]:,.0f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="metric-sub">Interest cost / total fees</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close summary-wrapper

    # ---- Chart with thinner bars & light background ----
    st.markdown('<div class="section-title">Margin before and after financing</div>', unsafe_allow_html=True)

    margin_df = pd.DataFrame(
        {
            "Type": ["Financing cost", "Gross margin (before)", "Net margin (after)"],
            "Amount": [margin_eaten_val, gross_margin, net_margin],
        }
    )

    chart = (
        alt.Chart(margin_df)
        .mark_bar(size=45)
        .encode(
            x=alt.X("Type:N", axis=alt.Axis(title=None, labelAngle=0)),
            y=alt.Y("Amount:Q", axis=alt.Axis(title=None)),
            tooltip=["Type", "Amount"],
        )
        .properties(
            height=280,
        )
        .configure_view(
            strokeWidth=0,
            fill="#f9fafb",
        )
        .configure_axis(
            labelColor="#4b5563",
            titleColor="#4b5563",
            grid=True,
            gridColor="#e5e7eb",
        )
    )

    st.altair_chart(chart, use_container_width=True)

    # ---- Detailed table ----
    with st.expander("Detailed breakdown"):
        breakdown_df = pd.DataFrame(
            {
                "Metric": [
                    "Invoice amount",
                    "Principal borrowed (advance)",
                    "Gross margin (before financing)",
                    "Interest cost",
                    "Total fees (arrangement + fixed)",
                    "Total financing cost",
                    "Net margin (after financing)",
                    "Margin eaten by financing (value)",
                    "Margin eaten by financing (% of margin)",
                    "Financing cost (% of invoice)",
                    "Effective annualized cost (% on invoice)",
                ],
                "Value": [
                    f"{result['invoice_amount']:,.2f}",
                    f"{result['principal_borrowed']:,.2f}",
                    f"{result['gross_margin_value']:,.2f}",
                    f"{result['interest_cost']:,.2f}",
                    f"{result['total_fees']:,.2f}",
                    f"{result['total_financing_cost']:,.2f}",
                    f"{result['net_margin_after_financing']:,.2f}",
                    f"{result['margin_eaten_value']:,.2f}",
                    f"{result['margin_eaten_pct_of_margin']:.2f} %",
                    f"{result['financing_cost_pct_of_invoice']:.2f} %",
                    f"{result['effective_annualized_cost_pct']:.2f} %",
                ],
            }
        )
        st.dataframe(breakdown_df, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)  # close main-block
