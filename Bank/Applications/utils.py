from .models import *
from .procedure import *

class UserInfo:
    def get_user_info(self, request):
        user = request.user  # Текущий пользователь
        client = False
        employee = False
        admin = False
        profile = False
        authorization = user.is_authenticated
        if authorization:
            client: bool = check_group(user, "Client")
            employee: bool = check_group(user, "Employee")
            admin: bool = check_group(user, "Admin")
            profile = check_profile_existence(user)  # Делаем проверочку зарегистрован ли профиль в системе
        return {
            "client": client,
            "employee": employee,
            "admin": admin,
            "profile": profile,
            "authorization": authorization,
            "login": user.username,
            "groups": user.groups.all()
        }
