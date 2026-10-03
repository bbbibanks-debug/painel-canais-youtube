import html
import re
from datetime import datetime
from yt_dlp import YoutubeDL
from datetime import datetime, timedelta, timezone

def coletar_videos(nome_exato, canal_url, categoria, limite=10):
    """
    Acessa a URL do canal do YouTube e extrai os metadados dos vídeos recentes
    utilizando a biblioteca yt_dlp de forma assíncrona/flat estruturada.
    """
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
            return nome_exato, videos, categoria
    except Exception as e:
        print(f"Erro ao coletar canal {nome_exato}: {e}")
        return nome_exato, [], categoria
def gerar_html(dados_canais, arquivo="youtube_multicanais.html"):
    """
    Gera o dashboard em HTML com navegação estruturada por janelas/abas e
    conteúdos em contêineres retráteis, mantendo o padrão visual escuro original.
    """
    agora = datetime.now(timezone(timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M:%S")
    
    # Extrair categorias únicas mantendo a ordem de aparição para as abas
    categorias_vistas = []
    for _, _, cat in dados_canais:
        if cat not in categorias_vistas:
            categorias_vistas.append(cat)
            
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
        .abas-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-bottom: 20px;
            border-bottom: 2px solid #45a29e;
            padding-bottom: 5px;
        }}
        .aba-btn {{
            background: #1a1a1a;
            color: #45a29e;
            border: 1px solid #45a29e;
            padding: 10px 15px;
            cursor: pointer;
            font-family: 'Consolas', monospace;
            font-weight: bold;
            font-size: 14px;
            text-transform: uppercase;
            border-radius: 3px 3px 0 0;
            transition: all 0.2s ease;
        }}
        .aba-btn:hover {{
            background: #262626;
            color: #ff6600;
        }}
        .aba-btn.ativa {{
            background: #45a29e;
            color: #0b0c10;
            border-bottom: 1px solid #45a29e;
        }}
        .janela-conteudo {{
            display: none;
        }}
        .janela-conteudo.ativa {{
            display: block;
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

        function mudarAba(slugCategoria) {{
            var janelas = document.getElementsByClassName('janela-conteudo');
            for (var i = 0; i < janelas.length; i++) {{
                janelas[i].classList.remove('ativa');
            }}
            var botoes = document.getElementsByClassName('aba-btn');
            for (var i = 0; i < botoes.length; i++) {{
                botoes[i].classList.remove('ativa');
            }}
            document.getElementById('janela-' + slugCategoria).classList.add('ativa');
            document.getElementById('tab-' + slugCategoria).classList.add('ativa');
        }}
    </script>
</head>
<body>
    <h2>Monitor Videos YouTube</h2>
    <div class="atualizacao">Atualizado em: {agora}</div>
    <div class="abas-container">
"""
    
    for idx, cat in enumerate(categorias_vistas):
        slug = re.sub(r'[^a-z0-9]', '', cat.lower())
        classe_ativa = "ativa" if idx == 0 else ""
        html_saida += f'        <button id="tab-{slug}" class="aba-btn {classe_ativa}" onclick="mudarAba(\'{slug}\')">{html.escape(cat)}</button>\n'
        
    html_saida += "    </div>\n"

    for idx_cat, cat in enumerate(categorias_vistas):
        slug = re.sub(r'[^a-z0-9]', '', cat.lower())
        classe_ativa = "ativa" if idx_cat == 0 else ""
        html_saida += f'    <div id="janela-{slug}" class="janela-conteudo {classe_ativa}">\n'
        
        for idx_canal, (nome_canal, videos, categoria_canal) in enumerate(dados_canais):
            if categoria_canal != cat:
                continue
                
            id_unico = f"{slug}-{idx_canal}"
            html_saida += f"""
        <div class="canal-container">
            <button id="btn-{id_unico}" class="btn-retratil" data-nome="{html.escape(nome_canal)}" onclick="alternarJanela('{id_unico}')">
                {html.escape(nome_canal)} <span>▼</span>
            </button>
            <div id="conteudo-{id_unico}" class="tabela-conteudo">
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
            
        html_saida += "    </div>\n"
        
    html_saida += """
</body>
</html>"""
    
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(html_saida)
if __name__ == "__main__":
    CANAIS_MAPEADOS = [
    ("The Economist", "https://www.youtube.com/@TheEconomist", "Notícias e Revistas"),
    ("TIME", "https://www.youtube.com/@TIME", "Notícias e Revistas"),
    ("The Wall Street Journal", "https://www.youtube.com/@wsj", "Notícias e Revistas"),
    ("The New York Times", "https://www.youtube.com/@nytimes/videos", "Notícias e Revistas"),
    ("The Atlantic", "https://www.youtube.com/@TheAtlantic", "Notícias e Revistas"),
    ("The Spectator", "https://www.youtube.com/@SpectatorTV", "Notícias e Revistas"),
    ("Forbes", "https://www.youtube.com/@Forbes", "Notícias e Revistas"),
    ("Fortune", "https://www.youtube.com/@fortune", "Notícias e Revistas"),
    ("Businessweek", "https://www.youtube.com/@businessweek", "Notícias e Revistas"),
    ("Yahoo Finance", "https://www.youtube.com/@YahooFinance", "Agências e TV"),
    ("Bloomberg", "https://www.youtube.com/@markets", "Agências e TV"),
    ("Bloomberg Originals", "https://www.youtube.com/@business", "Agências e TV"),
    ("Bloomberg Tech", "https://www.youtube.com/@BloombergTech", "Agências e TV"),
    ("Bloomberg Podcasts", "https://www.youtube.com/@BloombergPodcasts", "Agências e TV"),
    ("CNBC International Live", "https://www.youtube.com/@CNBCInternationalLive", "Agências e TV"),
    ("CNBCi", "https://www.youtube.com/@CNBCi", "Agências e TV"),
    ("CNBC Television", "https://www.youtube.com/@CNBCtelevision", "Agências e TV"),
    ("NBC News", "https://www.youtube.com/@NBCNews", "Agências e TV"),
    ("Associated Press", "https://www.youtube.com/@AssociatedPress", "Agências e TV"),
    ("Reuters", "https://www.youtube.com/@Reuters", "Agências e TV"),
    ("WSJ Opinion", "https://www.youtube.com/@WSJopinion", "Agências e TV"),
    ("FMI", "https://www.youtube.com/@imf/videos", "Instituições Oficiais"),
    ("World Bank", "https://www.youtube.com/@WorldBankGroup/videos", "Instituições Oficiais"),
    ("World Bank", "https://www.youtube.com/@WorldBankGroup/videos", "Instituições Oficiais"),
    ("BIS", "https://www.youtube.com/@bisbribiz/videos", "Instituições Oficiais"),
    ("IFC", "https://www.youtube.com/@IFC_org/videos", "Instituições Oficiais"),
    ("Banco Central do Brasil", "https://www.youtube.com/@BancoCentralBR", "Instituições Oficiais"),
    ("Federal Reserve", "https://www.youtube.com/@federalreserve", "Instituições Oficiais"),
    ("ECB", "https://www.youtube.com/@ecbeuro", "Instituições Oficiais"),
    ("B3", "https://www.youtube.com/@bolsadobrasil", "Instituições Oficiais"),
    ("Febraban", "https://www.youtube.com/@FEBRABANOficial", "Instituições Oficiais"),
    ("NYSE", "https://www.youtube.com/@NYSEofficial", "Instituições Oficiais"),
    ("LSE", "https://www.youtube.com/@theLondonSchoolofEconomics", "Instituições Oficiais"),
    ("Times Brasil", "https://www.youtube.com/@otimesbrasil", "Cobertura Nacional BR"),
    ("CNN Money", "https://www.youtube.com/@cnnbrmoney/videos", "Cobertura Nacional BR"),
    ("BBC Nacional", "https://www.youtube.com/@BBCNewsBrasil/videos", "Cobertura Nacional BR"),
    ("BrazilJournal", "https://www.youtube.com/@BrazilJournal", "Cobertura Nacional BR"),
    ("InvestNewsBR", "https://www.youtube.com/@InvestNewsBR", "Cobertura Nacional BR"),
    ("Capital Aberto", "https://www.youtube.com/@canalcapitalaberto", "Cobertura Nacional BR"),
    ("MoneyTimes", "https://www.youtube.com/@MoneyTimesBR", "Cobertura Nacional BR"),
    ("BMC News", "https://www.youtube.com/@BMCNEWStv", "Cobertura Nacional BR"),
    ("Exame", "https://www.youtube.com/@exame", "Cobertura Nacional BR"),
    ("Neo Feed", "https://www.youtube.com/@NeoFeedBrasil", "Cobertura Nacional BR"),
    ("Infomoney", "https://www.youtube.com/@infomoney/videos", "Cobertura Nacional BR"),
    ("Valor Econômico", "https://www.youtube.com/valoreconomico/videos", "Cobertura Nacional BR"),
    ("Canal MyNews", "https://www.youtube.com/@CanalMyNews", "Cobertura Nacional BR"),
    ("MRT News", "https://www.youtube.com/@mrtnewsoficial", "Cobertura Nacional BR"),
    ("Safra", "https://www.youtube.com/@SafraBanco/videos", "Bancos e Corretoras"),
    ("Bradesco", "https://www.youtube.com/@Bradesco/videos", "Bancos e Corretoras"),
    ("Itaú", "https://www.youtube.com/@itaupersonnalite/videos", "Bancos e Corretoras"),
    ("XP", "https://www.youtube.com/@XP_Oficial/videos", "Bancos e Corretoras"),
    ("BTG Trader", "https://www.youtube.com/@BTGTrader", "Bancos e Corretoras"),
    ("Genial", "https://www.youtube.com/@genialinvestimentos", "Bancos e Corretoras"),
    ("Avenue", "https://www.youtube.com/@avenue_us/videos", "Bancos e Corretoras"),
    ("Schwab Network", "https://www.youtube.com/@SchwabNetwork", "Bancos e Corretoras"),
    ("Empiricus", "https://www.youtube.com/@empiricus/videos", "Casas de Análise e Mídia"),
    ("Kinea", "https://www.youtube.com/@KineaInvestimentos/videos", "Casas de Análise e Mídia"),
    ("Nord", "https://www.youtube.com/@nordinvestimentos/videos", "Casas de Análise e Mídia"),
    ("Suno", "https://www.youtube.com/@GrupoSuno/videos", "Casas de Análise e Mídia"),
    ("Ágora", "https://www.youtube.com/@AgoraInvestimentos/videos", "Casas de Análise e Mídia"),
    ("Market Makers", "https://www.youtube.com/@mmakers", "Casas de Análise e Mídia"),
    ("Stock Pickers", "https://www.youtube.com/@StockPickers", "Casas de Análise e Mídia"),
    ("AGF", "https://www.youtube.com/@agf-oficial/videos", "Casas de Análise e Mídia"),
    ("IBD", "https://www.youtube.com/@investorsbusinessdaily", "Casas de Análise e Mídia"),
    ("Barron`s", "https://www.youtube.com/@Barrons", "Casas de Análise e Mídia"),
    ("Money Week", "https://www.youtube.com/@MoneyWeekVideos", "Casas de Análise e Mídia"),
    ("Yahoo Finance", "https://www.youtube.com/@YahooFinance", "Casas de Análise e Mídia"),
    ("Financial Times", "https://www.youtube.com/@FinancialTimes", "Casas de Análise e Mídia"),
    ("Morningstar_Europe", "https://www.youtube.com/@Morningstar_Europe", "Casas de Análise e Mídia"),
    ("Financial Post", "https://www.youtube.com/@financialpost", "Casas de Análise e Mídia"),
    ("MarketWatch", "https://www.youtube.com/@MarketWatch", "Casas de Análise e Mídia"),
    ("Curioso Mercado", "https://www.youtube.com/@curiosomercado", "Traders e Criadores"),
    ("Os Traders", "https://www.youtube.com/@ostraderspodcast/featured", "Traders e Criadores"),
    ("Futurum Talks", "https://www.youtube.com/@FuturumTalks", "Traders e Criadores"),
    ("Fernando Ulrich", "https://www.youtube.com/@FernandoUlrichCanal", "Traders e Criadores"),
    ("Stormer", "https://www.youtube.com/@StormerOficial", "Traders e Criadores"),
    ("Roxo", "https://www.youtube.com/@luizfernandoroxo/videos", "Traders e Criadores"),
    ("Fausto Botelho", "https://www.youtube.com/@ChartsFB/videos", "Traders e Criadores"),
    ("Andre Machado Ogro", "https://www.youtube.com/@ogrowallst/videos", "Traders e Criadores"),
    ("Bruno Corano", "https://www.youtube.com/@BrunoCorano/videos", "Traders e Criadores"),
    ("Mestre dos Derivativos", "https://www.youtube.com/@mestredosderivativos/videos", "Traders e Criadores"),
    ("Laatus", "https://www.youtube.com/@Laatusoficial/videos", "Traders e Criadores"),
    ("Pepa Silveira", "https://www.youtube.com/@pepasilveira/videos", "Traders e Criadores"),
    ("Alexandre Cabral", "https://www.youtube.com/@Cabral7e10/videos", "Traders e Criadores"),
    ("Tiago Reis", "https://www.youtube.com/@TiagoReisYT/videos", "Traders e Criadores"),
    ("Arthurito Faria Lima", "https://www.youtube.com/@arthurito.farialima", "Traders e Criadores"),
    ("Black Rock", "https://www.youtube.com/@blackrock/videos", "Gestoras Globais e Cultura"),
    ("Vanguard", "https://www.youtube.com/@vanguard/videos", "Gestoras Globais e Cultura"),
    ("Fidelity", "https://www.youtube.com/@fidelityinvestments/videos", "Gestoras Globais e Cultura"),
    ("Goldman Sachs", "https://www.youtube.com/@GoldmanSachs", "Gestoras Globais e Cultura"),
    ("JP Morgan", "https://www.youtube.com/@jpmorgan/videos", "Gestoras Globais e Cultura"),
    ("PIMCO", "https://www.youtube.com/@pimco/videos", "Gestoras Globais e Cultura"),
    ("UBS", "https://www.youtube.com/@UBS/videos", "Gestoras Globais e Cultura"),
    ("Capital Group", "https://www.youtube.com/@CapitalGroup/videos", "Gestoras Globais e Cultura"),
    ("Amundi", "https://www.youtube.com/@Amundi/videos", "Gestoras Globais e Cultura"),
    ("BNY", "https://www.youtube.com/@bnyglobal/videos", "Gestoras Globais e Cultura"),
    ("T Rowe Price Group", "https://www.youtube.com/@TRowePriceGroup/videos", "Gestoras Globais e Cultura"),
    ("Franklin Templeton", "https://www.youtube.com/@FranklnTempletn/videos", "Gestoras Globais e Cultura"),
    ("Black Stone", "https://www.youtube.com/@blackstonegroup", "Gestoras Globais e Cultura"),
    ("Julius Baer Group", "https://www.youtube.com/@JuliusBaerGroup", "Gestoras Globais e Cultura"),
    ("Finaius", "https://www.youtube.com/@Finaius", "Gestoras Globais e Cultura"),
    ("David Rubenstein", "https://www.youtube.com/@DavidRubenstein/videos", "Talk Show e Think Tanks"),
    ("92NY", "https://www.youtube.com/@92ndStreetY", "Talk Show e Think Tanks"),
    ("Jimmy Kimel", "https://www.youtube.com/@JimmyKimmelLive/videos", "Talk Show e Think Tanks"),
    ("Mahattan Connection", "https://www.youtube.com/@manhattanconnection/videos", "Talk Show e Think Tanks"),
    ("EY", "https://www.youtube.com/@ernstyoung/videos", "Consultoria"),
    ("Deloitte", "https://www.youtube.com/@deloitte/videos", "Consultoria"),
    ("Deloitte Brasil", "https://www.youtube.com/@deloittebrasil/videos", "Consultoria"),
    ("KPMG", "https://www.youtube.com/user/deloittevideo/custom/videos", "Consultoria"),
    ("KPMG Brasil", "https://www.youtube.com/@KPMGBrasil/videos", "Consultoria"),
    ("Boston Consulting Group", "https://www.youtube.com/@TheBostonConsultingGroup/videos", "Consultoria"),
    ("McKinsey & Company", "https://www.youtube.com/@McKinsey/videos", "Consultoria"),
    ("McKinsey Brasil", "https://www.youtube.com/@mckinseycobr/videos", "Consultoria"),
    ("PwC", "https://www.youtube.com/@PwC/videos", "Consultoria"),
    ("PwC Brasil", "https://www.youtube.com/@PwCBrasil/videos", "Consultoria"),
    ("Accenture", "https://www.youtube.com/@Accenture/videos", "Consultoria"),
    ("Accenture Brasil", "https://www.youtube.com/@accenturebrasil/videos", "Consultoria"),
    ("Bain & Company", "https://www.youtube.com/@bainandcompany/videos", "Consultoria"),
    ("Oliver Wyman", "https://www.youtube.com/@oliverwyman/videos", "Consultoria"),
    ("Roland Berger", "https://www.youtube.com/@rolandberger/videos", "Consultoria"),
    ("Steve Eisman", "https://www.youtube.com/@RealEismanPlaybook/videos", "Analistas"),


    
]

    
    resultados = []
    for item in CANAIS_MAPEADOS:
        nome_exato = item[0]
        url = item[1]
        categoria = item[2] if len(item) > 2 else "Geral"
        
        print(f"Coletando dados de: {nome_exato} [{categoria}]...")
        nome, lista_videos, cat_retornada = coletar_videos(nome_exato, url, categoria, limite=10)
        resultados.append((nome, lista_videos, cat_retornada))
        
    gerar_html(resultados)
    print("\nArquivo atualizado gerado com sucesso: youtube_multicanais.html")
