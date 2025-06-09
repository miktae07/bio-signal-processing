import streamlit as st

# Cấu hình phải là lệnh đầu tiên Streamlit
st.set_page_config(
    page_title="Biosignal Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

from datetime import datetime
from zoneinfo import ZoneInfo
from page.home import show_home_page
from page.analysis import show_analysis_page
from page.history import show_history_page
from page.image import show_image_page
from page.user import show_user_page
from utils.firebase_utils import list_all_users, get_user_profile

def main():
    if st.session_state.get("need_rerun", False):
        print("[main] 🔁 Đang rerun vì có update từ Firebase")
        st.session_state["need_rerun"] = False
        # if "sensor_groups" not in st.session_state:
        #     st.session_state["sensor_groups"] = {}
        # for sensor, df in st.session_state.get("sensor_groups_buffer", {}).items():
        #     st.session_state["sensor_groups"][sensor] = df
        # st.session_state["sensor_groups_buffer"] = {}

    # 1. Lấy danh sách user từ Firebase (hoặc định nghĩa sẵn)
    user_ids = list_all_users() if "user_ids" not in st.session_state else st.session_state["user_ids"]
    st.session_state["user_ids"] = user_ids
    # 3. Giao diện điều hướng và hiển thị dữ liệu
    now_bangkok = datetime.now(ZoneInfo("Asia/Bangkok"))
    hour = now_bangkok.hour
    greeting = "Chào buổi sáng" if hour < 12 else "Chào buổi chiều" if hour < 18 else "Chào buổi tối"
    st.sidebar.title(f"{greeting}")

    # 2. Sidebar chọn người dùng (dropdown)
    with st.sidebar:
        selected_user = st.selectbox("👤 Chọn Người Dùng", options=user_ids, index=0)
        st.session_state["user_id"] = selected_user
        profile = get_user_profile(selected_user) or {}
        if selected_user:
            ten = profile.get("Tên", selected_user)
            tuoi = profile.get("Tuổi", "")
            dia_chi = profile.get("Địa chỉ", "")
            gioi_tinh = profile.get("Giới tính", "")
        else:
            ten = "Nguyễn Văn A"
            tuoi = "30"
            dia_chi = "123 Đường ABC, Quận XYZ, Thành phố ABC"
            gioi_tinh = "Nam"

        st.markdown(f"**Tên:** {ten}")
        st.markdown(f"**Tuổi:** {tuoi}")
        st.markdown(f"**Địa chỉ:** {dia_chi}")
        st.markdown(f"**Giới tính:** {gioi_tinh}")

    # 4. Hiển thị các trang
    home_page = st.Page(show_home_page, title="Trang Chủ", icon="🏠", default=True)
    analysis = st.Page(show_analysis_page, title="Phân Tích", icon="📊")
    history = st.Page(show_history_page, title="Lịch sử", icon="🕒")
    image = st.Page(show_image_page, title="Phân tích ảnh", icon="📷")
    user = st.Page(show_user_page, title="Người Dùng", icon="👤")

    pg = st.navigation([home_page, analysis, history, image, user], position="sidebar", expanded=True)
    pg.run()

if __name__ == "__main__":
    main()
