import streamlit as st
import os
import base64
import requests
from PIL import Image, ImageDraw
import io
import numpy as np
from openai import OpenAI
from sklearn.cluster import KMeans
from collections import Counter

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

h3 {
    font-size: 1.3rem !important;
    color: #2d3748 !important;
    margin-bottom: 15px !important;
    font-weight: 500 !important;
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
    max-width: 400px !important;
    max-height: 300px !important;
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

.text-container {
    background: #f7fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 20px !important;
    text-align: right !important;
    line-height: 1.6 !important;
    color: #4a5568 !important;
    font-size: 1rem !important;
    white-space: pre-wrap !important;
    direction: rtl !important;
}

.gradient-container {
    background: #f7fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 15px !important;
    margin-top: 15px !important;
    text-align: center !important;
}

.color-info {
    background: #f7fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 15px !important;
    margin-top: 15px !important;
    text-align: right !important;
    direction: rtl !important;
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

# Color analysis functions
def analyze_image_colors(image_data, num_colors=6):
    """Analyze dominant colors in an image"""
    try:
        # Convert base64 to PIL Image
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        else:
            image = image_data
        
        # Resize image for faster processing
        image = image.resize((150, 150))
        
        # Convert to RGB array
        img_array = np.array(image)
        pixels = img_array.reshape(-1, 3)
        
        # Use K-means to find dominant colors
        kmeans = KMeans(n_clusters=num_colors, random_state=42)
        kmeans.fit(pixels)
        
        # Get colors and their counts
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        color_counts = Counter(labels)
        
        # Sort by frequency
        sorted_colors = sorted(zip(colors, color_counts.values()), 
                             key=lambda x: x[1], reverse=True)
        
        colors_rgb = [color for color, count in sorted_colors]
        
        # Create gradient image
        gradient_img = create_gradient_image(colors_rgb)
        
        # Convert gradient to base64
        buffered = io.BytesIO()
        gradient_img.save(buffered, format="PNG")
        gradient_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Convert colors to hex
        colors_hex = [f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}" for color in colors_rgb]
        
        # Create descriptions
        descriptions = []
        for i, (rgb, hex_color) in enumerate(zip(colors_rgb, colors_hex)):
            description = f"צבע {i+1}: RGB({rgb[0]}, {rgb[1]}, {rgb[2]}) - {hex_color}"
            descriptions.append(description)
        
        return {
            'colors_rgb': colors_rgb,
            'colors_hex': colors_hex,
            'descriptions': descriptions,
            'num_colors': len(colors_rgb),
            'gradient_image': f"data:image/png;base64,{gradient_base64}"
        }
        
    except Exception as e:
        return {'error': f'שגיאה בניתוח הצבעים: {str(e)}'}

def create_gradient_image(colors, width=400, height=100):
    """Create a gradient image from colors"""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    if len(colors) == 1:
        color = tuple(colors[0])
        draw.rectangle([0, 0, width, height], fill=color)
    else:
        segment_width = width // len(colors)
        for i, color in enumerate(colors):
            x1 = i * segment_width
            x2 = (i + 1) * segment_width if i < len(colors) - 1 else width
            draw.rectangle([x1, 0, x2, height], fill=tuple(color))
    
    return img

def analyze_image_edges(image_data):
    """Analyze edges in an image using PIL"""
    try:
        # Convert base64 to PIL Image
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        else:
            image = image_data
        
        # Convert to grayscale
        gray_image = image.convert('L')
        
        # Simple edge detection using PIL
        # Create a new image with edge detection
        edge_image = Image.new('L', gray_image.size)
        edge_pixels = edge_image.load()
        gray_pixels = gray_image.load()
        
        width, height = gray_image.size
        
        for x in range(1, width - 1):
            for y in range(1, height - 1):
                # Simple Sobel-like edge detection
                gx = (gray_pixels[x+1, y] - gray_pixels[x-1, y]) / 2
                gy = (gray_pixels[x, y+1] - gray_pixels[x, y-1]) / 2
                magnitude = int(min(255, (gx**2 + gy**2)**0.5))
                edge_pixels[x, y] = magnitude
        
        # Convert to base64
        buffered = io.BytesIO()
        edge_image.save(buffered, format="PNG")
        edge_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            'edge_image': f"data:image/png;base64,{edge_base64}",
            'width': width,
            'height': height
        }
        
    except Exception as e:
        return {'error': f'שגיאה בניתוח קווי המתאר: {str(e)}'}



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
        st.image(image, caption="התמונה שהועלתה", use_column_width=False, width=400)
        
        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Create columns for buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
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
                        
                        # Display result
                        st.success("✨ הניתוח הפואטי הושלם!")
                        st.markdown("### 🎭 תיאור פואטי:")
                        st.markdown(f'<div class="text-container">{result}</div>', unsafe_allow_html=True)
                        
                        # Add generate image button directly after analysis
                        if st.button("🎨 צור תמונה מהתיאור הזה"):
                            with st.spinner("יוצר תמונה חדשה..."):
                                try:
                                    image_result = client.images.generate(
                                        model="dall-e-3",
                                        prompt=result,
                                        size="1024x1024",
                                        quality="standard",
                                        n=1,
                                    )
                                    
                                    if image_result.data and len(image_result.data) > 0:
                                        generated_image_url = image_result.data[0].url
                                        
                                        # Display generated image
                                        st.success("🎨 התמונה נוצרה בהצלחה!")
                                        st.image(generated_image_url, caption="התמונה שנוצרה", use_column_width=False, width=400)
                                        
                                    else:
                                        st.error("נכשל ביצירת התמונה")
                                        
                                except Exception as e:
                                    st.error(f"שגיאה ביצירת התמונה: {str(e)}")
                        
                    except Exception as e:
                        st.error(f"שגיאה בניתוח: {str(e)}")
        
        with col2:
            # Color analysis button
            if st.button("🎨 ניתוח צבעים"):
                with st.spinner("מנתח צבעים..."):
                    try:
                        color_result = analyze_image_colors(img_str)
                        
                        if 'error' not in color_result:
                            # Display result
                            st.success("🎨 ניתוח הצבעים הושלם!")
                            st.markdown("### 🌈 גרדיאנט צבעים:")
                            st.image(color_result['gradient_image'], use_column_width=False, width=400)
                            
                            st.markdown("### 📊 פרטי צבעים:")
                            color_info = "\n".join(color_result['descriptions'])
                            st.markdown(f'<div class="color-info">{color_info}</div>', unsafe_allow_html=True)
                        else:
                            st.error(color_result['error'])
                            
                    except Exception as e:
                        st.error(f"שגיאה בניתוח צבעים: {str(e)}")
        
        with col3:
            # Edge analysis button
            if st.button("📐 ניתוח קווי מתאר"):
                with st.spinner("מנתח קווי מתאר..."):
                    try:
                        edge_result = analyze_image_edges(img_str)
                        
                        if 'error' not in edge_result:
                            # Display result
                            st.success("📐 ניתוח קווי המתאר הושלם!")
                            st.markdown("### 📐 קווי מתאר:")
                            st.image(edge_result['edge_image'], use_column_width=False, width=400)
                        else:
                            st.error(edge_result['error'])
                            
                    except Exception as e:
                        st.error(f"שגיאה בניתוח קווי מתאר: {str(e)}")
    

    

    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="stDivider"></div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: white; font-size: 0.9rem;">נוצר עם ❤️ באמצעות Streamlit ו-OpenAI</div>', unsafe_allow_html=True) 