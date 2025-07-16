import internetarchive
import os

# ==============================================================================
# MÓDULO 1: UTILITÁRIOS DE INTERAÇÃO COM O INTERNET ARCHIVE (A Lógica)
# Responsabilidade: Buscar dados e baixar arquivos. Não interage com o usuário.
# ==============================================================================

def buscar_opcoes_album(artista, album, formato_audio='FLAC', limite_resultados=5):
    """
    Busca por álbuns no Internet Archive e retorna uma lista de opções com detalhes.
    """
    search_query = f'title:("{album}") AND creator:("{artista}") AND format:("{formato_audio}")'
    
    try:
        resultados_busca = internetarchive.search_items(
            search_query,
            params={'sort[]': 'downloads desc', 'rows': limite_resultados}
        )
    except Exception as e:
        print(f"    ⛔ Erro ao se conectar com o Internet Archive: {e}")
        return []

    opcoes_validas = []
    for item in resultados_busca:
        identifier = item['identifier']
        try:
            meta = internetarchive.get_item(identifier).metadata
            titulo_item = meta.get('title', album)
            
            todos_os_arquivos = internetarchive.get_files(identifier)
            audio_files = [f for f in todos_os_arquivos if f.name.lower().endswith(f".{formato_audio.lower()}")]
            
            if audio_files:
                opcoes_validas.append({
                    "identifier": identifier, "titulo": titulo_item,
                    "artista": artista, "faixas": len(audio_files),
                    "formato": formato_audio, "arquivos": audio_files
                })
        except Exception:
            # Ignora itens que não puderam ser analisados
            continue
            
    return opcoes_validas

def baixar_album_selecionado(opcao_escolhida):
    """
    Baixa os arquivos de uma opção de álbum escolhida para um diretório local.
    """
    nome_pasta_limpo = "".join(c for c in opcao_escolhida['titulo'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    album_dir = os.path.join("biblioteca_local", f"{opcao_escolhida['artista']} - {nome_pasta_limpo}")
    os.makedirs(album_dir, exist_ok=True)
    print(f"\n[🎧] Baixando {opcao_escolhida['faixas']} faixas para: {album_dir}")

    try:
        for audio in opcao_escolhida['arquivos']:
            dest_path = os.path.join(album_dir, os.path.basename(audio.name))
            if os.path.exists(dest_path):
                print(f"        ↳ Já existe: {os.path.basename(audio.name)}")
                continue
            print(f"        ↳ Baixando: {os.path.basename(audio.name)}")
            audio.download(dest_path)
        print(f"\n✔️ Download concluído! Álbum salvo em: {album_dir}")
        return True
    except Exception as e:
        print(f"\n⛔ Ocorreu um erro durante o download: {e}")
        return False

# ==============================================================================
# MÓDULO 2: INTERFACE COM O USUÁRIO (A Apresentação)
# Responsabilidade: Mostrar menus e obter input do usuário.
# ==============================================================================

def apresentar_e_obter_escolha(opcoes, nome_album):
    """
    Mostra as opções para o usuário e retorna a opção escolhida.
    Retorna None se o usuário pular.
    """
    print(f"\n[💿] Opções encontradas para '{nome_album}':")
    for i, opcao in enumerate(opcoes):
        print(f"    [{i + 1}] {opcao['titulo']} ({opcao['faixas']} músicas)")
    print("    [0] Pular (não baixar nenhum)")

    while True:
        try:
            escolha = int(input("\nDigite o número da sua escolha: "))
            if 0 <= escolha <= len(opcoes):
                break
            else:
                print("    ⛔ Opção inválida. Tente novamente.")
        except ValueError:
            print("    ⛔ Por favor, digite apenas um número.")
    
    if escolha == 0:
        print("    OK, pulando para o próximo álbum.")
        return None
    
    return opcoes[escolha - 1]

# ==============================================================================
# MÓDULO 3: APLICAÇÃO PRINCIPAL (O Orquestrador)
# Responsabilidade: Definir a lista de trabalho e orquestrar as chamadas.
# ==============================================================================

def processar_busca_de_album(artista, album, formato):
    """
    Orquestra o processo completo para um único álbum: busca, apresenta e baixa.
    """
    print(f"\n{'='*50}\n[🚀] Iniciando busca por: {album} — {artista}")
    
    opcoes = buscar_opcoes_album(artista, album, formato_audio=formato)
    
    if not opcoes:
        print(f"[😞] Nenhuma opção de download válida foi encontrada.")
        return
        
    album_escolhido = apresentar_e_obter_escolha(opcoes, album)
    
    if album_escolhido:
        baixar_album_selecionado(album_escolhido)

if __name__ == "__main__":
    # Garante que o diretório principal exista
    os.makedirs("biblioteca_local", exist_ok=True)

    # --- CONFIGURAÇÃO ---
    # Aqui é o único lugar que você precisa mexer para definir o que baixar.
    albuns_para_buscar = {
        "Eminem": ["The Marshall Mathers LP", "The Eminem Show"],
        "Daft Punk": ["Discovery", "Random Access Memories"],
        "Pink Floyd": ["The Dark Side of the Moon"]
    }
    FORMATO_AUDIO_DESEJADO = "MP3"
    # --- FIM DA CONFIGURAÇÃO ---
    
    # O loop principal agora apenas chama o orquestrador.
    for artista, albuns in albuns_para_buscar.items():
        for album in albuns:
            processar_busca_de_album(artista, album, formato=FORMATO_AUDIO_DESEJADO)

    print(f"\n{'='*50}\n[🎉] Processo finalizado!")