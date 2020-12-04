import logging

#level - i,w,e,d
#module_name - name of py file
#step - int log number at py file
#message - any message
def make_log(level,module_name , step, message=None ):
    log_message = {'module':module_name,
                    'step': step,
                    'message': message,
                    }

    #initial modules
    if module_name == 'app' and step == 0:
        logging.info('=' * 30)
    elif step == 0:
        logging.info('-' * 20)


    #log message
    if level == 'i':
        logging.info(log_message)
    elif level == 'w':
        logging.warning(log_message)
    elif level == 'e':
        logging.error(log_message)
    elif level == 'd':
        logging.debug(log_message)


    return step + 1
