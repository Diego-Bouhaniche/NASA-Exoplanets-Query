from tkinter import BOTTOM, LEFT, TOP, Button, Entry, Label, LabelFrame, OptionMenu, Scrollbar, StringVar, Text, Tk, ttk, messagebox, messagebox, CENTER, NO
import webbrowser
import csv
import json
import requests
import os

# --- Functions --- #
def download_exoplanets_data():
    global is_data_loaded
    
    if(is_data_loaded):
        clear_data_table()
        is_data_loaded = False

    with requests.Session() as request:
        exoplanets_csv_file = request.get(PS_CSV_URL)
        file_size = round(len(exoplanets_csv_file.content)/1000000, 2)
        message_file_size = f"File size : {file_size} MB"

    if not os.path.exists('data/'):
        os.makedirs('data/')

    with open('data/raw_data.csv', 'w+') as f:
        writer = csv.writer(f)
        for line in exoplanets_csv_file.iter_lines():
            writer.writerow(line.decode('utf-8').split(','))

    messagebox.showinfo(title='File downloaded', message=message_file_size)   
    csv_to_json(CSV_FilePath, JSON_FilePath)
    
def csv_to_json(csvFile, jsonFilePath):
    jsonArray = []
      
    # read csv file
    with open(csvFile, encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            jsonArray.append(row)
  
    # convert python jsonArray to JSON String and write to file, create file if not exists
    with open(jsonFilePath, 'w+', encoding='utf-8') as jsonf: 
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)

def load_data():
    global data_json
    global is_data_loaded

    if(is_data_loaded == False):
        clear_data_table()

        # Opening JSON file
        try:
            f = open('data/data.json')
            # returns JSON object as a dictionary
            data_json = json.load(f)
            messagebox.showinfo(title='Data loaded', message=f"Data sucessfully loaded !\n Items found : {len(data_json)}")
        except:
            messagebox.showwarning(title='Error', message="No data found ! Use 'Download/Update' button")

        # Get uniques data for filter
        get_unique_data()

        # Display data table part
        display_data()

        # Display Search & Filter parts
        display_search_and_filter()

        # Update var
        is_data_loaded = True

    else:
        messagebox.showwarning(title='Error', message="Data already loaded !")


# [GUI] Table w/ data
def display_data():
    # heading & columns
    global headers

    if(len(data_json) == 0):
        messagebox.showwarning(title='Error', message="No data found !")
    else:
        headers = []
        for key in data_json[0].keys(): 
            headers.append(key)

        data_table_treeview.heading("#0", anchor=CENTER)
        data_table_treeview.column("#0",  width=0,  stretch=NO)

        data_table_treeview['columns'] = (headers[0], headers[1], headers[2], headers[3], headers[4])  
        for i in range(len(headers)):
            data_table_treeview.column(headers[i],  anchor=CENTER, width=263)

        data_table_treeview.heading(headers[0], anchor=CENTER, text="Planet Name")
        data_table_treeview.heading(headers[1], anchor=CENTER, text="Hostname")
        data_table_treeview.heading(headers[2], anchor=CENTER, text="Year")
        data_table_treeview.heading(headers[3], anchor=CENTER, text="Method")
        data_table_treeview.heading(headers[4], anchor=CENTER, text="Facility")
        
        # add data (rows)
        for i in range(len(data_json)):
            data_table_treeview.insert(parent='', index='end',
            values=(data_json[i][headers[0]], 
                    data_json[i][headers[1]], 
                    data_json[i][headers[2]], 
                    data_json[i][headers[3]], 
                    data_json[i][headers[4]])
            )

# Get uniques data to display them in the dropdown filtering menu
def get_unique_data():
    global data_json
    global unique_hostnames
    global unique_years
    global unique_methods
    global unique_facilities

    # get hostnames
    for i in range(len(data_json)):
        hostname = data_json[i]['hostname']
        if hostname not in unique_hostnames:
            unique_hostnames.append(hostname)
    # get years
    for i in range(len(data_json)):
        year = data_json[i]['disc_year']
        if year not in unique_years:
            unique_years.append(year)
    # get methods
    for i in range(len(data_json)):
        method = data_json[i]['discoverymethod']
        if method not in unique_methods:
            unique_methods.append(method)
    # get facilities
    for i in range(len(data_json)):
        facility = data_json[i]['disc_facility']
        if facility not in unique_facilities:
            unique_facilities.append(facility)

    unique_hostnames.sort()
    unique_years.sort()
    unique_methods.sort()
    unique_facilities.sort()

# Searching
def search_data_planet():
        user_input = planet_input.get().lower()
        result = list(filter(lambda x: user_input in x[headers[0]].lower(), data_json))
        update_table(result)

def search_data_hostname():
        user_input = hostname_input.get().lower()
        result = list(filter(lambda x: user_input in x[headers[1]].lower(), data_json))
        update_table(result)

def search_data_year():
        user_input = year_input.get().lower()
        result = list(filter(lambda x: user_input in x[headers[2]].lower(), data_json))
        update_table(result)

def search_data_method():
        user_input = method_input.get().lower()
        result = list(filter(lambda x: user_input in x[headers[3]].lower(), data_json))
        update_table(result)

def search_data_facility():
        user_input = facility_input.get().lower()
        result = list(filter(lambda x: user_input in x[headers[4]].lower(), data_json))
        update_table(result)

def filter_data():    
    if(len(hostname_choice) == 0 and len(year_choice) == 0 and len(method_choice) == 0 and len(facility_choice) == 0):
        messagebox.showwarning(title='Error', message="No filter selected !")
    else:
        filter_result = []

        for i in range(len(data_json)):
            if(hostname_choice in data_json[i]['hostname'] and
                year_choice  in data_json[i]['disc_year'] and
                method_choice in data_json[i]['discoverymethod']  and
                facility_choice in data_json[i]['disc_facility']):
                filter_result.append(data_json[i])
                
        update_table(filter_result)

# Update data table after searching / filtering
def update_table(result):        
    # clear data
    clear_data_table()

    if(len(result) == 0):
        messagebox.showwarning(title='Error', message="No data found !")
        display_data()
    else:
        # add filtered data
        for i in range(len(result)):
            data_table_treeview.insert(parent='', index='end',
            values=(result[i][headers[0]],
                    result[i][headers[1]],
                    result[i][headers[2]],
                    result[i][headers[3]],
                    result[i][headers[4]])
            )

# Clear function
def clear():
    # clear search
    planet_input.set("")
    hostname_input.set("")
    year_input.set("")
    method_input.set("")
    facility_input.set("")
    
    # clear filter
    global hostname_choice
    global year_choice
    global method_choice
    global facility_choice
    global wrapper4

    hostname_choice = ""
    year_choice = ""
    method_choice = ""
    facility_choice = ""

    wrapper4.destroy()

    wrapper4 = LabelFrame(root, text="Filter")

    display_search_and_filter()
    reset_data_table()

# Clear data table
def clear_data_table():
    global year_input

    for i in data_table_treeview.get_children():
        data_table_treeview.delete(i)

def reset_data_table():
    clear_data_table()
    display_data()

def display_search_and_filter():
    
    def get_hostname_variable(choice1):
        global hostname_choice
        choice1 = dropdown_filter_hostname_variable.get()
        hostname_choice = choice1
    def get_year_variable(choice2):
        global year_choice
        choice2 = dropdown_filter_year_variable.get()
        year_choice = choice2
    def get_method_variable(choice3):
        global method_choice
        choice3 = dropdown_filter_method_variable.get()
        method_choice = choice3
    def get_facility_variable(choice4):
        global facility_choice
        choice4 = dropdown_filter_facility_variable.get()
        facility_choice = choice4    

    # [GUI] Filter
    dropdown_filter_hostname_variable = StringVar(wrapper4)
    dropdown_filter_hostname_variable.set('Hostname') # default value
    dropdown_filter_hostname = OptionMenu(wrapper4, dropdown_filter_hostname_variable, *unique_hostnames, command=get_hostname_variable)
    dropdown_filter_hostname.grid(row=1, column=3, padx=6, pady=2)

    dropdown_filter_year_variable = StringVar(wrapper4)
    dropdown_filter_year_variable.set("Years") # default value
    dropdown_filter_year = OptionMenu(wrapper4, dropdown_filter_year_variable, *unique_years, command=get_year_variable)
    dropdown_filter_year.grid(row=2, column=3, padx=6, pady=2)

    dropdown_filter_method_variable = StringVar(wrapper4)
    dropdown_filter_method_variable.set("Methods") # default value
    dropdown_filter_method = OptionMenu(wrapper4, dropdown_filter_method_variable, *unique_methods, command=get_method_variable)
    dropdown_filter_method.grid(row=3, column=3, padx=6, pady=2)

    dropdown_filter_facility_variable = StringVar(wrapper4)
    dropdown_filter_facility_variable.set("Facilities") # default value
    dropdown_filter_facility = OptionMenu(wrapper4, dropdown_filter_facility_variable, *unique_facilities, command=get_facility_variable)
    dropdown_filter_facility.grid(row=4, column=3, padx=6, pady=2)  

    btn_apply = Button(wrapper4, text="Apply", command=filter_data)
    btn_apply.grid(row=5, column=3, padx=6, pady=2)  

    wrapper2.pack(fill="x",     expand="no", padx=20, pady=5)
    wrapper6.pack(fill="none",  expand="no", padx=20, pady=5, side=TOP, anchor='w')
    wrapper3.pack(fill="x",     expand="no", padx=20, pady=5, side=LEFT) # Search
    wrapper4.pack(fill="x",     expand="no", padx=20, pady=5, side=LEFT) # Filter
    wrapper5.pack(fill="none",  expand="no", padx=20, pady=5, side=LEFT) # Clear

def selectItem(e):
    global url_link

    curItem = data_table_treeview.focus()
    col = data_table_treeview.identify_column(e.x)

    hostname_clicked = data_table_treeview.item(curItem)['values'][1]
    planet_clicked = data_table_treeview.item(curItem)['values'][0]

    # Remove "
    hostname_clicked = hostname_clicked.replace("\"", "")
    planet_clicked = planet_clicked.replace("\"", "")

    # Generate link
    if(col == "#2"):
        url_link = f"https://exoplanetarchive.ipac.caltech.edu/overview/{hostname_clicked}"
    elif(col == "#1"):
        url_link = f"https://exoplanetarchive.ipac.caltech.edu/overview/{hostname_clicked}#planet_{planet_clicked}_collapsible"
        url_link = url_link.replace(" ", "-")

    link_text.set(url_link)

def link_clicked(e):
    global url_link
    
    webbrowser.open_new(url_link)

# --- MAIN CODE --- #

# Init GUI
root = Tk()
root.iconbitmap('favicon.ico')
root.title("NASA Exoplanets App")
root.geometry('1366x768')
root.state('zoomed')

# Link to Planetary Systems (PS) table
PS_CSV_URL  = 'https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+pl_name,hostname,disc_year,discoverymethod,disc_facility+from+ps&format=csv'

# Paths to download
CSV_FilePath  = 'data\\raw_data.csv'
JSON_FilePath = 'data\\data.json'

# Global variables
is_data_loaded = False
url_link = ""
link_text = StringVar()

# Global data
data_json = []
headers = []

unique_hostnames =[]
unique_years =[]
unique_methods =[]
unique_facilities =[]

# Search inputs
planet_input = StringVar()
hostname_input = StringVar()
year_input = StringVar()
method_input = StringVar()
facility_input = StringVar()

# Filters choices
hostname_choice = ""
year_choice = ""
method_choice = ""
facility_choice= ""
dropdown_filter_hostname_variable = StringVar()

# Add Some Style
style = ttk.Style()
# Pick A Theme
style.theme_use('default')

wrapper1 = LabelFrame(root, text="Commands")
wrapper2 = LabelFrame(root, text="Data")
wrapper3 = LabelFrame(root, text="Search")
wrapper4 = LabelFrame(root, text="Filter")
wrapper5 = LabelFrame(root, text="Clear")
wrapper6 = LabelFrame(root, text="Link")

wrapper1.pack(fill="x",     expand="no", padx=20, pady=2)

# [GUI] Button download data
btn_dl_data = Button(wrapper1, text="Download/Update data", bg="white", fg="black", command=download_exoplanets_data)
btn_dl_data.grid(row=0, column=0, padx=10, pady=10)

# [GUI] Button load data
btn_load_data = Button(wrapper1, text="Load data", bg="white", fg="black", command=load_data)
btn_load_data.grid(row=0, column=1, padx=10, pady=10)

# [GUI] Button reset data
btn_reset_data = Button(wrapper1, text="Reset data", bg="white", fg="black", command=reset_data_table)
btn_reset_data.grid(row=0, column=3, padx=10, pady=10)

# [GUI] Treeview (Data table)
data_table_treeview = ttk.Treeview(wrapper2, selectmode="extended", height=13)
data_table_treeview.bind('<ButtonRelease-1>', selectItem)

data_table_treeview.pack()

# configure the Treeview style
style.configure("Treeview",
	background="white",
	foreground="black",
    fieldbackground="#D3D3D3",
    highlightthickness=10,
	rowheight=25,
    font=('Calibri', 11))

# modify the font of the headings
style.configure("Treeview.Heading", font=('Calibri', 13,'bold')) 

# change Selected Color
style.map('Treeview',
	background=[('selected', "#347083")])

# [GUI] Search
lbl_search_planet = Label(wrapper3, text="Search planet :")
lbl_search_planet.grid(row=0, column=0, padx=10, pady=2)
ent_search_planet = Entry(wrapper3, textvariable=planet_input)
ent_search_planet.grid(row=0, column=1, padx=6, pady=2)
btn_search_planet = Button(wrapper3, text="Search ", command=search_data_planet)
btn_search_planet.grid(row=0, column=2, padx=6, pady=2)

lbl_search_hostname = Label(wrapper3, text="Search hostname :")
lbl_search_hostname.grid(row=1, column=0, padx=10, pady=2)
ent_search_hostname = Entry(wrapper3, textvariable=hostname_input)
ent_search_hostname.grid(row=1, column=1, padx=6, pady=2)
btn_search_hostname = Button(wrapper3, text="Search", command=search_data_hostname)
btn_search_hostname.grid(row=1, column=2, padx=6, pady=2)

lbl_search_year = Label(wrapper3, text="Search year :")
lbl_search_year.grid(row=2, column=0, padx=10, pady=2)
ent_search_year = Entry(wrapper3, textvariable=year_input)
ent_search_year.grid(row=2, column=1, padx=6, pady=2)
btn_search_year = Button(wrapper3, text="Search", command=search_data_year)
btn_search_year.grid(row=2, column=2, padx=6, pady=2)

lbl_search_method = Label(wrapper3, text="Search method :")
lbl_search_method.grid(row=3, column=0, padx=10, pady=2)
ent_search_method = Entry(wrapper3, textvariable=method_input)
ent_search_method.grid(row=3, column=1, padx=6, pady=2)
btn_search_method = Button(wrapper3, text="Search", command=search_data_method)
btn_search_method.grid(row=3, column=2, padx=6, pady=2)

lbl_search_facility = Label(wrapper3, text="Search facility :")
lbl_search_facility.grid(row=4, column=0, padx=10, pady=2)
ent_search_facility = Entry(wrapper3, textvariable=facility_input)
ent_search_facility.grid(row=4, column=1, padx=6, pady=2)
btn_search_facility = Button(wrapper3, text="Search", command=search_data_facility)
btn_search_facility.grid(row=4, column=2, padx=6, pady=2)

btn_clear = Button(wrapper5, text="Clear", command=clear)
btn_clear.grid(row=0, column=0, padx=6, pady=2)

# [GUI] Link
link_label = Label(wrapper6, textvariable=link_text, fg="blue", cursor="hand2")
link_label.grid(row=0, column=0, padx=6, pady=2)
link_label.bind('<ButtonRelease-1>', link_clicked)

# After
root.mainloop()