import tkinter as tk
from datetime import datetime
from tkinter import simpledialog, messagebox, ttk

from email_validator import validate_email, EmailNotValidError
from pymongo import MongoClient
from pymongo.errors import OperationFailure

MONGO_URI = "mongodb://{}:{}@localhost:27017/"
USERS = {
    "Read Only": ("readonlyuser", "12345678"),
    "Read/Write": ("readwriteuser", "12345678"),
    "Admin": ("adminuser", "root")
}
COLLECTIONS = {
    "users": [("name", str), ("email", str)],
    "coupons": [("code", str), ("discount_percentage", float), ("expiration_date", str)]
}


class MongoDBApp:
    def __init__(self):
        self.vertical_scrollbar = None
        self.collection_name = None
        self.output_text = None
        self.crud_buttons_frame = None
        self.fields_frame = None
        self.collection_combobox = None
        self.collection_var = None
        self.entries = None
        self.client = None
        self.db = None
        self.root = tk.Tk()
        self.root.title("MongoDB Login")
        tk.Label(self.root, text="Select User").pack(pady=10)
        for user_type in USERS:
            btn = tk.Button(self.root, text=user_type, command=lambda user=user_type: self.login(user))
            btn.pack(pady=5)
        self.root.mainloop()

    def login(self, user_type):
        username, password = USERS[user_type]
        pwd = simpledialog.askstring("Password", "Enter the password of the {} user: ".format(user_type), show='*')
        if pwd == password:
            self.client = MongoClient(MONGO_URI.format(username, password))
            self.db = self.client['testDB']
            test_collection = self.db['users']
            try:
                test_collection.find_one({"name": "Muhab", "email": "mohaboko31@gmail.com"})
            except OperationFailure as e:
                self.client = None
                self.db = None
                messagebox.showerror("Login Failed", "Incorrect username or password.\n" + str(e))
                return
            messagebox.showinfo("Login Success", "Logged in as {} user.".format(user_type))
            self.show_crud_interface()
        else:
            messagebox.showerror("Login Failed", "Incorrect password.")

    def create(self):
        if self.collection_name == "users":
            name = self.entries['name'].get()
            if not name:
                messagebox.showerror("Update Failed", "The name field cannot be empty.")
                return
            email = self.entries['email'].get()
            if not email:
                messagebox.showerror("Update Failed", "The email field cannot be empty.")
                return
            try:
                validate_email(email)
            except EmailNotValidError:
                messagebox.showerror("Update Failed", "The email must be a valid email.")
                return
            document = {"name": name, "email": email}
        else:
            code = self.entries['code'].get()
            if not code:
                messagebox.showerror("Update Failed", "The code field cannot be empty.")
                return
            discount_percentage = self.entries['discount_percentage'].get()
            if not discount_percentage:
                messagebox.showerror("Update Failed", "The discount percentage field cannot be empty.")
                return
            try:
                discount_percentage = float(discount_percentage)
            except ValueError:
                messagebox.showerror("Update Failed", "The discount percentage must be a valid number.")
                return
            expiration_date = self.entries['expiration_date'].get()
            if not expiration_date:
                messagebox.showerror("Update Failed", "The expiration date field cannot be empty.")
                return
            try:
                datetime.strptime(expiration_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Update Failed", "The expiration date must be a valid date (YYYY-MM-DD).")
                return
            document = {"code": code, "discount_percentage": discount_percentage,
                        "expiration_date": expiration_date}
        try:
            result = self.db[self.collection_name].insert_one(document)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Inserted document ID: {result.inserted_id}.")
            self.read()
        except OperationFailure:
            if self.collection_name == "users":
                messagebox.showerror("Create Failed",
                                     "The user roles with which you are logged in do not permit you to "
                                     "perform this operation, or the new email you entered is not unique.")
            else:
                messagebox.showerror("Create Failed",
                                     "The user roles with which you are logged in do not permit you to "
                                     "perform this operation, or the new code you entered is not unique.")

    def read(self):
        try:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, list(self.db[self.collection_name].find({})))
        except OperationFailure:
            messagebox.showerror("Read Failed", "The user roles with which you are logged in do not permit you to "
                                                "perform this operation.")

    def update(self):
        if self.collection_name == "users":
            name = self.entries['name'].get()
            if not name:
                messagebox.showerror("Update Failed", "The name field cannot be empty.")
                return
            email = self.entries['email'].get()
            if not email:
                messagebox.showerror("Update Failed", "The email field cannot be empty.")
                return
            user_exist = self.db[self.collection_name].find({"name": name, "email": email})
            if len(list(user_exist)) == 0:
                messagebox.showerror("Update Failed", "Cannot find a user with the name and email you entered.")
                return
            filter_query = {"name": name, "email": email}
            new_name = simpledialog.askstring("The new name", "Enter the new name:")
            if not new_name:
                messagebox.showerror("Update Failed", "The new name cannot be empty.")
                return
            new_email = simpledialog.askstring("The new email", "Enter the new email:")
            if not new_email:
                messagebox.showerror("Update Failed", "The new email cannot be empty.")
                return
            try:
                validate_email(new_email)
            except EmailNotValidError:
                messagebox.showerror("Update Failed", "The new email must be a valid email.")
                return
            update_query = {"$set": {"name": new_name, "email": new_email}}
        else:
            code = self.entries['code'].get()
            if not code:
                messagebox.showerror("Update Failed", "The code field cannot be empty.")
                return
            discount_percentage = self.entries['discount_percentage'].get()
            if not discount_percentage:
                messagebox.showerror("Update Failed", "The discount percentage field cannot be empty.")
                return
            try:
                discount_percentage = float(discount_percentage)
            except ValueError:
                messagebox.showerror("Update Failed", "The discount percentage must be a valid number.")
                return
            expiration_date = self.entries['expiration_date'].get()
            if not expiration_date:
                messagebox.showerror("Update Failed", "The expiration date field cannot be empty.")
                return
            try:
                datetime.strptime(expiration_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Update Failed", "The expiration date must be a valid date (YYYY-MM-DD).")
                return
            coupon_exist = self.db[self.collection_name].find(
                {"code": code, "discount_percentage": discount_percentage,
                 "expiration_date": expiration_date})
            if len(list(coupon_exist)) == 0:
                messagebox.showerror("Update Failed",
                                     "Cannot find a coupon with the code, discount percentage and expiration_date you "
                                     "entered.")
                return
            filter_query = {"code": code, "discount_percentage": discount_percentage,
                            "expiration_date": expiration_date}
            new_code = simpledialog.askstring("The new code", "Enter the new code:")
            if not new_code:
                messagebox.showerror("Update Failed", "The new code cannot be empty.")
                return
            new_discount_percentage = simpledialog.askstring("The new discount percentage", "Enter the new discount "
                                                                                            "percentage:")
            if not new_discount_percentage:
                messagebox.showerror("Update Failed", "The new discount percentage cannot be empty.")
                return
            try:
                new_discount_percentage = float(new_discount_percentage)
            except ValueError:
                messagebox.showerror("Update Failed", "The new discount percentage must be a valid number.")
                return
            new_expiration_date = simpledialog.askstring("The new expiration date", "Enter the new expiration date:")
            if not new_expiration_date:
                messagebox.showerror("Update Failed", "The new expiration date cannot be empty.")
                return
            try:
                datetime.strptime(new_expiration_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Update Failed", "The new expiration date must be a valid date (YYYY-MM-DD).")
                return
            update_query = {"$set": {"code": new_code, "discount_percentage": new_discount_percentage,
                                     "expiration_date": new_expiration_date}}
        try:
            result = self.db[self.collection_name].update_one(filter_query, update_query)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Modified {result.modified_count} documents.\n")
            self.read()
        except OperationFailure:
            if self.collection_name == "users":
                messagebox.showerror("Update Failed",
                                     "The user roles with which you are logged in do not permit you to "
                                     "perform this operation, or the new email you entered is not unique.")
            else:
                messagebox.showerror("Update Failed",
                                     "The user roles with which you are logged in do not permit you to "
                                     "perform this operation, or the new code you entered is not unique.")

    def delete(self):
        if self.collection_name == "users":
            name = self.entries['name'].get()
            if not name:
                messagebox.showerror("Update Failed", "The name field cannot be empty.")
                return
            filter_query = {"name": name}
        else:
            code = self.entries['code'].get()
            if not code:
                messagebox.showerror("Update Failed", "The code field cannot be empty.")
                return
            filter_query = {"code": code}
        try:
            result = self.db[self.collection_name].delete_one(filter_query)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Deleted {result.deleted_count} documents.")
            self.read()
        except OperationFailure:
            messagebox.showerror("Delete Failed", "The user roles with which you are logged in do not permit you to "
                                                  "perform this operation.")

    def show_crud_interface(self):
        crud_window = tk.Toplevel(self.root)
        crud_window.title("CRUD Operations")
        tk.Label(crud_window, text="Select Collection:").grid(row=0, column=0, padx=10, pady=5)
        self.collection_var = tk.StringVar()
        self.collection_combobox = ttk.Combobox(crud_window, textvariable=self.collection_var,
                                                values=list(COLLECTIONS.keys()))
        self.collection_combobox.grid(row=0, column=1, padx=10, pady=5)
        self.collection_combobox.bind("<<ComboboxSelected>>", self.update_fields)
        self.fields_frame = tk.Frame(crud_window)
        self.fields_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        self.crud_buttons_frame = tk.Frame(crud_window)
        self.crud_buttons_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        self.output_text = tk.Text(crud_window, height=10, width=50)
        self.vertical_scrollbar = ttk.Scrollbar(crud_window, command=self.output_text.yview)
        self.output_text.config(yscrollcommand=self.vertical_scrollbar.set)
        self.output_text.grid(row=3, column=0, columnspan=2, padx=10, pady=5)
        self.vertical_scrollbar.grid(row=3, column=2, sticky='NSE')
        self.update_fields()

    def update_fields(self, event=None):
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.collection_name = self.collection_var.get()
        if not self.collection_name:
            return
        self.entries = {}
        for idx, (field_name, field_type) in enumerate(COLLECTIONS[self.collection_name]):
            tk.Label(self.fields_frame, text=field_name.replace("_", " ") + ":").grid(row=idx, column=0, padx=5, pady=5)
            entry = tk.Entry(self.fields_frame)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            self.entries[field_name] = entry
        for widget in self.crud_buttons_frame.winfo_children():
            widget.destroy()
        tk.Button(self.crud_buttons_frame, text="Create", command=self.create).pack(side=tk.LEFT, padx=5,
                                                                                    pady=5)
        tk.Button(self.crud_buttons_frame, text="Read", command=self.read).pack(side=tk.LEFT, padx=5,
                                                                                pady=5)
        tk.Button(self.crud_buttons_frame, text="Update", command=self.update).pack(side=tk.LEFT, padx=5,
                                                                                    pady=5)
        tk.Button(self.crud_buttons_frame, text="Delete", command=self.delete).pack(side=tk.LEFT, padx=5,
                                                                                    pady=5)


if __name__ == "__main__":
    mongoDBApp = MongoDBApp()
