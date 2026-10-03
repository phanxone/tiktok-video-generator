import os
import requests
import json

TIKTOK_API_BASE = "https://open.tiktokapis.com/v2"

def publish_video_to_tiktok(access_token: str, video_path: str, caption: str, title: str):
    """
    ส่งคลิปวิดีโอขึ้น TikTok ผ่าน Content Posting API (Official v2)
    """
    if not access_token:
        return {
            "status": "error",
            "message": "กรุณาใส่ TIKTOK_ACCESS_TOKEN ก่อนใช้งาน Official API"
        }

    if not os.path.exists(video_path):
        return {
            "status": "error",
            "message": f"ไม่พบไฟล์วิดีโอ: {video_path}"
        }

    file_size = os.path.getsize(video_path)

    # Step 1: Initialize Video Post Request
    init_url = f"{TIKTOK_API_BASE}/post/publish/video/init/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    body = {
        "post_info": {
            "title": f"{title}\n\n{caption}",
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": file_size,
            "total_chunk_count": 1
        }
    }

    try:
        res = requests.post(init_url, headers=headers, json=body, timeout=15)
        res_data = res.json()

        if res_data.get("error", {}).get("code") != "ok":
            return {
                "status": "error",
                "message": res_data.get("error", {}).get("message", "TikTok Init Failed")
            }

        upload_url = res_data["data"]["upload_url"]
        publish_id = res_data["data"]["publish_id"]

        # Step 2: Upload Video File Stream
        with open(video_path, "rb") as video_file:
            upload_headers = {
                "Content-Type": "video/mp4",
                "Content-Length": str(file_size),
                "Content-Range": f"bytes 0-{file_size - 1}/{file_size}"
            }
            upload_res = requests.put(upload_url, headers=upload_headers, data=video_file, timeout=60)

        if upload_res.status_code in [200, 201]:
            return {
                "status": "success",
                "message": "อัปโหลดวิดีโอและโพสต์ลง TikTok สำเร็จ!",
                "publish_id": publish_id
            }
        else:
            return {
                "status": "error",
                "message": f"Upload Video Binary Failed (HTTP {upload_res.status_code})"
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}
