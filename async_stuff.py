import arrow
import asyncio
import speech_recognition as sr

r = sr.Recognizer()
mic = sr.Microphone()
now = arrow.utcnow()


class Test:
    def __init__(self):
        self.phrase = asyncio.Future()
        self.awakeners = [1, 2, 3]

    def callback(self, recognizer, audio):
        print("called back!")

        try:
            if not self.phrase.done():
                phrase = r.recognize_google(audio).lower()
                self.phrase.set_result(phrase)

        except sr.UnknownValueError:
            pass

    async def listen(self, n_secs):
        print("listening")
        self.phrase = asyncio.Future()

        while not self.phrase.done():  # while not activated
            print("about to listen...")
            with mic as source:
                r.adjust_for_ambient_noise(source)

            stop_listening = r.listen_in_background(mic, self.callback)

            try:

                await asyncio.wait_for(self.phrase, n_secs)
                print("done awaiting!")
                break

            except TimeoutError:
                break

        stop_listening()
        self.phrase = self.phrase.result() if self.phrase.done() else ""

        return self.phrase

    async def check_awakeners(self):
        while isinstance(self.phrase, asyncio.Future):  # while not activated
            for i in range(len(self.awakeners)):
                self.awakeners[i] += 1

                # if isinstance(self.phrase, asyncio.Future):
            await asyncio.sleep(1)

    async def main(self):
        await asyncio.gather(self.listen(10), self.check_awakeners())

    def run(self):
        loop = asyncio.get_event_loop()
        output = loop.run_until_complete(self.main())
        print(output)
        loop.close()


if __name__ == "__main__":
    test = Test()
    test.run()
