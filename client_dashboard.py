import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import jenkspy

st.set_page_config(layout="wide", page_title="Client Priority Analysis")

st.title("🎯 Client Priority Dashboard")
st.markdown("Upload your client rankings file and adjust weights to see how priorities shift")

# File uploader
uploaded_file = st.file_uploader(
    "Upload Client Rankings (Excel or CSV)", 
    type=['xlsx', 'xls', 'csv'],
    help="File should have columns: Client, Current Client, Current Work, Future Work, Difficulty Dealing With, Profitability, Ease to Distribute"
)

if uploaded_file is None:
    st.info("👆 Upload your client rankings file to get started")
    st.stop()

# Read the uploaded file
try:
    if uploaded_file.name.endswith('.csv'):
        df_upload = pd.read_csv(uploaded_file)
    else:
        # Read Excel, check if first row contains weights
        df_temp = pd.read_excel(uploaded_file, nrows=2)
        
        # Check if first row looks like it has weights (numeric column names)
        has_weights_row = any(isinstance(col, (int, float)) for col in df_temp.columns)
        
        if has_weights_row:
            # Skip first row (weights), use second row as header
            df_upload = pd.read_excel(uploaded_file, header=1)
        else:
            df_upload = pd.read_excel(uploaded_file)
    
    # Validate columns - handle various column name formats
    required_cols_map = {
        'client': 'Client',
        'current client': 'Current',
        'current work': 'CW',
        'future work': 'FW',
        'difficulty dealing with': 'DD',
        'profitability': 'Prof',
        'ease to distribute': 'Ease'
    }
    
    # Create mapping of actual columns to standardized names
    upload_cols_lower = {col.strip().lower(): col for col in df_upload.columns if isinstance(col, str)}
    
    # Check for missing columns
    missing_cols = []
    column_mapping = {}
    for required_lower, standard_name in required_cols_map.items():
        if required_lower not in upload_cols_lower:
            missing_cols.append(required_lower)
        else:
            column_mapping[upload_cols_lower[required_lower]] = standard_name
    
    if missing_cols:
        st.error(f"Missing required columns: {', '.join(missing_cols)}")
        st.info("Required columns: Client, Current Client, Current Work, Future Work, Difficulty Dealing With, Profitability, Ease to Distribute")
        st.info(f"Found columns: {', '.join([str(c) for c in df_upload.columns])}")
        st.stop()
    
    # Rename columns to standard names
    df_upload = df_upload.rename(columns=column_mapping)
    
    # Keep only the columns we need
    df_upload = df_upload[['Client', 'Current', 'CW', 'FW', 'DD', 'Prof', 'Ease']]
    
    st.success(f"✅ Loaded {len(df_upload)} clients")
    
except Exception as e:
    st.error(f"Error reading file: {str(e)}")
    st.info("Please check that your file has the correct format. See the template file for an example.")
    st.stop()

st.markdown("---")
st.markdown("### Adjust Factor Weights")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    cw = st.slider("Current Work", 0, 100, 30, 5, help="Weight for active work")
with col2:
    fw = st.slider("Future Work", 0, 100, 25, 5, help="Weight for pipeline/potential")
with col3:
    dd = st.slider("Difficulty", 0, 100, 15, 5, help="Weight for ease of working together")
with col4:
    prof = st.slider("Profitability", 0, 100, 25, 5, help="Weight for margin/rates")
with col5:
    ease = st.slider("Ease Distribute", 0, 100, 5, 5, help="Weight for staffing flexibility")

total = cw + fw + dd + prof + ease
weights = [cw/total, fw/total, dd/total, prof/total, ease/total]

st.markdown(f"**Normalized Weights:** Current: {weights[0]:.1%} | Future: {weights[1]:.1%} | Difficulty: {weights[2]:.1%} | Profit: {weights[3]:.1%} | Distribute: {weights[4]:.1%}")

df = df_upload.copy()
df['Score'] = (df['CW'] * weights[0] + df['FW'] * weights[1] + 
               df['DD'] * weights[2] + df['Prof'] * weights[3] + df['Ease'] * weights[4])

df = df.sort_values('Score', ascending=False).reset_index(drop=True)
df['Rank'] = range(1, len(df) + 1)

scores = df['Score'].values
breaks = jenkspy.jenks_breaks(scores, n_classes=4)

# Adjust intermediate breaks upward by 0.075
breaks[1] += 0.075
breaks[2] += 0.075
breaks[3] += 0.075

def assign_tier(score):
    if score >= breaks[3]:
        return 'Tier 1: Elite'
    elif score >= breaks[2]:
        return 'Tier 2: Priority'
    elif score >= breaks[1]:
        return 'Tier 3: Standard'
    else:
        return 'Tier 4: Maintenance'

df['Tier'] = df['Score'].apply(assign_tier)

tier_colors = {
    'Tier 1: Elite': '#1f77b4',
    'Tier 2: Priority': '#ff7f0e', 
    'Tier 3: Standard': '#2ca02c',
    'Tier 4: Maintenance': '#d62728'
}

st.markdown("---")

st.subheader("Client Rankings with Natural Tier Breaks")

fig = go.Figure()

for tier in ['Tier 1: Elite', 'Tier 2: Priority', 'Tier 3: Standard', 'Tier 4: Maintenance']:
    tier_df = df[df['Tier'] == tier]
    fig.add_trace(go.Bar(
        x=tier_df['Client'],
        y=tier_df['Score'],
        name=tier,
        marker_color=tier_colors[tier],
        hovertemplate='%{x}<br>Score: %{y:.2f}<extra></extra>'
    ))

for i in range(1, 4):
    fig.add_hline(y=breaks[i], line_dash="dash", line_color="gray", 
                 annotation_text=f"Break: {breaks[i]:.2f}", 
                 annotation_position="right")

fig.update_layout(
    height=500,
    xaxis_title="",
    yaxis_title="Weighted Score",
    showlegend=True,
    barmode='relative',
    xaxis={'categoryorder': 'total descending'},
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

col_curve, col_box, col_summary = st.columns(3)

with col_curve:
    st.subheader("Score Drop-Off Curve")
    
    fig_curve = go.Figure()
    
    fig_curve.add_trace(go.Scatter(
        x=df['Rank'],
        y=df['Score'],
        mode='lines+markers',
        marker=dict(size=4, color=df['Tier'].map(tier_colors)),
        line=dict(color='#1f77b4', width=2),
        hovertemplate='Rank: %{x}<br>Score: %{y:.2f}<extra></extra>'
    ))
    
    for i in range(1, 4):
        fig_curve.add_hline(y=breaks[i], line_dash="dash", line_color="lightgray", opacity=0.5)
    
    fig_curve.update_layout(
        height=400,
        xaxis_title="Client Rank",
        yaxis_title="Weighted Score",
        showlegend=False,
        hovermode='closest'
    )
    
    st.plotly_chart(fig_curve, use_container_width=True)
    st.caption("📉 Steep drops = natural tier breaks. Gradual slope = no clear priority groups.")

with col_box:
    st.subheader("Score Distribution by Status")
    
    fig_box = go.Figure()
    
    current_clients = df[df['Current'] == 'Y']['Score']
    non_current_clients = df[df['Current'] == 'N']['Score']
    
    fig_box.add_trace(go.Box(
        y=current_clients,
        name='Current Clients',
        marker_color='#2ca02c',
        boxmean='sd'
    ))
    
    fig_box.add_trace(go.Box(
        y=non_current_clients,
        name='Non-Current Clients',
        marker_color='#d62728',
        boxmean='sd'
    ))
    
    fig_box.update_layout(
        height=400,
        yaxis_title="Weighted Score",
        showlegend=True
    )
    
    st.plotly_chart(fig_box, use_container_width=True)
    st.caption("📊 Shows if current clients actually score higher than prospects/past clients.")

with col_summary:
    st.subheader("Tier Summary")
    
    tier_summary = df.groupby('Tier').agg({
        'Client': 'count',
        'Score': ['min', 'max', 'mean']
    }).round(2)
    
    tier_summary.columns = ['Count', 'Min Score', 'Max Score', 'Avg Score']
    tier_summary = tier_summary.reindex(['Tier 1: Elite', 'Tier 2: Priority', 'Tier 3: Standard', 'Tier 4: Maintenance'])
    
    st.dataframe(tier_summary, use_container_width=True, height=210)
    
    st.markdown("### Tier Boundaries")
    st.markdown(f"**Elite:** ≥ {breaks[3]:.2f}")
    st.markdown(f"**Priority:** {breaks[2]:.2f} - {breaks[3]:.2f}")
    st.markdown(f"**Standard:** {breaks[1]:.2f} - {breaks[2]:.2f}")
    st.markdown(f"**Maintenance:** < {breaks[1]:.2f}")

st.markdown("---")
st.subheader("Detailed Rankings")

display_df = df[['Rank', 'Client', 'Score', 'Tier', 'Current']].copy()
display_df['Score'] = display_df['Score'].round(2)

def color_tiers(row):
    color = tier_colors.get(row['Tier'], '')
    return [f'background-color: {color}; color: white' if col == 'Tier' else '' for col in row.index]

styled_df = display_df.style.apply(color_tiers, axis=1)
st.dataframe(styled_df, use_container_width=True, height=400)

st.markdown("---")
st.caption("💡 **Jenks Natural Breaks**: Algorithm identifies optimal tier boundaries, adjusted +0.075 to align with visual gaps")