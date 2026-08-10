from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os

app = FastAPI(title="Video of a Down API")

# Libera o acesso para o seu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "message": "Vídeo of a Down API está funcionando!"}

@app.get("/info")
def get_video_info(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="URL inválida")

    # Configurações do yt-dlp com os cookies e evasão de bots
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        # Verifica se o arquivo existe para não dar erro em outros sites
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'extractor_args': {
            'youtube': ['player_client=android,web']
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            thumbnail = info.get('thumbnail') or (info.get('thumbnails')[-1]['url'] if info.get('thumbnails') else '')
            title = info.get('title', 'Vídeo sem título')
            
            url_video = info.get('url')
            if not url_video and info.get('formats'):
                # Tenta pegar o melhor formato de mp4
                best_format = next((f for f in info['formats'][::-1] if f.get('ext') == 'mp4' and f.get('vcodec') != 'none'), info['formats'][-1])
                url_video = best_format.get('url')

            return {
                "title": title,
                "thumbnail": thumbnail,
                "extractor": info.get('extractor_key', 'Desconhecido'),
                "download_url": url_video or url
            }
    except Exception as e:
        print(f"Erro detalhado: {str(e)}") # Vai ajudar a ver no Log do Render se der ruim de novo
        raise HTTPException(status_code=500, detail="Erro ao extrair a mídia. O YouTube pode estar bloqueando a requisição.")
