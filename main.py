import os
from nicegui import ui

PORT = int(os.environ.get('PORT', 8080))

# Definição dos Sistemas / Módulos do Container
SISTEMAS = [
    {
        'nome': 'Decretos Municipais',
        'descricao': 'Consulta de decretos municipais de Francisco Morato.',
        'url': 'https://decretos-francisco-morato.onrender.com/',
        'logo': 'decretos.png',
        'cor': '#1e3a8a'
    },
    {
        'nome': 'IEG-M — Índice de Efetividade',
        'descricao': 'Acompanhamento do Índice de Efetividade da Gestão Municipal.',
        'url': 'https://www.iegm.app.br/',
        'logo': 'iegm.png',
        'cor': '#047857'
    },
    {
        'nome': 'Controle de Ponto',
        'descricao': 'Registro e controle eletrônico de ponto',
        'url': 'https://registro-de-ponto-ddbl.onrender.com/ponto',
        'logo': 'ponto.png',
        'cor': '#b91c1c'
    }
]

@ui.page('/')
def main_page():
    ui.colors(primary='#1e3a8a')
    
    # Cabeçalho do Portal
    with ui.header().classes('bg-blue-950 text-white p-4 flex justify-between items-center shadow-lg'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('balance', size='32px').classes('text-blue-300')
            ui.label('Procuradoria do Município').classes('text-2xl font-bold tracking-wide')
        ui.label('Portal de Sistemas Integrados').classes('text-sm text-blue-200 hidden sm:block')

    # Container Principal
    with ui.column().classes('w-full p-6 max-w-7xl mx-auto items-center'):
        
        # Título de Boas-Vindas
        with ui.column().classes('text-center my-6'):
            ui.label('Sistema Procuradoria').classes('text-3xl font-extrabold text-gray-800 mb-2')
            ui.label('Selecione abaixo o sistema que deseja acessar:').classes('text-base text-gray-600')

        # Grid de Sistemas/Módulos
        with ui.grid(columns=3).classes('w-full gap-8 my-4 max-w-6xl'):
            for sistema in SISTEMAS:
                # ui.link envolve todo o card, garantindo a abertura do link em nova aba (target="_blank")
                with ui.link(target=sistema['url'], new_tab=True).classes('no-underline w-full'):
                    with ui.card().classes(
                        'p-6 flex flex-col items-center justify-between shadow-md hover:shadow-2xl '
                        'transition-all duration-300 transform hover:-translate-y-2 rounded-xl border border-gray-100 h-full w-full'
                    ):
                        # Imagem do Logo expandida para ocupar maior espaço
                        with ui.column().classes('h-36 flex items-center justify-center w-full mb-3 overflow-hidden'):
                            try:
                                ui.image(sistema['logo']).classes('max-h-32 max-w-full object-contain')
                            except Exception:
                                ui.icon('apps', size='48px').classes('text-gray-400')

                        # Nome do Sistema em tamanho menor para dar destaque ao logo
                        ui.label(sistema['nome']).classes('text-base font-semibold text-gray-800 text-center mb-1')
                        
                        # Descrição Curta
                        ui.label(sistema['descricao']).classes('text-sm text-gray-500 text-center mb-6 flex-grow')
                        
                        # Botão Visual de Acesso
                        ui.button(
                            'Acessar Sistema ↗'
                        ).classes('w-full text-white font-bold py-2 rounded-lg shadow-sm pointer-events-none').style(f'background-color: {sistema["cor"]}')

    # Rodapé
    with ui.footer().classes('bg-gray-100 text-gray-600 p-4 text-center text-sm border-t mt-12'):
        ui.label('Prefeitura Municipal de Francisco Morato — Procuradoria do Município © 2026')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(host='0.0.0.0', port=PORT, reload=False)
