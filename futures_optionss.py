import numpy as np
import streamlit as st
import plotly.graph_objects as go

def call_payoff(S, K, premium=0.0, qty=1.0, long=True):
    payoff = np.maximum(S - K, 0) - premium
    return payoff * qty if long else -payoff * qty

def put_payoff(S, K, premium=0.0, qty=1.0, long=True):
    payoff = np.maximum(K - S, 0) - premium
    return payoff * qty if long else -payoff * qty

def combined_payoff(S, legs):
    total = np.zeros_like(S)
    for leg in legs:
        if leg['type'] == 'C':
            total += call_payoff(S, leg['K'], premium=leg['premium'], qty=leg['qty'], long=leg['long'])
        else:
            total += put_payoff(S, leg['K'], premium=leg['premium'], qty=leg['qty'], long=leg['long'])
    return total

def simulate_ST(S0, mu, sigma, T_days, n_sims=12000, seed=42):
    np.random.seed(seed)
    T = max(T_days, 0) / 252.0
    if T == 0:
        return np.array([S0])
    drift = (mu - 0.5 * sigma ** 2) * T
    diffusion = sigma * np.sqrt(T) * np.random.randn(n_sims)
    ST = S0 * np.exp(drift + diffusion)
    return ST

def expected_metrics_via_mc(legs, S0, mu, sigma, T_days, n_sims=12000):
    ST = simulate_ST(S0, mu, sigma, T_days, n_sims=n_sims)
    sim_payoffs = np.array([combined_payoff(np.array([s]), legs)[0] for s in ST])
    ev = sim_payoffs.mean()
    prob_profit = (sim_payoffs > 0).mean()
    median = np.median(sim_payoffs)
    downside_pct = (sim_payoffs < 0).mean()
    return {"ev": ev, "prob_profit": prob_profit, "median": median, "downside_pct": downside_pct}

def breakevens(S, payoff):
    signs = np.sign(payoff)
    idx = np.where(np.diff(signs) != 0)[0]
    be_points = []
    for i in idx:
        x0, x1 = S[i], S[i+1]
        y0, y1 = payoff[i], payoff[i+1]
        if (y1 - y0) == 0:
            be = x0
        else:
            be = x0 - y0 * (x1 - x0) / (y1 - y0)
        be_points.append(be)
    return be_points

# Default parameters
mu_default = 0.06
S0_default = 24900
strike_default = 25000
premium_call_default = 380.0
premium_put_default = 360.0
qty_default = 1.0
T_days_default = 9
sigma_default = 0.18

S_min_default = S0_default - 5000
S_max_default = S0_default + 5000
S = np.linspace(S_min_default, S_max_default, 400)

def make_straddle(K, p_call, p_put, qty):
    return [
        {"type": "C", "K": K, "premium": p_call, "qty": qty, "long": True},
        {"type": "P", "K": K, "premium": p_put, "qty": qty, "long": True},
    ]

def build_strategy_from_radio(strategy, K, p_call, p_put, qty):
    if strategy == 'Straddle':
        return make_straddle(K, p_call, p_put, qty), "Long Straddle"
    elif strategy == 'Strangle':
        Kput = max(1, K - 400)
        Kcall = K + 400
        legs = [
            {"type": "P", "K": Kput, "premium": p_put * 0.6, "qty": qty, "long": True},
            {"type": "C", "K": Kcall, "premium": p_call * 0.6, "qty": qty, "long": True},
        ]
        return legs, f"Long Strangle ({Kput}/{Kcall})"
    elif strategy == 'IronCondor':
        legs = [
            {"type": "P", "K": K-400, "premium": p_put*0.7, "qty": qty, "long": False},
            {"type": "P", "K": K-800, "premium": p_put*0.3, "qty": qty, "long": True},
            {"type": "C", "K": K+400, "premium": p_call*0.7, "qty": qty, "long": False},
            {"type": "C", "K": K+800, "premium": p_call*0.3, "qty": qty, "long": True},
        ]
        return legs, "Iron Condor"
    elif strategy == 'BullCallSpread':
        width = 400
        K_buy = max(1, K - int(width/2))
        K_sell = K_buy + width
        legs = [
            {"type": "C", "K": K_buy, "premium": p_call*0.9, "qty": qty, "long": True},
            {"type": "C", "K": K_sell, "premium": p_call*0.5, "qty": qty, "long": False},
        ]
        return legs, f"Bull Call Spread ({K_buy}->{K_sell})"
    elif strategy == 'Butterfly':
        wing = 600
        K_low = K - wing
        K_mid = K
        K_high = K + wing
        legs = [
            {"type": "C", "K": K_low, "premium": p_call*0.9, "qty": qty, "long": True},
            {"type": "C", "K": K_mid, "premium": p_call*0.7, "qty": qty*2, "long": False},
            {"type": "C", "K": K_high, "premium": p_call*0.9, "qty": qty, "long": True},
        ]
        return legs, f"Long Butterfly ({K_low},{K_mid},{K_high})"
    else:
        return make_straddle(K, p_call, p_put, qty), "Long Straddle"

st.title("Options Strategy Payoff & Monte Carlo Simulator")

st.sidebar.header("Choose Strategy & Parameters")
strategy = st.sidebar.selectbox("Strategy", ('Straddle', 'Strangle', 'IronCondor', 'BullCallSpread', 'Butterfly'))
K = st.sidebar.slider("Strike K", S_min_default, S_max_default, strike_default, step=50)
p_call = st.sidebar.slider("Call Premium", 0.0, 1000.0, premium_call_default)
p_put = st.sidebar.slider("Put Premium", 0.0, 1000.0, premium_put_default)
qty = st.sidebar.slider("Qty (contracts)", 0.1, 10.0, qty_default)
spot_now = st.sidebar.slider("Spot", S_min_default, S_max_default, S0_default)
T_days = st.sidebar.slider("Days to Expiry", 1, 90, T_days_default)
vol = st.sidebar.slider("Vol(ann)", 0.05, 1.0, sigma_default)

# Get legs and label for strategy
current_legs, label = build_strategy_from_radio(strategy, K, p_call, p_put, qty)
payoff = combined_payoff(S, current_legs)

fig = go.Figure()
fig.add_trace(go.Scatter(x=S, y=payoff, mode='lines', name=label, line=dict(width=3)))
fig.add_hline(y=0, line_color='black', line_width=1)
fig.add_vline(x=spot_now, line_color='red', line_dash='dash', line_width=2)

fig.update_layout(
    title="Payoff Chart",
    xaxis_title="Underlying Price at Expiry",
    yaxis_title="PnL per unit",
    template="plotly_white",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

st.plotly_chart(fig, use_container_width=True)

# Breakeven points
bes = breakevens(S, payoff)
be_str = "None" if not bes else ", ".join([f"{b:.0f}" for b in bes])
st.info(f"Breakeven(s): {be_str}")

# Monte Carlo analytics
metrics = expected_metrics_via_mc(current_legs, spot_now, mu_default, vol, T_days, n_sims=12000)
st.markdown(f"""
**Monte Carlo Analytics**
- Expected Value (EV): `{metrics['ev']:.1f}`
- Probability of Profit: `{metrics['prob_profit']*100:.1f}%`
- Median: `{metrics['median']:.1f}`
- Downside Probability: `{metrics['downside_pct']*100:.1f}%`
""")
