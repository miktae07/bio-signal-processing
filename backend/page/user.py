import streamlit as st
from utils.firebase_utils import init_firebase, get_user_profile, create_user_profile, list_all_users
import firebase_admin
from firebase_admin import db

def delete_user(user_id):
    """
    Xóa người dùng khỏi Firebase.
    """
    init_firebase()
    try:
        user_ref = db.reference(f"/Users/{user_id}")
        user_ref.delete()
        st.success(f"Đã xóa người dùng: {user_id}")
    except Exception as e:
        st.error(f"Lỗi khi xóa: {e}")

def update_user_profile(user_id, profile_data):
    """
    Cập nhật thông tin người dùng.
    """
    init_firebase()
    try:
        user_ref = db.reference(f"/Users/{user_id}/Profile")
        user_ref.update(profile_data)
        st.success(f"Hồ sơ `{user_id}` đã được cập nhật.")
    except Exception as e:
        st.error(f"Lỗi khi cập nhật: {e}")

def show_user_page():
    st.header("👤 Trang Người Dùng")

    tab1, tab2, tab3 = st.tabs(["📋 Danh sách người dùng", "➕ Thêm người dùng", "✏️ Sửa/Xóa người dùng"])

    # Tab 1: Danh sách
    with tab1:
        users = list_all_users()
        st.subheader("Danh sách người dùng hiện tại:")
        if users:
            for uid in users:
                profile = get_user_profile(uid)
                if profile:
                    st.markdown(f"- `{uid}`: {profile.get('Tên', '')}, {profile.get('Tuổi', '')} tuổi, {profile.get('Địa chỉ', '')}, {profile.get('Giới tính', '')}")
        else:
            st.info("Không có người dùng nào.")

    # Tab 2: Thêm mới
    with tab2:
        st.subheader("Tạo người dùng mới:")
        with st.form("add_user_form"):
            user_id = st.text_input("User ID")
            ten = st.text_input("Tên")
            tuoi = st.number_input("Tuổi", min_value=0, max_value=120, step=1)
            dia_chi = st.text_area("Địa chỉ")
            gioi_tinh = st.selectbox("Giới tính", ["Nam", "Nữ", "Khác"])
            submitted = st.form_submit_button("Tạo tài khoản")

            if submitted:
                if not all([user_id, ten, dia_chi]):
                    st.error("Vui lòng điền đầy đủ thông tin.")
                else:
                    try:
                        create_user_profile(user_id, ten, int(tuoi), dia_chi, gioi_tinh)
                        st.success(f"Đã thêm người dùng `{user_id}`.")
                    except Exception as e:
                        st.error(f"Lỗi khi tạo người dùng: {e}")

    # Tab 3: Sửa/Xóa
    with tab3:
        st.subheader("Chỉnh sửa hoặc xóa người dùng")
        users = list_all_users()
        if users:
            selected_user = st.selectbox("Chọn người dùng", users)
            profile = get_user_profile(selected_user)
            if profile:
                ten = st.text_input("Tên", profile.get("Name", ""))
                tuoi = st.number_input("Tuổi", min_value=0, max_value=120, value=profile.get("Age", 0), step=1)
                dia_chi = st.text_area("Địa chỉ", profile.get("Address", ""))
                gioi_tinh = st.selectbox("Giới tính", ["Nam", "Nữ", "Khác"], index=["Nam", "Nữ", "Khác"].index(profile.get("Sex", "Khác")))

                if st.button("Cập nhật"):
                    profile_data = {
                        "Name": ten,
                        "Age": int(tuoi),
                        "Address": dia_chi,
                        "Sex": gioi_tinh,
                    }
                    update_user_profile(selected_user, profile_data)

                if st.button("❌ Xóa người dùng"):
                    delete_user(selected_user)
        else:
            st.info("Không có người dùng nào.")
