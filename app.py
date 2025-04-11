
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# Page config – MUST be first Streamlit command
st.set_page_config(page_title="Mælaborð Suðurnesja", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("lidanargogn_sudurnes_gervi.csv")
    return df

df = load_data()

# Add a 'Tímabil' column to simulate 'Vor' and 'Haust' periods
df['Tímabil'] = df['Ár'].apply(lambda x: 'Vor' if x % 2 == 0 else 'Haust')  # Just as an example, you can adjust this logic

# Load logo
logo = Image.open("/mnt/data/OIP_corrected.png")  # Use the corrected logo

# Custom color palette (example from logo style)
PRIMARY_COLOR = "#2D3A3F"  # deep grey-blue
df_palette = {
    'Líðan': '#2D3A3F',
    'Kvíði': '#5D6D74',
    'Einmanaleiki': '#99A8AC',
    'Skjástund': '#CCD4D6',
    'Tengsl við kennara': '#88999F',
    'Ánægja með skólann': '#A9B8BB'
}

# Sidebar filters
st.sidebar.image(logo, use_container_width=True)
st.sidebar.title("Valmöguleikar")
skolar = df['Skóli'].unique()
valinn_skoli = st.sidebar.selectbox("Veldu skóla", sorted(skolar))
valin_ar = st.sidebar.multiselect("Veldu ár", sorted(df['Ár'].unique()), default=sorted(df['Ár'].unique()))

# Option for administrators to view comparison or individual school data
view_mode = st.sidebar.radio("Val: Sýna samanburð eða einstaklingsskóla?", ("Sýna samanburð", "Einstakur skóli"))

if view_mode == "Sýna samanburð":
    # For administrators: Comparison view between schools
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image(logo, width=100)
    st.title("Stjórnendaryfirlit um líðan barna á Suðurnesjum")
    
    # Show comparison between schools using heatmap
    st.subheader("Samanburður milli skóla")
    comparison_data = df.groupby('Skóli')[["Líðan", "Kvíði", "Einmanaleiki", "Skjástund", "Tengsl við kennara", "Ánægja með skólann"]].mean()
    st.dataframe(comparison_data)
    
    # Show heatmap for comparison between schools
    heatmap_data = df.groupby(['Skóli', 'Ár'])[['Líðan', 'Kvíði', 'Einmanaleiki', 'Skjástund', 'Tengsl við kennara', 'Ánægja með skólann']].mean().reset_index()
    heatmap_data_pivot = heatmap_data.pivot_table(index="Ár", columns="Skóli", values="Líðan")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_data_pivot, annot=True, cmap="RdYlGn", fmt=".1f", ax=ax)
    st.pyplot(fig)

elif view_mode == "Einstakur skóli":
    # For individual school: Display strengths, weaknesses, and comparison with the district and national averages
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image(logo, width=100)
    st.title(f"Yfirlit um líðan fyrir {valinn_skoli}")
    
    # Show individual school statistics
    filtered_df = df[(df['Skóli'] == valinn_skoli) & (df['Ár'].isin(valin_ar))]

    st.subheader("Meðaltal velferðarþátta fyrir valinn skóla")
    meðaltöl = filtered_df.groupby(['Ár'])[["Líðan", "Kvíði", "Einmanaleiki", "Skjástund", "Tengsl við kennara", "Ánægja með skólann"]].mean().round(2)
    st.dataframe(meðaltöl)
    
    # Top 3 strengths and challenges per individual school
    st.subheader(f"Top 3 styrkleikar og áskoranir fyrir {valinn_skoli}")
    school_data = df[df['Skóli'] == valinn_skoli]
    strengths = school_data[['Líðan', 'Kvíði', 'Einmanaleiki', 'Skjástund', 'Tengsl við kennara', 'Ánægja með skólann']].mean().nlargest(3)
    challenges = school_data[['Líðan', 'Kvíði', 'Einmanaleiki', 'Skjástund', 'Tengsl við kennara', 'Ánægja með skólann']].mean().nsmallest(3)
    st.markdown(f"**Styrkleikar**: {', '.join([f'{x}: {strengths[x]:.2f}' for x in strengths.index])}")
    st.markdown(f"**Áskoranir**: {', '.join([f'{x}: {challenges[x]:.2f}' for x in challenges.index])}")
    
    # Show comparison with the district and national averages
    st.subheader(f"Samanburður við landsmeðaltal og sveitarfélagið")
    national_avg = df[['Líðan', 'Kvíði', 'Einmanaleiki', 'Skjástund', 'Tengsl við kennara', 'Ánægja með skólann']].mean()
    district_avg = df[df['Skóli'] != valinn_skoli][['Líðan', 'Kvíði', 'Einmanaleiki', 'Skjástund', 'Tengsl við kennara', 'Ánægja með skólann']].mean()
    
    st.write("Landsmeðaltal:", national_avg)
    st.write(f"Sveitarfélagið ({valinn_skoli} ekki meðtalið):", district_avg)
    
    # Plotting trendline comparison across schools (individual school vs. district/national averages)
    st.subheader("Þróun yfir ár")
    trend_data = filtered_df.groupby(['Ár', 'Skóli'])[['Líðan', 'Kvíði', 'Einmanaleiki', 'Skjástund', 'Tengsl við kennara', 'Ánægja með skólann']].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(trend_data['Ár'], trend_data['Líðan'], label=f"{valinn_skoli} - Líðan")
    ax.plot(trend_data['Ár'], national_avg['Líðan'], label="Landsmeðaltal - Líðan", linestyle='dashed')
    ax.plot(trend_data['Ár'], district_avg['Líðan'], label="Sveitarfélagið - Líðan", linestyle='dotted')
    
    ax.set_xlabel("Ár")
    ax.set_ylabel("Meðaltal")
    ax.set_title(f"Þróun yfir ár fyrir {valinn_skoli} og samanburður við landsmeðaltal og sveitarfélagið")
    ax.legend()
    st.pyplot(fig)

# Warning system for Einmanaleiki and Kvíði with column check
st.subheader("Viðvörunarkerfi og tillögur að inngripum")
if 'Einmanaleiki' in df.columns and 'Kvíði' in df.columns:
    einman_alert = filtered_df[filtered_df["Einmanaleiki"] > 5]
    if not einman_alert.empty:
        st.markdown("**Viðvörun!** >25% nemenda skora 5 eða hærra á einmanaleika. Tillögur: Bæta félagslega þjónustu eða veita aukna ráðgjöf.")

    # High anxiety alert
    anxiety_alert = filtered_df[filtered_df["Kvíði"] > 4]
    if not anxiety_alert.empty:
        st.markdown("**Viðvörun!** >25% nemenda skora 4 eða hærra á kvíða. Tillögur: Auka náms- og félagslega stuðning.")
else:
    st.warning("Dálkarnir 'Einmanaleiki' og 'Kvíði' eru ekki til staðar í gögnunum.")

st.markdown("---")
st.caption("© Samband sveitarfélaga á Suðurnesjum – Mælaborð fyrir farsæld barna og ungmenna")
