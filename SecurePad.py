import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import pyzipper

file_path = ""
search_start = "1.0"
if len(sys.argv) > 1:
    file_path = sys.argv[1]

# Function to open the zip file and extract the text file
def open_zip(file_path, password):
    try:
        with pyzipper.AESZipFile(file_path, 'r', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zip_file:
            zip_file.pwd = password.encode()
            with zip_file.open('content.txt') as text_file:
                decrypted_text = text_file.read().decode('utf-8')
                text_box.delete("1.0", END)
                text_box.insert(END, decrypted_text)
                password_entry.config(state='disabled')
    except Exception as e:
        password_entry.config(state='normal')
        messagebox.showerror("Error", f"Error opening file: {e}")

# Function to save the text file to a password-protected zip
def save_zip(file_path, password):
    try:
        encrypted_text = text_box.get("1.0",'end-1c')
        with pyzipper.AESZipFile(file_path, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zip_file:
            zip_file.pwd = password.encode()
            with zip_file.open('content.txt', mode='w') as text_file:
                text_file.write(encrypted_text.encode('utf-8'))
            root.title("SecurePad - "+file_path)
            password_entry.config(state='disabled')
    except Exception as e:
        messagebox.showerror("Error", f"Error saving file: {e}")

# Function to handle the open button click event
def open_file():
    global file_path  
    if os.path.isfile(file_path):
        password = password_entry.get()
        open_zip(file_path, password)
        root.title("SecurePad - "+file_path)
    elif len(file_path)>0:
        messagebox.showerror("Info", "File not found, it will be created on your next save.")
    else:
        messagebox.showerror("Info", "You will be prompted for a file location when you next save.")
        
def open_butt():
    global file_path
    if(len(password_entry.get())<1):
        messagebox.showerror("Info", "Please enter your password before selecting a file.")
    else:
        file_path = filedialog.askopenfilename(filetypes=[("Zip Files", "*.zip")])
        open_file()
# Function to handle the save button click event
def save_file(event=None):
    global file_path
    if(len(file_path)==0):
        file_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Zip Files", "*.zip")])
    password = password_entry.get()
    save_zip(file_path, password)

def on_key_press(event):
    if event.keysym == 'Return':  # Check if Enter key is pressed
        open_file()

def search_text(event=None):
    global search_start
    search_term = search_entry.get()
    print(search_term)
    if search_term:
        start_pos = search_start
        start_pos = text_box.search(search_term, start_pos, stopindex=END)
        if not start_pos and search_start != "1.0":
            # Wrap around to the beginning if not found and not at the start
            start_pos = text_box.search(search_term, "1.0", stopindex=END)
        if start_pos:
            end_pos = f"{start_pos}+{len(search_term)}c"
            text_box.tag_remove("highlight", "1.0", END)
            text_box.tag_add("highlight", start_pos, end_pos)
            text_box.tag_configure("highlight", background="yellow")
            text_box.see(start_pos)
            search_start = f"{start_pos}+{len(search_term)}c"

def unsaved(event = None):
    root.title("SecurePad - "+file_path+ "*")
    
root = Tk()
root.title("SecurePad - "+file_path)

# Search Entry and Binding
# Create the left frame for password entry and buttons
left_frame = Frame(root)
left_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')

# Password Entry and Buttons
password_label = Label(left_frame, text="Enter Password:")
password_label.grid(row=0, column=0, padx=5)
password_entry = Entry(left_frame, show='*')
password_entry.grid(row=0, column=1, padx=5)
password_entry.bind('<Return>', on_key_press)
password_entry.focus_set()

open_button = Button(left_frame, text="Open", command=open_butt)
open_button.grid(row=0, column=2, padx=5)
save_button = Button(left_frame, text="Save", command=save_file)
save_button.grid(row=0, column=3, padx=5)

# Create the right frame for the search bar
right_frame = Frame(root)
right_frame.grid(row=0, column=1, padx=10, pady=10, sticky='e')

# Search Entry and Label
search_label = Label(right_frame, text="Search:")
search_label.grid(row=0, column=0, padx=5, sticky='e')  # Align to the right
search_entry = Entry(right_frame)
search_entry.grid(row=0, column=1, padx=5)
root.bind('<Control-f>', lambda event: search_entry.focus())
search_entry.bind('<KeyRelease>', search_text)

# Text Box Frame (underneath the other frames)
text_frame = Frame(root)
text_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10)

# Text Box
scrollbar = Scrollbar(text_frame)
scrollbar.pack(side=RIGHT, fill=Y)

text_box = Text(text_frame, wrap="word", yscrollcommand=scrollbar.set, width=150, height=40)
text_box.pack(expand=YES, fill=BOTH)
text_box.bind('<Control-s>', save_file)
text_box.bind('<Key>', unsaved)

scrollbar.config(command=text_box.yview)

# Add space between frames
root.grid_columnconfigure(1, minsize=20)
root.mainloop()
