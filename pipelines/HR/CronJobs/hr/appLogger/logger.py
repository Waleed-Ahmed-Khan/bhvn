import datetime, pytz


class AppLogger:
    def __init__(self):
        pass

    def log(self, file_object, log_message):
        self.date = datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%m/%d/%Y")
        self.current_time = datetime.datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%H:%M:%S")
        file_object.write(
            str(self.date) + "__" + str(self.current_time) + "\t\t" + log_message +"\n")