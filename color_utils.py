import os
os.environ['MPLBACKEND'] = 'Agg'  # Force Agg backend before importing matplotlib
os.environ['DISPLAY'] = ''  # Disable display

# Import with error handling
try:
    from PIL import Image, ImageDraw
except ImportError as e:
    print(f"Warning: PIL import failed: {e}")
    Image = None
    ImageDraw = None

try:
    import numpy as np
except ImportError as e:
    print(f"Warning: numpy import failed: {e}")
    np = None

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-GUI backend to prevent crashes
    matplotlib.rcParams['backend'] = 'Agg'  # Force Agg backend
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"Warning: matplotlib import failed: {e}")
    matplotlib = None
    plt = None

try:
    from sklearn.cluster import KMeans
except ImportError as e:
    print(f"Warning: sklearn import failed: {e}")
    KMeans = None

import base64
from io import BytesIO
import colorsys
from collections import Counter

def extract_dominant_colors(image_path, num_colors=5):
    """
    מחלץ צבעים דומיננטיים מתמונה
    
    Args:
        image_path (str): נתיב לתמונה או נתוני base64
        num_colors (int): מספר הצבעים לחילוץ
    
    Returns:
        list: רשימת צבעים ב-RGB
    """
    # Check if required libraries are available
    if Image is None:
        return []
    if np is None:
        return []
    if KMeans is None:
        return []
        
    try:
        # בדיקה אם זה נתיב קובץ או base64
        if os.path.exists(image_path):
            img = Image.open(image_path)
        elif image_path.startswith('data:image'):
            # הסרת ה-prefix של data URL
            image_data = image_path.split(',')[1]
            img_bytes = base64.b64decode(image_data)
            img = Image.open(BytesIO(img_bytes))
        else:
            # נסה לטפל כנתוני base64 רגילים
            img_bytes = base64.b64decode(image_path)
            img = Image.open(BytesIO(img_bytes))
        
        if img is None:
            raise ValueError("לא הצלחתי לטעון את התמונה")
        
        # המרה ל-RGB
        img = img.convert('RGB')
        
        # שינוי גודל לתמונה קטנה יותר לביצועים טובים יותר
        img = img.resize((150, 150))
        
        # המרה למערך numpy
        img_array = np.array(img)
        
        # שינוי צורה למערך של פיקסלים
        img_reshaped = img_array.reshape((-1, 3))
        
        # חילוץ צבעים דומיננטיים עם K-means
        kmeans = KMeans(n_clusters=num_colors, n_init='auto', random_state=42)
        kmeans.fit(img_reshaped)
        
        # קבלת הצבעים המרכזיים
        colors = kmeans.cluster_centers_.astype(int)
        
        return colors.tolist()
        
    except Exception as e:
        print(f"שגיאה בחילוץ צבעים: {str(e)}")
        return []

def colors_to_hex(colors):
    """
    ממיר צבעים מ-RGB ל-HEX
    
    Args:
        colors (list): רשימת צבעים ב-RGB
    
    Returns:
        list: רשימת צבעים ב-HEX
    """
    hex_colors = []
    for color in colors:
        hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
        hex_colors.append(hex_color)
    return hex_colors

def plot_colors(colors, save_path=None):
    """
    מציג גרף של הצבעים הדומיננטיים
    
    Args:
        colors (list): רשימת צבעים
        save_path (str): נתיב לשמירת הגרף (אופציונלי)
    """
    # Check if matplotlib is available
    if plt is None or np is None:
        print("Warning: matplotlib or numpy not available for plotting")
        return
        
    try:
        plt.figure(figsize=(10, 3))
        for i, color in enumerate(colors):
            plt.fill_between([i, i+1], 0, 1, color=np.array(color)/255)
            plt.text(i+0.5, 0.5, f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}', 
                    ha='center', va='center', fontsize=10, color='white' if sum(color)/3 < 128 else 'black')
        
        plt.title('צבעים דומיננטיים בתמונה', fontsize=14)
        plt.axis("off")
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            print(f"הגרף נשמר ב: {save_path}")
        else:
            plt.show()
            
        plt.close()
        
    except Exception as e:
        print(f"שגיאה ביצירת הגרף: {str(e)}")

def analyze_image_colors(image_data, num_colors=6, save_gradient=False, output_dir="color_results"):
    """
    פונקציה ראשית לניתוח צבעים של תמונה
    
    Args:
        image_data (str): נתוני התמונה (base64 או נתיב)
        num_colors (int): מספר צבעים לחילוץ
        save_gradient (bool): האם לשמור את הגרדיאנט כקובץ
        output_dir (str): תיקייה לשמירת הקבצים
    
    Returns:
        dict: תוצאות הניתוח
    """
    try:
        # חילוץ צבעים
        colors = extract_dominant_colors(image_data, num_colors)
        
        if not colors:
            return {'error': 'לא הצלחתי לחלץ צבעים מהתמונה'}
        
        # המרה ל-HEX
        hex_colors = colors_to_hex(colors)
        
        # יצירת תיאור של הצבעים
        color_descriptions = []
        for i, (rgb, hex_color) in enumerate(zip(colors, hex_colors)):
            description = f"צבע {i+1}: RGB({rgb[0]}, {rgb[1]}, {rgb[2]}) - {hex_color}"
            color_descriptions.append(description)
        
        # יצירת גרדיאנט
        import tempfile
        import os
        from datetime import datetime
        
        with tempfile.TemporaryDirectory() as temp_dir:
            gradient_path = os.path.join(temp_dir, 'color_gradient.png')
            create_color_gradient(colors, gradient_path)
            
            # קריאת הקובץ כ-base64
            with open(gradient_path, 'rb') as f:
                import base64
                gradient_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # שמירה קבועה אם נדרש
            saved_gradient_path = None
            if save_gradient:
                os.makedirs(output_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                saved_gradient_path = os.path.join(output_dir, f'gradient_{timestamp}.png')
                
                # העתקת הקובץ
                import shutil
                shutil.copy2(gradient_path, saved_gradient_path)
                print(f"✅ הגרדיאנט נשמר ב: {saved_gradient_path}")
        
        result = {
            'colors_rgb': colors,
            'colors_hex': hex_colors,
            'descriptions': color_descriptions,
            'num_colors': len(colors),
            'gradient_image': f"data:image/png;base64,{gradient_base64}"
        }
        
        if saved_gradient_path:
            result['saved_gradient_path'] = saved_gradient_path
        
        return result
        
    except Exception as e:
        return {'error': f'שגיאה בניתוח הצבעים: {str(e)}'}

def create_color_palette(colors, save_path=None):
    """
    יוצר פלטת צבעים יפה עם קודי HEX
    
    Args:
        colors (list): רשימת צבעים
        save_path (str): נתיב לשמירת הפלטה (אופציונלי)
    """
    try:
        fig, ax = plt.subplots(figsize=(12, 4))
        
        for i, color in enumerate(colors):
            # יצירת מלבן צבע
            from matplotlib.patches import Rectangle
            rect = Rectangle((i, 0), 1, 1, facecolor=np.array(color)/255)
            ax.add_patch(rect)
            
            # הוספת קוד HEX
            hex_code = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
            ax.text(i+0.5, 0.5, hex_code, ha='center', va='center', 
                   fontsize=12, fontweight='bold',
                   color='white' if sum(color)/3 < 128 else 'black')
        
        ax.set_xlim(0, len(colors))
        ax.set_ylim(0, 1)
        ax.set_title('פלטת צבעים דומיננטיים', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300, facecolor='white')
            print(f"הפלטה נשמרה ב: {save_path}")
        else:
            plt.show()
            
        plt.close()
        
    except Exception as e:
        print(f"שגיאה ביצירת פלטת צבעים: {str(e)}")

def create_color_pie_chart(colors, save_path=None):
    """
    יוצר גרף עוגה של הצבעים הדומיננטיים
    
    Args:
        colors (list): רשימת צבעים
        save_path (str): נתיב לשמירת הגרף (אופציונלי)
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # יצירת נתונים לגרף עוגה (כל צבע שווה חלק)
        sizes = [1] * len(colors)
        labels = [f'#{c[0]:02x}{c[1]:02x}{c[2]:02x}' for c in colors]
        colors_normalized = [np.array(c)/255 for c in colors]
        
        result = ax.pie(sizes, labels=labels, colors=[tuple(c) for c in colors_normalized],
                       autopct='%1.1f%%', startangle=90)
        
        # עיצוב הטקסט
        if len(result) > 2:
            autotexts = result[2]
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        
        ax.set_title('התפלגות הצבעים הדומיננטיים', fontsize=16, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300, facecolor='white')
            print(f"גרף העוגה נשמר ב: {save_path}")
        else:
            plt.show()
            
        plt.close()
        
    except Exception as e:
        print(f"שגיאה ביצירת גרף עוגה: {str(e)}")

def analyze_color_harmony(colors):
    """
    מנתח הרמוניה של צבעים
    
    Args:
        colors (list): רשימת צבעים
    
    Returns:
        dict: ניתוח ההרמוניה
    """
    try:
        harmony_analysis = {
            'complementary': [],
            'analogous': [],
            'triadic': [],
            'monochromatic': [],
            'color_temperatures': {'warm': 0, 'cool': 0, 'neutral': 0}
        }
        
        for color in colors:
            # המרה ל-HSV לניתוח טוב יותר
            h, s, v = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
            
            # ניתוח טמפרטורת צבע
            if h < 0.1 or h > 0.8:  # אדום-כתום או כחול-סגול
                if s > 0.3 and v > 0.3:
                    harmony_analysis['color_temperatures']['warm'] += 1
            elif 0.4 < h < 0.7:  # כחול-ירוק
                if s > 0.3 and v > 0.3:
                    harmony_analysis['color_temperatures']['cool'] += 1
            else:
                harmony_analysis['color_temperatures']['neutral'] += 1
        
        # ניתוח צבעים משלימים
        for i, color1 in enumerate(colors):
            for j, color2 in enumerate(colors[i+1:], i+1):
                h1, _, _ = colorsys.rgb_to_hsv(color1[0]/255, color1[1]/255, color1[2]/255)
                h2, _, _ = colorsys.rgb_to_hsv(color2[0]/255, color2[1]/255, color2[2]/255)
                
                # בדיקה אם צבעים משלימים (הפרש של 0.5 ב-HSV)
                if abs(h1 - h2) > 0.45 and abs(h1 - h2) < 0.55:
                    harmony_analysis['complementary'].append((i, j))
        
        return harmony_analysis
        
    except Exception as e:
        print(f"שגיאה בניתוח הרמוניה: {str(e)}")
        return {}

def create_color_wheel(colors, save_path=None):
    """
    יוצר גלגל צבעים עם הצבעים הדומיננטיים
    
    Args:
        colors (list): רשימת צבעים
        save_path (str): נתיב לשמירת הגרף (אופציונלי)
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # יצירת גלגל צבעים
        angles = np.linspace(0, 2*np.pi, len(colors), endpoint=False)
        
        for i, (angle, color) in enumerate(zip(angles, colors)):
            # יצירת קשת לכל צבע
            theta = np.linspace(angle, angle + 2*np.pi/len(colors), 100)
            r = [0.8, 1.0]
            theta_grid, r_grid = np.meshgrid(theta, r)
            
            from matplotlib.colors import ListedColormap
            ax.pcolormesh(theta_grid, r_grid, np.ones_like(theta_grid), 
                         cmap=ListedColormap([np.array(color)/255]))
            
            # הוספת תווית
            ax.text(angle + np.pi/len(colors), 0.6, f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}',
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   color='white' if sum(color)/3 < 128 else 'black')
        
        ax.set_title('גלגל צבעים דומיננטיים', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylim(0, 1.2)
        ax.set_xticks([])
        ax.set_yticks([])
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300, facecolor='white')
            print(f"גלגל הצבעים נשמר ב: {save_path}")
        else:
            plt.show()
            
        plt.close()
        
    except Exception as e:
        print(f"שגיאה ביצירת גלגל צבעים: {str(e)}")

def create_color_gradient(colors, save_path=None):
    """
    יוצר גרדיאנט צבעים מהצבעים הדומיננטיים
    
    Args:
        colors (list): רשימת צבעים
        save_path (str): נתיב לשמירת הגרף (אופציונלי)
    """
    try:
        fig, ax = plt.subplots(figsize=(12, 3))
        
        # יצירת גרדיאנט
        gradient = np.linspace(0, 1, 1000)
        
        for i in range(len(colors) - 1):
            color1 = np.array(colors[i]) / 255
            color2 = np.array(colors[i + 1]) / 255
            
            start_idx = int(i * 1000 / (len(colors) - 1))
            end_idx = int((i + 1) * 1000 / (len(colors) - 1))
            
            for j in range(start_idx, end_idx):
                t = (j - start_idx) / (end_idx - start_idx)
                interpolated_color = color1 * (1 - t) + color2 * t
                ax.axvline(x=j/1000, color=interpolated_color, linewidth=2)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300, facecolor='white')
            print(f"הגרדיאנט נשמר ב: {save_path}")
        else:
            plt.show()
            
        plt.close()
        
    except Exception as e:
        print(f"שגיאה ביצירת גרדיאנט: {str(e)}")

def generate_color_report(colors, save_dir=None):
    """
    יוצר דוח מלא של ניתוח הצבעים
    
    Args:
        colors (list): רשימת צבעים
        save_dir (str): תיקייה לשמירת הקבצים (אופציונלי)
    
    Returns:
        dict: דוח מלא עם כל הניתוחים
    """
    try:
        report = {
            'colors_rgb': colors,
            'colors_hex': colors_to_hex(colors),
            'harmony_analysis': analyze_color_harmony(colors),
            'visualizations': {}
        }
        
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            
            # יצירת כל הויזואליזציות
            plot_colors(colors, os.path.join(save_dir, 'color_bars.png'))
            create_color_palette(colors, os.path.join(save_dir, 'color_palette.png'))
            create_color_pie_chart(colors, os.path.join(save_dir, 'color_pie.png'))
            create_color_wheel(colors, os.path.join(save_dir, 'color_wheel.png'))
            create_color_gradient(colors, os.path.join(save_dir, 'color_gradient.png'))
            
            report['visualizations'] = {
                'bars': 'color_bars.png',
                'palette': 'color_palette.png',
                'pie': 'color_pie.png',
                'wheel': 'color_wheel.png',
                'gradient': 'color_gradient.png'
            }
        
        return report
        
    except Exception as e:
        print(f"שגיאה ביצירת דוח: {str(e)}")
        return {}

def create_combined_edge_image(image1_data, image2_data, output_path=None, blend_ratio=0.5):
    """
    יוצר תמונת קווי מתאר משולבת משתי תמונות
    Args:
        image1_data (str): נתוני התמונה הראשונה (base64 או נתיב)
        image2_data (str): נתוני התמונה השנייה (base64 או נתיב)
        output_path (str): נתיב לשמירת התמונה (אופציונלי)
        blend_ratio (float): יחס הערבוב בין התמונות (0-1)
    Returns:
        dict: {'combined_image': base64 string}
    """
    try:
        # טעינת התמונה הראשונה
        if os.path.exists(image1_data):
            img1 = cv2.imread(image1_data)
        elif image1_data.startswith('data:image'):
            image_data = image1_data.split(',')[1]
            img_array = np.frombuffer(base64.b64decode(image_data), np.uint8)
            img1 = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        else:
            img_array = np.frombuffer(base64.b64decode(image1_data), np.uint8)
            img1 = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        # טעינת התמונה השנייה
        if os.path.exists(image2_data):
            img2 = cv2.imread(image2_data)
        elif image2_data.startswith('data:image'):
            image_data = image2_data.split(',')[1]
            img_array = np.frombuffer(base64.b64decode(image_data), np.uint8)
            img2 = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        else:
            img_array = np.frombuffer(base64.b64decode(image2_data), np.uint8)
            img2 = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img1 is None or img2 is None:
            raise ValueError("לא ניתן לטעון את התמונות. בדקי את הנתונים.")
        # יישור גודל
        height = min(img1.shape[0], img2.shape[0])
        width = min(img1.shape[1], img2.shape[1])
        img1 = cv2.resize(img1, (width, height))
        img2 = cv2.resize(img2, (width, height))
        # ערבוב התמונות
        blended = cv2.addWeighted(img1, blend_ratio, img2, 1 - blend_ratio, 0)
        # המרה לגווני אפור
        gray = cv2.cvtColor(blended, cv2.COLOR_BGR2GRAY)
        # זיהוי קווי מתאר
        edges = cv2.Canny(gray, 100, 200)
        # המרה ל-RGB לצורך הצגה
        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        # שמירה זמנית
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            temp_path = tmp_file.name
        cv2.imwrite(temp_path, edges_rgb)
        # קריאת הקובץ כ-base64
        with open(temp_path, 'rb') as f:
            edges_base64 = base64.b64encode(f.read()).decode('utf-8')
        # שמירה קבועה אם נדרש
        if output_path:
            cv2.imwrite(output_path, edges_rgb)
            print(f"✔️ שמרתי את הרישום הקווי בשם {output_path}")
        # ניקוי קובץ זמני
        os.unlink(temp_path)
        return {'combined_image': f"data:image/png;base64,{edges_base64}"}
    except Exception as e:
        print(f"שגיאה ביצירת תמונת קווי המתאר: {str(e)}")
        return None

def analyze_image_edges(image_url):
    """
    פונקציה לניתוח קווי מתאר מתמונה אחת
    
    Args:
        image_url (str): URL של התמונה או נתוני base64
    
    Returns:
        dict: תוצאות הניתוח
    """
    try:
        import requests
        import base64
        from io import BytesIO
        
        # הורדת התמונה אם זה URL
        if image_url.startswith('http'):
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            img_bytes = response.content
            img = Image.open(BytesIO(img_bytes))
        else:
            # אם זה כבר base64
            if image_url.startswith('data:image'):
                image_data = image_url.split(',')[1]
                img_bytes = base64.b64decode(image_data)
            else:
                img_bytes = base64.b64decode(image_url)
            img = Image.open(BytesIO(img_bytes))
        
        if img is None:
            return {'error': 'לא הצלחתי לטעון את התמונה'}
        
        # המרה לגווני אפור
        gray = img.convert('L')
        
        # המרה למערך numpy
        gray_array = np.array(gray)
        
        # זיהוי קווי מתאר פשוט
        edges = np.zeros_like(gray_array)
        
        # Simple edge detection
        for x in range(1, gray_array.shape[0] - 1):
            for y in range(1, gray_array.shape[1] - 1):
                # Simple Sobel-like edge detection
                gx = (gray_array[x+1, y] - gray_array[x-1, y]) / 2
                gy = (gray_array[x, y+1] - gray_array[x, y-1]) / 2
                magnitude = int(min(255, (gx**2 + gy**2)**0.5))
                edges[x, y] = magnitude
        
        # המרה חזרה לתמונה
        edge_image = Image.fromarray(edges.astype(np.uint8))
        
        # המרה ל-base64
        buffer = BytesIO()
        edge_image.save(buffer, format='PNG')
        edges_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            'edge_image': f"data:image/png;base64,{edges_base64}",
            'width': img.width,
            'height': img.height
        }
        
    except Exception as e:
        return {'error': f'שגיאה בניתוח קווי המתאר: {str(e)}'}

def analyze_combined_edges(image1_data, image2_data, blend_ratio=0.5, save_image=False, output_dir="edge_results"):
    """
    פונקציה ראשית לניתוח קווי מתאר משולבים
    
    Args:
        image1_data (str): נתוני התמונה הראשונה
        image2_data (str): נתוני התמונה השנייה
        blend_ratio (float): יחס הערבוב
        save_image (bool): האם לשמור את התמונה כקובץ
        output_dir (str): תיקייה לשמירת הקבצים
    
    Returns:
        dict: תוצאות הניתוח
    """
    try:
        # יצירת נתיב שמירה אם נדרש
        saved_image_path = None
        if save_image:
            os.makedirs(output_dir, exist_ok=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_image_path = os.path.join(output_dir, f'combined_edges_{timestamp}.png')
        
        # יצירת תמונת קווי המתאר
        edges_image = create_combined_edge_image(
            image1_data, 
            image2_data, 
            output_path=saved_image_path,
            blend_ratio=blend_ratio
        )
        
        if edges_image is None:
            return {'error': 'לא הצלחתי ליצור תמונת קווי מתאר'}
        
        result = {
            'edges_image': edges_image,
            'blend_ratio': blend_ratio
        }
        
        if saved_image_path:
            result['saved_image_path'] = saved_image_path
        
        return result
        
    except Exception as e:
        return {'error': f'שגיאה בניתוח קווי המתאר: {str(e)}'}

# דוגמה לשימוש
if __name__ == "__main__":
    # דוגמה עם תמונה מקומית
    image_path = "/Users/morpeled/poeticagent/venv/1.jpeg"  # החלף בנתיב התמונה שלך
    
    if os.path.exists(image_path):
        result = analyze_image_colors(image_path, num_colors=6)
        
        if 'error' not in result:
            print("צבעים דומיננטיים:")
            for desc in result['descriptions']:
                print(desc)
            
            # יצירת גרף
            plot_colors(result['colors_rgb'])
        else:
            print(f"שגיאה: {result['error']}")
    else:
        print("התמונה לא נמצאה. אנא החלף את הנתיב ב-image_path") 