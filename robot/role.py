num = 0


def reset_num():
    global num
    num = 0


class role:
    friend = 0
    no = 0  # 从1开始
    identity = 0
    union = -1
    status = 1  # 1alive -2vote -1wolf 0witch
    link = -1
    skill = [1, 1]
    police = 0

    def __init__(self, friend):
        self.friend = friend
        global num
        num = 1 + num
        self.no = num

    def get_friend(self):
        return self.friend

    def set_identity(self, identity):
        self.identity = identity

    def get_identity(self):
        return self.identity

    def set_union(self, u):
        self.union = u

    def get_union(self):
        return self.union

    def set_status(self, status):
        self.status = status

    def get_status(self):
        return self.status

    def get_no(self):
        return self.no

    def set_link(self, r):
        self.link = r

    def get_link(self):
        return self.link

    def set_status(self, status: int):
        self.status = status

    def get_status(self):
        return self.status

    def set_skill(self, num: int, value: int):
        self.skill[num] = value

    def get_skill(self):
        return self.skill

    def set_police(self):
        self.police = 1

    def get_police(self):
        return self.police
