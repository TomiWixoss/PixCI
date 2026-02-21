import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import subprocess
import sys
import traceback

# Add pixci to path so we can import it
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pixci.core.grid_engine import encode_image, encode_code, decode_text
    from pixci.core.pxvg_engine import encode_pxvg, decode_pxvg
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import pixci modules: {e}")

class PixCIGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PixCI GUI")
        self.geometry("600x500")
        
        # Style
        style = ttk.Style(self)
        style.theme_use('clam')
        
        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Encode (Image -> Text/XML)
        self.encode_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.encode_frame, text="Encode (Ảnh -> Text/PXVG)")
        
        # Tab 2: Decode (Text/XML -> Image)
        self.decode_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.decode_frame, text="Decode (Text/PXVG -> Ảnh)")
        
        # Tab 3: Run Script (Python -> Image)
        self.run_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.run_frame, text="Run Script (Py -> Ảnh)")
        
        self.setup_encode_tab()
        self.setup_decode_tab()
        self.setup_run_tab()

    def setup_encode_tab(self):
        # Input
        ttk.Label(self.encode_frame, text="Ảnh đầu vào (.png, .jpg):").grid(row=0, column=0, sticky="w", padx=5, pady=10)
        self.enc_input_var = tk.StringVar()
        ttk.Entry(self.encode_frame, textvariable=self.enc_input_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(self.encode_frame, text="Browse...", command=lambda: self.browse_file(self.enc_input_var, [("Images", "*.png *.jpg *.jpeg")])).grid(row=0, column=2, padx=5)
        
        # Output
        ttk.Label(self.encode_frame, text="Thư mục đầu ra:").grid(row=1, column=0, sticky="w", padx=5, pady=10)
        self.enc_output_var = tk.StringVar()
        ttk.Entry(self.encode_frame, textvariable=self.enc_output_var, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(self.encode_frame, text="Browse...", command=lambda: self.browse_dir(self.enc_output_var)).grid(row=1, column=2, padx=5)
        
        # Format
        ttk.Label(self.encode_frame, text="Định dạng:").grid(row=2, column=0, sticky="w", padx=5, pady=10)
        self.enc_format_var = tk.StringVar(value="grid")
        formats = ["grid", "code", "code (minecraft)", "pxvg"]
        ttk.Combobox(self.encode_frame, textvariable=self.enc_format_var, values=formats, state="readonly").grid(row=2, column=1, sticky="w", padx=5)
        
        # Auto Block Size
        self.enc_auto_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.encode_frame, text="Tự động phát hiện kích thước block (Auto)", variable=self.enc_auto_var).grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Encode Button
        ttk.Button(self.encode_frame, text="Bắt đầu Encode", command=self.do_encode).grid(row=4, column=1, pady=20)

    def setup_decode_tab(self):
        # Input
        ttk.Label(self.decode_frame, text="Text/PXVG đầu vào:").grid(row=0, column=0, sticky="w", padx=5, pady=10)
        self.dec_input_var = tk.StringVar()
        ttk.Entry(self.decode_frame, textvariable=self.dec_input_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(self.decode_frame, text="Browse...", command=lambda: self.browse_file(self.dec_input_var, [("Text/XML", "*.txt *.xml *.pxvg")])).grid(row=0, column=2, padx=5)
        
        # Output
        ttk.Label(self.decode_frame, text="Thư mục đầu ra:").grid(row=1, column=0, sticky="w", padx=5, pady=10)
        self.dec_output_var = tk.StringVar()
        ttk.Entry(self.decode_frame, textvariable=self.dec_output_var, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(self.decode_frame, text="Browse...", command=lambda: self.browse_dir(self.dec_output_var)).grid(row=1, column=2, padx=5)
        
        # Scale
        ttk.Label(self.decode_frame, text="Scale (phóng to):").grid(row=2, column=0, sticky="w", padx=5, pady=10)
        self.dec_scale_var = tk.IntVar(value=1)
        ttk.Spinbox(self.decode_frame, from_=1, to=20, textvariable=self.dec_scale_var, width=10).grid(row=2, column=1, sticky="w", padx=5)
        
        # Decode Button
        ttk.Button(self.decode_frame, text="Bắt đầu Decode", command=self.do_decode).grid(row=3, column=1, pady=20)
        
    def setup_run_tab(self):
        # Input
        ttk.Label(self.run_frame, text="Script Python (.py):").grid(row=0, column=0, sticky="w", padx=5, pady=10)
        self.run_input_var = tk.StringVar()
        ttk.Entry(self.run_frame, textvariable=self.run_input_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(self.run_frame, text="Browse...", command=lambda: self.browse_file(self.run_input_var, [("Python Files", "*.py")])).grid(row=0, column=2, padx=5)
        
        # Scale
        ttk.Label(self.run_frame, text="Scale (PIXCI_SCALE):").grid(row=1, column=0, sticky="w", padx=5, pady=10)
        self.run_scale_var = tk.IntVar(value=1)
        ttk.Spinbox(self.run_frame, from_=1, to=20, textvariable=self.run_scale_var, width=10).grid(row=1, column=1, sticky="w", padx=5)
        
        # Run Button
        ttk.Button(self.run_frame, text="Chạy Script", command=self.do_run).grid(row=2, column=1, pady=20)

    def browse_file(self, string_var, filetypes):
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            string_var.set(filename)
            
    def browse_dir(self, string_var):
        dirname = filedialog.askdirectory()
        if dirname:
            string_var.set(dirname)

    def do_encode(self):
        input_path = self.enc_input_var.get()
        output_dir = self.enc_output_var.get()
        fmt = self.enc_format_var.get()
        auto = self.enc_auto_var.get()
        
        if not input_path or not output_dir:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn file đầu vào và thư mục đầu ra")
            return
            
        in_p = Path(input_path)
        out_d = Path(output_dir)
        
        if not in_p.exists():
            messagebox.showerror("Lỗi", "File đầu vào không tồn tại!")
            return
            
        try:
            if fmt == "pxvg":
                out_p = out_d / (in_p.stem + ".pxvg.xml")
                grid_w, grid_h, num_colors, final_block = encode_pxvg(in_p, out_p, block_size=1, auto_detect=auto)
            elif fmt == "code (minecraft)":
                out_p = out_d / (in_p.stem + ".txt")
                from pixci.styles.minecraft import MinecraftStyle
                grid_w, grid_h, num_colors, final_block = MinecraftStyle.encode(in_p, out_p, block_size=1, auto_detect=auto)
            elif fmt == "code":
                out_p = out_d / (in_p.stem + ".txt")
                grid_w, grid_h, num_colors, final_block = encode_code(in_p, out_p, block_size=1, auto_detect=auto)
            else: # grid
                out_p = out_d / (in_p.stem + ".txt")
                grid_w, grid_h, num_colors, final_block = encode_image(in_p, out_p, block_size=1, auto_detect=auto)
                
            msg = f"Đã encode thành công!\nFile: {out_p}\nKích thước: {grid_w}x{grid_h}\nSố màu: {num_colors}\nBlock size: {final_block}"
            messagebox.showinfo("Thành công", msg)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Lỗi Encode", str(e))

    def do_decode(self):
        input_path = self.dec_input_var.get()
        output_dir = self.dec_output_var.get()
        scale = self.dec_scale_var.get()
        
        if not input_path or not output_dir:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn file đầu vào và thư mục đầu ra")
            return
            
        in_p = Path(input_path)
        out_d = Path(output_dir)
        
        if not in_p.exists():
            messagebox.showerror("Lỗi", "File đầu vào không tồn tại!")
            return
            
        try:
            out_p = out_d / (in_p.stem + ".png")
            
            if in_p.suffix.lower() in [".pxvg", ".xml"]:
                w, h = decode_pxvg(in_p, out_p, scale)
            else:
                w, h = decode_text(in_p, out_p, scale)
                
            msg = f"Đã decode thành công!\nFile: {out_p}\nKích thước gốc: {w}x{h}\nScale: {scale}x"
            messagebox.showinfo("Thành công", msg)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Lỗi Decode", str(e))
            
    def do_run(self):
        script_path = self.run_input_var.get()
        scale = self.run_scale_var.get()
        
        if not script_path:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn file Python")
            return
            
        sp = Path(script_path)
        if not sp.exists():
            messagebox.showerror("Lỗi", "File script không tồn tại!")
            return
            
        env = os.environ.copy()
        current_dir = os.getcwd()
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{current_dir}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = current_dir

        if scale > 1:
            env["PIXCI_SCALE"] = str(scale)
            
        try:
            result = subprocess.run([sys.executable, str(sp)], env=env, capture_output=True, text=True, cwd=sp.parent)
            if result.returncode != 0:
                messagebox.showerror("Lỗi khi chạy Code", result.stderr)
            else:
                messagebox.showinfo("Chạy thành công", result.stdout if result.stdout else "Script chạy thành công nhưng không in ra gì.")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Lỗi Thực thi", str(e))

if __name__ == "__main__":
    app = PixCIGUI()
    app.mainloop()
