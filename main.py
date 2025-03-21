from fractions import Fraction
import numpy as np
from customtkinter import *
import tkinter as tk


# через списки смежности
class Graph:
    def __init__(self, name: str = ""):

        self.name: str = name  # имя текущей вершины
        self.criteries = np.zeros((1, 1))  # отношение критериев
        self.final_vector = np.zeros(
            (1, 1)
        )  # средние по каждой из таблиц. В главной = ответ

        self.sub_names = (
            []
        )  # имена подкритериев или же альтернатив (в графе = имя листов)
        self.adj_list: list[Graph] = []  # листья
        self.already_checked: bool = (
            False  # использовал для подсчета и проверки, какую вершину использовал
        )

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
            self.recursive_file_read(arr)

    def recursive_file_read(self, arr: list[str]):
        if len(arr) == 0:
            return

        self.name = arr[0].strip()
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


class Decide(
    Graph
):  # возможно будет нужен, пока что является вершиной, но можно и без него
    # для предоставления информации, чтобы она не существовала в каждом  объекте из класса Graph
    def __init__(self, name: str = ""):  #
        super().__init__()
        self.name: str = name

    # def id_by_name(self, name: str) -> int:
    #     return self.crit_names.index(name)
    #
    # def add_Subcriteria(self, parent: str, sub: str):
    #     self.adj_list[self.id_by_name(parent)].adj_list.append(Graph(sub))


if __name__ == "__main__":

    test = Decide()

    test.read_main("k2.txt")

    test.display()

    test.calculate_mean_forall()

    test.calculate_final_matrix()

    test.display_fin()

    window = CTk(fg_color="#333")
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    window.geometry(f"{width}x{height}+0+0")
    window.update()
    window.state("zoomed")

    custom_font = CTkFont(family="Helvetica", size=20)

    default_width = int(width * 0.6)  # 60% ширины экрана

    # Создаем контейнер PanedWindow для разделения
    paned_window = tk.PanedWindow(
        window, orient="horizontal", sashrelief="raised", bd=3
    )
    paned_window.pack(fill="both", expand=True)

    # Создаем левый frame (60% ширины)
    left_frame = CTkFrame(paned_window, fg_color="gray20", width=default_width)
    paned_window.add(left_frame, minsize=300)
    # left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    # left_frame.grid_columnconfigure(0, weight=1, minsize=50, pad=20)

    hierarchy = CTkFrame(left_frame, fg_color="#333")
    hierarchy.pack(fill="both", expand=True, padx=40, pady=40)

    level0 = CTkLabel(hierarchy, text="Уровень 0", text_color="#fff", font=custom_font)
    level0.grid(row=0, column=0, sticky="ew", padx=100, pady=50)
    CTkFrame(hierarchy, height=2, fg_color="gray").grid(
        row=1, column=0, columnspan=3, sticky="ew"
    )  # Разделитель

    level1 = CTkLabel(hierarchy, text="Уровень 1", text_color="#fff", font=custom_font)
    level1.grid(row=2, column=0, sticky="ew", padx=100, pady=50)
    CTkFrame(hierarchy, height=2, fg_color="gray").grid(
        row=3, column=0, columnspan=3, sticky="ew"
    )  # Разделитель
    level2 = CTkLabel(hierarchy, text="Уровень 2", text_color="#fff", font=custom_font)
    level2.grid(row=4, column=0, sticky="ew", padx=100, pady=50)
    CTkFrame(hierarchy, height=2, fg_color="gray").grid(
        row=5, column=0, columnspan=3, sticky="ew"
    )  # Разделитель
    level3 = CTkLabel(hierarchy, text="Уровень 3", text_color="#fff", font=custom_font)
    level3.grid(row=6, column=0, sticky="ew", padx=100, pady=50)

    goal = CTkFrame(hierarchy, fg_color="#333")
    goal.grid(row=0, column=1, sticky="ew")
    goalLabel = CTkLabel(goal, text="Цель", text_color="#fff", font=custom_font).pack()

    entry = CTkEntry(goal, placeholder_text="Цель", font=custom_font).pack()

    criteria1 = CTkFrame(hierarchy, fg_color="#333")
    criteria1.grid(row=2, column=1, sticky="ew", padx=100, pady=50)
    criteria1Label = CTkLabel(
        criteria1, text="Критерий 1", text_color="#fff", font=custom_font
    ).pack()

    criteria1Entry = CTkEntry(
        criteria1, placeholder_text="количество скибидителей", font=custom_font
    ).pack()

    criteria2 = CTkFrame(hierarchy, fg_color="#333")
    criteria2.grid(row=2, column=2, sticky="ew", padx=100, pady=50)
    criteria2Label = CTkLabel(
        criteria2, text="Критерий 2", text_color="#fff", font=custom_font
    ).pack()
    criteria2Entry = CTkEntry(
        criteria2, placeholder_text="размер пиписьки", font=custom_font
    ).pack()

    # Создаем правый пустой фрейм (занимает оставшуюся ширину)
    right_frame = CTkFrame(paned_window, fg_color="gray30")
    paned_window.add(right_frame, minsize=300)

    # Создаем вкладки
    tabview = CTkTabview(master=right_frame, fg_color="gray30")
    tabview.pack(fill="both", expand=True)

    # Добавляем вкладки
    tabview.add("Отношения и связи")
    tabview.add("Результаты")

    # Делаем кнопки вкладок на всю ширину
    tabview._segmented_button.grid(sticky="ew")  # Растягивает кнопки вкладок
    tabview.grid_columnconfigure(0, weight=1)  # Позволяет им адаптироваться по ширине
    tabview._segmented_button.configure(selected_color="#6f3cfa")
    tabview._segmented_button.configure(selected_hover_color="#5726de")

    # Контент первой вкладки
    relationsFrame = CTkFrame(
        master=tabview.tab("Отношения и связи"), fg_color="gray30"
    )
    relationsFrame.pack(fill="both", expand=True)

    label1 = CTkLabel(master=relationsFrame, text="Скибиди", text_color="#fff")
    label1.pack()

    resultsFrame = CTkFrame(master=tabview.tab("Результаты"), fg_color="gray30")
    resultsFrame.pack(fill="both", expand=True)

    label2 = CTkLabel(master=resultsFrame, text="Сиськи", text_color="#fff")
    label2.pack()

    window.mainloop()
