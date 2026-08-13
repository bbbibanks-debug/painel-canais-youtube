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
                
                # CORREÇÃO DEFINITIVA: Extrai apenas o ID de 11 caracteres (mantendo maiúsculas/minúsculas)
                id_cru = str(item["id"])
                match_id = re.search(r'([a-zA-Z0-9_-]{11})', id_cru)
                
                if match_id:
                    video_id = match_id.group(1)
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                else:
                    # Fallback de segurança caso o ID já venha limpo
                    video_url = f"https://www.youtube.com/watch?v={id_cru}"
                
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
    <title>Últimos vídeos dos canais</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 30px; }}
        h2 {{ color: #cc0000; margin-bottom: 5px; }}
        .atualizacao {{ font-size: 14px; color: #555; margin-bottom: 20px; }}
        .canal-container {{ margin-bottom: 15px; background: white; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; }}
        .btn-retratil {{ width: 100%; background: #cc0000; color: white; padding: 12px 20px; text-align: left; border: none; font-size: 16px; font-weight: bold; cursor: pointer; display: flex; justify-content: space-between; align-items: center; outline: none; }}
        .btn-retratil:hover {{ background: #b30000; }}
        .tabela-conteudo {{ display: none; padding: 15px; }}
        table {{ border-collapse: collapse; width: 100%; background: white; }}
        th {{ background: #f2f2f2; color: #333; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; }}
        td {{ border-bottom: 1px solid #ddd; padding: 10px; font-size: 14px; vertical-align: top; }}
        .desc-video {{ font-size: 12px; color: #666; margin-top: 4px; line-height: 1.4; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        a {{ color: #0066cc; text-decoration: none; font-weight: bold; }}
        a:hover {{ text-decoration: underline; }}
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
    <h2>Atualizado em: </h2>
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
                    <th style="width: 65%;">Título / Descrição</th>
                    <th style="width: 20%;">Horário</th>
                    <th style="width: 15%;">Link</th>
                </tr>"""
        
        if not videos:
            html_saida += """
                <tr>
                    <td colspan="3" style="text-align:center; color:#777;">Nenhum vídeo encontrado. Canal offline ou instável.</td>
                </tr>"""
        else:
            for v in videos:
                html_saida += f"""
                <tr>
                    <td>
                        <strong>{html.escape(str(v['titulo']))}</strong>
                        <div class="desc-video">{html.escape(str(v['descricao']))}</div>
                    </td>
                    <td>{v['horario']}</td>
                    <td><a href="{v['url']}" target="_blank">Abrir</a></td>
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
