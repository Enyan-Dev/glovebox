import os
import customtkinter as ctk
import requests

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class GloveboxApp(ctk.CTk):
    def __init__(self):
        super().__init__()

    #Window settings
        self.title("Glovebox")
        self.geometry("400x300")
    #UI Elements
        self.label = ctk.CTkLabel(self, text = "Glovebox Cloud Storage", font=("Arial", 20, "bold"))
        self.label.pack(pady=30)

    #File Selection Area
        self.upload_btn = ctk.CTkButton(self, text="select & Upload File", command=self.upload_file)
        self.upload_btn.pack(pady=20)

        self.file_info_label = ctk.CTkLabel(self, text="No file selected", text_color = "gray")
        self.file_info_label.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text= "Status: Ready", text_color="gray")
        self.status_label.pack(pady=30)

    def upload_file(self):
        """Opens a file explorer window, reads metadata, and uploads it to PocketBase."""
        # Open the file dialog window
        file_path = ctk.filedialog.askopenfilename()

        #If the user cancels the dialog box without picking anything
        if not file_path:
            return
        
        #Metadata extraction out of file path
        file_name = os.path.basename(file_path)
        #Calculate size in KB rounded 2 decimal places
        file_size_kb = round(os.path.getsize(file_path)/1024, 2)

        self.file_info_label.configure(text=f"Uploading: {file_name} ({file_size_kb} KB)")
        self.status_label.configure(text="Status: Uploading...", text_color="orange")
        self.update() #----Refresh UI to show processing state

        #Formulate multi-part payload for PocketBase
        url = "http://127.0.0.1:8090/api/collections/files/records"

        try:
            #Open file in binary read mode ('rb') and construct the data payload
            with open(file_path, 'rb') as f:
                data_payload = {
                    "name": file_name,
                    "size": file_size_kb
                }
                files_payload = {
                    "attachments": (file_name, f)
                }

                #Send a POST request containing our data and the file structure
                response = requests.post(url, data=data_payload, files=files_payload, timeout=10)

            #Verify if PocketBase successfully saved the record (HTTP 200 or 201 Created)
            if response.status_code in [200, 201]:
                self.status_label.configure(text="Status: Upload Successful!", text_color="green")
                self.file_info_label.configure(text=f"Saved: {file_name}")
            else:
                self.status_label.configure(text=f"Upload Fail: Server Error ({response.status_code})", text_color="red")
                print(response.json())#--->Prints details out to terminal to debug

        except requests.exceptions.ConnectError:
            self.status_label.configure(text="Status: Server Offline", text_color="red")

#App launcher
if __name__ == "__main__":
    app = GloveboxApp()
    app.mainloop()  

