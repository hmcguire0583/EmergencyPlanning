import tkinter as tk
from tkinter import filedialog, messagebox
import json
from logistic_solver import compute_routes, visualize_routes

class RouteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Disaster Delivery Optimizer")
        self.root.geometry("900x600")
        self.filename = None

        tk.Button(root, text="Select JSON File", command=self.select_file).pack(pady=10)
        self.file_label = tk.Label(root, text="No file chosen")
        self.file_label.pack(pady=5)
        tk.Button(root, text="Compute Routes", command=self.run_solver).pack(pady=10)

        self.results_text = tk.Text(root, height=32, width=100)
        self.results_text.pack(pady=10)

    def select_file(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filename:
            self.filename = filename
            self.file_label.config(text=filename)
        else:
            self.file_label.config(text="No file chosen")

    def run_solver(self):
        if not self.filename:
            messagebox.showerror("Error", "Please select a JSON file first.")
            return
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        output, truck_routes = compute_routes(data)
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert(tk.END, output)

        # Plot graph
        visualize_routes(data, truck_routes)


if __name__ == "__main__":
    root = tk.Tk()
    app = RouteApp(root)
    root.mainloop()
