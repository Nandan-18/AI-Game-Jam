# main function
import pygame as pg
import sys
import logging
import os
from scripts import entities, dialogue, ui, progress_bar, scoring
from clients.stable_diffusion import stable_diffusion_client
from clients import utils
import asyncio


class Game:
    def __init__(self) -> None:
        pg.init()
        info = pg.display.Info()
        w = info.current_w
        h = info.current_h
        os.environ["SDL_VIDEO_CENTERED"] = '1'
        self.win = pg.display.set_mode((w, h-30), pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.fps = 60

        pg.display.set_caption("Game")

        self.playing = False

        self.click = pg.mixer.Sound("sounds/Click.mp3")
        self.wrong_answer = pg.mixer.Sound("sounds/WrongAnswerShake.mp3")

        # Create an instance of the Score class
        self.score = scoring.Score(1)

    def main_menu(self):
        print("in menu")
        start_button = ui.Button((275, 200), (400, 50), "Start")
        mute_button = ui.Button((800, 10), (100, 50), "Mute")
        pg.mixer.music.load('sounds/JeopardyTypeBeat.mp3')
        pg.mixer.music.play(-1)
        menu_playing = True
        while menu_playing:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit()

            if start_button.clicked:
                self.click.play()
                menu_playing = False
            
            start_button.update(pg.mouse.get_pressed(), pg.mouse.get_pos())
            mute_button.update(pg.mouse.get_pressed(), pg.mouse.get_pos())

            # mute audio
            if mute_button.clicked:
                pg.mixer.music.stop()
            
            pg.display.update()
            self.win.fill((250, 248, 246))
            start_button.draw(self.win)
            mute_button.draw(self.win) 

        print("out menu")



    def load(self):
        self.text_input = ui.TextInput((100, 100), "pizza")
        self.button = ui.Button((10, 10), (100, 50), "hey")
        self.image = pg.surface.Surface((512, 512))
        self.word = utils.FileUtils.get_random_word()

        pg.mixer.music.load('sounds/Suspense.mp3')
        pg.mixer.music.play(-1)

        self.dialogue_sys = dialogue.DialogueSystem()

    def update(self):
        pg.display.update()
        self.clock.tick(self.fps)
        mouse_pos = pg.mouse.get_pos()
        mouse_buttons = pg.mouse.get_pressed()
        

        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                self.quit()

            if event.type == pg.VIDEORESIZE:
                self.win = pg.display.set_mode(
                    (event.w, event.h), pg.RESIZABLE)
            if self.playing == True:
                if event.type == pg.KEYDOWN:
                    # If you press RIGHT arrow key, run synchronously
                    if event.key == pg.K_RIGHT:
                        image_bytes = stable_diffusion_client.run(
                            prompt="A dog holding a gameboy console",
                        )
                        self.image = pg.image.load(
                            image_bytes, "assets/placeholder.svg"
                        )
                    # If you press LEFT arrow key, run asynchronously
                    elif event.key == pg.K_LEFT:
                        # Change this to change the style of the art
                        preprompt = "Isometic art of "

                        prompt = preprompt + self.word

                        # Load placeholder while the image is generating
                        self.image = pg.image.load(
                            "assets/placeholder.svg"
                        )

                        loop = asyncio.get_event_loop()
                        coroutine = stable_diffusion_client.arun(
                            prompt=prompt
                        )
                        logging.info("Generating image...")
                        image_bytes = loop.run_until_complete(coroutine)
                        logging.info("Image generated!")

                        # Pygame needs a name for the image file even if it's
                        # not going to be saved, so we just use a placeholder.
                        self.image = pg.image.load(
                            image_bytes, "assets/placeholder.svg"
                        )

                        # Get a new word for the next round
                        self.word = utils.FileUtils.get_random_word()

        self.text_input.update(events)
        self.button.update(mouse_buttons, mouse_pos)
        self.dialogue_sys.update(events)



    def draw(self):
        self.win.fill((0, 200, 200))
        self.text_input.draw(self.win)
        self.dialogue_sys.draw(self.win)
        self.score.draw(self.win)  # Draw the score
        self.win.blit(pg.transform.scale(
            self.image,
            tuple(stable_diffusion_client.image_dimensions)),
            (self.win.get_width()/2 - self.image.get_width()//2, self.win.get_height()/3 - self.image.get_height()//2),
        )


    def run(self):
        self.main_menu()
        self.load()

        while True:
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
