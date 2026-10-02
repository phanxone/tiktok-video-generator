from flask import Flask, request, jsonify
import generate_video_step3

app = Flask(__name__)

@app.route('/generate-video', methods=['POST'])
def make_video():
    data = request.json or {}
    title = data.get('title', 'หูฟังบลูทูธไร้สาย เสียงเบสแน่น')
    script = data.get('script', 'สวัสดีครับทุกคน! วันนี้ผมมีของเด็ดมาแนะนำ หูฟังบลูทูธไร้สาย เสียงเบสแน่น แบตอึด 40 ชั่วโมง กันน้ำ IPX5 กดสั่งซื้อที่ตะกร้าเหลืองได้เลยครับ!')
    output = data.get('output', 'tiktok_product_video.mp4')
    
    try:
        generate_video_step3.generate_tiktok_video(title, script, output)
        return jsonify({"status": "success", "video_path": output})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Video Generation API running on port {port}")
    app.run(host='0.0.0.0', port=port)
