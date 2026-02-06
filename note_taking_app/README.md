# Modern Note-Taking System with OCR Support

A beautiful, modern note-taking application built with Python featuring Optical Character Recognition (OCR) capabilities.

## Features

? **Modern UI**: Beautiful dark-themed interface built with CustomTkinter
?? **Note Management**: Create, edit, delete, and organize your notes
?? **Search Functionality**: Quickly find notes by title or content
?? **OCR Support**: Extract text from images using EasyOCR
?? **Auto-save**: Notes are automatically saved as you type
?? **Date Tracking**: See when notes were created and modified

## Installation

1. **Install Python** (3.8 or higher)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Note**: EasyOCR will download language models on first use (English by default). This may take a few minutes and requires an internet connection.

## Usage

Run the application:
```bash
python note_taking_app.py
```

### Creating Notes
- Click the **"+ New Note"** button to create a new note
- Type your title and content
- Notes are automatically saved as you type

### Using OCR
1. Click **"?? Extract Text from Image"**
2. Select an image file (PNG, JPG, JPEG, BMP, TIFF, GIF)
3. Wait for OCR processing (may take a moment)
4. Choose to add text to current note or create a new note

### Managing Notes
- Click on any note in the sidebar to open it
- Use the search box to filter notes
- Click **"?? Save"** to manually save
- Click **"??? Delete"** to remove a note

## Notes Storage

All notes are saved in the `notes/` directory as JSON files. Your data is stored locally on your computer.

## Requirements

- Python 3.8+
- CustomTkinter
- EasyOCR
- OpenCV
- Pillow
- NumPy

## Troubleshooting

**OCR not working?**
- Make sure you have an internet connection for the first run (to download language models)
- Ensure the image file is not corrupted
- Try a clearer, higher resolution image

**Application won't start?**
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

## License

Free to use and modify.
