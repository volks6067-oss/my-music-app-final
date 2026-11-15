import customtkinter as ctk
import pygame
import os
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD

# Инициализация звука
pygame.mixer.init()

# Кастомный класс, который объединяет CustomTkinter и поддержку Drag&Drop
class MusicApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self) # Активация Drag&Drop
        
        self.title("VOLK MUSIC PLAYER")
        self.geometry("1000x700")
        self.configure(fg_color="#0a0a14")
        
        self.tracks = []
        self.current_index = -1
        self.is_playing = False

        self.setup_ui()

    def setup_ui(self):
        # --- ЛЕВАЯ ПАНЕЛЬ ---
        self.sidebar = ctk.CTkFrame(self, width=380, corner_radius=0, fg_color="#12121e")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Заголовок и кнопка +
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="ПЛЕЙЛИСТ", font=ctk.CTkFont(size=20, weight="bold"), text_color="#00f3ff").pack(side="left")
        
        self.add_btn = ctk.CTkButton(
            header_frame, text="+", width=40, height=40, 
            fg_color="#00f3ff", text_color="black", hover_color="#00c3cc", 
            font=ctk.CTkFont(size=24, weight="bold"),
            command=self.open_add_modal
        )
        self.add_btn.pack(side="right")

        # Строка поиска
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_playlist)
        self.search_entry = ctk.CTkEntry(
            self.sidebar, textvariable=self.search_var, 
            placeholder_text="Поиск трека...", 
            fg_color="#1a1a24", border_color="#2a2a3e", 
            text_color="white"
        )
        self.search_entry.pack(fill="x", padx=15, pady=(0, 15))

        # Скролл-фрейм для треков
        self.scroll_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # --- ПРАВАЯ ПАНЕЛЬ (ПЛЕЕР) ---
        self.main_frame = ctk.CTkFrame(self, fg_color="#0a0a14")
        self.main_frame.pack(side="right", fill="both", expand=True)

        self.cover_label = ctk.CTkLabel(self.main_frame, text="🎵", font=ctk.CTkFont(size=120), fg_color="#1a1a24", corner_radius=150, width=250, height=250)
        self.cover_label.pack(pady=(60, 20))

        self.title_label = ctk.CTkLabel(self.main_frame, text="Ничего не играет", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(pady=5)
        
        self.artist_label = ctk.CTkLabel(self.main_frame, text="Перетащи музыку в окно", text_color="gray", font=ctk.CTkFont(size=18))
        self.artist_label.pack(pady=5)

        self.controls_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.controls_frame.pack(pady=40)

        ctk.CTkButton(self.controls_frame, text="⏮", width=60, height=60, fg_color="transparent", font=ctk.CTkFont(size=30), command=self.prev_track).pack(side="left", padx=20)
        self.play_btn = ctk.CTkButton(self.controls_frame, text="▶", width=80, height=80, fg_color="#00f3ff", text_color="black", font=ctk.CTkFont(size=36), hover_color="#00c3cc", command=self.toggle_play)
        self.play_btn.pack(side="left", padx=20)
        ctk.CTkButton(self.controls_frame, text="⏭", width=60, height=60, fg_color="transparent", font=ctk.CTkFont(size=30), command=self.next_track).pack(side="left", padx=20)

    # --- ОКНО ДОБАВЛЕНИЯ ---
    def open_add_modal(self):
        self.modal = ctk.CTkToplevel(self)
        self.modal.title("Добавить музыку")
        self.modal.geometry("500x400")
        self.modal.configure(fg_color="#12121e")
        self.modal.attributes("-topmost", True)
        self.modal.grab_set() # Блокирует главное окно, пока открыто это

        ctk.CTkLabel(self.modal, text="Добавление треков", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        # Зона для перетаскивания
        self.drop_zone = ctk.CTkFrame(self.modal, fg_color="#1a1a24", border_width=2, border_color="#2a2a3e", corner_radius=15, height=150)
        self.drop_zone.pack(fill="x", padx=30, pady=10)
        
        # Настраиваем зону как цель для Drag&Drop
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.drop_files)

        self.drop_label = ctk.CTkLabel(self.drop_zone, text="Перетащи сюда MP3 файлы", font=ctk.CTkFont(size=16), text_color="gray")
        self.drop_label.pack(expand=True)

        ctk.CTkButton(self.modal, text="Или выбери вручную", fg_color="#2a2a3e", hover_color="#3a3a4e", command=self.select_files).pack(pady=15)

    def drop_files(self, event):
        # Получаем список файлов из события перетаскивания
        files = self.tk.splitlist(event.data)
        valid_files = [f for f in files if f.lower().endswith(('.mp3', '.wav', '.ogg'))]
        
        for file_path in valid_files:
            self.add_single_track(file_path)
            
        self.render_playlist()
        if self.current_index == -1 and self.tracks:
            self.load_track(0)
        self.modal.destroy()

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
        if files:
            for file_path in files:
                self.add_single_track(file_path)
            self.render_playlist()
            if self.current_index == -1 and self.tracks:
                self.load_track(0)
            self.modal.destroy()

    def add_single_track(self, path):
        filename = os.path.basename(path)
        name = os.path.splitext(filename)[0]
        
        artist = "Неизвестный исполнитель"
        title = name
        
        if " - " in name:
            parts = name.split(" - ", 1)
            artist = parts[0]
            title = parts[1]

        self.tracks.append({"path": path, "title": title, "artist": artist})

    def render_playlist(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        search_query = self.search_var.get().lower()

        for i, track in enumerate(self.tracks):
            if search_query not in track['title'].lower() and search_query not in track['artist'].lower():
                continue

            color = "#1f1f2e" if i == self.current_index else "transparent"
            btn = ctk.CTkButton(
                self.scroll_frame, 
                text=f"{track['title']}\n{track['artist']}", 
                fg_color=color, 
                hover_color="#2a2a3e", 
                anchor="w",
                font=ctk.CTkFont(size=14),
                command=lambda idx=i: self.load_track(idx)
            )
            btn.pack(fill="x", pady=2)

    def filter_playlist(self, *args):
        self.render_playlist()

    # --- УПРАВЛЕНИЕ ---
    def load_track(self, index, play_after=False):
        if not self.tracks: return
        self.current_index = index
        track = self.tracks[index]
        
        self.title_label.configure(text=track["title"])
        self.artist_label.configure(text=track["artist"])
        self.render_playlist()

        try:
            pygame.mixer.music.load(track["path"])
            if play_after:
                self.play_audio()
            else:
                self.is_playing = False
                self.play_btn.configure(text="▶")
        except Exception as e:
            print(f"Ошибка: {e}")

    def toggle_play(self):
        if not self.tracks: return
        if self.is_playing:
            pygame.mixer.music.pause()
            self.play_btn.configure(text="▶")
            self.is_playing = False
        else:
            self.play_audio()

    def play_audio(self):
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            self.play_btn.configure(text="⏸")
            self.is_playing = True
        except Exception as e:
            print(f"Ошибка: {e}")

    def next_track(self):
        if not self.tracks: return
        next_idx = (self.current_index + 1) % len(self.tracks)
        self.load_track(next_idx, play_after=True)

    def prev_track(self):
        if not self.tracks: return
        prev_idx = (self.current_index - 1) % len(self.tracks)
        self.load_track(prev_idx, play_after=True)

if __name__ == "__main__":
    app = MusicApp()
    app.mainloop()
