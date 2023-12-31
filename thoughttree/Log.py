from Console import Console


class Log:
    def __init__(self, console: Console):
        self.console = console

    def system(self, message):
        self.console.tagged("system", message)

    def user(self, message):
        self.console.tagged("user", message)

    def assistant(self, message):
        self.console.tagged("assistant", message)

    def debug(self, message):
        self.console.tagged("debug", message)

    def info(self, message):
        self.console.tagged("info", message)

    def warn(self, message):
        self.console.tagged("warn", message)

    def error(self, message):
        self.console.tagged("error", message)

    def critical(self, message):
        self.console.tagged("critical", message)

    def cost(self, message):
        self.console.tagged("cost", message)


    # log = Log(self.ui.console)
    # log.system("System message")
    # log.user("User message")
    # log.assistant("Assistant message")
    # log.debug("Debug message")
    # log.info("Info message")
    # log.warn("Warn message")
    # log.error("Error message")
    # log.critical("Critical message")
    # log.cost("Cost message")
