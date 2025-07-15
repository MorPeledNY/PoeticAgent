#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from color_utils import extract_dominant_colors, create_color_gradient
import numpy as np
import base64
from io import BytesIO
from PIL import Image

def create_test_image():
    """יוצר תמונת בדיקה פשוטה"""
    # יצירת תמונה פשוטה עם צבעים שונים
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # אזור אדום
    img[0:50, 0:50] = [255, 0, 0]
    # אזור ירוק
    img[0:50, 50:100] = [0, 255, 0]
    # אזור כחול
    img[50:100, 0:50] = [0, 0, 255]
    # אזור צהוב
    img[50:100, 50:100] = [255, 255, 0]
    
    return img

def test_color_extraction():
    """בודק חילוץ צבעים"""
    print("🧪 בודק חילוץ צבעים...")
    
    # יצירת תמונת בדיקה
    test_img = create_test_image()
    
    # המרה ל-base64
    pil_img = Image.fromarray(test_img)
    buffer = BytesIO()
    pil_img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # חילוץ צבעים
    colors = extract_dominant_colors(img_base64, num_colors=4)
    
    if colors:
        print(f"✅ הצלחתי לחלץ {len(colors)} צבעים:")
        for i, color in enumerate(colors):
            print(f"   צבע {i+1}: RGB{tuple(color)}")
        return colors
    else:
        print("❌ נכשל חילוץ הצבעים")
        return None

def test_gradient_creation():
    """בודק יצירת גרדיאנט"""
    print("\n🧪 בודק יצירת גרדיאנט...")
    
    colors = test_color_extraction()
    if not colors:
        print("❌ לא ניתן ליצור גרדיאנט ללא צבעים")
        return False
    
    try:
        # יצירת גרדיאנט
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            gradient_path = os.path.join(temp_dir, 'test_gradient.png')
            create_color_gradient(colors, gradient_path)
            
            # בדיקה שהקובץ נוצר
            if os.path.exists(gradient_path):
                file_size = os.path.getsize(gradient_path)
                print(f"✅ הגרדיאנט נוצר בהצלחה! גודל: {file_size} bytes")
                return True
            else:
                print("❌ הגרדיאנט לא נוצר")
                return False
                
    except Exception as e:
        print(f"❌ שגיאה ביצירת הגרדיאנט: {str(e)}")
        return False

def main():
    """פונקציה ראשית לבדיקות"""
    print("🚀 מתחיל בדיקות...")
    
    # בדיקת חילוץ צבעים
    color_success = test_color_extraction() is not None
    
    # בדיקת יצירת גרדיאנט
    gradient_success = test_gradient_creation()
    
    print(f"\n📊 סיכום בדיקות:")
    print(f"   חילוץ צבעים: {'✅' if color_success else '❌'}")
    print(f"   יצירת גרדיאנט: {'✅' if gradient_success else '❌'}")
    
    if color_success and gradient_success:
        print("\n🎉 כל הבדיקות עברו בהצלחה!")
        return True
    else:
        print("\n⚠️  חלק מהבדיקות נכשלו")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 