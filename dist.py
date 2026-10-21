import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
import io

# ==========================================
# 1. إعدادات الصفحة المتقدمة
# ==========================================
st.set_page_config(page_title="بوابة إ-قسمي | مديرية الحوز", page_icon="🎓", layout="wide")

# ==========================================
# 2. تصميم CSS احترافي ومحاذاة كاملة
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
    
    #MainMenu {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    .viewerBadge_container {display: none !important;}
    .viewerBadge_link {display: none !important;}
    
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
# 4. دالة قراءة البيانات من النموذج المعتمد
# ==========================================
# اسم الملف المعتمد
FILE_PATH = "eQissmi_donnees_Haouz(1).xlsx"

@st.cache_data(ttl=30)
def load_data():
    if os.path.exists(FILE_PATH):
        try:
            # تجربة قراءة الترويسة من السطر الأول أو الثاني
            for h in [1, 0, 2]:
                try:
                    df_temp = pd.read_excel(FILE_PATH, header=h)
                    df_temp.columns = df_temp.columns.astype(str).str.strip()
                    if 'Bénéficiaire' in df_temp.columns or 'Statut: Validé' in df_temp.columns or 'Tuteur' in df_temp.columns:
                        return df_temp
                except Exception:
                    continue
            df_fallback = pd.read_excel(FILE_PATH)
            df_fallback.columns = df_fallback.columns.astype(str).str.strip()
            return df_fallback
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

df = load_data()

# توحيد أسماء وتنسيقات الأعمدة لتفادي الأخطاء
if not df.empty:
    if 'Statut: Validé' in df.columns:
        df['Statut: Validé'] = df['Statut: Validé'].astype(str).str.strip()
    if 'PPR' in df.columns:
        df['PPR'] = df['PPR'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

# ==========================================
# 5. القائمة الجانبية (Sidebar)
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
            "✏️ إدارة وتعديل اللائحة", 
            "🔍 التحقق من الاستفادة (PPR)",
            "📤 استيراد ملف جديد"
        ])
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

# ==========================================
# 6. محتوى الصفحات
# ==========================================

# ------------------------------------------
# 1. صفحة البداية للعموم (التقديم + الفيديو + الاستمارة)
# ------------------------------------------
if menu == "🏠 التقديم وطلب الانخراط":
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
        st.video("https://www.youtube.com/watch?v=J_jKjB7Z8oA")
        st.info("💡 المرجو الاطلاع على العرض التقديمي أعلاه للتعرف على محاور وأهداف المشروع قبل تسجيل الطلب.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📝 استمارة الانخراط في التكوين")
    
    with st.form("public_registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            nom_prenom = st.text_input("الاسم والنسب الكامل (Bénéficiaire):*")
            ppr = st.text_input("رقم التأجير (PPR):*")
        with col2:
            session_name = st.selectbox("الدورة المرغوبة (Session):", ["Session 2025/2026", "Session2 - FEV 2025"])
            tuteur_name = st.text_input("اسم المؤطر (Tuteur) إن وجد:", value="")
            
        submitted = st.form_submit_button("تأكيد التسجيل 💾", type="primary", use_container_width=True)
        
        if submitted:
            if nom_prenom == "" or ppr == "":
                st.error("المرجو ملء الحقول الإجبارية (الاسم ورقم التأجير).")
            else:
                ppr_clean = ppr.strip()
                if not df.empty and 'PPR' in df.columns and ppr_clean in df['PPR'].values:
                    st.error(f"❌ الأستاذ(ة) برقم التأجير {ppr_clean} مسجل مسبقاً في قاعدة البيانات.")
                else:
                    new_row = {
                        "Session": session_name,
                        "Tuteur": tuteur_name if tuteur_name else "غير محدد",
                        "Bénéficiaire": nom_prenom,
                        "PPR": ppr_clean,
                        "Statut: Validé": "Non" # التسجيل الأولي يكون غير مصادق عليه بعد
                    }
                    df_new_row = pd.DataFrame([new_row])
                    df_updated = df_new_row if df.empty else pd.concat([df, df_new_row], ignore_index=True)
                    
                    try:
                        df_updated.to_excel(FILE_PATH, index=False)
                        st.cache_data.clear()
                        st.success(f"✅ تم تسجيل الأستاذ(ة) {nom_prenom} بنجاح!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الحفظ: {e}")

# ------------------------------------------
# 2. صفحة تسجيل الدخول للإدارة فقط
# ------------------------------------------
elif menu == "🔐 ولوج الإدارة" and not st.session_state['logged_in']:
    st.markdown("<br>", unsafe_allow_html=True)
    
    logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])
    with logo_col2:
        try:
            st.image("logo_2026.png", use_container_width=True)
        except Exception:
            pass
            
    st.markdown("<div class='system-title'>نظام تتبع خطط العمل</div>", unsafe_allow_html=True)
    st.markdown("<div class='system-subtitle'>الأكاديمية الجهوية للتربية والتكوين - مراكش آسفي</div>", unsafe_allow_html=True)

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
                    st.error("بيانات الدخول غير صحيحة. المرجو المحاولة مجدداً.")
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# 3. لوحة القيادة التفاعلية (مع فلترة السنوات)
# ------------------------------------------
elif menu == "📊 لوحة القيادة التفاعلية" and st.session_state['logged_in']:
    top_col1, top_col2, top_col3 = st.columns([1, 2, 1])
    with top_col2:
        try:
            st.image("logo_2026.png", use_container_width=True)
        except Exception:
            pass

    st.markdown("### 📊 لوحة قيادة تتبع المصادقة على التكوينات")
    
    # فلترة حسب الدورة / السنة التكوينية
    df_filtered = df.copy()
    if not df.empty and 'Session' in df.columns:
        sessions_list = ["جميع الدورات والسنوات"] + sorted(list(df['Session'].dropna().unique()))
        selected_session = st.selectbox("📅 فلترة حسب الدورة / السنة التكوينية:", sessions_list)
        if selected_session != "جميع الدورات والسنوات":
            df_filtered = df[df['Session'] == selected_session]
    
    total = len(df_filtered)
    valide = non_valide = taux = tuteurs_count = 0

    if total > 0 and 'Statut: Validé' in df_filtered.columns:
        valide = len(df_filtered[df_filtered['Statut: Validé'].str.lower() == 'oui'])
        non_valide = len(df_filtered[df_filtered['Statut: Validé'].str.lower() == 'non'])
        taux = round((valide / total) * 100, 1)
        if 'Tuteur' in df_filtered.columns:
            tuteurs_count = df_filtered['Tuteur'].nunique()

    cols = st.columns(5)
    cols[0].metric("إجمالي المستفيدين", f"{total:,}")
    cols[1].metric("تمت المصادقة ✅", f"{valide:,}")
    cols[2].metric("لم تتم المصادقة ⏳", f"{non_valide:,}")
    cols[3].metric("نسبة الإنجاز 📈", f"{taux}%")
    cols[4].metric("عدد المؤطرين 👨‍🏫", tuteurs_count)

    st.markdown("<br>", unsafe_allow_html=True)

    if total > 0:
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("#### 🔄 وضعية المصادقة على التكوين")
            if 'Statut: Validé' in df_filtered.columns and (valide > 0 or non_valide > 0):
                fig_pie = px.pie(
                    values=[valide, non_valide], 
                    names=["تمت المصادقة (Oui)", "لم يصادق (Non)"],
                    color=["تمت المصادقة (Oui)", "لم يصادق (Non)"],
                    color_discrete_map={"تمت المصادقة (Oui)": "#2ecc71", "لم يصادق (Non)": "#e74c3c"},
                    hole=0.4
                )
                fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), font=dict(family="Tajawal"))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("لا توجد مؤشرات كافية للرسم في هذه الدورة.")

        with chart_col2:
            st.markdown("#### 👨‍🏫 توزيع المستفيدين ونسب المصادقة حسب المؤطر")
            if 'Tuteur' in df_filtered.columns:
                tuteur_group = df_filtered.groupby('Tuteur').agg(
                    إجمالي=('Statut: Validé', 'count'),
                    مصادق_عليه=('Statut: Validé', lambda x: (x.str.lower() == 'oui').sum())
                ).reset_index()
                
                fig_bar = px.bar(
                    tuteur_group, 
                    x='Tuteur', 
                    y=['مصادق_عليه', 'إجمالي'],
                    barmode='group',
                    text_auto=True,
                    color_discrete_map={'مصادق_عليه': '#2ecc71', 'إجمالي': '#3498db'}
                )
                fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20), font=dict(family="Tajawal"), xaxis_title="المؤطر", yaxis_title="العدد")
                st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("لا توجد بيانات مسجلة في هذا التحديد.")

# ------------------------------------------
# 4. صفحة إدارة وتعديل اللائحة (تعديل + حذف + إضافة أسطر)
# ------------------------------------------
elif menu == "✏️ إدارة وتعديل اللائحة" and st.session_state['logged_in']:
    st.markdown("### ✏️ تحرير اللائحة المباشر (التعديل، الحذف، والإضافة)")
    st.info("💡 يمكنك النقر مرتين على أي خلية لتعديلها مباشرة، تحديد أي سطر لحذفه عبر مفتاح Delete، أو إضافة أسطر جديدة أسفل الجدول، ثم الضغط على زر 'حفظ كافة التعديلات'.")

    if not df.empty:
        # شريط الفلترة
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            session_opts = ["الكل"] + sorted(list(df['Session'].dropna().unique())) if 'Session' in df.columns else ["الكل"]
            sel_sess = st.selectbox("تصفية حسب الدورة/السنة:", session_opts, key="edit_sess")
        with f_col2:
            status_opts = ["الكل", "Oui", "Non"]
            sel_stat = st.selectbox("تصفية حسب المصادقة:", status_opts, key="edit_stat")
        
        view_df = df.copy()
        if sel_sess != "الكل":
            view_df = view_df[view_df['Session'] == sel_sess]
        if sel_stat != "الكل":
            view_df = view_df[view_df['Statut: Validé'].str.lower() == sel_stat.lower()]

        # محرر البيانات التفاعلي المتقدم
        edited_df = st.data_editor(
            view_df,
            num_rows="dynamic", # يتيح إضافة وحذف الأسطر
            use_container_width=True,
            height=450,
            column_config={
                "Statut: Validé": st.column_config.SelectboxColumn(
                    "المصادقة (Statut: Validé)",
                    options=["Oui", "Non"],
                    required=True
                )
            }
        )
        
        btn_c1, btn_c2 = st.columns([1, 1])
        with btn_c1:
            if st.button("💾 حفظ كافة التعديلات في الملف", type="primary", use_container_width=True):
                try:
                    # في حالة الفلترة: تحديث الأسطر المعدلة في الجدول الرئيسي
                    if sel_sess != "الكل" or sel_stat != "الكل":
                        # استبدال الصفوف بناءً على PPR أو تحديث كامل الجدول
                        df.update(edited_df)
                    else:
                        df = edited_df

                    df.to_excel(FILE_PATH, index=False)
                    st.cache_data.clear()
                    st.success("✅ تم حفظ كافة التعديلات بنجاح في قاعدة البيانات!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الحفظ: {e}")

        with btn_c2:
            # زر الطباعة والتحميل
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                edited_df.to_excel(writer, index=False)
            st.download_button(
                label="🖨️ تحميل اللائحة الحالية للطباعة (Excel)",
                data=buffer.getvalue(),
                file_name=f"Liste_eQissmi_{sel_sess}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.warning("قاعدة البيانات فارغة حالياً.")

# ------------------------------------------
# 5. صفحة التحقق من الاستفادة (PPR)
# ------------------------------------------
elif menu == "🔍 التحقق من الاستفادة (PPR)" and st.session_state['logged_in']:
    st.markdown("### 🔍 فحص الاستفادة السابقة عبر رقم التأجير (PPR)")
    st.info("فحص الأساتذة الذين تمت المصادقة عليهم سابقاً (Statut = Oui) لتفادي تكرار تسجيلهم.")
    
    if not df.empty and 'PPR' in df.columns:
        # لائحة الذين صادقوا فعلاً
        df_valide = df[df['Statut: Validé'].str.lower() == 'oui']
        benefited_pprs = df_valide['PPR'].unique()
        
        st.markdown("#### 1️⃣ فحص فردي (أستاذ واحد)")
        search_ppr = st.text_input("📝 أدخل رقم التأجير (PPR) للبحث:")
        if search_ppr:
            clean_search = search_ppr.strip()
            if clean_search in benefited_pprs:
                st.error(f"❌ الأستاذ(ة) صاحب رقم التأجير **{clean_search}** صادق(ت) على التكوين مسبقاً (استفاد).")
                st.dataframe(df_valide[df_valide['PPR'] == clean_search], hide_index=True)
            else:
                st.success(f"✅ رقم التأجير **{clean_search}** لم يصادق عليه سابقاً (يمكنه الاستفادة).")
        
        st.markdown("---")
        st.markdown("#### 2️⃣ فحص لائحة كاملة دفعة واحدة")
        verify_file = st.file_uploader("ارفع لائحة Excel جديدة لفحصها:", type=["xlsx", "xls"], key="verify_upload")
        
        if verify_file:
            df_new = pd.read_excel(verify_file)
            if 'PPR' in df_new.columns:
                df_new['PPR_str'] = df_new['PPR'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
                df_new['ملاحظة الفحص'] = df_new['PPR_str'].apply(lambda x: 'استفاد سابقاً (صادق على التكوين) ❌' if x in benefited_pprs else 'مقبول (جديد) ✅')
                df_new = df_new.drop(columns=['PPR_str'])
                
                st.write("نتيجة الفحص الآلي:")
                st.dataframe(df_new, use_container_width=True, hide_index=True)
                
                buf_verify = io.BytesIO()
                with pd.ExcelWriter(buf_verify, engine='openpyxl') as w2:
                    df_new.to_excel(w2, index=False)
                st.download_button("📥 تحميل نتيجة الفحص", data=buf_verify.getvalue(), file_name="Resultat_Verification.xlsx", use_container_width=True)
            else:
                st.warning("الملف المرفوع لا يحتوي على عمود 'PPR'.")
    else:
        st.warning("قاعدة البيانات الحالية فارغة أو لا تحتوي على عمود 'PPR'.")

# ------------------------------------------
# 6. صفحة استيراد ملف جديد (للإدارة فقط)
# ------------------------------------------
elif menu == "📤 استيراد ملف جديد" and st.session_state['logged_in']:
    st.markdown("### استيراد وتحيين اللائحة الرسمية")
    st.info("💡 المرجو رفع الملف المعتمد الذي يتضمن الأعمدة: Session, Tuteur, Bénéficiaire, PPR, Statut: Validé.")
    
    uploaded_file = st.file_uploader("قم بسحب وإفلات ملف Excel هنا", type=["xlsx", "xls"], key="main_upload")
    
    if uploaded_file is not None:
        with st.spinner('جاري قراءة ومعالجة البيانات...'):
            time.sleep(1)
            preview_df = pd.read_excel(uploaded_file)
        
        st.success("تمت قراءة الملف بنجاح. معاينة أولية:")
        st.dataframe(preview_df.head(), use_container_width=True)
        
        if st.button("تأكيد واعتماد البيانات 💾", type="primary", use_container_width=True):
            try:
                preview_df.to_excel(FILE_PATH, index=False)
                st.cache_data.clear()
                st.success("✅ تم تحديث قاعدة البيانات بنجاح! التغييرات مفعلة الآن في لوحة القيادة.")
            except Exception as e:
                st.error(f"حدث خطأ غير متوقع: {e}")
