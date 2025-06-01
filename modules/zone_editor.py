
import fitz  # PyMuPDF
import pytesseract
import unicodedata
import platform
import subprocess
import threading
from PIL import Image, ImageTk
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, StringVar
from deep_translator import GoogleTranslator
import os
from PIL import Image
from modules.theme_manager import ThemeManager
from modules.path_util import resource_path
from collections import Counter


class ZoneEditorToplevel(ctk.CTkToplevel):
    def __init__(self, parent, pdf_path, lang_map, ocr_map, default_lang_name, original_name):
        super().__init__(parent)
        self.title("Éditeur PDF OCR multi-zones By Fawn")
        self.after(250, lambda: self.iconbitmap(
            resource_path(f"icon/logo.ico")))
        self.iconphoto(False, tk.PhotoImage(
            file=resource_path(f"icon/logo.png")))
        # Empêche la redimension verticale/horizontale
        self.resizable(False, False)
        # Lance en fenetre maximize
        #self.state("zoomed")  # fonctionne sur Windows
        self.current_theme = ThemeManager.get_theme()
        self.text_color = "black" if self.current_theme == "light" else "white"
        ThemeManager.register(self.update_theme)
        self.original_name = original_name
        self.bind("<Destroy>", self.on_close)
        self.add_mode = False  # mode "ajout de zone" désactivé au départ
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.page_index = 0
        self.scale = 1.0
        self.zones = {}
        self.zone_widgets = {}  # Clé = page_index, valeur = dict(zone_id: frame)
        self.zone_id_counter = 1  # ID global pour toutes les zones du document
        self.lang_map = lang_map
        self.ocr_map = ocr_map

        self.trad_lang_map = StringVar(value=default_lang_name)
        self.trad_lang_code = self.ocr_map[default_lang_name]

        self.ocr_lang_var = StringVar(value=default_lang_name)
        self.ocr_lang_code = self.ocr_map[default_lang_name]

        self.translator = GoogleTranslator(
            source="auto", target=self.lang_map[default_lang_name])

        # Nom de fichier
        self.filename_label = ctk.CTkLabel(
            self, text=os.path.basename(pdf_path), font=("Arial", 14, "bold"))
        self.filename_label.grid(
            row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        # Nouvelle ComboBox pour les langues OCR basées sur ocr_map
        self.ocr_key_menu = ctk.CTkComboBox(self, values=list(self.ocr_map.keys(
        )), variable=self.ocr_lang_var, command=self.change_ocr_language, width=100)
        self.ocr_key_menu.grid(row=1, column=0, padx=10,
                               pady=(5, 10), sticky="w")

        # Combobox select langue
        self.language_menu = ctk.CTkComboBox(self, values=list(self.lang_map.keys()), variable=self.trad_lang_map,
                                             command=self.change_trad_language, width=100)
        self.language_menu.grid(row=0, column=1, pady=(10, 0), sticky="s")

        # Load initial image
        lang_lower = default_lang_name.lower()
        self.flag_image = ctk.CTkImage(Image.open(
            resource_path(f"flags/{lang_lower}.jpg")), size=(25, 20))
        self.flag_label = ctk.CTkLabel(self, image=self.flag_image, text="")
        self.flag_label.grid(row=0, column=1, padx=(
            130, 0), pady=(10, 0), sticky="s")
        self.flag_ocr_label = ctk.CTkLabel(
            self, image=self.flag_image, text="")
        self.flag_ocr_label.grid(
            row=1, column=0, padx=115, pady=(5, 10), sticky="w")

        # Numeros de pages
        self.page_entry_var = tk.StringVar()
        self.page_entry = ctk.CTkEntry(
            self, textvariable=self.page_entry_var, width=50, justify="center")
        self.page_entry.grid(row=0, column=0, pady=(
            10, 0), padx=500, sticky="e")
        self.page_entry.bind("<Return>", self.go_to_page)

        self.canvas_container = ctk.CTkFrame(self, width=800, height=1000)
        self.canvas_container.grid(
            row=1, column=0, rowspan=6, padx=10, pady=10, sticky="n")

        self.canvas = tk.Canvas(self.canvas_container,
                                width=800, height=1000, bg="gray20")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scroll_y = tk.Scrollbar(
            self.canvas_container, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.scroll_x = tk.Scrollbar(
            self, orient="horizontal", command=self.canvas.xview)
        self.scroll_x.grid(row=7, column=0, sticky="we", padx=10)
        self.canvas.configure(xscrollcommand=self.scroll_x.set)

        self.zone_panel = ctk.CTkScrollableFrame(self, width=400, height=500)
        self.zone_panel.grid(row=1, column=1, padx=10, pady=10, sticky="n")

        # Container buttons ligne 1
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2, column=1, pady=10)

        btn_style = {"font": ("Franklin Gothic Medium", 30),
                     "fg_color": "transparent",
                     "corner_radius": 32,
                     "text_color": self.text_color,
                     "hover_color": "#FFA200",
                     "border_color": "#0022FF",
                     "border_width": 2,
                     "width": 40
                     }

        # Buttons
        self.button_prev = ctk.CTkButton(
            self.button_frame, text="←", command=self.prev_page, **btn_style)
        self.button_next = ctk.CTkButton(
            self.button_frame, text="→", command=self.next_page, **btn_style)
        self.button_add = ctk.CTkButton(
            self.button_frame, text="⿴", command=self.activate_selection, **btn_style)
        self.button_export = ctk.CTkButton(
            self.button_frame, text="💾", command=self.export_pdf, **btn_style)
        self.button_open_folder = ctk.CTkButton(
            self.button_frame, text="📂", command=self.ouvrir_dossier_export, **btn_style)
        self.button_app = ctk.CTkButton(
            self.button_frame, text="🗗", command=self.bring_main_to_front, **btn_style)

        for idx, btn in enumerate([self.button_prev, self.button_next, self.button_add, self.button_export, self.button_open_folder, self.button_app]):
            btn.grid(row=0, column=idx, padx=5)

        # Conatainer buytons ligne 2
        self.zoom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.zoom_frame.grid(row=3, column=1, pady=(0, 10))

        self.zoom_in_button = ctk.CTkButton(
            self.zoom_frame, text="🔍+", command=self.zoom_in, **btn_style)
        self.zoom_out_button = ctk.CTkButton(
            self.zoom_frame, text="🔍–", command=self.zoom_out, **btn_style)
        self.zoom_in_button.pack(side="left", padx=10)
        self.zoom_out_button.pack(side="left", padx=10)

        self.start_x = self.start_y = self.rect = None
        self.selection_mode = False
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.render_page()

    # Thread decorator
    def threaded(fn):
        def wrapper(*args, **kwargs):
            # daemon=True to kill threads with main app
            threading.Thread(target=fn, args=args,
                             kwargs=kwargs, daemon=True).start()
        return wrapper

    def on_zone_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]

        for idx, zone in enumerate(self.zones.get(self.page_index, [])):
            if zone.get("canvas_id") == item or zone.get("canvas_id_text") == item:
                self.selected_zone = (idx, zone)
                self.canvas.focus_set()

                for other in self.zones.get(self.page_index, []):
                    if other.get("canvas_id") != zone["canvas_id"]:
                        self.canvas.itemconfig(
                            other["canvas_id"], outline="red", width=2)
                break

    def change_ocr_language(self, _=None):
        selected = self.ocr_lang_var.get()
        self.ocr_lang_code = self.ocr_map.get(selected, "eng")

        lang_name = selected.lower()
        try:
            new_img = Image.open(resource_path(f"flags/{lang_name}.jpg"))
            self.flag_image = ctk.CTkImage(new_img, size=(25, 20))
            self.flag_ocr_label.configure(image=self.flag_image)
        except FileNotFoundError:
            # print(f"[!] Aucune image trouvée pour '{lang_name}'")
            pass

    def change_trad_language(self, _=None):
        selected = self.trad_lang_map.get()
        self.trad_lang_code = self.lang_map.get(selected, "en")
        self.translator = GoogleTranslator(
            source="auto", target=self.lang_map.get(selected, "en"))
        # Update flag image
        lang_name = selected.lower()
        try:
            new_img = Image.open(resource_path(f"flags/{lang_name}.jpg"))
            self.flag_image = ctk.CTkImage(new_img, size=(25, 20))
            self.flag_label.configure(image=self.flag_image)
        except FileNotFoundError:
            # print(f"[!] Aucune image trouvée pour '{lang_name}'")
            pass

    def render_page(self, force=False):
        page = self.doc[self.page_index]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        if not force:
            self.scale = 800 / pix.width

        scaled_width = int(pix.width * self.scale)
        scaled_height = int(pix.height * self.scale)
        img = img.resize((scaled_width, scaled_height))
        self.display_img = img

        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        self.canvas.image = self.tk_img
        self.canvas.config(scrollregion=(0, 0, scaled_width, scaled_height))

        total_pages = len(self.doc)
        self.page_entry_var.set(f"{self.page_index + 1} / {total_pages}")

        # Style bouton ajout de zone
        if self.selection_mode:
            self.button_add.configure(fg_color=self.button_add.cget("hover_color"))
        else:
            self.button_add.configure(fg_color="transparent")

        # Affichage visuel des rectangles sur le canvas
        for i, zone in enumerate(self.zones.get(self.page_index, [])):
            x0, y0, x1, y1 = [int(v * self.scale) for v in zone["rect"]]
            item_id = self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=2)
            text_id = self.canvas.create_text(x0 + 5, y0 + 5, anchor="nw", text=str(zone.get("id", i + 1)), fill="red", font=("Arial", 12, "bold"))

            zone["canvas_id"] = item_id
            zone["canvas_id_text"] = text_id

        self.canvas.focus_set()

        # 🔑 Étapes importantes liées aux widgets :
        self.ensure_zone_ids()          # s'assurer que toutes les zones ont un ID global
        self.cleanup_zone_panel()       # retirer les widgets de la page précédente
        self.display_zones()            # afficher les widgets pour la page courante

        
    def ensure_zone_ids(self, page_index=None):
        """Assure que chaque zone du document a un ID unique global."""
        page = page_index if page_index is not None else self.page_index
        for z in self.zones.get(page, []):
            if "id" not in z:
                z["id"] = self.zone_id_counter
                self.zone_id_counter += 1

    def ouvrir_dossier_export(self):
        export_dir = os.path.join(os.getcwd(), "trads")
        try:
            if platform.system() == "Windows":
                os.startfile(export_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", export_dir])
            else:  # Linux / Unix
                subprocess.Popen(["xdg-open", export_dir])
        except Exception as e:
            messagebox.showerror(
                "Erreur", f"Impossible d’ouvrir le dossier :\n{str(e)}")

    def go_to_page(self, event=None):
        try:
            user_input = self.page_entry_var.get()
            # pages are 0-indexed
            page_num = int(user_input.split("/")[0].strip()) - 1

            if 0 <= page_num < len(self.doc):
                self.page_index = page_num
                self.render_page()
            else:
                messagebox.showwarning(
                    "Page invalide", f"Entrez un numéro entre 1 et {len(self.doc)}")
        except ValueError:
            messagebox.showwarning(
                "Entrée invalide", "Veuillez entrer un numéro de page valide.")

    def update_theme(self, new_theme):
        self.current_theme = new_theme
        self.text_color = "black" if new_theme == "light" else "white"

        for btn in [
            self.button_prev, self.button_next, self.button_add,
            self.button_export, self.button_app,
            self.zoom_in_button, self.zoom_out_button
        ]:
            btn.configure(text_color=self.text_color)

        for frame in self.zone_panel.winfo_children():
            for widget in frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for b in widget.winfo_children():
                        if isinstance(b, ctk.CTkButton):
                            b.configure(text_color=self.text_color)

    def zoom_in(self):
        self.scale = min(3.0, self.scale + 0.1)
        self.render_page(force=True)

    def zoom_out(self):
        self.scale = max(0.2, self.scale - 0.1)
        self.render_page(force=True)

    def clear_removed_zone_widgets(self):
        current_ids = {z["id"] for z in self.zones.get(self.page_index, [])}
        existing = self.zone_widgets.get(self.page_index, {})

        # Supprimer seulement les widgets de zones qui n'existent plus
        for zone_id in list(existing):
            if zone_id not in current_ids:
                existing[zone_id].destroy()
                del existing[zone_id]

    @threaded
    def display_zones(self):
        if self.page_index not in self.zones:
            self.zones[self.page_index] = []

        self.ensure_zone_ids()

        if not hasattr(self, "zone_widgets"):
            self.zone_widgets = {}

        # Nettoyer les widgets des autres pages
        self.cleanup_zone_panel()

        # --- Définir la fonction AVANT de l'utiliser ---
        def create_zone_ui(zone_data):
            zid = zone_data["id"]
            frame = ctk.CTkFrame(self.zone_panel)
            frame.pack(padx=5, pady=5, fill="x")
            self.zone_widgets[zid] = frame  # attacher ce widget à l'ID

            label = ctk.CTkLabel(frame, text=f"Zone {zid} - {zone_data['rect']}")
            label.pack(anchor="w", padx=5)

            textbox = ctk.CTkTextbox(frame, height=100)
            textbox.insert("1.0", zone_data["text"])
            textbox.edit_modified(False)
            textbox.pack(fill="x", padx=5)

            btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
            btn_frame.pack(pady=4)

            def update_zone():
                new_text = textbox.get("1.0", "end").strip()
                for i, z in enumerate(self.zones[self.page_index]):
                    if z.get("id") == zid:
                        self.zones[self.page_index][i]["text"] = new_text
                        break

            def translate_zone():
                txt = textbox.get("1.0", "end").strip()
                translated = self.translator.translate(txt)
                textbox.delete("1.0", "end")
                textbox.insert("1.0", translated)
                update_zone()
                if save_btn.winfo_exists():
                    save_btn.configure(fg_color="skyblue")

            def delete_zone():
                for z in self.zones[self.page_index]:
                    if z.get("id") == zid:
                        if "canvas_id" in z:
                            self.canvas.delete(z["canvas_id"])
                        if "canvas_id_text" in z:
                            self.canvas.delete(z["canvas_id_text"])
                        break

                self.zones[self.page_index] = [z for z in self.zones[self.page_index] if z.get("id") != zid]
                frame.destroy()
                if zid in self.zone_widgets:
                    del self.zone_widgets[zid]
                self.render_page(force=True)

            def on_text_modified(event=None):
                if textbox.edit_modified():
                    print(f"[Zone {zid}] Texte modifié.")
                    zone_data["save_status"] = "edited"
                    save_btn.configure(fg_color=color_map["edited"])
                    textbox.edit_modified(False)
                    
            def mark_as_saved():
                zone_data["save_status"] = "saved"
                save_btn.configure(fg_color=color_map["saved"])
                    
            #Bouton de sauvegarde
            
            color_map = {
                "saved": "red",       
                "edited": "skyblue", # bleu par défaut
                }

            status = zone_data.get("save_status", "edited")
            initial_color = color_map.get(status, "skyblue")
            
            save_btn = ctk.CTkButton(
            btn_frame,
            text="⚿",
            text_color=self.text_color,
            font=("Franklin Gothic Medium", 30),
            width=30,
            fg_color=initial_color,
            command=lambda: mark_as_saved()
        )
            save_btn.pack(side="left", padx=2)
            zone_data["save_button"] = save_btn

            ctk.CTkButton(
            btn_frame,
            text="🗫",
            text_color=self.text_color,
            font=("Franklin Gothic Medium", 30),
            command=translate_zone,
            width=90,
            fg_color="skyblue",
        ).pack(side="left", padx=2)

            ctk.CTkButton(
            btn_frame,
            text="⛝",
            text_color=self.text_color,
            font=("Franklin Gothic Medium", 30),
            command=delete_zone,
            width=90,
            fg_color="skyblue",
        ).pack(side="left", padx=2)

            textbox.bind("<<Modified>>", on_text_modified)

        # --- Boucle sur les zones de la page actuelle ---
        for zone in self.zones[self.page_index]:
            zid = zone["id"]
            if zid in self.zone_widgets:
                continue  # déjà affiché
            create_zone_ui(zone)

    def cleanup_zone_panel(self):
        """Supprime les widgets de zones qui ne sont pas sur la page active."""
        to_remove = []
        for zid, frame in self.zone_widgets.items():
            for page, zones in self.zones.items():
                if any(z.get("id") == zid for z in zones):
                    if page != self.page_index:
                        frame.destroy()
                        to_remove.append(zid)
                    break
        for zid in to_remove:
            del self.zone_widgets[zid]


    def activate_selection(self):
        self.selection_mode = not self.selection_mode  # toggle logique

        if self.selection_mode:
            self.button_add.configure(
                fg_color=self.button_add.cget("hover_color"))
        else:
            self.button_add.configure(fg_color="transparent")

    def on_click(self, event):
        if not self.selection_mode:
            return
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_drag(self, event):
        if self.selection_mode and self.rect:
            self.canvas.coords(self.rect, self.start_x,
                               self.start_y, event.x, event.y)

    def on_release(self, event):
        if not self.selection_mode:
            return
        # Ne PAS désactiver ici !
        # self.selection_mode = False  ← À retirer
        x0, x1 = sorted([int(self.start_x / self.scale),
                        int(event.x / self.scale)])
        y0, y1 = sorted([int(self.start_y / self.scale),
                        int(event.y / self.scale)])

        if abs(x1 - x0) < 5 or abs(y1 - y0) < 5:
            return

        pix = self.doc[self.page_index].get_pixmap()
        img = Image.frombytes(
            "RGB", [pix.width, pix.height], pix.samples).convert("RGB")
        cropped = img.crop((x0, y0, x1, y1))
        text = pytesseract.image_to_string(
            cropped, lang=self.ocr_lang_code).strip()

        if not text:
            messagebox.showinfo("Aucun texte", "OCR n'a rien trouvé.")
            if self.rect:
                self.canvas.delete(self.rect)
                self.rect = None
            return

        if self.page_index not in self.zones:
            self.zones[self.page_index] = []

        rect_id = self.canvas.create_rectangle(
            x0 * self.scale, y0 * self.scale, x1 * self.scale, y1 * self.scale, outline="red", width=2)
        self.canvas.tag_bind(rect_id, "<Button-1>", self.on_zone_click)

        self.zones[self.page_index].append({
            "rect": (x0, y0, x1, y1),
            "text": text,
            "canvas_id": rect_id  # <- on garde une référence vers l'objet Canvas
        })
            
        self.ensure_zone_ids()
        self.render_page(force=True)

    def prev_page(self):
        if self.page_index > 0:
            self.page_index -= 1
            self.render_page()

    def next_page(self):
        if self.page_index < len(self.doc) - 1:
            self.page_index += 1
            self.render_page()

    def sanitize(self, text):
        # Nettoyage du texte sans supprimer les retours à la ligne
        text = unicodedata.normalize("NFKD", text)
        return ''.join(c for c in text if c == '\n' or unicodedata.category(c)[0] != 'C')

    def get_contrasting_text_color(self, rgb):
        r, g, b = rgb
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        return (0, 0, 0) if luminance > 186 else (1, 1, 1)

    def lighten(self, color, factor=0.6):
        return tuple(min(1.0, c + (1.0 - c) * factor) for c in color)

    def get_dominant_color_ignore_dark(self, image):
        from collections import Counter
        pixels = list(image.getdata())
        filtered = [px for px in pixels if sum(px) / 3 > 50]
        if not filtered:
            return (240, 240, 240)
        return Counter(filtered).most_common(1)[0][0]

    def find_max_fontsize_that_fits(self, page, bbox, text, fontname="helv", max_fontsize=14, min_fontsize=6):
        """
        Essaie les tailles de police décroissantes pour trouver celle qui permet de faire
        rentrer le texte dans la bbox (hauteur comprise).
        """
        for fontsize in range(max_fontsize, min_fontsize - 1, -1):
            # Crée une zone test à hauteur = bbox.height mais en position (0, 0)
            test_rect = fitz.Rect(0, 0, bbox.width, bbox.height)
            bottom_y = page.insert_textbox(
                test_rect,
                text.strip(),
                fontname=fontname,
                fontsize=fontsize,
                render_mode=3
            )
            text_height = bottom_y - test_rect.y0

            if text_height <= bbox.height and text_height > 0:
                return fontsize
        return min_fontsize

    @threaded
    def export_pdf(self):
        base_name = self.original_name
        langue = self.trad_lang_map.get().strip().lower()
        langue_safe = unicodedata.normalize('NFKD', langue).encode('ASCII', 'ignore').decode()

        output_dir = os.path.join(os.getcwd(), "trads")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"{base_name}_{langue_safe}_OCR.pdf"
        output_path = os.path.join(output_dir, output_filename)

        doc_out = fitz.open()
        font_sizes = []

        all_zones_by_page = {}

        # Étape 1 — Collecter et copier chaque page UNE FOIS
        for i, page in enumerate(self.doc):
            zones = self.zones.get(i, [])
            new_page = doc_out.new_page(width=page.rect.width, height=page.rect.height)

            # Insérer le contenu de fond (rendu image)
            pix = page.get_pixmap()
            img = fitz.Pixmap(pix, 0) if pix.alpha else pix
            new_page.insert_image(new_page.rect, pixmap=img)

            if not zones:
                continue

            all_zones_by_page[i] = []

            for zone in zones:
                bbox = fitz.Rect(*zone["rect"])
                text = self.sanitize(zone["text"])
                fontsize = self.find_max_fontsize_that_fits(new_page, bbox, text)
                font_sizes.append(fontsize)
                all_zones_by_page[i].append((bbox, text, fontsize))

        if not font_sizes:
            messagebox.showinfo("Aucune zone", "Aucune zone à exporter.")
            return

        global_fontsize = min(font_sizes)

        # Étape 2 — Insertion de texte traduit
        for i, page in enumerate(doc_out):
            if i not in all_zones_by_page:
                continue

            zones = all_zones_by_page[i]

            pix = page.get_pixmap()
            full_image_color = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            dominant_rgb = self.get_dominant_color_ignore_dark(full_image_color)
            fill_color = self.lighten(tuple(c / 255 for c in dominant_rgb), 0.6)
            text_color = self.get_contrasting_text_color(dominant_rgb)

            for bbox, text, _ in zones:
                fontsize = global_fontsize
                if fontsize < 6:
                    continue

                page.draw_rect(bbox, fill=fill_color, color=None)
                page.insert_textbox(
                    bbox,
                    text.strip(),
                    fontsize=fontsize,
                    fontname="helv",
                    color=text_color,
                    align=0,
                    render_mode=0
                )

        doc_out.save(output_path)
        messagebox.showinfo("Export réussi", f"Exporté vers :\n{output_path}")


    def bring_main_to_front(self):
        try:
            self.master.deiconify()
            self.master.lift()
            self.master.focus_force()
        except:
            pass

    def on_close(self, evt):
        if evt.widget == self:
            ThemeManager.unregister(self.update_theme)
