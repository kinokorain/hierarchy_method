import tkinter as tk
import customtkinter as ctk
from fractions import Fraction
import numpy as np


# через списки смежности


class Graph:
    def __init__(self, name: str = ""):

        self.name: str = name  # имя текущей вершины
        self.criteries = np.zeros((0, 0))  # отношение критерие
        self.level: int = -1

        self.base_criteries = np.zeros((0, 0))  # отношение критериев
        self.final_vector = np.zeros(
            (0, 0)
        )  # средние по каждой из таблиц. В главной = ответ

        self.sub_names = (
            []
        )  # имена подкритериев или же альтернатив (в графе = имя листов)
        self.adj_list: list[Graph] = []  # листья
        self.already_checked: bool = (
            False  # использовал для подсчета и проверки, какую вершину использовал
        )

        self.znachimost: float = -1

    def init_znachimost(self):
        for i in range(len(self.adj_list)):
            self.adj_list[i].znachimost = self.mean_vector[0, i]

            self.adj_list[i].init_znachimost()

    def display(self):
        print(f"\n\nBASE: {self.name}\n SUBS: {self.sub_names}")

        for elem in self.adj_list:
            elem.display()

    def display_fin(self):
        print(
            f"\n\nBASE: {self.name}    Checked: {self.already_checked}\nCriteries:\n{self.criteries}\n"
            f"SUBS: {self.sub_names}\nFin:   {self.final_vector}"
        )

        for elem in self.adj_list:
            elem.display_fin()

    def init_edges(self, names: list[str]):
        for name in names:
            self.adj_list.append(Graph(name))

    def read_main(self, filename):
        with open(filename, "r", encoding="utf-8") as file:
            arr = file.readlines()
            print(arr)
            self.level = 0
            self.recursive_file_read(arr)

    def recursive_file_read(self, arr: list[str]):
        if len(arr) == 0:
            return

        self.name = arr[0].strip()
        print(self.name, self.level)
        arr.pop(0)
        # print('start of:', self.name)

        self.sub_names = arr[0].strip().split()
        arr.pop(0)

        if self.sub_names[0] != "@":
            self.init_edges(self.sub_names)

        else:
            self.sub_names.pop(0)
            self.already_checked = True

        crit_size: int = len(self.sub_names)

        self.criteries = np.resize(self.criteries, (crit_size, crit_size))

        for i in range(0, 1):
            for k in range(0, crit_size):
                line = arr[0]
                arr.pop(0)

                data = line.strip().split(",")

                for l in range(0, crit_size):
                    if data[l] not in ["\n", " ", ""]:
                        self.criteries[k, l] = float(Fraction(data[l]))

        # print('going to rec:', self.name,'\n')
        for i in range(0, len(self.adj_list)):
            self.adj_list[i].level = self.level + 1
            self.adj_list[i].recursive_file_read(arr)

        # print('end of:', self.name)

    def calculate_mean(self):
        size: int = len(self.sub_names)
        criteries_T = np.transpose(self.criteries)
        for i in range(0, size):
            criteries_T[i] /= criteries_T[i].sum()

        self.criteries = np.transpose(criteries_T)

        mean_crit = np.empty((1, size))

        for i in range(0, size):
            mean_crit[0, i] = np.mean(self.criteries[i])

        return mean_crit

    def calculate_mean_forall(self):
        size: int = len(self.adj_list)

        self.final_vector = self.calculate_mean()

        for i in range(0, size):
            self.adj_list[i].calculate_mean_forall()

    def calculate_final_matrix(self):
        arr = np.empty((0, 0))

        for elem in self.adj_list:
            if not elem.already_checked:
                elem.calculate_final_matrix()
            if np.size(arr) == 0:
                arr.resize((0, np.size(elem.final_vector)))

            arr = np.append(arr, elem.final_vector, axis=0)

        arr = np.transpose(arr)

        if np.size(arr) > 0:
            sub = np.empty((1, arr.shape[0]))
            for i in range(0, arr.shape[0]):
                val = 0
                for j in range(0, arr.shape[1]):
                    val += arr[i, j] * self.final_vector[0, j]
                sub[0, i] = val
            self.final_vector = sub
            self.already_checked = True

    # возвращает объект по его имени
    def get_member_by_name(self, name_of_member: str):
        if self.name == name_of_member:
            return self

        for elem in self.adj_list:
            compare = elem.get_member_by_name(name_of_member)
            if compare != None:
                return compare

    def get_param_of_member_by_name(self, name_of_member: str, name_of_param: str):
        if self.name == name_of_member:
            return getattr(self, name_of_param)

        for elem in self.adj_list:
            compare = elem.get_param_of_member_by_name(name_of_member, name_of_param)
            if compare != None:
                return compare

    def construct_subs_by_level(self, arr=None):
        if arr is None:
            arr = [[]]

        if self.level >= len(arr):
            arr.append([])

        arr[self.level].append(self.name)
        for elem in self.adj_list:
            elem.construct_subs_by_level(arr)
        return arr

    # возвращает альтренативы
    def get_alts(self) -> list[str]:
        if len(self.adj_list) <= 0:
            return self.sub_names

        for elem in self.adj_list:
            compare = elem.get_alts()
            if compare != None:
                return compare

    def get_all_subs(self):
        # if len(self.adj_list) <= 0:
        #     return self.sub_names
        print(self.name, self.sub_names)
        for elem in self.adj_list:
            elem.get_all_subs()

            # if compare != None:
            #     return compare

    def get_attr_by_name(self, name: str):
        return getattr(self, name)

    def sogl_check(self, lambdaVec):
        print(lambdaVec)
        lambdaMax = max(lambdaVec)
        print(lambdaMax)
        n = len(lambdaVec)
        val = (lambdaMax - n) / (n - 1)
        print(val)
        return val <= 0.1

    def is_matrix_correct(self):
        print("is_matrix_correct")
        if self.final_vector.size == 0:
            print("f self.fin.size = 0")
            self.calculate_mean()
        print(self.base_criteries)
        print(self.final_vector)
        alambda = np.empty((1, self.base_criteries.shape[0]))
        for i in range(0, self.base_criteries.shape[0]):
            val = 0
            for j in range(0, self.base_criteries.shape[1]):
                val += self.base_criteries[i, j] * self.final_vector[0, j]
            alambda[0, i] = val

        print(alambda)
        lambdaVec = []
        for i in range(alambda[0].size):
            lambdaVec.append(alambda[0, i] / self.final_vector[0, i])

        return self.sogl_check(lambdaVec)


class Decide:  # возможно будет нужен, пока что является вершиной, но можно и без него
    # для предоставления информации, чтобы она не существовала в каждом  объекте из класса Graph
    def __init__(self):  #
        self.graph = Graph()
        self.alts: list[str] = []

    # def id_by_name(self, name: str) -> int:
    #     return self.crit_names.index(name)
    #
    # def add_Subcriteria(self, parent: str, sub: str):
    #     self.adj_list[self.id_by_name(parent)].adj_list.append(Graph(sub))


class HierarchyFrame(ctk.CTkFrame):
    def __init__(self, parent, font):
        super().__init__(parent, fg_color="#333")
        self.pack(fill="both", expand=True, padx=40, pady=40)

        # self.create_levels(font)
        # self.create_criteria(font)

    # def create_levels(self, font):
    #     levels = ["Уровень 0", "Уровень 1", "Уровень 2", "Уровень 3"]
    #     for i, level in enumerate(levels):
    #         ctk.CTkLabel(self, text=level, text_color="#fff", font=font).grid(
    #             row=i * 2, column=0, sticky="ew", padx=100, pady=50
    #         )
    #         ctk.CTkFrame(self, height=2, fg_color="gray").grid(
    #             row=i * 2 + 1, column=0, columnspan=3, sticky="ew"
    #         )

    # def create_criteria(self, font):
    #     goal = ctk.CTkFrame(self, fg_color="#333")
    #     goal.grid(row=0, column=1, sticky="ew")
    #     ctk.CTkLabel(goal, text="Цель", text_color="#fff", font=font).pack()
    #     ctk.CTkEntry(goal, placeholder_text="Цель", font=font).pack()

    #     criteria = [
    #         ("Критерий 1", "Критерий 1"),
    #         ("Критерий 2", "Критерий 2"),
    #         ("Критерий 3", "Критерий 3"),
    #         ("Критерий 4", "Критерий 4"),
    #     ]
    #     for i, (label, placeholder) in enumerate(criteria):
    #         frame = ctk.CTkFrame(self, fg_color="#333")
    #         frame.grid(row=2, column=i + 1, sticky="ew", padx=50, pady=50)
    #         ctk.CTkLabel(frame, text=label, text_color="#fff", font=font).pack()
    #         ctk.CTkEntry(frame, placeholder_text=placeholder, font=font).pack()


class TabView(ctk.CTkTabview):
    def __init__(self, parent):
        super().__init__(parent, fg_color="gray30")
        self.pack(fill="both", expand=True)

        self.add("Отношения и связи")
        self.add("Результаты")

        self._segmented_button.grid(sticky="ew")
        self.grid_columnconfigure(0, weight=1)
        # self._segmented_button.configure(
        #     selected_color="#6f3cfa", selected_hover_color="#5726de"
        # )

        self.create_tabs()

    def create_tabs(self):
        relations_frame = ctk.CTkFrame(self.tab("Отношения и связи"), fg_color="gray30")
        relations_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(relations_frame, text="Таблица", text_color="#fff").pack()

        results_frame = ctk.CTkFrame(self.tab("Результаты"), fg_color="gray30")
        results_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(results_frame, text="Результаты", text_color="#fff").pack()


class MyApp(ctk.CTk):
    def __init__(self, graph: Graph):
        super().__init__(fg_color="#333")

        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        self.geometry(f"{self.width}x{self.height}+0+0")
        self.update()
        self.state("zoomed")
        self.custom_font = ctk.CTkFont(family="Helvetica", size=20)
        self.create_layout(graph)

    def create_layout(self, graph: Graph):
        paned_window = tk.PanedWindow(
            self, orient="horizontal", sashrelief="raised", bd=3
        )
        paned_window.pack(fill="both", expand=True)

        left_frame = ctk.CTkFrame(
            paned_window, fg_color="gray20", width=int(self.width * 0.6)
        )
        paned_window.add(left_frame, minsize=300)

        self.displayGraph(left_frame, graph, 0)

        right_frame = ctk.CTkFrame(paned_window, fg_color="gray30")
        paned_window.add(right_frame, minsize=300)

        TabView(right_frame)

    def displayGraph(self, parent, graph: Graph, index):

        print("in displayGraph")

        canvas = tk.Canvas(parent, bg="#222", highlightthickness=0)
        canvas.pack(fill="both", expand=True)


        sub_levels = graph.construct_subs_by_level()
        sub_levels.append(graph.get_alts())
        vertexes = [[] for i in range(len(sub_levels))]
        print(vertexes)

        for i, level in enumerate(sub_levels):
            row = ctk.CTkFrame(canvas, fg_color="#333")
            row.grid(row=i, column=0, padx=50, pady=50, sticky="ew")

            # Ensure the row stretches to fill the width of parent
            row.grid_columnconfigure(0, weight=1)

            for j, elem in enumerate(level):
                vertex = ctk.CTkButton(
                    row,
                    text=elem,
                    text_color="#fff",
                    anchor="center",  # Center text
                    height=70,
                )
                # print(elem, graph.get_param_of_member_by_name(elem, "sub_names"))
                vertex._text_label.configure(wraplength=100)
                vertex.grid(row=0, column=j, sticky="ew", padx=5, pady=5)

                # Make each button expand proportionally
                row.grid_columnconfigure(j, weight=1)
                canvas.update_idletasks()
                vertexes[i].append(vertex)
        # print(vertexes)
   
   

        for i in range(len(vertexes)):
            for j in range(len(vertexes[i])):
                # vertexes[i][j].fg_color = '#100'
                unit = graph.get_member_by_name(vertexes[i][j]._text)
                if unit == None:
                    continue
                if len(unit.sub_names) > 0:
                    # print(vertexes[i][j]._text)
                    lever = False
                    
                    for sub in unit.sub_names:
                        
                        for elem in vertexes[i+1]:
                            # print(sub, elem._text)
                            if elem._text == sub:
                                print(vertexes[i][j]._text, unit.sub_names)
                                print(vertexes[i][j].winfo_rootx() + vertexes[i][j].winfo_width() // 2,
                                    vertexes[i][j].winfo_rooty() + vertexes[i][j].winfo_height() // 2,

                                    elem.winfo_rootx() + elem.winfo_width() // 2,
                                    elem.winfo_rooty() + elem.winfo_height() // 2)
                                canvas.create_line(
                                    vertexes[i][j].winfo_rootx() + vertexes[i][j].winfo_width() // 2,
                                    vertexes[i][j].winfo_rooty() + vertexes[i][j].winfo_height() // 2,

                                    elem.winfo_rootx() + elem.winfo_width() // 2,
                                    elem.winfo_rooty() + elem.winfo_height() // 2,
                                    fill = 'white', width = 3
                                )



                                lever = True
                                break
                            # if lever: break


        # Ensure the parent expands to accommodate the full width
        parent.grid_columnconfigure(0, weight=1)

        # row = ctk.CTkFrame(parent, fg_color="#fff")
        # row.grid(row=graph.level, column=0, padx=50, pady=10, sticky="ew")

        # if graph.level == 0:
        #     print("aboba")
        #     vertex = ctk.CTkButton(
        #         row,
        #         text=graph.name.replace("_", " ") + str(graph.level),
        #         text_color="#fff",
        #     )
        #     vertex.grid(row=0, column=0)

        # for index, elem in enumerate(graph.adj_list):
        #     vertex = ctk.CTkButton(
        #         row,
        #         text=elem.name.replace("_", " ") + str(elem.level),
        #         text_color="#fff",
        #     )
        #     vertex.grid(row=elem.level + 1, column=index)
        #     self.displayGraph(parent, elem, index)


if __name__ == "__main__":

    test = Graph()
    test.read_main("k2.txt")

    # test.calculate_mean_forall()
    # if not test.graph.is_matrix_correct():
    #     print("matrix incorrect")

    # test.display_fin()

    # test.calculate_final_matrix()

    # test.display_fin()

    # print(f"\ndef find by name:")
    # unit = test.graph.get_member_by_name("Цена_Земли")
    # unit.display_fin()

    # print(f"\ndef get_alts:")
    # print(test.graph.get_alts())

    # print(f"\ndef get_all_subs:")
    # test.graph.get_all_subs()

    # print(f"\ndef get_attr_by_name:")
    # print(test.graph.get_attr_by_name("name"))

    # print(f"\ndef get_param_of_member_by_name:")
    # val = test.graph.get_param_of_member_by_name("Земельный_Участок", "sub_names")
    # print(val)

    # val2 = test.graph.get_param_of_member_by_name("Набор_Персонала", "adj_list")
    # print(val2[0].display_fin())

    app = MyApp(test)
    # app.displayGraph(test)
    app.mainloop()
