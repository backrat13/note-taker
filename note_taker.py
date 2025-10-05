#!/usr/bin/env python3
"""
Note Taker Application
A feature-rich note-taking app with dark theme, folder organization, and font customization.
"""

import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, font
import tkinter.scrolledtext as scrolledtext
from datetime import datetime
import re

class NoteTaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Note Taker")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2b2b2b")

        # Data storage
        self.notes_dir = "notes_data"
        self.config_file = "app_config.json"
        self.folders = {}
        self.current_note = None
        self.current_folder = None

        # Create notes directory if it doesn't exist
        if not os.path.exists(self.notes_dir):
            os.makedirs(self.notes_dir)

        # Load configuration and data
        self.load_config()
        self.load_folders()

        # Setup UI
        self.setup_styles()
        self.create_menu_bar()
        self.create_main_area()
        self.create_sidebar()
        self.create_toolbar()

        # Load initial state
        self.refresh_sidebar()
        if self.folders:
            first_folder = list(self.folders.keys())[0]
            self.select_folder(first_folder)

    def setup_styles(self):
        """Setup dark theme styles"""
        style = ttk.Style()
        style.theme_use('default')

        # Configure colors
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'accent': '#3a3a3a',
            'button': '#404040',
            'button_hover': '#505050',
            'text_bg': '#1a1a1a',
            'border': '#555555',
            'folder_colors': ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7',
                             '#dda0dd', '#98d8c8', '#f7dc6f', '#bb8fce', '#85c1e9']
        }

        # Configure all styles
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', background=self.colors['button'], foreground=self.colors['fg'])
        style.configure('Horizontal.TScrollbar', background=self.colors['accent'], troughcolor=self.colors['bg'])
        style.configure('Vertical.TScrollbar', background=self.colors['accent'], troughcolor=self.colors['bg'])

        # Custom button style
        style.map('TButton',
                 background=[('active', self.colors['button_hover'])])

    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root, bg=self.colors['accent'], fg=self.colors['fg'])

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['accent'], fg=self.colors['fg'])
        file_menu.add_command(label="New Folder", command=self.create_folder)
        file_menu.add_command(label="New Note", command=self.create_note)
        file_menu.add_separator()
        file_menu.add_command(label="Export Note", command=self.export_note)
        file_menu.add_command(label="Import Note", command=self.import_note)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['accent'], fg=self.colors['fg'])
        edit_menu.add_command(label="Font Settings", command=self.show_font_dialog)
        edit_menu.add_command(label="Search", command=self.show_search_dialog)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['accent'], fg=self.colors['fg'])
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def create_toolbar(self):
        """Create the main toolbar"""
        toolbar_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)

        # Font family selector
        tk.Label(toolbar_frame, text="Font:", bg=self.colors['bg'], fg=self.colors['fg']).pack(side=tk.LEFT, padx=2)
        self.font_var = tk.StringVar(value=self.current_font['family'])
        font_combo = ttk.Combobox(toolbar_frame, textvariable=self.font_var, width=15)
        font_combo['values'] = list(font.families())
        font_combo.pack(side=tk.LEFT, padx=2)
        font_combo.bind('<<ComboboxSelected>>', self.change_font)

        # Font size selector
        tk.Label(toolbar_frame, text="Size:", bg=self.colors['bg'], fg=self.colors['fg']).pack(side=tk.LEFT, padx=2)
        self.size_var = tk.StringVar(value=str(self.current_font['size']))
        size_combo = ttk.Combobox(toolbar_frame, textvariable=self.size_var, width=5)
        size_combo['values'] = ['8', '9', '10', '11', '12', '14', '16', '18', '20', '24', '28', '32']
        size_combo.pack(side=tk.LEFT, padx=2)
        size_combo.bind('<<ComboboxSelected>>', self.change_font)

        # Bold/Italic buttons
        self.bold_var = tk.BooleanVar(value=self.current_font['weight'] == 'bold')
        bold_btn = tk.Checkbutton(toolbar_frame, text="B", variable=self.bold_var, command=self.change_font,
                                 bg=self.colors['bg'], fg=self.colors['fg'], selectcolor=self.colors['accent'])
        bold_btn.pack(side=tk.LEFT, padx=2)

        self.italic_var = tk.BooleanVar(value=self.current_font['slant'] == 'italic')
        italic_btn = tk.Checkbutton(toolbar_frame, text="I", variable=self.italic_var, command=self.change_font,
                                   bg=self.colors['bg'], fg=self.colors['fg'], selectcolor=self.colors['accent'])
        italic_btn.pack(side=tk.LEFT, padx=2)

    def create_sidebar(self):
        """Create the sidebar for folders and notes"""
        self.sidebar_frame = tk.Frame(self.root, bg=self.colors['accent'], width=250)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Sidebar header
        sidebar_header = tk.Frame(self.sidebar_frame, bg=self.colors['accent'])
        sidebar_header.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(sidebar_header, text="Folders", bg=self.colors['accent'], fg=self.colors['fg'],
                font=('Arial', 10, 'bold')).pack()

        # Add folder button
        add_folder_btn = tk.Button(sidebar_header, text="+", command=self.create_folder,
                                  bg=self.colors['button'], fg=self.colors['fg'], width=3)
        add_folder_btn.pack(side=tk.RIGHT)

        # Folders listbox
        self.folders_listbox = tk.Listbox(self.sidebar_frame, bg=self.colors['text_bg'],
                                         fg=self.colors['fg'], selectbackground=self.colors['button'])
        self.folders_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.folders_listbox.bind('<<ListboxSelect>>', self.on_folder_select)

        # Notes listbox (in main area)
        self.notes_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        notes_header = tk.Frame(self.notes_frame, bg=self.colors['bg'])
        notes_header.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(notes_header, text="Notes", bg=self.colors['bg'], fg=self.colors['fg'],
                font=('Arial', 10, 'bold')).pack()

        add_note_btn = tk.Button(notes_header, text="+", command=self.create_note,
                                bg=self.colors['button'], fg=self.colors['fg'], width=3)
        add_note_btn.pack(side=tk.RIGHT)

        self.notes_listbox = tk.Listbox(self.notes_frame, bg=self.colors['text_bg'],
                                       fg=self.colors['fg'], selectbackground=self.colors['button'])
        self.notes_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.notes_listbox.bind('<<ListboxSelect>>', self.on_note_select)

    def create_main_area(self):
        """Create the main content area"""
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Note editor area
        self.editor_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])

        # Note title
        title_frame = tk.Frame(self.editor_frame, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(title_frame, text="Title:", bg=self.colors['bg'], fg=self.colors['fg']).pack(side=tk.LEFT)
        self.note_title = tk.Entry(title_frame, bg=self.colors['text_bg'], fg=self.colors['fg'],
                                  insertbackground=self.colors['fg'])
        self.note_title.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Note content (unlimited size)
        content_frame = tk.Frame(self.editor_frame, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.note_content = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD,
                                                     bg=self.colors['text_bg'], fg=self.colors['fg'],
                                                     insertbackground=self.colors['fg'],
                                                     selectbackground=self.colors['button'])
        self.note_content.pack(fill=tk.BOTH, expand=True)

        # Configure scrollbar colors
        self.note_content.config(selectforeground=self.colors['fg'])

    def create_note(self):
        """Create a new note"""
        if not self.current_folder:
            messagebox.showwarning("Warning", "Please select a folder first")
            return

        note_title = f"Untitled Note {len(self.folders[self.current_folder]['notes']) + 1}"
        note_data = {
            'title': note_title,
            'content': '',
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'font': self.current_font.copy()
        }

        self.folders[self.current_folder]['notes'][note_title] = note_data
        self.refresh_notes()
        self.select_note(note_title)
        self.save_folders()

    def create_folder(self):
        """Create a new folder with color selection"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Folder")
        dialog.configure(bg=self.colors['bg'])
        dialog.geometry("300x200")

        tk.Label(dialog, text="Folder Name:", bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=10)

        name_var = tk.StringVar()
        name_entry = tk.Entry(dialog, textvariable=name_var, bg=self.colors['text_bg'], fg=self.colors['fg'])
        name_entry.pack(pady=5, padx=20, fill=tk.X)

        # Color selection
        color_frame = tk.Frame(dialog, bg=self.colors['bg'])
        color_frame.pack(pady=10)

        tk.Label(color_frame, text="Color:", bg=self.colors['bg'], fg=self.colors['fg']).pack(side=tk.LEFT)

        selected_color = tk.StringVar(value=self.colors['folder_colors'][0])
        color_buttons_frame = tk.Frame(color_frame, bg=self.colors['bg'])
        color_buttons_frame.pack(side=tk.LEFT, padx=10)

        for i, color in enumerate(self.colors['folder_colors']):
            btn = tk.Button(color_buttons_frame, bg=color, width=3, height=1,
                           command=lambda c=color: selected_color.set(c))
            btn.pack(side=tk.LEFT, padx=1)

        custom_btn = tk.Button(color_buttons_frame, text="...", width=3, height=1,
                              command=lambda: selected_color.set(colorchooser.askcolor()[1] or selected_color.get()))
        custom_btn.pack(side=tk.LEFT, padx=1)

        def save_folder():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter a folder name")
                return

            if name in self.folders:
                messagebox.showwarning("Warning", "Folder already exists")
                return

            self.folders[name] = {
                'color': selected_color.get(),
                'notes': {},
                'created': datetime.now().isoformat()
            }

            self.refresh_sidebar()
            self.save_folders()
            dialog.destroy()

        button_frame = tk.Frame(dialog, bg=self.colors['bg'])
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Create", command=save_folder,
                 bg=self.colors['button'], fg=self.colors['fg']).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                 bg=self.colors['button'], fg=self.colors['fg']).pack(side=tk.LEFT)

    def on_folder_select(self, event):
        """Handle folder selection"""
        selection = self.folders_listbox.curselection()
        if selection:
            folder_name = self.folders_listbox.get(selection[0])
            self.select_folder(folder_name)

    def select_folder(self, folder_name):
        """Select a folder and show its notes"""
        self.current_folder = folder_name
        self.refresh_notes()
        self.notes_frame.pack(side=tk.TOP, fill=tk.X)
        self.editor_frame.pack_forget()

    def refresh_sidebar(self):
        """Refresh the folders sidebar"""
        self.folders_listbox.delete(0, tk.END)
        for folder_name, folder_data in self.folders.items():
            color = folder_data['color']
            self.folders_listbox.insert(tk.END, f"● {folder_name}")
            # Color the text (simplified approach)
            try:
                self.folders_listbox.itemconfig(tk.END, {'fg': color})
            except:
                pass  # Some colors might not work well

    def refresh_notes(self):
        """Refresh the notes list"""
        if not self.current_folder:
            return

        self.notes_listbox.delete(0, tk.END)
        notes = self.folders[self.current_folder]['notes']
        for note_title in notes:
            self.notes_listbox.insert(tk.END, note_title)

    def on_note_select(self, event):
        """Handle note selection"""
        selection = self.notes_listbox.curselection()
        if selection:
            note_title = self.notes_listbox.get(selection[0])
            self.select_note(note_title)

    def select_note(self, note_title):
        """Select and display a note"""
        if not self.current_folder or note_title not in self.folders[self.current_folder]['notes']:
            return

        self.current_note = note_title
        note_data = self.folders[self.current_folder]['notes'][note_title]

        # Update UI
        self.note_title.delete(0, tk.END)
        self.note_title.insert(0, note_data['title'])

        self.note_content.delete(1.0, tk.END)
        self.note_content.insert(1.0, note_data['content'])

        # Apply note's font settings
        note_font = note_data.get('font', self.current_font)
        self.apply_font_to_editor(note_font)

        # Show editor
        self.notes_frame.pack(side=tk.TOP, fill=tk.X)
        self.editor_frame.pack(fill=tk.BOTH, expand=True)

    def apply_font_to_editor(self, font_settings):
        """Apply font settings to the editor"""
        current_font = font.Font(family=font_settings['family'],
                               size=font_settings['size'],
                               weight=font_settings['weight'],
                               slant=font_settings['slant'])
        self.note_content.configure(font=current_font)

    def change_font(self, event=None):
        """Change font settings"""
        # Update current font settings
        self.current_font.update({
            'family': self.font_var.get(),
            'size': int(self.size_var.get()),
            'weight': 'bold' if self.bold_var.get() else 'normal',
            'slant': 'italic' if self.italic_var.get() else 'roman'
        })

        # Apply to current note if exists
        if self.current_note and self.current_folder:
            note_data = self.folders[self.current_folder]['notes'][self.current_note]
            note_data['font'] = self.current_font.copy()
            note_data['modified'] = datetime.now().isoformat()

        # Apply to editor
        self.apply_font_to_editor(self.current_font)

        # Save config
        self.save_config()

    def show_font_dialog(self):
        """Show advanced font settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Font Settings")
        dialog.configure(bg=self.colors['bg'])
        dialog.geometry("400x300")

        # Font family
        tk.Label(dialog, text="Font Family:", bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=5)
        font_var = tk.StringVar(value=self.current_font['family'])
        font_combo = ttk.Combobox(dialog, textvariable=font_var)
        font_combo['values'] = list(font.families())
        font_combo.pack(pady=5, padx=20, fill=tk.X)

        # Font size
        tk.Label(dialog, text="Font Size:", bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=5)
        size_var = tk.StringVar(value=str(self.current_font['size']))
        size_spinbox = tk.Spinbox(dialog, from_=8, to=72, textvariable=size_var, width=10)
        size_spinbox.pack(pady=5)

        # Preview area
        preview_frame = tk.Frame(dialog, bg=self.colors['bg'])
        preview_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(preview_frame, text="Preview:", bg=self.colors['bg'], fg=self.colors['fg']).pack(anchor=tk.W)

        preview_text = tk.Text(preview_frame, height=3, bg=self.colors['text_bg'], fg=self.colors['fg'])
        preview_text.pack(fill=tk.X, pady=5)
        preview_text.insert(1.0, "This is how your text will look with the selected font settings.")

        def update_preview():
            current_font = font.Font(family=font_var.get(),
                                   size=int(size_var.get()),
                                   weight='bold' if bold_var.get() else 'normal',
                                   slant='italic' if italic_var.get() else 'roman')
            preview_text.configure(font=current_font)

        # Bold and italic checkboxes
        check_frame = tk.Frame(dialog, bg=self.colors['bg'])
        check_frame.pack(pady=10)

        bold_var = tk.BooleanVar(value=self.current_font['weight'] == 'bold')
        tk.Checkbutton(check_frame, text="Bold", variable=bold_var, command=update_preview,
                      bg=self.colors['bg'], fg=self.colors['fg'], selectcolor=self.colors['accent']).pack(side=tk.LEFT)

        italic_var = tk.BooleanVar(value=self.current_font['slant'] == 'italic')
        tk.Checkbutton(check_frame, text="Italic", variable=italic_var, command=update_preview,
                      bg=self.colors['bg'], fg=self.colors['fg'], selectcolor=self.colors['accent']).pack(side=tk.LEFT)

        def apply_font():
            self.current_font.update({
                'family': font_var.get(),
                'size': int(size_var.get()),
                'weight': 'bold' if bold_var.get() else 'normal',
                'slant': 'italic' if italic_var.get() else 'roman'
            })
            self.change_font()
            dialog.destroy()

        button_frame = tk.Frame(dialog, bg=self.colors['bg'])
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Apply", command=apply_font,
                 bg=self.colors['button'], fg=self.colors['fg']).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                 bg=self.colors['button'], fg=self.colors['fg']).pack(side=tk.LEFT)

        # Initial preview update
        update_preview()

    def show_search_dialog(self):
        """Show search dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Search Notes")
        dialog.configure(bg=self.colors['bg'])
        dialog.geometry("500x400")

        tk.Label(dialog, text="Search:", bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=5)
        search_var = tk.StringVar()
        search_entry = tk.Entry(dialog, textvariable=search_var, bg=self.colors['text_bg'], fg=self.colors['fg'])
        search_entry.pack(pady=5, padx=20, fill=tk.X)

        # Search results
        results_frame = tk.Frame(dialog, bg=self.colors['bg'])
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        results_listbox = tk.Listbox(results_frame, bg=self.colors['text_bg'], fg=self.colors['fg'],
                                   selectbackground=self.colors['button'])
        results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        results_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=results_listbox.yview)

        def perform_search(*args):
            query = search_var.get().lower()
            results_listbox.delete(0, tk.END)

            if not query:
                return

            for folder_name, folder_data in self.folders.items():
                for note_title, note_data in folder_data['notes'].items():
                    # Search in title and content
                    if (query in note_title.lower() or
                        query in note_data['content'].lower()):
                        display_text = f"{folder_name} > {note_title}"
                        results_listbox.insert(tk.END, display_text)
                        # Store the actual folder and note for selection
                        results_listbox.itemconfig(tk.END, {'data': (folder_name, note_title)})

        search_var.trace('w', perform_search)

        def select_result(event):
            selection = results_listbox.curselection()
            if selection:
                data = results_listbox.get(selection[0])
                # This is a simplified approach - in a real app you'd store the actual references
                dialog.destroy()

        results_listbox.bind('<<ListboxSelect>>', select_result)

    def export_note(self):
        """Export current note to file"""
        if not self.current_note:
            messagebox.showwarning("Warning", "Please select a note to export")
            return

        filetypes = [
            ('Text files', '*.txt'),
            ('Markdown files', '*.md'),
            ('All files', '*.*')
        ]

        filename = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=filetypes,
            initialfile=self.current_note + '.txt'
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.note_content.get(1.0, tk.END).strip())
                messagebox.showinfo("Success", "Note exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export note: {str(e)}")

    def import_note(self):
        """Import note from file"""
        if not self.current_folder:
            messagebox.showwarning("Warning", "Please select a folder first")
            return

        filetypes = [
            ('Text files', '*.txt'),
            ('Markdown files', '*.md'),
            ('All files', '*.*')
        ]

        filename = filedialog.askopenfilename(filetypes=filetypes)

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract title from filename
                title = os.path.splitext(os.path.basename(filename))[0]

                note_data = {
                    'title': title,
                    'content': content,
                    'created': datetime.now().isoformat(),
                    'modified': datetime.now().isoformat(),
                    'font': self.current_font.copy()
                }

                self.folders[self.current_folder]['notes'][title] = note_data
                self.refresh_notes()
                self.select_note(title)
                self.save_folders()

                messagebox.showinfo("Success", "Note imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import note: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Note Taker\nA powerful note-taking application\nCreated with Python and Tkinter")

    def save_config(self):
        """Save application configuration"""
        config = {
            'current_font': self.current_font,
            'window_size': self.root.geometry()
        }

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")

    def load_config(self):
        """Load application configuration"""
        self.current_font = {
            'family': 'Arial',
            'size': 12,
            'weight': 'normal',
            'slant': 'roman'
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.current_font.update(config.get('current_font', self.current_font))
            except Exception as e:
                print(f"Warning: Could not load config: {e}")

    def save_folders(self):
        """Save folders and notes data"""
        try:
            with open(os.path.join(self.notes_dir, 'folders.json'), 'w') as f:
                json.dump(self.folders, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save folders: {e}")

    def load_folders(self):
        """Load folders and notes data"""
        folders_file = os.path.join(self.notes_dir, 'folders.json')
        if os.path.exists(folders_file):
            try:
                with open(folders_file, 'r') as f:
                    self.folders = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load folders: {e}")
                self.folders = {}

if __name__ == "__main__":
    root = tk.Tk()
    app = NoteTaker(root)
    root.mainloop()
