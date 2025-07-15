import streamlit as st
import os
import base64
import requests
from PIL import Image
import io
import numpy as np
from openai import OpenAI

# Custom CSS to match the original design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700&display=swap');

* {
    font-family: 'Heebo', sans-serif;
}

.main {
    background: #1e3a8a;
    min-height: 100vh;
    padding: 20px;
}

.stApp {
    background: #1e3a8a;
}

.stMarkdown {
    text-align: center;
}

h1 {
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    color: #2d3748 !important;
    margin-bottom: 10px !important;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1) !important;
    text-align: center !important;
}

.stButton > button {
    background: #1e3a8a !important;
    color: white !important;
    border: none !important;
    padding: 15px 30px !important;
    border-radius: 25px !important;
    font-size: 1.1rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    margin: 20px 0 !important;
    box-shadow: 0 5px 15px rgba(30, 58, 138, 0.3) !important;
    width: auto !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(30, 58, 138, 0.4) !important;
}

.stButton > button:disabled {
    opacity: 0.6 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

.stFileUploader {
    border: 3px dashed #cbd5e0 !important;
    border-radius: 15px !important;
    padding: 40px !important;
    margin: 30px 0 !important;
    background: rgba(247, 250, 252, 0.5) !important;
    text-align: center !important;
}

.stFileUploader:hover {
    border-color: #1e3a8a !important;
    background: rgba(247, 250, 252, 0.8) !important;
}

.stTextArea > div > div > textarea {
    background: #f7fafc !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-family: 'Heebo', sans-serif !important;
    font-size: 1rem !important;
    line-height: 1.6 !important;
    padding: 15px !important;
}

.stTextArea > div > div > textarea:focus {
    border-color: #1e3a8a !important;
    background: white !important;
}

.stExpander {
    background: #f7fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    margin: 10px 0 !important;
}

.stSelectbox > div > div > div {
    background: #f7fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
}

.stMarkdown {
    text-align: center !important;
}

.stMarkdown p {
    font-size: 1.1rem !important;
    color: #718096 !important;
    font-weight: 300 !important;
    text-align: center !important;
}

.stSuccess {
    background: #f0fff4 !important;
    border: 1px solid #9ae6b4 !important;
    border-radius: 10px !important;
    padding: 15px !important;
    margin: 15px 0 !important;
    text-align: center !important;
}

.stError {
    background: #fed7d7 !important;
    border: 1px solid #feb2b2 !important;
    border-radius: 10px !important;
    padding: 15px !important;
    margin: 15px 0 !important;
    text-align: center !important;
}

.stImage {
    border-radius: 10px !important;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
    border: 2px solid #e2e8f0 !important;
    margin: 10px auto !important;
    display: block !important;
}

.stDivider {
    margin: 30px 0 !important;
    border-top: 2px solid #e2e8f0 !important;
}

.container {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 20px !important;
    padding: 40px !important;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
    max-width: 800px !important;
    width: 100% !important;
    margin: 0 auto !important;
}

</style>
""", unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="הסוכן הפואטי",
    page_icon="🎨",
    layout="wide"
)

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found in secrets!")
        return None
    return OpenAI(api_key=api_key)

client = get_openai_client()

# Session state
if 'images' not in st.session_state:
    st.session_state.images = []
if 'texts' not in st.session_state:
    st.session_state.texts = []
if 'gradients' not in st.session_state:
    st.session_state.gradients = []

# Main container
with st.container():
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    # Main title
    st.title("🎨 הסוכן הפואטי")
    st.markdown("העלה תמונה וקבל תיאור פואטי ומוזיקלי!")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "בחר תמונה...", 
        type=['png', 'jpg', 'jpeg'],
        help="העלה תמונה לקבלת ניתוח פואטי"
    )
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="התמונה שהועלתה", use_column_width=True)
        
        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Analyze button
        if st.button("🎵 נתח תמונה פואטית"):
            with st.spinner("יוצר ניתוח פואטי..."):
                try:
                    # Call OpenAI API
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        temperature=0.60,
                        max_tokens=1500,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "אתה סוכן מוזיקלי-פואטי הזוי, ציני ומצחיק. אתה רואה תמונות כאילו היו תווים, צבעים כצלילים, ותנועה כקצב. "
                                    "כל תיאור שאתה כותב נועד להעביר תחושת סאונד, מרקם, ואווירה, כמו פסקול רגשי שנולד מהחזות. "
                                    "אל תיקח את עצמך יותר מידי ברצינות תהיה פיוטי ומצחיק והזוי. "
                                    "אל תברח לגמרי מהתמונה מהתיאור שלך סוכן אחר צריך לייצר סאונד ותמונה חדשים"
                                )
                            },
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "התיאור יהפוך לאחר מכן להנחייה ליצירת תמונה נוספת אבל אל תכתוב את זה. תאר את התמונה המצורפת כמוזיקה פיוטית מצחיקה וצינית בעברית."},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{img_str}"
                                        }
                                    }
                                ]
                            }
                        ]
                    )
                    
                    result = response.choices[0].message.content
                    
                    # Store in session state
                    st.session_state.texts.append({
                        'id': len(st.session_state.texts),
                        'text': result,
                        'timestamp': len(st.session_state.texts)
                    })
                    
                    # Display result
                    st.success("✨ הניתוח הפואטי הושלם!")
                    st.markdown("### 🎭 תיאור פואטי:")
                    st.markdown(f'<div style="background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; text-align: right; line-height: 1.6; color: #4a5568; font-size: 1rem; white-space: pre-wrap;">{result}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"שגיאה בניתוח: {str(e)}")
    
    # Generate image section
    if st.session_state.texts:
        st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
        st.markdown("### 🎨 צור תמונה חדשה")
        
        # Select text to use as prompt
        if len(st.session_state.texts) > 1:
            selected_text_idx = st.selectbox(
                "בחר תיאור ליצירת תמונה:",
                range(len(st.session_state.texts)),
                format_func=lambda x: f"תיאור {x+1}"
            )
            selected_text = st.session_state.texts[selected_text_idx]['text']
        else:
            selected_text = st.session_state.texts[0]['text']
        
        st.markdown("**התיאור שנבחר:**")
        st.markdown(f'<div style="background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; text-align: right; line-height: 1.6; color: #4a5568; font-size: 1rem;">{selected_text}</div>', unsafe_allow_html=True)
        
        if st.button("🎨 צור תמונה"):
            with st.spinner("יוצר תמונה חדשה..."):
                try:
                    image_result = client.images.generate(
                        model="dall-e-3",
                        prompt=selected_text,
                        size="1024x1024",
                        quality="standard",
                        n=1,
                    )
                    
                    if image_result.data and len(image_result.data) > 0:
                        generated_image_url = image_result.data[0].url
                        
                        # Store in session state
                        st.session_state.images.append({
                            'id': len(st.session_state.images),
                            'url': generated_image_url,
                            'prompt': selected_text,
                            'type': 'generated',
                            'timestamp': len(st.session_state.images)
                        })
                        
                        # Display generated image
                        st.success("🎨 התמונה נוצרה בהצלחה!")
                        st.image(generated_image_url, caption="התמונה שנוצרה", use_column_width=True)
                        
                    else:
                        st.error("נכשל ביצירת התמונה")
                        
                except Exception as e:
                    st.error(f"שגיאה ביצירת התמונה: {str(e)}")
    
    # Display history
    if st.session_state.texts or st.session_state.images:
        st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
        st.markdown("### 📚 היסטוריה")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.texts:
                st.markdown("**📝 תיאורים:**")
                for i, text_data in enumerate(st.session_state.texts):
                    with st.expander(f"תיאור {i+1}"):
                        st.markdown(f'<div style="text-align: right; direction: rtl;">{text_data["text"]}</div>', unsafe_allow_html=True)
        
        with col2:
            if st.session_state.images:
                st.markdown("**🖼️ תמונות שנוצרו:**")
                for i, img_data in enumerate(st.session_state.images):
                    with st.expander(f"תמונה {i+1}"):
                        st.image(img_data['url'], use_column_width=True)
                        st.markdown(f'<div style="text-align: right; direction: rtl; font-size: 0.9rem; color: #718096;">{img_data["prompt"][:100]}...</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: white; font-size: 0.9rem;">נוצר עם ❤️ באמצעות Streamlit ו-OpenAI</div>', unsafe_allow_html=True) 