# Poetic Agent - סוכן פואטי-מוזיקלי

אפליקציה שמנתחת תמונות וממירה אותן לתיאורים פואטיים-מוזיקליים, ואז יוצרת תמונות חדשות בהתבסס על התיאורים.

## תכונות

- **ניתוח תמונות**: מנתח תמונות וממיר אותן לתיאורים פואטיים-מוזיקליים
- **יצירת תמונות**: יוצר תמונות חדשות בהתבסס על התיאורים הפואטיים
- **ניתוח צבעים מתקדם**: מחלץ צבעים דומיננטיים ומציג אותם כגרדיאנט
- **ניתוח צבעים משולב**: מנתח צבעים מהתמונה המקורית והתמונה שנוצרה יחד
- **ממשק ווב**: ממשק ידידותי למשתמש עם כפתור לניתוח צבעים מתקדם

## התקנה

1. התקן את התלויות:
```bash
pip install -r requirements.txt
```

2. הפעל את האפליקציה:
```bash
python app.py
```

3. פתח את הדפדפן בכתובת: `http://localhost:8080`

## API Endpoints

### `/analyze` (POST)
מנתח תמונה ויוצר תיאור פואטי-מוזיקלי.

**פרמטרים:**
- `image`: נתוני התמונה ב-base64

**תגובה:**
```json
{
  "result": "תיאור פואטי של התמונה..."
}
```

### `/generate-image` (POST)
יוצר תמונה חדשה בהתבסס על טקסט.

**פרמטרים:**
- `prompt`: הטקסט להנחיית יצירת התמונה

**תגובה:**
```json
{
  "generated_image_url": "URL של התמונה שנוצרה"
}
```

### `/analyze-colors` (POST)
מחלץ צבעים דומיננטיים מתמונה ויוצר גרדיאנט אוטומטית.

**פרמטרים:**
- `image`: נתוני התמונה ב-base64
- `num_colors`: מספר הצבעים לחילוץ (ברירת מחדל: 6)

**תגובה:**
```json
{
  "colors_rgb": [[255, 0, 0], [0, 255, 0], ...],
  "colors_hex": ["#ff0000", "#00ff00", ...],
  "descriptions": ["צבע 1: RGB(255, 0, 0) - #ff0000", ...],
  "num_colors": 6,
  "gradient_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "harmony_analysis": {
    "color_temperatures": {"warm": 2, "cool": 3, "neutral": 1},
    "complementary": [[0, 3], [1, 4]]
  }
}
```

### `/analyze-colors-combined` (POST)
מנתח צבעים משולב מהתמונה המקורית והתמונה שנוצרה.

**פרמטרים:**
- `original_image`: נתוני התמונה המקורית ב-base64
- `generated_image_url`: URL של התמונה שנוצרה
- `num_colors`: מספר הצבעים לחילוץ מכל תמונה (ברירת מחדל: 8)

**תגובה:**
```json
{
  "colors_rgb": [[255, 0, 0], [0, 255, 0], ...],
  "colors_hex": ["#ff0000", "#00ff00", ...],
  "descriptions": ["צבע 1 (מקורית): RGB(255, 0, 0) - #ff0000", ...],
  "num_colors": 16,
  "gradient_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "harmony_analysis": {
    "color_temperatures": {"warm": 4, "cool": 6, "neutral": 2},
    "complementary": [[0, 8], [1, 9]]
  },
  "original_colors_count": 8,
  "generated_colors_count": 8
}
```

## שימוש בקוד

### ניתוח צבעים בסיסי
```python
from color_utils import analyze_image_colors

# ניתוח צבעים מתמונה
result = analyze_image_colors(image_data, num_colors=6)
print(result['colors_hex'])  # ['#ff0000', '#00ff00', ...]
```

### ניתוח צבעים עם גרדיאנט אוטומטי
```python
from color_utils import analyze_image_colors

# ניתוח צבעים עם גרדיאנט אוטומטי
result = analyze_image_colors(image_data, num_colors=6)
print(result['colors_hex'])  # ['#ff0000', '#00ff00', ...]
print(result['gradient_image'])  # data:image/png;base64,...

# ניתוח הרמוניה
from color_utils import analyze_color_harmony
harmony = analyze_color_harmony(result['colors_rgb'])
print(f"צבעים חמים: {harmony['color_temperatures']['warm']}")
print(f"צבעים קרים: {harmony['color_temperatures']['cool']}")
```

### ניתוח צבעים משולב
```python
# ניתוח צבעים משולב מהתמונה המקורית והתמונה שנוצרה
response = requests.post('/analyze-colors-combined', json={
    'original_image': 'base64_original_image',
    'generated_image_url': 'https://example.com/generated_image.jpg',
    'num_colors': 8
})
result = response.json()
print(f"גרדיאנט משולב: {result['gradient_image']}")
```

### דוגמה מלאה
```python
# הרץ את הדוגמה המלאה
python color_demo.py
```

## הצגת תוצאות ניתוח הצבעים

### 🎨 **גרדיאנט אוטומטי:**
- **יצירה אוטומטית** - הגרדיאנט נוצר בכל ניתוח
- **איכות גבוהה** - תמונה ב-300 DPI
- **פורמט base64** - זמין ישירות ב-API
- **מעבר חלק** - בין כל הצבעים הדומיננטיים

### 🔄 **ניתוח צבעים משולב:**
- **שילוב דימויים** - מנתח את התמונה המקורית והתמונה שנוצרה יחד
- **גרדיאנט משולב** - יוצר גרדיאנט מכל הצבעים הדומיננטיים
- **מזהה מקור** - מציין מאיזה תמונה הגיע כל צבע
- **ניתוח הרמוניה משולב** - מנתח את ההרמוניה של כל הצבעים יחד

### 📊 **ניתוח מתקדם:**
- **ניתוח הרמוניה** - זיהוי צבעים משלימים וטמפרטורות
- **טמפרטורת צבעים** - חלוקה לצבעים חמים/קרים/ניטרליים
- **צבעים משלימים** - זיהוי זוגות צבעים משלימים

### 📋 **מידע מפורט:**
- **קודי צבעים** - RGB ו-HEX לכל צבע
- **תיאורים מפורטים** - הסבר על כל צבע ומקורו
- **ניתוח סטטיסטי** - מידע על התפלגות הצבעים

## תלויות

- Flask - שרת ווב
- OpenAI - API ליצירת תוכן ותמונות
- OpenCV - עיבוד תמונות
- NumPy - חישובים מתמטיים
- Matplotlib - יצירת גרפים
- Scikit-learn - אלגוריתמי למידת מכונה

## מבנה הפרויקט

```
poeticagent/
├── app.py                    # האפליקציה הראשית
├── color_utils.py            # פונקציות לניתוח צבעים
├── color_demo.py             # דוגמה לשימוש
├── requirements.txt          # תלויות הפרויקט
├── templates/                # תבניות HTML
│   └── index.html
├── color_analysis_results/   # תוצאות ניתוח צבעים
└── README.md                # קובץ זה
```

## הערות

- האפליקציה דורשת מפתח API של OpenAI
- הפונקציונליות של ניתוח הצבעים עובדת עם תמונות בפורמטים נפוצים (JPEG, PNG, וכו')
- הגרפים נוצרים עם matplotlib ויכולים להישמר כקבצים
- הגרדיאנט נוצר אוטומטית באיכות גבוהה (300 DPI)
- הניתוח כולל זיהוי אוטומטי של הרמוניה וטמפרטורת צבעים
- התמונה נשלחת בפורמט base64 זמין ישירות ב-API 