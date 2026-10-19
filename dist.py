import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time

# 1. إعدادات الصفحة المتقدمة
st.set_page_config(page_title="المنصة الإقليمية لتتبع التكوينات", page_icon="🇲🇦", layout="wide")

# 2. تصميم CSS احترافي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
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
    </style>
""", unsafe_allow_html=True)

# 3. نظام تسجيل الدخول
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'username': '', 'role': ''})

users_db = {
    "jalal": {"password": "admin", "role": "admin", "name": "جلال الكميلي"},
    "tuteur1": {"password": "123", "role": "tuteur", "name": "مكون 1"}
}

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center; color: #1f77b4;'>المنصة الإقليمية لتتبع التكوينات</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>المرجو إدخال بيانات الاعتماد للولوج</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username_input = st.text_input("اسم المستخدم")
            password_input = st.text_input("كلمة المرور", type="password")
            submit_button = st.form_submit_button("تسجيل الدخول", use_container_width=True)
            
            if submit_button:
                if username_input in users_db and users_db[username_input]["password"] == password_input:
                    st.session_state.update({'logged_in': True, 'username': users_db[username_input]["name"], 'role': users_db[username_input]["role"]})
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة.")
    st.stop()

# 4. دالة قراءة البيانات الذكية (المحدثة لتفادي مشكل الأصفار)
FILE_PATH = "eQissmi_donnees_Haouz(1).xlsx"

@st.cache_data(ttl=60)
def load_data():
    if os.path.exists(FILE_PATH):
        try:
            # المحاولة الأولى: قراءة السطر الأول كعناوين
            df = pd.read_excel(FILE_PATH)
            
            # إذا لم يجد عمود 'Statut: Validé'، سيجرب السطر الثاني
            if 'Statut: Validé' not in df.columns:
                df_alt = pd.read_excel(FILE_PATH, header=1)
                if 'Statut: Validé' in df_alt.columns:
                    return df_alt
            return df
        except Exception as e:
            return pd.DataFrame()
    return pd.DataFrame()

df = load_data()

# 5. الترويسة الرسمية
st.markdown("""
<div class="official-header">
    <h4 style="margin: 0; font-weight: 700;">المملكة المغربية | وزارة التربية الوطنية والتعليم الأولي والرياضة</h4>
    <h5 style="margin: 5px 0 0 0; color: #7f8c8d;">الأكاديمية الجهوية للتربية والتكوين لجهة مراكش آسفي | المديرية الإقليمية بالحوز</h5>
</div>
""", unsafe_allow_html=True)

# 6. القائمة الجانبية
with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: #1f77b4;'>إ-قسمي 2025</h3>", unsafe_allow_html=True)
    st.markdown("---")
    role_title = "رئيس مصلحة" if st.session_state['role'] == 'admin' else "مكون إقليمي"
    st.markdown(f"<div style='text-align: center;'><strong>{st.session_state['username']}</strong><br><span style='color: #7f8c8d; font-size: 0.9em;'>{role_title}</span></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = st.radio("خيارات التصفح", ["📊 لوحة القيادة التفاعلية", "📋 اللوائح الإسمية", "📤 تحديث قاعدة البيانات"])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()

# 7. الحسابات والمؤشرات (مع حماية ضد غياب الأعمدة)
total = len(df)
valide = non_valide = taux = tuteurs_count = 0

if total > 0:
    if 'Statut: Validé' in df.columns:
        # نقوم بتنظيف النصوص من أي مسافات زائدة لضمان دقة الحساب
        df['Statut: Validé'] = df['Statut: Validé'].astype(str).str.strip()
        valide = len(df[df['Statut: Validé'].str.lower() == 'oui'])
        non_valide = len(df[df['Statut: Validé'].str.lower() == 'non'])
        if total > 0:
            taux = round((valide / total) * 100, 1)
    
    if 'Tuteur' in df.columns:
        tuteurs_count = df['Tuteur'].nunique()

# 8. محتوى الصفحات
if menu == "📊 لوحة القيادة التفاعلية":
    cols = st.columns(5)
    cols[0].metric("إجمالي المستفيدين", f"{total:,}")
    cols[1].metric("تمت المصادقة ✅", f"{valide:,}")
    cols[2].metric("في الانتظار ⏳", f"{non_valide:,}")
    cols[3].metric("نسبة الإنجاز 📈", f"{taux}%")
    cols[4].metric("المؤطرون المعتمدون 👨‍🏫", tuteurs_count)

    st.markdown("<br>", unsafe_allow_html=True)

    if total > 0:
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("#### 🔄 وضعية المصادقة على التكوين")
            if 'Statut: Validé' in df.columns and (valide > 0 or non_valide > 0):
                fig_pie = px.pie(
                    values=[valide, non_valide], 
                    names=["تمت المصادقة", "في الانتظار"],
                    color=["تمت المصادقة", "في الانتظار"],
                    color_discrete_map={"تمت المصادقة": "#2ecc71", "في الانتظار": "#e74c3c"},
                    hole=0.4
                )
                fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), font=dict(family="Tajawal"))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.warning("عمود 'Statut: Validé' غير متوفر أو فارغ في ملف الإكسيل.")

        with chart_col2:
            st.markdown("#### 📊 الحصيلة حسب المكون الإقليمي")
            if 'Tuteur' in df.columns:
                tuteur_counts = df['Tuteur'].value_counts().reset_index()
                tuteur_counts.columns = ['المؤطر', 'عدد المستفيدين']
                fig_bar = px.bar(
                    tuteur_counts, 
                    x='المؤطر', 
                    y='عدد المستفيدين',
                    text_auto=True,
                    color='عدد المستفيدين',
                    color_continuous_scale='Blues'
                )
                fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20), font=dict(family="Tajawal"), xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("عمود 'Tuteur' غير متوفر في ملف الإكسيل.")
    else:
        st.info("لا توجد بيانات لعرض المبيانات. المرجو استيراد قاعدة البيانات.")

elif menu == "📋 اللوائح الإسمية":
    st.markdown("### قاعدة بيانات المستفيدين")
    if total > 0:
        if 'Statut: Validé' in df.columns:
            col1, col2 = st.columns([1, 3])
            status_filter = col1.selectbox("تصفية حسب الحالة:", ["الكل", "تمت المصادقة", "في الانتظار"])
            
            if status_filter == "تمت المصادقة":
                filtered_df = df[df['Statut: Validé'].str.lower() == 'oui']
            elif status_filter == "في الانتظار":
                filtered_df = df[df['Statut: Validé'].str.lower() == 'non']
            else:
                filtered_df = df
            st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=500)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True, height=500)
    else:
        st.warning("قاعدة البيانات فارغة حالياً.")

elif menu == "📤 تحديث قاعدة البيانات":
    st.markdown("### استيراد وتحيين المعطيات")
    st.info("💡 هذه الواجهة مخصصة لرفع النسخ المحينة من لوائح مشروع إ-قسمي (بصيغة Excel).")
    
    uploaded_file = st.file_uploader("قم بسحب وإفلات الملف هنا", type=["xlsx", "xls"])
    
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
