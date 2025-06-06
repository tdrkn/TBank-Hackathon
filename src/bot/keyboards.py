from telegram import ReplyKeyboardMarkup


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([
        ["/digest", "/rank"],
    ], resize_keyboard=True)
