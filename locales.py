class TEXT:
    ON_START = 'onStartMessage'
    ON_HELP = 'onHelpMessage'
    ON_BIND_ERROR = 'onBindError'
    ON_UNBIND_DELETE = 'onUnbindDelete'
    ON_UNBIND_DELETE_ERROR = 'onUnbindDeleteError'
    ON_LIST = 'onListMessage'
    ON_LIST_EMPTY = 'onListEmpty'


LOCALES = {
    'ru': {
        TEXT.ON_START: 'Привет, я бот, который позволяет быстро получать доступ к заранее заготовленной информации'
                       ' и моментально отправлять её в телеграм. Введите /help для дополнительной информации',
        TEXT.ON_HELP: 'Для того, чтобы задать ключевое слово используй \n'
                      '<code>/bind</code> <b>&lt;ключевое_слово&gt;</b> <i>любое ваше значение</i>\n '
                      'Ключевое слово не должно содержать пробелов.\n '
                      'Всё, что указано после ключевого слова станет его значением.\n '
                      'Если ключевое слово уже существует, его значение будет переписано.\n\n'
                      '<code>/unbind</code> <b>&lt;ключевое_слово&gt;</b>\n'
                      'Удаляет ключевое слово.\n\n'
                      '/list\n'
                      'Отображает список всех сгенерированных ключевых слов.\n\n'
                      'Для использования созданных ключевых слов просто набери в чате '
                      '\n<code>@kBinderBot</code> <b>&lt;ключевое_слово&gt;</b>'
                      '\nи нажмите на появившийся предложенный ответ.',
        TEXT.ON_BIND_ERROR: 'Формат /bind не верен. \n'
                            'Не хватает аргументов. \n'
                            'Используй /bind &lt;ключевое_слово&gt; <значение>. \n'
                            'Используй /help для дополнительной информации.',
        TEXT.ON_UNBIND_DELETE: 'Ключевое слово успешно удалено',
        TEXT.ON_UNBIND_DELETE_ERROR: 'Ключевое слово не найдено',
        TEXT.ON_LIST: '<b>Твои ключевые слова:</b>\n{}',
        TEXT.ON_LIST_EMPTY: 'У тебя ещё нет ключевых слов. Задай их с помошью <code>/bind</code>.\n'
                            'Введи /help для дополнительной информации.'
    },
    'en': {
        TEXT.ON_START: 'Hi, I am a bot that allows you to quickly access preliminary prepared information and '
                       'instantly send it in Telegram. Type /help for more information',
        TEXT.ON_HELP: 'To set a keyword use \n'
                      '<code>/bind</code> <b>&lt;keyword&gt;</b> <i>everything you want</i>\n'
                      'The keyword must not contain spaces. \n'
                      'If the keyword already exists, its value will be overwritten.\n'
                      'All, what follows the keyword becomes its value. \n\n'
                      '<code>/unbind</code> <b>&lt;keyword&gt;</b>\n'''
                      'Deletes the <b>keyword</b>\n\n'
                      '/list '
                      '\nDisplays a list of all generated keywords.\n'
                      'To use the generated keywords, just type in chat\n'
                      '<code>@kBinderBot</code> <b>&lt;keyword&gt;</b>'
                      '\nand click on the suggested answer that appears',
        TEXT.ON_BIND_ERROR: 'Invalid format for /bind. \n'
                            'Not enough arguments. \n'
                            'Use <code>/bind &lt;keyword&gt; <value></code>. \n'
                            'Use /help for additional info.',
        TEXT.ON_UNBIND_DELETE: 'Keyword successfully deleted',
        TEXT.ON_UNBIND_DELETE_ERROR: 'Keyword not found',
        TEXT.ON_LIST: '<b>Your keywords:</b>\n{}',
        TEXT.ON_LIST_EMPTY: 'You have no keywords yet. Add them using <code>/bind</code>.\n'
                            'Type /help for additional information.'
    }
}
