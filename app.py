from tkinter import *
import os
import hashlib
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import pymysql
import sys
import pandas as panda
from panda_rf import data_modle_smasher, rf_kgo, dat_molder
import subprocess
import time

# Globals
file_loc = None


def sys_runtime_check():
    if getattr(sys, 'frozen', False):
        return False
    else:
        return True


if sys_runtime_check():
    bin_loc = os.getcwd()
else:
    bin_loc = sys._MEIPASS


# Check if SHA_256 key is the same for temp dir.
def file_hash_check(key):
    hashington = hashlib.sha3_256()
    for r, d, f in os.walk(bin_loc):
        for a in f:
            raw_dat = os.path.join(r, a)
            hash_dat = raw_dat.replace('\\', '/')
            hash_file_open = open(hash_dat, 'rb')
            buffer = hash_file_open.read()
            hashington.update(buffer)
    if key is True:
        return hashington.hexdigest()
    elif key == hashington.hexdigest():
        return True
    else:
        return False


# globals
pid_list = {'exp': '', 'lap': '', 'sps': '', 'ses': ''}


class FrankinbotUi(Tk):
    def __init__(self):
        Tk.__init__(self)
        ## Check if dev or compiled EXE
        self.abso_path = bin_loc
        self.zip_loc = os.path.join(self.abso_path, r'bin\apps.zip')
        self.temp_loc = os.path.join(self.abso_path, r'bin\temp')
        self.bin_loc = os.path.join(self.abso_path, r'bin')
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # Frames
        self.title('FIBT')
        self.admin_menu = Frame(self, bg='green')
        # Progress bar
        self.progress = ttk.Progressbar(self.admin_menu, orient="horizontal",
                                        length=200, mode="determinate")
        self.progress["value"] = 0
        # Labels
        self.title_n_est = Label(self.admin_menu, text='n_estimators EG: 10,20,30', bg='green')
        self.title_max_feat = Label(self.admin_menu, text='max_features between 0.1 and 1.0', bg='green')
        self.title_cores = Label(self.admin_menu, text='# of CPU cores -1 is all cores', bg='green')
        # Command buttons
        self.sql_connect = Button(self.admin_menu, text='Connect to SQL server', height=2, width=25,
                         command=self.sql_con)
        self.open_csv = Button(self.admin_menu, text="Open CSV", height=2, width=25,
                         command=lambda pos=1: self.file_exp_open(pos))
        self.go = Button(self.admin_menu, text="Run Forest, RUN!!!!", height=2, width=25,
                         command=self.data_rf_run)
        # Text box
        self.n_est = Entry(self.admin_menu)
        self.max_feat = Entry(self.admin_menu)
        self.cores = Entry(self.admin_menu)
        # Check box's
        #self.check_box_dict.update({'load_csv': IntVar()})
        #self.load_csv = Checkbutton(self.admin_menu, text='Load CSV file?', variable=self.check_box_dict['load_csv'])
        # Menu
        self.admin_menu.pack(fill="both", expand=True)
        self.open_csv.grid(row=0, column=0, columnspan=3, sticky="NSEW", padx=2, pady=2)
        #self.load_csv.grid(row=0, column=0, columnspan=3, sticky="NSEW", padx=2, pady=2)
        self.sql_connect.grid(row=1, column=0, columnspan=3, sticky="NSEW", padx=2, pady=2)
        self.title_n_est.grid(row=3, column=0, columnspan=3, sticky="NSEW", padx=2, pady=2)
        self.n_est.grid(row=4, column=0, columnspan=3, sticky="NSEW", padx=2, pady=2)
        self.title_max_feat.grid(row=5, column=0, columnspan=3, sticky="NSEW", padx=2, pady=2)
        self.max_feat.grid(row=6, column=0, columnspan=3, sticky="NSEW", padx=2, pady=2)
        self.title_cores.grid(row=7, column=0, columnspan=3, sticky="NSEW", padx=2, pady=2)
        self.cores.grid(row=8, column=0, sticky="NSEW", padx=2, pady=2)
        self.go.grid(row=9, column=0, columnspan=3, sticky="NSEW", padx=2, pady=2)
        self.progress.grid(row=10, column=0, columnspan=3, sticky="NSEW", padx=2, pady=2)
        # containers

        # Grad layout

        # Binds
        self.bind('<Escape>', esc_bind)
        # Global
        self.check_btn_list = {}
        self.dat_sel_list = {}
        self.file_loc = None

    def options_out(self):
        n_est = self.n_est.get()
        n_est = list(n_est.split(','))
        max_feat = self.max_feat.get()
        max_feat = list(max_feat.split(','))
        cores = self.cores.get()
        cores = list(cores.split(','))
        opt_list = {'n_est': n_est, 'max_feat': max_feat, 'cores': cores}
        return opt_list

    def file_exp_open(self, pos):
        file_for_execute = filedialog.askopenfilenames()
        if pos == 1:
            if bool(file_for_execute):
                self.file_loc = file_for_execute
                self.train_station()

    def data_selector(self):
        sel_win = Toplevel(self)
        sel_win.grid_rowconfigure(1, weight=1)
        sel_win.grid_columnconfigure(1, weight=1)
        main_window = Frame(sel_win)
        connect_mysql = Button(main_window, text="Open CSV", height=2, width=25,
                         command=self.sql_con)
        main_window.pack(fill="both", expand=True)
        connect_mysql.grid(row=0, column=0, columnspan=3, sticky="NSEW", padx=2, pady=2)

    def sql_con(self):
        self.con_win = Toplevel(self)
        self.con_win.grid_rowconfigure(0, weight=1)
        self.con_win.grid_columnconfigure(0, weight=1)
        self.sql_con_mw = Frame(self.con_win)
        self.sql_con_mw.pack(fill="both", expand=True)
        # Lables
        tital_server_ip = Label(self.sql_con_mw, text='server name or ip', bg='green', width=20)
        title_port = Label(self.sql_con_mw, text='Port: blank for default', bg='green', width=20)
        title_user = Label(self.sql_con_mw, text='username', bg='green', width=20)
        title_password = Label(self.sql_con_mw, text='password to server', bg='green', width=20)
        title_database = Label(self.sql_con_mw, text='database name', bg='green', width=20)
        # Text filelds
        text_server_ip = Text(self.sql_con_mw, height=1, width=20)
        text_user = Text(self.sql_con_mw, height=1, width=20)
        text_password = Text(self.sql_con_mw, height=1, width=20)
        text_database = Text(self.sql_con_mw, height=1, width=20)
        text_port = Text(self.sql_con_mw, height=1, width=20)
        # Button's
        con_sql = Button(self.sql_con_mw, text="Connect SQL", height=2, width=20,
                          command=lambda ip=text_server_ip, usr=text_user, passw=text_password, db=text_database,
                                         port=text_port: self.try_con_sql(ip, usr, passw, db, port))
        # Grid layout Title's
        tital_server_ip.grid(row=0, column=0, sticky="NSEW", padx=2, pady=2)
        title_port.grid(row=2, column=0, sticky="NSEW", padx=2, pady=2)
        title_user.grid(row=4, column=0, sticky="NSEW", padx=2, pady=2)
        title_password.grid(row=6, column=0, sticky="NSEW", padx=2, pady=2)
        title_database.grid(row=8, column=0, sticky="NSEW", padx=2, pady=2)
        # Grid layout Text Field's
        text_server_ip.grid(row=1, column=0, sticky="SW", padx=2, pady=2)
        text_port.grid(row=3, column=0, sticky="SW", padx=2, pady=2)
        text_user.grid(row=5, column=0, sticky="SW", padx=2, pady=2)
        text_password.grid(row=7, column=0, sticky="SW", padx=2, pady=2)
        text_database.grid(row=9, column=0, sticky="SW", padx=2, pady=2)
        # Grid layout Buttons
        con_sql.grid(row=10, column=0, sticky="SW", padx=2, pady=2)


    def try_con_sql(self, ip, usr, passw, db, port):
        ip = ip.get("1.0", END).rstrip()
        usr = usr.get("1.0", END).rstrip()
        passw = passw.get("1.0", END).rstrip()
        db = db.get("1.0", END).rstrip()
        port = port.get("1.0", END).rstrip()
        error_bool = True
        try:
            self.con = pymysql.connect(host=ip, port=port, user=usr, password=passw, db=db,
                                  cursorclass=pymysql.cursors.DictCursor)
        except pymysql.err.OperationalError:
            error_bool = False
            messagebox.showerror(title='AttributeError', message=str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1])
                                                                                       + ' ' + str(sys.exc_info()[2]))
        if error_bool:
            self.create_all(db)

    def select_all_things(self, cbl):
        for k in cbl:
            if cbl[k].get() == 0:
                cbl[k].set(1)

    def deselect_all_things(self, cbl):
        for k in cbl:
            if cbl[k].get() == 1:
                cbl[k].set(0)

    def data_set_feed(self, cbl):
        table_list = []
        for a in cbl:
            if cbl[a].get() == 1:
                table_list.append(a)
        self.table_show.destroy()
        self.data_rf_run(table_list)

    def data_rf_run(self):
        prog_bar_p = 0
        dsl = self.dat_sel_list
        dsl_list = []
        for key in dsl:
            if dsl[key].get() == 1:
                dsl_list.append(key)
        opt = self.options_out()
        if self.file_loc is None:
            table_list = []
            for key in self.check_btn_list:
                if self.check_btn_list[key].get() == 1:
                    table_list.append(key)
            self.progress["maximum"] = len(table_list)
            with self.con as cur:
                for a in table_list:
                    fetch_all = 'SELECT * FROM ' + a
                    try:
                        cur.execute(fetch_all)
                    except ValueError:
                        continue
                    data = panda.DataFrame(cur.fetchall())
                    data = data_modle_smasher(data)
                    data = dat_molder(data)
                    plot_dat = rf_kgo(a, opt['n_est'], opt['max_feat'], opt['cores'], data, dsl_list)
                    prog_bar_p += 1
                    self.progress["value"] = prog_bar_p
                final_data = panda.DataFrame(plot_dat)
        else:
            self.progress["maximum"] = len(self.file_loc)
            for a in self.file_loc:
                data = panda.read_csv(a)
                data = data_modle_smasher(data)
                data = dat_molder(data)
                plot_dat = rf_kgo(a.rsplit('/', 1)[1], opt['n_est'], opt['max_feat'], opt['cores'], data, dsl_list)
                prog_bar_p += 1
                self.progress["value"] = prog_bar_p
            final_data = panda.DataFrame(plot_dat)
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=(("xlsx", "*.xlsx"),
                                                                                     ("All Files", "*.*")))
        path_true = os.path.normpath(file_path)
        writer = panda.ExcelWriter(path=file_path, engine='xlsxwriter')
        final_data.to_excel(writer, sheet_name='rf_out', index=False)
        writer.save()
        subprocess.Popen('powershell ' + path_true)

    def create_all(self, db):
        # window
        self.sql_con_mw.destroy()
        self.table_show = Frame(self.con_win)
        vbar = Scrollbar(self.table_show, orient=VERTICAL)
        vbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self.table_show, bd=0, highlightthickness=0,
                        yscrollcommand=vbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vbar.config(command=canvas.yview)
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        interior = Frame(canvas)
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=NW)
        self.table_show.pack()
        with self.con as cur:
            cur.execute('SHOW TABLES')
            datast_cnt = 0
            col_num = -1
            row_num = 1
            dat_all = cur.fetchall()
            for a in dat_all:
                table = a['Tables_in_' + db]
                datast_cnt += 1
                col_num += 1
                self.check_btn_list.update({table: IntVar()})
                cb = Checkbutton(self.interior, text=table, variable=self.check_btn_list[table])
                cb.grid(row=row_num, column=col_num, sticky="SW")
                if col_num > 3:
                    col_num = -1
                    row_num += 1
        select_all = Button(self.interior, text='Select All', height=2, width=20, command=lambda
            cbl=self.check_btn_list: self.select_all_things(cbl))
        deselect_all = Button(self.interior, text='deSelect All', height=2, width=20, command=lambda
            cbl=self.check_btn_list: self.deselect_all_things(cbl))
        done = Button(self.interior, text='Next!', height=2, width=20, command=self.train_station)
        done.grid(row=0, column=2, sticky="SW")
        deselect_all.grid(row=0, column=1, sticky="SW")
        select_all.grid(row=0, column=0, sticky="SW")

        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

    def train_station(self):
        if self.file_loc is not None:
            self.dat_sel = Toplevel(self)
            self.dat_sel.grid_rowconfigure(1, weight=1)
            self.dat_sel.grid_columnconfigure(1, weight=1)
            done = Button(self.dat_sel, text='Done!', height=2, width=20, command=self.dat_sel.destroy)
            cbl = self.file_loc
            for a in cbl:
                dat = panda.read_csv(a)
                datast_cnt = 0
                col_num = -1
                row_num = 2
                for b in dat:
                    rn = b
                    datast_cnt += 1
                    col_num += 1
                    self.dat_sel_list.update({rn: IntVar()})
                    cb = Checkbutton(self.dat_sel, text=rn, variable=self.dat_sel_list[rn])
                    cb.grid(row=row_num, column=col_num, sticky="SW")
                    if col_num > 2:
                        col_num = -1
                        row_num += 1
                break
        else:
            self.dat_sel = Frame(self.con_win)
            self.dat_sel.grid_rowconfigure(1, weight=1)
            self.dat_sel.grid_columnconfigure(1, weight=1)
            self.dat_sel.pack(side=LEFT, fill=BOTH, expand=TRUE)
            done = Button(self.dat_sel, text='Done!', height=2, width=20, command=self.con_win.destroy)
            self.table_show.destroy()
            cbl = self.check_btn_list
            with self.con as cur:
                for a in cbl:
                    if cbl[a].get() == 1:
                        cur.execute('DESCRIBE ' + a)
                        dat = cur.fetchall()
                        datast_cnt = 0
                        col_num = -1
                        row_num = 2
                        for b in dat:
                            rn = b['Field']
                            datast_cnt += 1
                            col_num += 1
                            self.dat_sel_list.update({rn: IntVar()})
                            cb = Checkbutton(self.dat_sel, text=rn, variable=self.dat_sel_list[rn])
                            cb.grid(row=row_num, column=col_num, sticky="SW")
                            if col_num > 2:
                                col_num = -1
                                row_num += 1
                        break
                    else:
                        continue
        frame_title = Label(self.dat_sel, text='Select the training column(s).', bg='green', width=20)
        select_all = Button(self.dat_sel, text='Select All', height=2, width=20, command=lambda
            cbl=self.dat_sel_list: self.select_all_things(cbl))
        deselect_all = Button(self.dat_sel, text='deSelect All', height=2, width=20, command=lambda
            cbl=self.dat_sel_list: self.deselect_all_things(cbl))
        frame_title.grid(row=0, column=0, columnspan=4, sticky="SW")
        done.grid(row=1, column=2, sticky="SW")
        deselect_all.grid(row=1, column=1, sticky="SW")
        select_all.grid(row=1, column=0, sticky="SW")


def esc_bind(event):
    on_closing()


def on_closing():
    FrankinbotUi().quit()


app = FrankinbotUi()
app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
