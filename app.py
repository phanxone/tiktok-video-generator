import os
import sys
import json
import time
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory
import generate_video_step3
import tiktok_official_api

app = Flask(__name__, static_folder='static', template_folder='templates')

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
TIKTOK_ACCESS_TOKEN = os.environ.get("TIKTOK_ACCESS_TOKEN", "")

def call_deepseek_ai(mode, topic_name, category, highlights, audience):
    """เรียกใช้ DeepSeek API เพื่อคิดสคริปต์ ชื่อคลิป แคปชัน และแฮชแท็ก ตามโหมดที่เลือก"""
    if not DEEPSEEK_API_KEY:
        if mode == 'normal':
            return {
                "title": f"🔥 {topic_name} รู้ไว้ไม่เพลีย!",
                "voice_script": f"สวัสดีครับทุกคน! วันนี้มาฟังเรื่อง {topic_name} ประเด็นสำคัญคือ {highlights} เหมาะสำหรับ {audience} ชอบคลิปนี้อย่าลืมกดติดตามไว้นะครับ!",
                "caption": f"สาระน่ารู้ประจำวัน! {topic_name} {highlights} ฝากกดติดตามกันด้วยนะครับ ✨🔥",
                "hashtags": "#สาระน่ารู้ #รู้หรือไม่ #เกร็ดความรู้ #ผู้ติดตามใหม่ #TikTokViral"
            }
        else:
            return {
                "title": f"🔥 {topic_name} สายช้อปห้ามพลาด!",
                "voice_script": f"สวัสดีครับทุกคน! วันนี้ผมมีของเด็ดมาแนะนำ {topic_name} จุดเด่นคือ {highlights} ใครสนใจกดที่ตะกร้าเหลืองด้านล่างได้เลยครับ!",
                "caption": f"ไอเทมเด็ดที่ต้องมี! {topic_name} {highlights} กดสั่งซื้อที่ตะกร้าเหลืองมุมล่างซ้ายได้เลย 🛒✨",
                "hashtags": "#TikTokShop #ตะกร้าเหลือง #ของดีบอกต่อ #ปักตะกร้า"
            }
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    if mode == 'normal':
        prompt = f"""คุณคือ Creator มืออาชีพบน TikTok ช่วยเขียนคอนเทนต์สร้างตัวตน/ปั๊มผู้ติดตาม:
หัวข้อเรื่อง: {topic_name}
หมวดหมู่: {category}
ประเด็นสำคัญ: {highlights}
กลุ่มเป้าหมาย: {audience}

ตอบกลับเป็น JSON Format เท่านั้นที่มีคีย์ดังนี้:
1. "title": ชื่อคลิปสั้นๆ สะดุดตา (ไม่เกิน 40 ตัวอักษร)
2. "voice_script": สคริปต์สำหรับเสียงพากย์ความยาว 15-20 วินาที
3. "caption": แคปชันชวนติดตาม
4. "hashtags": แฮชแท็กติดเทรนด์ 5 แท็กรวม #สาระน่ารู้ #รู้หรือไม่"""
    else:
        prompt = f"""คุณคือพนักงานขายมืออาชีพบน TikTok Shop ช่วยเขียนคอนเทนต์ขายสินค้า:
ชื่อสินค้า: {topic_name}
หมวดหมู่: {category}
จุดเด่น: {highlights}
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
        print(f"DeepSeek API Warning: {e}")
        return {
            "title": f"🔥 {topic_name}",
            "voice_script": f"แนะนำ {topic_name} {highlights}",
            "caption": f"{topic_name} {highlights}",
            "hashtags": "#TikTokViral #สาระน่ารู้" if mode == 'normal' else "#TikTokShop #ตะกร้าเหลือง"
        }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    data = request.json or {}
    mode = data.get('mode', 'normal')
    topic_name = data.get('product_name', 'เรื่องน่ารู้ประจำวัน')
    category = data.get('product_category', 'ทั่วไป')
    highlights = data.get('usp_highlights', 'สาระน่ารู้')
    audience = data.get('target_audience', 'ทั่วไป')
    affiliate_link = data.get('affiliate_link', '')

    try:
        # 1. ให้ DeepSeek AI คิดคอนเทนต์ตามโหมด
        ai_result = call_deepseek_ai(mode, topic_name, category, highlights, audience)

        # 2. สร้างไฟล์วิดีโอ MP4 ในโฟลเดอร์ static/videos
        filename = f"video_{mode}_{int(time.time())}.mp4"
        output_path = os.path.join(app.static_folder, 'videos', filename)

        generate_video_step3.generate_tiktok_video(
            product_title=ai_result.get('title', topic_name),
            voice_script=ai_result.get('voice_script', ''),
            output_mp4=output_path
        )

        return jsonify({
            "status": "success",
            "mode": mode,
            "video_url": f"/static/videos/{filename}",
            "video_path": output_path,
            "title": ai_result.get('title', topic_name),
            "caption": ai_result.get('caption', ''),
            "hashtags": ai_result.get('hashtags', ''),
            "product_name": topic_name,
            "affiliate_link": affiliate_link
        })
    except Exception as e:
        print(f"Generation Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/post-tiktok', methods=['POST'])
def post_tiktok():
    data = request.json or {}
    mode = data.get('mode', 'normal')
    video_path = data.get('video_path', '')
    title = data.get('title', '')
    caption = data.get('caption', '') + "\n\n" + data.get('hashtags', '')
    access_token = data.get('access_token', TIKTOK_ACCESS_TOKEN)

    if not access_token:
        time.sleep(1.2)
        mode_str = "คลิปปักตะกร้า Affiliate" if mode == "affiliate" else "คลิปทั่วไปสร้างผู้ติดตาม"
        return jsonify({
            "status": "success",
            "is_simulation": True,
            "message": f"[Simulation Mode] อัปโหลด ({mode_str}) สำเร็จแล้ว! (หากต้องการโพสต์ลงแอปจริง ให้ใส่ TikTok Access Token)",
            "tiktok_post_id": f"tt_sim_{int(time.time())}"
        })

    result = tiktok_official_api.publish_video_to_tiktok(
        access_token=access_token,
        video_path=video_path,
        caption=caption,
        title=title
    )
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"TikTok AI Studio Dashboard running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port)
