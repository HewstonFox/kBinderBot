class MESSAGE:
    class COMMAND:
        START = 'message_start'
        HELP = 'message_help'
        LIST = 'message_list'
        LIST_EMPTY = 'message_list_empty'

    class BIND:
        ERROR = 'bind_error'

    class KEYWORD:
        class DELETE:
            SUCCESS = 'keyword_delete_success'
            ERROR = 'keyword_delete_error'
