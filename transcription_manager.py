import whisper
import threading
import time
import os
import re
import json
from utils import format_timestamp
from notes_manager import NotesManager

class TranscriptionManager:
    def __init__(self, ui):
        self.ui = ui
        self.model_name = "small"
        self.model = whisper.load_model(self.model_name)
        self.file_queue = []
        self.processing_queue = False
        self.transcribing = False
        self.progress_value = 0
        try:
            self.notes_manager = NotesManager()
        except Exception as e:
            print(f"Warning: Could not initialize NotesManager: {e}")
            self.notes_manager = None

    def on_model_change(self, new_model):
        if new_model != self.model_name:
            if self.processing_queue or self.transcribing:
                self.ui.update_status("Wait until current transcription completes to switch model.")
                self.ui.model_var.set(self.model_name)
                return
            threading.Thread(target=self.load_new_model, args=(new_model,), daemon=True).start()

    def load_new_model(self, new_model):
        self.ui.update_status(f"Loading {new_model} model...")
        self.model = whisper.load_model(new_model)
        self.model_name = new_model
        self.ui.update_status("Model loaded. Ready for transcription.")

    def handle_drop(self, event):
        file_paths = self.parse_file_list(event.data)
        valid_files = [fp for fp in file_paths if os.path.isfile(fp)]
        if not valid_files:
            self.ui.update_status("No valid files dropped.")
            return

        self.file_queue.extend(valid_files)
        self.ui.update_status(f"{len(valid_files)} file(s) added to queue.")
        
        if not self.processing_queue:
            self.processing_queue = True
            threading.Thread(target=self.process_queue, daemon=True).start()

    def parse_file_list(self, data):
        files = re.findall(r'{([^}]*)}', data)
        if files:
            return files
        return data.split()

    def process_queue(self):
        while self.file_queue:
            file_path = self.file_queue.pop(0)
            self.transcribe_file(file_path)
            time.sleep(1)
        self.processing_queue = False
        self.ui.update_status("All files processed.")

    def transcribe_file(self, file_path):
        base_name = os.path.basename(file_path)
        self.ui.update_status(f"Transcribing: {base_name}")
        self.ui.update_transcription_state("processing")
        
        self.progress_value = 0
        self.transcribing = True
        self.start_progress_update()
        
        try:
            result = self.model.transcribe(file_path)
            output_path = self.get_output_path(file_path)
            
            # Generate transcription in selected format
            if self.ui.format_var.get() == "srt":
                self.generate_srt(result, output_path)
            elif self.ui.format_var.get() == "vtt":
                self.generate_vtt(result, output_path)
            elif self.ui.format_var.get() == "json":
                self.generate_json(result, output_path)
            else:
                self.generate_txt(result, output_path)
            
            self.ui.update_transcription_state("completed")
            
            # Generate notes from transcription
            self.ui.update_status(f"Generating notes for: {base_name}")
            self.ui.update_notes_state("processing")
            
            base_name_without_ext = os.path.splitext(base_name)[0]
            notes_path = self.notes_manager.generate_notes(result["text"], base_name_without_ext)
            
            self.ui.update_notes_state("completed")
            self.ui.update_status(f"Completed: {base_name}\nNotes saved to: {notes_path}")
        except Exception as e:
            self.ui.update_transcription_state("error")
            self.ui.update_notes_state("error")
            self.ui.update_status(f"Error with {base_name}: {str(e)}")
        finally:
            self.transcribing = False

    def start_progress_update(self):
        def update():
            if self.transcribing:
                if self.progress_value < 99:
                    self.progress_value += 3
                    if self.progress_value > 99:
                        self.progress_value = 99
                self.ui.update_progress(self.progress_value)
                self.ui.window.after(300, update)
            else:
                self.progress_value = 100
                self.ui.update_progress(100)
        
        self.ui.window.after(100, update)

    def get_output_path(self, input_file):
        format_ext = self.ui.format_var.get()
        base_filename = os.path.splitext(os.path.basename(input_file))[0] + f'.{format_ext}'
        output_dir = self.ui.output_dir_var.get().strip()
        if output_dir and os.path.isdir(output_dir):
            return os.path.join(output_dir, base_filename)
        return os.path.join(os.path.dirname(input_file), base_filename)

    def generate_srt(self, result, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result.get('segments', []), start=1):
                start = format_timestamp(segment['start'])
                end = format_timestamp(segment['end'])
                f.write(f"{i}\n{start} --> {end}\n{segment['text'].strip()}\n\n")

    def generate_vtt(self, result, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for i, segment in enumerate(result.get('segments', []), start=1):
                start = format_timestamp(segment['start']).replace(',', '.')
                end = format_timestamp(segment['end']).replace(',', '.')
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment['text'].strip()}\n\n")

    def generate_txt(self, result, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result["text"])

    def generate_json(self, result, output_path):
        output_data = {
            'text': result['text'],
            'segments': result.get('segments', []),
            'language': result.get('language', 'unknown')
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
