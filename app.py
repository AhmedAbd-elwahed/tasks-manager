import streamlit as st
import pandas as pd
import datetime
import re
import json
import os

# إعدادات الصفحة
st.set_page_config(
    page_title="Sameq Rank - Agency Dashboard", 
    page_icon="🦅", 
    layout="wide"
)

LOGO_URL = "https://lh3.googleusercontent.com/d/1Gxf8uTnDc_u4ivDQ-ZIIY0j_XFrJwuom"
CONFIG_FILE = "config_links.json"

def load_config():
    default_config = {
        "username": "admin",
        "password": "1234",
        "companies": {
            "Tam-Crete Engineering": {"link": "", "target": 20},
            "tam-building": {"link": "", "target": 20},
            "Al-Jazeera Office Furniture": {"link": "", "target": 25},
            "Sameq Rank": {"link": "", "target": 15}
        }
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return default_config

def save_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

config = load_config()

# --- تنسيق عام ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; direction: rtl; }
    [data-testid="stSidebar"] { background-color: #0f172a; color: #f8fafc; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #f8fafc !important; }
    </style>
""", unsafe_allow_html=True)

# --- تسجيل الدخول (تصحيح آمن لمنع KeyError) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🔐 تسجيل الدخول — Sameq Rank</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        try: st.image(LOGO_URL, width=140)
        except: pass
        
        user_input = st.text_input("اسم المستخدم:")
        pass_input = st.text_input("كلمة المرور:", type="password")
        
        if st.button("دخول", use_container_width=True):
            if user_input == config.get("username", "admin") and pass_input == config.get("password", "1234"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
    st.stop()

# --- الهيدر الرئيسي ---
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 25px 30px; border-radius: 16px; color: white; box-shadow: 0 8px 20px rgba(0,0,0,0.12); margin-bottom: 25px; display: flex; align-items: center; gap: 20px;">
        <img src="{LOGO_URL}" width="80" style="border-radius: 12px; background: white; padding: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
        <div>
            <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 700;">لوحة تحكم أحمد — Sameq Rank</h1>
            <p style="color: #93c5fd; margin: 5px 0 0 0; font-size: 15px;">نظام متابعة وإدارة مهام الشركات وأداء الأنشطة الرقمية بذكاء وأمان</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
st.sidebar.header("⚙️ لوحة التحكم والإعدادات")
companies_dict = config.get("companies", {})
available_companies = list(companies_dict.keys())

selected_companies = st.sidebar.multiselect("اختر الشركات للمتابعة:", options=available_companies, default=available_companies)

with st.sidebar.expander("🔗 إعداد الروابط والأهداف الشهرية"):
    st.write("ضع رابط الشيت وأدخل الهدف الشهري للمهام:")
    updated = False
    for comp in available_companies:
        st.markdown(f"**🏢 {comp}**")
        curr_link = companies_dict[comp].get("link", "")
        curr_target = companies_dict[comp].get("target", 20)
        
        new_link = st.text_input(f"رابط شيت {comp}:", value=curr_link, key=f"link_{comp}")
        new_target = st.number_input(f"الهدف الشهري اليدوي:", value=int(curr_target), min_value=1, max_value=200, key=f"target_{comp}")
        
        if new_link != curr_link or new_target != curr_target:
            companies_dict[comp]["link"] = new_link
            companies_dict[comp]["target"] = new_target
            updated = True
        st.markdown("---")
        
    if updated:
        config["companies"] = companies_dict
        save_config(config)

st.sidebar.markdown("---")
date_mode = st.sidebar.radio("طريقة عرض التواريخ:", ["تاريخ اليوم", "تاريخ محدد", "فترة زمنية"])
today = datetime.date.today()

if date_mode == "تاريخ اليوم":
    start_date, end_date = today, today
elif date_mode == "تاريخ محدد":
    selected_single_date = st.sidebar.date_input("اختر التاريخ المطلوب:", today)
    start_date, end_date = selected_single_date, selected_single_date
else:
    date_range = st.sidebar.date_input("اختر الفترة (من - إلى):", [today, today])
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = today, today

def get_csv_export_url(url):
    match_id = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if not match_id: return url
    sheet_id = match_id.group(1)
    match_gid = re.search(r'[?&]gid=([0-9]+)', url) or re.search(r'#gid=([0-9]+)', url)
    gid = match_gid.group(1) if match_gid else '0'
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

@st.cache_data(ttl=5)
def fetch_all_tasks(config_json_str):
    cfg = json.loads(config_json_str)
    companies_dict = cfg.get("companies", {})
    all_tasks = []
    for comp, data in companies_dict.items():
        url = data.get("link", "")
        if not url.strip(): continue
        try:
            csv_url = get_csv_export_url(url)
            df = pd.read_csv(csv_url)
            df.columns = [str(col).strip() for col in df.columns]
            
            service_col = next((c for c in df.columns if "خدمة" in c or "خدمه" in c or "مهمة" in c), df.columns[0])
            date_col = next((c for c in df.columns if "تاريخ" in c), df.columns[1] if len(df.columns) > 1 else "")
            status_col = next((c for c in df.columns if "حالة" in c or "الحالة" in c), df.columns[2] if len(df.columns) > 2 else "")
            notes_col = next((c for c in df.columns if "ملاحظات" in c), "")

            for _, row in df.iterrows():
                task_raw = str(row.get(service_col, "")).strip()
                if not task_raw or task_raw.lower() in ["nan", "none", "null", "0", "unnamed: 0"]:
                    continue
                
                date_str = str(row.get(date_col, "")).strip() if date_col else ""
                try:
                    task_date = pd.to_datetime(date_str).date()
                except:
                    continue 
                
                status = str(row.get(status_col, "غير محدد")).strip() if status_col else "غير محدد"
                notes = str(row.get(notes_col, "")).strip() if notes_col else ""
                
                all_tasks.append({
                    "company": comp,
                    "task": task_raw,
                    "date": task_date,
                    "status": status,
                    "notes": notes if notes.lower() != "nan" else "",
                })
        except Exception as e:
            pass
    return all_tasks

config_json_str = json.dumps(config)
real_tasks = fetch_all_tasks(config_json_str)

# --- 2. قسم ملخص الأداء والتقييم ---
st.markdown("""
    <div style="background-color: #dcfce7; padding: 25px; border-radius: 16px; border: 2px solid #86efac; box-shadow: 0 4px 12px rgba(0,0,0,0.04); margin-bottom: 25px;">
        <h3 style="color: #166534; margin-top: 0;">📊 ملخص الأداء والإنتاجية الشهرية</h3>
""", unsafe_allow_html=True)

company_stats = []
chart_data = {}

for comp in selected_companies:
    total_company_tasks = [t for t in real_tasks if t["company"] == comp]
    completed_count = sum(1 for t in total_company_tasks if "تم" in t["status"])
    
    # حساب إجمالي عدد المهام المكتوبة الحقيقي في الشيت
    total_written_tasks = len(total_company_tasks)
    display_target = total_written_tasks if total_written_tasks > 0 else config["companies"][comp].get("target", 20)
    
    company_stats.append({
        "الشركة": comp,
        "المنجز": completed_count,
        "المستهدف": display_target,
        "النسبة": int((completed_count / display_target) * 100) if display_target > 0 else 0
    })
    chart_data[comp] = completed_count

if company_stats:
    cols = st.columns(len(company_stats) if len(company_stats) <= 4 else 4)
    for idx, stat in enumerate(company_stats):
        col_idx = idx % 4
        with cols[col_idx]:
            st.metric(
                label=stat["الشركة"],
                value=f"{stat['المنجز']} / {stat['المستهدف']} مهمة",
                delta=f"{stat['النسبة']}% من المستهدف"
            )

st.markdown('</div>', unsafe_allow_html=True)

# --- تصفية المهام ---
filtered_tasks = []
for t in real_tasks:
    if t["company"] not in selected_companies: continue
    if start_date <= t["date"] <= end_date:
        filtered_tasks.append(t)

# --- 3. جدول المهام المطابقة ---
st.markdown(f"""
    <div style="background-color: #dbeafe; padding: 25px; border-radius: 16px; border: 2px solid #93c5fd; box-shadow: 0 4px 12px rgba(0,0,0,0.04); margin-bottom: 25px;">
        <h3 style="color: #1e40af; margin-top: 0;">📋 جدول المهام المطابقة ({len(filtered_tasks)} مهمة):</h3>
""", unsafe_allow_html=True)

has_links = any(d.get("link", "").strip() for d in config["companies"].values())

if not has_links:
    st.warning("⚠️ برجاء وضع روابط Google Sheets للشركات من القائمة الجانبية لتظهر البيانات.")
elif not real_tasks:
    st.warning("⚠️ تم إدخال روابط، ولكن لم يتم جلب أي بيانات. تأكد أن الشيت عام وأن الأعمدة مطابقة ('الخدمة', 'تاريخ بدء الخدمة', 'الحالة').")
elif not filtered_tasks:
    st.warning(f"⚠️ لا توجد مهام مطابقة للفترة المحددة ({start_date} إلى {end_date}).")
else:
    for i, t in enumerate(filtered_tasks):
        status_str = t["status"]
        status_color = "🟢" if "تم" in status_str else ("🔴" if "بدأ" in status_str or "تنفيذ" in status_str else "🟡")
        
        card_html = f"""
        <div style="background-color: white; padding: 16px; border-radius: 10px; border-right: 6px solid #1e3a8a; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.03); margin-bottom: 10px;">
            <b>🏢 {t['company']}</b> | 📅 {t['date']}<br>
            📌 <b>{t['task']}</b><br>
            {status_color} الحالة: <b>{t['status']}</b>
            {f" | ملاحظات: {t['notes']}" if t['notes'] else ""}
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
    
    df_export = pd.DataFrame(filtered_tasks)
    df_export = df_export.rename(columns={"company": "الشركة", "task": "الخدمة / المهمة", "date": "التاريخ", "status": "الحالة", "notes": "ملاحظات"})
    csv_data = df_export.to_csv(index=False, encoding="utf-8-sig")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="📥 تحميل تقرير المهام المصفاة (Excel / CSV)",
        data=csv_data,
        file_name=f"SameqRank_Tasks_Report_{start_date}_to_{end_date}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# --- 4. الرسم البياني ---
if chart_data:
    st.markdown("""
        <div style="background-color: #f3e8ff; padding: 25px; border-radius: 16px; border: 2px solid #d8b4fe; box-shadow: 0 4px 12px rgba(0,0,0,0.04); margin-bottom: 25px;">
            <h3 style="color: #6b21a8; margin-top: 0;">📈 الرسم البياني للمهام المنجزة لكل شركة</h3>
    """, unsafe_allow_html=True)
    chart_df = pd.DataFrame(list(chart_data.items()), columns=["الشركة", "المهام المنجزة"]).set_index("الشركة")
    st.bar_chart(chart_df)
    st.markdown('</div>', unsafe_allow_html=True)