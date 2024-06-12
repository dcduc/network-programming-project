import tkinter as tk
def close_event(main, client_socket):
    client_socket.sendall(bytes("QUIT", "utf8"))
    main.destroy()
    return

def shutdown(client_socket):
    client_socket.sendall(bytes("SHUTDOWN", "utf8"))

def shutdown_UI(client_socket, root):
    window = tk.Toplevel(root)
    window.geometry("250x160")
    window.grab_set()
    window.protocol("WM_DELETE_WINDOW", lambda: close_event(window, client_socket))
    label = tk.Label(window, text="Do you want to shutdown client?")
    label.pack(pady=10)
    
    shutdown_button = tk.Button(
        window, 
        text = 'YES',  
        fg = 'white', 
        bg = 'dodgerblue', 
        command = lambda: shutdown(client_socket)

        )
    shutdown_button.place(
        x = 50,
        y = 100,
        width = 75, 
        height = 40
        )

    no_shutdown_button = tk.Button(
        window, 
        text = 'NO',  
        fg = 'white', 
        bg = 'dodgerblue', 
        command = lambda: close_event(window, client_socket)
        )
    no_shutdown_button.place(
        x = 150,
        y = 100,
        width = 75, 
        height = 40
        )
    
    window.mainloop()