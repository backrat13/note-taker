# Note Taker Application

A feature-rich note-taking application with dark theme, folder organization, font customization, and unlimited text size support.

## Features

- **Dark Theme**: Modern dark UI that's easy on the eyes
- **Folder Organization**: Create folders with custom colors to organize your notes
- **Font Customization**: Change font family, size, and style (bold/italic)
- **Unlimited Text Size**: No character limits on your notes
- **Search Functionality**: Search through your notes and folders
- **Import/Export**: Export notes to text files and import existing notes
- **Persistent Storage**: All your notes are automatically saved

## Installation

1. Make sure you have Python 3.6 or higher installed
2. Navigate to the note-taker directory:
   ```bash
   cd /home/labrat/note-taker
   ```
3. Install dependencies (if needed):
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python note_taker.py
   ```

2. Create a folder:
   - Click the "+" button in the sidebar or use File > New Folder
   - Choose a name and color for your folder

3. Create a note:
   - Select a folder in the sidebar
   - Click the "+" button in the notes area or use File > New Note

4. Customize fonts:
   - Use the toolbar to change font family, size, bold/italic
   - Or use Edit > Font Settings for more options

5. Search notes:
   - Use Edit > Search to find specific content

## File Structure

- `note_taker.py` - Main application file
- `notes_data/` - Directory where your notes are stored
- `app_config.json` - Application settings (created automatically)

## Tips

- Your notes are automatically saved when you switch between them
- Use different colors for folders to visually organize your projects
- The search function looks through both note titles and content
- Export important notes as text files for backup

## Keyboard Shortcuts

- Ctrl+N: New note (when folder is selected)
- Ctrl+F: Search notes
- Ctrl+E: Export current note
- Ctrl+I: Import note
