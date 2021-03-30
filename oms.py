
def oreMinutiSecondi(h, m, s, id):
    """Analyze hours, minutes and seconds, choosing which sentence is grammatically correct
    
    :param h: hours
    :param m: minutes
    :param s: seconds
    :param id: to understand if it's used for playlist duration or time spent for analyzing the playlist
    :type h: int
    :type m: int
    :type s: int
    :type id: int
    
    :return: Returns a grammatically correct string to display hours minutes and seconds, if h, m, s are < 0 return None
    """
    output = ""
    if h < 0 and m < 0 and s < 0 and id != 0 and id != 1:
        return None
    else:
        if h == 1 and m > 1 and s > 1:  # 1NN
            output += (f'Un\'ora, {m} minuti e {s} secondi.')
        elif h > 1 and m == 1 and s > 1:  # N1N
            output += (f'{h} ore, un minuto e {s} secondi.')
        elif h == 1 and m == 1 and s == 1:  # 111
            output += ('Un\'ora, un minuto e un secondo.')
        elif h > 1 and m == 1 and s == 1:  # N11
            output += (f'{h} ore, un minuto e un secondo.')
        elif h == 1 and m == 1 and s > 1:  # 11N
            output += (f'Un\'ora, un minuto e {s} secondi.')
        elif h == 1 and m > 1 and s == 1:  # 1N1
            output += (f'Un\'ora, {m} minuti e un secondo.')
        elif h > 1 and m > 1 and s == 1:  # NN1
            output += (f'{h} ore, {m} minuti e un secondo.')
        elif h > 1 and m > 1 and s > 1:  # NNN
            output += (f'{h} ore, {m} minuti e {s} secondi.')
        elif h == 0 and m == 0 and s == 0 and id == 0:  # 000 tempo impiegato
            output += ('Istantaneo.')
        elif h == 0 and m == 0 and s == 0 and id == 1:  # 000 playlist vuota
            output += ('La PlayList è vuota.')
        elif h == 0 and m > 1 and s > 1:  # 0NN
            output += (f'{m} minuti e {s} secondi.')
        elif h > 1 and m == 0 and s > 1:  # N0N
            output += (f'{h} ore e {s} secondi.')
        elif h > 1 and m == 0 and s == 0:  # N00
            output += (f'{h} ore.')
        elif h == 0 and m == 0 and s > 1:  # 00N
            output += (f'{s} secondi.')
        elif h == 0 and m > 1 and s == 0:  # 0N0
            output += (f'{m} minuti.')
        elif h > 1 and m > 1 and s == 0:  # NN0
            output += (f'{h} ore e {m} minuti.')
        elif h == 1 and m == 0 and s == 0:  # 100
            output += ('Un\'ora.')
        elif h == 0 and m == 1 and s == 0:  # 010
            output += ('Un minuto.')
        elif h == 0 and m == 0 and s == 1:  # 001
            output += ('Un secondo.')
        elif h == 0 and m > 1 and s == 1:  # 0N1
            output += (f'{m} minuti e un secondo.')
        elif h > 1 and m == 0 and s == 1:  # N01
            output += (f'{h} ore e un secondo.')
        elif h == 0 and m == 1 and s > 1:  # 01N
            output += (f'Un minuto e {s} secondi.')
        elif h == 0 and m == 1 and s == 1:  # 011
            output += ('Un minuto e un secondo.')
        elif h == 1 and m == 0 and s == 1:  # 101
            output += ('Un\'ora e un secondo.')
        elif h == 1 and m == 0 and s > 1:  # 10N
            output += (f'Un\'ora e {s} secondi.')
        elif h == 1 and m == 1 and s == 0:  # 110
            output += ('Un\'ora e un minuto.')
        elif h == 1 and m > 1 and s == 0:  # 1N0
            output += (f'Un\'ora e {m} minuti.')
        elif h > 1 and m == 1 and s == 0:  # N10
            output += (f'{h} ore e un minuto.')
        return output
