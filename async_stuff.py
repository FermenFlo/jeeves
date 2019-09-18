import arrow
import asyncio
import time
import speech_recognition as sr
import asyncio

r = sr.Recognizer()
mic = sr.Microphone()
now = arrow.utcnow()

class Test():
    def __init__(self):
        self.phrase = asyncio.Future()
        self.awaiters = [1,2,3]

    def callback(self, recognizer, audio):
        print('called back!')

        try:
            if not self.phrase.done():
                phrase = r.recognize_google(audio).lower()
                self.phrase.set_result(phrase)

        except sr.UnknownValueError:
            pass

    async def listen(self, n_secs):
        print('listening')
        self.phrase = asyncio.Future()

        while not self.phrase.done(): # while not activated
            print('about to listen...')
            with mic as source:
                r.adjust_for_ambient_noise(source)

            stop_listening = r.listen_in_background(mic, self.callback)

            try:

                await asyncio.wait_for(self.phrase, n_secs)
                print('done awaiting!')
                print(self.phrase)
                break

            except TimeoutError:
                break

        stop_listening()

        print('here')
        self.phrase = self.phrase.result() if self.phrase.done() else ""

        return self.phrase

            #await self.phrase

        return self.phrase.result()

    async def check_awaiters(self):
        print('checking')
        while True: # while not activated
            for i in range(len(self.awaiters)):
                self.awaiters[i] += 1

            if isinstance(self.phrase, asyncio.Future):



            await asyncio.sleep(1)

    async def main(self):
        await asyncio.gather(
            self.listen(5),
            self.check_awaiters(),
        )
        return self.phrase

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main())
        loop.close()
        print(self.phrase)
        print(self.awaiters)

test = Test()
test.run()