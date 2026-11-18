import sqlite3  
import tkinter as tk
from tkinter import ttk, messagebox
from database import BancoDeDados
from motor import MotorAlocacao

class AppController:
    def __init__(self, root):
        self.root = root
        self.root.title("Aloki - Sistema Institucional") # Nome alterado aqui
        self.root.geometry("1000x700")
        
        self.db = BancoDeDados()
        self.motor = MotorAlocacao(self.db)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("TButton", font=("Arial", 10, "bold"))

        self.frame_atual = None
        self.abrir_login()

    def abrir_login(self):
        frame = tk.Frame(self.root, bg="#F3F4F6")
        
        caixa = tk.Frame(frame, bg="white", padx=40, pady=40, relief="groove", bd=2)
        caixa.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(caixa, text="Acesso ao Aloki", font=("Arial", 16, "bold"), bg="white").pack(pady=(0,20))
        
        tk.Label(caixa, text="Utilizador:", bg="white").pack(anchor="w")
        entry_usr = ttk.Entry(caixa, width=30)
        entry_usr.pack(pady=5)
        
        tk.Label(caixa, text="Palavra-passe:", bg="white").pack(anchor="w")
        entry_pwd = ttk.Entry(caixa, width=30, show="*")
        entry_pwd.pack(pady=5)
        
        def tentar_login(event=None):
            u, p = entry_usr.get(), entry_pwd.get()
            with self.db.conectar() as conn:
                c = conn.cursor()
                c.execute("SELECT id, perfil FROM usuarios WHERE login=? AND senha=?", (u, p))
                user = c.fetchone()
                if user:
                    self.root.unbind('<Return>') # Remove o atalho do Enter após logar
                    self.abrir_dashboard(user[1], user[0])
                else:
                    messagebox.showerror("Erro", "Credenciais inválidas.")

        tk.Button(caixa, text="Entrar", bg="#3B82F6", fg="white", font=("Arial", 10, "bold"), 
                  command=tentar_login, relief="flat", pady=5).pack(fill="x", pady=20)
        
        # Liga o Enter à função de login
        self.root.bind('<Return>', tentar_login)
        
        self.trocar_tela(frame)

    def abrir_dashboard(self, perfil, user_id):
        frame = tk.Frame(self.root, bg="#F3F4F6")
        
        sidebar = tk.Frame(frame, bg="#FFFFFF", width=220)
        sidebar.pack(side="left", fill="y")
        
        tk.Label(sidebar, text=f"Perfil:\n{perfil}", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#3B82F6").pack(pady=20)

        self.content = tk.Frame(frame, bg="#F3F4F6")
        self.content.pack(side="right", fill="both", expand=True)

        if perfil == "Coordenador":
            self.add_menu_btn(sidebar, "Configurar Horários", self.tela_horarios)
            self.add_menu_btn(sidebar, "Gerenciar Recursos", self.tela_recursos)
            self.add_menu_btn(sidebar, "Gerenciar Salas", self.tela_salas)
            self.add_menu_btn(sidebar, "Gerenciar Professores", self.tela_professores)
            self.add_menu_btn(sidebar, "Gerenciar Disciplinas", self.tela_disciplinas)
            self.add_menu_btn(sidebar, "Gerenciar Turmas", self.tela_turmas)
            self.add_menu_btn(sidebar, "Gerar Grade (Rascunho)", self.tela_gerar_rascunho)
            self.add_menu_btn(sidebar, "Consultar Grade Oficial", self.tela_consultar_oficial)
            self.add_menu_btn(sidebar, "Gerenciar Alunos", self.tela_alunos)
            self.add_menu_btn(sidebar, "Matrículas", self.tela_matriculas)
            
        elif perfil == "Professor":
            self.add_menu_btn(sidebar, "Minha Disponibilidade", lambda: self.tela_disponibilidade_prof(user_id))
            self.add_menu_btn(sidebar, "Consultar Minhas Aulas", lambda: self.tela_consultar_oficial(filtro_prof=user_id))
            
        elif perfil == "Aluno":
            self.add_menu_btn(sidebar, "Consultar Grade Geral", self.tela_consultar_oficial)

        self.add_menu_btn(sidebar, "Sair", self.abrir_login)
        self.trocar_tela(frame)
        
        tk.Label(self.content, text=f"Bem-vindo ao painel do {perfil}", font=("Arial", 16), bg="#F3F4F6").pack(pady=50)

    def add_menu_btn(self, parent, text, command):
        tk.Button(parent, text=text, command=command, bg="#FFFFFF", fg="#1F2937", 
                  relief="flat", anchor="w", padx=20, font=("Arial", 10)).pack(fill="x", pady=2)

    def limpar_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ==========================================
    # TELAS DO COORDENADOR
    # ==========================================
    def tela_horarios(self):
        self.limpar_content()
        tk.Label(self.content, text="Calendário Académico (Horários)", font=("Arial", 16, "bold"), bg="#F3F4F6").pack(pady=20)
        
        f = tk.Frame(self.content, bg="white", padx=20, pady=20)
        f.pack(fill="x", padx=20)
        
        tk.Label(f, text="Dia:", bg="white").grid(row=0, column=0)
        cb_dia = ttk.Combobox(f, values=["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"])
        cb_dia.grid(row=0, column=1, padx=5)
        
        tk.Label(f, text="Início (HH:MM):", bg="white").grid(row=0, column=2)
        ent_ini = ttk.Entry(f, width=10)
        ent_ini.grid(row=0, column=3, padx=5)
        
        tk.Label(f, text="Fim (HH:MM):", bg="white").grid(row=0, column=4)
        ent_fim = ttk.Entry(f, width=10)
        ent_fim.grid(row=0, column=5, padx=5)
        
        tv = ttk.Treeview(self.content, columns=("ID", "Dia", "Início", "Fim"), show="headings")
        for col in tv["columns"]: tv.heading(col, text=col)
        tv.pack(fill="both", expand=True, padx=20, pady=20)

        def recarregar():
            for i in tv.get_children(): tv.delete(i)
            with self.db.conectar() as c:
                for row in c.execute("SELECT * FROM horarios"): tv.insert("", "end", values=row)

        def salvar():
            d, i, fim = cb_dia.get(), ent_ini.get(), ent_fim.get()
            if d and i and fim:
                with self.db.conectar() as conn:
                    conn.execute("INSERT INTO horarios (dia_semana, hora_inicio, hora_fim) VALUES (?, ?, ?)", (d, i, fim))
                recarregar()
        
        tk.Button(f, text="Salvar", command=salvar, bg="#10B981", fg="white", relief="flat").grid(row=0, column=6, padx=15)
        recarregar()

    def tela_disciplinas(self):
        self.limpar_content()
        tk.Label(self.content, text="Gestão de Disciplinas e Seus Recursos", font=("Arial", 16, "bold"), bg="#F3F4F6").pack(pady=10)
        
        f = tk.Frame(self.content, bg="white", padx=20, pady=20)
        f.pack(fill="x", padx=20)
        
        tk.Label(f, text="Nome da Disciplina:", bg="white").grid(row=0, column=0, sticky="n", pady=5)
        ent_nome = ttk.Entry(f, width=30)
        ent_nome.grid(row=0, column=1, padx=5, sticky="n", pady=5)
        
        tk.Label(f, text="Recursos Exigidos (Use Ctrl para múltipla escolha):", bg="white").grid(row=0, column=2, sticky="n", pady=5)
        
        # Frame para a Listbox e Scrollbar
        f_list = tk.Frame(f)
        f_list.grid(row=0, column=3, padx=5)
        scroll = tk.Scrollbar(f_list)
        scroll.pack(side="right", fill="y")
        list_rec = tk.Listbox(f_list, selectmode=tk.MULTIPLE, yscrollcommand=scroll.set, height=4, exportselection=False)
        list_rec.pack(side="left")
        scroll.config(command=list_rec.yview)

        id_em_edicao = tk.IntVar(value=0)
        recursos_map = {} # Mapeia o índice da listbox para o ID do recurso no banco

        tv = ttk.Treeview(self.content, columns=("ID", "Nome"), show="headings")
        tv.heading("ID", text="ID"); tv.heading("Nome", text="Nome da Disciplina")
        tv.pack(fill="both", expand=True, padx=20, pady=10)

        def carregar_listbox():
            list_rec.delete(0, tk.END)
            recursos_map.clear()
            with self.db.conectar() as c:
                for idx, row in enumerate(c.execute("SELECT id, nome FROM recursos")):
                    list_rec.insert(tk.END, row[1])
                    recursos_map[idx] = row[0]

        def recarregar():
            for i in tv.get_children(): tv.delete(i)
            with self.db.conectar() as c:
                for row in c.execute("SELECT id, nome FROM disciplinas"): tv.insert("", "end", values=row)
            ent_nome.delete(0, tk.END)
            list_rec.selection_clear(0, tk.END)
            id_em_edicao.set(0)

        def salvar():
            n = ent_nome.get()
            selecionados_idx = list_rec.curselection()
            if not n: return
            
            with self.db.conectar() as conn:
                c = conn.cursor()
                if id_em_edicao.get() == 0:
                    c.execute("INSERT INTO disciplinas (nome) VALUES (?)", (n,))
                    id_disc = c.lastrowid
                else:
                    id_disc = id_em_edicao.get()
                    c.execute("UPDATE disciplinas SET nome=? WHERE id=?", (n, id_disc))
                    c.execute("DELETE FROM disciplina_recursos WHERE id_disciplina=?", (id_disc,))
                
                # Salvar a relação N:N
                for idx in selecionados_idx:
                    id_rec = recursos_map[idx]
                    c.execute("INSERT INTO disciplina_recursos (id_disciplina, id_recurso) VALUES (?, ?)", (id_disc, id_rec))
            recarregar()

        f_botoes = tk.Frame(f, bg="white")
        f_botoes.grid(row=0, column=4, padx=15, sticky="n", pady=5)
        tk.Button(f_botoes, text="Gravar", command=salvar, bg="#10B981", fg="white", relief="flat", width=8).pack(pady=2)

        carregar_listbox()
        recarregar()

    def tela_salas(self):
        self.limpar_content()
        tk.Label(self.content, text="Gestão de Salas e Recursos", font=("Arial", 16, "bold"), bg="#F3F4F6").pack(pady=10)
        
        f = tk.Frame(self.content, bg="white", padx=20, pady=20)
        f.pack(fill="x", padx=20)
        
        tk.Label(f, text="Número:", bg="white").grid(row=0, column=0, sticky="n", pady=5)
        ent_num = ttk.Entry(f, width=15)
        ent_num.grid(row=0, column=1, padx=5, sticky="n", pady=5)
        
        tk.Label(f, text="Capacidade:", bg="white").grid(row=0, column=2, sticky="n", pady=5)
        ent_cap = ttk.Entry(f, width=10)
        ent_cap.grid(row=0, column=3, padx=5, sticky="n", pady=5)
        
        tk.Label(f, text="Recursos Presentes:", bg="white").grid(row=0, column=4, sticky="n", pady=5)
        f_list = tk.Frame(f)
        f_list.grid(row=0, column=5, padx=5)
        scroll = tk.Scrollbar(f_list)
        scroll.pack(side="right", fill="y")
        list_rec = tk.Listbox(f_list, selectmode=tk.MULTIPLE, yscrollcommand=scroll.set, height=4, exportselection=False)
        list_rec.pack(side="left")
        scroll.config(command=list_rec.yview)

        id_em_edicao = tk.IntVar(value=0)
        recursos_map = {}

        tv = ttk.Treeview(self.content, columns=("ID", "Número", "Capacidade"), show="headings")
        for col in tv["columns"]: tv.heading(col, text=col)
        tv.pack(fill="both", expand=True, padx=20, pady=10)

        def carregar_listbox():
            list_rec.delete(0, tk.END)
            recursos_map.clear()
            with self.db.conectar() as c:
                for idx, row in enumerate(c.execute("SELECT id, nome FROM recursos")):
                    list_rec.insert(tk.END, row[1])
                    recursos_map[idx] = row[0]

        def recarregar():
            for i in tv.get_children(): tv.delete(i)
            with self.db.conectar() as c:
                for row in c.execute("SELECT * FROM salas"): tv.insert("", "end", values=row)
            ent_num.delete(0, tk.END); ent_cap.delete(0, tk.END); list_rec.selection_clear(0, tk.END)
            id_em_edicao.set(0)

        def salvar():
            try:
                n, cap = ent_num.get(), int(ent_cap.get())
                selecionados_idx = list_rec.curselection()
                with self.db.conectar() as conn:
                    c = conn.cursor()
                    if id_em_edicao.get() == 0:
                        c.execute("INSERT INTO salas (numero, capacidade) VALUES (?, ?)", (n, cap))
                        id_sala = c.lastrowid
                    else:
                        id_sala = id_em_edicao.get()
                        c.execute("UPDATE salas SET numero=?, capacidade=? WHERE id=?", (n, cap, id_sala))
                        c.execute("DELETE FROM sala_recursos WHERE id_sala=?", (id_sala,))
                    
                    for idx in selecionados_idx:
                        c.execute("INSERT INTO sala_recursos (id_sala, id_recurso) VALUES (?, ?)", (id_sala, recursos_map[idx]))
                recarregar()
            except ValueError:
                messagebox.showerror("Erro", "A capacidade deve ser numérica.")

        f_botoes = tk.Frame(f, bg="white")
        f_botoes.grid(row=0, column=6, padx=15, sticky="n", pady=5)
        tk.Button(f_botoes, text="Gravar", command=salvar, bg="#10B981", fg="white", relief="flat", width=8).pack(pady=2)

        carregar_listbox()
        recarregar()

    def tela_turmas(self):
        self.limpar_content()
        tk.Label(self.content, text="Gestão de Turmas", font=("Arial", 16, "bold"), bg="#F3F4F6").pack(pady=10)
        
        f = tk.Frame(self.content, bg="white", padx=20, pady=20)
        f.pack(fill="x", padx=20)
        
        tk.Label(f, text="Disciplina:", bg="white").grid(row=0, column=0)
        cb_disc = ttk.Combobox(f, width=20, state="readonly")
        cb_disc.grid(row=0, column=1, padx=5)
        
        tk.Label(f, text="Alunos:", bg="white").grid(row=0, column=2)
        ent_alu = ttk.Entry(f, width=10)
        ent_alu.grid(row=0, column=3, padx=5)
        
        tk.Label(f, text="Professor:", bg="white").grid(row=0, column=4)
        cb_prof = ttk.Combobox(f, width=20, state="readonly")
        cb_prof.grid(row=0, column=5, padx=5)
        
        id_em_edicao = tk.IntVar(value=0)
        mapa_disc = {}
        mapa_prof = {}
        
        tv = ttk.Treeview(self.content, columns=("ID", "Disciplina", "Qtd Alunos", "Professor"), show="headings")
        for col in tv["columns"]: tv.heading(col, text=col)
        tv.pack(fill="both", expand=True, padx=20, pady=10)

        def carregar_combos():
            with self.db.conectar() as c:
                discs = c.execute("SELECT id, nome FROM disciplinas").fetchall()
                mapa_disc.update({d[1]: d[0] for d in discs})
                cb_disc['values'] = list(mapa_disc.keys())
                
                profs = c.execute("SELECT id, nome FROM professores").fetchall()
                mapa_prof.update({p[1]: p[0] for p in profs})
                cb_prof['values'] = list(mapa_prof.keys())

        def recarregar():
            for i in tv.get_children(): tv.delete(i)
            with self.db.conectar() as c:
                query = """SELECT t.id, d.nome, t.alunos, p.nome 
                           FROM turmas t 
                           JOIN disciplinas d ON t.id_disciplina = d.id 
                           JOIN professores p ON t.id_prof = p.id"""
                for row in c.execute(query): tv.insert("", "end", values=row)
            cb_disc.set(''); ent_alu.delete(0, tk.END); cb_prof.set('')
            id_em_edicao.set(0)

        def salvar():
            try:
                id_d = mapa_disc[cb_disc.get()]
                id_p = mapa_prof[cb_prof.get()]
                a = int(ent_alu.get())
                with self.db.conectar() as conn:
                    if id_em_edicao.get() == 0:
                        conn.execute("INSERT INTO turmas (id_disciplina, alunos, id_prof) VALUES (?, ?, ?)", (id_d, a, id_p))
                    else:
                        conn.execute("UPDATE turmas SET id_disciplina=?, alunos=?, id_prof=? WHERE id=?", (id_d, a, id_p, id_em_edicao.get()))
                recarregar()
            except (ValueError, KeyError):
                messagebox.showerror("Erro", "Preencha todos os campos corretamente.")

        f_botoes = tk.Frame(f, bg="white")
        f_botoes.grid(row=0, column=6, padx=15)
        tk.Button(f_botoes, text="Gravar", command=salvar, bg="#10B981", fg="white", relief="flat", width=8).pack(pady=2)
        
        carregar_combos()
        recarregar()

    def tela_alunos(self):
        self.limpar_content()
        tk.Label(self.content, text="Gestão de Alunos", font=("Arial", 16, "bold"), bg="#F3F4F6").pack(pady=10)
        
        f = tk.Frame(self.content, bg="white", padx=20, pady=20)
        f.pack(fill="x", padx=20)
        
        tk.Label(f, text="Matrícula:", bg="white").grid(row=0, column=0)
        ent_mat = ttk.Entry(f, width=15)
        ent_mat.grid(row=0, column=1, padx=5)
        
        tk.Label(f, text="Nome do Aluno:", bg="white").grid(row=0, column=2)
        ent_nome = ttk.Entry(f, width=40)
        ent_nome.grid(row=0, column=3, padx=5)
        
        id_em_edicao = tk.IntVar(value=0)
        
        tv = ttk.Treeview(self.content, columns=("ID", "Matrícula", "Nome"), show="headings")
        tv.heading("ID", text="ID"); tv.heading("Matrícula", text="Matrícula"); tv.heading("Nome", text="Nome")
        tv.pack(fill="both", expand=True, padx=20, pady=10)

        def recarregar():
            for i in tv.get_children(): tv.delete(i)
            with self.db.conectar() as c:
                for row in c.execute("SELECT * FROM alunos"): tv.insert("", "end", values=row)
            ent_mat.delete(0, tk.END); ent_nome.delete(0, tk.END)
            id_em_edicao.set(0)

        def salvar():
            m, n = ent_mat.get(), ent_nome.get()
            if not m or not n: return
            try:
                with self.db.conectar() as conn:
                    if id_em_edicao.get() == 0:
                        conn.execute("INSERT INTO alunos (matricula, nome) VALUES (?, ?)", (m, n))
                    else:
                        conn.execute("UPDATE alunos SET matricula=?, nome=? WHERE id=?", (m, n, id_em_edicao.get()))
                recarregar()
            except Exception as e:
                messagebox.showerror("Erro", "Erro ao gravar. Verifique se a matrícula já existe.")

        def carregar_para_edicao():
            selecionado = tv.focus()
            if not selecionado: return
            valores = tv.item(selecionado, "values")
            id_em_edicao.set(int(valores[0]))
            ent_mat.delete(0, tk.END); ent_mat.insert(0, valores[1])
            ent_nome.delete(0, tk.END); ent_nome.insert(0, valores[2])

        def excluir():
            selecionado = tv.focus()
            if not selecionado: return
            id_aluno = int(tv.item(selecionado, "values")[0])
            with self.db.conectar() as conn:
                conn.execute("DELETE FROM matriculas WHERE id_aluno=?", (id_aluno,))
                conn.execute("DELETE FROM alunos WHERE id=?", (id_aluno,))
            recarregar()

        f_botoes = tk.Frame(f, bg="white")
        f_botoes.grid(row=0, column=4, padx=15)
        tk.Button(f_botoes, text="Gravar", command=salvar, bg="#10B981", fg="white", relief="flat", width=8).pack(side="left", padx=2)
        tk.Button(f_botoes, text="Editar", command=carregar_para_edicao, bg="#3B82F6", fg="white", relief="flat", width=8).pack(side="left", padx=2)
        tk.Button(f_botoes, text="Apagar", command=excluir, bg="#EF4444", fg="white", relief="flat", width=8).pack(side="left", padx=2)
        
        recarregar()

    def tela_matriculas(self):
        self.limpar_content()
        tk.Label(self.content, text="Matrículas (Vincular Aluno à Turma)", font=("Arial", 16, "bold"), bg="#F3F4F6").pack(pady=10)
        
        f = tk.Frame(self.content, bg="white", padx=20, pady=20)
        f.pack(fill="x", padx=20)
        
        tk.Label(f, text="Aluno:", bg="white").grid(row=0, column=0)
        cb_aluno = ttk.Combobox(f, width=30, state="readonly")
        cb_aluno.grid(row=0, column=1, padx=5)
        
        tk.Label(f, text="Turma (Disciplina):", bg="white").grid(row=0, column=2)
        cb_turma = ttk.Combobox(f, width=30, state="readonly")
        cb_turma.grid(row=0, column=3, padx=5)
        
        mapa_aluno = {}
        mapa_turma = {}
        
        tv = ttk.Treeview(self.content, columns=("ID Aluno", "Nome do Aluno", "Turma ID", "Disciplina"), show="headings")
        for col in tv["columns"]: tv.heading(col, text=col)
        tv.pack(fill="both", expand=True, padx=20, pady=10)

        def carregar_combos():
            with self.db.conectar() as c:
                alunos = c.execute("SELECT id, nome FROM alunos").fetchall()
                mapa_aluno.update({a[1]: a[0] for a in alunos})
                cb_aluno['values'] = list(mapa_aluno.keys())
                
                # Para exibir a turma de forma amigável, junta com a disciplina
                query = "SELECT t.id, d.nome FROM turmas t JOIN disciplinas d ON t.id_disciplina = d.id"
                turmas = c.execute(query).fetchall()
                mapa_turma.update({f"Turma {t[0]} - {t[1]}": t[0] for t in turmas})
                cb_turma['values'] = list(mapa_turma.keys())

        def recarregar():
            for i in tv.get_children(): tv.delete(i)
            with self.db.conectar() as c:
                query = """SELECT m.id_aluno, a.nome, m.id_turma, d.nome 
                           FROM matriculas m 
                           JOIN alunos a ON m.id_aluno = a.id
                           JOIN turmas t ON m.id_turma = t.id
                           JOIN disciplinas d ON t.id_disciplina = d.id"""
                for row in c.execute(query): tv.insert("", "end", values=row)

        def matricular():
            try:
                id_a = mapa_aluno[cb_aluno.get()]
                id_t = mapa_turma[cb_turma.get()]
                with self.db.conectar() as conn:
                    conn.execute("INSERT INTO matriculas (id_aluno, id_turma) VALUES (?, ?)", (id_a, id_t))
                recarregar()
            except KeyError:
                messagebox.showerror("Erro", "Selecione um aluno e uma turma válidos.")
            except sqlite3.IntegrityError:
                messagebox.showwarning("Aviso", "O aluno já está matriculado nesta turma.")

        def remover_matricula():
            selecionado = tv.focus()
            if not selecionado: return
            valores = tv.item(selecionado, "values")
            with self.db.conectar() as conn:
                conn.execute("DELETE FROM matriculas WHERE id_aluno=? AND id_turma=?", (valores[0], valores[2]))
            recarregar()

        f_botoes = tk.Frame(f, bg="white")
        f_botoes.grid(row=0, column=4, padx=15)
        tk.Button(f_botoes, text="Matricular", command=matricular, bg="#10B981", fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(f_botoes, text="Remover Matrícula", command=remover_matricula, bg="#EF4444", fg="white", relief="flat").pack(side="left", padx=5)
        
        carregar_combos()
        recarregar()

    def tela_recursos(self):
        self.limpar_content()
        import tkinter as tk # Garantir importações locais caso precise
        from tkinter import ttk
        
        tk.Label(self.content, text="Gestão de Recursos Físicos", font=("Arial", 16, "bold"), bg="#F3F4F6").pack(pady=10)
        
        f = tk.Frame(self.content, bg="white", padx=20, pady=20)
        f.pack(fill="x", padx=20)
        
        tk.Label(f, text="Nome do Recurso (Ex: Projetor, Laboratório):", bg="white").grid(row=0, column=0)
        ent_nome = ttk.Entry(f, width=40)
        ent_nome.grid(row=0, column=1, padx=5)
        
        tv = ttk.Treeview(self.content, columns=("ID", "Nome"), show="headings")
        tv.heading("ID", text="ID"); tv.heading("Nome", text="Nome")
        tv.pack(fill="both", expand=True, padx=20, pady=10)

        def recarregar():
            for i in tv.get_children(): tv.delete(i)
            with self.db.conectar() as c:
                for row in c.execute("SELECT id, nome FROM recursos"): tv.insert("", "end", values=row)
            ent_nome.delete(0, tk.END)

        def salvar():
            n = ent_nome.get()
            if n:
                with self.db.conectar() as conn:
                    conn.execute("INSERT INTO recursos (nome) VALUES (?)", (n,))
                recarregar()

        tk.Button(f, text="Adicionar Recurso", command=salvar, bg="#10B981", fg="white", relief="flat", padx=10).grid(row=0, column=2, padx=15)
        recarregar()

    def tela_professores(self):
        self.limpar_content()
        tk.Label(self.content, text="Gestão de Professores", font=("Arial", 16, "bold"), bg="#F3F4F6").pack(pady=10)
        
        f = tk.Frame(self.content, bg="white", padx=20, pady=20)
        f.pack(fill="x", padx=20)
        
        tk.Label(f, text="Nome:", bg="white").grid(row=0, column=0)
        ent_nome = ttk.Entry(f, width=40)
        ent_nome.grid(row=0, column=1, padx=5)
        
        id_em_edicao = tk.IntVar(value=0)
        
        tv = ttk.Treeview(self.content, columns=("ID", "Nome"), show="headings")
        tv.heading("ID", text="ID"); tv.heading("Nome", text="Nome")
        tv.pack(fill="both", expand=True, padx=20, pady=10)

        def recarregar():
            for i in tv.get_children(): tv.delete(i)
            with self.db.conectar() as c:
                for row in c.execute("SELECT id, nome FROM professores"): tv.insert("", "end", values=row)
            ent_nome.delete(0, tk.END)
            id_em_edicao.set(0)

        def salvar():
            n = ent_nome.get()
            if not n: return
            with self.db.conectar() as conn:
                if id_em_edicao.get() == 0:
                    conn.execute("INSERT INTO professores (nome) VALUES (?)", (n,))
                else:
                    conn.execute("UPDATE professores SET nome=? WHERE id=?", (n, id_em_edicao.get()))
            recarregar()

        def carregar_para_edicao():
            selecionado = tv.focus()
            if not selecionado: return
            valores = tv.item(selecionado, "values")
            id_em_edicao.set(int(valores[0]))
            ent_nome.delete(0, tk.END)
            ent_nome.insert(0, valores[1])

        def excluir():
            selecionado = tv.focus()
            if not selecionado: return
            id_prof = int(tv.item(selecionado, "values")[0])
            
            with self.db.conectar() as conn:
                uso = conn.execute("SELECT 1 FROM grade WHERE id_prof=?", (id_prof,)).fetchone()
                if uso:
                    messagebox.showerror("Erro", "Não é possível excluir um professor com aulas atribuídas na grade.")
                    return
                if messagebox.askyesno("Confirmar", "Deseja excluir este professor?"):
                    conn.execute("DELETE FROM professores WHERE id=?", (id_prof,))
            recarregar()

        f_botoes = tk.Frame(f, bg="white")
        f_botoes.grid(row=0, column=2, padx=15)
        
        tk.Button(f_botoes, text="Gravar", command=salvar, bg="#10B981", fg="white", relief="flat", width=8).pack(side="left", padx=2)
        tk.Button(f_botoes, text="Editar", command=carregar_para_edicao, bg="#3B82F6", fg="white", relief="flat", width=8).pack(side="left", padx=2)
        tk.Button(f_botoes, text="Apagar", command=excluir, bg="#EF4444", fg="white", relief="flat", width=8).pack(side="left", padx=2)
        
        recarregar()

    def tela_gerar_rascunho(self):
        self.limpar_content()
        tk.Label(self.content, text="Motor de Alocação e Ajuste Manual", font=("Arial", 16, "bold"), bg="#F3F4F6").pack(pady=10)
        
        lbl_qualidade = tk.Label(self.content, text="Qualidade: --%", font=("Arial", 12, "bold"), fg="#10B981", bg="#F3F4F6")
        lbl_qualidade.pack(pady=5)
        
        btn_frame = tk.Frame(self.content, bg="#F3F4F6")
        btn_frame.pack(pady=10)
        
        tv = ttk.Treeview(self.content, columns=("Turma", "Sala", "Prof ID", "Horário ID", "Índice"), show="headings")
        tv.heading("Turma", text="Turma ID"); tv.heading("Sala", text="Sala ID")
        tv.heading("Prof ID", text="Prof ID"); tv.heading("Horário ID", text="Horário ID")
        tv["displaycolumns"] = ("Turma", "Sala", "Prof ID", "Horário ID") 
        tv.pack(fill="both", expand=True, padx=20, pady=10)

        def recarregar_tabela_rascunho():
            for i in tv.get_children(): tv.delete(i)
            for idx, aloc in enumerate(self.motor.grade_rascunho):
                tv.insert("", "end", values=(aloc["id_turma"], aloc["id_sala"], aloc["id_prof"], aloc["id_horario"], idx))

        def processar_algoritmo():
            sucesso, msg = self.motor.gerar_grade_rascunho()
            if sucesso:
                lbl_qualidade.config(text=f"Qualidade: {self.motor.score_qualidade}% das preferências atendidas")
                recarregar_tabela_rascunho()
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showwarning("Aviso", msg)

        def ajustar_manualmente():
            selecionado = tv.focus()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione uma linha para ajustar.")
                return
            
            valores = tv.item(selecionado, "values")
            idx_memoria = int(valores[4])
            aloc_atual = self.motor.grade_rascunho[idx_memoria]

            modal = tk.Toplevel(self.root)
            modal.title("Ajuste Manual")
            modal.geometry("300x250")
            modal.configure(bg="white")
            
            tk.Label(modal, text=f"Turma ID: {aloc_atual['id_turma']}", bg="white", font=("Arial", 10, "bold")).pack(pady=10)
            tk.Label(modal, text="Novo Horário ID:", bg="white").pack()
            ent_h = ttk.Entry(modal); ent_h.insert(0, str(aloc_atual['id_horario'])); ent_h.pack(pady=5)
            tk.Label(modal, text="Nova Sala ID:", bg="white").pack()
            ent_s = ttk.Entry(modal); ent_s.insert(0, str(aloc_atual['id_sala'])); ent_s.pack(pady=5)

            def confirmar_ajuste():
                try:
                    nh, ns = int(ent_h.get()), int(ent_s.get())
                    conflito = self.motor._checar_conflito_memoria(nh, ns, aloc_atual['id_prof'])
                    if conflito and (nh != aloc_atual['id_horario'] or ns != aloc_atual['id_sala']):
                        messagebox.showerror("Erro", "Conflito! Sala ou Professor ocupados neste horário.")
                        return
                        
                    self.motor.grade_rascunho[idx_memoria]["id_horario"] = nh
                    self.motor.grade_rascunho[idx_memoria]["id_sala"] = ns
                    recarregar_tabela_rascunho()
                    
                    # Opcional: recalcular score aqui seria ótimo, mas para manter simples só mostramos sucesso
                    lbl_qualidade.config(text="Qualidade: Recalculando após ajuste manual...")
                    modal.destroy()
                except ValueError:
                    messagebox.showerror("Erro", "IDs devem ser inteiros.")

            tk.Button(modal, text="Confirmar Alteração", command=confirmar_ajuste, bg="#F59E0B", fg="white", relief="flat").pack(pady=15)

        def confirmar_e_salvar():
            sucesso, msg = self.motor.salvar_grade_definitiva()
            if sucesso:
                messagebox.showinfo("Gravação Concluída", msg)
                self.tela_consultar_oficial()
            else:
                messagebox.showerror("Erro", msg)

        tk.Button(btn_frame, text="1. Gerar Rascunho", command=processar_algoritmo, bg="#3B82F6", fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(btn_frame, text="2. Ajustar Selecionada", command=ajustar_manualmente, bg="#F59E0B", fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(btn_frame, text="3. Validar e Gravar", command=confirmar_e_salvar, bg="#10B981", fg="white", relief="flat").pack(side="left", padx=5)

    # ==========================================
    # TELAS DO PROFESSOR
    # ==========================================
    def tela_disponibilidade_prof(self, prof_id):
        self.limpar_content()
        tk.Label(self.content, text="Minhas Preferências de Horário", font=("Arial", 16, "bold"), bg="#F3F4F6").pack(pady=10)
        
        tv = ttk.Treeview(self.content, columns=("ID", "Dia", "Período", "Status"), show="headings")
        tv.heading("ID", text="ID"); tv.heading("Dia", text="Dia"); tv.heading("Período", text="Período"); tv.heading("Status", text="Status")
        tv.pack(fill="both", expand=True, padx=20, pady=10)

        def recarregar():
            for i in tv.get_children(): tv.delete(i)
            with self.db.conectar() as c:
                horarios = c.execute("SELECT id, dia_semana, hora_inicio, hora_fim FROM horarios").fetchall()
                bloqueados = [r[0] for r in c.execute("SELECT id_horario FROM prof_indisponibilidade WHERE id_prof=?", (prof_id,)).fetchall()]
                preferidos = [r[0] for r in c.execute("SELECT id_horario FROM prof_preferencias WHERE id_prof=?", (prof_id,)).fetchall()]
                
                for h in horarios:
                    if h[0] in bloqueados: status = "Bloqueado (Indisponível)"
                    elif h[0] in preferidos: status = "⭐ Preferência"
                    else: status = "Livre (Neutro)"
                    tv.insert("", "end", values=(h[0], h[1], f"{h[2]} às {h[3]}", status))

        def ciclar_status():
            selecionado = tv.focus()
            if not selecionado: return
            id_horario = int(tv.item(selecionado, "values")[0])
            status_atual = tv.item(selecionado, "values")[3]
            
            with self.db.conectar() as c:
                # Remove de ambas primeiro para limpar o estado
                c.execute("DELETE FROM prof_indisponibilidade WHERE id_prof=? AND id_horario=?", (prof_id, id_horario))
                c.execute("DELETE FROM prof_preferencias WHERE id_prof=? AND id_horario=?", (prof_id, id_horario))
                
                if "Livre" in status_atual:
                    # De Livre -> Bloqueado
                    c.execute("INSERT INTO prof_indisponibilidade (id_prof, id_horario) VALUES (?, ?)", (prof_id, id_horario))
                elif "Bloqueado" in status_atual:
                    # De Bloqueado -> Preferência
                    c.execute("INSERT INTO prof_preferencias (id_prof, id_horario) VALUES (?, ?)", (prof_id, id_horario))
                # Se for Preferência, não faz INSERT nenhum, voltando naturalmente a "Livre"
            recarregar()

        tk.Button(self.content, text="Ciclar Status (Livre ➔ Bloqueado ➔ Preferência)", command=ciclar_status, bg="#3B82F6", fg="white", relief="flat", pady=10, padx=20).pack(pady=10)
        recarregar()

    # ==========================================
    # CONSULTA OFICIAL (TODOS)
    # ==========================================
    def tela_consultar_oficial(self, filtro_prof=None):
        self.limpar_content()
        tk.Label(self.content, text="Grade Horária Oficial", font=("Arial", 16, "bold"), bg="#F3F4F6").pack(pady=20)
        
        tv = ttk.Treeview(self.content, columns=("Dia", "Período", "Turma", "Sala", "Professor"), show="headings")
        for col in tv["columns"]: tv.heading(col, text=col)
        tv.pack(fill="both", expand=True, padx=20, pady=20)

        query = """
            SELECT h.dia_semana, h.hora_inicio || ' às ' || h.hora_fim, t.codigo, s.numero, p.nome 
            FROM grade g
            JOIN turmas t ON g.id_turma = t.id
            JOIN salas s ON g.id_sala = s.id
            JOIN professores p ON g.id_prof = p.id
            JOIN horarios h ON g.id_horario = h.id
        """
        params = ()
        if filtro_prof:
            query += " WHERE p.id = ?"
            params = (filtro_prof,)
            
        with self.db.conectar() as c:
            for row in c.execute(query, params):
                tv.insert("", "end", values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppController(root)
    root.mainloop()