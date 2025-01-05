import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import json
import os
import webbrowser

def extract_relevant_metadata(filepath):
    try:
        image = Image.open(filepath)
        metadata = image.info

        # Parse the "prompt" field as JSON
        if 'prompt' in metadata:
            try:
                prompt_data = json.loads(metadata['prompt'])
            except json.JSONDecodeError:
                return {"Error": "Failed to parse prompt data as JSON."}

            # Extract relevant metadata
            relevant_data = {
                "Positive Prompt": prompt_data.get("6", {}).get("inputs", {}).get("text", "Not Available"),
                "Negative Prompt": prompt_data.get("7", {}).get("inputs", {}).get("text", "Not Available"),
                "Model Information": os.path.basename(prompt_data.get("4", {}).get("inputs", {}).get("ckpt_name", "Not Available")),
                "LoRA": os.path.basename(prompt_data.get("10", {}).get("inputs", {}).get("lora_name", "Not Available")),
                "Seed": prompt_data.get("3", {}).get("inputs", {}).get("seed", "Not Available"),
                "CFG": prompt_data.get("3", {}).get("inputs", {}).get("cfg", "Not Available"),
                "Sampling Method": prompt_data.get("3", {}).get("inputs", {}).get("sampler_name", "Not Available"),
                "Scheduler": prompt_data.get("3", {}).get("inputs", {}).get("scheduler", "Not Available"),
                "VAE": os.path.basename(prompt_data.get("11", {}).get("inputs", {}).get("vae_name", "Not Available")),
            }
            return relevant_data
        else:
            return {"Error": "No prompt data found in metadata."}
    except Exception as e:
        return {"Error": f"Error extracting metadata: {e}"}

def copy_to_clipboard(text):
    """Copies given text to clipboard."""
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

def browse_file():
    """Opens file dialog, displays image, extracts & shows metadata."""
    filepath = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if filepath:
        try:
            # Open and resize image
            img = Image.open(filepath)
            original_width, original_height = img.size
            max_size = 450
            ratio = min(max_size / original_width, max_size / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Display image
            img_tk = ImageTk.PhotoImage(img)
            image_label.config(image=img_tk)
            image_label.image = img_tk
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {e}")
            return

        # Extract metadata
        metadata = extract_relevant_metadata(filepath)

        # Update metadata text boxes
        for key, value in metadata.items():
            if key in metadata_boxes:
                metadata_boxes[key].config(state="normal")
                metadata_boxes[key].delete("1.0", tk.END)
                metadata_boxes[key].insert(tk.END, value)
                metadata_boxes[key].config(state="disabled")

                # Update copy button command, if button exists
                if key in copy_buttons:
                    copy_buttons[key].config(command=lambda v=value: copy_to_clipboard(v))

def open_link(event):
    """Opens the specified YouTube page in the default web browser."""
    webbrowser.open_new("https://www.youtube.com/@UD.SMedia")

# Main Window
root = tk.Tk()
root.title("ComfyUI Metadata Extractor")
root.geometry("1280x720")
root.resizable(False, False)

# Configure root grid
root.grid_columnconfigure(0, minsize=640)
root.grid_columnconfigure(1, minsize=640)
root.grid_rowconfigure(0, minsize=720)

# Dictionaries to store references
metadata_boxes = {}
copy_buttons = {}

# Left Frame: Image
left_frame = tk.Frame(root, width=640, height=720, bg="lightgray")
left_frame.grid(row=0, column=0, sticky="nsew")
left_frame.grid_propagate(False)

# Browse Button at top-left
browse_button = tk.Button(left_frame, text="Browse Image", command=browse_file)
browse_button.pack(side="top", anchor="nw", padx=10, pady=10)

# Sub-frame to center the image
image_frame = tk.Frame(left_frame, bg="lightgray")
image_frame.pack(fill="both", expand=True)
image_frame.pack_propagate(False)

# Label to hold the image (centered via place)
image_label = tk.Label(image_frame, bg="lightgray", width=450, height=450)
image_label.place(relx=0.5, rely=0.5, anchor="center")

# Right Frame: Metadata
right_frame = tk.Frame(root, width=640, height=720)
right_frame.grid(row=0, column=1, sticky="nsew")
right_frame.grid_propagate(False)

# Positive Prompt Section
positive_frame = tk.Frame(right_frame)
positive_frame.pack(fill="x", pady=5, padx=(10, 20))

# Row 0: Copy Button + Label
copy_button_positive = tk.Button(positive_frame, text="📋")
copy_button_positive.grid(row=0, column=0, padx=(5,2), pady=5, sticky="w")
copy_buttons["Positive Prompt"] = copy_button_positive

positive_label = tk.Label(positive_frame, text="Positive Prompt:", anchor="w")
positive_label.grid(row=0, column=1, padx=0, pady=5, sticky="w")

# Row 1: ScrolledText
from tkinter.scrolledtext import ScrolledText
positive_text = ScrolledText(positive_frame, width=73, height=6, wrap="word")
positive_text.grid(row=1, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="we")
positive_text.config(state="disabled")
metadata_boxes["Positive Prompt"] = positive_text

# Negative Prompt Section
negative_frame = tk.Frame(right_frame)
negative_frame.pack(fill="x", pady=5, padx=(10, 20))

# Row 0: Copy Button + Label
copy_button_negative = tk.Button(negative_frame, text="📋")
copy_button_negative.grid(row=0, column=0, padx=(5,2), pady=5, sticky="w")
copy_buttons["Negative Prompt"] = copy_button_negative

negative_label = tk.Label(negative_frame, text="Negative Prompt:", anchor="w")
negative_label.grid(row=0, column=1, padx=0, pady=5, sticky="w")

# Row 1: ScrolledText
negative_text = ScrolledText(negative_frame, width=73, height=6, wrap="word")
negative_text.grid(row=1, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="we")
negative_text.config(state="disabled")
metadata_boxes["Negative Prompt"] = negative_text

# Other Metadata Fields
metadata_frame = tk.Frame(right_frame)
metadata_frame.pack(fill="x", pady=10, padx=(10, 20))

fields = ["Model Information", "Scheduler", "Sampling Method", "CFG", "Seed", "VAE"]
for i, field in enumerate(fields):
    field_label = tk.Label(metadata_frame, text=field + ":", anchor="w")
    field_label.grid(row=i, column=0, sticky="w", padx=5, pady=2)

    field_text = tk.Text(metadata_frame, height=1, width=50, state="disabled")
    field_text.grid(row=i, column=1, padx=(0, 5), pady=2, sticky="we")
    metadata_boxes[field] = field_text

    # Example: copy button for the 'Seed' field
    if field == "Seed":
        copy_button_seed = tk.Button(
            metadata_frame,
            text="📋",
            command=lambda: copy_to_clipboard(field_text.get("1.0", "end-1c"))
        )
        copy_button_seed.grid(row=i, column=2, padx=(0,10), pady=2, sticky="e")
        copy_buttons[field] = copy_button_seed

# LoRA Section (no copy button)
lora_frame = tk.Frame(right_frame)
lora_frame.pack(fill="x", pady=5, padx=(10, 20))

lora_label = tk.Label(lora_frame, text="LoRA:", anchor="w")
lora_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

lora_text = ScrolledText(lora_frame, width=73, height=6, wrap="word")
lora_text.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="we")
lora_text.config(state="disabled")
metadata_boxes["LoRA"] = lora_text

# Footer Credit with clickable link
footer_label = tk.Label(right_frame, text="By Koorosh Ghotb", font=("Arial", 10), fg="blue", cursor="hand2")
footer_label.pack(pady=10, anchor="center")
footer_label.bind("<Button-1>", open_link)

# Run the application
root.mainloop()
