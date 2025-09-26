# Label Tracker Application 

## Requirements
- Multi-user capabilities
- Able to send xlsx files to client 
- Track user, Sn, time, pass/fail status, and if fail notes
- label format ` CUSTID-ORDNO-XXXXX `
    - THT-1-423-10 or THT-36-423-10 for label size is TBD

### Version 1.0.0

- Create xlsx files that are order number specific
- User log in for application session that would require log-in and log-out
- Simple ui
- Local DB to manage companies, admin rights, boards, track file progress and file locations

#### Tech Stack 
- python 3.13.7
- Excel xlsx files
- sqlite3 database
- pyqt5
- pyinstaller
- openpyxl
- see requirements.txt for other libraries

#### File layout:
- Application in `P:\EMS Testing & Repair\LabelTrackingApplication.exe`
- Database in `P:\EMS_TR_PATH\label tracking`
- XLSX files in `P:\EMS Testing & Repair\clients\<client>\logging\<ordernumberLogging.xlsx`

#### Application layout:
- Application/
- |
- |-- main.py
- |
- |-- gui/
    - |	|-- __init__.py
    - |	|-- app.py
    - |	|-- windows.py
    - |	|-- widgets.py
    - |	|-- styles.py
- |
- |-- managers/
    - |	|-- __init__.py
    - |	|-- xlsx_manager.py
    - |	|--db_manager.py
- |
- |-- utils/
    - |	|-- __init__.py
    - |	|-- config.py `Abandoned`
    - |	|-- logger.py
    - |	|-- validators.py
- |
- |-- logs/
    - |	|-- app.log (move once prod ready)
- |
- |-- tests/
    - |	|-- __init__.py
    - |	|-- test_db.py
    - |	|-- test_xlsx.py
    - |	|-- test_gui.py
    - | |-- test_logger.py
- |
- |-- main.spec
- |--requirements.txt


#### Database Schema:
- Users (username, password, role)
    - admin (permission to create new companies, boards and view work in progress)
    - standard aka users (permission to create new orders)
- Companies
    - company id, name, client path
- Boards
    - board id, company id, board name
- notes
    - User ID, Company ID, Board ID, Serial Number, pass/fail, pass/fail timestamp, if failed explanation, if fixed explanation, if fixed timestamp

#### xlsx schema
- user id
- company id
- serial number
- pass/fail
    - timestamp pass/fail
- if fail then failure explanation
- if fixed then explanation
    - timestamp when fail changed to pass

TODO: finish readme 