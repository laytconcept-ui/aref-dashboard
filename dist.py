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
# ==========================================
# 2. تصميم CSS احترافي (محدث لإخفاء الأزرار)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    /* إخفاء قوائم وأزرار Streamlit الافتراضية بالكامل */
    #MainMenu {visibility: hidden; display: none;}
    footer {visibility: hidden; display: none;}
    header {visibility: hidden; display: none;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    
    /* تصميم البطاقات */
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
    
    .official-header {
        text-align: center;
        color: #2c3e50;
        border-bottom: 2px solid #e0e6ed;
        padding-bottom: 15px;
        margin-bottom: 30px;
    }
    
    .presentation-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
        border: 1px solid #e9ecef;
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
        except Exception as e:
            return pd.DataFrame()
    return pd.DataFrame()

df = load_data()

# ==========================================
# 5. الترويسة الرسمية (تظهر للجميع)
# ==========================================
# ==========================================
# 5. الترويسة الرسمية (تظهر للجميع)
# ==========================================
# التحقق من وجود الشعار وعرضه
LOGO_PATH = "logo_2026.jpg"
if os.path.exists(LOGO_PATH):
    # استخدام أعمدة لتوسيط الشعار بشكل جميل
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_PATH, use_container_width=True)
else:
    # في حالة عدم وجود الصورة، سيتم عرض النص كبديل
    st.markdown("""
    <div class="official-header">
        <h4 style="margin: 0; font-weight: 700;">المملكة المغربية | وزارة التربية الوطنية والتعليم الأولي والرياضة</h4>
        <h5 style="margin: 5px 0 0 0; color: #7f8c8d;">الأكاديمية الجهوية للتربية والتكوين لجهة مراكش آسفي | المديرية الإقليمية بالحوز</h5>
    </div>
    """, unsafe_allow_html=True)
    st.warning("الشعار 'logo_2026.jpg' غير موجود في مجلد المشروع.")

st.markdown("---") # خط فاصل تحت الشعار

# ==========================================
# 6. هندسة القائمة الجانبية (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: #1f77b4;'>مشروع إ-قسمي 2025</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    if not st.session_state['logged_in']:
        # قائمة العموم (للأساتذة)
        menu = st.radio("القائمة الرئيسية:", ["🏠 التقديم وطلب الانخراط", "🔐 ولوج الإدارة"])
    else:
        # قائمة الإدارة
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
# 7. الحسابات والمؤشرات الإجمالية للإدارة
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
# 8. محتوى الصفحات (حسب اختيار القائمة)
# ==========================================

# ------------------------------------------
# صفحة الأساتذة (العرض + التسجيل)
# ------------------------------------------
if menu == "🏠 التقديم وطلب الانخراط":
    st.markdown("### 📽️ العرض التقديمي لمشروع إ-قسمي")
    st.markdown("<div class='presentation-box'>", unsafe_allow_html=True)
    
    # يمكنك استبدال الرابط أدناه برابط فيديو حقيقي أو تركه هكذا
    st.video("https://www.youtube.com/watch?v=ejZeosbChAE") 
    st.info("💡 المرجو الاطلاع على العرض التقديمي أعلاه لفهم أهداف المشروع قبل الشروع في التسجيل.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📝 استمارة الانخراط في التكوين")
    
    with st.form("registration_form"):
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
# صفحة ولوج الإدارة
# ------------------------------------------
elif menu == "🔐 ولوج الإدارة":
    st.markdown("<h3 style='text-align: center; color: #1f77b4;'>ولوج الفضاء الإداري والتتبع</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("admin_login_form"):
            username_input = st.text_input("اسم المستخدم")
            password_input = st.text_input("كلمة المرور", type="password")
            submit_button = st.form_submit_button("تسجيل الدخول", use_container_width=True)
            
            if submit_button:
                if username_input in users_db and users_db[username_input]["password"] == password_input:
                    st.session_state.update({'logged_in': True, 'username': users_db[username_input]["name"], 'role': users_db[username_input]["role"]})
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة.")

# ------------------------------------------
# صفحة لوحة القيادة (للإدارة فقط)
# ------------------------------------------
elif menu == "📊 لوحة القيادة التفاعلية" and st.session_state['logged_in']:
    cols = st.columns(5)
    cols[0].metric("إجمالي المستفيدين", f"{total:,}")
    cols[1].metric("مصادقة بالاستحقاق ✅", f"{valide_merite:,}")
    cols[2].metric("مصادقة بالتعويض 🔄", f"{valide_compensation:,}")
    cols[3].metric("في الانتظار ⏳", f"{en_attente:,}")
    cols[4].metric("نسبة الإنجاز 📈", f"{taux}%")

    st.markdown("<br>", unsafe_allow_html=True)

    if total > 0:
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("#### 🔄 وضعية المصادقة على التكوين")
            if 'Validé par mérite (X)' in df.columns or 'Validé par compensasion (X)' in df.columns:
                fig_pie = px.pie(
                    values=[valide_merite, valide_compensation, en_attente], 
                    names=["بالاستحقاق", "بالتعويض", "في الانتظار"],
                    color=["بالاستحقاق", "بالتعويض", "في الانتظار"],
                    color_discrete_map={"بالاستحقاق": "#2ecc71", "بالتعويض": "#f39c12", "في الانتظار": "#e74c3c"},
                    hole=0.4
                )
                fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), font=dict(family="Tajawal"))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.warning("الأعمدة المطلوبة غير متوفرة لرسم المبيان.")

        with chart_col2:
            st.markdown("#### 📊 توزيع المستفيدين حسب المديرية")
            if 'DP (Nom Officiel)' in df.columns:
                dp_counts = df['DP (Nom Officiel)'].value_counts().reset_index()
                dp_counts.columns = ['المديرية الإقليمية', 'عدد المستفيدين']
                fig_bar = px.bar(
                    dp_counts, x='المديرية الإقليمية', y='عدد المستفيدين', text_auto=True,
                    color='عدد المستفيدين', color_continuous_scale='Blues'
                )
                fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20), font=dict(family="Tajawal"), xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("عمود 'DP (Nom Officiel)' غير متوفر.")
    else:
        st.info("لا توجد بيانات لعرض المبيانات. المرجو استيراد قاعدة البيانات.")

# ------------------------------------------
# صفحة اللوائح الإسمية (للإدارة فقط)
# ------------------------------------------
elif menu == "📋 اللوائح الإسمية" and st.session_state['logged_in']:
    st.markdown("### قاعدة بيانات المستفيدين")
    if total > 0:
        col1, col2 = st.columns([1, 3])
        status_filter = col1.selectbox("تصفية حسب حالة المصادقة:", ["الكل", "مصادق بالاستحقاق", "مصادق بالتعويض", "في الانتظار"])
        
        if status_filter == "مصادق بالاستحقاق" and 'Validé par mérite (X)' in df.columns:
            filtered_df = df[df['Validé par mérite (X)'].astype(str).str.upper() == 'X']
        elif status_filter == "مصادق بالتعويض" and 'Validé par compensasion (X)' in df.columns:
            filtered_df = df[df['Validé par compensasion (X)'].astype(str).str.upper() == 'X']
        elif status_filter == "في الانتظار":
            if 'Validé par mérite (X)' in df.columns and 'Validé par compensasion (X)' in df.columns:
                cond_merite = df['Validé par mérite (X)'].astype(str).str.upper() != 'X'
                cond_comp = df['Validé par compensasion (X)'].astype(str).str.upper() != 'X'
                filtered_df = df[cond_merite & cond_comp]
            else:
                filtered_df = df
        else:
            filtered_df = df
            
        st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=400)
        
        # زر الطباعة / التحميل
        st.markdown("<br>", unsafe_allow_html=True)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False)
        st.download_button(
            label="🖨️ تحميل اللائحة للطباعة (Excel)",
            data=buffer.getvalue(),
            file_name=f"Liste_{status_filter}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
    else:
        st.warning("قاعدة البيانات فارغة حالياً.")

# ------------------------------------------
# صفحة التحقق من الاستفادة (للإدارة فقط)
# ------------------------------------------
elif menu == "🔍 التحقق من الاستفادة (PPR)" and st.session_state['logged_in']:
    st.markdown("### 🔍 فحص الاستفادة السابقة عبر رقم التأجير")
    st.info("تمكنك هذه الواجهة من التأكد مما إذا كان الأساتذة قد استفادوا في دورات سابقة لتفادي التكرار.")
    
    if total > 0 and 'PPR' in df.columns:
        cond_m = df['Validé par mérite (X)'].astype(str).str.upper() == 'X' if 'Validé par mérite (X)' in df.columns else False
        cond_c = df['Validé par compensasion (X)'].astype(str).str.upper() == 'X' if 'Validé par compensasion (X)' in df.columns else False
        df_benefited = df[cond_m | cond_c]
        benefited_pprs = df_benefited['PPR'].astype(str).str.strip().unique()
        
        st.markdown("#### 1️⃣ فحص فردي (أستاذ واحد)")
        search_ppr = st.text_input("📝 أدخل رقم التأجير (PPR) للبحث:")
        if search_ppr:
            clean_search = search_ppr.strip()
            if clean_search in benefited_pprs:
                st.error(f"❌ الأستاذ(ة) صاحب رقم التأجير **{clean_search}** سبق له أن استفاد.")
                st.dataframe(df_benefited[df_benefited['PPR'].astype(str).str.strip() == clean_search], hide_index=True)
            else:
                st.success(f"✅ الأستاذ(ة) صاحب رقم التأجير **{clean_search}** لم يستفد سابقاً (يمكن إضافته).")
        
        st.markdown("---")
        st.markdown("#### 2️⃣ فحص لائحة كاملة دفعة واحدة")
        verify_file = st.file_uploader("ارفع اللائحة الجديدة لفحصها (Excel):", type=["xlsx", "xls"], key="verify_upload")
        
        if verify_file:
            df_new = pd.read_excel(verify_file)
            if 'PPR' in df_new.columns:
                df_new['PPR_str'] = df_new['PPR'].astype(str).str.strip()
                df_new['ملاحظة الفحص'] = df_new['PPR_str'].apply(lambda x: 'استفاد سابقاً ❌' if x in benefited_pprs else 'مقبول (جديد) ✅')
                df_new = df_new.drop(columns=['PPR_str'])
                
                st.write("نتيجة الفحص الآلي:")
                st.dataframe(df_new, use_container_width=True, hide_index=True)
                
                buf_verify = io.BytesIO()
                with pd.ExcelWriter(buf_verify, engine='openpyxl') as w2:
                    df_new.to_excel(w2, index=False)
                st.download_button("📥 تحميل نتيجة الفحص", data=buf_verify.getvalue(), file_name="Resultat_Verification.xlsx", use_container_width=True)
            else:
                st.warning("الملف المرفوع لا يحتوي على عمود 'PPR'. يرجى التأكد من هيكلة الملف.")
    else:
        st.warning("قاعدة البيانات الحالية فارغة أو لا تحتوي على عمود 'PPR'.")

# ------------------------------------------
# صفحة تحديث قاعدة البيانات (للإدارة فقط)
# ------------------------------------------
elif menu == "📤 تحديث قاعدة البيانات" and st.session_state['logged_in']:
    st.markdown("### استيراد وتحيين المعطيات")
    st.info("💡 المرجو رفع الملف الذي يحتوي على الأعمدة: N°, Nom & Prénom, PPR, AREF, DP, Validé par mérite, Validé par compensasion.")
    
    uploaded_file = st.file_uploader("قم بسحب وإفلات الملف هنا", type=["xlsx", "xls"], key="main_upload")
    
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
