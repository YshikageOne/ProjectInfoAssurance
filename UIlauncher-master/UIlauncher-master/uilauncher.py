import sys
import sqlite3
from datetime import datetime
import csv
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QHeaderView
from PyQt5.QtCore import Qt
import random
import re
import requests

def log_event(event):
    with open("log.txt", "a") as f:
        f.write(f"{datetime.now()} - {event}\n")

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(500, 200, 300, 150)
        self.layout = QtWidgets.QVBoxLayout()
        self.username = QtWidgets.QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QtWidgets.QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)

        self.layout.addWidget(self.username)
        self.layout.addWidget(self.password)
        self.layout.addWidget(self.login_button)
        self.setLayout(self.layout)

    def handle_login(self):
        user = self.username.text()
        pwd = self.password.text()

        try:
            response = requests.post(
                "http://127.0.0.1:5000/login",
                json={"username": user, "password": pwd}
            )
            data = response.json()

            if response.status_code == 200 and data['status'] == 'success':
                log_event(f"User '{user}' logged in via API.")
                self.accept_login()
            else:
                QMessageBox.warning(self, "Login Failed", data.get('message', 'Login failed.'))
        except Exception as e:
            QMessageBox.critical(self, "Network Error", str(e))
    def accept_login(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

# Create a custom MainWindow class to override the resizeEvent
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1134, 350)  # Lock the window size to 1680x1053

        # Create a SQLite connection
        self.conn = sqlite3.connect('LaundryItems.db')
        self.cursor = self.conn.cursor()

        # Create the table if it doesn't exist
        self.create_table()

        # Load the UI file and setup the UI elements
        self.setup_ui()


    def setup_ui(self):
        # Load the UI file (path can be changed)
        uic.loadUi("LaunQueue.ui", self)

        # Access UI elements
        self.transactupdate = self.findChild(QtWidgets.QComboBox, 'transactupdate')
        self.transactinfo = self.findChild(QtWidgets.QComboBox, 'transactinfo')
        self.statusupdate = self.findChild(QtWidgets.QComboBox, 'statusupdate')
        self.nameinfo = self.findChild(QtWidgets.QLineEdit, 'nameinfo')
        self.nameupdate = self.findChild(QtWidgets.QLineEdit, 'nameupdate')
        self.contactinfo = self.findChild(QtWidgets.QLineEdit, 'contactinfo')
        self.contactupdate = self.findChild(QtWidgets.QLineEdit, 'contactupdate')
        self.kiloinfo = self.findChild(QtWidgets.QDoubleSpinBox, 'kiloinfo')
        self.addbutton = self.findChild(QtWidgets.QPushButton, 'addbutton')
        self.tableinfo = self.findChild(QtWidgets.QTableWidget, 'tableinfo')
        self.tableinfo_2 = self.findChild(QtWidgets.QTableWidget, 'tableinfo_2')
        self.remarksinfo = self.findChild(QtWidgets.QLineEdit, 'remarksinfo')
        self.remarksupdate = self.findChild(QtWidgets.QLineEdit, 'remarksupdate')


        self.contactinfo.setInputMask("000-000-0000")
        self.contactupdate.setInputMask("000-000-0000")
       
        # Add "Rush" and "Normal" options to ComboBoxes
        options = ["Rush", "Normal"]
        self.transactupdate.addItems(options)
        self.transactinfo.addItems(options)

        optionsupdate = ["In progress", "awaiting pick-up", "Picked-up"]

        self.statusupdate.addItems(optionsupdate)

        # Connect the add button to the add_data function
        self.addbutton.clicked.connect(self.add_data)
        self.deletebutton_2.clicked.connect(self.confirm_delete)
        self.deletebutton.clicked.connect(self.confirm_delete)
        self.selectbutton.clicked.connect(self.select_update)
        self.updatebutton.clicked.connect(self.update_selected)
        self.statuspickuptab.currentChanged.connect(self.on_tab_changed)
        self.printallbutton.clicked.connect(self.print_all_data_today)

        self.update_table()


        # Show the window
        self.show()
        # Update table with data from the database
        # Update Laundry Combo with data from the database
        self.populate_laundry_combo()
        self.transactbutton.clicked.connect(self.show_transaction_window)


    def create_table(self):
        """Create the table if it doesn't already exist."""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS LaundryItems (
                               LaundryID INTEGER PRIMARY KEY,
                               Date TEXT,
                               Name TEXT,
                               CellNum TEXT,
                               TransactionType TEXT,
                               Kilos REAL,
                               Total REAL,
                               Status TEXT,
                               Remarks TEXT)''')
        self.conn.commit()

    def select_update(self):
        # Get the selected ID from laundrycombo
        selected_id = self.laundrycombo.currentText()

        # Check if an ID is selected
        if not selected_id:
            QMessageBox.warning(self, "Selection Error", "Please select an ID from the laundry combo.")
            return

        # Connect to the SQLite database
        conn = sqlite3.connect("LaundryItems.db")
        cursor = conn.cursor()

        # Query to fetch the data for the selected ID
        query = """
            SELECT Name, CellNum, TransactionType, Kilos, Total, Status, Remarks
            FROM LaundryItems
            WHERE LaundryID = ?
        """
        try:
            cursor.execute(query, (selected_id,))
            result = cursor.fetchone()

            # Check if the data exists for the given ID
            if result:
                # Populate the QLineEdits with the retrieved data
                name, contact, transacttype, kilo, total, status, remarks = result
                self.nameupdate.setText(name)
                self.contactupdate.setText(contact)
                self.kiloupdate.setValue(int(kilo))
                self.totalupdate.setText(str(total))
                self.remarksupdate.setText(remarks)

                # Set the current status in the combo box
                if status == "In progress":
                    self.statusupdate.setCurrentIndex(0)
                elif status == "awaiting pick-up":
                    self.statusupdate.setCurrentIndex(1)
                elif status == "Picked-up":
                    self.statusupdate.setCurrentIndex(2)

                if transacttype == "Rush":
                    self.transactupdate.setCurrentIndex(0)
                elif transacttype == "Normal":
                    self.transactupdate.setCurrentIndex(1)
            
            else:
                QMessageBox.warning(self, "Data Not Found", f"No data found for ID {selected_id}.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while querying the database: {str(e)}")
        
        finally:
            # Close the database connection
            conn.close()

    def update_selected(self):
        # Get the selected ID from laundrycombo
        selected_id = self.laundrycombo.currentText()

        # Regular expression for validating name (only letters, capital or lowercase)
        name_regex = r"^[A-Za-z]+$"
        # Regular expression for validating contact number (10 digits or specific format like XXX-XXX-XXXX)
        contact_regex = r"^\d{3}-\d{3}-\d{4}$"  # For 10 digits; you can modify if needed for other formats


        # Check if an ID is selected
        if not selected_id:
            QMessageBox.warning(self, "Selection Error", "Please select an ID from the laundry combo.")
            return
        


        # Get the new status and transaction type from the UI
        new_status = self.statusupdate.currentText()
        new_name = self.nameupdate.text()
        new_contact = self.contactupdate.text()
        new_transact_type = self.transactupdate.currentText()
        new_remarks = self.remarksupdate.text()
        transaction_type = self.transactupdate.currentText()
        kilos = self.kiloupdate.value()
        new_total = 50 * kilos if transaction_type == 'Rush' else 40 * kilos


         # Validate Name - only letters, no spaces or special characters
        if not re.match(name_regex, new_name):
            QMessageBox.warning(self, "Input Error", "Please enter a valid name (letters only).", QMessageBox.Ok)
            return

        # Validate Contact Number - check if it matches the 10-digit format
        if not re.match(contact_regex, new_contact):
            QMessageBox.warning(self, "Input Error", "Please enter a valid contact number (10 digits).", QMessageBox.Ok)
            return

        # Connect to the SQLite database
        conn = sqlite3.connect("LaundryItems.db")
        cursor = conn.cursor()

        # Query to update the status and transaction type for the selected ID
        update_query = """
            UPDATE LaundryItems
            SET Status = ?, TransactionType = ?, Total = ?, Name = ?, Remarks = ?, CellNum = ?, Kilos = ?
            WHERE LaundryID = ?
        """

        try:
            # Execute the update query
            cursor.execute(update_query, (new_status, new_transact_type, new_total, new_name, new_remarks, new_contact, kilos, selected_id))
            
            # Commit the changes to the database
            conn.commit()

            self.update_table()

            # Check if any rows were updated
            if cursor.rowcount > 0:
                QMessageBox.information(self, "Update Successful", f"ID {selected_id} has been updated successfully.")
            else:
                QMessageBox.warning(self, "No Changes", f"No changes made for ID {selected_id}.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while updating the database: {str(e)}")

        finally:
            # Close the database connection
            conn.close()

    def populate_laundry_combo(self):
        """Populate the laundrycombo QComboBox with all LaundryID values from the database."""
        # Clear any existing items in the combo box
        self.laundrycombo.clear()

        # Fetch all LaundryID values from the database
        self.cursor.execute("SELECT LaundryID FROM LaundryItems WHERE Status IN ('awaiting pick-up', 'In progress')")
        laundry_ids = self.cursor.fetchall()

        # Add each LaundryID to the QComboBox
        for laundry_id in laundry_ids:
            # laundry_id is returned as a tuple, so we access the first element
            self.laundrycombo.addItem(str(laundry_id[0]))

        # Optionally, you can set a default value (e.g., the first item in the list)
        if self.laundrycombo.count() > 0:
            self.laundrycombo.setCurrentIndex(0)

    def confirm_delete(self):
        """Show a confirmation dialog before deleting a row."""
        reply = QtWidgets.QMessageBox.question(self, 'Confirm Delete', 
                                            "Are you sure you want to delete this row?",
                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
                                            QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.delete_row()

    def delete_row(self):
        """Delete the selected row from the table and the database."""
        # Get the selected row index in the table
        if self.statuspickuptab.currentIndex() == 0 :
            selected_row = self.tableinfo.currentRow()
            # Get the LaundryID from the selected row (assuming it's in the first column)
            laundry_id = self.tableinfo.item(selected_row, 0).text()
            # Delete the record from the database using the LaundryID
            self.cursor.execute("DELETE FROM LaundryItems WHERE LaundryID = ?", (laundry_id,))
            self.conn.commit()
            # Remove the row from the table widget
            self.tableinfo.removeRow(selected_row)
        else:
            selected_row = self.tableinfo_2.currentRow()
            # Get the LaundryID from the selected row (assuming it's in the first column)
            laundry_id = self.tableinfo_2.item(selected_row, 0).text()
            # Delete the record from the database using the LaundryID
            self.cursor.execute("DELETE FROM LaundryItems WHERE LaundryID = ?", (laundry_id,))
            self.conn.commit()

            # Remove the row from the table widget
            self.tableinfo.removeRow(selected_row)
        
        # If no row is selected, return early
        if selected_row == -1:
            return

        # After deletion, update the combo box with the new list of LaundryIDs
        self.populate_laundry_combo()

        # After deleting data, update the table to reflect changes
        self.update_table()


    def add_data(self):
        """Add data to the database from UI elements."""
        # Get user inputs
        name = self.nameinfo.text()
        contactnum = self.contactinfo.text()
        transaction_type = self.transactinfo.currentText()
        remarks = self.remarksinfo.text()
        kilos = self.kiloinfo.value()

        # Regular expression for validating name (only letters, capital or lowercase)
        name_regex = r"^[A-Za-z]+$"
        # Regular expression for validating contact number (10 digits or specific format like XXX-XXX-XXXX)
        contact_regex = r"^\d{3}-\d{3}-\d{4}$"  # For 10 digits; you can modify if needed for other formats

        if not name or not contactnum or not transaction_type or kilos <= 0 or not remarks:
            # Show an error message if any field is invalid or empty
            QMessageBox.warning(self, "Input Error", "Please make sure all fields are filled and Kilos is greater than 0.", QMessageBox.Ok)
            return  # Exit the function if validation fails

        # Validate Name - only letters, no spaces or special characters
        if not re.match(name_regex, name):
            QMessageBox.warning(self, "Input Error", "Please enter a valid name (letters only).", QMessageBox.Ok)
            return

        # Validate Contact Number - check if it matches the 10-digit format
        if not re.match(contact_regex, contactnum):
            QMessageBox.warning(self, "Input Error", "Please enter a valid contact number (10 digits).", QMessageBox.Ok)
            return

        # Validate Kilos - must be greater than 0
        if kilos <= 0:
            QMessageBox.warning(self, "Input Error", "Kilos must be greater than 0.", QMessageBox.Ok)
            return

        # Validate Remarks - can be anything, but ensure it's not empty
        if not remarks:
            QMessageBox.warning(self, "Input Error", "Remarks cannot be empty.", QMessageBox.Ok)
            return

        # Set the total based on the transaction type
        total = 50 * kilos if transaction_type == 'Rush' else 40 * kilos
        status = "In progress"

        # Generate a random LaundryID (You might want to check for uniqueness in a real-world app)
        laundry_id = random.randint(0, 9999)

        # Get the current date and time
        current_date = datetime.now().strftime("%Y-%m-%d")

        try:
            # Insert the data into the database
            self.cursor.execute('''INSERT INTO LaundryItems (LaundryID, Date, Name, CellNum, TransactionType, Kilos, Total, Status, Remarks)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                (laundry_id, current_date, name, contactnum, transaction_type, kilos, total, status, remarks))
            self.conn.commit()

            # After adding data, update the table and the combo box
            self.update_table()
            self.populate_laundry_combo()

        except Exception as e:
            # Show an error message if there was a problem inserting the data into the database
            QMessageBox.critical(self, "Database Error", f"An error occurred while saving the data: {str(e)}", QMessageBox.Ok)


   
    from PyQt5.QtWidgets import QMessageBox

    def update_table(self):
        """Update the table widget with data from the database based on the selected tab."""

        # Clear the table before updating
        self.tableinfo.setRowCount(0)
        self.tableinfo_2.setRowCount(0)

        # Get the current tab index
        current_tab = self.statuspickuptab.currentIndex()
        # Determine the SQL query based on the selected tab
        try:
            if current_tab == 1:
                query = "SELECT * FROM LaundryItems WHERE Status = ?"
                self.cursor.execute(query, ('awaiting pick-up',))

                rows = self.cursor.fetchall()

                # Adjust the width of the date column to make sure it is wide enough
                self.tableinfo_2.setColumnWidth(1, 200)

                # Populate the table with data from the database
                for row in rows:
                    row_position = self.tableinfo_2.rowCount()
                    self.tableinfo_2.insertRow(row_position)
                    for col, data in enumerate(row):  # Populate all columns (assuming no column needs to be skipped)
                        self.tableinfo_2.setItem(row_position, col, QtWidgets.QTableWidgetItem(str(data)))
            else:
                query = "SELECT * FROM LaundryItems WHERE Status = ?"
                self.cursor.execute(query, ('In progress',))

                rows = self.cursor.fetchall()

                # Adjust the width of the date column to make sure it is wide enough
                self.tableinfo.setColumnWidth(1, 200)

                # Populate the table with data from the database
                for row in rows:
                    row_position = self.tableinfo.rowCount()
                    self.tableinfo.insertRow(row_position)
                    for col, data in enumerate(row):  # Populate all columns (assuming no column needs to be skipped)
                        self.tableinfo.setItem(row_position, col, QtWidgets.QTableWidgetItem(str(data)))

            

        except sqlite3.Error as e:
            # If an error occurs with the database query, show an error message
            QMessageBox.critical(self, "Database Error", f"An error occurred while querying the database: {str(e)}")

    def on_tab_changed(self, index):
        """Handles tab change event to update the table accordingly."""
        # Call update_table to update the table when the tab is changed
        self.update_table()
    

    def show_transaction_window(self):
        # Create and show the transaction window
        self.transaction_window = TransactionWindow()
        self.transaction_window.show()

    def closeEvent(self, event):
        # Close the database connection when the window is closed
        self.conn.close()
        event.accept()

    def print_all_data_today(self):
        # Get today's date in the format you use in the database (e.g., 'YYYY-MM-DD')
        today_date = datetime.today().strftime('%Y-%m-%d')

        # Connect to the database
        conn = sqlite3.connect("LaundryItems.db")
        cursor = conn.cursor()

        try:
            # Query to fetch all data for today's date (assuming the date column is named 'Date')
            cursor.execute("SELECT * FROM LaundryItems WHERE Date = ? AND Status = ?", (today_date, 'Picked-up'))
            data = cursor.fetchall()

            # Check if there is any data for today
            if not data:
                QMessageBox.warning(self, "No Data", f"No data found for {today_date}.")
                return

            # Define the filename for the CSV file
            filename = f"LaundryItems_{today_date}.csv"

            # Get the column names
            columns = [description[0] for description in cursor.description]

            # Open the CSV file and write the data
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)

                # Write the header (column names)
                writer.writerow(columns)

                # Write the data rows
                for row in data:
                    writer.writerow(row)

            # Inform the user that the data has been successfully written to a CSV file
            QMessageBox.information(self, "Success", f"Data for {today_date} has been saved to {filename}.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while accessing the database: {str(e)}")

        finally:
            # Close the database connection
            conn.close()


# Transaction Window Class
class TransactionWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transaction Details")
        self.setGeometry(100, 100, 800, 600)

        # Create a table widget
        self.table = QtWidgets.QTableWidget(self)
        self.table.setGeometry(10, 10, 780, 580)

        # Set table headers
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "LaundryID", "Date", "Name", "CellNum", "TransactionType", "Kilos", "Total", "Status", "Remarks"
        ])

        # Use a layout to make the table fill the entire window
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)  # Add the table to the layout
        self.setLayout(layout)  # Set the layout for the window

        self.table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.setFixedSize(580, 350)
        # Fetch and display data from the database
        self.load_data()

    def load_data(self):
        # Connect to the database
        conn = sqlite3.connect("LaundryItems.db")
        cursor = conn.cursor()

        # Fetch all data from the LaundryItems table
        cursor.execute("SELECT * FROM LaundryItems")
        rows = cursor.fetchall()

        # Populate the table with the data
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, data in enumerate(row):
                self.table.setItem(row_index, column_index, QtWidgets.QTableWidgetItem(str(data)))

        # Resize columns to fit content
        self.table.resizeColumnsToContents()

        # Close the database connection
        conn.close()


def load_ui(ui_file):
    app = QtWidgets.QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())


# Path to your .ui file
ui_file = "LaunQueue.ui"

# Launch the UI
if __name__ == "__main__":
    load_ui(ui_file)
