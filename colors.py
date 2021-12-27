class colors:
    #cant have two different colors
    ENDC = '\033[m'
    BLACK='\033[30m'
    RED='\033[31m'
    GREEN='\033[32m'
    ORANGE='\033[33m'
    BLUE='\033[34m'
    PURPLE='\033[35m'
    CYAN='\033[36m'
    LIGHTGRAY='\033[37m'
    DARKGRAY='\033[90m'
    LIGHTRED='\033[91m'
    LIGHTGREEN='\033[92m'
    YELLOW='\033[93m'
    LIGHTBLUE='\033[94m'
    PINK='\033[95m'
    LIGHTCYAN='\033[96m'
    WHITE='\33[97m'
    class front:
        BOLD    = "\033[;1m"
        REVERSE = "\033[;7m"#white background and black text
        DISABLE='\033[02m'
        UNDERLINE='\033[04m'
        STRIKETHROGH='\033[09m' #a line conering the text
        INVINSIBLE='\033[08m'

    class back:
        BLACK='\033[40m'
        RED='\033[41m'
        GREEN='\033[42m'
        ORANGE='\033[43m'
        BLUE='\033[44m'
        PURPLE='\033[45m'
        CYAN='\033[46m'
        WHITE='\033[47m'


