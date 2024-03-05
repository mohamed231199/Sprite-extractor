import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
from collections import Counter


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

                        # Crop the image to the bounding box of non-transparent pixels
                        bbox = sprite_image.getbbox()
                        if bbox:
                            sprite_image = sprite_image.crop(bbox)

                        sprite_image.save(
                            os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_sprite_{i}.png"))

                except Exception as e:
                    print(f"Error processing file {filename}: {str(e)}")

        messagebox.showinfo("Sprites Extracted",
                            f"Sprites extracted from all images in folder and saved in: {output_folder}")

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

    root.mainloop()


if __name__ == "__main__":
    main()
