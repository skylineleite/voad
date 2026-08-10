from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(title="Video of a Down API")

# Libera o acesso para o seu frontend no GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "message": "Vídeo of a Down API funcionando!"}

@app.get("/info")
def get_video_info(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="URL inválida")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            thumbnail = info.get('thumbnail') or (info.get('thumbnails')[-1]['url'] if info.get('thumbnails') else '')
            title = info.get('title', 'Vídeo sem título')
            
            # Pega a URL direta da mídia extraída pelo yt-dlp
            download_url = info.get('url')
            if not download_url and info.get('formats'):
                download_url = info['formats'][-1].get('url')

            return {
                "title": title,
                "thumbnail": thumbnail,
                "extractor": info.get('extractor_key', ''),
                "download_url": download_url or url
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar URL: {str(e)}")
