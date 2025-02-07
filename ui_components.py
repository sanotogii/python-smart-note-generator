import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading

# Import TranscriptionManager after other core imports
from transcription_manager import TranscriptionManager

class TranscriberUI:
    def __init__(self):
        self.setup_window()
        # Initialize TranscriptionManager first
        self.transcription_manager = TranscriptionManager(self)
        self.create_ui_components()

    def setup_window(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.window = TkinterDnD.Tk()
        self.window.title("Video Transcriber")
        self.window.geometry("700x600")
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

    def create_ui_components(self):
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True)
        
        self.create_top_frame()
        self.create_drop_zone()
        self.create_progress_components()

    def create_top_frame(self):
        top_frame = ctk.CTkFrame(self.main_frame)
        top_frame.pack(fill="x")

        # Model selection frame
        model_frame = ctk.CTkFrame(top_frame)
        model_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(model_frame, text="Select Whisper Model:").pack(side="left", padx=10)
        self.model_var = ctk.StringVar(value=self.transcription_manager.model_name)
        self.model_selector = ctk.CTkOptionMenu(
            model_frame,
            variable=self.model_var,
            values=["tiny", "base", "small", "medium", "large"],
            command=self.transcription_manager.on_model_change,
            width=120
        )
        self.model_selector.pack(side="left")

        # Format selection frame
        format_frame = ctk.CTkFrame(top_frame)
        format_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(format_frame, text="Output Format:").pack(side="left", padx=10)
        self.format_var = ctk.StringVar(value="srt")
        formats = ["srt", "txt", "vtt"]
        for fmt in formats:
            ctk.CTkRadioButton(
                format_frame,
                text=fmt.upper(),
                variable=self.format_var,
                value=fmt
            ).pack(side="left", padx=10)

        # Output directory frame
        output_frame = ctk.CTkFrame(top_frame)
        output_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(output_frame, text="Output Directory:").pack(side="left", padx=10)
        self.output_dir_var = ctk.StringVar(value="")
        self.output_dir_entry = ctk.CTkEntry(
            output_frame,
            textvariable=self.output_dir_var,
            width=400
        )
        self.output_dir_entry.pack(side="left", padx=(0, 10))
        
        self.browse_button = ctk.CTkButton(
            output_frame,
            text="Browse",
            command=self.browse_output_dir,
            width=100
        )
        self.browse_button.pack(side="left")

        # State indicators frame
        state_frame = ctk.CTkFrame(top_frame)
        state_frame.pack(fill="x", pady=5)
        
        # Transcription state
        self.transcription_state = ctk.CTkLabel(
            state_frame,
            text="⚪ Transcription: Ready",
            font=("Arial", 12, "bold")
        )
        self.transcription_state.pack(side="left", padx=10)
        
        # Notes generation state
        self.notes_state = ctk.CTkLabel(
            state_frame,
            text="⚪ Notes: Ready",
            font=("Arial", 12, "bold")
        )
        self.notes_state.pack(side="left", padx=10)

    def create_drop_zone(self):
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Drag and drop video files here",
            pady=10
        )
        self.status_label.pack()

        self.drop_zone = ctk.CTkLabel(
            self.main_frame,
            text="Drop Zone",
            fg_color=("gray85", "gray25"),
            width=600,
            height=200,
            corner_radius=6
        )
        self.drop_zone.pack(pady=10)
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.transcription_manager.handle_drop)

    def create_progress_components(self):
        self.progress_label = ctk.CTkLabel(self.main_frame, text="Progress: 0%")
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame,
            width=600,
            height=16,
            corner_radius=6
        )
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)

    def update_status(self, text):
        self.status_label.configure(text=text)

    def update_progress(self, value):
        self.progress_bar.set(value / 100)
        self.progress_label.configure(text=f"Progress: {value}%")

    def update_transcription_state(self, state):
        states = {
            "ready": "⚪ Transcription: Ready",
            "processing": "🟡 Transcription: Processing",
            "completed": "🟢 Transcription: Completed",
            "error": "🔴 Transcription: Error"
        }
        self.transcription_state.configure(text=states.get(state, states["ready"]))

    def update_notes_state(self, state):
        states = {
            "ready": "⚪ Notes: Ready",
            "processing": "🟡 Notes: Processing",
            "completed": "🟢 Notes: Completed",
            "error": "🔴 Notes: Error"
        }
        self.notes_state.configure(text=states.get(state, states["ready"]))

    def run(self):
        self.window.mainloop()
