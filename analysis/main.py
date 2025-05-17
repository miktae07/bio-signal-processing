import streamlit as st

# PHẢI: set_page_config ở dòng Streamlit đầu tiên
st.set_page_config(
    page_title="Biosignal Dashboard",
    layout="wide",
)

from page.home      import show_home_page
from page.analysis  import show_analysis_page
from page.history  import show_history_page
from page.image import show_image_page

home_page = st.Page(show_home_page, title="Trang Chủ", icon="🏠", default=True)
analysis  = st.Page(show_analysis_page,   title="Phân Tích", icon="📊")
history  = st.Page(show_history_page,   title="Lịch sử",   icon="🕒")
image  = st.Page(show_image_page,   title="Phân tích ảnh",   icon="📷")

pg = st.navigation([home_page, analysis, history, image], position="sidebar", expanded=True)
pg.run()
