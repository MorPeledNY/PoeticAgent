#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from color_utils import analyze_image_edges, create_combined_edge_image
import numpy as np
import base64
from io import BytesIO
from PIL import Image

def create_test_image():
    """יוצר תמונת בדיקה עם קווי מתאר ברורים"""
    # יצירת תמונה עם צורות גיאומטריות
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    
    # רקע לבן
    img.fill(255)
    
    # עיגול שחור
    center = (100, 100)
    radius = 50
    y, x = np.ogrid[:200, :200]
    mask = (x - center[0])**2 + (y - center[1])**2 <= radius**2
    img[mask] = [0, 0, 0]
    
    # ריבוע אדום
    img[20:80, 20:80] = [255, 0, 0]
    
    return img

def test_edge_analysis():
    """בודק ניתוח קווי מתאר"""
    print("🧪 בודק ניתוח קווי מתאר...")
    
    # יצירת תמונת בדיקה
    test_img = create_test_image()
    
    # המרה ל-base64
    pil_img = Image.fromarray(test_img)
    buffer = BytesIO()
    pil_img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    try:
        # ניתוח קווי מתאר
        result = analyze_image_edges(img_base64)
        
        if result and 'edges_image' in result:
            print(f"✅ הצלחתי לנתח קווי מתאר!")
            print(f"   גודל תמונת הקווי מתאר: {len(result['edges_image'])} תווים")
            return True
        else:
            print("❌ נכשל ניתוח קווי המתאר")
            if result and 'error' in result:
                print(f"   שגיאה: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ שגיאה בניתוח קווי המתאר: {str(e)}")
        return False

def test_combined_edge_analysis():
    """בודק ניתוח קווי מתאר משולב"""
    print("\n🧪 בודק ניתוח קווי מתאר משולב...")
    
    # יצירת שתי תמונות בדיקה
    test_img1 = create_test_image()
    test_img2 = create_test_image()
    
    # המרה ל-base64
    pil_img1 = Image.fromarray(test_img1)
    pil_img2 = Image.fromarray(test_img2)
    
    buffer1 = BytesIO()
    buffer2 = BytesIO()
    pil_img1.save(buffer1, format='PNG')
    pil_img2.save(buffer2, format='PNG')
    
    img1_base64 = base64.b64encode(buffer1.getvalue()).decode('utf-8')
    img2_base64 = base64.b64encode(buffer2.getvalue()).decode('utf-8')
    
    try:
        # ניתוח קווי מתאר משולב
        result = create_combined_edge_image(img1_base64, img2_base64)
        
        if result and 'combined_image' in result:
            print(f"✅ הצלחתי ליצור תמונת קווי מתאר משולבת!")
            print(f"   גודל התמונה המשולבת: {len(result['combined_image'])} תווים")
            return True
        else:
            print("❌ נכשל יצירת תמונת קווי המתאר המשולבת")
            return False
            
    except Exception as e:
        print(f"❌ שגיאה ביצירת תמונת קווי המתאר המשולבת: {str(e)}")
        return False

def main():
    """פונקציה ראשית לבדיקות"""
    print("🚀 מתחיל בדיקות קווי מתאר...")
    
    # בדיקת ניתוח קווי מתאר
    edge_success = test_edge_analysis()
    
    # בדיקת ניתוח קווי מתאר משולב
    combined_success = test_combined_edge_analysis()
    
    print(f"\n📊 סיכום בדיקות קווי מתאר:")
    print(f"   ניתוח קווי מתאר: {'✅' if edge_success else '❌'}")
    print(f"   ניתוח קווי מתאר משולב: {'✅' if combined_success else '❌'}")
    
    if edge_success and combined_success:
        print("\n🎉 כל בדיקות קווי המתאר עברו בהצלחה!")
        return True
    else:
        print("\n⚠️  חלק מבדיקות קווי המתאר נכשלו")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 