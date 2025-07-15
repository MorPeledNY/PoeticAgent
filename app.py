import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set environment variables for matplotlib before importing
os.environ['MPLBACKEND'] = 'Agg'  # Force Agg backend before importing matplotlib
os.environ['DISPLAY'] = ''  # Disable display

# Import matplotlib with proper backend
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-GUI backend to prevent crashes
    matplotlib.rcParams['backend'] = 'Agg'  # Force Agg backend
except ImportError as e:
    print(f"Warning: matplotlib import failed: {e}")

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
import base64
from werkzeug.utils import secure_filename

# Import color_utils with error handling
try:
    from color_utils import analyze_image_colors, analyze_combined_edges, analyze_image_edges
except ImportError as e:
    print(f"Warning: color_utils import failed: {e}")
    # Define fallback functions
    def analyze_image_colors(*args, **kwargs):
        return {'error': 'Color analysis not available'}
    def analyze_combined_edges(*args, **kwargs):
        return {'error': 'Edge analysis not available'}
    def analyze_image_edges(*args, **kwargs):
        return {'error': 'Edge analysis not available'}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
CORS(app)

# Global variable to store session data
session_data = {
    'images': [],
    'texts': [],
    'gradients': [],
    'edge_images': []
}

# OpenAI client with error handling
api_key = os.getenv('OPENAI_API_KEY')
print(f"DEBUG: API key found: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"DEBUG: API key starts with: {api_key[:10]}...")

if not api_key:
    print("ERROR: OPENAI_API_KEY environment variable is not set!")
    print("DEBUG: Available environment variables:")
    for key, value in os.environ.items():
        if 'OPENAI' in key or 'API' in key:
            print(f"  {key}: {value[:10] if value else 'None'}...")
    client = None
else:
    try:
        # Set the environment variable explicitly before creating the client
        os.environ['OPENAI_API_KEY'] = api_key
        client = OpenAI()  # This will use the environment variable
        print("✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"ERROR: OpenAI client initialization failed: {e}")
        client = None

# Function to encode image from base64 string
def encode_image_from_base64(base64_string):
    return base64_string

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-all-content', methods=['GET'])
def get_all_content():
    """
    נקודת קצה לקבלת כל התוכן שנוצר במהלך הסשן
    """
    try:
        return jsonify({
            'images': session_data['images'],
            'texts': session_data['texts'],
            'gradients': session_data['gradients'],
            'edge_images': session_data['edge_images']
        })
    except Exception as e:
        return jsonify({'error': f'שגיאה בקבלת התוכן: {str(e)}'}), 500

@app.route('/analyze', methods=['POST'])
def analyze_image():
    try:
        data = request.get_json()
        image_data = data.get('image')
        is_additional = data.get('is_additional', False)  # New parameter to identify additional images
        
        if not image_data:
            return jsonify({'error': 'לא נשלחה תמונה'}), 400
        
        # Remove data URL prefix if present
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Store the image in session data
        image_type = 'additional' if is_additional else 'original'
        session_data['images'].append({
            'id': len(session_data['images']),
            'url': f"data:image/jpeg;base64,{image_data}",
            'type': image_type,
            'timestamp': len(session_data['images'])
        })
        
        if client is None:
            return jsonify({'error': 'OpenAI client not initialized. Please check that OPENAI_API_KEY is set correctly.'}), 500
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.60,
            max_tokens=1500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
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
                        {"type": "text", "text": " התיאור יהפוך לאחר מכן להנחייה ליצירת תמונה נוספת אבל אל תכתוב את זה. תאר את התמונה המצורפת כמוזיקה פיוטית מצחיקה וצינית בעברית."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
        )
        
        result = response.choices[0].message.content
        if result is None:
            result = "לא הצלחתי ליצור תיאור פואטי לתמונה"
        
        # Store the text in session data
        session_data['texts'].append({
            'id': len(session_data['texts']),
            'text': result,
            'timestamp': len(session_data['texts'])
        })
        
        return jsonify({'result': result})
        
    except Exception as e:
        return jsonify({'error': f'שגיאה: {str(e)}'}), 500

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        is_additional = data.get('is_additional', False)  # New parameter to identify additional images
        
        if not prompt:
            return jsonify({'error': 'לא נשלח טקסט להנחיית יצירת התמונה'}), 400
        
        # Generate new image based on the poetic text
        try:
            if client is None:
                return jsonify({'error': 'OpenAI client not initialized. Please check that OPENAI_API_KEY is set correctly.'}), 500
                
            image_result = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Get the image URL
            if image_result.data and len(image_result.data) > 0:
                generated_image_url = image_result.data[0].url
                if generated_image_url:
                    # Store the generated image in session data
                    image_type = 'additional_generated' if is_additional else 'generated'
                    session_data['images'].append({
                        'id': len(session_data['images']),
                        'url': generated_image_url,
                        'prompt': prompt,
                        'type': image_type,
                        'timestamp': len(session_data['images'])
                    })
                    return jsonify({'generated_image_url': generated_image_url})
                else:
                    return jsonify({'error': 'לא התקבל URL לתמונה'}), 500
            else:
                return jsonify({'error': 'לא התקבלו נתונים מהמודל'}), 500
                
        except Exception as e:
            return jsonify({'error': f'שגיאה ביצירת התמונה: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'שגיאה: {str(e)}'}), 500

@app.route('/analyze-colors', methods=['POST'])
def analyze_colors():
    """
    נקודת קצה לניתוח צבעים דומיננטיים בתמונה
    """
    try:
        data = request.get_json()
        image_url = data.get('image_url')
        num_colors = data.get('num_colors', 6)
        save_gradient = data.get('save_gradient', False)  # אופציונלי - שמירה קבועה
        output_dir = data.get('output_dir', 'color_results')  # אופציונלי - תיקיית שמירה
        
        if not image_url:
            return jsonify({'error': 'לא נשלחה תמונה'}), 400
        
        # הורדת התמונה אם זה URL
        import requests
        import base64
        
        if image_url.startswith('http'):
            try:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                image_data = base64.b64encode(response.content).decode('utf-8')
            except Exception as e:
                return jsonify({'error': f'שגיאה בהורדת התמונה: {str(e)}'}), 500
        else:
            # אם זה כבר base64
            image_data = image_url
        
        # ניתוח הצבעים (כולל גרדיאנט אוטומטי)
        result = analyze_image_colors(image_data, num_colors, save_gradient, output_dir)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        # הוספת ניתוח הרמוניה
        from color_utils import analyze_color_harmony
        harmony_result = analyze_color_harmony(result['colors_rgb'])
        if harmony_result and isinstance(result, dict):
            result['harmony_analysis'] = harmony_result
        
        # Store the gradient in session data
        session_data['gradients'].append({
            'id': len(session_data['gradients']),
            'gradient_image': result.get('gradient_image', ''),
            'colors_count': len(result.get('colors_rgb', [])),
            'timestamp': len(session_data['gradients']),
            'type': 'single'
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'שגיאה בניתוח הצבעים: {str(e)}'}), 500

@app.route('/analyze-colors-combined', methods=['POST'])
def analyze_colors_combined():
    """
    נקודת קצה לניתוח צבעים משולב מהתמונה המקורית והתמונה שנוצרה
    """
    try:
        data = request.get_json()
        original_image = data.get('original_image')
        generated_image_url = data.get('generated_image_url')
        num_colors = data.get('num_colors', 8)
        
        if not original_image or not generated_image_url:
            return jsonify({'error': 'חסרים דימויים לניתוח'}), 400
        
        # הורדת התמונה שנוצרה
        import requests
        import base64
        from io import BytesIO
        
        try:
            response = requests.get(generated_image_url, timeout=10)
            response.raise_for_status()
            
            # המרה ל-base64
            generated_image_base64 = base64.b64encode(response.content).decode('utf-8')
            
        except Exception as e:
            return jsonify({'error': f'שגיאה בהורדת התמונה שנוצרה: {str(e)}'}), 500
        
        # ניתוח צבעים מהתמונה המקורית
        original_result = analyze_image_colors(original_image, num_colors)
        if 'error' in original_result:
            return jsonify({'error': f'שגיאה בניתוח התמונה המקורית: {original_result["error"]}'}), 500
        
        # ניתוח צבעים מהתמונה שנוצרה
        generated_result = analyze_image_colors(generated_image_base64, num_colors)
        if 'error' in generated_result:
            return jsonify({'error': f'שגיאה בניתוח התמונה שנוצרה: {generated_result["error"]}'}), 500
        
        # שילוב הצבעים משני הדימויים
        combined_colors = original_result['colors_rgb'] + generated_result['colors_rgb']
        
        # יצירת גרדיאנט משולב
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            gradient_path = os.path.join(temp_dir, 'combined_gradient.png')
            from color_utils import create_color_gradient
            create_color_gradient(combined_colors, gradient_path)
            
            # קריאת הקובץ כ-base64
            with open(gradient_path, 'rb') as f:
                gradient_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # ניתוח הרמוניה משולב
        from color_utils import analyze_color_harmony, colors_to_hex
        harmony_analysis = analyze_color_harmony(combined_colors)
        
        # יצירת תיאורים משולבים
        combined_hex = colors_to_hex(combined_colors)
        combined_descriptions = []
        for i, (rgb, hex_color) in enumerate(zip(combined_colors, combined_hex)):
            source = "מקורית" if i < len(original_result['colors_rgb']) else "נוצרה"
            description = f"צבע {i+1} ({source}): RGB({rgb[0]}, {rgb[1]}, {rgb[2]}) - {hex_color}"
            combined_descriptions.append(description)
        
        result = {
            'colors_rgb': combined_colors,
            'colors_hex': combined_hex,
            'descriptions': combined_descriptions,
            'num_colors': len(combined_colors),
            'gradient_image': f"data:image/png;base64,{gradient_base64}",
            'harmony_analysis': harmony_analysis,
            'original_colors_count': len(original_result['colors_rgb']),
            'generated_colors_count': len(generated_result['colors_rgb'])
        }
        
        # Store the gradient in session data
        session_data['gradients'].append({
            'id': len(session_data['gradients']),
            'gradient_image': f"data:image/png;base64,{gradient_base64}",
            'colors_count': len(combined_colors),
            'timestamp': len(session_data['gradients'])
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'שגיאה בניתוח הצבעים המשולב: {str(e)}'}), 500

@app.route('/analyze-edges', methods=['POST'])
def analyze_edges():
    """
    נקודת קצה לניתוח קווי מתאר מתמונה אחת
    """
    try:
        data = request.get_json()
        image_url = data.get('image_url')
        
        if not image_url:
            return jsonify({'error': 'לא נשלחה תמונה'}), 400
        
        # ניתוח קווי המתאר
        result = analyze_image_edges(image_url)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        # Store the edge image in session data
        session_data['edge_images'].append({
            'id': len(session_data['edge_images']),
            'edge_image': result.get('edge_image', ''),
            'timestamp': len(session_data['edge_images']),
            'type': 'single'
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'שגיאה בניתוח קווי המתאר: {str(e)}'}), 500

@app.route('/analyze-edges-combined', methods=['POST'])
def analyze_edges_combined():
    """
    נקודת קצה לניתוח קווי מתאר משולבים מהתמונה המקורית והתמונה שנוצרה
    """
    try:
        data = request.get_json()
        original_image = data.get('original_image')
        generated_image_url = data.get('generated_image_url')
        blend_ratio = data.get('blend_ratio', 0.5)
        save_image = data.get('save_image', False)
        output_dir = data.get('output_dir', 'edge_results')
        
        if not original_image or not generated_image_url:
            return jsonify({'error': 'חסרים דימויים לניתוח'}), 400
        
        # הורדת התמונה שנוצרה
        import requests
        import base64
        
        try:
            response = requests.get(generated_image_url, timeout=10)
            response.raise_for_status()
            
            # המרה ל-base64
            generated_image_base64 = base64.b64encode(response.content).decode('utf-8')
            
        except Exception as e:
            return jsonify({'error': f'שגיאה בהורדת התמונה שנוצרה: {str(e)}'}), 500
        
        # ניתוח קווי המתאר המשולבים
        result = analyze_combined_edges(
            original_image, 
            generated_image_base64, 
            blend_ratio, 
            save_image, 
            output_dir
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        # Store the edge image in session data
        session_data['edge_images'].append({
            'id': len(session_data['edge_images']),
            'edge_image': result.get('edge_image', ''),
            'blend_ratio': blend_ratio,
            'timestamp': len(session_data['edge_images'])
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'שגיאה בניתוח קווי המתאר: {str(e)}'}), 500

@app.route('/create-combined-gradient', methods=['POST'])
def create_combined_gradient():
    """
    נקודת קצה ליצירת גרדיאנט משולב מרשימת צבעים
    """
    try:
        data = request.get_json()
        colors = data.get('colors')
        
        if not colors:
            return jsonify({'error': 'לא נשלחו צבעים'}), 400
        
        # יצירת גרדיאנט משולב
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            gradient_path = os.path.join(temp_dir, 'combined_gradient.png')
            from color_utils import create_color_gradient
            create_color_gradient(colors, gradient_path)
            
            # קריאת הקובץ כ-base64
            with open(gradient_path, 'rb') as f:
                gradient_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({
            'gradient_image': f"data:image/png;base64,{gradient_base64}",
            'num_colors': len(colors)
        })
        
    except Exception as e:
        return jsonify({'error': f'שגיאה ביצירת הגרדיאנט המשולב: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=True) 