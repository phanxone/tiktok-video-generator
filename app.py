import os
import sys
import json
import time
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory
import generate_video_step3

app = Flask(__name__, static_folder='static', template_folder='templates')

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

def call_deepseek_ai(product_name, category, usp, audience):
    """เรียกใช้ DeepSeek API เพื่อคิดสคริปต์ ชื่อคลิป แคปชัน และแฮชแท็ก"""
    if not DEEPSEEK_API_KEY:
        # Fallback AI Generator หากยังไม่ได้ใส่ API Key ใน Environment
        return {
            "title": f"🔥 {product_name} สายฟังเพลงห้ามพลาด!",
            "voice_script": f"สวัสดีครับทุกคน! วันนี้ผมมีของเด็ดมาแนะนำ {product_name} จุดเด่นคือ {usp} เหมาะสำหรับ {audience} ใครสนใจกดที่ตะกร้าเหลืองได้เลยครับ!",
            "caption": f"ไอเทมเด็ดที่ต้องมี! {product_name} สเปกจัดเต็ม {usp} กดสั่งซื้อที่ตะกร้าเหลืองมุมล่างซ้ายได้เลย 🛒✨",
            "hashtags": "#TikTokShop #ตะกร้าเหลือง #ของดีบอกต่อ #ปักตะกร้า #หูฟังบลูทูธ"
        }
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""คุณคือ Creator มืออาชีพบน TikTok Shop ช่วยเขียนคอนเทนต์ขายสินค้านี้:
ชื่อสินค้า: {product_name}
หมวดหมู่: {category}
จุดเด่น: {usp}
กลุ่มเป้าหมาย: {audience}

ตอบกลับเป็น JSON Format เท่านั้นที่มีคีย์ดังนี้:
1. "title": ชื่อคลิปสั้นๆ สะดุดตา (ไม่เกิน 40 ตัวอักษร)
2. "voice_script": สคริปต์สำหรับเสียงพากย์ความยาว 15-20 วินาที
3. "caption": แคปชันชวนซื้อ
4. "hashtags": แฮชแท็กติดเทรนด์ 5 แท็กรวม #TikTokShop #ตะกร้าเหลือง"""

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "คุณคือผู้เชี่ยวชาญคอนเทนต์ TikTok ตอบกลับเป็น JSON ภาษาไทยเท่านั้น"},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }

    try:
        res = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=20)
        res_data = res.json()
        content = res_data['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        print(f"DeepSeek API Warning: {e}, falling back to default generator.")
        return {
            "title": f"🔥 {product_name} ของมันต้องมี!",
            "voice_script": f"สวัสดีครับ! แนะนำ {product_name} {usp} ใครสนใจกดที่ตะกร้าเหลืองได้เลยครับ!",
            "caption": f"ปักตะกร้าเรียบร้อย! {product_name} {usp} 🛒✨",
            "hashtags": "#TikTokShop #ตะกร้าเหลือง #ของดีบอกต่อ"
        }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    data = request.json or {}
    product_name = data.get('product_name', 'หูฟังบลูทูธไร้สาย')
    category = data.get('product_category', 'Gadget')
    usp = data.get('usp_highlights', 'แบตอึด เบสแน่น')
    audience = data.get('target_audience', 'สายฟังเพลง')
    affiliate_link = data.get('affiliate_link', '')

    try:
        # 1. ให้ AI (DeepSeek) คิดคอนเทนต์
        ai_result = call_deepseek_ai(product_name, category, usp, audience)

        # 2. สร้างไฟล์วิดีโอ MP4 ในโฟลเดอร์ static/videos
        filename = f"video_{int(time.time())}.mp4"
        output_path = os.path.join(app.static_folder, 'videos', filename)

        generate_video_step3.generate_tiktok_video(
            product_title=ai_result.get('title', product_name),
            voice_script=ai_result.get('voice_script', ''),
            output_mp4=output_path
        )

        return jsonify({
            "status": "success",
            "video_url": f"/static/videos/{filename}",
            "title": ai_result.get('title', product_name),
            "caption": ai_result.get('caption', ''),
            "hashtags": ai_result.get('hashtags', '#TikTokShop'),
            "product_name": product_name,
            "affiliate_link": affiliate_link
        })
    except Exception as e:
        print(f"Generation Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/post-tiktok', methods=['POST'])
def post_tiktok():
    data = request.json or {}
    # จำลองหรือเรียกใช้ TikTok Content Posting API
    time.sleep(1.5)
    return jsonify({
        "status": "success",
        "message": "อัปโหลดคลิปและปักตะกร้าลง TikTok สำเร็จเรียบร้อย!",
        "tiktok_post_id": f"tt_{int(time.time())}"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"TikTok AI Studio Dashboard running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port)
