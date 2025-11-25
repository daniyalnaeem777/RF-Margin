import streamlit as st
import pandas as pd

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
    page_icon="💸",
    layout="wide",
)

# Custom CSS for a more aesthetic UI
st.markdown(
    """
    <style>
    /* Main background */
    .stApp {
        background: radial-gradient(circle at top left, #0f172a, #020617);
        color: #f9fafb;
    }

    /* Card style */
    .metric-card {
        padding: 1.2rem 1.4rem;
        border-radius: 1.2rem;
        background: rgba(15,23,42,0.85);
        border: 1px solid rgba(148,163,184,0.3);
        box-shadow: 0 18px 45px rgba(0,0,0,0.45);
    }

    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #9ca3af;
        margin-bottom: 0.25rem;
    }

    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #e5e7eb;
    }

    .metric-sub {
        font-size: 0.8rem;
        color: #9ca3af;
        margin-top: 0.25rem;
    }

    /* Headers */
    h1, h2, h3 {
        color: #e5e7eb !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #020617;
        border-right: 1px solid rgba(148,163,184,0.35);
    }

    /* Dataframe */
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        color: #e5e7eb;
        background-color: #020617;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------
# Sidebar Inputs
# --------------

st.sidebar.title("🔧 Inputs")

st.sidebar.caption("Configure your bridge / invoice financing assumptions.")

invoice_amount = st.sidebar.number_input(
    "Invoice Amount",
    min_value=0.0,
    value=10_000.0,
    step=1_000.0,
    format="%.2f",
)

margin_pct = st.sidebar.slider(
    "Gross Margin on Invoice (%)",
    min_value=1.0,
    max_value=80.0,
    value=25.0,
    step=1.0,
)

annual_interest_rate_pct = st.sidebar.slider(
    "Annual Interest Rate Charged by Bank (%)",
    min_value=5.0,
    max_value=40.0,
    value=18.0,
    step=0.5,
)

days_outstanding = st.sidebar.slider(
    "Days Until Repayment",
    min_value=1,
    max_value=180,
    value=60,
    step=1,
)

advance_rate_pct = st.sidebar.slider(
    "Advance Rate (% of Invoice Borrowed)",
    min_value=40.0,
    max_value=100.0,
    value=80.0,
    step=5.0,
)

st.sidebar.markdown("---")

arrangement_fee_pct = st.sidebar.slider(
    "Arrangement Fee (% of Invoice)",
    min_value=0.0,
    max_value=5.0,
    value=1.0,
    step=0.1,
)

fixed_fee = st.sidebar.number_input(
    "Fixed Fees (Legal / Processing)",
    min_value=0.0,
    value=0.0,
    step=100.0,
    format="%.2f",
)

st.sidebar.markdown("---")
st.sidebar.caption("Tip: Use this tool to quickly test if the financing cost still keeps your trade profitable.")


# ----------------
# Main Dashboard
# ----------------

st.title("💸 Bridge Financing Margin Calculator")
st.markdown(
    """
    Quickly see **how much of your margin is eaten by short-term bank financing** on an invoice.

    Use this for:
    - Discounting / bridge financing against invoices  
    - Testing if a trade is still worth doing after financing costs  
    - Comparing different repayment periods and advance rates  
    """
)

# Calculate results
if invoice_amount <= 0:
    st.warning("Please enter a positive invoice amount to see results.")
else:
    result = calculate_bridge_financing(
        annual_interest_rate_pct=annual_interest_rate_pct,
        invoice_amount=invoice_amount,
        days_outstanding=days_outstanding,
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

    col_top_left, col_top_mid, col_top_right = st.columns([1.3, 1.1, 1.1])

    with col_top_left:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Invoice Overview</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{result["invoice_amount"]:,.0f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="metric-sub">Principal borrowed (advance): '
            f'{result["principal_borrowed"]:,.0f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_top_mid:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Margin After Financing</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{net_margin:,.0f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="metric-sub">Gross margin before financing: {gross_margin:,.0f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_top_right:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Margin Eaten by Financing</div>', unsafe_allow_html=True)
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

    col_mid_left, col_mid_mid, col_mid_right = st.columns([1.1, 1.1, 1.1])

    with col_mid_left:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Financing Cost vs Invoice</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{financing_cost_pct_of_invoice:.2f}%</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="metric-sub">Total financing cost: {result["total_financing_cost"]:,.0f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_mid_mid:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Effective Annualized Cost</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{effective_annualized_cost_pct:.1f}%</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="metric-sub">Based on {days_outstanding} days outstanding</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_mid_right:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Interest vs Fees Split</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{result["interest_cost"]:,.0f} / {result["total_fees"]:,.0f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="metric-sub">Interest cost / Total fees</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------
    # Charts & Breakdown
    # ---------------------

    st.markdown("## 📊 Margin Before & After Financing")

    margin_df = pd.DataFrame(
        {
            "Type": ["Gross Margin (Before)", "Net Margin (After)", "Financing Cost"],
            "Amount": [gross_margin, net_margin, margin_eaten_val],
        }
    ).set_index("Type")

    st.bar_chart(margin_df)

    with st.expander("🔍 Detailed Breakdown"):
        st.write("All values in your base currency:")

        breakdown_df = pd.DataFrame(
            {
                "Metric": [
                    "Invoice Amount",
                    "Principal Borrowed (Advance)",
                    "Gross Margin (Before Financing)",
                    "Interest Cost",
                    "Total Fees (Arrangement + Fixed)",
                    "Total Financing Cost",
                    "Net Margin (After Financing)",
                    "Margin Eaten by Financing (Value)",
                    "Margin Eaten by Financing (% of Margin)",
                    "Financing Cost (% of Invoice)",
                    "Effective Annualized Cost (% on Invoice)",
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

    st.markdown(
        """
        ---  
        💡 **Interpretation Tips**
        - If **Net Margin After Financing** is close to zero or negative → the deal is not worth it.  
        - Watch **Margin Eaten by Financing (% of Margin)** — if you're giving 30–50% of your profit to the bank, it might be too expensive.  
        - Use different **Days Until Repayment** to negotiate better terms with clients/banks.  
        """
    )
