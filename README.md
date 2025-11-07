# Earthquakes & Tropical Cyclones Monitor

**Real-time dashboard tracking global earthquakes (M≥1.0) and tropical cyclones over the last 30 days** — powered by open data from **USGS**, **NOAA NHC**, and **JTWC**.

Live Demo: [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://realtime-disasters-monitoring-cxephdtyww4jf2dwjunnhq.streamlit.app/)

---

## Live App Preview

When you open the app, you'll see a **clean, responsive dashboard** that loads fresh data every 30 minutes:

- **Header**: "Earthquakes & Tropical Cyclones – Last 30 Days" with a subtitle crediting USGS, NOAA NHC, and JTWC.
- **Sidebar**: A slider labeled "Minimum Intensity" (default: 1.0) to filter events by magnitude or wind-scaled severity. Below it, an info box: "Data auto-refreshes every 30 min | USGS – NOAA – JTWC".
- **Main Content**: Two tabs – **Earthquakes** and **Tropical Cyclones**.
  - **Earthquakes Tab**: Left side shows an interactive world map (OpenStreetMap basemap) with red markers sized by severity and colored by magnitude. Hover for name, location, depth, impact, and tsunami info. Right side lists the top 12 recent events (e.g., "M4.2 – 150 km S of Atka, Alaska" with depth, felt reports, tsunami status, and clickable USGS detail link). Data pulls ~500+ events from the last 30 days, filtered dynamically.
  - **Tropical Cyclones Tab**: Similar layout with a blue-themed map showing storm markers sized by wind speed. Hover reveals basin, category, max winds (kts), and impact. Right side lists active/recent storms (e.g., "Tropical Storm Name – Atlantic" with Cat level, winds, status, and forecast link). Currently shows 0–5 events (off-season; updates in real-time during hurricane season).
- **Real-Time Behavior**: Maps zoom/pan smoothly; data refreshes automatically. If no events match the filter, a friendly info message appears (e.g., "No active cyclones (off-season).").

The app is fully interactive – no static images, just live maps and tables updating from public APIs.

---

## Features

- **Interactive World Maps**: Zoom, pan, and hover for details on earthquakes (sized by severity, colored by magnitude) and cyclones (sized by wind speed, colored by category).
- **Rich Event Details**:
  - **Earthquakes**: Magnitude, location, depth (km), felt reports, tsunami risk, USGS detail links.
  - **Tropical Cyclones**: Storm name, basin (Atlantic/Pacific-Indian), Saffir-Simpson category (0-5), max wind speed (kts), advisory status, forecast links.
- **Filtering**: Sidebar slider to filter by minimum intensity (magnitude for quakes, wind-scaled for cyclones).
- **Auto-Refresh**: Data updates every 30 minutes (no manual reload needed).
- **Responsive Layout**: Map on left, event list with clickable links on right.

---

## How to Run Locally

```bash
# Clone the repo
git clone https://github.com/yourusername/realtime-disasters-monitoring.git
cd realtime-disasters-monitoring

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
