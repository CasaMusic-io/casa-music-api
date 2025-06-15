from flask import Flask, request, jsonify
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
import requests

app = Flask(__name__)

def download_file(url, filename):
    print(f"Descargando {filename} desde {url}...")
    r = requests.get(url)
    r.raise_for_status()
    with open(filename, 'wb') as f:
        f.write(r.content)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📦 Datos recibidos:", data)

    try:
        title = data.get("title", "output")
        audio_url = data["audio_url"]
        video_url = data["video_url"]
        logo_url = data["logo_url"]
        logo_casa = data["logo_casa"]

        # Descargar archivos
        download_file(audio_url, "audio.mp3")
        download_file(video_url, "video_base.mp4")
        download_file(logo_url, "logo.png")
        download_file(logo_casa, "logo_casa.png")

        # Procesar video
        video = VideoFileClip("video_base.mp4").resize(height=1080)
        audio = AudioFileClip("audio.mp3")
        loop_count = int(audio.duration // video.duration) + 1
        video_looped = video.loop(n=loop_count).subclip(0, audio.duration)

        logo1 = ImageClip("logo.png").set_duration(audio.duration).resize(height=150).set_position(("left", "bottom"))
        logo2 = ImageClip("logo_casa.png").set_duration(audio.duration).resize(height=100).set_position(("right", "bottom"))

        final = CompositeVideoClip([video_looped, logo1, logo2]).set_audio(audio)
        final.write_videofile(f"{title}.mp4", codec="libx264", audio_codec="aac")

        return jsonify({"message": f"✅ Video generado: {title}.mp4"}), 200

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
