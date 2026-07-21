import os
import customtkinter as ctk
import requests

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class GloveboxApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.pb_base_url = "http://127.0.0.1:8090"

    #Window settings
        self.title("Glovebox")
        self.geometry("550x550")
    #UI Elements
        self.label = ctk.CTkLabel(self, text = "Glovebox Cloud Storage", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

    #File Selection Area
        self.upload_btn = ctk.CTkButton(self, text="select & Upload File", command=self.upload_file)
        self.upload_btn.pack(pady=10)

        self.file_info_label = ctk.CTkLabel(self, text="No file selected", text_color = "gray")
        self.file_info_label.pack(pady=10)

    #Divider
        self.line = ctk.CTkLabel(self, text="----------------------------------------------------",text_color="gray")
        self.line.pack(pady=5)

    #Scrollable area for cloud files
        self.vault_label = ctk.CTkLabel(self, text="Files in your Cloud Vault:", font=("Arial", 14, "bold"))
        self.vault_label.pack(pady=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=450, height= 220)
        self.scroll_frame.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text= "Status: Ready", text_color="gray")
        self.status_label.pack(pady=15)

    #loads existing files on startup automatically
        self.refresh_vault_list()

    def get_file_icon(self, filename):
        """Returns a visual icon based on the file extension."""
        ext = os.path.splitext(filename)[1].lower()
        if ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"]:
            return "🖼️"
        elif ext in [".pdf", ".doc", ".docx", ".txt"]:
            return "📄"
        elif ext in [".mp3", ".wav", ".aac"]:
            return "🎵"
        elif ext in [".mp4", ".mkv", ".mov"]:
            return "🎥"
        elif ext in [".zip", ".rar", ".7z"]:
            return "📦"
        elif ext in [".py", ".js", ".html", ".css", ".json"]:
            return "💻"
        else:
            return "📁"
        

    def refresh_vault_list(self):
        """Fetches the list of records from PocketBase and displays them in the scroll frame."""
        #C lean out any old widgets inside the scroll frame first
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        url = f"{self.pb_base_url}/api/collections/files/records"

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                #PocketBase returns a JSON object: our records live inside the 'items' array
                data = response.json()
                files_list = data.get("items", [])

                if not files_list:
                    empty_label = ctk.CTkLabel(self.scroll_frame, text="vault is empty.", text_color="gray")
                    empty_label.pack(pady=20)
                    return
                
                for file_record in files_list:
                    record_id = file_record.get("id")
                    file_name = file_record.get("name", "Unknown File")
                    file_size = file_record.get("size", 0)
                    attachment_field = file_record.get("attachments","")

                    #Main item container row(card)
                    row_frame = ctk.CTkFrame(self.scroll_frame)
                    row_frame.pack(fill="x", padx=5, pady=5)

                    #Delete Button
                    delete_btn = ctk.CTkButton(
                        row_frame,
                        text="🗑️",
                        width=35,
                        fg_color="#c92a2a",
                        hover_color="#a61e1e",
                        command=lambda r=record_id, fn=file_name: self.delete_file(r, fn)
                    )
                    delete_btn.pack(side="right", padx=5, pady=5)

                      #Download Button
                    download_btn = ctk.CTkButton(
                        row_frame,
                        text="⏬",
                        width=35,
                        fg_color="#2b8a3e",
                        hover_color="#216a30",
                        command= lambda r=record_id, fn=file_name, att= attachment_field: self.download_file(r, fn, att)
                    )
                    download_btn.pack(side="right", padx=5, pady=5)

                    #Icon and details
                    icon = self.get_file_icon(file_name)
                    display_text = f"{icon} {file_name} ({file_size} KB)"
                    file_info = ctk.CTkLabel(row_frame, text=display_text, font=("Arial", 13),anchor="w")
                    file_info.pack(side="left", padx=10, expand=True, fill="x")

            else:
                error_label = ctk.CTkLabel(self.scroll_frame, text="Failed to fetch file index.", text_color="red")
                error_label.pack(pady=20)
        except requests.exceptions.ConnectionError:
            offline_label = ctk.CTkLabel(self.scroll_frame, text="Server offline.", text_color="red")
            offline_label.pack(pady=20)      

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
        url = f"{self.pb_base_url}/api/collections/files/records"

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
                #Refresh UI list immediately so the new file pops up!
                self.refresh_vault_list()
            else:
                self.status_label.configure(text=f"Upload Fail: Server Error ({response.status_code})", text_color="red")
                print(response.json())#--->Prints details out to terminal to debug

        except requests.exceptions.ConnectionError:
            self.status_label.configure(text="Status: Server Offline", text_color="red")

    def download_file(self, record_id,filename, attachment_filename):
        #if attachments is a list or string, handle accordingly
        if isinstance(attachment_filename, list) and len(attachment_filename) > 0:
            actual_filename = attachment_filename[0]
        else:
            actual_filename = attachment_filename
        
        file_url = f"{self.pb_base_url}/api/files/files/{record_id}/{actual_filename}"

        #Ask user where to save the file
        save_path = ctk.filedialog.asksaveasfilename(initialfile=filename)
        if not save_path:
            return
        
        try:
            self.status_label.configure(text=f"Downloading {filename}....", text_color="orange")
            self.update()

            res = requests.get(file_url,stream=True)
            if res.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.status_label.configure(text=f"Downloaded: {filename} ✅", text_color="green")
            else:
                self.status_label.configure(text="Download failed.", text_color="red")
        except Exception as error:
            self.status_label.configure(text="Download error.", text_color="red")   

    def delete_file(self,record_id, filename):
        delete_url = f"{self.pb_base_url}/api/collections/files/records/{record_id}"

        try:
            response = requests.delete(delete_url, timeout=5)
            if response.status_code in [200,204]:
                self.status_label.configure(text=f"Deleted: {filename} 🗑️", text_color="green")
                self.refresh_vault_list()
            else:
                self.status_label.configure(text="Delete failed.", text_color="red")
        except requests.exceptions.ConnectionError:
            self.status_label.configure(text="Server offline.", text_color="red")   
#App launcher 
if __name__ == "__main__":
    app = GloveboxApp()
    app.mainloop()  

