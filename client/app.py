import tkinter as tk
from tkinter import messagebox
import requests

API_URL = "http://localhost:8000"
token = None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Microservices Client")
        self.geometry("600x500")
        self.show_login()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def show_login(self):
        self.clear()

        tk.Label(self, text="Username").pack()
        username = tk.Entry(self)
        username.pack()

        tk.Label(self, text="Password").pack()
        password = tk.Entry(self, show="*")
        password.pack()

        def login():
            global token
            r = requests.post(
                f"{API_URL}/auth/login",
                json={
                    "username": username.get(),
                    "password": password.get()
                }
            )
            if r.status_code == 200:
                token = r.json()["access_token"]
                self.show_menu()
            else:
                messagebox.showerror("Error", "Login failed")

        def register():
            r = requests.post(
                f"{API_URL}/auth/register",
                json={
                    "username": username.get(),
                    "password": password.get()
                }
            )
            if r.status_code == 200:
                messagebox.showinfo("OK", "Registered, now login")
            else:
                messagebox.showerror("Error", "Register failed")

        tk.Button(self, text="Login", command=login).pack(pady=5)
        tk.Button(self, text="Register", command=register).pack(pady=5)

    def show_menu(self):
        self.clear()

        tk.Button(self, text="Items", width=20, command=self.show_items).pack(pady=10)
        tk.Button(self, text="Logs", width=20, command=self.show_logs).pack(pady=10)
        tk.Button(self, text="Logout", width=20, command=self.show_login).pack(pady=10)

    def show_items(self):
        self.clear()

        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(f"{API_URL}/crud/items", headers=headers)

        if r.status_code != 200:
            messagebox.showerror("Error", "Unauthorized")
            self.show_menu()
            return

        items = r.json()

        listbox = tk.Listbox(self, width=70)
        listbox.pack(pady=10)

        for i in items:
            listbox.insert(
                tk.END,
                f'{i["id"]} | {i["name"]} | {i["description"]}'
            )

        tk.Label(self, text="Item name").pack()
        name = tk.Entry(self, width=40)
        name.pack()

        tk.Label(self, text="Description").pack()
        desc = tk.Entry(self, width=40)
        desc.pack()

        def refresh():
            self.show_items()

        def add_item():
            requests.post(
                f"{API_URL}/crud/items",
                headers=headers,
                json={"name": name.get(), "description": desc.get()}
            )
            refresh()

        def update_item():
            if not listbox.curselection():
                return
            item_id = listbox.get(listbox.curselection()).split("|")[0].strip()
            requests.put(
                f"{API_URL}/crud/items/{item_id}",
                headers=headers,
                json={"name": name.get(), "description": desc.get()}
            )
            refresh()

        def delete_item():
            if not listbox.curselection():
                return
            item_id = listbox.get(listbox.curselection()).split("|")[0].strip()
            requests.delete(
                f"{API_URL}/crud/items/{item_id}",
                headers=headers
            )
            refresh()

        tk.Button(self, text="Add", command=add_item).pack(pady=3)
        tk.Button(self, text="Update", command=update_item).pack(pady=3)
        tk.Button(self, text="Delete", command=delete_item).pack(pady=3)
        tk.Button(self, text="Back", command=self.show_menu).pack(pady=10)

    def show_logs(self):
        self.clear()

        r = requests.get(f"{API_URL}/logs/logs")
        logs = r.json()

        listbox = tk.Listbox(self, width=90)
        listbox.pack(pady=10)

        for l in logs:
            listbox.insert(
                tk.END,
                f'user {l["user_id"]} | {l["action"]} | {l["created_at"]}'
            )

        tk.Button(self, text="Back", command=self.show_menu).pack(pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
