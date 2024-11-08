from tkinter import *
from tkinter import filedialog, ttk  
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from stegano import lsb
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.io import wavfile
import wave
import numpy as np


filename = ''
audio_path = ''

root = Tk()
root.title("Steganografia si steganaliza imaginilor si fisierelor audio")
root.geometry("700x600+150+180")  
root.resizable(False, False)
root.configure(bg="#2f4155")

style = ttk.Style()

if "MyStyle" not in style.theme_names():
    style.theme_create( "MyStyle", parent="alt", settings={
        "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
        "TNotebook.Tab": {
            "configure": {"padding": [5, 1], "background": "#2f4155" },
            "map":       {"background": [("selected", "#0080FF")],
                          "expand": [("selected", [1, 1, 1, 0])] } } } )

style.theme_use("MyStyle")




#Controlul tab-urilor
tabControl = ttk.Notebook(root, style='TNotebook')
tabControl.place(x=0, y=0, width=700, height=700)

# Frame pentru fiecare tab
tab1 = Frame(tabControl, bg="#2f4155")
tab2 = Frame(tabControl, bg="#2f4155")


tabControl.add(tab1, text='Foto')
tabControl.add(tab2, text='Audio')

def select_image():
    global filename
    filename = filedialog.askopenfilename(initialdir=os.getcwd(),
                                          title='Select Image File',
                                          filetype=(("PNG file", "*.png"),
                                          ("JPG File", "*.jpg"), ("All file", "*.txt")))
    img = Image.open(filename)
    img = img.resize((250, 250), Image.LANCZOS)  
    img = ImageTk.PhotoImage(img)
    lbl.configure(image=img, width=250, height=250)
    lbl.image = img

    
    
def to_binary(data):
    return ''.join(format(ord(i), '08b') for i in data)

def from_binary(binary_data):
    return ''.join(chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8))

def image_capacity(image_path):
    img = Image.open(image_path)
    width, height = img.size
    return width * height

def encode_image(image_path, message):
    delimiter = "###END_OF_MESSAGE###"
    message = message + delimiter  
    img = Image.open(image_path)
    width, height = img.size

    message = to_binary(message)
    message_index = 0

    for y in range(height):
        for x in range(width):
            pixel = list(img.getpixel((x, y)))
            for i in range(len(pixel)):
                if message_index < len(message):
                    pixel[i] = pixel[i] & ~1 | int(message[message_index])
                    message_index += 1
            img.putpixel((x, y), tuple(pixel))

            if message_index >= len(message):
                break

    return img

def decode_image(image_path):
    img = Image.open(image_path)
    width, height = img.size

    binary_data = ""
    for y in range(height):
        for x in range(width):
            pixel = list(img.getpixel((x, y)))
            for i in range(len(pixel)):
                binary_data += str(pixel[i] & 1)

    decoded_message = from_binary(binary_data.rstrip('0'))
    delimiter = "###END_OF_MESSAGE###"
    decoded_message = decoded_message.split(delimiter, 1)[0]  

    return decoded_message


def on_encode_click():
    global filename, lbl
    if 'filename' in globals():  # verificam daca file-ul este selectat
        message = text1.get("1.0", tk.END).strip()  # .strip() sterge spatiul liber de dinainte si de dupa
        if len(message) == 0:  #Verifica daca nu s-a completat un mesaj
            messagebox.showwarning("Niciun mesaj selectat", "Introduceti un mesaj pentru a fi ascuns.")
        elif len(message) > 1000: # Verifica daca mesajul are mai mult de 1000 de caractere
            messagebox.showwarning("Eroare de codare", "Mesajul nu poate avea mai mult de 1000 de caractere.")
        elif len(message) > image_capacity(filename):
            messagebox.showwarning("Eroare de codare", "Mesajul este prea lung pentru a fi ascuns in poza selectata.")
        else:
            encoded_image = encode_image(filename, message)
            save_path = save_file_dialog()
            if save_path:
                encoded_image.save(save_path)
                img = Image.open(save_path)
                img = img.resize((250, 250), Image.LANCZOS)  
                img = ImageTk.PhotoImage(img)
                lbl.configure(image=img, width=250, height=250)
                lbl.image = img
                messagebox.showinfo("Ascundere", "Datele au fost ascunse cu succes in imagine.")
                text1.delete('1.0', END)  #Curata aria de text dupa codare cu succes
    else:
        tk.messagebox.showwarning("Nicio imagine selectata", "Selectati o imagine pentru a se ascunde mesajul.")



        
def on_decode_click():
    global filename
    decoded_message = decode_image(filename)
    text1.delete("1.0", tk.END)
    text1.insert(tk.END, decoded_message)    


def save_file_dialog():
    file_path = filedialog.asksaveasfilename(defaultextension=".png")
    return file_path

Label(tab1,text="Steganaliza Foto",bg="#2d4155",fg="white",font="arial 25 bold").place(x=30,y=20)

#Primul Frame
f=Frame(tab1,bd=3,bg="black",width=340,height=365,relief=GROOVE)
f.place(x=10,y=80)


lbl= Label(f,bg="black")
lbl.place(x=40,y=10)

default_img = Image.new('RGB', (380, 380), color='black')
default_img = ImageTk.PhotoImage(default_img)
lbl.configure(image=default_img, width=380, height=380)
lbl.image = default_img

#Al doilea Frame

frame2 = Frame(tab1, bd=3, width=340, height=365, bg="white", relief=GROOVE)
frame2.place(x=350,y=80)

text1 = Text(frame2,font="Robote 20", bg="white", fg="black", relief=GROOVE, wrap=WORD)
text1.place(x=0,y=0, width=320, height=375)


scrollbar1 = Scrollbar(frame2)
scrollbar1.place(x=320,y=0,height=380)


scrollbar1.configure(command=text1.yview)
text1.configure(yscrollcommand=scrollbar1.set)


#Al treilea Frame


frame3 = Frame(tab1,bd=3,bg="#2f4155", width=330, height=100,relief=GROOVE)
frame3.place(x=10,y=460)


Button(frame3, text="Open Image", width=10, height=2, font="arial 14 bold", command=select_image).place(x=20,y=30)
Button(frame3, text="Save Image", width=10, height=2, font="arial 14 bold",command=save_file_dialog).place(x=180, y=30)
Label(frame3, text="Picture, Image, Photo File", bg="#2f4155", fg="white").place(x=20, y=5)



#Al patrulea Frame


frame4 = Frame(tab1,bd=3,bg="#2f4155", width=330, height=100,relief=GROOVE)
frame4.place(x=360,y=460)


Button(frame4, text="Hide Data", width=10, height=2, font="arial 14 bold", command=on_encode_click).place(x=20, y=30)
Button(frame4, text="Show Data", width=10, height=2, font="arial 14 bold", command=on_decode_click).place(x=180, y=30)
Label(frame4, text="Picture, Image, Photo File", bg="#2f4155", fg="white").place(x=20, y=5)


# Tab2 


def select_audio():
    global audio_path
    audio_path = filedialog.askopenfilename(initialdir=os.getcwd(),
                                            title='Select Audio File',
                                            filetype=(("WAV file", "*.wav"), ("All Files", "*.*")))
    #Citeste file-ul audio si ploteaza forma de unda
    samplerate, data = wavfile.read(audio_path)
    ax.clear()  # Sterge plot-ul anterior
    ax.plot(data)
    fig.canvas.draw()

    plt.close(fig)  #Inchide plot-ul
    plt.ioff()  #Opreste modul interactiv


    
def to_binary(data):
    return ''.join(format(ord(i), '08b') for i in data)


def from_binary(binary_data):
    return ''.join(chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8))


def audio_capacity(audio_path):
    audio = wave.open(audio_path, 'rb')
    return audio.getnframes()


def encode_audio(audio_path, message):
    delimiter = "###END_OF_MESSAGE###"
    message = message + delimiter  
    message = to_binary(message)

    with wave.open(audio_path, "rb") as wav:
        params = wav.getparams()  #Obtine parametrii file-ului .wav original
        frames = bytearray(wav.readframes(wav.getnframes()))

    message_index = 0
    for i in range(len(frames)):
        frame = frames[i]
        if message_index < len(message):
            frame = frame & 254 | int(message[message_index])
            message_index += 1
        frames[i] = frame

    save_path = save_audio_file_dialog()
    if save_path:
        with wave.open(save_path, "wb") as wav:
            wav.setparams(params)  #Seteaza parametrii noului file .wav
            wav.writeframes(frames)

    return save_path


def decode_audio(audio_path):
    with wave.open(audio_path, "rb") as wav:
        frames = bytearray(wav.readframes(wav.getnframes()))

    binary_data = "".join([str(frame & 1) for frame in frames])

    decoded_message = from_binary(binary_data.rstrip('0'))
    delimiter = "###END_OF_MESSAGE###"
    decoded_message = decoded_message.split(delimiter, 1)[0]

    return decoded_message



def on_audio_encode_click():
    global audio_path
    message = text2.get("1.0", tk.END).strip()  # .strip() sterge spatiul liber de dinainte si de dupa
    if len(message) == 0:  #Verifica daca s-a introdus un mesaj 
        messagebox.showwarning("Niciun mesaj", "Introduceti un mesaj pentru a fi ascuns.")
    elif len(message) > 1000: # Verifica daca mesajul are mai mult de 1000 de caractere
        messagebox.showwarning("Eroare de codare", "Mesajul nu poate avea mai mult de 1000 de caractere.")
    elif len(message) > audio_capacity(audio_path):
        messagebox.showwarning("Eroare de codare", "Mesajul este prea lung pentru a fi ascuns in file-ul audio.")
    else:
        encoded_audio = encode_audio(audio_path, message)
        messagebox.showinfo("Ascundere", "Datele au fost ascunse cu succes in file-ul audio.")
        text2.delete('1.0', END)  #Curata aria de text dupa codare cu succes 


def on_audio_decode_click():
    global audio_path
    decoded_message = decode_audio(audio_path)
    text2.delete("1.0", tk.END)
    text2.insert(tk.END, decoded_message)
    
    
    
def save_audio_file_dialog():
    file_path = filedialog.asksaveasfilename(defaultextension=".wav")
    return file_path


#Definirea widget-urilor pentru audio
Label(tab2,text="Steganaliza Audio",bg="#2d4155",fg="white",font="arial 25 bold").place(x=30,y=20)

# Primul Frame
f2=Frame(tab2,bd=3,bg="black",width=340,height=380,relief=GROOVE)
f2.place(x=10,y=80)

#Afiseaza un plot blank ca si inlocuitor
fig, ax = plt.subplots(1)
canvas = FigureCanvasTkAgg(fig, master=f2)
canvas.draw()
canvas.get_tk_widget().place(x=20, y=10, width=300, height=360)

# Al doilea Frame
frame5 = Frame(tab2, bd=3, width=340, height=380, bg="white", relief=GROOVE)
frame5.place(x=350, y=80)

text2 = Text(frame5,font="Robote 20", bg="white", fg="black", relief=GROOVE, wrap=WORD)
text2.place(x=0, y=0, width=320, height=395)

scrollbar2 = Scrollbar(frame5)
scrollbar2.place(x=320, y=0, height=400)

scrollbar2.configure(command=text2.yview)
text2.configure(yscrollcommand=scrollbar2.set)

# Al treilea Frame
frame6 = Frame(tab2, bd=3, bg="#2f4155", width=330, height=100, relief=GROOVE)
frame6.place(x=10, y=465)


#Adaugare butoane pe cel de-al 3 lea Frame
Button(frame6, text="Open Audio", width=10, height=2, font="arial 14 bold", command=select_audio).place(x=20, y=30)
Button(frame6, text="Save Audio", width=10, height=2, font="arial 14 bold", command=save_audio_file_dialog).place(x=180, y=30)
Label(frame6, text="Audio File", bg="#2f4155", fg="white").place(x=20, y=5)

# Al patrulea Frame
frame7 = Frame(tab2, bd=3, bg="#2f4155", width=330, height=100, relief=GROOVE)
frame7.place(x=360, y=465)


# Adaugare butoane pe cel de-al 4 lea Frame
Button(frame7, text="Hide Data", width=10, height=2, font="arial 14 bold", command=on_audio_encode_click).place(x=20, y=30)
Button(frame7, text="Show Data", width=10, height=2, font="arial 14 bold", command=on_audio_decode_click).place(x=180, y=30)
Label(frame7, text="Audio File", bg="#2f4155", fg="white").place(x=20, y=5)

root.mainloop()