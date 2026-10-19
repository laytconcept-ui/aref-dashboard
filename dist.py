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

# 4. دالة قراءة البيانات الذكية (مكيفة مع هيكلة الملف الجديدة)
FILE_PATH = "eQissmi_donnees_Haouz(1).xlsx"

@st.cache_data(ttl=60)
def load_data():
    if os.path.exists(FILE_PATH):
        try:
            for i in range(5):
                df_temp = pd.read_excel(FILE_PATH, header=i)
                df_temp.columns = df_temp.columns.astype(str).str.strip()
                # البحث عن الأعمدة الجديدة
                if 'Validé par mérite (X)' in df_temp.columns or 'Nom & Prénom' in df_temp.columns:
                    return df_temp
            
            df_fallback = pd.read_excel(FILE_PATH)
            df_fallback.columns = df_fallback.columns.astype(str).str.strip()
            return df_fallback
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

# 7. الحسابات والمؤشرات (مكيفة مع الهيكلة الجديدة)
total = len(df)
valide_merite = valide_compensation = en_attente = taux = 0

if total > 0:
    # حساب المصادقة بالاستحقاق (X)
    if 'Validé par mérite (X)' in df.columns:
        valide_merite = len(df[df['Validé par mérite (X)'].astype(str).str.upper() == 'X'])
    
    # حساب المصادقة بالتعويض (X)
    if 'Validé par compensasion (X)' in df.columns:
        valide_compensation = len(df[df['Validé par compensasion (X)'].astype(str).str.upper() == 'X'])
    
    # من لم يصادق عليه لا في الاستحقاق ولا في التعويض
    en_attente = total - (valide_merite + valide_compensation)
    
    # نسبة الإنجاز الإجمالية
    if total > 0:
        taux = round(((valide_merite + valide_compensation) / total) * 100, 1)

# 8. محتوى الصفحات
if menu == "📊 لوحة القيادة التفاعلية":
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
                st.warning("الأعمدة المطلوبة غير متوفرة في ملف الإكسيل.")

        with chart_col2:
            st.markdown("#### 📊 توزيع المستفيدين حسب المديرية")
            if 'DP (Nom Officiel)' in df.columns:
                dp_counts = df['DP (Nom Officiel)'].value_counts().reset_index()
                dp_counts.columns = ['المديرية الإقليمية', 'عدد المستفيدين']
                fig_bar = px.bar(
                    dp_counts, 
                    x='المديرية الإقليمية', 
                    y='عدد المستفيدين',
                    text_auto=True,
                    color='عدد المستفيدين',
                    color_continuous_scale='Blues'
                )
                fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20), font=dict(family="Tajawal"), xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("عمود 'DP (Nom Officiel)' غير متوفر في ملف الإكسيل.")
    else:
        st.info("لا توجد بيانات لعرض المبيانات. المرجو استيراد قاعدة البيانات.")

elif menu == "📋 اللوائح الإسمية":
    st.markdown("### قاعدة بيانات المستفيدين")
    if total > 0:
        col1, col2 = st.columns([1, 3])
        status_filter = col1.selectbox("تصفية حسب حالة المصادقة:", ["الكل", "مصادق بالاستحقاق", "مصادق بالتعويض", "في الانتظار"])
        
        if status_filter == "مصادق بالاستحقاق" and 'Validé par mérite (X)' in df.columns:
            filtered_df = df[df['Validé par mérite (X)'].astype(str).str.upper() == 'X']
        elif status_filter == "مصادق بالتعويض" and 'Validé par compensasion (X)' in df.columns:
            filtered_df = df[df['Validé par compensasion (X)'].astype(str).str.upper() == 'X']
        elif status_filter == "في الانتظار":
            # تصفية من ليس لديهم X لا هنا ولا هنا
            if 'Validé par mérite (X)' in df.columns and 'Validé par compensasion (X)' in df.columns:
                cond_merite = df['Validé par mérite (X)'].astype(str).str.upper() != 'X'
                cond_comp = df['Validé par compensasion (X)'].astype(str).str.upper() != 'X'
                filtered_df = df[cond_merite & cond_comp]
            else:
                filtered_df = df
        else:
            filtered_df = df
            
        st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=500)
    else:
        st.warning("قاعدة البيانات فارغة حالياً.")

elif menu == "📤 تحديث قاعدة البيانات":
    st.markdown("### استيراد وتحيين المعطيات")
    st.info("💡 المرجو رفع الملف الذي يحتوي على الأعمدة: N°, Nom & Prénom, PPR, AREF, DP, Validé par mérite, Validé par compensasion.")
    
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
