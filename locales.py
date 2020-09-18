class TEXT:
    on_start = 'onStartMessage'
    on_help = 'onHelpMessage'


LOCALES = {
    'ru': {
        TEXT.on_start: 'Привет, я бот, который позволяет быстро получать доступ к заранее заготовленной информации'
                       ' и моментально отправлять её в телеграм. Введите /help для дополнительной информации',
        TEXT.on_help: 'Для того, чтобы задать ключевое слово используй \n`/bind <ключевое слово> <значение>`\n '
                      'Ключевое слово не должно содержать пробелов. Всё, '
                      'что указано после ключевого слова станет его значением\n\n'
                      'Для отображения списка всех созданых ключевых слов используй \n/list\n'
                      'При нажатии на ключевое слово выведется его значение'
    },
    'en': {
        TEXT.on_start: 'Hi, I am a bot that allows you to quickly access preliminary prepared information and '
                       'instantly send it in Telegram. Type /help for more information',
        TEXT.on_help: 'To set a keyword use \n`/bind <keyword> <value>`\n'
                      'The keyword must not contain spaces. All, '
                      'what follows the keyword becomes its value \n\n'
                      'Use \n /list \n to display a list of all generated keywords'
    }
}
