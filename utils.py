def get_emails_from_file(path):
    with open(path, 'r') as file:
        emails = file.readlines()
        file.close()
        return [email.replace("\n", "") for email in set(emails) if email != "\n"]
