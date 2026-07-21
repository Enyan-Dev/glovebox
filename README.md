#  Glovebox — Desktop Cloud Storage Client

Glovebox is a lightweight desktop cloud client built with Python and CustomTkinter. It provides a clean, user-friendly graphical interface for uploading, browsing, downloading, and managing files stored on a local PocketBase backend.

---

##  Features

* Modern UI:** Clean, dark-mode friendly desktop application powered by CustomTkinter.
* File Management:** Seamlessly upload local files directly to your cloud vault.
* Direct Downloads & Deletes:** Independent controls for downloading or deleting specific file records.
* Visual File Icons:** Automatically assigns dynamic file icons based on extension types (`.pdf`, `.png`, `.mp3`, `.py`, `.zip`, etc.).
* PocketBase Integration:** Powered by REST APIs for fast metadata indexing and payload transfers.

---

##  Tech Stack

* **Language:** Python 3.11+
* **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* **Backend Storage:** [PocketBase](https://pocketbase.io/)
* **HTTP Client:** `requests`

---

##  Getting Started

### Prerequisites

1. Python 3.8+ installed on your machine.
2. PocketBase running locally on `http://127.0.0.1:8090`.

### 1. PocketBase Collection Setup

Ensure your PocketBase database has a collection named **`files`** with the following fields:

| Field Name | Type | Notes |
|---|---|---|
| `name` | Text | Stores the file name |
| `size` | Number | Stores size in KB |
| `attachments` | File | File upload field |

---

### 2. Installation & Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/enyan-dev/glovebox.git

