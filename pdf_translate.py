from deep_translator import GoogleTranslator
import customtkinter as ctk,threading,os,webbrowser,pymupdf
import ocrmypdf #important !
from PIL import Image
import contextlib,io,pytesseract,psutil,json
import pikepdf
from playsound import playsound
import tkinter as tk
from tkinter import messagebox
from modules.zone_editor import ZoneEditorToplevel
from modules.theme_manager import ThemeManager

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Initialize variables
        self.init_variables()
        # Load config from JSON
        self.load_config()
        # Initialize language mappings
        self.init_language_mappings()
        # Initialize OCR languages
        self.init_ocr_languages()
        # Set up UI appearance
        self.setup_appearance()
        # Create UI frames
        self.create_frames()
        # Create UI elements
        self.create_ui_elements()
        # Create donate button
        self.create_donate_button()

    def init_language_mappings(self):
        self.LANG_CODE_MAP = {
            'Allemand': 'de', 
            'Anglais': 'en',
            'Chinois': 'zh-CN', 
            'Espagnol': 'es', 
            'Francais': 'fr',
            'Italien': 'it',
            'Russe': 'ru'
        }

    def init_ocr_languages(self):
        pytesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR\\tesseract.exe"
        base_langs = {
        'Allemand': 'deu',
        'Anglais': 'eng',
        'Chinois': 'chi_sim',
        'Espagnol': 'spa',
        'Francais': 'fra',
        'Italien': 'ita',
        'Russe': 'rus'
    }

        installed = set(pytesseract.get_languages(config=''))
        self.OCR_LANG_MAP = {}

        for label, code in base_langs.items():
            if code in installed:
                self.OCR_LANG_MAP[label] = code
            else:
                self.OCR_LANG_MAP[label] = 'eng'  # fallback

    def init_variables(self):
        # Init dictionaries and variables
        self.open_editors = {}  # cle = chemin absolu du PDF, valeur = fenêtre ZoneEditorToplevel
        self.current_theme = "dark"
        self.s_langue = "Allemand"
        self.pdf_img = 0
        os.environ["PATH"] += os.pathsep + r"pngquant"
        os.environ["PATH"] += os.pathsep + r"gs\\bin"
        os.environ["PATH"] += os.pathsep + r"poppler\\library\\bin"

    def setup_appearance(self):
        # Appearance settings
        ThemeManager.set_theme(self.current_theme)
        
        # Window sizing and properties
        screen_width = self.winfo_screenwidth()  # Use instance method
        screen_height = self.winfo_screenheight()  # Use instance method
        width = 450
        height = 310
        x = int((screen_width/2) - (width/2) * self._get_window_scaling())
        y = int((screen_height/2) - (height/1.5) * self._get_window_scaling())
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.update()
        self.title("PDF OCR Translate Tool v1.0 By Fawn")
        self.resizable(False,False)
        self.iconbitmap("icon/logo.ico")
        self.iconphoto(False, tk.PhotoImage(file="icon/logo.png"))
        self.grid_columnconfigure(3, weight=1)
        self.attributes('-alpha', 1)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_frames(self):
        # Create main frames for layout
        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.grid(row=0, column=0,padx = 20, pady=10)

        self.frame2 = ctk.CTkFrame(self, fg_color="transparent")
        self.frame2.grid(row=1, column = 0)

    def create_ui_elements(self):
        # Create theme
        self.create_theme()
        # Create language selection
        self.create_language_selector()
        # Create main menu buttons
        self.create_main_menu_buttons()
        # Create loading
        self.create_loading()

    def load_config(self):
        try:
            with open("conf\\config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                self.current_theme = config["theme"]
        except FileNotFoundError:
            self.current_theme = "dark"

    def create_theme(self):
        text_color = "black" if self.current_theme == "light" else "white"
        opposite_theme = "dark" if self.current_theme == "light" else "light"
        self.theme_button = ctk.CTkButton(
        self.frame,
        text="Theme : "+opposite_theme.capitalize(),
        command=self.toggle_theme,
        font = ("Franklin Gothic Medium", 16),
        fg_color = "transparent",
        corner_radius = 32,
        text_color=text_color,
        hover_color = "#FFA200",
        border_color = "#0022FF",
        border_width = 2,
        width = 60
        )
        self.theme_button.grid(row=1, column=1, padx=10, pady=10)

    
    def langue_from_img(self):
        # Get language names from image files
        l = os.listdir('flags')
        self.liste_langues = [x.split('.')[0].capitalize() for x in l]

    def create_loading(self):
        self.progress_bar = ctk.CTkProgressBar(self.frame, width=400)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=2, column=0, columnspan = 4)

        # Label du pourcentage
        self.progress_label = ctk.CTkLabel(self.frame, text="Progression : 0 %", font=("Arial", 12))
        self.progress_label.grid(row=3, column=0, pady=5)

        # Nouveau label pour afficher le nom du fichier
        self.filename_label = ctk.CTkLabel(self.frame, text="", font=("Arial", 14, "bold"))
        self.filename_label.grid(row=3, column=1, columnspan=3, sticky="w", padx=10)

    def create_language_selector(self):
        self.button_image_l = ctk.CTkImage(Image.open("flags/allemand.jpg"), size=(25, 20))
        self.langue_from_img()
        self.combobox_l = ctk.CTkComboBox(self.frame, values=self.liste_langues, width=100, height=20, command=self.select_langue)
        self.image_lbl_l = ctk.CTkLabel(self.frame, image=self.button_image_l, text="")
        self.image_lbl_l.grid(row=0, column=2)
        self.combobox_l.grid(row=0, column=1, padx=5)
        
    def create_main_menu_buttons(self):
        text_color = "black" if self.current_theme == "light" else "white"
        # Common button style
        button_style = {
            "font": ("Franklin Gothic Medium", 16),
            "fg_color": "transparent",
            "corner_radius": 32,
            "text_color": text_color,
            "hover_color": "#FFA200",
            "border_color": "#0022FF",
            "border_width": 2,
            "width" : 60
        }
        
        # Create buttons
        self.button_choose_file = ctk.CTkButton(self.frame, text="Text", command=self.select_file, **button_style)
        self.button_choose_file.grid(row=0, column=0, padx=20)

        # button translate
        self.button_go = ctk.CTkButton(self.frame, text="Go !", command=self.translate_file, **button_style)
        self.button_go.grid(row=0, column=3, padx=20)
        self.button_go.configure(state="disabled")

        self.button_pdf_image = ctk.CTkButton(self.frame, text="Scan", command=self.select_pdf_image, **button_style)
        self.button_pdf_image.grid(row=1, column=0, pady=10)
        self.button_edit = ctk.CTkButton(self.frame, text="📝 Edit PDF", command=self.open_editor, **button_style)
        self.button_edit.grid(row=1, column=3, padx=10)

    # Thread decorator
    def threaded(fn):
        def wrapper(*args, **kwargs):
            threading.Thread(target=fn, args=args, kwargs=kwargs,daemon=True).start()#daemon=True to kill threads with main app
        return wrapper

    @threaded
    def don(self):
        # Open donation link
        url = "https://www.paypal.com/paypalme/noobpythondev"
        webbrowser.open(url)

    def create_donate_button(self):
        self.button_image = ctk.CTkImage(Image.open("icon/donate.png"), size=(240, 166))
        self.image_button = ctk.CTkButton(
            self.frame2, 
            image=self.button_image, 
            text="",
            hover=False,
            fg_color="transparent",
            border_width=0,
            command=self.don
        )
        self.image_button.grid(row=0, column=0)

    def on_closing(self):
        current_process = psutil.Process(os.getpid())
        # Terminer les sous-processus si existants
        for child in current_process.children(recursive=True):
            try:
                child.terminate()
            except Exception:
                pass

        self.destroy()
        os._exit(0)  # Force l'arrêt de Python et de tous les threads restants

    def toggle_theme(self):
        self.fade_theme_transition()


    def fade_theme_transition(self, steps=20, delay=20):
        def play_click_sound():
            def safe_play():
                try:
                    playsound("sound\\sound2.wav")
                except Exception as e:
                    print("Erreur audio :", e)

            threading.Thread(target=safe_play, daemon=True).start()

        play_click_sound()  # <- joue le son immédiatement, dès l’appel
        def fade_out(step=0):
            if step <= steps:
                alpha = 1.0 - (step / steps)
                self.attributes('-alpha', alpha)
                self.after(delay, lambda: fade_out(step + 1))
            else:
                switch_theme()
                fade_in()

        def fade_in(step=0):
            if step <= steps:
                alpha = step / steps
                self.attributes('-alpha', alpha)
                self.after(delay, lambda: fade_in(step + 1))

        def switch_theme():
            if self.current_theme == "dark":
                ThemeManager.set_theme("light")
                self.current_theme = "light"
                self.theme_button.configure(text="Theme : Dark", text_color="black")
            else:
                ThemeManager.set_theme("dark")
                self.current_theme = "dark"
                self.theme_button.configure(text="Theme : Light", text_color="white")

            for btn in [self.button_choose_file, self.button_go, self.button_pdf_image,self.button_edit]:
                btn.configure(text_color="black" if self.current_theme == "light" else "white")

            self.save_config()

        fade_out()


    def select_langue(self,evt):
        self.s_langue = self.combobox_l.get()
        self.button_image_l = ctk.CTkImage(Image.open(f"flags/{self.s_langue}.jpg"), size=(25, 20))
        self.image_lbl_l.configure(image=self.button_image_l)

    @threaded
    def select_pdf_image(self):
        self.pdf_img = 1
        self.select_file()

    def save_config(self):
        config = {"theme": self.current_theme}
        with open("conf\\config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)


    def select_file(self):
        self.progress_label.configure(text="Progression : 0%")
        filetypes = [
        ('PDF files', '*.pdf')
        ]
        self.filename = ctk.filedialog.askopenfilename(title='Select a file...',filetypes=filetypes,)
        self.file_and_ext = self.filename.split('/')[-1:][0]
        self.final_name = self.file_and_ext.split('.')[0]
        if self.final_name != "":
            self.button_go.configure(state="normal")
            self.filename_label.configure(text=self.file_and_ext)

    @threaded
    def translate_file(self):
        self.button_go.configure(state="disabled")
        self.button_pdf_image.configure(state="disabled")
        self.button_choose_file.configure(state="disabled")
        if self.pdf_img==1:
            os.makedirs("tmp", exist_ok=True)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                #Pour des fichiers peu volumineux ne laissser que deskew
                #Options : language,deskew,rotat_pages,optimize,force_ocr,output_type,progress_bar
                if __name__ == '__main__':  # To ensure correct behavior on Windows and macOS
                    ocrmypdf.ocr(
                        self.filename,
                        'tmp/' + self.file_and_ext,
                        progress_bar=False,
                                 )
                self.filename =os.getcwd()+'/tmp/'+self.file_and_ext
        # Define color "white"
        WHITE = pymupdf.pdfcolor["white"]
        # This flag ensures that text will be dehyphenated after extraction.
        textflags = pymupdf.TEXT_DEHYPHENATE
        # Configure the desired translator
        # Get language code
        lang_code = self.LANG_CODE_MAP.get(self.s_langue, "")
        to_trad = GoogleTranslator(source="auto", target=lang_code)
        # Open the document
        doc = pymupdf.open(self.filename)
        # Define an Optional Content layer in the document named "Layer".
        # Activate it by default.
        ocg_xref = doc.add_ocg("Layer", on=True)
        self.progress_bar.set(0)
        page_count = len(doc)
        # Iterate over all pages
        for idx,page in enumerate(doc):
        # Extract text grouped like lines in a paragraph.
            blocks = page.get_text("blocks", flags=textflags)
            # Every block of text is contained in a rectangle ("bbox")
            for block in blocks:
                bbox = block[:4]  # area containing the text
                langue = block[4]  # the text of this block
                # Invoke the actual translation to deliver us a translated string
                trad = to_trad.translate(langue)
                # Cover the original text with a white rectangle.
                page.draw_rect(bbox, color=None, fill=WHITE, oc=ocg_xref)
                # Write the translated text into the rectangle
                page.insert_htmlbox(bbox, trad, oc=ocg_xref)
                # Mise à jour de la barre de progression
            progress_value = ((idx + 1) / page_count)
            self.progress_bar.set(progress_value)
            self.progress_label.configure(text=f"Progression : {int(progress_value * 100)} %")
        doc.subset_fonts()
        doc.set_metadata({})  # Supprimer les métadonnées pour alléger le PDF
        os.makedirs("trads", exist_ok=True)
        doc.save("trads/"+self.final_name+"-"+lang_code.upper()+".pdf")
        # Compression du PDF avec pikepdf en gardant un seul fichier
        final_pdf_path = f"trads/{self.final_name}-{lang_code.upper()}.pdf"
        compressed_tmp_path = final_pdf_path + ".tmp"
        with pikepdf.open(final_pdf_path) as pdf:
            pdf.save(compressed_tmp_path, compress_streams=True)
        os.remove(final_pdf_path)  # Supprime le fichier non compressé
        os.rename(compressed_tmp_path, final_pdf_path)  # Renomme le compressé proprement
        doc.close()  # <- ici, on libère le fichier
        self.progress_label.configure(text="Terminé !")
        self.del_file()
        self.button_pdf_image.configure(state="normal")
        self.button_choose_file.configure(state="normal")

    def del_file(self):
        if self.pdf_img==1:
            location =os.getcwd()+"\\tmp"
            path = os.path.join(location, self.file_and_ext)
            os.remove(path)
            os.rmdir(location)
            self.pdf_img=0
            

    def open_editor(self):
        if not hasattr(self, "filename") or not self.filename:
            messagebox.showwarning("Aucun fichier", "Veuillez d'abord ouvrir un fichier PDF ou DOCX.")
            return

        abs_path = os.path.abspath(self.filename)

        if abs_path in self.open_editors:
            try:
                self.open_editors[abs_path].lift()
                self.open_editors[abs_path].focus_force()
            except:
                pass
            messagebox.showinfo("Déjà ouvert", "Ce fichier est déjà en cours d’édition.")
            return

        # Extraire le nom du fichier sans extension
        filename_only = os.path.splitext(os.path.basename(self.filename))[0]

        editor = ZoneEditorToplevel(
            self,
            self.filename,
            self.LANG_CODE_MAP,
            self.OCR_LANG_MAP,
            self.s_langue,
            original_name=filename_only
        )

        self.open_editors[abs_path] = editor

        def on_editor_close():
            if abs_path in self.open_editors:
                del self.open_editors[abs_path]
            editor.destroy()

        editor.protocol("WM_DELETE_WINDOW", on_editor_close)

app = App()
# Set as overlay
app.attributes('-topmost', True)
app.update()
app.mainloop()

#Written By Fawn 27/05/2025
