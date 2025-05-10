import json
import customtkinter as ctk
from tkinterweb import HtmlFrame
from PIL import Image, ImageTk
import certifi
import ssl
import urllib.request
import io

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BrowserTab(ctk.CTkFrame):
    def __init__(self, notebook, url=None):
        super().__init__(notebook)
        self.history = []
        self.history_position = -1

        self.html_frame = HtmlFrame(self)
        self.html_frame.pack(fill="both", expand=True, padx=2, pady=2)

        if url:
            self.load_url(url)

    def load_url(self, url):
        try:
            self.html_frame.load_website(url)
            self.update_history(url)
            self.master.master.update_tab_title(self)
        except Exception as e:
            self.show_error(f"Failed to load {url}\n{str(e)}")

    def show_error(self, message):
        self.html_frame.load_html(f"<h2 style='color:red'>{message}</h2>")

    def update_history(self, url):
        if not self.history or self.history[self.history_position] != url:
            if self.history_position < len(self.history) - 1:
                self.history = self.history[:self.history_position+1]
            self.history.append(url)
            self.history_position += 1

    def back(self):
        if self.history_position > 0:
            self.history_position -= 1
            self.html_frame.load_website(self.history[self.history_position])

    def forward(self):
        if self.history_position < len(self.history) - 1:
            self.history_position += 1
            self.html_frame.load_website(self.history[self.history_position])

class ByteBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("Byte Search Engine (Beta) 2025")
        self.root.geometry("1200x800")

        self.tab_counter = 1  # <-- Robust tab counter

        self.websites = self.load_websites()
        self.web_db = self.load_web_db()
        self.create_ui()
        self.create_home_tab()
        self.set_window_icon()

    def load_websites(self):
        with open("websites.txt", "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]

    def load_web_db(self):
        with open("web_db.txt", "r", encoding="utf-8") as file:
            return json.load(file)

    def create_ui(self):
        nav_frame = ctk.CTkFrame(self.root)
        nav_frame.pack(side="top", fill="x", padx=8, pady=6)

        self.back_btn = ctk.CTkButton(nav_frame, text="←", width=40, command=self.navigate_back)
        self.back_btn.pack(side="left", padx=2)

        self.forward_btn = ctk.CTkButton(nav_frame, text="→", width=40, command=self.navigate_forward)
        self.forward_btn.pack(side="left", padx=2)

        self.refresh_btn = ctk.CTkButton(nav_frame, text="↻", width=40, command=self.refresh_page)
        self.refresh_btn.pack(side="left", padx=2)

        self.url_entry = ctk.CTkEntry(nav_frame, width=600, font=("Arial", 16))
        self.url_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.url_entry.bind("<Return>", lambda e: self.perform_search())
        self.url_entry.bind("<Alt_L>", self.on_alt_press)
        self.url_entry.bind("<Alt_R>", self.on_alt_press)

        self.search_btn = ctk.CTkButton(nav_frame, text="Search", width=80, command=self.perform_search)
        self.search_btn.pack(side="left", padx=2)

        new_tab_btn = ctk.CTkButton(nav_frame, text="+", width=40, command=self.new_tab)
        new_tab_btn.pack(side="right", padx=2)

        self.notebook = ctk.CTkTabview(self.root, width=1200, height=760, segmented_button_selected_color="#2a7cff")
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

    def perform_search(self):
        query = self.url_entry.get().lower()
        if not query:
            return

        wp = {site: 0 for site in self.websites}
        words = query.split()

        for word in words:
            for site in self.websites:
                if word in self.web_db.get(site, "").lower():
                    wp[site] += 1

        if wp:
            best_match = max(wp, key=wp.get)
            self.load_url(url=best_match)
        else:
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, "No matches found.")

    def on_alt_press(self, event):
        url = self.url_entry.get()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.load_url(url=url)
        return "break"

    def create_home_tab(self):
        self.new_tab("")

    def new_tab(self, url=None):
        tab_name = f"Tab {self.tab_counter}"
        self.tab_counter += 1
        self.notebook.add(tab_name)
        tab = BrowserTab(self.notebook.tab(tab_name), url)
        tab.pack(fill="both", expand=True)
        self.notebook.set(tab_name)
        return tab

    def get_current_tab(self):
        tab_name = self.notebook.get()
        tab_container = self.notebook.tab(tab_name)
        for child in tab_container.winfo_children():
            if isinstance(child, BrowserTab):
                return child
        return None

    def load_url(self, event=None, url=None):
        if url is None:
            url = self.url_entry.get()
        tab = self.get_current_tab()
        if tab:
            tab.load_url(url)
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, url)
        self.update_tab_title(tab)

    def navigate_back(self):
        tab = self.get_current_tab()
        if tab:
            tab.back()
            self.update_url_entry()

    def navigate_forward(self):
        tab = self.get_current_tab()
        if tab:
            tab.forward()
            self.update_url_entry()

    def refresh_page(self):
        tab = self.get_current_tab()
        if tab and tab.history:
            tab.load_url(tab.history[tab.history_position])
            self.update_url_entry()

    def update_tab_title(self, tab):
        if not tab:
            return
        try:
            title = tab.html_frame.title
            if not title:
                title = tab.history[tab.history_position]
        except Exception:
            title = tab.history[tab.history_position] if tab.history else "New Tab"
        if len(title) > 30:
            title = title[:30] + "..."
        tab_name = self.notebook.get()
        self.notebook.tab(tab_name, text=title)

    def update_url_entry(self):
        tab = self.get_current_tab()
        if tab and tab.history:
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, tab.history[tab.history_position])

    def set_window_icon(self):
        try:
            logo_url = "https://img.freepik.com/free-photo/magnifying-glass_1156-674.jpg"
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(logo_url, context=ssl_context) as u:
                raw_data = u.read()
            image = Image.open(io.BytesIO(raw_data))
            icon_size = (32, 32)
            resample = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS
            image = image.resize(icon_size, resample)
            photo = ImageTk.PhotoImage(image)
            self.root.iconphoto(False, photo)
        except Exception as e:
            print(f"Error loading icon: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    browser = ByteBrowser(root)
    root.mainloop()
