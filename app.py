import streamlit as st
import pandas as pd

# Cấu hình trang
st.set_page_config(
    page_title="Công cụ tính Lãi tiết kiệm",
    page_icon="💰",
    layout="centered"
)

st.title("💰 Công Cụ Tính Lãi Tiết Kiệm")
st.write("Nhập thông tin tiền gửi của bạn bên dưới để xem dự tính lãi suất.")

# --- PHẦN NHẬP DỮ LIỆU ---
col1, col2 = st.columns(2)

with col1:
    so_tien_gui = st.number_input(
        "Số tiền gửi (VNĐ):",
        min_value=1_000_000,
        value=100_000_000,
        step=10_000_000,
        format="%d"
    )
    
    ky_han_thang = st.number_input(
        "Kỳ hạn gửi (tháng):",
        min_value=1,
        max_value=120,
        value=12,
        step=1
    )

    loai_lai = st.radio(
        "Phương pháp tính lãi:",
        options=["Lãi đơn", "Lãi kép"],
        help="Lãi đơn: Tiền lãi không gộp gốc. Lãi kép: Tiền lãi định kỳ gộp vào gốc để tính lãi cho kỳ tiếp theo."
    )

with col2:
    lai_suat_nam = st.number_input(
        "Lãi suất (%/năm):",
        min_value=0.1,
        max_value=30.0,
        value=6.0,
        step=0.1,
        format="%.2f"
    )

    hinh_thuc_nhan = st.selectbox(
        "Hình thức nhận lãi:",
        options=["Nhận lãi cuối kỳ", "Nhận lãi hàng tháng", "Nhận lãi hàng quý"]
    )

# --- XỬ LÝ TÍNH TOÁN ---
def tinh_lai_tiet_kiem(so_tien, ky_han, lai_suat, hinh_thuc, loai_tinh_lai):
    # Xác định số tháng của mỗi kỳ nhận lãi
    if hinh_thuc == "Nhận lãi hàng tháng":
        thang_moi_ky = 1
    elif hinh_thuc == "Nhận lãi hàng quý":
        thang_moi_ky = 3
    else: # Cuối kỳ
        thang_moi_ky = ky_han

    so_lan_nhan_lai = ky_han / thang_moi_ky
    lai_suat_ky = (lai_suat / 100) * (thang_moi_ky / 12)
    
    goc = so_tien
    tong_lai = 0
    lich_suki = []

    if loai_tinh_lai == "Lãi đơn":
        # Với lãi đơn, tiền lãi mỗi kỳ luôn cố định
        lai_dinh_ky = goc * lai_suat_ky
        tong_lai = lai_dinh_ky * so_lan_nhan_lai
        
        # Tạo lịch trả lãi
        goc_tich_luy = goc
        for i in range(1, int(so_lan_nhan_lai) + 1):
            thang = i * thang_moi_ky
            if thang > ky_han:
                break
            lich_suki.append({
                "Kỳ": i,
                "Tháng": thang,
                "Tiền gốc (VNĐ)": goc,
                "Lãi nhận được (VNĐ)": lai_dinh_ky,
                "Tổng tiền nhận đến kỳ này (VNĐ)": goc + (lai_dinh_ky * i)
            })
            
    else: # Lãi kép
        goc_tich_luy = goc
        for i in range(1, int(so_lan_nhan_lai) + 1):
            thang = i * thang_moi_ky
            if thang > ky_han:
                break
            lai_ky_nay = goc_tich_luy * lai_suat_ky
            tong_lai += lai_ky_nay
            goc_tich_luy += lai_ky_nay
            
            lich_suki.append({
                "Kỳ": i,
                "Tháng": thang,
                "Tiền gốc đầu kỳ (VNĐ)": goc_tich_luy - lai_ky_nay,
                "Lãi kỳ này (VNĐ)": lai_ky_nay,
                "Gốc + Lãi tích lũy (VNĐ)": goc_tich_luy
            })
        
        lai_dinh_ky = tong_lai / so_lan_nhan_lai if so_lan_nhan_lai > 0 else 0

    tong_tiengoc_va_lai = so_tien + tong_lai
    return lai_dinh_ky, tong_lai, tong_tiengoc_va_lai, pd.DataFrame(lich_suki)

# Nút tính toán
st.markdown("---")
if st.button("🧮 Tính kết quả", type="primary", use_container_width=True):
    # Kiểm tra điều kiện hình thức nhận lãi phù hợp kỳ hạn
    if hinh_thuc_nhan == "Nhận lãi hàng quý" and ky_han_thang < 3:
        st.warning("⚠️ Kỳ hạn phải từ 3 tháng trở lên để chọn nhận lãi hàng quý.")
    else:
        lai_dinh_ky, tong_lai, tong_goc_lai, df_lich = tinh_lai_tiet_kiem(
            so_tien_gui, ky_han_thang, lai_suat_nam, hinh_thuc_nhan, loai_lai
        )

        # Display results
        st.subheader("📊 Kết quả tính toán")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Tiền lãi định kỳ (trung bình)", f"{lai_dinh_ky:,.0f} VNĐ")
        m2.metric("Tổng tiền lãi", f"{tong_lai:,.0f} VNĐ")
        m3.metric("Tổng gốc + lãi", f"{tong_goc_lai:,.0f} VNĐ")

        # Bảng lịch nhận lãi
        if not df_lich.empty:
            st.write("---")
            st.subheader("📅 Chi tiết lịch nhận lãi theo từng kỳ")
            
            # Format các cột số tiền trong DataFrame cho dễ nhìn
            df_formatted = df_lich.copy()
            for col in df_formatted.columns:
                if "VNĐ" in col:
                    df_formatted[col] = df_formatted[col].apply(lambda x: f"{x:,.0f}")
                    
            st.dataframe(df_formatted, use_container_width=True, hide_index=True)
