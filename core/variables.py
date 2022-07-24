import json


def token():
    with open("./config.json", "r", encoding="utf-8") as f:
        return dict(json.loads(f.read()))


TOKEN = token().get("token", None)


def text():
    with open("./config_text.json", "r", encoding="utf-8") as f:
        return dict(json.loads(f.read()))


HCOM_WEL = text().get("HCOM_WEL", None)
HCOM_AUT_EXIT = text().get("HCOM_AUT_EXIT", None)
HCOM_AUT_MUSIC = text().get("HCOM_AUT_MUSIC", None)
HCOM_AUT_NOMUSIC = text().get("HCOM_AUT_NOMUSIC", None)
HCOM_NOWEL = text().get("HCOM_NOWEL", None)
HCOM_EXIT = text().get("HCOM_EXIT", None)

HAUTH_LOGIN = text().get("HAUTH_LOGIN", None)
HAUTH_PS = text().get("HAUTH_PS", None)

HID_MUSIC = text().get("HID_MUSIC", None)
HSR_MUSIC = text().get("HSR_MUSIC", None)
H_MUSIC_RD = text().get("H_MUSIC_RD", None)
