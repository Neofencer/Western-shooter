import pygame, sys
from settings import *
from player import Player
from monster import Coffin,Cactus
from pygame.math import Vector2 as vector
from pytmx.util_pygame import load_pygame
from sprite import Sprite, Bullet

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = vector()
        self.display_surface = pygame.display.get_surface()
        self.background= pygame.image.load('Western\graphics\other\BG.png').convert()

    def customize_draw(self,player):
        #change the offset vector with are moving the object in the game opposite direction of the player to make this camera sensation
        self.offset.x= player.rect.centerx - WINDOW_WIDTH/2
        self.offset.y= player.rect.centery - WINDOW_HEIGHT/2
        #blit the surface bg and sprite inside the groups
        #if the player is moving diagonally we want to make sure the backgroud goes opposite direction that way we have a camera
        self.display_surface.blit(self.background,-self.offset)
        #sprites inside of the group (player) which is to say the player animation
        #for overlap with need to sorted by the y position to put the element on top of each other
        for sprite in sorted(self.sprites(),key=lambda sprite:sprite.rect.centery):
            offset_rect = sprite.image.get_rect(center=sprite.rect.center)
            offset_rect.center -= self.offset
            self.display_surface.blit(sprite.image,offset_rect)
class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
        pygame.display.set_caption('Western shooter')
        self.clock = pygame.time.Clock()
        self.bullet_surf=pygame.image.load("Western\graphics\other\particle.png").convert_alpha()

        #groups
        self.all_sprites=AllSprites()
        self.obstacles = pygame.sprite.Group()
        self.bullets=pygame.sprite.Group()
        self.monsters=pygame.sprite.Group()

        self.setup()
        self.music=pygame.mixer.Sound('Western\sound\music.mp3')
        self.music.play(loops=-1)



    def create_bullet(self,pos,direction):
        Bullet(pos,direction,self.bullet_surf,[self.all_sprites,self.bullets])

    def bullet_collision(self):
        #bullet obstacle collision
        for obstacle in self.obstacles.sprites():
            pygame.sprite.spritecollide(obstacle,self.bullets,True,pygame.sprite.collide_mask)
        #bullet monster collision
        for bullet in self.bullets.sprites():
            sprites=pygame.sprite.spritecollide(bullet,self.monsters,False,pygame.sprite.collide_mask)
            if sprites:
                bullet.kill()
                for sprite in sprites:
                    sprite.damage()
                    
        #player collision: 1 damage the player 2 destroy the player
        if pygame.sprite.spritecollide(self.player,self.bullets,True,pygame.sprite.collide_mask):
            self.player.damage()


    def setup(self):
        tmx_map=load_pygame('Western\data\map.tmx')
        #Tile
        #return a list we can iterate over and you are getting the position with the image
        for x,y,surf in tmx_map.get_layer_by_name("Fence").tiles():
            Sprite((x*64,y*64),surf,[self.all_sprites,self.obstacles])
        #object
        for obj in tmx_map.get_layer_by_name('Object'):
            #we can create a sprite
            Sprite((obj.x,obj.y),obj.image,[self.all_sprites,self.obstacles])
            #place and create the player at the specific position
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name=='Player':
                self.player=Player(
                    pos=(obj.x,obj.y), 
                    groups=self.all_sprites,
                    path=PATHS['player'],
                    collision_sprite=self.obstacles,
                    create_bullet=self.create_bullet)
            if obj.name=='Coffin':
                self.coffin=Coffin(
                    pos=(obj.x,obj.y), 
                    groups=[self.all_sprites,self.monsters],
                    path=PATHS['coffin'],
                    collision_sprite=self.obstacles,
                    player=self.player)

            if obj.name=='Cactus':
                self.cactus=Cactus(
                    pos=(obj.x,obj.y), 
                    groups=[self.all_sprites,self.monsters],
                    path=PATHS['cactus'],
                    collision_sprite=self.obstacles,
                    player=self.player,
                    create_bullet=self.create_bullet)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type ==pygame.KEYDOWN:
                    if event.key ==pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            dt = self.clock.tick()/1000
            pygame.display.update()

            #update groups
            self.all_sprites.update(dt)
            self.bullet_collision()
            #draw groups
            self.display_surface.fill('black')
            self.all_sprites.customize_draw(self.player)


if __name__=='__main__':
    game=Game()
    game.run()    