import subprocess
from threading import Thread
import time
import tkinter as tk
from tkinter import messagebox
import queue

MP3_FILE = "traffic.mp3"
ERROR = "error.mp3"
SUCCESS = "success.mp3"

popup_queue = queue.Queue()
sound_queue = queue.Queue()  # file d'attente pour les sons

def play_sound_loop():
    while True:
        sound_file = sound_queue.get()
        if sound_file:
            subprocess.run(f"mpg123 {sound_file}", shell=True)

# Ajoute un son dans la queue
def queue_sound(file):
    sound_queue.put(file)

def play_alert():
    print("[ALERTE] Trafic Serveo détecté ! 🔥")
    queue_sound(MP3_FILE)

def enqueue_popup(title, message, sound_file=None):
    popup_queue.put((title, message, sound_file))

def popup_loop():
    root = tk.Tk()
    root.withdraw()

    def check_queue():
        while not popup_queue.empty():
            title, message, sound = popup_queue.get()
            if sound:
                queue_sound(sound)
            messagebox.showinfo(title, message)
        root.after(100, check_queue)

    check_queue()
    root.mainloop()

def run_command(command):
    while True:
        print("[*] Lancement de la commande SSH...")
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            ssh_started = False

            for line in process.stdout:
                line = line.strip()
                print("[SSH]", line)

                if not ssh_started and ("Forwarding" in line or "remote port" in line or "authenticated" in line):
                    ssh_started = True
                    enqueue_popup("OK", "Commande de Forwarding SSH démarrée avec succès!", SUCCESS)

                if "HTTP request from" in line:
                    play_alert()

        except KeyboardInterrupt:
            print("[!] Interruption manuelle.")
            process.terminate()
            break

        except Exception as e:
            print(f"[ERROR] Une erreur est survenue : {e}")

        enqueue_popup("Erreur", "Redémarrage de la commande SSH...", ERROR)

        try:
            process.terminate()
        except:
            pass
        time.sleep(5)

def main():
    Thread(target=popup_loop, daemon=True).start()
    Thread(target=play_sound_loop, daemon=True).start()  # lecteur audio permanent
    run_command("ssh -R tsilavina.serveo.net:80:localhost:80 serveouser@serveo.net")

if __name__ == "__main__":
    main()
