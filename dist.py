import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
import io
import streamlit.components.v1 as components

# ==========================================
# 1. إعدادات الصفحة المتقدمة
# ==========================================
st.set_page_config(page_title="بوابة إ-قسمي | مديرية الحوز", page_icon="🎓", layout="wide")

# ==========================================
# 2. تصميم CSS احترافي
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stApp {
        background-color: #f4f7f9;
    }
    
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        text-align: right !important;
        direction: rtl !important;
    }
    div[data-testid="stMarkdownContainer"] {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* إخفاء شريط وأزرار Streamlit */
    #MainMenu {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    .viewerBadge_container {display: none !important;}
    .viewerBadge_link {display: none !important;}
    
    /* بطاقات لوحة التحكم */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e6ed;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
        border-right: 5px solid #1f77b4;
        transition: transform 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stMetricValue"] {
        color: #2c3e50;
        font-size: 2rem !important;
        font-weight: 700;
    }
    
    /* صندوق تسجيل الدخول المخصص */
    .login-card [data-testid="stForm"] {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid #e5e7eb;
    }
    
    .system-title {
        color: #1d4ed8;
        text-align: center !important;
        font-size: 30px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    .system-subtitle {
        color: #64748b;
        text-align: center !important;
        font-size: 16px;
        margin-bottom: 25px;
    }
    
    .presentation-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 30px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. نظام تسجيل الدخول والصلاحيات
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'username': '', 'role': ''})

users_db = {
    "jalal": {"password": "admin", "role": "admin", "name": "جلال الكميلي"},
    "tuteur1": {"password": "123", "role": "tuteur", "name": "مكون 1"}
}

# ==========================================
# 4. دالة قراءة البيانات الذكية
# ==========================================
FILE_PATH = "eQissmi_donnees_Haouz(1).xlsx"

@st.cache_data(ttl=60)
def load_data():
    if os.path.exists(FILE_PATH):
        try:
            for i in range(5):
                df_temp = pd.read_excel(FILE_PATH, header=i)
                df_temp.columns = df_temp.columns.astype(str).str.strip()
                if 'Validé par mérite (X)' in df_temp.columns or 'Nom & Prénom' in df_temp.columns:
                    return df_temp
            
            df_fallback = pd.read_excel(FILE_PATH)
            df_fallback.columns = df_fallback.columns.astype(str).str.strip()
            return df_fallback
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

df = load_data()

# ==========================================
# 5. القائمة الجانبية (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: #1f77b4;'>مشروع إ-قسمي 2025</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    if not st.session_state['logged_in']:
        # تبدأ القائمة بصفحة التقديم كخيار افتراضي أولي
        menu = st.radio("القائمة الرئيسية:", ["🏠 التقديم وطلب الانخراط", "🔐 ولوج الإدارة"])
    else:
        role_title = "رئيس مصلحة" if st.session_state['role'] == 'admin' else "مكون إقليمي"
        st.markdown(f"<div style='text-align: center;'><strong>{st.session_state['username']}</strong><br><span style='color: #7f8c8d; font-size: 0.9em;'>{role_title}</span></div>", unsafe_allow_html=True)
        st.markdown("---")
        menu = st.radio("خيارات الفضاء الإداري:", [
            "📊 لوحة القيادة التفاعلية", 
            "📋 اللوائح الإسمية", 
            "🔍 التحقق من الاستفادة (PPR)",
            "📤 تحديث قاعدة البيانات"
        ])
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

# ==========================================
# 6. الحسابات والمؤشرات الإجمالية
# ==========================================
total = len(df)
valide_merite = valide_compensation = en_attente = taux = 0

if total > 0:
    if 'Validé par mérite (X)' in df.columns:
        valide_merite = len(df[df['Validé par mérite (X)'].astype(str).str.upper() == 'X'])
    if 'Validé par compensasion (X)' in df.columns:
        valide_compensation = len(df[df['Validé par compensasion (X)'].astype(str).str.upper() == 'X'])
    
    en_attente = total - (valide_merite + valide_compensation)
    if total > 0:
        taux = round(((valide_merite + valide_compensation) / total) * 100, 1)

# ==========================================
# 7. محتوى الصفحات
# ==========================================

# ------------------------------------------
# 1. صفحة البداية للعموم (التقديم + الفيديو + الاستمارة)
# ------------------------------------------
if menu == "🏠 التقديم وطلب الانخراط":
    # عرض الشعار في أعلى صفحة البداية
    c_logo1, c_logo2, c_logo3 = st.columns([1, 2, 1])
    with c_logo2:
        try:
            st.image("logo_2026.png", use_container_width=True)
        except Exception:
            pass

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📽️ العرض التقديمي لمشروع إ-قسمي")
    with st.container():
        st.markdown("<div class='presentation-box'>", unsafe_allow_html=True)
        # رابط الفيديو التعريفي للمشروع
        st.video("https://www.youtube.com/watch?v=J_jKjB7Z8oA")
        st.info("💡 المرجو الاطلاع على العرض التقديمي أعلاه للتعرف على محاور وأهداف المشروع قبل تسجيل الطلب.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📝 استمارة الانخراط في التكوين")
    
    with st.form("public_registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            nom_prenom = st.text_input("الاسم والنسب (Nom & Prénom):*")
            ppr = st.text_input("رقم التأجير (PPR):*")
        with col2:
            aref = st.text_input("الأكاديمية (AREF):", value="Marrakech - Safi", disabled=True)
            dp = st.text_input("المديرية الإقليمية (DP):", value="Al Haouz", disabled=True)
            
        submitted = st.form_submit_button("تأكيد التسجيل 💾", type="primary", use_container_width=True)
        
        if submitted:
            if nom_prenom == "" or ppr == "":
                st.error("المرجو ملء الحقول الإجبارية (الاسم والنسب ورقم التأجير).")
            else:
                ppr_clean = ppr.strip()
                if not df.empty and 'PPR' in df.columns and ppr_clean in df['PPR'].astype(str).str.strip().values:
                    st.error(f"❌ عذراً، الأستاذ(ة) برقم التأجير {ppr_clean} مسجل مسبقاً في قاعدة البيانات.")
                else:
                    new_row = {
                        "N°": len(df) + 1, 
                        "Nom & Prénom": nom_prenom, 
                        "PPR": ppr_clean, 
                        "AREF (Nom officiel)": "Marrakech - Safi", 
                        "DP (Nom Officiel)": "Al Haouz", 
                        "Validé par mérite (X)": "", 
                        "Validé par compensasion (X)": ""
                    }
                    df_new_row = pd.DataFrame([new_row])
                    df_updated = df_new_row if df.empty else pd.concat([df, df_new_row], ignore_index=True)
                    
                    try:
                        df_updated.to_excel(FILE_PATH, index=False)
                        st.cache_data.clear()
                        st.success(f"✅ تم تسجيل الأستاذ(ة) {nom_prenom} بنجاح! شكراً لانخراطكم.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الحفظ: {e}")

# ------------------------------------------
# 2. صفحة تسجيل الدخول للإدارة فقط
# ------------------------------------------
elif menu == "🔐 ولوج الإدارة" and not st.session_state['logged_in']:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # الشعار في الوسط
    logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])
    with logo_col2:
        try:
            st.image("logo_2026.png", use_container_width=True)
        except Exception:
            pass
            
    st.markdown("<div class='system-title'>نظام تتبع خطط العمل</div>", unsafe_allow_html=True)
    st.markdown("<div class='system-subtitle'>الأكاديمية الجهوية للتربية والتكوين - مراكش آسفي</div>", unsafe_allow_html=True)

    # صندوق الدخول بتصميم البطاقة
    _, form_col, _ = st.columns([1, 2, 1])
    with form_col:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        with st.form("admin_login_form"):
            st.markdown("<h3 style='text-align: right; color: #1e293b; font-weight: bold;'>تسجيل الدخول</h3>", unsafe_allow_html=True)
            st.markdown("<hr style='margin-top: 0px; margin-bottom: 20px;'>", unsafe_allow_html=True)
            
            username_input = st.text_input("اسم المستخدم:")
            password_input = st.text_input("كلمة المرور:", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("تسجيل الدخول", use_container_width=True)
            
            if submit_button:
                if username_input in users_db and users_db[username_input]["password"] == password_input:
                    st.session_state.update({'logged_in': True, 'username': users_db[username_input]["name"], 'role': users_db[username_input]["role"]})
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير
