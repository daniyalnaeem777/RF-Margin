import streamlit as st
import pandas as pd
import altair as alt

# ---------------------------
#  Streamlit Configuration (MUST BE FIRST)
# ---------------------------
st.set_page_config(
    page_title="Bridge Financing Calculator",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    """Calculate the economics of bridge financing against an invoice."""

    annual_rate = annual_interest_rate_pct / 100.0
    margin_rate = margin_pct / 100.0
    advance_rate = advance_rate_pct / 100.0
    arrangement_fee_rate = arrangement_fee_pct / 100.0

    principal_borrowed = invoice_amount * advance_rate
    gross_margin_value = invoice_amount * margin_rate

    # If days outstanding is 0 or less, interest cost is 0
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


# ---------------------------
#  Aesthetic CSS Styling (NUCLEAR FIX FOR TOP BAR)
# ---------------------------
st.markdown(
    """
    <style>
    /* ----------------------------------------------------------------- */
    /* NUCLEAR LAYOUT FIX: ELIMINATE THE TOP WHITE BAR/PADDING */
    /* ----------------------------------------------------------------- */
    
    /* Global body and html reset */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        height: 100%;
    }
    
    /* 1. Target the top-level app wrapper (highest priority) */
    .stApp {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* 2. Target the main content container and eliminate all padding */
    div[data-testid="stAppViewBlockContainer"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* 3. Target the main element block that often controls the top margin/padding for wide layouts */
    .main > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* 4. Target the immediate container holding the title/subtitle block */
    div[data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* 5. Target the container immediately surrounding the header block */
    .block-container:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* 6. Target the header element itself */
    header {
        visibility: hidden;
        height: 0;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
    }
    
    /* 7. Ensure the entire page starts at the top */
    div[data-testid="stFullScreenFrame"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* ----------------------------------------------------------------- */
    /* THEME & FONT STYLING (Rest of the previous styles)                */
    /* ----------------------------------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', Arial, Helvetica, sans-serif !important;
    }

    /* Background and global spacing */
    .stApp {
        background-color: #f8f9fa !important;
        color: #1f2937 !important;
    }
    
    /* HEADINGS & TEXT STYLING */
    h1 {
        font-weight: 900;
        letter-spacing: -0.02em;
        color: #111827 !important;
        margin-bottom: 0.5rem;
    }
    
    h3 {
        font-weight: 700;
        color: #111827 !important;
        font-size: 1.25rem;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    
    p, li, span, div[data-testid="stWidgetLabel"] p, label {
        color: #111827 !important;
        font-weight: 400 !important;
    }
    
    /* INPUT BOX STYLING */
    .input-section-container {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        padding: 20px 20px 30px 20px;
        margin-bottom: 2rem;
    }

    div[data-testid="stWidgetLabel"] p, label, .stWidgetLabel {
        color: #111827 !important;
        font-weight: 700 !important;
    }

    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        color: #111827 !important;
        border-color: #d1d5db;
        border-radius: 6px !important;
        border: 1px solid #d1d5db !important;
    }
    
    input[type="number"], input[type="text"] {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        caret-color: #111827 !important;
        background-color: #ffffff !important;
    }

    div[data-testid="stNumberInput"] button {
        display: none !important;
    }
    
    div[data-baseweb="input"]:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }

    /* OUTPUT CARD STYLING */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-radius: 10px;
        border: 1px solid #e5e7eb !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        padding: 1.5rem;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: white !important;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    
    .metric-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #6b7280;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }
    
    .metric-sub {
        font-size: 0.9rem;
        color: #9ca3af;
        font-weight: 400;
    }

    .negative { color: #ef4444 !important; }
    .positive { color: #10b981 !important; }
    .neutral { color: #3b82f6 !important; }

    /* Hide Streamlit footer */
    footer {visibility: hidden;}
    
    /* Table styling for breakdown */
    table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.9rem; }
    th { text-align: left; color: #6b7280 !important; font-weight: 600; padding-bottom: 8px; border-bottom: 1px solid #e5e7eb; }
    td { padding: 8px 0; color: #111827 !important; border-bottom: 1px solid #f3f4f6; }
    tr:last-child td { border-bottom: none; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
#  UI Structure
# ---------------------------

# Use st.container to wrap the entire main content to potentially help with layout control
# The column structure below ensures the content is centered and wide.
col_spacer_l, col_main, col_spacer_r = st.columns([0.5, 10, 0.5])

with col_main:
    # Header
    # Added a utility div around the main content for another layer of reset
    st.markdown('<div class="app-content-wrapper">', unsafe_allow_html=True) 
    
    st.title("Bridge Financing Calculator")
    st.markdown('<div class="subtitle">Analyze the impact of short-term financing costs on your deal margins.</div>', unsafe_allow_html=True)

    # ---------------------------
    #  Inputs Section
    # ---------------------------
    
    st.markdown('<div class="input-section-container">', unsafe_allow_html=True)
    
    st.markdown("### 🛠 Deal Parameters")
    
    st.markdown("---")
    
    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
    
    # Input Widgets
    c1, c2, c3 = st.columns(3)
    with c1:
        invoice_amount = st.number_input("Invoice Amount ($)", min_value=0.0, value=10000.0, step=1000.0, format="%.2f")
        days_outstanding = st.number_input("Days Outstanding", min_value=1, value=60, step=1)
        
    with c2:
        margin_pct = st.number_input("Gross Margin (%)", min_value=0.0, value=25.0, step=0.5, format="%.2f")
        advance_rate_pct = st.number_input("Advance Rate (%)", min_value=0.0, max_value=100.0, value=80.0, step=1.0, format="%.2f")
        
    with c3:
        annual_interest_rate_pct = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=18.0, step=0.25, format="%.2f")
        arrangement_fee_pct = st.number_input("Arrangement Fee (%)", min_value=0.0, value=1.0, step=0.1, format="%.2f")
    
    # Additional fixed fee
    st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True) 
    fixed_fee = st.number_input("Fixed Fees (Legal/Processing $)", min_value=0.0, value=0.0, step=100.0, format="%.2f")

    st.markdown('</div>', unsafe_allow_html=True) # Closing the custom input-section-container

    # ---------------------------
    #  Calculations and Output
    # ---------------------------
    if invoice_amount > 0:
        result = calculate_bridge_financing(
            annual_interest_rate_pct, invoice_amount, int(days_outstanding),
            margin_pct, advance_rate_pct, arrangement_fee_pct, fixed_fee
        )
        
        # Extract values for display
        net_margin = result["net_margin_after_financing"]
        gross_margin = result["gross_margin_value"]
        margin_eaten_val = result["margin_eaten_value"]
        margin_eaten_pct = result["margin_eaten_pct_of_margin"]
        
        # ---------------------------
        #  KPI Dashboard (HTML/CSS)
        # ---------------------------
        st.markdown("### 📊 Financial Impact")
        
        st.markdown(f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Net Margin (Profit)</div>
                <div class="metric-value positive">${net_margin:,.0f}</div>
                <div class="metric-sub">vs ${gross_margin:,.0f} Gross Margin</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Cost of Financing</div>
                <div class="metric-value negative">${margin_eaten_val:,.0f}</div>
                <div class="metric-sub">Interest: ${result['interest_cost']:,.0f} | Fees: ${result['total_fees']:,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Margin Erosion</div>
                <div class="metric-value negative">{margin_eaten_pct:.1f}%</div>
                <div class="metric-sub">of your gross margin is gone</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Effective APR</div>
                <div class="metric-value neutral">{result['effective_annualized_cost_pct']:.2f}%</div>
                <div class="metric-sub">Annualized cost of capital</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ---------------------------
        #  Visuals (Altair) & Table
        # ---------------------------
        
        col_chart, col_data = st.columns([1.5, 1])

        with col_chart:
            with st.container(border=True):
                st.markdown("### Margin Visualization")
                
                # Prepare data for chart
                chart_data = pd.DataFrame([
                    {"Category": "Gross Margin", "Amount": gross_margin, "Type": "Initial"},
                    {"Category": "Financing Cost", "Amount": margin_eaten_val, "Type": "Cost"},
                    {"Category": "Net Margin", "Amount": net_margin, "Type": "Final"}
                ])
                
                # Create a clean bar chart
                bar_chart = alt.Chart(chart_data).mark_bar(
                    cornerRadiusTopLeft=6,
                    cornerRadiusTopRight=6,
                    size=50
                ).encode(
                    x=alt.X('Category', sort=["Gross Margin", "Financing Cost", "Net Margin"], axis=alt.Axis(labelAngle=0, title=None, grid=False)),
                    y=alt.Y('Amount', axis=alt.Axis(format='$,.0f', title=None, grid=True)),
                    color=alt.Color('Type', scale=alt.Scale(domain=['Initial', 'Cost', 'Final'], range=['#9CA3AF', '#EF4444', '#10B981']), legend=None),
                    tooltip=['Category', alt.Tooltip('Amount', format='$,.2f')]
                ).properties(
                    height=320,
                    background='transparent'
                ).configure_view(
                    strokeWidth=0
                ).configure_axis(
                    labelFont='Roboto, Arial, sans-serif',
                    labelColor='#6B7280',
                    gridColor='#F3F4F6'
                )
                
                st.altair_chart(bar_chart, use_container_width=True)

        with col_data:
            with st.container(border=True):
                st.markdown("### Detailed Breakdown")
                breakdown_data = {
                    "Metric": [
                        "Principal Borrowed", 
                        "Interest Cost", 
                        "Arrangement & Fixed Fees", 
                        "Total Financing Cost",
                        "Financing % of Invoice"
                    ],
                    "Value": [
                        f"${result['principal_borrowed']:,.2f}",
                        f"${result['interest_cost']:,.2f}",
                        f"${result['total_fees']:,.2f}",
                        f"${result['total_financing_cost']:,.2f}",
                        f"{result['financing_cost_pct_of_invoice']:.2f}%"
                    ]
                }
                df_breakdown = pd.DataFrame(breakdown_data)
                
                # Use HTML table for cleaner look than st.dataframe
                st.markdown(
                    df_breakdown.to_html(index=False, classes="table table-striped", border=0, justify="left"), 
                    unsafe_allow_html=True
                )
                
            
    else:
        st.info("Please enter a valid invoice amount to generate calculations.")
        
    st.markdown('</div>', unsafe_allow_html=True) # Closing the app-content-wrapper div
