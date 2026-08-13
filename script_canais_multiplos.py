import html
import re
from datetime import datetime
from yt_dlp import YoutubeDL
from datetime import datetime, timedelta, timezone

def coletar_videos(nome_exato, canal_url, limite=10):
    canal_url = canal_url.rstrip("/")
    if not canal_url.endswith("/videos"):
        if canal_url.endswith("/featured"):
            canal_url = canal_url.replace("/featured", "/videos")
        else:
            canal_url = canal_url + "/videos"
    
    opts = {
        "quiet": True,
        "extract_flat": True,
        "playlistend": limite,
        "no_warnings": True,
        "ignoreerrors": True,
        "nocheckcertificate": True,
        "extractor_args": {
            "youtube": {
                "lang": ["pt"]
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    }
    
    try:
        with YoutubeDL(opts) as ydl:
            playlist = ydl.extract_info(canal_url, download=False)
            
            videos = []
            if playlist and "entries" in playlist:
                for item in playlist["entries"]:
                    if not item or not item.get("id"):
                        continue
                    
                    # Captura estritamente o ID de 11 caracteres puro fornecido pelo extract_flat
                    video_id = str(item["id"]).strip()
                    
                    # GARANTIA ABSOLUTA DO FORMATO DO LINK:
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    dia_postagem = "Não disponível"
                    if item.get("upload_date"):
                        try:
                            dia_postagem = datetime.strptime(item["upload_date"], "%Y%m%d").strftime("%d/%m/%Y")
                        except Exception:
                            pass
                    
                    descricao = item.get("description", "Sem descrição disponível.")
                    if len(descricao) > 150:
                        descricao = descricao[:147] + "..."
                    
                    videos.append({
                        "titulo": item.get("title", "Vídeo sem título"),
                        "descricao": descricao,
                        "horario": dia_postagem,
                        "url": video_url
                    })
            return nome_exato, videos
    except Exception as e:
        print(f"Erro ao coletar canal {nome_exato}: {e}")
        return nome_exato, []

def gerar_html(dados_canais, arquivo="youtube_multicanais.html"):
    agora = datetime.now(timezone(timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M:%S")
    
    html_saida = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <title> YouTube Monitor</title>
    <style>
        body {{ 
            font-family: 'Consolas', 'Courier New', monospace, Arial, sans-serif; 
            background: #0b0c10; 
            color: #ffffff; 
            margin: 30px; 
        }}
        h2 {{ 
            color: #ff6600; 
            margin-bottom: 5px; 
            font-size: 24px;
            text-transform: uppercase;
            border-bottom: 2px solid #ff6600;
            padding-bottom: 10px;
        }}
        .atualizacao {{ 
            font-size: 13px; 
            color: #888888; 
            margin-bottom: 20px; 
        }}
        .canal-container {{ 
            margin-bottom: 10px; 
            background: #1f2833; 
            border: 1px solid #45a29e;
            border-radius: 2px; 
            overflow: hidden; 
        }}
        .btn-retratil {{ 
            width: 100%; 
            background: #1a1a1a; 
            color: #ff6600; 
            padding: 12px 20px; 
            text-align: left; 
            border: none; 
            font-size: 15px; 
            font-weight: bold; 
            cursor: pointer; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            outline: none;
            border-bottom: 1px solid #333;
        }}
        .btn-retratil:hover {{ 
            background: #262626; 
            color: #ff8533;
        }}
        .tabela-conteudo {{ 
            display: none; 
            padding: 15px; 
            background: #121212;
        }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            background: #121212; 
        }}
        th {{ 
            background: #1a1a1a; 
            color: #ff6600; 
            padding: 10px;
            text-align: left; 
            border-bottom: 2px solid #ff6600; 
            font-size: 13px;
            text-transform: uppercase;
        }}
        td {{ 
            border-bottom: 1px solid #262626; 
            padding: 12px 10px; 
            font-size: 14px; 
            vertical-align: top; 
        }}
        .desc-video {{ 
            font-size: 12px; 
            color: #aaaaaa; 
            margin-top: 6px; 
            line-height: 1.5; 
        }}
        tr:nth-child(even) {{ 
            background: #161616; 
        }}
        a {{ 
            color: #00ffcc; 
            text-decoration: none; 
            font-weight: bold; 
        }}
        a:hover {{ 
            text-decoration: underline; 
            color: #ff6600;
        }}
    </style>
    <script>
        function alternarJanela(id) {{
            var conteudo = document.getElementById('conteudo-' + id);
            var botao = document.getElementById('btn-' + id);
            var nomeCanal = botao.getAttribute('data-nome');
            
            if (conteudo.style.display === 'block') {{
                conteudo.style.display = 'none';
                botao.innerHTML = nomeCanal + ' <span>▼</span>';
            }} else {{
                conteudo.style.display = 'block';
                botao.innerHTML = nomeCanal + ' <span>▲</span>';
            }}
        }}
    </script>
</head>
<body>
    <h2>Monitor Videos YouTube</h2>
    <div class="atualizacao">Atualizado em: {agora}</div>
"""

    for idx, (nome_canal, videos) in enumerate(dados_canais):
        html_saida += f"""
        <div class="canal-container">
            <button id="btn-{idx}" class="btn-retratil" data-nome="{html.escape(nome_canal)}" onclick="alternarJanela({idx})">
                {html.escape(nome_canal)} <span>▼</span>
            </button>
            <div id="conteudo-{idx}" class="tabela-conteudo">
                <table>
                    <tr>
                        <th style="width: 85%;">Título / Descrição</th>
                        <th style="width: 15%;">Link</th>
                    </tr>"""
        
        if not videos:
            html_saida += """
                    <tr>
                        <td colspan="2" style="text-align:center; color:#555;">Nenhum vídeo encontrado. Canal offline ou instável.</td>
                    </tr>"""
        else:
            for v in videos:
                html_saida += f"""
                    <tr>
                        <td>
                            <strong style="color: #ffffff;">{html.escape(str(v['titulo']))}</strong>
                            <div class="desc-video">{html.escape(str(v['descricao']))}</div>
                        </td>
                        <td><a href="{v['url']}" target="_blank">► ABRIR</a></td>
                    </tr>"""
                    
        html_saida += """
                </table>
            </div>
        </div>"""
        
    html_saida += """
</body>
</html>"""
    
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(html_saida)

if __name__ == "__main__":
    CANAIS_MAPEADOS = [
        ("Market Makers", "https://www.youtube.com/@mmakers"),
        ("Stock Pickers", "https://www.youtube.com/@StockPickers"),
        ("BTG Trader", "https://www.youtube.com/@BTGTrader"),
        ("Futurum Talks", "https://www.youtube.com/@FuturumTalks"),
        ("Os Traders", "https://www.youtube.com/@ostraderspodcast/featured"),
        ("BMC News", "https://www.youtube.com/@BMCNEWStv"),
        ("Exame", "https://www.youtube.com/@exame"),
        ("Invest News", "https://www.youtube.com/@InvestNewsBR"),
        ("Neo Feed", "https://www.youtube.com/@NeoFeedBrasil"),
        ("Infomoney", "https://www.youtube.com/@infomoney/videos"),
        ("Valor Econômico", "https://www.youtube.com/valoreconomico/videos")

    ]

    
    resultados = []
    for nome_exato, url in CANAIS_MAPEADOS:
        print(f"Coletando dados de: {nome_exato}...")
        nome, lista_videos = coletar_videos(nome_exato, url, limite=10)
        resultados.append((nome, lista_videos))
        
    gerar_html(resultados)
    print("\nArquivo atualizado gerado com sucesso: youtube_multicanais.html")
