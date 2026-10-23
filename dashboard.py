from datetime import datetime, timezone
import streamlit as st
import cv2
import time
from ultralytics import YOLO

from config import BATTERY_CRITICAL_V
from db import initialize
from repository import get_missions, get_telemetry_df

# Konfigurasi Halaman harus di paling atas
st.set_page_config(page_title="Cargo Drone Telemetry & AI", layout="wide")

@st.cache_resource
def _ensure_schema() -> None:

    initialize()

@st.cache_data(ttl=3)
def _load(mission_ids: tuple[int, ...] | None):
    return get_telemetry_df(list(mission_ids) if mission_ids else None)


@st.cache_resource
def load_yolo_model():
   
    return YOLO("best.pt")

def main() -> None:
    _ensure_schema()
    st.title("🚁 Cargo Drone Telemetry & AI Precision Landing")

    # Load Model AI di awal
    model = load_yolo_model()

    try:
        missions = get_missions()
    except Exception as exc:
        st.error(f"Gagal membaca daftar misi: {exc}")
        return

    if not missions:
        st.warning("Belum ada misi. Jalankan `py -m simulator` terlebih dahulu.")
        return

    mission_labels = {m.id: f"#{m.id} — {m.name}" for m in missions}
    selected = st.multiselect(
        "Filter missions",
        options=list(mission_labels.keys()),
        default=list(mission_labels.keys())[:1],
        format_func=lambda mid: mission_labels[mid],
    )

    col_refresh, col_meta = st.columns([1, 4])
    if col_refresh.button("Refresh now"):
        _load.clear()
    col_meta.caption(
        f"Last render: {datetime.now(timezone.utc).isoformat(timespec='seconds')}"
    )

    if not selected:
        st.info("Pilih minimal satu misi untuk menampilkan telemetri.")
        return

    try:
        df = _load(tuple(selected))
    except Exception as exc:
        st.error(f"Gagal memuat telemetri: {exc}")
        return

    if df.empty:
        st.info("Belum ada telemetri untuk misi yang dipilih.")
        return

    last = df.iloc[-1]

    # BANNER STATUS UTAMA
    if not last["link_up"]:
        st.error(
            f"LINK DOWN — paket terakhir {last['timestamp']} "
            f"({last['mission_name']})"
        )
    elif last["battery_v"] < BATTERY_CRITICAL_V:
        st.warning(f"Baterai lemah: {last['battery_v']:.3f} V")
    else:
        st.success(f"Link aktif — paket terakhir {last['timestamp']}")


    # --- PEMBAGIAN LAYAR: KIRI (TELEMETRI) & KANAN (KAMERA AI) ---
    col_telemetry, col_camera = st.columns([1, 1])

    # KIRI: TELEMETRI
    with col_telemetry:
        st.subheader("📊 Metrik Telemetri")
        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)
        
        c1.metric("Samples", len(df))
        c2.metric("Battery (V)", f"{last['battery_v']:.3f}")
        c3.metric("Status", last["mission_status"])
        c4.metric("Link", "UP" if last["link_up"] else "DOWN")

        st.subheader("Battery over time")
        battery_series = df.set_index("timestamp")[["battery_v"]]
        st.line_chart(battery_series, height=250)


    # KANAN: KAMERA AI
    with col_camera:
        st.subheader("📷 Kamera Bawah (Visual Servoing)")
        
        # Tombol kontrol kamera
        col_btn1, col_btn2 = st.columns(2)
        start_cam = col_btn1.button("Aktifkan AI Camera", use_container_width=True)
        stop_cam = col_btn2.button("Matikan Kamera", use_container_width=True)
        
        #render video
        video_placeholder = st.empty()
        
        # Tampilan default jika kamera mati
        if not start_cam:
            video_placeholder.info("Kamera dinonaktifkan. Tekan 'Aktifkan AI Camera' untuk melihat simulasi pendaratan.")
            
        if start_cam:
            
            cap = cv2.VideoCapture("sample_video.mp4")
            
            if not cap.isOpened():
                video_placeholder.error("Gagal membuka sample_video.mp4! Pastikan file ada di folder.")
            else:
                while cap.isOpened() and not stop_cam:
                    ret, frame = cap.read()
                    if not ret:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Ulangi video (looping)
                        continue
                    
                    
                    results = model.predict(frame, imgsz=320, conf=0.6, verbose=False)
                    annotated_frame = results[0].plot()
                    
                    # Konversi warna 
                    frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                    
                    # Tampilkan frame di dashboard
                    video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                    
                    # Proteksi CPU/RAM
                    time.sleep(0.05) 
                    
                cap.release()
                video_placeholder.warning("Simulasi kamera dihentikan.")


   
    st.markdown("---")
    col_title, col_dl = st.columns([3, 1])
    col_title.subheader("Riwayat Telemetri Lengkap")

    view = df.sort_values("timestamp", ascending=False).copy()
    view["link_up"] = view["link_up"].map({True: "UP", False: "DOWN"})

    csv_bytes = view.to_csv(index=False).encode("utf-8")
    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    col_dl.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name=f"telemetry_{timestamp_str}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.dataframe(view, width="stretch", hide_index=True)

if __name__ == "__main__":
    main()