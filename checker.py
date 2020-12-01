import telega
from timeloop import Timeloop
from datetime import timedelta

bot = telega.TelBot()

tl = Timeloop()


@tl.job(interval=timedelta(minutes=1))
def check():
    bot.check_out()


if __name__ == "__main__":
    tl.start(block=True)
