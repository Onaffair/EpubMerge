from tkinter import messagebox,Button,Label,Listbox
import tkinter as tk
import handle


class UI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("epub合并")
        self.geometry("800x600")
        self.btn_select = Button(self, text="选择文件(Select Files)", width=40, height=5, command=self.select_option)

        self.list_title = Label(self,text="已选择的文件(Selected)")
        self.file_list = Listbox(width=40)
        self.btn_sort = Button(self,text="清空(Empty)",width=10,height=3,command=self.clear_option)
        self.btn_conbine = Button(self,text="合并(Merge)",width=10,height=3,command=self.conbine_option)
        self.btn_quit = Button(self,text="退出 Quit",width=10,height=3,command=self.quit_option)

        self.btn_select.place(x=200,y=0)
        self.list_title.place(x=200,y=125)
        self.file_list.place(x=200,y=150)
        self.btn_sort.place(x=200,y=350)
        self.btn_conbine.place(x=400,y=350)
        self.btn_quit.place(x=300,y=350)

    def quit_option(self):
        self.destroy()

    def conbine_option(self):
        handle.files_conbine()

    def clear_option(self):
        handle.clear_files()
        self.getChange()

    def select_option(self):
        handle.select_files()
        self.getChange()

    def getChange(self):
        self.file_list.delete(0,tk.END)
        for i,file in enumerate(handle.files):
            self.file_list.insert(i,file[file.rindex('/')+1:])
