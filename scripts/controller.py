import pygame as pg
from .dialogue import DialogueSystem
from .scoring import Score
from .ui import TextInput
from .progress_bar import ProgressBar
from .entities import Entity

from .img_gen import ImageGenerator
import random

class GameController:
    def __init__(self, win_size) -> None:
        self.win_size = win_size
        self.round = 0
        self.dialouge_sys = DialogueSystem()
        self.score = Score(self.round+1)
        self.timer = ProgressBar(200, 30, 60*20)
        self.img_gen_client = ImageGenerator(active=True, image_dimensions=[512, 512])
        self.img_gen_client.round_img_gen(1)
        new_prompt = self.img_gen_client.get_cur_prompt()
        print(f"prompt: {new_prompt}")
        self.text_input = TextInput(self.win_size[1]*8/10, new_prompt , win_size)

        self.reset_timer = 0

        self.dialouges = ["Ladies and gentlemen, welcome to AI-Eye, the game show where artificial intelligence meets human intuition! I am your host, the one and only robotic mastermind.",
                          " In this game, you'll be challenged to guess images generated by advanced AI algorithms. ",
                          "With my lightning-fast processing power, I'll be guiding you through each round as you put your visual recognition skills to the test.",
                          " So get ready to see if you can outsmart the machine and guess the AI-generated images. Let the games begin!"]

        self.round_dialouge =["Welcome back, players! Are you ready for the next round of AI-Eye?",
                              "Remember, the faster you guess, the more points you’ll earn. So put on your thinking caps and get ready to play.",
                               "Let’s begin the next round of AI-Eye!"]
        
        self.cur_dialouge = 0
        self.game_no = 0
        self.ingame = False

        self.correct_sound = pg.mixer.Sound("assets/GoodAnswerDing.mp3")
        self.wrong_sound = pg.mixer.Sound("assets/WrongAnswerShake.mp3")
        self.time_over = pg.mixer.Sound("assets/Timer-Run-Out-Sound.mp3")

        self.ent_host = Entity((win_size[0]*4//6-30, 0),["assets/robo_host"],0.3, "robo_host")
        self.ent_avatar = Entity((win_size[0]*4//6-30, 30),["assets/avatar_neutral"],0.3, "avatar_neutral")


    def to_ingame(self):
        self.dialouge_sys.visible = False
        self.img_gen_client.visible = True
        self.text_input.visible =True
        self.timer.visible = True
        self.timer.reset_timer()
        self.game_no = 0

    def to_dialouges(self):
        self.cur_dialouge = 0
        self.dialouge_sys.reset()
        self.img_gen_client.visible = False
        self.dialouge_sys.visible = True
        self.text_input.visible =False
        self.timer.visible = False
        self.ingame = False
        self.game_no = 0


    def update(self, events):
        self.dialouge_sys.update(events)
        self.timer.update()
        self.text_input.update(events)
        if self.ingame:
            self.ent_avatar.update(events)
        else:
            self.ent_host.update(events)

        if self.reset_timer >= 0:
            self.reset_timer -= 1
        
        if self.reset_timer == 0:
            self.game_no += 1
            new_prompt = self.img_gen_client.next_image()
            print(f"prompt: {new_prompt}")
            self.text_input.reset_input(new_prompt)
            self.timer.reset_timer()

            
        if self.text_input.is_completed():
            if self.text_input.is_correct_answer() and self.reset_timer == -1:
                self.reset_timer = 30
                self.correct_sound.play()
                self.score.game_update(0)
            if not self.text_input.is_correct_answer() and self.text_input.shake == 30:
                self.score.game_update(1)
                self.wrong_sound.play()

        self.img_gen_client.update(events, self.text_input.get_cur_word())
        for event in events:
            if not self.ingame:
        
                if event.type == pg.KEYDOWN and event.key == pg.K_x:
                    if self.cur_dialouge >= len(self.dialouges):

                        self.ingame = True
                        self.to_ingame()
                    else:
                        self.dialouge_sys.start_talking(self.dialouges[self.cur_dialouge], 2)
                        self.cur_dialouge += 1

        if self.timer.is_complete:
            self.time_over.play()
            self.score.game_update(2)
            new_prompt = self.img_gen_client.next_image()
            self.text_input.reset_input(new_prompt)
            self.game_no += 1
            self.timer.reset_timer()
        
        if self.score.score <= 0:
            self.score.reset_score()
            return True

        if self.game_no >= 5:
            self.round += 1
            print(f"this is round {self.round+1}")
            new_prompt = self.img_gen_client.round_img_gen(self.round+1)
            self.text_input.reset_input(new_prompt)
            self.dialouges = [f"The round is over lets start round {self.round+1}"]
            self.to_dialouges()

        return False


    def draw(self, win : pg.Surface):
        if self.ingame:
            self.ent_avatar.draw(win)
        else:
            self.ent_host.draw(win)
        self.dialouge_sys.draw(win)
        self.score.draw(win)
        self.timer.draw(win, win.get_width() // 2 - self.timer.width // 2, win.get_height() - 50)
        self.text_input.draw(win)
        self.img_gen_client.draw(win)