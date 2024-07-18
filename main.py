import threading
from tkinter import messagebox
from selenium import webdriver
from tkinter import *
from centrar_Ventana import centrar_ventana
from tkinter import filedialog
from selenium.webdriver.chrome.options import Options
import tkinter as tk
import os
from utils import get_emails_from_file
from scrapping import verify_email
from const import EMAIL_VALIDATION_RESULT
import time

class EmailsValidator():
    def __init__(self):
        #Selenium config
        self.options = Options()
        self.options.binary_location = "chrome-win64/chrome.exe"
        self.browser = None
        self.url = f"https://www.verifyemailaddress.org/es/validacion-de-email"
        
        #global variables
        self.original_email_list = []
        self.emails_to_verify = []
        self.valid_mails = []
        self.invalid_mails = []
        self.error_analizing_mails = []
        self.not_analized_mails = []
        self.stop_validation = False
        self.stop_validation_message = None
        
        #creamos la ventana
        self.root = Tk()

        #propiedades de la ventana
        self.root.title("Email Validator") 
        self.root.resizable(0,0)
        self.root.geometry(centrar_ventana(600, 700, self.root)) 
        
        #logo
        self.absolute_folder_path = os.path.dirname(os.path.realpath(__file__))
        self.icon_path = os.path.join(self.absolute_folder_path, './logo.png')
        self.icon = PhotoImage(file = self.icon_path)
        self.root.iconphoto(True, self.icon)
        
        #frame que contiene los elementos
        self.frame = Frame() # se crea el frame
        self.frame.pack(fill = "both", expand = "true")
        self.frame.config(width = "600", height = "500")
        
        #label emails to verify
        self.label_ruta_emails_to_verify = Label(self.frame, text = "Emails to Verify")
        self.label_ruta_emails_to_verify.place(x = 10, y = 13 ) 
        
        #button to select the emails to verify
        self.button_select_file_with_emails = Button(self.frame, text = "Seleccionar", command = self.get_emails_to_verify)
        self.button_select_file_with_emails.place(x = 100, y = 10)
        
        #boton to clear the email to verify textarea
        self.button_reset = Button(self.frame, text = "Reset", command = self.reset)
        self.button_reset.place(x = 550, y = 10)
        
        #label to show the amount of email
        self.label_total_emails = Label(self.frame, text = "")
        self.label_total_emails.place(x = 200, y = 10)
        
        #label to show the amount of email verifyed
        self.label_verifyed_emails = Label(self.frame, text = "")
        self.label_verifyed_emails.place(x = 300, y = 10)
        
        #label to show the amount of email to verify
        self.label_emails_to_verify = Label(self.frame, text = "")
        self.label_emails_to_verify.place(x = 400, y = 10)
        
        #textarea with the emails to verify
        self.textarea_emails_to_verify = Text(self.frame)
        self.textarea_emails_to_verify.config(width = 72, height = 15, state="disabled")
        self.textarea_emails_to_verify.place(x = 10, y = 50)
        
        #button validate emails
        self.button_convert = Button(self.frame, text = "Validar Emails", command = self.handle_start_verification_emails)
        self.button_convert.config(bg="green", fg="white", width = 15, height = 2)
        self.button_convert.place(x = 10, y = 310)
        
        #button stop validating emails
        self.button_stop_validating_emails = Button(self.frame, text = "Detener Validación", command = lambda: threading.Thread(target = self.handle_stop_validation).start())
        self.button_stop_validating_emails.config(bg="green", fg="white", width = 15, height = 2)
        self.button_stop_validating_emails.place(x = 150, y = 310)
        
        #labe loading state
        self.label_loading_state = Label(self.frame, text = "")
        self.label_loading_state.place(x = 300, y = 320)
        
        #text to show the output of the program
        self.text_area_log = Text(self.frame)
        self.text_area_log.config(width = 72, height = 14, state="disabled")
        self.text_area_log.place(x = 10, y = 365)
        
        #label to show the result of verification
        self.label_show_result = Label(self.frame, text = "")
        self.label_show_result.place(x = 10, y = 600)
        
        #button export valid mails
        self.button_export_valid_mails = Button(self.frame, text = "Exportar mails válidos", command = self.handle_export_valid_mails)
        self.button_export_valid_mails.config(bg="green")
        self.button_export_valid_mails.place(x = 10, y = 650)
        
        #button export invalid mails
        self.button_export_invalid_mails = Button(self.frame, text = "Exportar mail inválidos", command = self.handle_export_invalid_mails)
        self.button_export_invalid_mails.config(bg="green")
        self.button_export_invalid_mails.place(x = 140, y = 650)
        
        #button exporterror analizing mails
        self.button_export_error_analizing_mails = Button(self.frame, text = "Exportar con errores al verificar", command = self.handle_export_error_analizing_mails)
        self.button_export_error_analizing_mails.config(bg="green")
        self.button_export_error_analizing_mails.place(x = 278, y = 650)
        
        #button export not analized mails
        self.button_export_not_analized_mails = Button(self.frame, text = "Exportar  no analizados", command = self.handle_export_not_analized_mails)
        self.button_export_not_analized_mails.config(bg="green")
        self.button_export_not_analized_mails.place(x = 460, y = 650)
        
        self.root.mainloop()

    def get_emails_to_verify(self):
        self.textarea_emails_to_verify.config(state = "normal")
        emails_file_path = filedialog.askopenfilename(parent = self.frame, title='Selecciona el acrhivo con los emails', filetypes=[("TXT file","*.txt")])
        emails = get_emails_from_file(emails_file_path)
        cont_emails = len(self.emails_to_verify) + 1
        self.emails_to_verify = self.emails_to_verify + emails
        self.original_email_list = self.emails_to_verify.copy()
        for email in emails: 
            self.textarea_emails_to_verify.insert(END, f"{cont_emails}. {email}\n")
            cont_emails += 1
            self.textarea_emails_to_verify.see("end")                
        self.textarea_emails_to_verify.config(state = "disabled")
        #update the label with the amount of emails
        self.label_total_emails.config(text = f"Total: {len(self.original_email_list)}") 
        self.label_verifyed_emails.config(text = f"Verificados: {len(self.valid_mails) + len(self.invalid_mails) + len(self.error_analizing_mails)}") 
        self.label_emails_to_verify.config(text = f"Pendientes: {len(self.emails_to_verify)}") 
    
    def reset(self):
        #reset all the global variables
        self.original_email_list = []
        self.emails_to_verify= []
        self.valid_mails = []
        self.invalid_mails = []
        self.not_analized_mails = []
        self.error_analizing_mails = []
        #clear the email list textarea
        self.textarea_emails_to_verify.config(state = "normal")
        self.textarea_emails_to_verify.delete(1.0, "end") 
        self.textarea_emails_to_verify.config(state = "disabled") 
        #clear the output textarea
        self.text_area_log.config(state = "normal")
        self.text_area_log.delete(1.0, "end") 
        self.text_area_log.config(state = "disabled") 
        #update the label with the amount of emails
        self.label_total_emails.config(text = "") 
        self.label_verifyed_emails.config(text = "") 
        self.label_emails_to_verify.config(text = "") 
        #remove load status
        self.label_loading_state.config(text = "")
        #clear result text
        self.label_show_result.config(text = "")
    
    def handle_start_verification_emails(self):
        if len(self.emails_to_verify) == 0:
            return messagebox.showinfo("!", "Debes importar los mails para verificar")
        #disable button to evoid user click them
        self.button_reset.config(state = "disabled")
        self.button_select_file_with_emails.config(state = "disabled")
        self.button_convert.config(state = "disabled")
        #start verification
        self.stop_validation = False
        self.label_show_result.config(text = "")
        threading.Thread(target = self.handle_verify_emails).start()
        
    def handle_verify_emails(self):
        #open the browser and go to the url
        self.browser = webdriver.Chrome(options=self.options)
        self.browser.get(str(self.url))
        self.show_load_state()
        time.sleep(5)
        #verify each email
        emails_to_verify = self.emails_to_verify.copy()
        for email in emails_to_verify:
            if self.stop_validation == True:
                self.not_analized_mails = self.emails_to_verify.copy()
                break
            res = verify_email(self.browser, email, self.callback_log_function, self.callback_show_messagebox_function)   
            if res == EMAIL_VALIDATION_RESULT["VALID"]:
                self.valid_mails.append(email)
            elif res == EMAIL_VALIDATION_RESULT["INVALID"]:
                self.invalid_mails.append(email)
            else:
                self.error_analizing_mails.append(email)
            self.remove_verifyed_emails(email)
            self.show_load_state()
        
        self.show_validation_result()
        if self.stop_validation_message != None:
            self.stop_validation_message.destroy()
    
    def remove_verifyed_emails(self, email):
        self.emails_to_verify.remove(email)  
        #update textarea with the email to verify to show the correct email list
        cont_emails = 1
        self.textarea_emails_to_verify.config(state = "normal")
        self.textarea_emails_to_verify.delete(1.0, "end") 
        for email in self.emails_to_verify: 
            self.textarea_emails_to_verify.insert(END, f"{cont_emails}. {email}\n")
            cont_emails += 1
            self.textarea_emails_to_verify.see("end")                
        self.textarea_emails_to_verify.config(state = "disabled")
        self.label_total_emails.config(text = f"Total: {len(self.emails_to_verify)}")
        
    def callback_log_function(self, log):
        '''function to show a log in the log textarea'''
        self.text_area_log.config(state = "normal")
        self.text_area_log.insert(END, f"•{log}\n \n")
        self.text_area_log.see("end")
        self.text_area_log.config(state = "disabled")
        
    def callback_show_messagebox_function(self, message):
        '''function to show a message box'''
        messagebox.showinfo("!",message)
    
    def handle_export_valid_mails(self):
        path = str(filedialog.askdirectory())
        with open(f'{path}/valid_emails.txt', 'w') as archivo:
            for email in self.valid_mails:
                archivo.write(email + '\n')
    
    def handle_export_invalid_mails(self):
        path = str(filedialog.askdirectory())
        with open(f'{path}/invalid_emails.txt', 'w') as archivo:
            for email in self.invalid_mails:
                archivo.write(email + '\n')
    
    def handle_export_error_analizing_mails(self):
        path = str(filedialog.askdirectory())
        with open(f'{path}/error_analizing_emails.txt', 'w') as archivo:
            for email in self.error_analizing_mails:
                archivo.write(email + '\n')    
                
    def handle_export_not_analized_mails(self):
        path = str(filedialog.askdirectory())
        with open(f'{path}/not_analized_emails.txt', 'w') as archivo:
            for email in self.not_analized_mails:
                archivo.write(email + '\n')    
    
    def show_validation_result(self):
        self.label_show_result.config(text = f"Mails Válidos: {len(self.valid_mails)} | Mails Inválidos: {len(self.invalid_mails)} | Mails con error al Analizarlos: {len(self.error_analizing_mails)} | Mails No Analizados: {len(self.not_analized_mails)}")
    
    def handle_stop_validation(self):
        #show message "stoping validation"
        self.stop_validation_message = tk.Toplevel()
        self.stop_validation_message.title("!")
        self.stop_validation_message.geometry(centrar_ventana(300, 50, self.stop_validation_message))
        tk.Label(self.stop_validation_message, text="Deteniendo Verificación").pack(ipady=10)
        
        self.stop_validation = True  
        self.button_reset.config(state = "normal")
        self.button_select_file_with_emails.config(state = "normal")
        self.button_convert.config(state = "normal")
        if self.browser != None:
            self.browser.quit()
        self.browser = None
    
    def show_load_state(self):
        percent = round( ( ( ( len(self.valid_mails) + len(self.invalid_mails) + len(self.error_analizing_mails)) / len(self.original_email_list) ) * 100 ), 1)
        self.label_loading_state.config(text = f"Verificando Mails: {percent} %")   
        #update the label with the amount of emails
        self.label_total_emails.config(text = f"Total: {len(self.original_email_list)}") 
        self.label_verifyed_emails.config(text = f"Verificados: {len(self.valid_mails) + len(self.invalid_mails) + len(self.error_analizing_mails)}") 
        self.label_emails_to_verify.config(text = f"Pendientes: {len(self.emails_to_verify)}") 
    
EmailsValidator()        