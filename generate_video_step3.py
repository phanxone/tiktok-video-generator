import os
import sys
import asyncio
import edge_tts
from moviepy import ImageClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont

async def create_voiceover(text: str, output_mp3: str, voice: str = "th-TH-NiwatNeural"):
    """สร้างเสียงพากย์จากข้อความด้วย Edge-TTS"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_mp3)

def create_product_banner(title: str, output_image: str):
    """สร้างภาพแบนเนอร์แนวตั้ง 9:16 (1080x1920) สำหรับ TikTok"""
    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), color=(18, 18, 24))
    draw = ImageDraw.Draw(img)

    # วาดพื้นหลัง Box สีแนว TikTok
    draw.rectangle([50, 200, width - 50, 400], fill=(255, 0, 75))
    
    # พิมพ์ข้อความ
    try:
        font = ImageFont.truetype("arial.ttf", 55)
    except:
        font = ImageFont.load_default()
        
    draw.text((width // 2, 300), title, font=font, fill=(255, 255, 255), anchor="mm")
    draw.text((width // 2, 1600), "👇 กดปุ่มสั่งซื้อที่ตะกร้าเหลืองด้านล่างได้เลย!", font=font, fill=(255, 220, 0), anchor="mm")

    img.save(output_image)

def generate_tiktok_video(product_title: str, voice_script: str, output_mp4: str):
    """ประกอบเสียงพากย์ + ภาพ ออกมาเป็นไฟล์ MP4"""
    audio_file = "temp_voice.mp3"
    banner_image = "temp_banner.png"

    # 1. แปลงเสียงพากย์
    print("[1/3] Generating Edge-TTS voiceover...")
    asyncio.run(create_voiceover(voice_script, audio_file))

    # 2. สร้างภาพประกอบ
    print("[2/3] Generating TikTok banner image...")
    create_product_banner(product_title, banner_image)

    # 3. รวมเป็นวิดีโอด้วย MoviePy
    print("[3/3] Rendering MP4 video with MoviePy...")
    audio_clip = AudioFileClip(audio_file)
    duration = audio_clip.duration

    image_clip = ImageClip(banner_image).with_duration(duration)
    final_clip = image_clip.with_audio(audio_clip)

    final_clip.write_videofile(
        output_mp4,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    # ทำความสะอาดไฟล์ชั่วคราว
    if os.path.exists(audio_file): os.remove(audio_file)
    if os.path.exists(banner_image): os.remove(banner_image)

    print(f"DONE: Generated video successfully: {output_mp4}")

if __name__ == "__main__":
    title = "หูฟังบลูทูธไร้สาย เสียงเบสแน่น"
    script = "สวัสดีครับทุกคน! วันนี้ผมมีของเด็ดมาแนะนำ หูฟังบลูทูธไร้สาย เสียงเบสแน่น แบตอึด 40 ชั่วโมง กันน้ำ IPX5 ใครเป็นสายฟังเพลงห้ามพลาด กดสั่งที่ตะกร้าเหลืองได้เลยครับ!"
    output = "tiktok_product_video.mp4"

    generate_tiktok_video(title, script, output)
