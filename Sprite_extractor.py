import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import shutil
from collections import Counter

sprite_folder_path = ""

def extract_sprites_from_folder():
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return

    try:
        output_folder = os.path.join(folder_path, "extracted_sprites")
        os.makedirs(output_folder, exist_ok=True)

        for filename in os.listdir(folder_path):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(folder_path, filename)
                try:
                    image = Image.open(file_path)
                    width, height = image.size
                    pixels = image.load()

                    sprites = []
                    sprite_start = None

                    for x in range(width):
                        has_color = any(pixels[x, y][3] != 0 for y in range(height))
                        if sprite_start is None and has_color:
                            sprite_start = x
                        elif sprite_start is not None and not has_color:
                            sprites.append((sprite_start, x))
                            sprite_start = None

                    if sprite_start is not None:
                        sprites.append((sprite_start, width))

                    for i, (start, end) in enumerate(sprites):
                        sprite_image = image.crop((start, 0, end, height))
                        sprite_image.save(os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_sprite_{i}.png"))

                except Exception as e:
                    print(f"Error processing file {filename}: {str(e)}")

        messagebox.showinfo("Sprites Extracted", f"Sprites extracted from all images in folder and saved in: {output_folder}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def split_sprite_sheet(image_path, output_folder):
    try:
        image = Image.open(image_path)
        width, height = image.size
        pixels = image.load()

        sprites = []
        sprite_start = None

        # Check for vertical sections with non-alpha pixels
        for y in range(height):
            has_color = any(pixels[x, y][3] != 0 for x in range(width))
            if sprite_start is None and has_color:
                sprite_start = y
            elif sprite_start is not None and not has_color:
                # Found the end of a sprite section
                sprites.append((sprite_start, y))
                sprite_start = None

        # If the last sprite extends to the bottom of the sheet
        if sprite_start is not None:
            sprites.append((sprite_start, height))

        # Save each sprite image
        os.makedirs(output_folder, exist_ok=True)
        for i, (start, end) in enumerate(sprites):
            sprite_image = image.crop((0, start, width, end))
            sprite_image.save(os.path.join(output_folder, f"sprite_{i}.png"))

        messagebox.showinfo("Sprite Sheet Split", f"Sprite sheet split into {len(sprites)} parts saved in folder: {output_folder}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def remove_most_displayed_color(image_path):
    try:
        image = Image.open(image_path)
        pixels = list(image.getdata())
        pixel_counter = Counter(pixels)
        most_common_pixel = pixel_counter.most_common(1)[0][0][:3]  # Extract RGB values only

        new_pixels = [(0, 0, 0,0) if pixel[:3] == most_common_pixel else pixel for pixel in pixels]
        new_image = Image.new("RGBA", image.size)
        new_image.putdata(new_pixels)

        return new_image

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return None

def remove_background():
    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if not image_path:
        return

    new_image = remove_most_displayed_color(image_path)
    if new_image:
        output_folder = filedialog.askdirectory()
        if not output_folder:
            return
        new_image.save(os.path.join(output_folder, "image_without_background.png"))
        messagebox.showinfo("Image Modified", f"Image saved without the background in folder: {output_folder}")

def split_sprite_sheet_and_extract():
    sprite_sheet_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if not sprite_sheet_path:
        return

    output_folder = os.path.splitext(sprite_sheet_path)[0] + "_split"
    split_sprite_sheet(sprite_sheet_path, output_folder)

def open_sprite_table():
    global sprite_folder_path
    sprite_folder_path = filedialog.askdirectory()
    if not sprite_folder_path:
        return

    sprite_files = os.listdir(sprite_folder_path)
    sprite_files.sort()

    sprite_table_window = tk.Toplevel()
    sprite_table_window.title("Sprite Table")

    prefix_label = tk.Label(sprite_table_window, text="Prefix:")
    prefix_label.grid(row=0, column=0, padx=5, pady=5)

    prefix_entry = tk.Entry(sprite_table_window)
    prefix_entry.grid(row=0, column=1, padx=5, pady=5)

    sprite_table = ttk.Treeview(sprite_table_window, columns=("Sprite Name",), show="headings")
    sprite_table.heading("Sprite Name", text="Sprite Name")
    sprite_table.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    for sprite_file in sprite_files:
        sprite_table.insert("", "end", values=(sprite_file,))

    def rename_sprites():
        prefix = prefix_entry.get()
        if not prefix:
            messagebox.showerror("Error", "Please enter a prefix.")
            return

        selected_sprites = sprite_table.selection()
        for sprite in selected_sprites:
            old_name = sprite_table.item(sprite, "values")[0]
            sprite_index = sprite_files.index(old_name)
            filename, extension = os.path.splitext(old_name)
            new_name = f"{prefix}_{sprite_index:02d}{extension}"
            os.rename(os.path.join(sprite_folder_path, old_name), os.path.join(sprite_folder_path, new_name))
            sprite_table.item(sprite, values=(new_name,))

    rename_button = tk.Button(sprite_table_window, text="Rename Selected", command=rename_sprites)
    rename_button.grid(row=2, column=0, padx=5, pady=5)

    def create_folder_and_move():
        prefix = prefix_entry.get()
        if not prefix:
            messagebox.showerror("Error", "Please enter a prefix.")
            return

        selected_sprites = sprite_table.selection()
        if not selected_sprites:
            messagebox.showerror("Error", "No sprites selected.")
            return

        folder_name = f"{prefix}_sprites"
        new_folder_path = os.path.join(sprite_folder_path, folder_name)
        os.makedirs(new_folder_path, exist_ok=True)

        for sprite in selected_sprites:
            sprite_name = sprite_table.item(sprite, "values")[0]
            shutil.move(os.path.join(sprite_folder_path, sprite_name), os.path.join(new_folder_path, sprite_name))

        messagebox.showinfo("Folder Created", f"Selected sprites moved to folder: {new_folder_path}")

    move_button = tk.Button(sprite_table_window, text="Create Folder & Move Selected", command=create_folder_and_move)
    move_button.grid(row=2, column=1, padx=5, pady=5)

def main():
    root = tk.Tk()
    root.title("Sprite Extractor")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack()

    remove_button = tk.Button(frame, text="Remove Background", command=remove_background)
    remove_button.grid(row=0, column=0, columnspan=2, pady=5)

    split_button = tk.Button(frame, text="Split Sprite Sheet", command=split_sprite_sheet_and_extract)
    split_button.grid(row=1, column=0, columnspan=2, pady=5)

    extract_button = tk.Button(frame, text="Extract Sprites from Folder", command=extract_sprites_from_folder)
    extract_button.grid(row=3, column=0, columnspan=2, pady=5)

    sprite_table_button = tk.Button(frame, text="Open Sprite Table", command=open_sprite_table)
    sprite_table_button.grid(row=4, column=0, columnspan=2, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
