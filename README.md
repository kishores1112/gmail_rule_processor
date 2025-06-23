# Gmail Rule Processor (PostgreSQL)

## Overview
This project processes Gmail emails based on user-defined rules and actions. It uses the Gmail API for email operations and PostgreSQL for storage.

---

## Setup Instructions

### 1. **Google API Setup**
1. Create a Google Cloud project:
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project or select an existing one.
2. Enable the Gmail API:
   - Navigate to **APIs & Services > Library**.
   - Search for **Gmail API** and click **Enable**.
3. Create OAuth credentials:
   - Go to **APIs & Services > Credentials**.
   - Click **Create > OAuth client ID**.
   - Select **Desktop App** as the application type.
   - Download the `credentials.json` file and place it in the project directory.
4. Generate `token.json`:
   - Run the script to initiate the OAuth flow:
     ```bash
     python fetch_emails.py
     ```
   - Follow the instructions in the browser to authenticate and authorize the app.
   - The `token.json` file will be created automatically.

---

### 2. **PostgreSQL Setup**
1. Install PostgreSQL:
   - Follow the instructions for your operating system to install PostgreSQL.
2. Create a database and user:
   - Open the PostgreSQL shell (`psql`) and run:
     ```sql
     CREATE DATABASE your_db;
     CREATE USER your_user WITH PASSWORD 'your_password';
     GRANT ALL PRIVILEGES ON DATABASE your_db TO your_user;
     ```
3. Set environment variables for database connection:
   ```bash
   export PGDATABASE=your_db
   export PGUSER=your_user
   export PGPASSWORD=your_password
   export PGHOST=localhost
   export PGPORT=5432
   ```

---

### 3. **Install Dependencies**
Install the required Python packages:
```bash
pip install -r requirements.txt
```

---

### 4. **Run the Project**
#### Fetch Emails:
Fetch emails from the Gmail inbox and store them in the database:
```bash
python fetch_emails.py
```

#### Edit Rules:
Define rules and actions in `rules.json`:
```json
{
    "predicate": "Any",
    "rules": [
        {
            "field": "Subject",
            "predicate": "Contains",
            "value": "Invoice"
        },
        {
            "field": "From",
            "predicate": "Equals",
            "value": "boss@example.com"
        }
    ],
    "actions": [
        {
            "type": "mark_read"
        },
        {
            "type": "move_message",
            "label": "Important"
        }
    ]
}
```

#### Process Emails:
Apply rules and actions to emails stored in the database:
```bash
python process_rules.py
```

---

### 5. **Run Test Cases**
You can run all tests at once using the following command:
```bash
python -m unittest discover -s tests -p "*.py"
```

#### Unit Tests Only:
To run only unit tests:
```bash
python -m unittest discover -s tests -p "units.py"
```

#### Integration Tests Only:
To run only integration tests:
```bash
python -m unittest discover -s tests -p "integrations.py"
```

---

### 6. **Folder Creation**
If a folder specified in the rules does not exist, the script will automatically create it using the Gmail API. Ensure the folder name conforms to Gmail's naming conventions (e.g., no special characters like `/`, `\`, `?`, etc.).

---

## Notes
- **Database:** Uses PostgreSQL for email storage.
- **Rules:** Rules and actions are customizable in `rules.json`.
- **Authentication:** Requires `credentials.json` and `token.json` for Gmail API access.
- **Scopes:** Uses the `https://www.googleapis.com/auth/gmail.modify` scope for both fetching and processing emails.
- **Folder Creation:** Automatically creates missing folders during email processing.
