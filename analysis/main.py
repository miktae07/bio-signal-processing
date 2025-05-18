import streamlit as st

# PHẢI: set_page_config ở dòng Streamlit đầu tiên
st.set_page_config(
    page_title="Biosignal Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add dark mode toggle in the sidebar
theme_options = {"Light": "light", "Dark": "dark", "Auto": "auto"}
selected_theme = st.sidebar.selectbox(
    "Chọn chế độ giao diện",
    list(theme_options.keys()),
    index=0,  # Default to "Sáng (Light)"
)

# Apply the selected theme (workaround since Streamlit doesn't support dynamic theme changes)
if selected_theme:
    st._config.set_option("theme.base", theme_options[selected_theme])

from page.home import show_home_page
from page.analysis import show_analysis_page
from page.history import show_history_page
from page.image import show_image_page

home_page = st.Page(show_home_page, title="Trang Chủ", icon="🏠", default=True)
analysis = st.Page(show_analysis_page, title="Phân Tích", icon="📊")
history = st.Page(show_history_page, title="Lịch sử", icon="🕒")
image = st.Page(show_image_page, title="Phân tích ảnh", icon="📷")

pg = st.navigation([home_page, analysis, history, image], position="sidebar", expanded=True)
pg.run()