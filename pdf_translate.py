from deep_translator import GoogleTranslator
import customtkinter as ctk,threading,os,webbrowser,pymupdf
import ocrmypdf,ocrmypdf.data #important !
from PIL import Image
import contextlib,io,pytesseract

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Initialize language mappings
        self.init_language_mappings()
        # Initialize OCR languages
        self.init_ocr_languages()
        # Initialize variables
        self.init_variables()
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
        self.s_langue = "Allemand"
        self.pdf_img = 0
        os.environ["PATH"] += os.pathsep + r"pngquant"
        os.environ["PATH"] += os.pathsep + r"gs\\bin"
        os.environ["PATH"] += os.pathsep + r"poppler\\library\\bin"

    def setup_appearance(self):
        # Appearance settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Window sizing and properties
        screen_width = self.winfo_screenwidth()  # Use instance method
        screen_height = self.winfo_screenheight()  # Use instance method
        width = 500
        height = 310
        x = int((screen_width/2) - (width/2) * self._get_window_scaling())
        y = int((screen_height/2) - (height/1.5) * self._get_window_scaling())
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.update()
        self.title("PDF & DOCX OCR Translate Tool v1.0 By Fawn")
        self.resizable(False,False)
        self.iconbitmap("icon/logo.ico")
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
        # Create language selection
        self.create_language_selector()
        # Create main menu buttons
        self.create_main_menu_buttons()
        # Create loading
        self.create_loading()
    
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

    def create_language_selector(self):
        self.button_image_l = ctk.CTkImage(Image.open("flags/allemand.jpg"), size=(25, 20))
        self.langue_from_img()
        self.combobox_l = ctk.CTkComboBox(self.frame, values=self.liste_langues, width=100, height=20, command=self.select_langue)
        self.image_lbl_l = ctk.CTkLabel(self.frame, image=self.button_image_l, text="")
        self.image_lbl_l.grid(row=0, column=2)
        self.combobox_l.grid(row=0, column=1, padx=5)
        
    def create_main_menu_buttons(self):
        # Common button style
        button_style = {
            "font": ("Franklin Gothic Medium", 16),
            "fg_color": "transparent",
            "corner_radius": 32,
            "hover_color": "#FFA200",
            "border_color": "#0022FF",
            "border_width": 2
        }
        
        # Create buttons
        self.button_choose_file = ctk.CTkButton(self.frame, text="PDF/DOCX Txt", command=self.select_file, **button_style)
        self.button_choose_file.grid(row=0, column=0, padx=20)

        # button translate
        self.button_go = ctk.CTkButton(self.frame, text="Go !", command=self.translate_file, **button_style)
        self.button_go.grid(row=0, column=3, padx=20)
        self.button_go.configure(state="disabled")

        self.button_pdf_image = ctk.CTkButton(self.frame, text="PDF/DOCX Img", command=self.select_pdf_image, **button_style)
        self.button_pdf_image.grid(row=1, column=0, pady=10)

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
        self.destroy()
    
    
    def select_langue(self,evt):
        #if self.ocr_langue == 0:
        self.s_langue = self.combobox_l.get()
        self.button_image_l = ctk.CTkImage(Image.open(f"flags/{self.s_langue}.jpg"), size=(25, 20))
        self.image_lbl_l.configure(image=self.button_image_l)

    @threaded
    def select_pdf_image(self):
        self.pdf_img = 1
        self.select_file()


    def select_file(self):
        self.progress_label.configure(text="Progression : 0%")
        filetypes = (
        ('PDF files', '*.pdf'),
        ('DOCX files', '*.docx'),
                    )
        self.filename = ctk.filedialog.askopenfilename(title='Select a file...',filetypes=filetypes,)
        self.file_and_ext = self.filename.split('/')[-1:][0]
        self.final_name = self.file_and_ext.split('.')[0]
        if self.final_name != "":
            self.button_go.configure(state="normal")

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
                        'tmp/' + self.file_and_ext,        # ← choisi ici
                         progress_bar=False
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
        os.makedirs("trads", exist_ok=True)
        doc.save("trads/"+self.final_name+"-"+lang_code.upper()+".pdf")
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

app = App()
# Set as overlay
app.attributes('-topmost', True)
app.update()
app.mainloop()


#Written By Fawn 27/05/2025
