import logging
import logging.handlers

def get_logger(logs_file_path):
    logger = logging.getLogger()
    fh = logging.handlers.RotatingFileHandler(logs_file_path, maxBytes=1024000, backupCount=10)
    fh.setLevel(logging.DEBUG)#no matter what level I set here
    formatter = logging.Formatter("[%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(lineno)s] : %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    #logger.info('INFO')
    #logger.error('ERROR')
    logger.setLevel(logging.INFO)
    return logger