import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from blockchain import Blockchain
from file_manager import compute_file_hash
import os

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blockchain Data Integrity System")
        self.geometry("1050x600")
        self.configure(bg="#121212")

        self.blockchain = Blockchain()
        self.selected_file = None
        self.file_hash = None

        self.create_widgets()
        self.refresh_chain_view()

    def create_widgets(self):
        left = tk.Frame(self, bg="#1F1F1F", padx=20, pady=20, width=300)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        tk.Label(left, text="File:", fg="#FFF", bg="#1F1F1F", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        self.file_label = tk.Label(left, text="No file selected", fg="#BBB", bg="#1F1F1F", wraplength=260, font=("Segoe UI", 11))
        self.file_label.pack(anchor=tk.W, pady=(0,10))

        btn_style = {"bg":"#333", "fg":"#FFF", "activebackground":"#555", "bd":0, "height":2, "width":22, "font":("Segoe UI",11,"bold")}

        tk.Button(left, text="Choose File", command=self.choose_file, **btn_style).pack(pady=5)
        tk.Button(left, text="Compute Hash", command=self.compute_hash, **btn_style).pack(pady=5)
        self.progress = ttk.Progressbar(left, orient="horizontal", length=260, mode="determinate")
        self.progress.pack(fill=tk.X, pady=5)
        tk.Button(left, text="Add to Blockchain", command=self.add_to_chain, **btn_style).pack(pady=5)

        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        tk.Button(left, text="Verify Blockchain", command=self.verify_chain, **btn_style).pack(pady=5)
        tk.Button(left, text="Save Chain", command=self.save_chain, **btn_style).pack(pady=5)
        tk.Button(left, text="Load Chain", command=self.load_chain, **btn_style).pack(pady=5)
        tk.Button(left, text="Simulate Tamper", command=self.simulate_tamper, **btn_style).pack(pady=5)

        right = tk.Frame(self, bg="#121212", padx=10, pady=10)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        columns = ("index", "timestamp", "file_name", "file_hash")
        self.tree = ttk.Treeview(right, columns=columns, show="headings", height=22)
        vsb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        for col, w in zip(columns, [70, 200, 250, 300]):
            self.tree.heading(col, text=col.title(), anchor=tk.W)
            self.tree.column(col, width=w, anchor=tk.W, stretch=True)

        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=30)
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

        self.tree.bind("<<TreeviewSelect>>", self.on_select_block)

        self.tree.tag_configure("valid", background="#003300", foreground="#FFFFFF")
        self.tree.tag_configure("tampered", background="#330000", foreground="#FFFFFF")

        self.details = tk.Text(right, height=8, bg="#1F1F1F", fg="#EEE", insertbackground="#EEE", font=("Segoe UI", 11))
        self.details.pack(fill=tk.X, pady=10)

    def choose_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.selected_file = path
            self.file_label.config(text=os.path.basename(path))
            self.file_hash = None
            self.progress['value'] = 0

    def compute_hash(self):
        if not self.selected_file:
            messagebox.showwarning("Warning", "Choose a file first.")
            return
        self.progress['value'] = 0
        self.file_hash = None
        threading.Thread(target=self._compute_hash_thread, daemon=True).start()

    def _compute_hash_thread(self):
        def cb(read, total):
            self.progress['maximum'] = total
            self.progress['value'] = read
        try:
            h = compute_file_hash(self.selected_file, progress_callback=cb)
            self.file_hash = h
            self.details_insert(f"Computed SHA-256: {h}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ----- Blockchain operations -----
    def add_to_chain(self):
        if not self.file_hash or not self.selected_file:
            messagebox.showwarning("Warning", "Compute hash first.")
            return
        block = self.blockchain.add_block(os.path.basename(self.selected_file), self.file_hash)
        self.details_insert(f"Added block {block.index}\n")
        self.refresh_chain_view()

    def refresh_chain_view(self):
        self.tree.delete(*self.tree.get_children())
        for i, b in enumerate(self.blockchain.chain):
            tag = "valid"
            if i > 0 and self.blockchain.chain[i].previous_hash != self.blockchain.chain[i-1].hash:
                tag = "tampered"
            self.tree.insert("", tk.END, values=(
                b.index,
                b.timestamp,
                b.file_name,
                b.hash[:20]+"..."
            ), tags=(tag,))

    def verify_chain(self):
        valid, msg = self.blockchain.is_valid()
        messagebox.showinfo("Verification", "Blockchain is valid ✅" if valid else f"Invalid chain ❌\n{msg}")
        self.refresh_chain_view()

    def save_chain(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if path:
            try:
                import json
                data = [vars(b) for b in self.blockchain.chain]
                with open(path, "w") as f:
                    json.dump(data, f, indent=2)
                messagebox.showinfo("Saved", "Chain saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_chain(self):
        path = filedialog.askopenfilename(filetypes=[("JSON","*.json")])
        if path:
            try:
                import json
                with open(path, "r") as f:
                    arr = json.load(f)
                self.blockchain.load_from_list(arr)
                self.refresh_chain_view()
                messagebox.showinfo("Loaded", "Chain loaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def simulate_tamper(self):
        if len(self.blockchain.chain) > 1:
            self.blockchain.chain[1].file_name += "_TAMPERED"
            self.refresh_chain_view()
            messagebox.showwarning("Tamper", "Block 1 modified (tamper simulated).")
        else:
            messagebox.showinfo("Info", "Add at least one block first.")

    # ----- Tree selection -----
    def on_select_block(self, event):
        sel = self.tree.selection()
        if not sel: return
        idx = int(self.tree.item(sel[0])['values'][0])
        b = self.blockchain.chain[idx]
        self.details.delete("1.0", tk.END)
        self.details.insert(tk.END,
            f"Index: {b.index}\n"
            f"Timestamp: {b.timestamp}\n"
            f"File Name: {b.file_name}\n"
            f"File Hash: {b.file_hash}\n"
            f"Previous Hash: {b.previous_hash}\n"
            f"Block Hash: {b.hash}\n"
        )

    def details_insert(self, text):
        self.details.insert(tk.END, text)
        self.details.see(tk.END)

if __name__ == "__main__":
    app = App()
    app.mainloop()
