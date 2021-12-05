import pygame, socket, pickle, os, random, math

buffer = 2048

class Network:
    def __init__(self):
        self.server = (self.ip, self.port) = ("localhost", 2911)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player = self.connect()

    def getPlayer(self):
        return self.player

    def connect(self):
        try:
            self.client.connect(self.server)
            return pickle.loads(self.client.recv(buffer))
        except: pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(buffer))
        except socket.error as errMsg:
            print(errMsg)


size = (width, height) = (1280, 960)

window = pygame.display.set_mode(size)
pygame.display.set_caption("Better Together")

ship = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'ocean_e_new_ship_small.png')).convert(), (width//2, height)) #(825, 750)
water = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'water.png')).convert(), (width//4, height))
aim = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'aim.png')).convert_alpha(), (80, 80))

def refresh(window, playerMe, playerOthers):
    window.blit(water, (0, 0), (0, 0, width, height))
    window.blit(water, (width-width//4, 0), (0, 0, width, height))
    window.blit(ship, (width//4, 0),(0, 0, width, height))
    #hit
    for damage in hit:
        window.blit(water, damage, (0, 0, 15, 15)) #x 440~880 #y 410~820
    for p in playerOthers:
        p.draw(window)

    playerMe.draw(window)

    #font = pygame.font.SysFont(None, 64)

    window.blit(pygame.image.load(os.path.join('Images', 'wood plank.png')).convert_alpha(), (10,20))
    window.blit(pygame.image.load(os.path.join('Images', 'cannonball.png')).convert_alpha(), (10,70))

    window.blit(font.render("{}".format(playerMe.inventoryWood), True, (0,0,0)), (60, 20))
    window.blit(font.render("{}".format(playerMe.inventoryCannon), True, (0,0,0)), (60, 70))

    #pygame.display.update()


if __name__ =="__main__":
    game = True
    server = Network()
    playerMe = server.getPlayer()
    framerate = pygame.time.Clock()
    infoCount = 0
    gameOverCount = 0
    aimX = 300
    aimY = 320
    aimVelocity = 4
    cannonShoot = 60*2+1
    enemyShoots = random.randrange(3,5)
    missChance = random.randrange(-300,301)
    enemyCannonShoot = 0
    inventoryCannonWait = 0
    inventoryWoodWait = 0
    enemyShotCooldown = 0
    cannonCooldown=60*3
    repairCooldown=60*3
    shootAnimation=False
    gameOver = False
    font = pygame.font.SysFont(None, 64)
    hit = []

    while game:
        shootInfoDisplayed = False
        repairInfoDisplayed = False
        framerate.tick(60)

            #for i in range(60*500):
                #window.blit(font.render("Game Over", True, (255,255,255)), (width//2-50, height//2))
                #refresh(window, playerMe, playerOthers)
            #game = False
            #break

        # refill inventory
        if playerMe.inventoryCannon <= 0:
            inventoryCannonWait += 1
            if inventoryCannonWait >= 60*10: # 1 minute
                playerMe.inventoryCannon = 9
                inventoryCannonWait = 0
        if playerMe.inventoryWood <= 0:
            inventoryWoodWait += 1
            if inventoryWoodWait >= 60*10: # 1 minute
                playerMe.inventoryWood = 9
                inventoryWoodWait = 0

        playerOthers = server.send(playerMe)

        refresh(window, playerMe, playerOthers)
        #gameOver = True
        if len(hit)>=30:
            gameOver = True

        if gameOver:
            gameOverFont = pygame.font.SysFont(None, 256)
            window.blit(gameOverFont.render("Game Over", True, (255,0,0)), (width//8, height//2))
            gameOverCount += 1
            if gameOverCount > 60*10: # 5 seconds
                game = False

        # enemy shoot
        enemyShotCooldown += 1
        if enemyShotCooldown >= 60*6: # 1 minute
            if enemyCannonShoot <= 60*1:
                enemyCannonShoot += 1
                enemyAimX=playerOthers[enemyShoots].x+playerOthers[enemyShoots].width//4-(playerOthers[enemyShoots].x+playerOthers[enemyShoots].width//4-playerMe.x+missChance)*enemyCannonShoot/60
                enemyAimY=playerOthers[enemyShoots].y+playerOthers[enemyShoots].height//4-(playerOthers[enemyShoots].y+playerOthers[enemyShoots].height//4-playerMe.y+missChance)*enemyCannonShoot/60
                window.blit(pygame.image.load(os.path.join('Images', 'cannonball.png')).convert_alpha(), (enemyAimX, enemyAimY))#(playerMe.x-60-(playerMe.x-aimX+20)*enemyCannonShoot/60, playerMe.y+20-(playerMe.y-aimY+20)*enemyCannonShoot/60))
            else:
                enemyShotCooldown = 0
                #if playerMe.x+missChance in range(440,880) and playerMe.y+missChance in range(410,820):
                if math.floor(enemyAimY) < 820:
                    hit.append((math.floor(enemyAimX), math.floor(enemyAimY)));
                enemyCannonShoot = 0
                enemyShoots = random.randrange(3,5)
                missChance = random.randrange(-300,301)
        if not gameOver:
            # repair interaction
            for damage in hit:
                if damage[0]+15//2 in range(playerMe.x-playerMe.width//3, playerMe.x+playerMe.width+playerMe.width//3) and damage[1]+15//2 in range(playerMe.y-playerMe.width//3, playerMe.y+playerMe.height+playerMe.width//3):
                    if playerMe.inventoryWood > 0:

                        window.blit(font.render(f"Hold SPACE for {int(repairCooldown/6)/10} seconds to repair", True, (255,255,255)), (width//4-50, height-height//12))
                        repairInfoDisplayed = True
                        keys = pygame.key.get_pressed()
                        if repairCooldown>0:
                            if keys[pygame.K_SPACE]:
                                repairCooldown-=1;
                        else:
                            playerMe.inventoryWood -= 1
                            hit.remove(damage)
                            repairCooldown=60*3
                    else:
                        if not shootInfoDisplayed and not repairInfoDisplayed:
                            window.blit(font.render("No Wood", True, (255,255,255)), (width//2-50, height-height//12))

            # cannon interaction
            if 420 <= playerMe.y <= 740 and (470 <= playerMe.x <= 550 or 760 <= playerMe.x <= 840):
                keys = pygame.key.get_pressed()
                if playerMe.inventoryCannon > 0 and cannonCooldown<=0 and not repairInfoDisplayed:
                    shootInfoDisplayed = True
                    if keys[pygame.K_SPACE]:
                        if cannonShoot<=0:
                            window.blit(font.render("Release SPACE to shoot", True, (255,255,255)), (width//3-50, height-height//12))
                        else:
                            window.blit(font.render("Release SPACE to cancel", True, (255,255,255)), (width//3-50, height-height//12))
                        if (keys[ord('w')] or keys[pygame.K_UP]) and aimY - aimVelocity > 0:
                            aimY -= aimVelocity
                            cannonShoot = 0

                        if (keys[ord('a')] or keys[pygame.K_LEFT]) and aimX - aimVelocity > 0:
                            aimX -= aimVelocity
                            cannonShoot = 0

                        if (keys[ord('s')] or keys[pygame.K_DOWN]) and aimY + aimVelocity < height:
                            aimY += aimVelocity
                            cannonShoot = 0

                        if (keys[ord('d')] or keys[pygame.K_RIGHT]) and aimX + aimVelocity < width:
                            aimX += aimVelocity
                            cannonShoot = 0

                        window.blit(aim, (aimX, aimY),(0, 0, width, height))
                    else:
                        shootAnimation=True
                        if not cannonShoot:
                            playerMe.inventoryCannon -= 1
                            cannonCooldown=60*3 # 10 seconds

                        if cannonShoot > 60*1:
                            #reset aim
                            aimY = playerMe.y-playerMe.height
                            if 470 <= playerMe.x <= 550:
                                aimX = playerMe.x-6*playerMe.width
                            if 760 <= playerMe.x <= 840:
                                aimX = playerMe.x+6*playerMe.width
                        if not repairInfoDisplayed:
                            window.blit(font.render("Hold SPACE to use Cannon", True, (255,255,255)), (width//3-50, height-height//12))
                        playerMe.move()
                else:
                    if cannonCooldown>0 and playerMe.inventoryCannon > 0:
                        if not repairInfoDisplayed:
                            window.blit(font.render(f"Hold SPACE for {int(cannonCooldown/6)/10} seconds to reload", True, (255,255,255)), (width//4-50, height-height//12))
                        if keys[pygame.K_SPACE]:
                            cannonCooldown-=1;
                    elif not repairInfoDisplayed:
                        window.blit(font.render("No Ammo", True, (255,255,255)), (width//2-50, height-height//12))
                    playerMe.move()
            else:
                playerMe.move()
                # move info
                if infoCount < 60*5: # 5 seconds
                    infoCount += 1
                    #font = pygame.font.SysFont(None, 64)
                    if not shootInfoDisplayed and not repairInfoDisplayed:
                        window.blit(font.render("Use WASD or Arrow Keys to MOVE", True, (255,255,255)), (width//4-50, height-height//12))
            if shootAnimation:
                if cannonShoot <= 60*1: # 3 seconds
                    cannonShoot += 1

                    window.blit(pygame.image.load(os.path.join('Images', 'cannonball.png')).convert_alpha(), (playerMe.x-60-(playerMe.x-aimX+20)*cannonShoot/60, playerMe.y+20-(playerMe.y-aimY+20)*cannonShoot/60))
                else:
                    shootAnimation=False
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
                pygame.quit()
