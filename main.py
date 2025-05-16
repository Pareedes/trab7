import tkinter as tk
from tkinter import ttk, messagebox
import random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class CourseSubject:
    def __init__(self, nome, aulas, professor, turma):
        self.nome = nome
        self.aulas = aulas
        self.professor = professor
        self.turma = turma

class ScheduleGAApp:
    def __init__(self, root):

        # Configuração da janela
        self.root = root
        self.root.title("Algoritmo Genético - Horário")
        self.root.configure(bg="#2E2E2E")

        self.controls = tk.Frame(root, bg="#2E2E2E")
        self.controls.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.canvas_frame = tk.Frame(root, bg="#2E2E2E")
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.entries = {}

        # Inputs dos parâmetros automaticos
        self.add_input("Tamanho da população", "30")
        self.add_input("Gerações", "100")
        self.add_input("Prob. Cruzamento", "0.9")
        self.add_input("Prob. Mutação", "0.01")
        self.add_input("Elitismo", "4")
        self.add_input("Tam. Torneio", "5")

        # Seleção do metodo
        self.selecao_var = tk.StringVar(value="Torneio")
        tk.Label(self.controls, text="Método de Seleção:", bg="#2E2E2E", fg="white").pack()
        ttk.Combobox(self.controls, textvariable=self.selecao_var, values=["Torneio", "Roleta"]).pack(pady=5)

        self.start_btn = tk.Button(self.controls, text="Executar", command=self.start_algorithm, bg="#555555", fg="white")
        self.start_btn.pack(pady=10)

        self.result_label = tk.Label(self.controls, text="", bg="#2E2E2E", fg="white", justify=tk.LEFT)
        self.result_label.pack(pady=10)

        # Parametros do algoritmo (quantidade periodos dias e horarios)
        self.TURMAS = 6
        self.DIAS = 5
        self.HORARIOS_POR_DIA = 4
        self.TOTAL_SLOTS = self.TURMAS * self.DIAS * self.HORARIOS_POR_DIA

        self.course_schedule = [
            # Período 1
            CourseSubject("Algoritmos", 8, "Ernani Borges", 1),
            CourseSubject("F. WEB Design", 2, "Marco Maciel", 1),
            CourseSubject("Matemática", 6, "Jorge", 1),
            CourseSubject("Extensão 1", 1, "Aline", 1),
            CourseSubject("Arquitetura", 3, "Rogélio", 1),

            # Período 2
            CourseSubject("Lógica", 3, "Marcelo Barreiro", 2),
            CourseSubject("E.D.", 6, "Alexandre", 2),
            CourseSubject("Mod. B.D.", 2, "Camilo", 2),
            CourseSubject("S.O.", 4, "Gustavo Bota", 2),
            CourseSubject("Extensão 2", 1, "Rogélio", 2),
            CourseSubject("Script Web", 2, "Aline", 2),

            # Período 3
            CourseSubject("P.O.O.", 6, "Eduardo Silvestre", 3),
            CourseSubject("Extensão 3", 1, "Camilo", 3),
            CourseSubject("P.O.", 5, "Hugo", 3),
            CourseSubject("B.D.", 6, "Rogério Costa", 3),
            CourseSubject("Interface", 2, "Lídia", 3),

            # Período 4
            CourseSubject("P.D.M.", 8, "Jefferson", 4),
            CourseSubject("D.A.W.1", 4, "Rafael Godoi", 4),
            CourseSubject("Esof", 4, "Mauro", 4),
            CourseSubject("Redes", 4, "Frederico", 4),

            # Período 5
            CourseSubject("LabEsof", 6, "Mauro", 5),
            CourseSubject("P.P.", 2, "Marco Maciel", 5),
            CourseSubject("DAW 2", 4, "Lídia", 5),
            CourseSubject("Probabilidade", 2, "Alef", 5),
            CourseSubject("Ética", 2, "Ana Lúcia", 5),
            CourseSubject("Implant Servidores", 4, "Gustavo Bota", 5),

            # Período 6
            CourseSubject("GeProj", 4, "Marco Maciel", 6),
            CourseSubject("Seg. Info.", 4, "Elson", 6),
            CourseSubject("Extensão 6", 2, "Ademir", 6),
            CourseSubject("Empreend.", 2, "Ana Lúcia", 6),
            CourseSubject("Ciência de Dados", 4, "Marcelo Barreiro", 6),
            CourseSubject("Intel Comput", 4, "José Ricardo", 6),
        ]


    # Funções de interface
    def add_input(self, label, default):
        tk.Label(self.controls, text=label, bg="#2E2E2E", fg="white").pack()
        entry = tk.Entry(self.controls)
        entry.insert(0, default)
        entry.pack(pady=5)
        self.entries[label] = entry

    # Inicia o algoritmo genético
    def start_algorithm(self):
        try:
            # Utiliza os valores inseridos
            pop_size = int(self.entries["Tamanho da população"].get())
            generations = int(self.entries["Gerações"].get())
            crossover_rate = float(self.entries["Prob. Cruzamento"].get())
            mutation_rate = float(self.entries["Prob. Mutação"].get())
            elitism = int(self.entries["Elitismo"].get())
            tournament_size = int(self.entries["Tam. Torneio"].get())
            selection_method = self.selecao_var.get()

            # Executa e mostra o melhor horario encontrado
            best_schedule = self.run_ag(
                pop_size, generations, crossover_rate,
                mutation_rate, elitism, tournament_size,
                selection_method
            )
            self.display_schedule(best_schedule)

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    ###
    
    # Fitness atribui pontuação ao individuo (horario)
    def fitness(self, individual):
        score = 0
        professor_horarios = {}
        disciplina_dias = {}  # Para rastrear dias por disciplina
        
        for turma in range(self.TURMAS):
            offset = turma * self.DIAS * self.HORARIOS_POR_DIA
            for dia in range(self.DIAS):
                profs_no_dia = set()
                disciplinas_no_dia = set()
                
                for hora in range(self.HORARIOS_POR_DIA):
                    idx = offset + dia * self.HORARIOS_POR_DIA + hora
                    subj = individual[idx]
                    if subj:
                        # Verificação de conflito de professor
                        prof_key = (subj.professor, dia, hora)
                        if prof_key in professor_horarios:
                            score -= 5  # penalidade maior para conflitos
                        else:
                            professor_horarios[prof_key] = True
                            profs_no_dia.add(subj.professor)
                        
                        # Rastrear disciplinas por dia
                        if subj.nome not in disciplinas_no_dia:
                            disciplinas_no_dia.add(subj.nome)
                        
                        # Verificar se a aula anterior é da mesma disciplina
                        if hora > 0:
                            prev_idx = idx - 1
                            prev_subj = individual[prev_idx]
                            if prev_subj and prev_subj.nome == subj.nome:
                                score += 3  # recompensa por aulas consecutivas
                
                # Recompensa por ter menos disciplinas diferentes no dia
                score += (self.HORARIOS_POR_DIA - len(disciplinas_no_dia)) * 2
                
                # Verifica se a disciplina está em múltiplos dias quando poderia estar em menos
                for subj in disciplinas_no_dia:
                    if subj not in disciplina_dias:
                        disciplina_dias[subj] = set()
                    disciplina_dias[subj].add(dia)
        
        # Penaliza disciplinas distribuídas em muitos dias
        for subj, dias in disciplina_dias.items():
            if len(dias) > 1:
                # Mais dias, maior a penalidade
                score -= (len(dias) - 1) * 2
        
        return score

    # Selecao de pais por metodo
    def selecionar_pais(self, population, fitnesses, method, k):
        if method == "Torneio":
            pais = []
            for _ in range(2):
                competidores = random.sample(list(zip(population, fitnesses)), k)
                competidores.sort(key=lambda x: x[1], reverse=True)
                pais.append(competidores[0][0])
            return pais
        elif method == "Roleta":
            total = sum(fitnesses)
            chances = [f / total for f in fitnesses]
            pais = random.choices(population, weights=chances, k=2)
            return pais

    # Operador de cruzamento com ponto unico
    def crossover(self, parent1, parent2, rate):
        if random.random() > rate:
            return parent1[:], parent2[:]
        point = random.randint(1, len(parent1) - 2)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2

    # Troca dois elementos do indivíduo com probabilidade
    def mutar(self, individuo, rate):
        for i in range(len(individuo)):
            if random.random() < rate:
                j = random.randint(0, len(individuo) - 1)
                individuo[i], individuo[j] = individuo[j], individuo[i]


    ###

    def run_ag(self, pop_size, generations, crossover_rate, mutation_rate, elitism, tournament_size, selection_method):
        # Funçao que cria o individuo (solucao possivel para o horario)
        def create_individual():
            total_aulas = sum(subj.aulas for subj in self.course_schedule)
            if total_aulas > self.TOTAL_SLOTS:
                raise ValueError(f"Total de aulas ({total_aulas}) excede o total de slots disponíveis ({self.TOTAL_SLOTS})")
            
            slots = [None] * self.TOTAL_SLOTS # Inicia os slots totais

            for subj in self.course_schedule:
                aulas_restantes = subj.aulas
                turma_offset = (subj.turma - 1) * self.DIAS * self.HORARIOS_POR_DIA
                dias = list(range(self.DIAS))
                random.shuffle(dias) # Embaralha os dias para variar alocação

                for dia in dias:
                    if aulas_restantes == 0:
                        break
                    start_horas = list(range(self.HORARIOS_POR_DIA))
                    random.shuffle(start_horas) # Embaralha as horas para variar alocação

                    # Tenta alocar as aulas em horários
                    for hora in start_horas:
                        idx = turma_offset + dia * self.HORARIOS_POR_DIA + hora
                        if all(
                            idx2 < turma_offset + (dia + 1) * self.HORARIOS_POR_DIA and slots[idx2] is None
                            for idx2 in range(idx, idx + aulas_restantes)
                        ):
                            for i in range(aulas_restantes):
                                slots[idx + i] = subj
                            aulas_restantes = 0
                            break

                    # Caso o bloco de horarios não encaixe, preenche hora a hora
                    for hora in range(self.HORARIOS_POR_DIA):
                        if aulas_restantes == 0:
                            break
                        idx = turma_offset + dia * self.HORARIOS_POR_DIA + hora
                        if slots[idx] is None:
                            slots[idx] = subj
                            aulas_restantes -= 1
            return slots

        # Primeira geraçao aleatoria
        population = [create_individual() for _ in range(pop_size)]

        for gen in range(generations):
            fitnesses = [self.fitness(ind) for ind in population]
            nova_pop = []

            # Elitismo para manter os melhores
            elite_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)[:elitism]
            for idx in elite_indices:
                nova_pop.append(population[idx][:])

            # Reprodução
            while len(nova_pop) < pop_size:
                # Seleciona os pais
                p1, p2 = self.selecionar_pais(population, fitnesses, selection_method, tournament_size)
                # Aplica crossover e mutaçao
                f1, f2 = self.crossover(p1, p2, crossover_rate)
                self.mutar(f1, mutation_rate)
                self.mutar(f2, mutation_rate)
                nova_pop.append(f1)
                if len(nova_pop) < pop_size:
                    nova_pop.append(f2)

            population = nova_pop

        # Retorna o melhor indivíduo
        fitnesses = [self.fitness(ind) for ind in population]
        best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        return population[best_idx]

    # Exibe o horario encontrado
    def display_schedule(self, schedule):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.canvas_frame, bg="white")
        frame.pack(fill=tk.BOTH, expand=True)

        for turma in range(self.TURMAS):
            tk.Label(frame, text=f"Turma {turma + 1}", bg="gray", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=turma+1, sticky="nsew")

        # Preenche a grade com os horários
        for dia in range(self.DIAS):
            for hora in range(self.HORARIOS_POR_DIA):
                slot_idx = dia * self.HORARIOS_POR_DIA + hora
                tk.Label(frame, text=f"D{dia+1}-H{hora+1}", bg="lightgray").grid(row=slot_idx+1, column=0, sticky="nsew")
                for turma in range(self.TURMAS):
                    index = turma * self.DIAS * self.HORARIOS_POR_DIA + slot_idx
                    subj = schedule[index]
                    texto = subj.nome if subj else ""
                    tk.Label(frame, text=texto, borderwidth=1, relief="solid").grid(row=slot_idx+1, column=turma+1, sticky="nsew")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScheduleGAApp(root)
    root.mainloop()
