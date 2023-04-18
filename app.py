import os
from core.http.navigator import Browser

URL_BASE = "https://ava3.cefor.ifes.edu.br/"


class AvaClientApi(Browser):

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        self.token = None
        self.course_link = None
        self.set_headers()
        self.headers = self.get_headers()

    def get_token(self):
        print("Gerando nova sessão...")
        self.response = self.send_request(
            "GET",
            f"{URL_BASE}/login/index.php",
            headers=self.headers
        )
        self.token = self.get_soup().find_all(
            "input", {"name": "logintoken"})[0]["value"]

    def auth(self):
        result_status = False
        if not os.path.exists("./session.json"):
            self.get_token()
            payload = {
                "anchor": "",
                "username": self.username,
                "password": self.password,
                "logintoken": self.token,
                "rememberusername": "1"
            }
            self.headers["referer"] = URL_BASE
            self.response = self.send_request(
                "POST",
                f"{URL_BASE}/login/index.php",
                data=payload,
                headers=self.headers
            )
            self.save_cookies()
        else:
            self.headers["referer"] = URL_BASE
            self.response = self.send_request(
                "POST",
                f"{URL_BASE}/my",
                headers=self.headers
            )
        message = self.get_soup().find("div", {"class": "logininfo"}).get_text()
        if "Sair" in message:
            message = message.replace("(Sair)", "")
            result_status = True
        else:
            if os.path.exists("./session.json"):
                os.remove("./session.json")
                print("Sessão expirada, efetuando login novamente...")
                self.auth()
        return result_status, message

    def get_courses(self):
        courses = self.get_soup().find(
            "div", {"class": "dropdown-menu"}).find_all("a")
        for index, course in enumerate(courses):
            print(f'[{index}] {course.get_text()}')

        action = int(input("\nSelecione o item inserindo o número correspondente: "))
        course_selected = courses[action].get_text()
        self.course_link = courses[action]["href"]
        print(course_selected, self.course_link)

    def open_course(self):
        self.response = self.send_request(
            "GET",
            self.course_link,
            headers=self.headers
        )
        self.page_preview()


if __name__ == "__main__":
    ava_client = AvaClientApi("USER", "SENHA")
    status, reason = ava_client.auth()
    print(f"{reason}\n")
    if status:
        ava_client.get_courses()
        ava_client.open_course()
