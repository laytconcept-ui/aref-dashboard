import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
import io

# مكتبات توليد ملفات PDF الاحترافية
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="بوابة إ-قسمي | مديرية الحوز", page_icon="🎓", layout="wide")

# ==========================================
# 2. تصميم CSS ومحاذاة الواجهة
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stApp { background-color: #f4f7f9; }
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        text-align: right !important; direction: rtl !important;
    }
    div[data-testid="stMarkdownContainer"] { text-align: right !important; direction: rtl !important; }
    #MainMenu, footer, header, [data-testid="stToolbar"], .viewerBadge_container { visibility: hidden !important; display: none !important; }
    
    div[data-testid="metric-container"] {
        background-color: #ffffff; border: 1px solid #e0e6ed; padding: 20px;
        border-radius: 12px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
        border-right: 5px solid #1f77b4;
    }
    div[data-testid="stMetricValue"] { color: #2c3e50; font-size: 2rem !important; font-weight: 700; }
    .system-title { color: #1d4ed8; text-align: center !important; font-size: 30px; font-weight: 700; margin-top: 10px; }
    .system-subtitle { color: #64748b; text-align: center !important; font-size: 16px; margin-bottom: 25px; }
    .presentation-box { background-color: #ffffff; padding: 20px; border-radius: 12px; margin-bottom: 25px; border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. الصلاحيات وتسجيل الدخول
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'username': '', 'role': ''})

users_db = {
    "jalal": {"password": "admin", "role": "admin", "name": "جلال الكميلي"},
    "tuteur1": {"password": "123", "role": "tuteur", "name": "مكون 1"}
}

# ==========================================
# 4. دالة إدارة البيانات (قراءة وحفظ)
# ==========================================
FILE_PATH = "eQissmi_donnees_Haouz(1).xlsx"

@st.cache_data(ttl=30)
def load_data():
    if os.path.exists(FILE_PATH):
        try:
            for h in [0, 1, 2]:
                try:
                    df_temp = pd.read_excel(FILE_PATH, header=h)
                    df_temp.columns = df_temp.columns.astype(str).str.strip()
                    if 'Bénéficiaire' in df_temp.columns or 'Statut: Validé' in df_temp.columns:
                        return df_temp
                except Exception:
                    continue
            df_alt = pd.read_excel(FILE_PATH)
            df_alt.columns = df_alt.columns.astype(str).str.strip()
            return df_alt
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

df = load_data()

# توحيد الأعمدة وإضافة الحقول الجديدة إن لم تكن متوفرة
default_columns = ['Session', 'Tuteur', 'Bénéficiaire', 'PPR', 'Cycle', 'Établissement', 'Statut: Validé']
if not df.empty:
    for col in default_columns:
        if col not in df.columns:
            df[col] = "غير محدد"
    df['Statut: Validé'] = df['Statut: Validé'].astype(str).str.strip()
    df['PPR'] = df['PPR'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

# ==========================================
# --- 5. التقرير التركيبي التنفيذي (Executive PDF) ---
elif menu == "📄 التقرير التركيبي التنفيذي" and st.session_state['logged_in']:
    st.markdown("### 📄 إعداد وتصدير التقرير التنفيذي الرسمي (PDF)")
    st.info("💡 تقرير رسمي ملخص في صفحة واحدة مخصص لتقديمه للسيد المدير الإقليمي ورؤساء المصالح.")
    
    # التحقق الآمن من وجود عمود Session
    session_col = None
    for c in df.columns:
        if 'session' in c.lower():
            session_col = c
            break
            
    if session_col and not df.empty:
        session_list = ["جميع الدورات"] + sorted(list(df[session_col].dropna().unique().astype(str)))
    else:
        session_list = ["جميع الدورات"]
        
    sess_choice = st.selectbox("اختر الدورة المراد إعداد التقرير حولها:", session_list)
    
    if session_col and sess_choice != "جميع الدورات":
        df_rep = df[df[session_col].astype(str) == sess_choice]
    else:
        df_rep = df.copy()
    
    if st.button("🚀 توليد وتحميل التقرير التنفيذي (PDF)", type="primary", use_container_width=True):
        if not df_rep.empty:
            pdf_bytes = generate_executive_pdf(df_rep, sess_choice)
            st.download_button(
                label="📥 اضغط هنا لتنزيل التقرير (Bilan_eQissmi.pdf)",
                data=pdf_bytes,
                file_name=f"Rapport_Executif_eQissmi_{sess_choice}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.warning("لا توجد بيانات متاحة لإصدار التقرير.")

# ==========================================
# 6. القائمة الجانبية (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: #1f77b4;'>مشروع إ-قسمي 2025</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    if not st.session_state['logged_in']:
        menu = st.radio("القائمة الرئيسية:", ["🏠 التقديم وطلب الانخراط", "🔐 ولوج الإدارة"])
    else:
        role_title = "رئيس مصلحة" if st.session_state['role'] == 'admin' else "مكون إقليمي"
        st.markdown(f"<div style='text-align: center;'><strong>{st.session_state['username']}</strong><br><span style='color: #7f8c8d; font-size: 0.9em;'>{role_title}</span></div>", unsafe_allow_html=True)
        st.markdown("---")
        menu = st.radio("خيارات الفضاء الإداري:", [
            "📊 لوحة القيادة التفاعلية", 
            "✏️ تحرير وإدارة المعطيات", 
            "📄 التقرير التركيبي التنفيذي",
            "🔍 فحص رقم التأجير (PPR)"
        ])
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

# ==========================================
# 7. محتوى الصفحات
# ==========================================

# --- 1. صفحة البداية للعموم مع الحقول الجديدة ---
if menu == "🏠 التقديم وطلب الانخراط":
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        try: st.image("logo_2026.png", use_container_width=True)
        except Exception: pass

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📽️ العرض التقديمي لمشروع إ-قسمي")
    with st.container():
        st.markdown("<div class='presentation-box'>", unsafe_allow_html=True)
        st.video("https://www.youtube.com/watch?v=J_jKjB7Z8oA")
        st.info("💡 المرجو الاطلاع على العرض التقديمي للتعرف على محاور التكوين قبل تسجيل الطلب.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📝 استمارة الانخراط في التكوين")
    with st.form("public_reg_form"):
        col1, col2 = st.columns(2)
        with col1:
            nom_prenom = st.text_input("الاسم والنسب الكامل:*")
            ppr = st.text_input("رقم التأجير (PPR):*")
            cycle = st.selectbox("السلك التعليمي:*", ["التعليم الابتدائي", "الثانوي الإعدادي", "الثانوي التأهيلي"])
        with col2:
            etab = st.text_input("المؤسسة التعليمية:*")
            session_name = st.selectbox("الدورة المرغوبة:", ["Session 2025/2026", "Session2 - FEV 2025"])
            tuteur_name = st.text_input("اسم المؤطر إن وجد:", value="")
            
        submitted = st.form_submit_button("تأكيد التسجيل 💾", type="primary", use_container_width=True)
        if submitted:
            if nom_prenom == "" or ppr == "" or etab == "":
                st.error("المرجو ملء الحقول الإجبارية.")
            else:
                clean_ppr = ppr.strip()
                if not df.empty and 'PPR' in df.columns and clean_ppr in df['PPR'].values:
                    st.error(f"❌ رقم التأجير {clean_ppr} مسجل مسبقاً.")
                else:
                    new_row = {
                        "Session": session_name,
                        "Tuteur": tuteur_name if tuteur_name else "غير محدد",
                        "Bénéficiaire": nom_prenom,
                        "PPR": clean_ppr,
                        "Cycle": cycle,
                        "Établissement": etab,
                        "Statut: Validé": "Non"
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    try:
                        df.to_excel(FILE_PATH, index=False)
                        st.cache_data.clear()
                        st.success(f"✅ تم تسجيل الأستاذ(ة) {nom_prenom} بنجاح!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الحفظ: {e}")

# --- 2. صفحة تسجيل الدخول ---
elif menu == "🔐 ولوج الإدارة" and not st.session_state['logged_in']:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        try: st.image("logo_2026.png", use_container_width=True)
        except Exception: pass
    st.markdown("<div class='system-title'>نظام تتبع خطط العمل</div>", unsafe_allow_html=True)
    st.markdown("<div class='system-subtitle'>الأكاديمية الجهوية للتربية والتكوين - مراكش آسفي</div>", unsafe_allow_html=True)
    
    _, form_col, _ = st.columns([1, 2, 1])
    with form_col:
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: right; font-weight: bold;'>تسجيل الدخول</h3>", unsafe_allow_html=True)
            u_in = st.text_input("اسم المستخدم:")
            p_in = st.text_input("كلمة المرور:", type="password")
            if st.form_submit_button("تسجيل الدخول", use_container_width=True):
                if u_in in users_db and users_db[u_in]["password"] == p_in:
                    st.session_state.update({'logged_in': True, 'username': users_db[u_in]["name"], 'role': users_db[u_in]["role"]})
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة.")

# --- 3. لوحة القيادة والمبيانات المتطورة ---
elif menu == "📊 لوحة القيادة التفاعلية" and st.session_state['logged_in']:
    st.markdown("### 📊 لوحة قيادة المؤشرات والتوزيع المؤسساتي")
    
    f1, f2 = st.columns(2)
    with f1:
        s_opts = ["الكل"] + sorted(list(df['Session'].dropna().unique())) if 'Session' in df.columns else ["الكل"]
        sel_s = st.selectbox("📅 فلترة الدورة:", s_opts)
    with f2:
        c_opts = ["الكل"] + sorted(list(df['Cycle'].dropna().unique())) if 'Cycle' in df.columns else ["الكل"]
        sel_c = st.selectbox("🏫 فلترة السلك:", c_opts)
        
    df_v = df.copy()
    if sel_s != "الكل": df_v = df_v[df_v['Session'] == sel_s]
    if sel_c != "الكل": df_v = df_v[df_v['Cycle'] == sel_c]
    
    tot = len(df_v)
    val = len(df_v[df_v['Statut: Validé'].str.lower() == 'oui']) if tot > 0 else 0
    non_val = tot - val
    taux = round((val / tot * 100), 1) if tot > 0 else 0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("إجمالي المستفيدين", f"{tot:,}")
    m2.metric("تمت المصادقة ✅", f"{val:,}")
    m3.metric("في الانتظار ⏳", f"{non_val:,}")
    m4.metric("نسبة الإنجاز 📈", f"{taux}%")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if tot > 0:
        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown("#### 🔄 نسب المصادقة حسب السلك التعليمي")
            if 'Cycle' in df_v.columns:
                cycle_summary = df_v.groupby(['Cycle', 'Statut: Validé']).size().reset_index(name='العدد')
                fig_cycle = px.bar(cycle_summary, x='Cycle', y='العدد', color='Statut: Validé', barmode='group',
                                   color_discrete_map={'Oui': '#2ecc71', 'Non': '#e74c3c'})
                fig_cycle.update_layout(font=dict(family="Tajawal"), xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_cycle, use_container_width=True)
        with ch2:
            st.markdown("#### 🏫 أعلى 5 مؤسسات منخرطة")
            if 'Établissement' in df_v.columns:
                top_etab = df_v['Établissement'].value_counts().head(5).reset_index()
                top_etab.columns = ['المؤسسة', 'العدد']
                fig_etab = px.bar(top_etab, x='المؤسسة', y='العدد', text_auto=True, color='العدد', color_continuous_scale='Blues')
                fig_etab.update_layout(font=dict(family="Tajawal"), xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_etab, use_container_width=True)

# --- 4. تحرير البيانات التفاعلي ---
elif menu == "✏️ تحرير وإدارة المعطيات" and st.session_state['logged_in']:
    st.markdown("### ✏️ قاعدة البيانات التفاعلية")
    if not df.empty:
        edited_data = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            height=450,
            column_config={
                "Statut: Validé": st.column_config.SelectboxColumn("المصادقة", options=["Oui", "Non"], required=True),
                "Cycle": st.column_config.SelectboxColumn("السلك", options=["التعليم الابتدائي", "الثانوي الإعدادي", "الثانوي التأهيلي"])
            }
        )
        if st.button("💾 حفظ كافة التعديلات في الملف", type="primary"):
            try:
                edited_data.to_excel(FILE_PATH, index=False)
                st.cache_data.clear()
                st.success("✅ تم تحديث الملف بنجاح.")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"خطأ في الحفظ: {e}")

# --- 5. التقرير التركيبي التنفيذي (Executive PDF) ---
elif menu == "📄 التقرير التركيبي التنفيذي" and st.session_state['logged_in']:
    st.markdown("### 📄 إعداد وتصدير التقرير التنفيذي الرسمي (PDF)")
    st.info("💡 تقرير رسمي ملخص في صفحة واحدة مخصص لتقديمه للسيد المدير الإقليمي ورؤساء المصالح.")
    
    sess_choice = st.selectbox("اختر الدورة المراد إعداد التقرير حولها:", ["جميع الدورات"] + list(df['Session'].dropna().unique()))
    df_rep = df if sess_choice == "جميع الدورات" else df[df['Session'] == sess_choice]
    
    if st.button("🚀 توليد وتحميل التقرير التنفيذي (PDF)", type="primary"):
        pdf_bytes = generate_executive_pdf(df_rep, sess_choice)
        st.download_button(
            label="📥 اضغط هنا لتنزيل التقرير (Bilan_eQissmi.pdf)",
            data=pdf_bytes,
            file_name=f"Rapport_Executif_eQissmi_{sess_choice}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# --- 6. فحص أرقام التأجير ---
elif menu == "🔍 فحص رقم التأجير (PPR)" and st.session_state['logged_in']:
    st.markdown("### 🔍 تدقيق وتفادي التكرار")
    p_search = st.text_input("أدخل رقم التأجير للتدقيق:")
    if p_search:
        clean = p_search.strip()
        valides = df[df['Statut: Validé'].str.lower() == 'oui']['PPR'].values if not df.empty else []
        if clean in valides:
            st.error(f"❌ الأستاذ صاحب الرقم {clean} سبق له أن صادق على التكوين.")
            st.dataframe(df[df['PPR'] == clean], hide_index=True)
        else:
            st.success(f"✅ الأستاذ صاحب الرقم {clean} لم يصادق عليه سابقاً.")
