import pygame
import random
import time

pygame.init()
pygame.mixer.init()

info_ecran = pygame.display.Info()
largeur, hauteur = info_ecran.current_w, info_ecran.current_h
ecran = pygame.display.set_mode((largeur, hauteur), pygame.FULLSCREEN)
pygame.display.set_caption("Le Mega Casino de Bikini Bottom")

JAUNE_BOB = (255, 235, 59)
VERT_PLANKTON = (76, 175, 80)
BLEU_OCEAN = (3, 169, 244)
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE_SANG = (200, 0, 0)

def charger_polices():
    try:
        return (pygame.font.Font("font/Spongebob.ttf", 50),
                pygame.font.Font("font/Spongebob.ttf", 28),
                pygame.font.Font("font/Spongebob.ttf", 100))
    except FileNotFoundError:
        return (pygame.font.SysFont("comicsansms", 40, bold=True),
                pygame.font.SysFont("comicsansms", 22),
                pygame.font.SysFont("comicsansms", 80, bold=True))

police_titre, police_texte, police_screamer = charger_polices()

def charger_images():
    try:
        fond_menu = pygame.transform.scale(pygame.image.load("sprites/wallpaper.jpeg"), (largeur, hauteur))
    except FileNotFoundError:
        fond_menu = None
    try:
        fond_jeu = pygame.transform.scale(pygame.image.load("sprites/wallpaper_game.jpg"), (largeur, hauteur))
    except FileNotFoundError:
        fond_jeu = None
    try:
        sprites = pygame.image.load("sprites/sprites_blackjack.png")
    except FileNotFoundError:
        sprites = None
    try:
        img_bob = pygame.transform.scale(pygame.image.load("sprites/bob_eponge.png"), (180, 225))
        img_croupier = pygame.transform.scale(pygame.image.load("sprites/carlo.png"), (150, 270))
    except FileNotFoundError:
        img_bob = None
        img_croupier = None

    return fond_menu, fond_jeu, sprites, img_bob, img_croupier

fond_menu, fond_jeu, sprite_sheet_cartes, sprite_bob, sprite_croupier = charger_images()

def jouer_son(chemin):
    try:
        son = pygame.mixer.Sound(chemin).play()
        son.set_volume(0.3)
        son.play
    except FileNotFoundError:
        pass

valeurs_cartes = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
couleurs_cartes = ['Coeur', 'Carreau', 'Trefle', 'Pique']

def creer_deck():
    deck = [{'valeur': v, 'couleur': c} for v in valeurs_cartes for c in couleurs_cartes]
    random.shuffle(deck)
    return deck

def calculer_score(main):
    score = 0
    as_count = 0
    for carte in main:
        if carte['valeur'] in ['J', 'Q', 'K']:
            score += 10
        elif carte['valeur'] == 'A':
            as_count += 1
            score += 11
        else:
            score += int(carte['valeur'])
    while score > 21 and as_count > 0:
        score -= 10
        as_count -= 1
    return score

def piocher(main, paquet):
    if paquet:
        main.append(paquet.pop())

def initialiser_manche(jeu_data):
    jeu_data['deck'] = creer_deck()
    jeu_data['main_joueur'] = []
    jeu_data['main_croupier'] = []
    jeu_data['blackjack_reveal_jusqu_a'] = 0
    jeu_data['blackjack_fin_action'] = None
    jeu_data['blackjack_message_final'] = ""
    jeu_data['blackjack_est_21'] = False
    piocher(jeu_data['main_joueur'], jeu_data['deck'])
    piocher(jeu_data['main_joueur'], jeu_data['deck'])
    piocher(jeu_data['main_croupier'], jeu_data['deck'])
    jeu_data['tour_blackjack'] += 1

def dessiner_de(surface, x, y, valeur):
    pygame.draw.rect(surface, BLANC, (x, y, 100, 100), border_radius=15)
    pygame.draw.rect(surface, NOIR, (x, y, 100, 100), 4, border_radius=15)
    centres = {
        1: [(x+50, y+50)],
        2: [(x+25, y+25), (x+75, y+75)],
        3: [(x+25, y+25), (x+50, y+50), (x+75, y+75)],
        4: [(x+25, y+25), (x+75, y+25), (x+25, y+75), (x+75, y+75)],
        5: [(x+25, y+25), (x+75, y+25), (x+50, y+50), (x+25, y+75), (x+75, y+75)],
        6: [(x+25, y+20), (x+75, y+20), (x+25, y+50), (x+75, y+50), (x+25, y+80), (x+75, y+80)]
    }
    if valeur in centres:
        for cx, cy in centres[valeur]:
            pygame.draw.circle(surface, NOIR, (cx, cy), 10)

def gerer_event_menu(event, jeu_data):
    if event.type == pygame.KEYDOWN:
        if event.key in [pygame.K_RETURN, pygame.K_1]:
            jouer_son("sounds/applepay.mp3")
            jeu_data['jeu_actuel'] = "BLACKJACK"
            jeu_data['victoires'] = 0
            jeu_data['tour_blackjack'] = 0
            initialiser_manche(jeu_data)
            jeu_data['etat'] = "JEU"
        elif event.key == pygame.K_2:
            jouer_son("sounds/applepay.mp3")
            jeu_data['jeu_actuel'] = "421"
            jeu_data['victoires_421'] = 0
            jeu_data['tour_421'] = 0
            initialiser_manche_421(jeu_data)
            jeu_data['etat'] = "JEU_421"
        elif event.key == pygame.K_3:
            jouer_son("sounds/applepay.mp3")
            initialiser_qcm(jeu_data)
            jeu_data['etat'] = "QCM"
        elif event.key == pygame.K_h:
            jeu_data['etat_precedent'] = jeu_data['etat']
            jeu_data['etat'] = "HELP"

def dessiner_menu(ecran):
    titre = police_titre.render("CASINO BIKINI BOTTOM", True, JAUNE_BOB)
    choix_1 = police_texte.render("[1] Blackjack", True, BLANC)
    choix_2 = police_texte.render("[2] 421", True, BLANC)
    choix_3 = police_texte.render("[3] QCM", True, BLANC)
    collab = police_texte.render("Defi collab JAM : Crossover avec le groupe Casino Valorant", True, JAUNE_BOB)
    info = police_texte.render("[H] Aide", True, BLANC)
    pygame.draw.rect(ecran, NOIR, (largeur//2 - titre.get_width()//2 - 10, 40, titre.get_width() + 20, 70), border_radius=10)
    ecran.blit(titre, (largeur//2 - titre.get_width()//2, 50))

    y_choix = hauteur // 2
    pygame.draw.rect(ecran, NOIR, (largeur//2 - choix_1.get_width()//2 - 20, y_choix - 10, choix_1.get_width() + 40, 55), border_radius=10)
    ecran.blit(choix_1, (largeur//2 - choix_1.get_width()//2, y_choix))

    pygame.draw.rect(ecran, NOIR, (largeur//2 - choix_2.get_width()//2 - 20, y_choix + 70, choix_2.get_width() + 40, 55), border_radius=10)
    ecran.blit(choix_2, (largeur//2 - choix_2.get_width()//2, y_choix + 80))

    pygame.draw.rect(ecran, NOIR, (largeur//2 - choix_3.get_width()//2 - 20, y_choix + 140, choix_3.get_width() + 40, 55), border_radius=10)
    ecran.blit(choix_3, (largeur//2 - choix_3.get_width()//2, y_choix + 150))

    pygame.draw.rect(ecran, NOIR, (largeur//2 - collab.get_width()//2 - 10, y_choix + 220, collab.get_width() + 20, 40), border_radius=10)
    ecran.blit(collab, (largeur//2 - collab.get_width()//2, y_choix + 225))

    pygame.draw.rect(ecran, NOIR, (largeur//2 - info.get_width()//2 - 10, hauteur - 150, info.get_width() + 20, 40), border_radius=10)
    ecran.blit(info, (largeur//2 - info.get_width()//2, hauteur - 145))

def evaluer_combinaison_421(des):
    des_tries = sorted(des)
    des_desc = sorted(des, reverse=True)

    if des_tries == [1, 2, 4]:
        return (7,)
    if des_tries[0] == des_tries[1] == des_tries[2]:
        return (6, des_tries[0])
    if des_tries in ([1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6]):
        return (5, des_tries[2])
    if des_tries[0] == des_tries[1]:
        return (4, des_tries[0], des_tries[2])
    if des_tries[1] == des_tries[2]:
        return (4, des_tries[1], des_tries[0])
    return (3, des_desc[0], des_desc[1], des_desc[2])

def nom_combinaison_421(des):
    des_tries = sorted(des)
    if des_tries == [1, 2, 4]:
        return "421"
    if des_tries[0] == des_tries[1] == des_tries[2]:
        return f"Brelan de {des_tries[0]}"
    if des_tries in ([1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6]):
        return f"Suite {des_tries[0]}-{des_tries[1]}-{des_tries[2]}"
    if des_tries[0] == des_tries[1] or des_tries[1] == des_tries[2]:
        return "Paire"
    return f"{sorted(des, reverse=True)}"

def initialiser_manche_421(jeu_data):
    jeu_data['des_joueur'] = [1, 1, 1]
    jeu_data['des_croupier'] = [1, 1, 1]
    jeu_data['selection_des_421'] = [False, False, False]
    jeu_data['a_lance_421'] = False
    jeu_data['lancers_restants_421'] = 3
    jeu_data['lancer_compte_421'] = 0
    jeu_data['anim_fin_421'] = 0
    jeu_data['anim_cible_421'] = None
    jeu_data['croupier_sequence_en_cours_421'] = False
    jeu_data['croupier_lancers_total_421'] = 0
    jeu_data['croupier_lancers_effectues_421'] = 0
    jeu_data['croupier_prochain_lancer_421'] = 0
    jeu_data['tour_termine_421'] = False
    jeu_data['resultat_421'] = "Lance une premiere fois avec ESPACE, puis clique les des a relancer."
    jeu_data['tour_421'] += 1

def decalage_saut_de_421(jeu_data, cible, index):
    if jeu_data.get('anim_cible_421') != cible:
        return 0

    maintenant = pygame.time.get_ticks()
    fin = jeu_data.get('anim_fin_421', 0)
    if maintenant >= fin:
        return 0

    duree = max(1, jeu_data.get('anim_duree_421', 450))
    progression = 1 - ((fin - maintenant) / duree)
    phase = (progression * 4 + index * 0.18) % 1.0

    if phase < 0.5:
        return int(-22 * (phase / 0.5))
    return int(-22 * ((1 - phase) / 0.5))

def rects_des_421(x_depart, y_depart):
    return [pygame.Rect(x_depart + i * 120, y_depart, 100, 100) for i in range(3)]

def relancer_des_selectionnes_421(jeu_data):
    selection = jeu_data.get('selection_des_421', [False, False, False])
    if not any(selection):
        return False

    for i, selectionne in enumerate(selection):
        if selectionne:
            jeu_data['des_joueur'][i] = random.randint(1, 6)

    jeu_data['anim_cible_421'] = 'joueur'
    jeu_data['anim_fin_421'] = pygame.time.get_ticks() + jeu_data.get('anim_duree_421', 450)
    jeu_data['lancers_restants_421'] -= 1
    jeu_data['lancer_compte_421'] += 1
    jeu_data['selection_des_421'] = [False, False, False]
    jeu_data['a_lance_421'] = True
    return True

def avancer_lancers_croupier_421(jeu_data):
    if not jeu_data.get('croupier_sequence_en_cours_421'):
        return

    maintenant = pygame.time.get_ticks()
    if maintenant < jeu_data.get('croupier_prochain_lancer_421', 0):
        return

    jeu_data['des_croupier'] = [random.randint(1, 6) for _ in range(3)]
    jeu_data['anim_cible_421'] = 'croupier'
    jeu_data['anim_fin_421'] = maintenant + jeu_data.get('anim_duree_421', 450)
    jeu_data['croupier_lancers_effectues_421'] += 1
    total = jeu_data.get('croupier_lancers_total_421', 1)

    if jeu_data['croupier_lancers_effectues_421'] < total:
        jeu_data['resultat_421'] = f"Croupier lance {jeu_data['croupier_lancers_effectues_421']}/{total}..."
        jeu_data['croupier_prochain_lancer_421'] = maintenant + 700
        return

    score_joueur = evaluer_combinaison_421(jeu_data['des_joueur'])
    score_croupier = evaluer_combinaison_421(jeu_data['des_croupier'])
    jeu_data['tour_termine_421'] = True
    jeu_data['croupier_sequence_en_cours_421'] = False

    if score_joueur > score_croupier:
        jouer_son("sounds/gary_meow.mp3")
        jeu_data['victoires_421'] += 1
        jeu_data['resultat_421'] = f"Tu gagnes la manche ! (Croupier: {total} lancer(s)) [J] pour continuer."
        if jeu_data['victoires_421'] >= 5:
            jeu_data['etat'] = "VICTOIRE"
    elif score_joueur < score_croupier:
        jouer_son("sounds/spongebob-fail.mp3")
        jeu_data['resultat_421'] = f"Le croupier gagne la manche... ({total} lancer(s)) [J] pour rejouer."
    else:
        jeu_data['resultat_421'] = f"Egalite ! (Croupier: {total} lancer(s)) [J] pour une nouvelle manche."

def gerer_event_jeu_421(event, jeu_data):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_h:
            jeu_data['etat_precedent'] = jeu_data['etat']
            jeu_data['etat'] = "HELP"

        elif event.key == pygame.K_SPACE and not jeu_data['tour_termine_421'] and not jeu_data['croupier_sequence_en_cours_421']:
            if jeu_data['lancers_restants_421'] <= 0:
                jeu_data['resultat_421'] = "Plus de lancers disponibles. Appuie sur ENTREE pour valider."
                return
            jouer_son("sounds/applepay.mp3")
            if not jeu_data['a_lance_421']:
                jeu_data['des_joueur'] = [random.randint(1, 6) for _ in range(3)]
                jeu_data['anim_cible_421'] = 'joueur'
                jeu_data['anim_fin_421'] = pygame.time.get_ticks() + jeu_data.get('anim_duree_421', 450)
                jeu_data['a_lance_421'] = True
                jeu_data['lancers_restants_421'] -= 1
                jeu_data['lancer_compte_421'] = 1
                if jeu_data['lancers_restants_421'] > 0:
                    jeu_data['resultat_421'] = "Premier lancer effectue. Clique les des a relancer."
                else:
                    jeu_data['resultat_421'] = "3/3 lancers utilises. Appuie sur ENTREE pour valider la manche."
            else:
                if relancer_des_selectionnes_421(jeu_data):
                    if jeu_data['lancers_restants_421'] > 0:
                        jeu_data['resultat_421'] = f"Lancer {jeu_data['lancer_compte_421']}/3 effectue. Clique a nouveau tes des."
                    else:
                        jeu_data['resultat_421'] = "3/3 lancers utilises. Appuie sur ENTREE pour valider la manche."
                else:
                    jeu_data['resultat_421'] = "Clique au moins un de avant de relancer."

        elif event.key == pygame.K_RETURN and jeu_data['a_lance_421'] and not jeu_data['tour_termine_421'] and not jeu_data['croupier_sequence_en_cours_421']:
            lancers_joueur = jeu_data.get('lancer_compte_421', 1)
            jeu_data['selection_des_421'] = [False, False, False]
            jeu_data['croupier_lancers_total_421'] = lancers_joueur
            jeu_data['croupier_lancers_effectues_421'] = 0
            jeu_data['croupier_sequence_en_cours_421'] = True
            jeu_data['croupier_prochain_lancer_421'] = pygame.time.get_ticks()
            jeu_data['resultat_421'] = f"Le croupier lance ses des ({lancers_joueur} lancer(s))..."

        elif event.key == pygame.K_j and jeu_data['tour_termine_421'] and jeu_data['etat'] == "JEU_421":
            initialiser_manche_421(jeu_data)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and jeu_data['etat'] == "JEU_421" and jeu_data['a_lance_421'] and not jeu_data['tour_termine_421'] and not jeu_data['croupier_sequence_en_cours_421']:
        if jeu_data.get('lancer_compte_421', 0) >= 1:
            x_depart = largeur // 2 - 150
            y_depart = hauteur // 2 + 90
            for i, rect in enumerate(rects_des_421(x_depart, y_depart)):
                if rect.collidepoint(event.pos) and jeu_data['lancers_restants_421'] > 0:
                    jeu_data['selection_des_421'][i] = not jeu_data['selection_des_421'][i]

def dessiner_jeu_421(ecran, jeu_data):
    titre = police_titre.render(f"421 - Tour {jeu_data['tour_421']} | Victoires : {jeu_data['victoires_421']}/5", True, BLANC)
    pygame.draw.rect(ecran, NOIR, (15, 15, titre.get_width() + 10, titre.get_height() + 5), border_radius=5)
    ecran.blit(titre, (20, 20))

    txt_lancers = police_texte.render(f"Lancers restants : {jeu_data['lancers_restants_421']}/3", True, JAUNE_BOB)
    pygame.draw.rect(ecran, NOIR, (20, 85, txt_lancers.get_width() + 10, txt_lancers.get_height() + 5), border_radius=5)
    ecran.blit(txt_lancers, (25, 88))

    txt_joueur = police_texte.render("Tes des", True, BLANC)
    txt_croupier = police_texte.render("Des du croupier", True, BLANC)
    ecran.blit(txt_joueur, (largeur // 2 - 300, hauteur // 2 + 40))
    ecran.blit(txt_croupier, (largeur // 2 - 300, hauteur // 2 - 220))

    x_depart = largeur // 2 - 150
    for i, de_valeur in enumerate(jeu_data['des_joueur']):
        y_joueur = hauteur // 2 + 90 + decalage_saut_de_421(jeu_data, 'joueur', i)
        if jeu_data.get('selection_des_421', [False, False, False])[i]:
            pygame.draw.rect(ecran, (255, 215, 0), (x_depart + i * 120 - 4, y_joueur - 4, 108, 108), border_radius=16)
        dessiner_de(ecran, x_depart + i * 120, y_joueur, de_valeur)

    if jeu_data['tour_termine_421'] or jeu_data.get('croupier_sequence_en_cours_421') or jeu_data.get('croupier_lancers_effectues_421', 0) > 0:
        for i, de_valeur in enumerate(jeu_data['des_croupier']):
            y_croupier = hauteur // 2 - 170 + decalage_saut_de_421(jeu_data, 'croupier', i)
            dessiner_de(ecran, x_depart + i * 120, y_croupier, de_valeur)
    else:
        for i in range(3):
            pygame.draw.rect(ecran, BLANC, (x_depart + i * 120, hauteur // 2 - 170, 100, 100), border_radius=15)
            pygame.draw.rect(ecran, NOIR, (x_depart + i * 120, hauteur // 2 - 170, 100, 100), 4, border_radius=15)
            cache = police_texte.render("?", True, NOIR)
            ecran.blit(cache, (x_depart + i * 120 + 40, hauteur // 2 - 150))

    if jeu_data['a_lance_421']:
        combo_joueur = police_texte.render(f"Ta combinaison : {nom_combinaison_421(jeu_data['des_joueur'])}", True, JAUNE_BOB)
        ecran.blit(combo_joueur, (largeur // 2 - combo_joueur.get_width() // 2, hauteur // 2 + 220))
    if jeu_data['tour_termine_421']:
        combo_croupier = police_texte.render(f"Combinaison croupier : {nom_combinaison_421(jeu_data['des_croupier'])}", True, JAUNE_BOB)
        ecran.blit(combo_croupier, (largeur // 2 - combo_croupier.get_width() // 2, hauteur // 2 - 240))
    elif jeu_data.get('croupier_sequence_en_cours_421'):
        progression = police_texte.render(
            f"Lancers croupier : {jeu_data.get('croupier_lancers_effectues_421', 0)}/{jeu_data.get('croupier_lancers_total_421', 0)}",
            True,
            JAUNE_BOB,
        )
        ecran.blit(progression, (largeur // 2 - progression.get_width() // 2, hauteur // 2 - 240))

    resultat = police_texte.render(jeu_data['resultat_421'], True, BLANC)
    pygame.draw.rect(ecran, NOIR, (largeur // 2 - resultat.get_width() // 2 - 10, hauteur - 120, resultat.get_width() + 20, resultat.get_height() + 10), border_radius=5)
    ecran.blit(resultat, (largeur // 2 - resultat.get_width() // 2, hauteur - 115))

    consigne = police_texte.render("[ESPACE] Lancer / Relancer  [CLIC] Choisir les des  [ENTREE] Valider  [J] Manche suivante  [H] Aide", True, JAUNE_BOB)
    pygame.draw.rect(ecran, NOIR, (largeur//2 - consigne.get_width()//2 - 10, hauteur - 50, consigne.get_width() + 20, consigne.get_height() + 10), border_radius=5)
    ecran.blit(consigne, (largeur//2 - consigne.get_width()//2, hauteur - 45))

def gerer_event_jeu(event, jeu_data):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_h:
            jeu_data['etat_precedent'] = jeu_data['etat']
            jeu_data['etat'] = "HELP"

        elif event.key == pygame.K_SPACE:
            piocher(jeu_data['main_joueur'], jeu_data['deck'])
            if calculer_score(jeu_data['main_joueur']) > 21:
                jouer_son("sounds/spongebob-fail.mp3")
                initialiser_manche(jeu_data)
                
        elif event.key == pygame.K_RETURN:
            while calculer_score(jeu_data['main_croupier']) < 17:
                piocher(jeu_data['main_croupier'], jeu_data['deck'])
            sj = calculer_score(jeu_data['main_joueur'])
            sc = calculer_score(jeu_data['main_croupier'])

            jeu_data['blackjack_reveal_jusqu_a'] = pygame.time.get_ticks() + 4000

            if sc > 21 or sj > sc:
                jeu_data['victoires'] += 1
                jeu_data['blackjack_est_21'] = (sj == 21)
                if sj == 21:
                    jeu_data['blackjack_message_final'] = "Tu bats le croupier avec un 21 !"
                else:
                    jeu_data['blackjack_message_final'] = "Tu gagnes la manche !"

                if jeu_data['victoires'] >= 5:
                    jeu_data['blackjack_fin_action'] = "VICTOIRE"
                else:
                    jeu_data['blackjack_fin_action'] = "NOUVELLE_MANCHE"
            else:
                jeu_data['blackjack_message_final'] = "Le croupier gagne la manche."
                jeu_data['blackjack_est_21'] = False
                jeu_data['blackjack_fin_action'] = "NOUVELLE_MANCHE"

            jeu_data['etat'] = "BLACKJACK_REVEAL"
                
        elif event.key == pygame.K_j:
            jouer_son("sounds/applepay.mp3")
            initialiser_manche(jeu_data)

def dessiner_jeu(ecran, jeu_data):
    titre = police_titre.render(f"Blackjack - Tour {jeu_data['tour_blackjack']} | Victoires : {jeu_data['victoires']}/5", True, BLANC)
    pygame.draw.rect(ecran, NOIR, (15, 15, titre.get_width() + 10, titre.get_height() + 5), border_radius=5)
    ecran.blit(titre, (20, 20))
    
    score_croupier = calculer_score(jeu_data['main_croupier']) if jeu_data['etat'] == "BLACKJACK_REVEAL" else "?"
    txt_croupier = police_texte.render(f"Croupier Carlo (Score: {score_croupier})", True, BLANC)
    txt_joueur = police_texte.render(f"Toi (Score: {calculer_score(jeu_data['main_joueur'])})", True, BLANC)
    
    pygame.draw.rect(ecran, NOIR, (largeur//2 - txt_croupier.get_width()//2 - 5, 145, txt_croupier.get_width() + 10, txt_croupier.get_height() + 5), border_radius=5)
    ecran.blit(txt_croupier, (largeur//2 - txt_croupier.get_width()//2, 150))
    
    y_texte_joueur = hauteur - 300
    pygame.draw.rect(ecran, NOIR, (largeur//2 - txt_joueur.get_width()//2 - 5, y_texte_joueur - 5, txt_joueur.get_width() + 10, txt_joueur.get_height() + 5), border_radius=5)
    ecran.blit(txt_joueur, (largeur//2 - txt_joueur.get_width()//2, y_texte_joueur))

    espacement = 90
    largeur_totale_croupier = len(jeu_data['main_croupier']) * espacement
    debut_x_croupier = largeur // 2 - largeur_totale_croupier // 2

    if sprite_croupier:
        ecran.blit(sprite_croupier, (debut_x_croupier - 160, 160))
        
    afficher_croupier_complet = jeu_data['etat'] == "BLACKJACK_REVEAL"
    for i, carte in enumerate(jeu_data['main_croupier']):
        x_carte = debut_x_croupier + i * espacement
        if afficher_croupier_complet or i == 0:
            pygame.draw.rect(ecran, BLANC, (x_carte, 200, 80, 120), border_radius=5)
            pygame.draw.rect(ecran, NOIR, (x_carte, 200, 80, 120), 2, border_radius=5)
            txt_carte = police_texte.render(carte['valeur'], True, NOIR)
            ecran.blit(txt_carte, (x_carte + 10, 210))
        else:
            pygame.draw.rect(ecran, (70, 70, 110), (x_carte, 200, 80, 120), border_radius=5)
            pygame.draw.rect(ecran, NOIR, (x_carte, 200, 80, 120), 2, border_radius=5)
            cache = police_texte.render("?", True, BLANC)
            ecran.blit(cache, (x_carte + 28, 210))

    largeur_totale_joueur = len(jeu_data['main_joueur']) * espacement
    debut_x_joueur = largeur // 2 - largeur_totale_joueur // 2
    y_cartes_joueur = hauteur - 240
    
    if sprite_bob:
        ecran.blit(sprite_bob, (debut_x_joueur - 190, y_cartes_joueur - 40)) 

    for i, carte in enumerate(jeu_data['main_joueur']):
        x_carte = debut_x_joueur + i * espacement
        pygame.draw.rect(ecran, BLANC, (x_carte, y_cartes_joueur, 80, 120), border_radius=5)
        pygame.draw.rect(ecran, NOIR, (x_carte, y_cartes_joueur, 80, 120), 2, border_radius=5)
        txt_carte = police_texte.render(carte['valeur'], True, NOIR)
        ecran.blit(txt_carte, (x_carte + 10, y_cartes_joueur + 10))

    consigne = police_texte.render("[ESPACE] Tirer  [ENTREE] Rester  [J] Joker  [H] Aide", True, JAUNE_BOB)
    pygame.draw.rect(ecran, NOIR, (largeur//2 - consigne.get_width()//2 - 10, hauteur - 50, consigne.get_width() + 20, consigne.get_height() + 10), border_radius=5)
    ecran.blit(consigne, (largeur//2 - consigne.get_width()//2, hauteur - 45))

    if jeu_data['etat'] == "BLACKJACK_REVEAL":
        message = police_texte.render(jeu_data.get('blackjack_message_final', ''), True, JAUNE_BOB)
        pygame.draw.rect(ecran, NOIR, (largeur//2 - message.get_width()//2 - 12, 95, message.get_width() + 24, message.get_height() + 12), border_radius=8)
        ecran.blit(message, (largeur//2 - message.get_width()//2, 100))

def dessiner_help(ecran):
    ecran.fill(NOIR)
    titre = police_titre.render("REGLES DU CASINO", True, JAUNE_BOB)
    ecran.blit(titre, (largeur//2 - titre.get_width()//2, 50))
    
    regles = [
        "MENU : [1] Blackjack | [2] 421 | [3] QCM",
        "DEFI COLLAB : reference directe au groupe Casino Valorant.",
        "",
        "Objectif : Avoir un score plus proche de 21 que le croupier.",
        "Si tu depasses 21, tu perds. Gagne 5 fois pour remporter la partie !",
        "",
        "BLACKJACK - TOUCHES :",
        "[ESPACE] : Tirer une carte supplementaire",
        "[ENTREE] : Rester et laisser le croupier jouer",
        "[J] : Joker - Relancer entierement ta main (triche autorisee !)",
        "",
        "421 - TOUCHES :",
        "[ESPACE] : Lancer tes 3 des (max 3 fois par manche)",
        "[ENTREE] : Le croupier joue et la manche est comparee",
        "[J] : Rejouer une manche apres le resultat",
        "",
        "QCM - TOUCHES :",
        "[1] ou [2] : Repondre",
        "[J] : Recommencer le QCM une fois termine",
        "[H] : Quitter l'aide et reprendre la partie",
        "[ECHAP] : Quitter completement le jeu"
    ]
    
    for i, ligne in enumerate(regles):
        txt = police_texte.render(ligne, True, BLANC)
        ecran.blit(txt, (100, 180 + i * 40))

def gerer_event_help(event, jeu_data):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
        jeu_data['etat'] = jeu_data['etat_precedent']

def initialiser_qcm(jeu_data):
    jeu_data['qcm_questions'] = random.sample(jeu_data['qcm_banque'], len(jeu_data['qcm_banque']))
    jeu_data['qcm_index'] = 0
    jeu_data['qcm_score'] = 0
    jeu_data['qcm_termine'] = False

def gerer_event_qcm(event, jeu_data):
    if event.type == pygame.KEYDOWN:
        if jeu_data['qcm_termine']:
            if event.key == pygame.K_j:
                initialiser_qcm(jeu_data)
            return

        if event.key not in [pygame.K_1, pygame.K_2]:
            return

        question = jeu_data['qcm_questions'][jeu_data['qcm_index']]
        reponse_utilisateur = 0 if event.key == pygame.K_1 else 1
        if reponse_utilisateur == question['bonne']:
            jouer_son("sounds/gary_meow.mp3")
            jeu_data['qcm_score'] += 1
        else:
            jouer_son("sounds/spongebob-fail.mp3")

        jeu_data['qcm_index'] += 1
        if jeu_data['qcm_index'] >= len(jeu_data['qcm_questions']):
            jeu_data['qcm_termine'] = True

def dessiner_qcm(ecran, jeu_data):
    titre = police_titre.render("QCM SPECIAL JAM", True, JAUNE_BOB)
    pygame.draw.rect(ecran, NOIR, (largeur//2 - titre.get_width()//2 - 10, 90, titre.get_width() + 20, titre.get_height() + 10), border_radius=5)
    ecran.blit(titre, (largeur//2 - titre.get_width()//2, 100))

    progression = police_texte.render(
        f"Question {min(jeu_data['qcm_index'] + 1, len(jeu_data['qcm_questions']))}/{len(jeu_data['qcm_questions'])} | Score: {jeu_data['qcm_score']}",
        True,
        JAUNE_BOB,
    )
    pygame.draw.rect(ecran, NOIR, (largeur//2 - progression.get_width()//2 - 10, 180, progression.get_width() + 20, progression.get_height() + 10), border_radius=5)
    ecran.blit(progression, (largeur//2 - progression.get_width()//2, 185))

    if jeu_data['qcm_termine']:
        final = police_texte.render(
            f"QCM termine ! Score final: {jeu_data['qcm_score']}/{len(jeu_data['qcm_questions'])}  |  [J] Rejouer",
            True,
            BLANC,
        )
        pygame.draw.rect(ecran, NOIR, (largeur//2 - final.get_width()//2 - 10, 300, final.get_width() + 20, final.get_height() + 10), border_radius=5)
        ecran.blit(final, (largeur//2 - final.get_width()//2, 305))
        return

    question = jeu_data['qcm_questions'][jeu_data['qcm_index']]
    q_txt = police_texte.render(question["q"], True, BLANC)
    pygame.draw.rect(ecran, NOIR, (largeur//2 - q_txt.get_width()//2 - 10, 245, q_txt.get_width() + 20, q_txt.get_height() + 10), border_radius=5)
    ecran.blit(q_txt, (largeur//2 - q_txt.get_width()//2, 250))
    
    rep1 = police_texte.render(f"1: {question['reponses'][0]}", True, BLANC)
    rep2 = police_texte.render(f"2: {question['reponses'][1]}", True, BLANC)
    
    pygame.draw.rect(ecran, NOIR, (largeur//2 - rep1.get_width()//2 - 10, 345, rep1.get_width() + 20, rep1.get_height() + 10), border_radius=5)
    ecran.blit(rep1, (largeur//2 - rep1.get_width()//2, 350))
    
    pygame.draw.rect(ecran, NOIR, (largeur//2 - rep2.get_width()//2 - 10, 395, rep2.get_width() + 20, rep2.get_height() + 10), border_radius=5)
    ecran.blit(rep2, (largeur//2 - rep2.get_width()//2, 400))

    if "Valorant" in question["q"]:
        badge = police_texte.render("CROSSOVER : GROUPE CASINO VALORANT", True, JAUNE_BOB)
        pygame.draw.rect(ecran, NOIR, (largeur//2 - badge.get_width()//2 - 10, 165, badge.get_width() + 20, badge.get_height() + 10), border_radius=5)
        ecran.blit(badge, (largeur//2 - badge.get_width()//2, 170))

def dessiner_victoire(ecran):
    texte_gg = police_screamer.render("GG T'AS REUSSI !", True, JAUNE_BOB)
    info = police_texte.render("[ECHAP] pour quitter le Casino", True, BLANC)
    
    pygame.draw.rect(ecran, NOIR, (largeur//2 - texte_gg.get_width()//2 - 20, hauteur//2 - texte_gg.get_height()//2 - 10, texte_gg.get_width() + 40, texte_gg.get_height() + 20), border_radius=15)
    ecran.blit(texte_gg, (largeur//2 - texte_gg.get_width()//2, hauteur//2 - texte_gg.get_height()//2))
    
    pygame.draw.rect(ecran, NOIR, (largeur//2 - info.get_width()//2 - 10, hauteur//2 + 100, info.get_width() + 20, info.get_height() + 10), border_radius=5)
    ecran.blit(info, (largeur//2 - info.get_width()//2, hauteur//2 + 105))

def main():
    qcm_banque = [
        {"q": "Quel est le nom du restaurant de Plankton ?", "reponses": ["Le Seau de l'Enfer", "Le Crabe Croustillant"], "bonne": 0},
        {"q": "Quel instrument joue Carlo ?", "reponses": ["De la flute", "De la clarinette"], "bonne": 1},
        {"q": "Quelle est la couleur de l'etoile de mer Patrick ?", "reponses": ["Rose", "Rouge"], "bonne": 0},
        {"q": "Dans quel fruit habite Bob l'eponge ?", "reponses": ["Une Noix de Coco", "Un Ananas"], "bonne": 1},
        {"q": "Comment s'appelle l'escargot de compagnie de Bob ?", "reponses": ["Gary", "Larry"], "bonne": 0},
        {"q": "Quel animal est Sandy, l'amie texane de Bob ?", "reponses": ["Un Ecureuil", "Un Castor"], "bonne": 0},
        {"q": "Quel est le plus grand amour de M. Krabs ?", "reponses": ["Sa fille Pearl", "L'Argent"], "bonne": 1},
        {"q": "Que tente inlassablement de voler Plankton ?", "reponses": ["La recette du Pate de Crabe", "Le coffre-fort de Krabs"], "bonne": 0},
        {"q": "Qui est la professeure d'auto-ecole de Bob ?", "reponses": ["Mme Puff", "Mme Prout"], "bonne": 0},
        {"q": "Quel est le super-heros favori de Bob et Patrick ?", "reponses": ["L'Homme Poisson", "L'Homme Sirene"], "bonne": 1},
        {"q": "Dans Valorant, quel agent est une sentinelle ?", "reponses": ["Sage", "Jett"], "bonne": 0},
        {"q": "Dans Valorant, quelle equipe attaque en posant le Spike ?", "reponses": ["Les attaquants", "Les defenseurs"], "bonne": 0},
        {"q": "Dans Valorant, quel mode de tir est ideal pour etre precis ?", "reponses": ["Rafales courtes", "Spray continu"], "bonne": 0}
    ]
    jeu_data = {
        'etat': "MENU",
        'jeu_actuel': None,
        'etat_precedent': "MENU",
        'tour_blackjack': 0,
        'victoires': 0,
        'tour_421': 0,
        'victoires_421': 0,
        'des_joueur': [1, 1, 1],
        'des_croupier': [1, 1, 1],
        'a_lance_421': False,
        'selection_des_421': [False, False, False],
        'lancers_restants_421': 3,
        'lancer_compte_421': 0,
        'anim_duree_421': 450,
        'anim_fin_421': 0,
        'anim_cible_421': None,
        'croupier_sequence_en_cours_421': False,
        'croupier_lancers_total_421': 0,
        'croupier_lancers_effectues_421': 0,
        'croupier_prochain_lancer_421': 0,
        'tour_termine_421': False,
        'resultat_421': "",
        'qcm_banque': qcm_banque,
        'qcm_questions': [],
        'qcm_index': 0,
        'qcm_score': 0,
        'qcm_termine': False,
        'deck': [],
        'main_joueur': [],
        'main_croupier': [],
        'blackjack_reveal_jusqu_a': 0,
        'blackjack_fin_action': None,
        'blackjack_message_final': "",
        'blackjack_est_21': False,
        'en_cours': True
    }

    horloge = pygame.time.Clock()

    while jeu_data['en_cours']:
        if jeu_data['etat'] == "BLACKJACK_REVEAL" and pygame.time.get_ticks() >= jeu_data['blackjack_reveal_jusqu_a']:
            action = jeu_data.get('blackjack_fin_action')
            if action == "VICTOIRE":
                jouer_son("sounds/patrick_ihc.mp3")
                jeu_data['etat'] = "VICTOIRE"
            else:
                if jeu_data['blackjack_message_final'] == "Le croupier gagne la manche.":
                    jouer_son("sounds/spongebob-fail.mp3")
                elif jeu_data.get('blackjack_est_21'):
                    jouer_son("sounds/patrick_ihc.mp3")
                else:
                    jouer_son("sounds/gary_meow.mp3")
                initialiser_manche(jeu_data)
                jeu_data['etat'] = "JEU"

        if jeu_data['etat'] == "JEU_421":
            avancer_lancers_croupier_421(jeu_data)

        if jeu_data['etat'] != "HELP":
            if jeu_data['etat'] == "MENU":
                if fond_menu: ecran.blit(fond_menu, (0, 0))
                else: ecran.fill(BLEU_OCEAN)
            else:
                if fond_jeu: ecran.blit(fond_jeu, (0, 0))
                else: ecran.fill(BLEU_OCEAN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jeu_data['en_cours'] = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if jeu_data['etat'] == "MENU":
                    jeu_data['en_cours'] = False
                else:
                    jeu_data['etat'] = "MENU"
                    jeu_data['etat_precedent'] = "MENU"

            if jeu_data['etat'] == "MENU":
                gerer_event_menu(event, jeu_data)
            elif jeu_data['etat'] == "JEU":
                gerer_event_jeu(event, jeu_data)
            elif jeu_data['etat'] == "JEU_421":
                gerer_event_jeu_421(event, jeu_data)
            elif jeu_data['etat'] == "HELP":
                gerer_event_help(event, jeu_data)
            elif jeu_data['etat'] == "QCM":
                gerer_event_qcm(event, jeu_data)

        if jeu_data['etat'] == "MENU": dessiner_menu(ecran)
        elif jeu_data['etat'] == "JEU": dessiner_jeu(ecran, jeu_data)
        elif jeu_data['etat'] == "BLACKJACK_REVEAL": dessiner_jeu(ecran, jeu_data)
        elif jeu_data['etat'] == "JEU_421": dessiner_jeu_421(ecran, jeu_data)
        elif jeu_data['etat'] == "HELP": dessiner_help(ecran)
        elif jeu_data['etat'] == "QCM": dessiner_qcm(ecran, jeu_data)
        elif jeu_data['etat'] == "VICTOIRE": dessiner_victoire(ecran)

        pygame.display.flip()
        horloge.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()