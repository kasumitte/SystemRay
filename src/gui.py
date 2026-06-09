import customtkinter as ctk
from PIL import Image
import queue
from src.metrics import bytes_to_readable


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.success_frame = None
        
        scan_btn = ctk.CTkButton(self, text=controller.t("scan"),
                                width=200, height=40, command=lambda: self.controller.send_task("scan"))
        scan_btn.grid(row=1, column=0, columnspan=3, pady=20)
        
        cpu_card = ctk.CTkFrame(self, corner_radius=10)
        cpu_card.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(cpu_card, text=controller.t("cpu"), font=("Arial", 12)).pack(pady=(10, 0))
        self.cpu_label = ctk.CTkLabel(cpu_card, text="0%", font=("Arial", 24))
        self.cpu_label.pack(pady=(0, 10))
        
        ram = ctk.CTkFrame(self, corner_radius=10)
        ram.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(ram, text=controller.t("ram"), font=("Arial", 12)).pack(pady=(10, 0))
        self.ram_label = ctk.CTkLabel(ram, text="0%", font=("Arial", 24))
        self.ram_label.pack(pady=(0, 10))
        
        disk = ctk.CTkFrame(self, corner_radius=10)
        disk.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(disk, text=controller.t("disk"), font=("Arial", 12)).pack(pady=(10, 0))
        self.disk_label = ctk.CTkLabel(disk, text="0%", font=("Arial", 24))
        self.disk_label.pack(pady=(0, 10))
        
        self.progress_label = ctk.CTkLabel(self, text=controller.t("scan_proc"))
        self.progress_label.grid(row=2, column=0, columnspan=3, pady=(10, 0))
        
        self.file_rows = []   
        
        self.progress_bar = ctk.CTkProgressBar(self, corner_radius=10)
        self.progress_bar.grid(row=3, columnspan=3, padx=30, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)
        
        self.results_frame = ctk.CTkScrollableFrame(self)
        self.results_frame.grid(row=4, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.grid_rowconfigure(4, weight=1)
        
        self.clean_btn = ctk.CTkButton(self, text=controller.t("clean"), command=self.clean_selected)
        self.clean_btn.grid(row=5, columnspan=3, pady=10)       
                
    def update_bar(self, value, label):
        self.progress_bar.set(value)
        self.progress_label.configure(text=label)   
        
    def add_cat_row(self, cat_name, size, files_list):
        var = ctk.BooleanVar()
        row = ctk.CTkFrame(self.results_frame)
        row.pack(fill="x", pady=2)
        
        ctk.CTkCheckBox(row, text=str(cat_name), variable=var).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=size).pack(side="right", padx=5)
        
        self.file_rows.append((row, files_list, var))
            
    def clean_selected(self):
        selected = []
        for row, files_list, var in self.file_rows:
            if var.get():
                selected.extend(files_list)
        
        if selected:
            self.controller.send_task("clean", selected)        
        
    def update_metrics_cards(self, cpu_val, ram_val, disk_val):
        self.cpu_label.configure(text=cpu_val)
        self.ram_label.configure(text=ram_val)
        self.disk_label.configure(text=disk_val)
        
    def clean_done_ui(self, deleted: list, stats: tuple):
        for row, _, _ in self.file_rows:
            row.destroy()
        self.file_rows.clear()
        
        self.results_frame.grid_remove()
        self.progress_bar.grid_remove()
        self.progress_label.grid_remove()
        self.clean_btn.grid_remove()
        
        self.success_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.success_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=20, pady=20)
        self.success_frame.columnconfigure(0, weight=1)
        
        size = bytes_to_readable(stats[1]) if isinstance(stats[1], (int, float)) else stats[1]
        
        if self.controller.lang == "en":
            success_text = f"Done! Deleted files: {stats[0]}, Space cleaned: {size}"
            btn_text = "<- Go Back"
        else:
            success_text = f"Готово! Очищенно файлов: {stats[0]}, Очищенно места: {size}"
            btn_text = "<- Назад"
            
        text_label = ctk.CTkLabel(self.success_frame, text=success_text, font=("Arial", 16, "bold"))
        text_label.pack(pady=(50, 20))
        
        back_btn = ctk.CTkButton(
            self.success_frame, 
            text=btn_text,
            width=170, height=40,
            fg_color="#333333", hover_color="#444444",
            command=self.reset_ui)
        back_btn.pack(pady=10)
        
    def reset_ui(self):
        if self.success_frame is not None:
            self.success_frame.destroy()
            self.success_frame = None
            
        self.results_frame.grid()
        self.progress_bar.grid()
        self.progress_label.grid()
        self.clean_btn.grid()
        
        self.progress_bar.set(0)
        self.progress_label.configure(text=self.controller.t("scan_proc"))
        
        
class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0)
        self.controller = controller
        
        chat_icon = ctk.CTkImage(light_image=Image.open("assets/chat_icon_b.png"),
                                 dark_image=Image.open("assets/chat_icon_l.png"), size=(20, 20))
        
        chat_btn = ctk.CTkButton(self, image=chat_icon, fg_color="transparent", hover_color="#333333",
                                 text="", width=40, command=lambda: controller.toggle_chat())
        chat_btn.pack(side="top", pady=10)
        
        btn = ctk.CTkButton(self, text="Home", 
                            command=lambda: controller.show_page(HomePage))     
        btn.pack(pady=10, padx=5)
        
        gear_icon = ctk.CTkImage(light_image=Image.open("assets/gear_icon_b.png"),
                                 dark_image=Image.open("assets/gear_icon_l.png"), size=(20, 20))
        
        set_btn = ctk.CTkButton(self, fg_color="transparent", hover_color="#333333", image=gear_icon, text="", 
                                width=40, command=lambda: controller.show_page(SettingsPage))
        set_btn.pack(side="bottom", pady=10)


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text=controller.t("api_key")).grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.api_entry = ctk.CTkEntry(self, show="*")
        self.api_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(self, text=controller.t("theme")).grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.theme = ctk.CTkOptionMenu(self, values=[
            str(controller.t("theme_opt")[0]), str(controller.t("theme_opt")[1]), str(controller.t("theme_opt")[2])], button_hover_color="#333333")
        self.theme.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        self.theme.configure(fg_color="#333333")
        
        ctk.CTkLabel(self, text=controller.t("lang")).grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.lang = ctk.CTkOptionMenu(self, values=[str(controller.t("lang_opt")[0]), str(controller.t("lang_opt")[1])], button_hover_color="#333333")
        self.lang.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        self.lang.configure(fg_color="#333333")
        
        ctk.CTkLabel(self, text=controller.t("prompt")).grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.prompt = ctk.CTkEntry(self, placeholder_text="Your prompt here")
        self.prompt.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        self.prompt.configure(fg_color="#333333")
        
        save_btn = ctk.CTkButton(self, text=controller.t("save"), command=lambda: self.save_settings())
        save_btn.grid(row=5, columnspan=3, pady=10)

    def save_settings(self):
        theme_ops = self.theme.cget("values")
        lang_ops = self.lang.cget("values")
        
        theme_idx = theme_ops.index(self.theme.get())
        lang_idx = lang_ops.index(self.lang.get())
        
        sys_theme = ["dark", "system", "light"][theme_idx]
        sys_lang_code = "en" if lang_idx == 0 else "ru"
        
        ctk.set_appearance_mode(sys_theme)
        
        self.controller.send_task("save_settings", {
            "theme": sys_theme,
            "language": sys_lang_code,
            "api_key": self.api_entry.get(),
            "custom_prompt": self.prompt.get()
        })
    

class ChatBar(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent", width=400)
        self.controller = controller
        self.pack_propagate(False)
        self.row_c = 0
        
        self.chat_display = ctk.CTkScrollableFrame(self)
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.chat_entry = ctk.CTkEntry(self, placeholder_text=controller.t("chat_entr"), 
                                  corner_radius=20, height=50, font=("Helvetica", 14))
        self.chat_entry.pack(fill="x", pady=(0, 10), padx=10)
        self.chat_entry.bind("<Return>", lambda e: self.send_message())
        
        send_img = ctk.CTkImage(Image.open("assets/send_btn.png"), size=(20, 20))
        send_btn = ctk.CTkButton(self, image=send_img, width=30, text="", 
                                 height=30, corner_radius=20, command=lambda: self.send_message())
        send_btn.pack(side="right", pady=2, padx=2)
        
    def send_message(self):
        text = self.chat_entry.get()
        if not text:
            return
        self.chat_entry.delete(0, "end")
        self.add_chat_message(text, is_us=True)
        self.controller.send_task("message", text)
        
    def add_chat_message(self, msg: str, is_us: bool = True):
        if not msg:
            return
        anchor = "e" if is_us else "w"
        bubble = ctk.CTkLabel(self.chat_display, 
                text=msg, corner_radius=15, fg_color="#1a5fb4" if is_us else "#333333", wraplength=250
        )
        bubble.pack(anchor=anchor, padx=10, pady=5)
        
    def no_key_case(self):
        popup = ctk.CTkLabel(self.chat_display,
                text="No API keys were found, go to settings and add your key",
                corner_radius=15, fg_color="#b82323", wraplength=250
        )
        popup.pack(anchor="w", padx=10, pady=5)
        
        
class MainWindow(ctk.CTk):
    def __init__(self, task_queue: queue.Queue, result_queue: queue.Queue, translations: dict, lang: str, theme: str):
        super().__init__()
        self.geometry("1280x800")
        self.title("SystemRay")
        self.iconbitmap("assets/main_icon.ico")
        self.translations = translations
        self.lang = lang
        self.theme = theme
        self.current_page = None
         
        self.task_queue = task_queue
        self.result_queue = result_queue
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = Sidebar(self, controller=self)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        
        self.chat_vis = False
        self.chat_bar = ChatBar(self, controller=self)
        
        self.show_page(HomePage)
        self.check_result()
        self.send_task("load_history")
    
        
    def t(self, key: str) -> str:
        """ Get translations for set language (English by default) """
        return self.translations.get(self.lang, {}).get(key, key)
        
    def toggle_chat(self):
        if self.chat_vis:
            self.chat_bar.grid_remove()
        else:
            self.chat_bar.grid(row=0, column=2, sticky="ns", padx=10, pady=10)
        self.chat_vis = not self.chat_vis  
        
    def show_page(self, page_class):
        if self.current_page:
            self.current_page.destroy()
        self.current_page = page_class(self, controller=self)
        self.current_page.grid(row=0, column=1, sticky="nsew")
    
    
    def send_task(self, task_type, data=None):
        self.task_queue.put((task_type, data))
        
    def check_result(self):
        try:
            result = self.result_queue.get_nowait()
            self.handle_result(result)    
        except queue.Empty:
            pass
        self.after(100, self.check_result)
    
    def handle_result(self, result):
        match result[0]:
            case "scan_done":
                if isinstance(self.current_page, HomePage):
                    for row, _, _ in self.current_page.file_rows:
                        row.destroy()
                    self.current_page.file_rows.clear()
                    
                    for cat_name, data in result[1].items():
                        self.current_page.add_cat_row(cat_name, data["size"], data["files"])
            
            case "save_settings":
                data = result[1]
                self.lang = data.get("language", self.lang)
                self.theme = data.get("theme", self.theme)
                self.show_page(type(self.current_page))       
            
            case "message":
                self.chat_bar.add_chat_message(result[1], is_us=False)
            
            case "update_bar":
                if isinstance(self.current_page, HomePage):
                    self.current_page.update_bar(result[1][0], result[1][1])
                    
            case "update_metrics":
                if isinstance(self.current_page, HomePage):
                    self.current_page.update_metrics_cards(result[1][1], result[1][2], result[1][3])        

            case "no_key":
                self.chat_bar.no_key_case()

            case "clean_done":
                if isinstance(self.current_page, HomePage):
                    self.current_page.clean_done_ui(result[1]['paths'], result[1]["stats"])
            
            case "load_history":
                for row in result[1]:
                    user = True if row["role"] == "user" else False
                    self.chat_bar.add_chat_message(row["content"], user)
