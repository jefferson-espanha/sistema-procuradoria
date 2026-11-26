import hashlib
import os
import secrets
import psycopg2
from psycopg2.extras import RealDictCursor
from nicegui import app, ui

app.add_static_files('/static', '.')

PORT = int(os.getenv('PORT', '8080'))

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://neondb_owner:npg_0hKgv8FNPuoC@ep-bold-frog-bc570g4q-pooler.c-16.us-east-1.aws.neon.tech/neondb?sslmode=require'
)

ADMIN_USER = 'jefferson.espanha'
ADMIN_PASS = 'odio'


def hash_senha(senha: str, salt: str | None = None) -> str:
    if not salt:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt.encode('utf-8'), 100_000)
    return f'{salt}${dk.hex()}'


def verificar_senha(senha: str, armazenado: str) -> bool:
    try:
        salt, dk_h = armazenado.split('$', 1)
        dk = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt.encode('utf-8'), 100_000)
        return secrets.compare_digest(dk.h(), dk_h)
    cept ception:
        return False


def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def inicializar_usuarios():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.ecute("""
            CREATE TABLE IF NOT ISTS usuarios_procuradoria (
                id SERIAL PRIMARY KEY,
                usuario VARCHAR(100) UNIQUE NOT NULL,
                nome_completo VARCHAR(180) DEFAULT '',
                senha_hash TT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                ativo BOOLEAN DEFAULT TRUE,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cur.ecute(
            'SELECT id, senha_hash FROM usuarios_procuradoria WHERE usuario = %s;',
            (ADMIN_USER,)
        )
        admin_row = cur.fetchone()
        if not admin_row:
            cur.ecute("""
                INSERT INTO usuarios_procuradoria (usuario, nome_completo, senha_hash, is_admin, ativo)
                VALUES (%s, %s, %s, TRUE, TRUE);
            """, (ADMIN_USER, 'Administrador do Sistema', hash_senha(ADMIN_PASS)))

        conn.commit()
        cur.close()
        conn.close()
    cept ception as e:
        print(f'Erro ao inicializar tabela de usuários: {e}')


inicializar_usuarios()


def autenticar_usuario(usuario: str, senha: str) -> dict | None:
    u = (usuario or '').strip().lower()
    s = senha or ''
    if not u or not s:
        return None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.ecute("""
            SELECT id, usuario, nome_completo, senha_hash, is_admin, ativo
            FROM usuarios_procuradoria
            WHERE LOWER(usuario) = %s;
        """, (u,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row and row.get('ativo') and verificar_senha(s, row['senha_hash']):
            return dict(row)
        return None
    cept Exception as e:
        print(f'Erro ao autenticar usuário: {e}')
        return None


def alterar_senha_usuario(
    usuario: str,
    senha_atual: str,
    nova_senha: str,
    confirmar_senha: str,
) -> tuple[bool, str]:
    u = (usuario or '').strip().lower()
    atual = senha_atual or ''
    nova = nova_senha or ''
    conf = confirmar_senha or ''

    if not u or not atual:
        return False, 'Informe seu usuário e a senha atual.'
    if len(nova) < 4:
        return False, 'A nova senha deve ter pelo menos 4 caracteres.'
    if nova != conf:
        return False, 'A nova senha e a confirmação não coincidem.'
    if nova == atual:
        return False, 'A nova senha deve ser diferente da senha atual.'

    user_ok = autenticar_usuario(u, atual)
    if not user_ok:
        return False, 'Usuário ou senha atual inválidos.'

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'UPDATE usuarios_procuradoria SET senha_hash = %s WHERE id = %s;',
            (hash_senha(nova), user_ok['id'])
        )
        conn.commit()
        cur.close()
        conn.close()
        return True, 'Senha alterada com sucesso!'
    except Exception as e:
        return False, f'Erro ao alterar senha: {e}'


def cadastrar_usuario_via_admin(
    admin_user: str,
    admin_pass: str,
    novo_usuario: str,
    novo_nome: str,
    nova_senha: str,
    tornar_admin: bool = False,
) -> tuple[bool, str]:
    if (admin_user or '').strip().lower() != ADMIN_USER or (admin_pass or '') != ADMIN_PASS:
        return False, 'Acesso negado: apenas o administrador jefferson.espanha pode cadastrar usuários.'

    u_novo = (novo_usuario or '').strip().lower()
    nome_novo = (novo_nome or '').strip()
    s_nova = nova_senha or ''

    if len(u_novo) < 3:
        return False, 'Informe um nome de usuário com pelo menos 3 caracteres.'
    if len(s_nova) < 4:
        return False, 'Informe uma senha com pelo menos 4 caracteres.'

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT id FROM usuarios_procuradoria WHERE LOWER(usuario) = %s;', (u_novo,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return False, f'O usuário "{u_novo}" já está cadastrado.'

        cur.execute("""
            INSERT INTO usuarios_procuradoria (usuario, nome_completo, senha_hash, is_admin, ativo)
            VALUES (%s, %s, %s, %s, TRUE);
        """, (u_novo, nome_novo, hash_senha(s_nova), bool(tornar_admin)))

        conn.commit()
        cur.close()
        conn.close()
        return True, f'Usuário "{u_novo}" cadastrado com sucesso!'
    except Exception as e:
        return False, f'Erro ao cadastrar usuário: {e}'


@ui.page('/login')
def login_page():
    ui.colors(primary='#1e3a8a')

    usuario_logado = app.storage.user.get('usuario') or ''

    with ui.header().classes('bg-blue-950 text-white p-4 flex justify-between items-center shadow-lg'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('balance', size='30px').classes('text-blue-300')
            ui.label('Procuradoria do Município').classes('text-xl font-bold tracking-wide')
        ui.label('Acesso ao Sistema').classes('text-sm text-blue-200 hidden sm:block')

    with ui.column().classes('w-full min-h-[82vh] items-center justify-center p-4 bg-gray-50'):
        with ui.card().classes('w-full max-w-md p-7 rounded-2xl shadow-xl border border-gray-100 bg-white'):
            # Logo centralizado
            with ui.column().classes('w-full items-center justify-center mb-4'):
                ui.image('/static/procuradoria.png').props('fit=contain').classes('w-36 h-28 object-contain')
                ui.label('Portal da Procuradoria').classes('text-xl font-extrabold text-blue-950 mt-2')
                ui.label('Entre com seu usuário e senha').classes('text-xs text-gray-500')

            with ui.tabs().classes('w-full mb-4') as tabs:
                tab_entrar = ui.tab('Entrar', icon='login')
                tab_senha = ui.tab('Alterar Senha', icon='lock_reset')
                tab_admin = ui.tab('Cadastrar Usuário', icon='admin_panel_settings')

            with ui.tab_panels(tabs, value=tab_entrar).classes('w-full p-0'):
                # Aba Entrar
                with ui.tab_panel(tab_entrar).classes('p-0 flex flex-col gap-3'):
                    inp_user = ui.input(
                        label='Usuário',
                        value=usuario_logado,
                        placeholder='Ex: chuck norris'
                    ).classes('w-full').props('outlined dense')
                    inp_pass = ui.input(
                        label='Senha',
                        password=True,
                        password_toggle_button=True
                    ).classes('w-full').props('outlined dense')

                    def fazer_login():
                        user_ok = autenticar_usuario(inp_user.value, inp_pass.value)
                        if not user_ok:
                            ui.notify('Usuário ou senha inválidos.', type='negative')
                            return
                        app.storage.user['usuario'] = user_ok['usuario']
                        app.storage.user['nome'] = user_ok.get('nome_completo') or user_ok['usuario']
                        app.storage.user['is_admin'] = bool(user_ok.get('is_admin'))
                        ui.notify(f"potência, {app.storage.user['usuario']}!", type='positive')
                        ui.navigate.to('/')

                    inp_pass.on('keydown.enter', lambda _: fazer_login())

                    ui.button('Entrar', icon='login', on_click=fazer_login).classes(
                        'w-full bg-blue-900 text-white font-bold py-2.5 rounded-lg mt-2 shadow-md'
                    )

                # Aba Alterar Senha (livre para qualquer usuário com sua senha atual)
                with ui.tab_panel(tab_senha).classes('p-0 flex flex-col gap-3'):
                    ui.label(
                        'Confirme sua senha atual e altere.'
                    ).classes('text-xs text-blue-900 bg-blue-50 p-2.5 rounded-lg border border-blue-200')

                    alt_user = ui.input(
                        label='Usuário',
                        value=usuario_logado,
                        placeholder='Seu usuário'
                    ).classes('w-full').props('outlined dense')

                    alt_atual = ui.input(
                        label='Senha Atual',
                        password=True,
                        password_toggle_button=True
                    ).classes('w-full').props('outlined dense')

                    alt_nova = ui.input(
                        label='Nova Senha',
                        password=True,
                        password_toggle_button=True
                    ).classes('w-full').props('outlined dense')

                    alt_conf = ui.input(
                        label='Confirmar Nova Senha',
                        password=True,
                        password_toggle_button=True
                    ).classes('w-full').props('outlined dense')

                    def salvar_nova_senha():
                        ok, msg = alterar_senha_usuario(
                            alt_user.value,
                            alt_atual.value,
                            alt_nova.value,
                            alt_conf.value,
                        )
                        if ok:
                            ui.notify(msg, type='positive')
                            alt_atual.value = ''
                            alt_nova.value = ''
                            alt_conf.value = ''
                            tabs.set_value(tab_entrar)
                        else:
                            ui.notify(msg, type='negative')

                    ui.button(
                        'Alterar Senha',
                        icon='check_circle',
                        on_click=salvar_nova_senha
                    ).classes('w-full bg-blue-900 text-white font-bold py-2.5 rounded-lg mt-1 shadow-md')

                # Aba Cadastrar Usuário (restrita ao admin jefferson.espanha)
                with ui.tab_panel(tab_admin).classes('p-0 flex flex-col gap-3'):
                    ui.label(
                        'Restrito ao administrador "jefferson.espanha".'
                    ).classes('text-xs font-semibold text-amber-800 bg-amber-50 p-2.5 rounded-lg border border-amber-200')

                    adm_user = ui.input(
                        label='Usuário Administrador',
                        placeholder='jefferson.espanha'
                    ).classes('w-full').props('outlined dense')

                    adm_pass = ui.input(
                        label='Senha do Administrador',
                        password=True,
                        password_toggle_button=True
                    ).classes('w-full').props('outlined dense')

                    ui.separator().classes('my-1')

                    novo_u = ui.input(
                        label='Novo Usuário',
                        placeholder='Ex: maria.silva'
                    ).classes('w-full').props('outlined dense')

                    novo_n = ui.input(
                        label='Nome Completo (opcional)',
                        placeholder='Ex: Maria Silva'
                    ).classes('w-full').props('outlined dense')

                    novo_s = ui.input(
                        label='Senha do Novo Usuário',
                        password=True,
                        password_toggle_button=True
                    ).classes('w-full').props('outlined dense')

                    novo_is_adm = ui.checkbox('Conceder permissão de administrador')

                    def criar_usuario():
                        ok, msg = cadastrar_usuario_via_admin(
                            adm_user.value,
                            adm_pass.value,
                            novo_u.value,
                            novo_n.value,
                            novo_s.value,
                            novo_is_adm.value,
                        )
                        if ok:
                            ui.notify(msg, type='positive')
                            novo_u.value = ''
                            novo_n.value = ''
                            novo_s.value = ''
                            novo_is_adm.value = False
                        else:
                            ui.notify(msg, type='negative')

                    ui.button(
                        'Cadastrar Usuário',
                        icon='person_add',
                        on_click=criar_usuario
                    ).classes('w-full bg-blue-950 text-white font-bold py-2.5 rounded-lg mt-1 shadow-md')

    with ui.footer().classes('bg-gray-100 text-gray-600 p-3 text-center text-xs border-t'):
        ui.label('Prefeitura Municipal de Francisco Morato — Procuradoria do Município © 2026')


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        host='0.0.0.0',
        port=PORT,
        reload=False,
        storage_secret=os.getenv('STORAGE_SECRET', 'procuradoria-francisco-morato-secret-2026')
    )
