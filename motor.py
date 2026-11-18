class MotorAlocacao:
    def __init__(self, db):
        self.db = db
        self.grade_rascunho = [] 
        self.score_qualidade = 0.0 # Nova métrica de otimização

    def gerar_grade_rascunho(self):
        self.grade_rascunho.clear()
        self.score_qualidade = 0.0
        
        with self.db.conectar() as conn:
            c = conn.cursor()
            c.execute("SELECT id, id_disciplina, alunos, id_prof FROM turmas ORDER BY alunos DESC")
            turmas = c.fetchall()
            
            c.execute("SELECT id, capacidade FROM salas ORDER BY capacidade ASC")
            salas = c.fetchall()
            
            c.execute("SELECT id FROM horarios")
            horarios = [h[0] for h in c.fetchall()]

            c.execute("SELECT id_prof, id_horario FROM prof_indisponibilidade")
            indisp = set(c.fetchall())
            c.execute("SELECT id_prof, id_horario FROM prof_preferencias")
            prefs = set(c.fetchall())

            # Mapeamento N:N de Recursos
            c.execute("SELECT id_sala, id_recurso FROM sala_recursos")
            recursos_das_salas = {}
            for s, r in c.fetchall():
                recursos_das_salas.setdefault(s, set()).add(r)
                
            c.execute("SELECT id_disciplina, id_recurso FROM disciplina_recursos")
            recursos_das_disciplinas = {}
            for d, r in c.fetchall():
                recursos_das_disciplinas.setdefault(d, set()).add(r)

            if not turmas or not salas or not horarios:
                return False, "Dados insuficientes para gerar a grade."

            score_total = 0
            alocacoes_feitas = 0

            for turma_id, disc_id, alunos, prof_id in turmas:
                alocado = False
                recursos_necessarios = recursos_das_disciplinas.get(disc_id, set())
                horarios_ordenados = sorted(horarios, key=lambda h: 0 if (prof_id, h) in prefs else 1)

                for horario_id in horarios_ordenados:
                    if (prof_id, horario_id) in indisp:
                        continue
                        
                    for sala_id, capacidade in salas:
                        recursos_da_sala = recursos_das_salas.get(sala_id, set())
                        
                        # VERIFICAÇÃO DUPLA: Capacidade E Recursos (A disciplina é um subconjunto da sala?)
                        if capacidade >= alunos and recursos_necessarios.issubset(recursos_da_sala):
                            if not self._checar_conflito_memoria(horario_id, sala_id, prof_id):
                                self.grade_rascunho.append({
                                    "id_turma": turma_id, "id_sala": sala_id, 
                                    "id_prof": prof_id, "id_horario": horario_id
                                })
                                if (prof_id, horario_id) in prefs:
                                    score_total += 1
                                alocacoes_feitas += 1
                                alocado = True
                                break
                    if alocado:
                        break
                
                if not alocado:
                    self.grade_rascunho.clear()
                    return False, f"Falha ao alocar a turma ID {turma_id}. Verifique se há salas com os recursos e capacidade exigidos."
            
            if alocacoes_feitas > 0:
                self.score_qualidade = round((score_total / alocacoes_feitas) * 100, 2)
            
            return True, f"Rascunho gerado! Qualidade da Grade: {self.score_qualidade}%"

    def _checar_conflito_memoria(self, id_horario, id_sala, id_prof):
        for alocacao in self.grade_rascunho:
            if alocacao["id_horario"] == id_horario:
                if alocacao["id_sala"] == id_sala or alocacao["id_prof"] == id_prof:
                    return True
        return False

    def salvar_grade_definitiva(self):
        if not self.grade_rascunho:
            return False, "Não há grade para salvar."
        with self.db.conectar() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM grade")
            for aloc in self.grade_rascunho:
                c.execute('''INSERT INTO grade (id_turma, id_sala, id_prof, id_horario) VALUES (?, ?, ?, ?)''', 
                          (aloc["id_turma"], aloc["id_sala"], aloc["id_prof"], aloc["id_horario"]))
            conn.commit()
        return True, "Grade validada e salva no banco com sucesso!"