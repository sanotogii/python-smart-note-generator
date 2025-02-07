# Video Transcriber & smart notes generator

A Python application that transcribes video files to text, generates subtitles, and creates smart notes using AI.

## Features

- 🎥 Drag and drop video files for transcription
- 📝 Multiple output formats (SRT, VTT, TXT, JSON)
- 🤖 Uses OpenAI's Whisper for accurate transcription
- 🧠 AI-powered notes generation using Google's Gemini
- 🎯 Progress tracking and status indicators
- 🎨 Dark mode interface

## Prerequisites & Disclamer

The app is not tested yet on Linux/Unix based os.

Before I started working on this project i installed whisper with the assistance of this Youtube video:
[Link](https://www.youtube.com/watch?v=ABFqbY_rmEk).

Generally you would need whisper to be working fine on your machine.
check out : https://github.com/openai/whisper

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd python-transcriber
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here

NOTES_OUTPUT_DIR=path/to/your/notes/directory
```

## Usage

1. Run the application:
```bash
python transcriber_app.py
```

2. Select your preferences:
   - Choose Whisper model (tiny, base, small, medium, large)
   - Select output format (SRT, VTT, TXT, JSON)
   - Set output directory (optional)

3. Drag and drop video files into the application window

4. Monitor progress and wait for completion

## Output Formats

- **SRT**: Standard subtitle format with timestamps
- **VTT**: Web Video Text Tracks format
- **TXT**: Plain text transcription
- **JSON**: Structured data including segments and metadata
- **Smart Notes**: Markdown files with AI-generated structured notes

## Models

### Whisper Models
- `tiny`: Fastest, least accurate (1GB VRAM)
- `base`: Good balance for short clips (1GB VRAM)
- `small`: Recommended for general use (2GB VRAM)
- `medium`: More accurate, slower (5GB VRAM)
- `large`: Most accurate, requires more resources (10GB VRAM)

## Requirements

```
customtkinter
tkinterdnd2
whisper
python-dotenv
google-generativeai
```

## Troubleshooting

1. **FFmpeg not found**: Ensure FFmpeg is installed and in system PATH
2. **API Key errors**: Verify your Gemini API key in .env file
3. **Permission errors**: Check write permissions for output directories

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

MIT License - feel free to use and modify for your needs.
