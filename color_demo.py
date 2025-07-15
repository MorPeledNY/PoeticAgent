#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
דוגמה לשימוש בכל הדרכים להצגת תוצאות ניתוח צבעים
"""

import os
from color_utils import (
    analyze_image_colors, 
    plot_colors, 
    create_color_palette,
    create_color_pie_chart,
    create_color_wheel,
    create_color_gradient,
    generate_color_report,
    analyze_color_harmony
)

def demo_color_analysis(image_path):
    """
    מדגים ניתוח צבעים עם גרדיאנט בלבד
    """
    print("🎨 מתחיל ניתוח צבעים...")
    
    # ניתוח עם גרדיאנט אוטומטי (ללא שמירה)
    result = analyze_image_colors(image_path, num_colors=8)
    
    if 'error' in result:
        print(f"❌ שגיאה: {result['error']}")
        return
    
    print("✅ ניתוח הצבעים הושלם!")
    print(f"📊 נמצאו {result['num_colors']} צבעים דומיננטיים")
    
    # ניתוח הרמוניה
    print("🎼 מנתח הרמוניה...")
    harmony = analyze_color_harmony(result['colors_rgb'])
    
    # הצגת התוצאות
    print("\n" + "="*50)
    print("🎨 תוצאות ניתוח הצבעים")
    print("="*50)
    
    print(f"\n📊 צבעים דומיננטיים ({result['num_colors']}):")
    for i, (rgb, hex_color) in enumerate(zip(result['colors_rgb'], result['colors_hex'])):
        print(f"  {i+1}. RGB{rgb} - {hex_color}")
    
    print(f"\n🎼 ניתוח הרמוניה:")
    print(f"  🌡️  צבעים חמים: {harmony['color_temperatures']['warm']}")
    print(f"  ❄️  צבעים קרים: {harmony['color_temperatures']['cool']}")
    print(f"  ⚪ צבעים ניטרליים: {harmony['color_temperatures']['neutral']}")
    
    if harmony['complementary']:
        print(f"  🔄 צבעים משלימים: {len(harmony['complementary'])} זוגות")
    
    print(f"\n🌈 הגרדיאנט נוצר אוטומטית!")
    print(f"📊 התמונה נשלחת ב-base64 בשדה 'gradient_image'")
    
    print(f"\n✨ הניתוח הושלם בהצלחה!")
    print("🎨 הגרדיאנט זמין בתוצאות ה-API")
    
    # דוגמה לשמירה קבועה
    print(f"\n" + "="*50)
    print("💾 דוגמה לשמירה קבועה")
    print("="*50)
    
    print("💡 כדי לשמור את הגרדיאנט כקובץ קבוע:")
    print("   result = analyze_image_colors(image_path, num_colors=8, save_gradient=True)")
    print("   print(f'הקובץ נשמר ב: {result[\"saved_gradient_path\"]}')")
    
    # הדגמה של שמירה
    print("\n🎯 מנסה לשמור גרדיאנט קבוע...")
    saved_result = analyze_image_colors(image_path, num_colors=8, save_gradient=True, output_dir="my_gradients")
    
    if 'saved_gradient_path' in saved_result:
        print(f"✅ הגרדיאנט נשמר בהצלחה!")
        print(f"📁 מיקום: {saved_result['saved_gradient_path']}")
    else:
        print("❌ לא הצלחתי לשמור את הגרדיאנט")

def demo_api_usage():
    """
    מדגים שימוש ב-API
    """
    print("\n" + "="*50)
    print("🌐 שימוש ב-API")
    print("="*50)
    
    print("\n🎨 ניתוח צבעים עם גרדיאנט אוטומטי:")
    print("   Endpoint: /analyze-colors")
    print("   Method: POST")
    print("   Data: {")
    print("     'image': 'base64_image_data',")
    print("     'num_colors': 6")
    print("   }")
    
    print("\n📊 תגובה:")
    print("   {")
    print("     'colors_rgb': [[255, 0, 0], [0, 255, 0], ...],")
    print("     'colors_hex': ['#ff0000', '#00ff00', ...],")
    print("     'descriptions': ['צבע 1: RGB(255, 0, 0) - #ff0000', ...],")
    print("     'num_colors': 6,")
    print("     'gradient_image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...',")
    print("     'harmony_analysis': {")
    print("       'color_temperatures': {'warm': 2, 'cool': 3, 'neutral': 1},")
    print("       'complementary': [[0, 3], [1, 4]]")
    print("     }")
    print("   }")

if __name__ == "__main__":
    # בדיקה אם קיימת תמונה לדוגמה
    image_path = "/Users/morpeled/poeticagent/venv/1.jpeg"
    
    if os.path.exists(image_path):
        print("🚀 מתחיל הדגמה של ניתוח צבעים...")
        demo_color_analysis(image_path)
        demo_api_usage()
    else:
        print("❌ לא נמצאה תמונה לדוגמה")
        print("📝 אנא החלף את הנתיב ב-image_path או העלה תמונה")
        print("💡 דוגמה: python color_demo.py") 