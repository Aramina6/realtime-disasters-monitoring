# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Earthquakes & Cyclones – Last 30 Days",
    page_icon="Alert",
    layout="wide"
)

# ----------------------------------------------------------------------
# EARTHQUAKES – USGS FDSN (30-day, min-mag 1.0)
# ----------------------------------------------------------------------
@st.cache_data(ttl=1800)
def fetch_earthquakes_month():
    end = datetime.utcnow().strftime("%Y-%m-%d")
    start = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    url = (
        f"https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&starttime={start}&endtime={end}"
        f"&minmagnitude=1&orderby=time"
    )
    try:
        data = requests.get(url, timeout=15).json()
        rows = []
        for f in data.get("features", []):
            p = f["properties"]
            g = f["geometry"]["coordinates"]
            rows.append({
                "name": f"M{p['mag']:.1f}",
                "location": p["place"],
                "impact": f"{p.get('felt', 0)} felt reports",
                "tsunami": bool(p.get("tsunami", 0)),
                "depth_km": g[2],
                "detail_url": p.get("detail", ""),
                "magnitude": p["mag"],
                "time_utc": pd.to_datetime(p["time"], unit="ms"),
                "lat": g[1],
                "lon": g[0],
                "severity": min(int(p["mag"] * 2), 10)
            })
        return pd.DataFrame(rows).sort_values("time_utc", ascending=False)
    except Exception as e:
        st.error(f"Earthquakes error: {e}")
        return pd.DataFrame()

# ----------------------------------------------------------------------
# TROPICAL CYCLONES – NOAA NHC + JTWC RSS
# ----------------------------------------------------------------------
@st.cache_data(ttl=1800)
def fetch_cyclones_month():
    urls = [
        ("NHC", "https://www.nhc.noaa.gov/index-at.xml"),
        ("JTWC", "https://metoc.navy.mil/jtwc/rss/jtwc.xml")
    ]
    cyclones = []
    for src, url in urls:
        try:
            xml = requests.get(url, timeout=12).text
            root = ET.fromstring(xml)
            for item in root.findall(".//item"):
                title = (item.find("title").text or "").strip()
                link = item.find("link").text or ""
                desc = (item.find("description").text or "").lower()

                if any(k in title.lower() for k in ["tropical", "hurricane", "typhoon"]):
                    name = title.split(":")[0].split("-")[0].strip()
                    basin = "Atlantic" if src == "NHC" else "Pacific/Indian"

                    cat = wind_kts = 0
                    for txt in [title, desc]:
                        if "category 5" in txt: cat, wind_kts = 5, 137
                        elif "category 4" in txt: cat, wind_kts = 4, 113
                        elif "category 3" in txt: cat, wind_kts = 3, 96
                        elif "category 2" in txt: cat, wind_kts = 2, 83
                        elif "category 1" in txt: cat, wind_kts = 1, 64
                        elif "tropical storm" in txt: cat, wind_kts = 0, 34

                    lat, lon = 20.0, -70.0
                    if "lat" in desc and "lon" in desc:
                        try:
                            lat = float(desc.split("lat")[1].split()[0].replace("°", ""))
                            lon = float(desc.split("lon")[1].split()[0].replace("°", ""))
                        except: pass

                    cyclones.append({
                        "name": name,
                        "basin": basin,
                        "category": cat,
                        "max_wind_kts": wind_kts,
                        "impact": "Active advisory" if "active" in desc else "Recent event",
                        "article_link": link,
                        "magnitude": wind_kts / 20,
                        "time_utc": pd.NaT,
                        "lat": lat,
                        "lon": lon,
                        "severity": cat if cat else 1
                    })
        except: continue
    return pd.DataFrame(cyclones).drop_duplicates("name")

# ----------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------
st.title("Earthquakes & Tropical Cyclones – Last 30 Days")
st.markdown("Real-time data from **USGS**, **NOAA NHC**, and **JTWC**")

min_intensity = st.sidebar.slider("Minimum Intensity", 0.0, 10.0, 1.0, 0.5)

tab_eq, tab_tc = st.tabs(["Earthquakes", "Tropical Cyclones"])

# --- Earthquakes ---
with tab_eq:
    df = fetch_earthquakes_month()
    if not df.empty:
        df = df[df["magnitude"] >= min_intensity]
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.scatter_mapbox(
                df, lat="lat", lon="lon",
                size="severity", color="magnitude",
                color_continuous_scale="Reds",
                hover_name="name",
                hover_data=["location", "depth_km", "impact", "tsunami"],
                zoom=1, height=560
            )
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Recent Events")
            for _, r in df.head(12).iterrows():
                st.markdown(f"**{r['name']}** – {r['location']}")
                st.caption(f"Depth: {r['depth_km']:.1f} km | Felt: {r['impact']} | Tsunami: {'Yes' if r['tsunami'] else 'No'}")
                st.markdown(f"[USGS Detail]({r['detail_url']})")
                st.divider()
    else:
        st.info("No earthquake data.")

# --- Cyclones ---
with tab_tc:
    df = fetch_cyclones_month()
    if not df.empty:
        df = df[df["magnitude"] >= min_intensity]
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.scatter_mapbox(
                df, lat="lat", lon="lon",
                size="magnitude", color="severity",
                color_continuous_scale="Blues",
                hover_name="name",
                hover_data=["basin", "category", "max_wind_kts", "impact"],
                zoom=1, height=560
            )
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Active / Recent Storms")
            for _, r in df.iterrows():
                st.markdown(f"**{r['name']}** – {r['basin']}")
                st.caption(f"Cat {r['category']} | {r['max_wind_kts']} kts | {r['impact']}")
                st.markdown(f"[Forecast]({r['article_link']})")
                st.divider()
    else:
        st.info("No active cyclones (off-season).")

st.sidebar.info("Data auto-refreshes every 30 min | USGS – NOAA – JTWC")
