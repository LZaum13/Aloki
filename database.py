import sqlite3

class BancoDeDados:
    def __init__(self, db_name="alocacao_base.db"):
        self.db_name = db_name
        self.criar_tabelas()
        self.inserir_dados_iniciais()

    def conectar(self):
        return sqlite3.connect(self.db_name)

    def criar_tabelas(self):
        with self.conectar() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, login TEXT UNIQUE, senha TEXT, perfil TEXT)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS recursos (id INTEGER PRIMARY KEY, nome TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS salas (id INTEGER PRIMARY KEY, numero TEXT, capacidade INTEGER)''')
            c.execute('''CREATE TABLE IF NOT EXISTS disciplinas (id INTEGER PRIMARY KEY, nome TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS professores (id INTEGER PRIMARY KEY, nome TEXT)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS alunos (id INTEGER PRIMARY KEY, matricula TEXT UNIQUE, nome TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS matriculas (id_aluno INTEGER, id_turma INTEGER, PRIMARY KEY (id_aluno, id_turma))''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS sala_recursos (id_sala INTEGER, id_recurso INTEGER, PRIMARY KEY (id_sala, id_recurso))''')
            c.execute('''CREATE TABLE IF NOT EXISTS disciplina_recursos (id_disciplina INTEGER, id_recurso INTEGER, PRIMARY KEY (id_disciplina, id_recurso))''')
            c.execute('''CREATE TABLE IF NOT EXISTS turmas (id INTEGER PRIMARY KEY, id_disciplina INTEGER, alunos INTEGER, id_prof INTEGER)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS horarios (id INTEGER PRIMARY KEY, dia_semana TEXT, hora_inicio TEXT, hora_fim TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS prof_indisponibilidade (id_prof INTEGER, id_horario INTEGER, PRIMARY KEY (id_prof, id_horario))''')
            c.execute('''CREATE TABLE IF NOT EXISTS prof_preferencias (id_prof INTEGER, id_horario INTEGER, PRIMARY KEY (id_prof, id_horario))''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS grade (id INTEGER PRIMARY KEY AUTOINCREMENT, id_turma INTEGER, id_sala INTEGER, id_prof INTEGER, id_horario INTEGER)''')
            conn.commit()

    def inserir_dados_iniciais(self):
        with self.conectar() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM usuarios")
            if c.fetchone()[0] == 0:
                # Inserir utilizadores
                c.executemany("INSERT INTO usuarios (login, senha, perfil) VALUES (?, ?, ?)", [
                    ('coord', '123', 'Coordenador'),
                    ('prof', '123', 'Professor'),
                    ('aluno', '123', 'Aluno')
                ])
                
                # Blocos de horário extraídos da imagem
                periodos = [
                    ('07:30', '08:20'), ('08:20', '09:10'), ('09:10', '10:00'),
                    ('10:10', '11:00'), ('11:00', '11:50'),
                    ('13:30', '14:20'), ('14:20', '15:10'), ('15:10', '16:00'),
                    ('16:20', '17:10'), ('17:10', '18:00'),
                    ('18:30', '19:20'), ('19:20', '20:10'),
                    ('20:20', '21:10'), ('21:10', '22:00')
                ]
                
                dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira']
                
                horarios_db = []
                for dia in dias:
                    for inicio, fim in periodos:
                        horarios_db.append((dia, inicio, fim))
                        
                # Inserir os 70 horários gerados no banco
                c.executemany("INSERT INTO horarios (dia_semana, hora_inicio, hora_fim) VALUES (?, ?, ?)", horarios_db)
            
            conn.commit()