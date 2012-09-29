def hello(language="english"):
    '''
    Says hello in the specified language... sort of!
    '''
    return {
        'chinese': 'ni hao',
        'croatian': 'bok',
        'english': 'hello',
        'filipino': 'kumusta',
        'german': 'hallo',
        'hindi': 'namaste',
        'japanese': 'konnichiwa',
        'swahili': 'hujambo',
        'thai': 'swadikap'
        }.get(language, "Sorry I can't speak {0}, still, hello!"
                .format(language))
