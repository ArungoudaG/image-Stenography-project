import numpy as np

from PIL import Image

import tkinter as tk

from tkinter import ttk, filedialog, messagebox, scrolledtext

import argparse

import sys

import os







print("file found")



print("file not found! check your path")



class ImageSteganography:

    """Complete image steganography implementation using LSB technique"""

    

    def _init_(self):

        self.delimiter = "###STEGO_END###"

    

    def string_to_binary(self, text):

        """Convert string to binary representation"""

        return ''.join(format(ord(char), '08b') for char in text)

    

    def binary_to_string(self, binary):

        """Convert binary to string with error handling"""

        text = ""

        for i in range(0, len(binary), 8):

            if i + 8 <= len(binary):

                byte = binary[i:i+8]

                try:

                    ascii_val = int(byte, 2)

                    if 32 <= ascii_val <= 126 or ascii_val in [9, 10, 13]:

                        text += chr(ascii_val)

                    else:

                        text += '?'

                except ValueError:

                    text += '?'

        return text

    

    def encode_message(self, image_path, message, output_path, password=None):

        """Hide message in image file"""

        try:

            # Load image

            img = Image.open(image_path)

            img_array = np.array(img)

            

            # Add password protection if provided

            if password:

                message = f"PWD:{password}|{message}"

            

            # Prepare message

            full_message = message + self.delimiter

            binary_message = self.string_to_binary(full_message)

            

            # Check capacity

            if len(binary_message) > img_array.size:

                return False, (f"Message too long! Need {len(binary_message)} bits, image has {img_array.size} pixels")

            

            # Flatten image

            flat_img = img_array.flatten()

            

            # Embed message in LSBs

            for i, bit in enumerate(binary_message):

                if i < len(flat_img):

                    flat_img[i] = (flat_img[i] & 0xFE) | int(bit)

            

            # Reshape and save

            stego_array = flat_img.reshape(img_array.shape)

            stego_img = Image.fromarray(stego_array.astype('uint8'))

            stego_img.save(output_path)

            

            return True, f"Message hidden successfully in {output_path}"

            

        except Exception as e:

            return False, f"Error: {str(e)}"

    

    def decode_message(self, image_path, password=None):

        """Extract message from steganographic image"""

        try:

            # Load image

            img = Image.open(image_path)

            img_array = np.array(img)

            

            # Extract LSBs

            flat_img = img_array.flatten()

            binary_data = ''.join(str(pixel & 1) for pixel in flat_img)

            

            # Convert to text

            text_data = self.binary_to_string(binary_data)

            

            # Find delimiter

            delimiter_pos = text_data.find(self.delimiter)

            if delimiter_pos == -1:

                return False, "No hidden message found"

            

            hidden_message = text_data[:delimiter_pos]

            

            # Handle password protection

            if hidden_message.startswith("PWD:"):

                try:

                    pwd_part, msg_part = hidden_message.split("|", 1)

                    stored_password = pwd_part[4:]  # Remove "PWD:" prefix

                    

                    if password and password == stored_password:

                        return True, msg_part

                    elif password:

                        return False, "Incorrect password"

                    else:

                        return False, "Password required to decode this message"

                except ValueError:

                    return False, "Corrupted password-protected message"

            

            return True, hidden_message

            

        except Exception as e:

            return False, f"Error: {str(e)}"

    

    def get_image_info(self, image_path):

        """Get image capacity information"""

        try:

            img = Image.open(image_path)

            img_array = np.array(img)

            

            total_pixels = img_array.size

            max_chars = total_pixels // 8

            

            return {

                'width': img.width,

                'height': img.height,

                'channels': len(img_array.shape),

                'total_pixels': total_pixels,

                'max_characters': max_chars,

                'format': img.format

            }

        except Exception as e:

            return None



class SteganographyGUI:

    """GUI application for steganography"""

    

    def init(self):

        self.root = tk.Tk()

        self.root.title("Image Steganography Tool")

        self.root.geometry("800x600")

        self.root.configure(bg='#f0f0f0')

        

        self.stego = ImageSteganography()

        self.setup_gui()

    

    def setup_gui(self):

        """Setup the GUI interface"""

        # Title

        title_label = tk.Label(self.root, text="ðŸ” Image Steganography Tool", 

                              font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#2c3e50')

        title_label.pack(pady=20)

        

        # Create notebook for tabs

        notebook = ttk.Notebook(self.root)

        notebook.pack(fill='both', expand=True, padx=20, pady=10)

        

        # Encode tab

        encode_frame = ttk.Frame(notebook)

        notebook.add(encode_frame, text="Hide Message")

        self.setup_encode_tab(encode_frame)

        

        # Decode tab

        decode_frame = ttk.Frame(notebook)

        notebook.add(decode_frame, text="Reveal Message")

        self.setup_decode_tab(decode_frame)

        

        # Info tab

        info_frame = ttk.Frame(notebook)

        notebook.add(info_frame, text="Image Info")

        self.setup_info_tab(info_frame)

    

    def setup_encode_tab(self, parent):

        """Setup encoding tab"""

        # Cover image selection

        ttk.Label(parent, text="Cover Image:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10,5))

        

        img_frame = ttk.Frame(parent)

        img_frame.pack(fill='x', pady=5)

        

        self.cover_image_var = tk.StringVar()

        ttk.Entry(img_frame, textvariable=self.cover_image_var, state='readonly').pack(side='left', fill='x', expand=True)

        ttk.Button(img_frame, text="Browse", command=self.browse_cover_image).pack(side='right', padx=(5,0))

        

        # Message input

        ttk.Label(parent, text="Secret Message:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(15,5))

        

        self.message_text = scrolledtext.ScrolledText(parent, height=10, font=('Arial', 10))

        self.message_text.pack(fill='both', expand=True, pady=5)

        

        # Password (optional)

        ttk.Label(parent, text="Password (Optional):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(15,5))

        self.password_var = tk.StringVar()

        ttk.Entry(parent, textvariable=self.password_var, show="*").pack(fill='x', pady=5)

        

        # Output path

        ttk.Label(parent, text="Output Image:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(15,5))

        

        out_frame = ttk.Frame(parent)

        out_frame.pack(fill='x', pady=5)

        

        self.output_path_var = tk.StringVar()

        ttk.Entry(out_frame, textvariable=self.output_path_var, state='readonly').pack(side='left', fill='x', expand=True)

        ttk.Button(out_frame, text="Browse", command=self.browse_output_path).pack(side='right', padx=(5,0))

        

        # Encode button

        ttk.Button(parent, text="ðŸ”’ Hide Message", command=self.encode_message,

                  style='Accent.TButton').pack(pady=20)

    

    def setup_decode_tab(self, parent):

        """Setup decoding tab"""

        # Stego image selection

        ttk.Label(parent, text="Steganographic Image:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10,5))

        

        stego_frame = ttk.Frame(parent)

        stego_frame.pack(fill='x', pady=5)

        

        self.stego_image_var = tk.StringVar()

        ttk.Entry(stego_frame, textvariable=self.stego_image_var, state='readonly').pack(side='left', fill='x', expand=True)

        ttk.Button(stego_frame, text="Browse", command=self.browse_stego_image).pack(side='right', padx=(5,0))

        

        # Password input

        ttk.Label(parent, text="Password (if protected):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(15,5))

        self.decode_password_var = tk.StringVar()

        ttk.Entry(parent, textvariable=self.decode_password_var, show="*").pack(fill='x', pady=5)

        

        # Decode button

        ttk.Button(parent, text="ðŸ”“ Reveal Message", command=self.decode_message,

                  style='Accent.TButton').pack(pady=20)

        

        # Message display

        ttk.Label(parent, text="Revealed Message:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(15,5))

        

        self.revealed_text = scrolledtext.ScrolledText(parent, height=10, font=('Arial', 10))

        self.revealed_text.pack(fill='both', expand=True, pady=5)

    

    def setup_info_tab(self, parent):

        """Setup info tab"""

        ttk.Label(parent, text="Image Analysis:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10,5))

        

        info_img_frame = ttk.Frame(parent)

        info_img_frame.pack(fill='x', pady=5)

        

        self.info_image_var = tk.StringVar()

        ttk.Entry(info_img_frame, textvariable=self.info_image_var, state='readonly').pack(side='left', fill='x', expand=True)

        ttk.Button(info_img_frame, text="Browse", command=self.browse_info_image).pack(side='right', padx=(5,0))

        

        ttk.Button(parent, text="ðŸ“Š Analyze Image", command=self.analyze_image).pack(pady=10)

        

        # Info display

        self.info_text = scrolledtext.ScrolledText(parent, height=15, font=('Arial', 10))

        self.info_text.pack(fill='both', expand=True, pady=10)

    

    def browse_cover_image(self):

        """Browse for cover image"""

        filename = filedialog.askopenfilename(

            title="Select Cover Image",

            filetypes=[("Image files", ".png .jpg *.jpeg *.bmp *.tiff"), ("All files", ".")]

        )

        if filename:

            self.cover_image_var.set(filename)

    

    def browse_output_path(self):

        """Browse for output path"""

        filename = filedialog.asksaveasfilename(

            title="Save Steganographic Image",

            defaultextension=".png",

            filetypes=[("PNG files", ".png"), ("All files", ".*")]

        )

        if filename:

            self.output_path_var.set(filename)

    

    def browse_stego_image(self):

        """Browse for steganographic image"""

        filename = filedialog.askopenfilename(

            title="Select Steganographic Image",

            filetypes=[("Image files", ".png .jpg *.jpeg *.bmp *.tiff"), ("All files", ".")]

        )

        if filename:

            self.stego_image_var.set(filename)

    

    def browse_info_image(self):

        """Browse for image to analyze"""

        filename = filedialog.askopenfilename(

            title="Select Image to Analyze",

            filetypes=[("Image files", ".png .jpg *.jpeg *.bmp *.tiff"), ("All files", ".")]

        )

        if filename:

            self.info_image_var.set(filename)

    

    def encode_message(self):

        """Encode message into image"""

        if not self.cover_image_var.get():

            messagebox.showerror("Error", "Please select a cover image")

            return

        

        if not self.output_path_var.get():

            messagebox.showerror("Error", "Please specify output path")

            return

        

        message = self.message_text.get("1.0", tk.END).strip()

        if not message:

            messagebox.showerror("Error", "Please enter a message to hide")

            return

        

        password = self.password_var.get() if self.password_var.get() else None

        

        success, result = self.stego.encode_message(

            self.cover_image_var.get(),

            message,

            self.output_path_var.get(),

            password

        )

        

        if success:

            messagebox.showinfo("Success", result)

        else:

            messagebox.showerror("Error", result)

    

    def decode_message(self):

        """Decode message from image"""

        if not self.stego_image_var.get():

            messagebox.showerror("Error", "Please select a steganographic image")

            return

        

        password = self.decode_password_var.get() if self.decode_password_var.get() else None

        

        success, result = self.stego.decode_message(

            self.stego_image_var.get(),

            password

        )

        

        self.revealed_text.delete("1.0", tk.END)

        

        if success:

            self.revealed_text.insert("1.0", result)

            messagebox.showinfo("Success", "Message revealed successfully!")

        else:

            self.revealed_text.insert("1.0", f"Error: {result}")

    

    def analyze_image(self):

        """Analyze image capacity"""

        if not self.info_image_var.get():

            messagebox.showerror("Error", "Please select an image to analyze")

            return

        

        info = self.stego.get_image_info(self.info_image_var.get())

        

        self.info_text.delete("1.0", tk.END)

        

        if info:

            analysis = f"""IMAGE ANALYSIS REPORT

{'='*50}



File: {os.path.basename(self.info_image_var.get())}

Format: {info['format']}

Dimensions: {info['width']} x {info['height']} pixels

Total Pixels: {info['total_pixels']:,}



STEGANOGRAPHY CAPACITY:

Maximum Characters: {info['max_characters']:,}

Maximum Message Size: {info['max_characters'] / 1024:.2f} KB



EXAMPLES:

- Short message (100 chars): {(100 / info['max_characters'] * 100):.2f}% capacity

- Medium message (1000 chars): {(1000 / info['max_characters'] * 100):.2f}% capacity

- Large message (10000 chars): {(10000 / info['max_characters'] * 100):.2f}% capacity



RECOMMENDATIONS:

- Use PNG format for best results

- Keep message size under 50% of capacity

- Larger images = more hiding capacity

- Complex images hide changes better

"""

            self.info_text.insert("1.0", analysis)

        else:

            self.info_text.insert("1.0", "Error analyzing image")

    

    def run(self):

        """Run the GUI application"""

        



def command_line_interface():

    """Command line interface for steganography"""

    parser = argparse.ArgumentParser(description="Image Steganography Tool")

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    

    # Encode command

    encode_parser = subparsers.add_parser('encode', help='Hide message in image')

    encode_parser.add_argument('-i', '--input', required=True, help='Input cover image')

    encode_parser.add_argument('-m', '--message', help='Message to hide')

    encode_parser.add_argument('-f', '--file', help='Text file containing message')

    encode_parser.add_argument('-o', '--output', required=True, help='Output image path')

    encode_parser.add_argument('-p', '--password', help='Password protection')

    

    # Decode command

    decode_parser = subparsers.add_parser('decode', help='Reveal message from image')

    decode_parser.add_argument('-i', '--input', required=True, help='Steganographic image')

    decode_parser.add_argument('-p', '--password', help='Password for decoding')

    

    # Info command

    info_parser = subparsers.add_parser('info', help='Get image information')

    info_parser.add_argument('-i', '--input', required=True, help='Image to analyze')

    

    args = parser.parse_args()

    

    if not args.command:

        parser.print_help()

        return

    

    stego = ImageSteganography()

    

    if args.command == 'encode':

        if args.message:

            message = args.message

        elif args.file:

            with open(args.file, 'r') as f:

                message = f.read()

        else:

            print("Error: Provide message with -m or file with -f")

            return

        

        success, result = stego.encode_message(args.input, message, args.output, args.password)

        print(result)

    

    elif args.command == 'decode':

        success, result = stego.decode_message(args.input, args.password)

        if success:

            print("Hidden message:")

            print("-" * 40)

            print(result)

            print("-" * 40)

        else:

            print(f"Error: {result}")

    

    elif args.command == 'info':

        info = stego.get_image_info(args.input)

        if info:

            print(f"Image: {args.input}")

            print(f"Dimensions: {info['width']}x{info['height']}")

            print(f"Format: {info['format']}")

            print(f"Maximum capacity: {info['max_characters']} characters")

        else:

            print("Error analyzing image")



if __name__ == "__main__":

    if len(sys.argv) > 1:

        print('Command line mode')

        command_line_interface()

    else:

        # GUI mode
        print("GUI mode")
        app = SteganographyGUI()
        app.run()
