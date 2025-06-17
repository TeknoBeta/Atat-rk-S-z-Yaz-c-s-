import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, ttk
from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageGrab

import os
import sys

class AtaturkSozYapici:
    # resource_path fonksiyonunu bir sınıf metodu olarak tanımladık
    def resource_path(self, relative_path): # self parametresini ekledik
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def __init__(self, root):
        self.root = root
        self.root.title("Atatürk Söz Yapıcı")
        self.root.geometry("1000x650")
        self.root.config(bg="white")

        # Görseller ve Renkler
        # Artık self.resource_path() olarak çağırıyoruz
        self.default_ataturk_images = [self.resource_path(f"images/ataturk{i}.png") for i in range(1, 5)]
        self.ataturk_images = list(self.default_ataturk_images)
        self.current_img_index = 0

        self.bg_colors = ["#d3d3d3", "#ffffff"]
        self.current_bg_index = 0

        self.custom_bg_color = None
        self.custom_bg_path = None
        self.custom_ataturk_path = None

        self.include_signature = tk.BooleanVar(value=True)
        self.text_color = "black"
        self.font_size = tk.IntVar(value=24)

        # Font ayarı
        try:
            self.font = ImageFont.truetype("arial.ttf", self.font_size.get())
        except IOError:
            try:
                self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", self.font_size.get())
            except IOError:
                self.font = ImageFont.load_default()
                messagebox.showwarning("Font Hatası", "Arial veya DejaVuSans-Bold fontu bulunamadı. Varsayılan font kullanılacak.")

        # Sürükle-bırak için değişkenler
        self.draggable_item = None
        self.offset_x = 0
        self.offset_y = 0

        # Başlangıç konumları (Canvas'a göre)
        self.ataturk_pos = (30, 50)
        self.signature_pos = (420, 310)

        # Sol Panel
        self.create_left_panel()

        # Sağ Önizleme Alanı
        self.preview_canvas = tk.Canvas(self.root, width=600, height=400, bg="white", highlightthickness=0)
        self.preview_canvas.place(x=350, y=50)

        # Sürükle-bırak olayları bağlandı
        self.preview_canvas.bind("<Button-1>", self.on_press)
        self.preview_canvas.bind("<B1-Motion>", self.on_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_release)

        # Önizleme görseli
        self.update_preview()

    def create_left_panel(self):
        panel = tk.Frame(self.root, bg="gray", width=330, height=630)
        panel.place(x=10, y=10)

        # Metin kutusu
        tk.Label(panel, text="Yazacak Metin:", bg="gray", fg="white").pack(pady=5)
        text_frame = tk.Frame(panel)
        text_frame.pack(pady=5)
        self.text_widget = tk.Text(text_frame, width=35, height=8, wrap="word")
        self.text_widget.insert("1.0", "Vatanını en çok seven, görevini en iyi yapandır. Ne mutlu Türk'üm diyene!")
        self.text_widget.pack(side="left", fill="y")

        text_scrollbar = ttk.Scrollbar(text_frame, command=self.text_widget.yview)
        text_scrollbar.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=text_scrollbar.set)

        self.text_widget.bind("<KeyRelease>", lambda e: self.update_preview())

        # Metin Özelleştirme
        tk.Label(panel, text="<Metin Özellikleri>", bg="gray", fg="white").pack(pady=10)

        font_size_frame = tk.Frame(panel, bg="gray")
        font_size_frame.pack()
        tk.Label(font_size_frame, text="Font Boyutu:", bg="gray", fg="white").pack(side="left")
        self.font_size_slider = tk.Scale(font_size_frame, from_=16, to=48, orient="horizontal",
                                         variable=self.font_size, command=self.update_font_size, bg="gray", fg="white", highlightthickness=0)
        self.font_size_slider.pack(side="left", padx=5)

        tk.Button(panel, text="Metin Rengi Seç", command=self.choose_text_color).pack(pady=5)

        # Atatürk Görseli
        tk.Label(panel, text="<Atatürk Görseli Ayarları>", bg="gray", fg="white").pack(pady=10)
        ataturk_btns = tk.Frame(panel, bg="gray")
        ataturk_btns.pack()
        tk.Button(ataturk_btns, text="<< Önceki", command=self.prev_ataturk).pack(side="left", padx=5)
        tk.Button(ataturk_btns, text="Sonraki >>", command=self.next_ataturk).pack(side="right", padx=5)
        tk.Button(panel, text="Kendi Görselini Yükle", command=self.load_custom_ataturk).pack(pady=5)

        # Arka Plan Rengi
        tk.Label(panel, text="<Arka Plan Ayarları>", bg="gray", fg="white").pack(pady=10)
        bg_btns = tk.Frame(panel, bg="gray")
        bg_btns.pack()
        tk.Button(bg_btns, text="<< Renk", command=self.prev_bg).pack(side="left", padx=5)
        tk.Button(bg_btns, text="Renk >>", command=self.next_bg).pack(side="right", padx=5)
        tk.Button(panel, text="Arka Plan Rengi Seç", command=self.choose_custom_background_color).pack(pady=5)
        tk.Button(panel, text="Kendi Arka Planını Yükle", command=self.load_custom_background).pack(pady=5)

        # İmza kutusu
        self.signature_check = tk.Checkbutton(panel, text="İmza Ekle?", bg="gray", variable=self.include_signature, command=self.update_preview, fg="white", selectcolor="gray")
        self.signature_check.select()
        self.signature_check.pack(pady=15)

        # Reset Butonu
        tk.Button(panel, text="Ayarları Sıfırla", command=self.reset_settings).pack(pady=10)

        # İndir Butonu
        tk.Button(panel, text="İndir", command=self.save_image, font=("Arial", 14, "bold")).pack(pady=20)

    def update_font_size(self, val=None):
        try:
            self.font = ImageFont.truetype("arial.ttf", self.font_size.get())
        except IOError:
            try:
                self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", self.font_size.get())
            except IOError:
                self.font = ImageFont.load_default()
        self.update_preview()

    def choose_text_color(self):
        color_code = colorchooser.askcolor(title="Metin Rengi Seç")
        if color_code and color_code[1]:
            self.text_color = color_code[1]
            self.update_preview()

    def choose_custom_background_color(self):
        color_code = colorchooser.askcolor(title="Arka Plan Rengi Seç")
        if color_code and color_code[1]:
            self.custom_bg_color = color_code[1]
            self.custom_bg_path = None
            self.update_preview()

    def load_custom_background(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Resim Dosyaları", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")],
            title="Arka Plan Görseli Seç"
        )
        if file_path:
            self.custom_bg_path = file_path
            self.custom_bg_color = None
            self.update_preview()
        else:
            self.custom_bg_path = None
            self.update_preview()

    def load_custom_ataturk(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Resim Dosyaları", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")],
            title="Atatürk Görseli Seç"
        )
        if file_path:
            self.custom_ataturk_path = file_path
            self.ataturk_images = [file_path]
            self.current_img_index = 0
            self.update_preview()
        else:
            self.custom_ataturk_path = None
            # resource_path() fonksiyonunu kullanarak yolları güncelleyin
            self.ataturk_images = [self.resource_path(f"images/ataturk{i}.png") for i in range(1, 5)]
            self.current_img_index = 0
            self.update_preview()

    def reset_settings(self):
        self.current_img_index = 0
        self.current_bg_index = 0
        self.include_signature.set(True)
        self.text_color = "black"
        self.font_size.set(24)
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", "Vatanını en çok seven, görevini en iyi yapandır. Ne mutlu Türk'üm diyene!")
        self.custom_bg_path = None
        self.custom_bg_color = None
        self.custom_ataturk_path = None
        # resource_path() fonksiyonunu kullanarak yolları güncelleyin
        self.ataturk_images = [self.resource_path(f"images/ataturk{i}.png") for i in range(1, 5)]
        self.ataturk_pos = (30, 50)
        self.signature_pos = (420, 310)
        self.update_font_size()
        self.update_preview()
        messagebox.showinfo("Bilgi", "Tüm ayarlar sıfırlandı.")

    def prev_ataturk(self):
        if not self.custom_ataturk_path:
            self.current_img_index = (self.current_img_index - 1) % len(self.ataturk_images)
            self.update_preview()
        else:
            messagebox.showinfo("Bilgi", "Kendi görselinizi yüklediğiniz için ileri/geri seçeneği devre dışıdır. Sıfırlayarak varsayılan görsellere dönebilirsiniz.")


    def next_ataturk(self):
        if not self.custom_ataturk_path:
            self.current_img_index = (self.current_img_index + 1) % len(self.ataturk_images)
            self.update_preview()
        else:
            messagebox.showinfo("Bilgi", "Kendi görselinizi yüklediğiniz için ileri/geri seçeneği devre dışıdır. Sıfırlayarak varsayılan görsellere dönebilirsiniz.")

    def prev_bg(self):
        self.current_bg_index = (self.current_bg_index - 1) % len(self.bg_colors)
        self.custom_bg_path = None
        self.custom_bg_color = None
        self.update_preview()

    def next_bg(self):
        self.current_bg_index = (self.current_bg_index + 1) % len(self.bg_colors)
        self.custom_bg_path = None
        self.custom_bg_color = None
        self.update_preview()

    def on_press(self, event):
        x, y = event.x, event.y
        items = self.preview_canvas.find_overlapping(x, y, x, y)

        ataturk_id = getattr(self, 'ataturk_canvas_id', None)
        if ataturk_id and ataturk_id in items:
            self.draggable_item = 'ataturk'
            self.offset_x = x - self.ataturk_pos[0]
            self.offset_y = y - self.ataturk_pos[1]
            self.preview_canvas.config(cursor="fleur")
            return

        signature_id = getattr(self, 'signature_canvas_id', None)
        if signature_id and signature_id in items:
            self.draggable_item = 'signature'
            self.offset_x = x - self.signature_pos[0]
            self.offset_y = y - self.signature_pos[1]
            self.preview_canvas.config(cursor="fleur")
            return

        self.draggable_item = None

    def on_drag(self, event):
        if self.draggable_item:
            new_x = event.x - self.offset_x
            new_y = event.y - self.offset_y

            if self.draggable_item == 'ataturk':
                new_x = max(0, min(new_x, 600 - 250))
                new_y = max(0, min(new_y, 400 - 300))
                self.ataturk_pos = (new_x, new_y)
            elif self.draggable_item == 'signature':
                new_x = max(0, min(new_x, 600 - 150))
                new_y = max(0, min(new_y, 400 - 60))
                self.signature_pos = (new_x, new_y)

            self.update_preview()
            self.preview_canvas.update_idletasks()

    def on_release(self, event):
        self.draggable_item = None
        self.preview_canvas.config(cursor="")

    def wrap_text(self, text, font, max_width):
        lines = []
        words = text.split(' ')
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = self.draw.textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]

            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

                bbox_word = self.draw.textbbox((0,0), word, font=font)
                if bbox_word[2] - bbox_word[0] > max_width and len(word) > 1:
                    split_word = ""
                    for char in word:
                        test_char_line = split_word + char
                        bbox_char = self.draw.textbbox((0,0), test_char_line, font=font)
                        if (bbox_char[2] - bbox_char[0]) <= max_width:
                            split_word += char
                        else:
                            if split_word: lines.append(split_word)
                            split_word = char
                    if split_word: lines.append(split_word)
                    current_line = []
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def update_preview(self):
        bg_color = None
        if self.custom_bg_path and os.path.exists(self.custom_bg_path):
            try:
                bg_image = Image.open(self.custom_bg_path).resize((600, 400), Image.LANCZOS)
                if bg_image.mode != 'RGB':
                    bg_image = bg_image.convert('RGB')
                image = bg_image.copy()
            except Exception as e:
                messagebox.showerror("Hata", f"Özel arka plan görseli yüklenemedi: {e}\nVarsayılan renk kullanılacak.")
                self.custom_bg_path = None
                bg_color = self.bg_colors[self.current_bg_index]
                image = Image.new("RGB", (600, 400), bg_color)
        elif self.custom_bg_color:
            image = Image.new("RGB", (600, 400), self.custom_bg_color)
        else:
            bg_color = self.bg_colors[self.current_bg_index]
            image = Image.new("RGB", (600, 400), bg_color)

        self.draw = ImageDraw.Draw(image)

        ataturk_image_to_use = self.ataturk_images[self.current_img_index]
        try:
            if self.custom_ataturk_path:
                img_path = self.custom_ataturk_path
            else:
                img_path = ataturk_image_to_use # Burası zaten self.resource_path ile oluşturuldu
            
            if os.path.exists(img_path):
                ataturk_img = Image.open(img_path).resize((250, 300), Image.LANCZOS)
                if ataturk_img.mode == 'RGBA':
                    image.paste(ataturk_img, self.ataturk_pos, ataturk_img)
                else:
                    image.paste(ataturk_img, self.ataturk_pos)
            else:
                messagebox.showerror("Hata", f"Atatürk görseli bulunamadı: {img_path}")
        except Exception as e:
            messagebox.showerror("Görsel Yükleme Hatası", f"Atatürk görseli yüklenirken bir hata oluştu: {e}")

        # Metin
        text = self.text_widget.get("1.0", "end-1c")
        max_text_width = 600 - 250 - 50

        wrapped_text_lines = self.wrap_text(text, self.font, max_text_width)

        y_offset = 70
        line_height_tuple = self.font.getmetrics()
        line_height = line_height_tuple[0] + abs(line_height_tuple[1]) + 5

        for line in wrapped_text_lines:
            bbox = self.draw.textbbox((0, 0), line, font=self.font)
            text_width = bbox[2] - bbox[0]
            text_x = self.ataturk_pos[0] + 250 + (max_text_width - text_width) / 2

            self.draw.text((text_x, y_offset), line, font=self.font, fill=self.text_color)
            y_offset += line_height

        # İmza
        if self.include_signature.get():
            try:
                # self.resource_path() fonksiyonunu kullanarak yolları güncelleyin
                imza_path = self.resource_path("images/imza.png")
                if os.path.exists(imza_path):
                    imza = Image.open(imza_path).resize((150, 60), Image.LANCZOS)
                    if imza.mode == 'RGBA':
                        image.paste(imza, self.signature_pos, imza)
                    else:
                        image.paste(imza, self.signature_pos)
                else:
                    messagebox.showerror("Hata", f"İmza görseli bulunamadı: {imza_path}")
            except Exception as e:
                messagebox.showerror("İmza Yükleme Hatası", f"İmza yüklenirken bir hata oluştu: {e}")

        self.current_preview = image
        tk_img = ImageTk.PhotoImage(image)
        self.preview_canvas.delete("all")

        self.preview_canvas.create_image(0, 0, anchor="nw", image=tk_img)
        self.preview_canvas.image = tk_img

        try:
            # Sürükleme için ayrı Atatürk görseli
            if self.custom_ataturk_path:
                ataturk_img_raw = Image.open(self.custom_ataturk_path).resize((250, 300), Image.LANCZOS)
            else:
                ataturk_img_raw = Image.open(ataturk_image_to_use).resize((250, 300), Image.LANCZOS)
                
            self.ataturk_tk_img = ImageTk.PhotoImage(ataturk_img_raw)
            self.ataturk_canvas_id = self.preview_canvas.create_image(self.ataturk_pos[0], self.ataturk_pos[1], anchor="nw", image=self.ataturk_tk_img, tags="draggable_ataturk")
        except Exception:
            self.ataturk_canvas_id = None

        if self.include_signature.get():
            try:
                # Sürükleme için ayrı imza görseli
                # self.resource_path() fonksiyonunu kullanarak yolları güncelleyin
                imza_raw = Image.open(self.resource_path("images/imza.png")).resize((150, 60), Image.LANCZOS)
                self.imza_tk_img = ImageTk.PhotoImage(imza_raw)
                self.signature_canvas_id = self.preview_canvas.create_image(self.signature_pos[0], self.signature_pos[1], anchor="nw", image=self.imza_tk_img, tags="draggable_signature")
            except Exception:
                self.signature_canvas_id = None
        else:
            self.signature_canvas_id = None

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png")],
                                                 title="Kaydedilecek dosya adı:")
        if file_path:
            try:
                self.current_preview.save(file_path)
                messagebox.showinfo("Başarılı", f"Görsel '{os.path.basename(file_path)}' başarıyla kaydedildi!")
            except Exception as e:
                messagebox.showerror("Kaydetme Hatası", f"Görsel kaydedilirken bir hata oluştu: {e}")

if __name__ == "__main__":
    if not os.path.exists("images"):
        os.makedirs("images")
        messagebox.showinfo("Bilgi", "images klasörü oluşturuldu. Lütfen içine ataturk1.png, ataturk2.png, ataturk3.png, ataturk4.png ve imza.png dosyalarını kopyalayın.")

    root = tk.Tk()
    app = AtaturkSozYapici(root)
    root.mainloop()