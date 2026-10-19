import streamlit as st
import pandas as pd
import os

# 1. إعدادات الصفحة (مهمة لدعم العربية وتوجيه الصفحة)
st.set_page_config(page_title="نظام تتبع خطط العمل - AREF MS", page_icon="📊", layout="wide")

# فرض التوجيه من اليمين لليسار (RTL) باستخدام CSS
st.markdown("""
    <style>
    * {
        direction: rtl;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- إعداد دوال قراءة وحفظ البيانات ---
DATA_FILE = "plan_action_data.xlsx"


@st.cache_data(ttl=60)
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_excel(DATA_FILE)
        except:
            return pd.DataFrame()
    return pd.DataFrame()


def save_data(uploaded_file):
    df_new = pd.read_excel(uploaded_file)
    df_new.to_excel(DATA_FILE, index=False)
    st.cache_data.clear()


df = load_data()

# --- حساب المؤشرات من البيانات ---
total = len(df)
if total > 0 and 'الحالة' in df.columns:
    completed = len(df[df['الحالة'] == 'منجزة'])
    in_progress = len(df[df['الحالة'] == 'في طور الإنجاز'])
    delayed = len(df[df['الحالة'] == 'متأخرة'])
    not_started = len(df[df['الحالة'] == 'لم تبدأ'])
else:
    completed = in_progress = delayed = not_started = 0

# 2. القائمة الجانبية (Sidebar) - بقيت كما هي تماماً
with st.sidebar:
    st.title("نظام تتبع خطط العمل")
    st.caption("AREF Marrakech-Safi")
    st.markdown("---")

    st.markdown("**جلال الكميلي** · *منسق إقليمي*")

    annee_scolaire = st.selectbox("السنة الدراسية:", ["2026/2027", "2027/2028", "2028/2029"])

    st.markdown("---")
    menu = st.radio("القائمة الرئيسية", [
        "الرئيسية / لوحة القيادة",
        "خطة العمل / العمليات",
        "التقارير",
        "استيراد البيانات"
    ])

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.button("تسجيل الخروج", use_container_width=True)

# 3. محتوى الصفحات (Main Content)
if menu == "الرئيسية / لوحة القيادة":
    st.header("لوحة القيادة - تتبع خطة العمل السنوية")
    st.subheader("مديرية الحوز", divider='gray')

    # البطاقات العلوية (Metrics) تم ربطها بالبيانات
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("إجمالي العمليات", total)
    col2.metric("منجزة", completed)
    col3.metric("في طور الإنجاز", in_progress)
    col4.metric("متأخرة", delayed)
    col5.metric("لم تبدأ", not_started)

    st.markdown("<br>", unsafe_allow_html=True)

    # تقسيم الشاشة إلى عمودين للمؤشرات (كما في التصميم الأصلي)
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("### وضعية العمليات")
        if total > 0:
            status_df = pd.DataFrame({"الحالة": ["منجزة", "في طور الإنجاز", "متأخرة", "لم تبدأ"],
                                      "العدد": [completed, in_progress, delayed, not_started]})
            st.dataframe(status_df, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد عمليات مسجلة لهذه السنة الدراسية.")

        st.markdown("### توزيع العمليات حسب المنسق")
        if total > 0 and 'المنسق' in df.columns:
            st.dataframe(df['المنسق'].value_counts().reset_index().rename(columns={'count': 'العدد'}),
                         use_container_width=True, hide_index=True)
        else:
            st.info("لا يوجد منسقون بعد.")

    with right_col:
        st.markdown("### المؤشرات: المستهدف مقابل المنجز")
        if total > 0 and 'المستهدف' in df.columns and 'المنجز' in df.columns:
            st.dataframe(df[['اسم العملية', 'المستهدف', 'المنجز']].head(5), use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد مؤشرات مسجلة.")

        st.markdown(f"### ⚠ العمليات المتأخرة ( {delayed} )")
        if delayed > 0:
            st.warning("العمليات التالية تجاوزت الآجال المحددة:")
            st.dataframe(df[df['الحالة'] == 'متأخرة'][['اسم العملية', 'المنسق']], use_container_width=True,
                         hide_index=True)
        else:
            st.warning("لا توجد عمليات متأخرة.")

        st.markdown("### ⏰ عمليات ستنتهي قريبًا ( 0 )")
        st.success("لا توجد عمليات قريبة من الانتهاء حالياً.")

# --- قسم استيراد البيانات (تمت برمجته) ---
elif menu == "استيراد البيانات":
    st.header("📥 استيراد ورفع البيانات")
    st.info(
        "قم برفع ملف Excel يحتوي على بيانات خطة العمل. يفضل أن يحتوي على أعمدة مثل: (اسم العملية، المنسق، الحالة، المستهدف، المنجز).")

    uploaded_file = st.file_uploader("اختر ملف الإكسيل (Excel)", type=["xlsx", "xls"])

    if uploaded_file:
        preview_df = pd.read_excel(uploaded_file)
        st.write("معاينة سريعة للملف قبل الحفظ:")
        st.dataframe(preview_df.head(), use_container_width=True)

        if st.button("تأكيد وحفظ البيانات", type="primary"):
            try:
                save_data(uploaded_file)
                st.success("تم استيراد البيانات بنجاح! انتقل الآن إلى 'لوحة القيادة' لرؤية الإحصائيات الجديدة.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء حفظ الملف: {e}")

# --- قسم خطة العمل (تمت برمجته) ---
elif menu == "خطة العمل / العمليات":
    st.header("📋 خطة العمل والعمليات المبرمجة")
    if total > 0:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("لم يتم رفع أي بيانات بعد. يرجى الذهاب إلى صفحة 'استيراد البيانات' لرفع ملفك الأول.")

else:
    st.info(f"أنت الآن في صفحة: {menu} (قيد التطوير)")