import os
from email.message import EmailMessage
import smtplib
import ssl
from email.message import EmailMessage


def enviar_mail(receptor, asunto, cuerpo):
    try:
        # Define email sender and receiver
        email_sender = 'exerom.eldorado.desarrollo@gmail.com'
        email_password = "zixudnydwgjgwmqb"
        email_receiver = receptor

        # Set the subject and body of the email
        subject = asunto
        body = cuerpo

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        # Add CSV attachments from 'ultima_respuesta' folder
        #path = r'C:\Abastecimiento\bot_abastecimiento\test\ultima_respuesta'
        #for file_name in os.listdir(path):
        #    if file_name.endswith('.csv'):
        #        with open(os.path.join(path, file_name), 'rb') as f:
        #           em.add_attachment(f.read(), maintype='text', subtype='csv', filename=file_name)
                    
        # Add SSL (layer of security)
        context = ssl.create_default_context()

        # Log in and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
    except Exception as e:
        print(e)
        

    else:
        print("Correo enviado con éxito")



if __name__ == '__main__':
    enviar_mail('francogdimartino@gmail.com', 'Prueba', 'Esto es una prueba')