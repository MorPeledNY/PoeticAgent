import streamlit as st
import os
import base64
import requests
from PIL import Image
import io
import numpy as np
from openai import OpenAI

# Page configuration
st.set_page_config(
    page_title="Poetic Agent - AI Image Analysis",
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

# Main title
st.title("🎨 Poetic Agent - AI Image Analysis")
st.markdown("Upload an image and get a poetic, musical description!")

# File uploader
uploaded_file = st.file_uploader(
    "Choose an image...", 
    type=['png', 'jpg', 'jpeg'],
    help="Upload an image to get a poetic analysis"
)

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Convert to base64
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Analyze button
    if st.button("🎵 Analyze Image Poetically"):
        with st.spinner("Creating poetic analysis..."):
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
                st.success("✨ Poetic Analysis Complete!")
                st.markdown("### 🎭 Poetic Description:")
                st.write(result)
                
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")

# Generate image section
if st.session_state.texts:
    st.markdown("---")
    st.markdown("### 🎨 Generate New Image")
    
    # Select text to use as prompt
    if len(st.session_state.texts) > 1:
        selected_text_idx = st.selectbox(
            "Choose a description to generate image from:",
            range(len(st.session_state.texts)),
            format_func=lambda x: f"Description {x+1}"
        )
        selected_text = st.session_state.texts[selected_text_idx]['text']
    else:
        selected_text = st.session_state.texts[0]['text']
    
    st.markdown("**Selected description:**")
    st.write(selected_text)
    
    if st.button("🎨 Generate Image"):
        with st.spinner("Generating new image..."):
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
                    st.success("🎨 Image Generated Successfully!")
                    st.image(generated_image_url, caption="Generated Image", use_column_width=True)
                    
                else:
                    st.error("Failed to generate image")
                    
            except Exception as e:
                st.error(f"Error generating image: {str(e)}")

# Display history
if st.session_state.texts or st.session_state.images:
    st.markdown("---")
    st.markdown("### 📚 History")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.texts:
            st.markdown("**📝 Descriptions:**")
            for i, text_data in enumerate(st.session_state.texts):
                with st.expander(f"Description {i+1}"):
                    st.write(text_data['text'])
    
    with col2:
        if st.session_state.images:
            st.markdown("**🖼️ Generated Images:**")
            for i, img_data in enumerate(st.session_state.images):
                with st.expander(f"Image {i+1}"):
                    st.image(img_data['url'], use_column_width=True)
                    st.write(f"**Prompt:** {img_data['prompt'][:100]}...")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and OpenAI") 