class TEXT:
    ON_START = 'onStartMessage'
    ON_HELP = 'onHelpMessage'
    ON_BIND_ERROR = 'onBindError'
    ON_BIND_DELETE = 'onBondDelete'
    ON_BIND_DELETE_ERROR = 'onBondDelete'
    ON_LIST = 'onList'


LOCALES = {
    'ru': {
        TEXT.ON_START: 'Привет, я бот, который позволяет быстро получать доступ к заранее заготовленной информации'
                       ' и моментально отправлять её в телеграм. Введите /help для дополнительной информации',
        TEXT.ON_HELP: 'Для того, чтобы задать ключевое слово используй \n'
                      '`/bind <ключевое слово> <значение>`\n '
                      'Ключевое слово не должно содержать пробелов.\n '
                      'Всё, что указано после ключевого слова станет его значением.\n '
                      'Если ключевое слово уже существует, его значение будет переписано.\n '
                      'Если значение не указано, ключевое слово будет удалено\n\n'
                      '/list\nОтображает список всех сгенерированных ключевых слов',
        TEXT.ON_BIND_ERROR: 'Формат /bind не верен. \n'
                          'Не хватает аргументов. \n'
                          'Используй /bind <ключевое слово> <значение>. \n'
                          'Используй /help для дополнительной информации.',
        TEXT.ON_BIND_DELETE: 'Ключевое слово успешно удалено',
        TEXT.ON_BIND_DELETE_ERROR: 'Ключевое слово не существует',
        TEXT.ON_LIST: 'Твои ключевые слова:\n{}'
        
    },
    'en': {
        TEXT.ON_START: 'Hi, I am a bot that allows you to quickly access preliminary prepared information and '
                       'instantly send it in Telegram. Type /help for more information',
        TEXT.ON_HELP: 'To set a keyword use \n'
                      '`/bind <keyword> <value>`\n'
                      'The keyword must not contain spaces. \n'
                      'If the keyword already exists, its value will be overwritten.\n'
                      'All, what follows the keyword becomes its value. \n'
                      'If no value is specified, the keyword will be removed \n\n'
                      '/list \nDisplays a list of all generated keywords',
        TEXT.ON_BIND_ERROR: 'Invalid format for /bind. \n'
                          'Not enough arguments. \n'
                          'Use `/bind <keyword> <value>`. \n'
                          'Use /help for additional info.',
        TEXT.ON_BIND_DELETE: 'Keyword successfully deleted',
        TEXT.ON_BIND_DELETE_ERROR: 'Keyword is not exist',
        TEXT.ON_LIST: 'Your keywords:\n{}'
    }
}
