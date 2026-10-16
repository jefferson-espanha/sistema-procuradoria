import os
from nicegui import app, ui

PORT = int(os.environ.get('PORT', 8080))

# Os arquivos PNG devem ficar na mesma pasta deste main.py.
app.add_static_files('/static', '.')

# Sistemas e módulos disponíveis no portal.
SISTEMAS = [
    {
        'nome': 'Decretos Municipais',
        'descricao': 'Consulta de decretos municipais de Francisco Morato.',
        'url': 'https://decretos-francisco-morato.onrender.com/',
        'logo': '/static/decretos.png',
        'cor': '#1e3a8a'
    },
    {
        'nome': 'IEG-M — Índice de Efetividade',
        'descricao': 'Acompanhamento do Índice de Efetividade da Gestão Municipal.',
        'url': 'https://www.iegm.app.br/',
        'logo': '/static/iegm.png',
        'cor': '#047857'
    },
    {
        'nome': 'Controle de Ponto',
        'descricao': 'Registro e controle eletrônico de ponto.',
        'url': 'https://registro-de-ponto-ddbl.onrender.com/ponto',
        'logo': '/static/ponto.png',
        'cor': '#b91c1c'
    },
    {
        'nome': 'Gestão Orçamentária',
        'descricao': 'Acompanhamento de fichas, dotações e saldo disponível.',
        'url': 'https://orcamento-procuradoria.onrender.com',
        'logo': '/static/orcamento.png',
        'cor': '#0284c7'
    },
    {
        'nome': 'Contratos e Aditivos',
        'descricao': 'Gestão de contratos, aditivos, vigências e fiscais.',
        'url': 'https://contratos-ifo5.onrender.com',
        'logo': '/static/contratos.png',
        'cor': '#0f766e'
    },
    {
        'nome': 'Contencioso',
        'descricao': 'Consulta e gerenciamento dos processos do contencioso.',
        'url': 'https://arquivo-contensioso.onrender.com/',
        'logo': '/static/contencioso.png',
        'cor': '#7c3aed'
    },
    {
        'nome': 'Ministério Público',
        'descricao': 'Consulta e gerenciamento dos procedimentos do Ministério Público.',
        'url': 'https://ministerio-publico.onrender.com',
        'logo': '/static/ministerio.png',
        'cor': '#4338ca'
    },
    {
        'nome': 'Arquivos em Geral',
        'descricao': 'Controle de caixas, pastas, envelopes e arquivos digitalizados.',
        'url': 'https://arquivos-geral.onrender.com/',
        'logo': '/static/arquivos_geral.png',
        'cor': '#0369a1'
    },
]


@ui.page('/')
def main_page():
    ui.colors(primary='#1e3a8a')

    # Cabeçalho do portal.
    with ui.header().classes('bg-blue-950 text-white p-4 flex justify-between items-center shadow-lg'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('balance', size='32px').classes('text-blue-300')
            ui.label('Procuradoria do Município').classes('text-2xl font-bold tracking-wide')
        ui.label('Portal de Sistemas Integrados').classes('text-sm text-blue-200 hidden sm:block')

    # Container principal.
    with ui.column().classes('w-full p-6 max-w-7xl mx-auto items-center'):
        with ui.column().classes('text-center my-6'):
            ui.label('Sistema Procuradoria').classes('text-3xl font-extrabold text-gray-800 mb-2')
            ui.label('Selecione abaixo o sistema que deseja acessar:').classes('text-base text-gray-600')

        # Grid responsivo dos sistemas.
        with ui.grid().classes('w-full grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 my-4 max-w-7xl'):
            for sistema in SISTEMAS:
                with ui.link(target=sistema['url'], new_tab=True).classes('no-underline w-full'):
                    with ui.card().classes(
                        'p-6 flex flex-col items-center justify-between shadow-md hover:shadow-2xl '
                        'transition-all duration-300 transform hover:-translate-y-2 rounded-xl '
                        'border border-gray-100 h-full w-full'
                    ):
                        with ui.column().classes('w-full h-44 items-center justify-center mb-2 overflow-hidden'):
                            ui.image(sistema['logo']).props('fit=contain').classes('w-full h-full')

                        ui.label(sistema['nome']).classes(
                            'text-base font-semibold text-gray-800 text-center mb-1'
                        )
                        ui.label(sistema['descricao']).classes(
                            'text-sm text-gray-500 text-center mb-6 flex-grow'
                        )
                        ui.button('Acessar Sistema ↗').classes(
                            'w-full text-white font-bold py-2 rounded-lg shadow-sm pointer-events-none'
                        ).style(f'background-color: {sistema["cor"]}')

    # Rodapé.
    with ui.footer().classes('bg-gray-100 text-gray-600 p-4 text-center text-sm border-t mt-12'):
        ui.label('Prefeitura Municipal de Francisco Morato — Procuradoria do Município © 2026')


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(host='0.0.0.0', port=PORT, reload=False)
