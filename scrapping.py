import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from const import EMAIL_VALIDATION_RESULT

def verify_email(browser, email, callback_log_function, show_messagebox):
    try:
        callback_log_function(f"Validando correo: {email}")
        #elements
        email_input = browser.find_element(By.NAME, "email")
        verify_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Verificar')]")
        #captcha
        check_captcha(browser, show_messagebox)  
        #set the email into the email input
        email_input.click()
        # Clean the email input
        email_input.send_keys(Keys.CONTROL + 'a')
        email_input.send_keys(Keys.DELETE)
        # set the new email
        email_input.send_keys(email)
        verify_button.click()
        time.sleep(3)
        #check if the "verify you are not a robot" message appears
        captcha_error_message = browser.find_elements(By.XPATH, "//div[contains(text(), 'Por favor, verifique que no es un robot')]")
        if len(captcha_error_message) > 0:
            check_captcha(browser, show_messagebox)
            verify_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Verificar')]")
            verify_button.click()  
            time.sleep(3)
        #check if the email is valid
        status_success = browser.find_elements(
            By.XPATH, 
            "//li[contains(@class, 'status') and contains(@class, 'success')]"
            )
        if len(status_success) > 0:
            callback_log_function(f"El correo {email} es valido")
            return EMAIL_VALIDATION_RESULT["VALID"]
        else:
            callback_log_function(f"El correo {email} no es valido")
            return EMAIL_VALIDATION_RESULT["INVALID"] 
    except Exception as e:
        callback_log_function(f"Error al verificar el email: {email} || {e}")  
        return EMAIL_VALIDATION_RESULT["NOT_ANALIZED"]
    
def check_captcha(browser, show_messagebox):
    time.sleep(5)
    iframe_captcha = browser.find_elements(By.XPATH, "//*[@title='reCAPTCHA']")
    if len(iframe_captcha) > 0:
        show_messagebox("Esperando solucion del captcha. Presiona enter cuando este resuelto")  