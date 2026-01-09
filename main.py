import flet as ft
import sqlite3
import time
import os
import unicodedata
from datetime import datetime, timedelta

# ==============================================================================
# 1. CONFIGURAÇÃO (GAME DESIGN & LORE)
# ==============================================================================

THEME = {
    "bg": "#121212",
    "bg_overlay": "#D9000000", 
    "card_bg": "#E61e1e1e",
    "primary": "#8a0303",
    "accent": "#FFD700",
    "text": "#E0E0E0",
    "font": "VT323"
}

# --- CHEFES ---
BOSS_LADDER = [
    {"lvl": 1, "name": "Slime de Whey", "hp": 2000, "img": "boss_slime.png", "desc": "Uma poça gelatinosa de proteína mal misturada."},
    {"lvl": 2, "name": "Goblin Frango", "hp": 5000, "img": "boss_goblin.png", "desc": "Ele pula o treino de perna, mas é rápido."},
    {"lvl": 3, "name": "Orc da Maromba", "hp": 15000, "img": "boss_orc.png", "desc": "Grita muito alto a cada repetição."},
    {"lvl": 4, "name": "Golem de Anilha", "hp": 50000, "img": "boss_golem.png", "desc": "Feito de ferro puro. Dureza extrema."},
    {"lvl": 5, "name": "Dragão Catabólico", "hp": 150000, "img": "boss_dragon.png", "desc": "O devorador de massa muscular."},
]

CLASSES_RPG = {
    "Berserker": {"titulo": "Berserker", "subtitulo": "Força Bruta", "icon": "fitness_center", "lore": "Focado em carga máxima.", "estilo": "Bônus: Upper ++ | Lower ++", "learning_rate": {"upper": 1.3, "lower": 1.3, "stamina": 0.7, "focus": 1.0}},
    "Valkyria": {"titulo": "Valkyria", "subtitulo": "Membros Inferiores", "icon": "accessibility_new", "lore": "Pernas de aço.", "estilo": "Bônus: Lower +++ | Cardio +", "learning_rate": {"upper": 1.0, "lower": 1.6, "stamina": 1.1, "focus": 1.0}},
    "Cavaleiro": {"titulo": "Cavaleiro", "subtitulo": "Bodybuilder", "icon": "shield", "lore": "Estética e simetria.", "estilo": "Bônus: Equilibrado", "learning_rate": {"upper": 1.2, "lower": 1.2, "stamina": 1.0, "focus": 1.0}},
    "Assassino": {"titulo": "Assassino", "subtitulo": "Funcional", "icon": "bolt", "lore": "Resistência infinita.", "estilo": "Bônus: Stamina +++", "learning_rate": {"upper": 0.9, "lower": 1.1, "stamina": 1.5, "focus": 1.1}},
    "Clérigo": {"titulo": "Clérigo", "subtitulo": "Upper Focus", "icon": "health_and_safety", "lore": "Tronco impenetrável.", "estilo": "Bônus: Upper +++", "learning_rate": {"upper": 1.6, "lower": 0.9, "stamina": 1.0, "focus": 1.1}},
    "Monge": {"titulo": "Monge", "subtitulo": "Mobilidade", "icon": "self_improvement", "lore": "Controle corporal.", "estilo": "Bônus: Focus +++", "learning_rate": {"upper": 0.8, "lower": 0.8, "stamina": 1.0, "focus": 1.6}}
}

# --- LISTA COMPLETA DE EXERCÍCIOS ---
DEFAULT_EXERCISES = [
    # PEITO
    {"name": "Supino Reto (Barra)", "target": "upper", "category": "Peito", "icon": "fitness_center"},
    {"name": "Supino Reto (Halter)", "target": "upper", "category": "Peito", "icon": "fitness_center"},
    {"name": "Supino Inclinado (Barra)", "target": "upper", "category": "Peito", "icon": "fitness_center"},
    {"name": "Supino Inclinado (Halter)", "target": "upper", "category": "Peito", "icon": "fitness_center"},
    {"name": "Supino Declinado", "target": "upper", "category": "Peito", "icon": "fitness_center"},
    {"name": "Crucifixo (Halter)", "target": "upper", "category": "Peito", "icon": "accessibility"},
    {"name": "Crucifixo (Máquina)", "target": "upper", "category": "Peito", "icon": "accessibility"},
    {"name": "Peck Deck (Voador)", "target": "upper", "category": "Peito", "icon": "accessibility"},
    {"name": "Crossover (Polia Alta)", "target": "upper", "category": "Peito", "icon": "accessibility"},
    {"name": "Crossover (Polia Baixa)", "target": "upper", "category": "Peito", "icon": "accessibility"},
    {"name": "Flexão de Braço", "target": "upper", "category": "Peito", "icon": "accessibility"},
    
    # COSTAS
    {"name": "Puxada Frontal", "target": "upper", "category": "Costas", "icon": "arrow_downward"},
    {"name": "Puxada Triângulo", "target": "upper", "category": "Costas", "icon": "arrow_downward"},
    {"name": "Puxada Atrás", "target": "upper", "category": "Costas", "icon": "arrow_downward"},
    {"name": "Remada Curvada (Barra)", "target": "upper", "category": "Costas", "icon": "rowing"},
    {"name": "Remada Baixa (Triângulo)", "target": "upper", "category": "Costas", "icon": "rowing"},
    {"name": "Remada Cavalinho", "target": "upper", "category": "Costas", "icon": "rowing"},
    {"name": "Remada Unilateral (Serrote)", "target": "upper", "category": "Costas", "icon": "rowing"},
    {"name": "Barra Fixa (Pronada)", "target": "upper", "category": "Costas", "icon": "height"},
    {"name": "Barra Fixa (Supinada)", "target": "upper", "category": "Costas", "icon": "height"},
    {"name": "Levantamento Terra", "target": "upper", "category": "Costas", "icon": "fitness_center"},
    {"name": "Pulldown (Polia)", "target": "upper", "category": "Costas", "icon": "arrow_downward"},
    
    # OMBRO
    {"name": "Desenvolvimento (Halter)", "target": "upper", "category": "Ombro", "icon": "accessibility"},
    {"name": "Desenvolvimento (Barra)", "target": "upper", "category": "Ombro", "icon": "accessibility"},
    {"name": "Desenvolvimento Arnold", "target": "upper", "category": "Ombro", "icon": "accessibility"},
    {"name": "Elevação Lateral", "target": "upper", "category": "Ombro", "icon": "accessibility"},
    {"name": "Elevação Frontal", "target": "upper", "category": "Ombro", "icon": "accessibility"},
    {"name": "Crucifixo Inverso", "target": "upper", "category": "Ombro", "icon": "accessibility"},
    {"name": "Encolhimento (Trapézio)", "target": "upper", "category": "Ombro", "icon": "accessibility"},
    {"name": "Remada Alta", "target": "upper", "category": "Ombro", "icon": "accessibility"},
    
    # TRÍCEPS
    {"name": "Tríceps Corda", "target": "upper", "category": "Braço", "icon": "fitness_center"},
    {"name": "Tríceps Testa", "target": "upper", "category": "Braço", "icon": "fitness_center"},
    {"name": "Tríceps Francês", "target": "upper", "category": "Braço", "icon": "fitness_center"},
    {"name": "Tríceps Pulley (Barra)", "target": "upper", "category": "Braço", "icon": "fitness_center"},
    {"name": "Tríceps Banco", "target": "upper", "category": "Braço", "icon": "fitness_center"},
    {"name": "Tríceps Coice", "target": "upper", "category": "Braço", "icon": "fitness_center"},

    # BÍCEPS
    {"name": "Rosca Direta (Barra)", "target": "upper", "category": "Braço", "icon": "fitness_center"},
    {"name": "Rosca Direta (Halter)", "target": "upper", "category": "Braço", "icon": "fitness_center"},
    {"name": "Rosca Martelo", "target": "upper", "category": "Braço", "icon": "fitness_center"},
    {"name": "Rosca Scott", "target": "upper", "category": "Braço", "icon": "fitness_center"},
    {"name": "Rosca Concentrada", "target": "upper", "category": "Braço", "icon": "fitness_center"},
    {"name": "Rosca Inclinada", "target": "upper", "category": "Braço", "icon": "fitness_center"},
    
    # PERNAS - QUADRICEPS
    {"name": "Agachamento Livre", "target": "lower", "category": "Perna", "icon": "accessibility_new"},
    {"name": "Agachamento Smith", "target": "lower", "category": "Perna", "icon": "accessibility_new"},
    {"name": "Leg Press 45", "target": "lower", "category": "Perna", "icon": "chair"},
    {"name": "Leg Press Horizontal", "target": "lower", "category": "Perna", "icon": "chair"},
    {"name": "Cadeira Extensora", "target": "lower", "category": "Perna", "icon": "chair"},
    {"name": "Afundo (Passada)", "target": "lower", "category": "Perna", "icon": "directions_walk"},
    {"name": "Agachamento Búlgaro", "target": "lower", "category": "Perna", "icon": "accessibility_new"},
    {"name": "Hack Machine", "target": "lower", "category": "Perna", "icon": "accessibility_new"},
    
    # PERNAS - POSTERIOR/GLÚTEO
    {"name": "Mesa Flexora", "target": "lower", "category": "Perna", "icon": "chair"},
    {"name": "Cadeira Flexora", "target": "lower", "category": "Perna", "icon": "chair"},
    {"name": "Flexora em Pé", "target": "lower", "category": "Perna", "icon": "directions_walk"},
    {"name": "Stiff", "target": "lower", "category": "Perna", "icon": "accessibility_new"},
    {"name": "Levantamento Terra Romeno", "target": "lower", "category": "Perna", "icon": "accessibility_new"},
    {"name": "Elevação Pélvica", "target": "lower", "category": "Perna", "icon": "accessibility_new"},
    {"name": "Cadeira Abdutora", "target": "lower", "category": "Perna", "icon": "chair"},
    {"name": "Cadeira Adutora", "target": "lower", "category": "Perna", "icon": "chair"},
    {"name": "Glúteo na Polia (Coice)", "target": "lower", "category": "Perna", "icon": "directions_walk"},
    
    # PANTURRILHA
    {"name": "Panturrilha em Pé", "target": "lower", "category": "Perna", "icon": "directions_walk"},
    {"name": "Panturrilha Sentado", "target": "lower", "category": "Perna", "icon": "chair"},
    {"name": "Panturrilha no Leg Press", "target": "lower", "category": "Perna", "icon": "chair"},
    
    # CARDIO
    {"name": "Esteira (Caminhada)", "target": "stamina", "category": "Cardio", "icon": "directions_run"},
    {"name": "Esteira (Corrida)", "target": "stamina", "category": "Cardio", "icon": "directions_run"},
    {"name": "Bicicleta Ergométrica", "target": "stamina", "category": "Cardio", "icon": "directions_bike"},
    {"name": "Elíptico", "target": "stamina", "category": "Cardio", "icon": "directions_run"},
    {"name": "Escada", "target": "stamina", "category": "Cardio", "icon": "stairs"},
    {"name": "Pular Corda", "target": "stamina", "category": "Cardio", "icon": "refresh"},
    {"name": "Remo (Ergômetro)", "target": "stamina", "category": "Cardio", "icon": "rowing"},
    
    # FOCUS/OUTROS
    {"name": "Abdominal Supra", "target": "focus", "category": "Outros", "icon": "self_improvement"},
    {"name": "Abdominal Infra", "target": "focus", "category": "Outros", "icon": "self_improvement"},
    {"name": "Abdominal Remador", "target": "focus", "category": "Outros", "icon": "self_improvement"},
    {"name": "Prancha (Plank)", "target": "focus", "category": "Outros", "icon": "self_improvement"},
    {"name": "Alongamento Geral", "target": "focus", "category": "Outros", "icon": "self_improvement"},
    {"name": "Mobilidade de Quadril", "target": "focus", "category": "Outros", "icon": "loop"},
    {"name": "Mobilidade de Ombro", "target": "focus", "category": "Outros", "icon": "loop"},
]

PREMADE_WORKOUTS = {
    "Adaptação (Full Body)": ["Supino Reto (Barra)", "Puxada Frontal", "Agachamento Livre", "Desenvolvimento (Halter)", "Rosca Direta", "Tríceps Corda", "Abdominal Supra"],
    "Treino A (Superiores)": ["Supino Reto (Barra)", "Puxada Frontal", "Desenvolvimento (Barra)", "Tríceps Corda", "Rosca Direta"],
    "Treino B (Inferiores)": ["Agachamento Livre", "Leg Press 45", "Stiff"],
    "Só Cardio": ["Esteira (Corrida)", "Bicicleta Ergométrica"]
}

SHOP_ITEMS = [
    {"name": "Whey Protein", "type": "consumable", "slot": "none", "price": 200, "desc": "+500 XP", "icon": "item_whey_protein.png", "bonus": "xp_500"},
    {"name": "Elixir Pré-Treino", "type": "consumable", "slot": "none", "price": 500, "desc": "+1000 XP", "icon": "item_elixir_pre_treino.png", "bonus": "xp_1000"},
    {"name": "Espada Olímpica", "type": "equip", "slot": "main_hand", "price": 5000, "desc": "+10 Upper", "icon": "item_espada_olimpica.png", "bonus": "upper_10"},
    {"name": "Escudo de Anilha", "type": "equip", "slot": "off_hand", "price": 3500, "desc": "+5 Upper", "icon": "item_escudo_de_anilha.png", "bonus": "upper_5"},
    {"name": "Cinturão Hércules", "type": "equip", "slot": "chest", "price": 10000, "desc": "+25 Lower", "icon": "item_cinturao_de_hercules.png", "bonus": "lower_25"},
    {"name": "Tênis de Hermes", "type": "equip", "slot": "feet", "price": 12000, "desc": "+20 Stamina", "icon": "item_tenis_de_hermes.png", "bonus": "stamina_20"},
    {"name": "Mjolnir", "type": "equip", "slot": "main_hand", "price": 15000, "desc": "+30 Upper", "icon": "item_mjolnir.png", "bonus": "upper_30"},
    {"name": "Javali da Esteira", "type": "equip", "slot": "mount", "price": 10000, "desc": "+10 Stamina", "icon": "item_javali_da_esteira.png", "bonus": "stamina_10"},
    {"name": "Pílula de Cafeína", "type": "consumable", "slot": "none", "price": 99999, "desc": "+2000 XP", "icon": "item_capsula_do_tempo.png", "bonus": "xp_2000"},
]

ACHIEVEMENTS_DATA = [
    # NÍVEL
    {"id": "lvl5", "name": "O Despertar", "desc": "Alcance o Nível 5", "type": "level", "value": 5, "reward_title": "Novato", "xp": 500, "gold": 200},
    {"id": "lvl10", "name": "Guerreiro Iniciante", "desc": "Alcance o Nível 10", "type": "level", "value": 10, "reward_title": "Aprendiz", "xp": 1000, "gold": 500},
    {"id": "lvl20", "name": "Veterano de Ferro", "desc": "Alcance o Nível 20", "type": "level", "value": 20, "reward_title": "Veterano", "xp": 2000, "gold": 1000},
    {"id": "lvl50", "name": "Lenda Viva", "desc": "Alcance o Nível 50", "type": "level", "value": 50, "reward_title": "Lenda", "xp": 5000, "gold": 5000},
    
    # OURO
    {"id": "gold2k", "name": "Primeiro Salário", "desc": "Acumule 2.000 Gold", "type": "gold", "value": 2000, "reward_title": "Patrocinado", "xp": 200, "gold": 0},
    {"id": "gold10k", "name": "Magnata Fitness", "desc": "Acumule 10.000 Gold", "type": "gold", "value": 10000, "reward_title": "Magnata", "xp": 1000, "gold": 0},

    # VOLUME DE TREINO (FORÇA - KG TOTAIS NA VIDA)
    {"id": "vol10k", "name": "Primeira Tonelada", "desc": "Levante 10.000 kg totais", "type": "volume", "value": 10000, "reward_title": "Levantador", "xp": 500, "gold": 100},
    {"id": "vol100k", "name": "Hércules", "desc": "Levante 100.000 kg totais", "type": "volume", "value": 100000, "reward_title": "Hércules", "xp": 2000, "gold": 500},
    {"id": "vol1m", "name": "Atlas", "desc": "Levante 1 Milhão de kg totais", "type": "volume", "value": 1000000, "reward_title": "Atlas", "xp": 10000, "gold": 2000},

    # DISTÂNCIA (CARDIO - KM TOTAIS NA VIDA)
    {"id": "dist50", "name": "Peregrino", "desc": "Percorra 50 km totais", "type": "distance", "value": 50, "reward_title": "Peregrino", "xp": 500, "gold": 100},
    {"id": "dist500", "name": "Maratonista", "desc": "Percorra 500 km totais", "type": "distance", "value": 500, "reward_title": "Maratonista", "xp": 2000, "gold": 500},

    # CONSTÂNCIA (STREAK - DIAS SEGUIDOS)
    {"id": "streak7", "name": "Focado", "desc": "Treine 7 dias seguidos", "type": "streak", "value": 7, "reward_title": "Focado", "xp": 1000, "gold": 300},
    {"id": "streak30", "name": "Disciplina de Monge", "desc": "Treine 30 dias seguidos", "type": "streak", "value": 30, "reward_title": "Monge", "xp": 5000, "gold": 1500},
]

DAILY_REWARDS_CONFIG = [
    {"day": 1, "gold": 50, "xp": 100, "item": None},
    {"day": 2, "gold": 100, "xp": 150, "item": None},
    {"day": 3, "gold": 150, "xp": 200, "item": None},
    {"day": 4, "gold": 200, "xp": 300, "item": None},
    {"day": 5, "gold": 300, "xp": 400, "item": None},
    {"day": 6, "gold": 500, "xp": 600, "item": None},
    {"day": 7, "gold": 1000, "xp": 1000, "item": "Pílula de Cafeína"},
]

# ==============================================================================
# 2. BANCO DE DADOS
# ==============================================================================
class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("iron_rpg_global.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()
        self.populate_data()

    def init_db(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS heroes (
                user_id INTEGER PRIMARY KEY, name TEXT, gender TEXT, rpg_class TEXT, alignment TEXT,
                level INTEGER, xp_atual INTEGER, xp_max INTEGER, gold INTEGER, hp_atual INTEGER, hp_max INTEGER,
                skill_upper INTEGER, prog_upper INTEGER, skill_lower INTEGER, prog_lower INTEGER,
                skill_stamina INTEGER, prog_stamina INTEGER, skill_focus INTEGER, prog_focus INTEGER,
                equip_head INTEGER, equip_chest INTEGER, equip_legs INTEGER, equip_feet INTEGER,
                equip_main_hand INTEGER, equip_off_hand INTEGER, equip_acc1 INTEGER, equip_acc2 INTEGER, equip_mount INTEGER,
                current_title TEXT DEFAULT 'Aventureiro',
                current_streak INTEGER DEFAULT 1,
                last_claim_date TEXT DEFAULT '',
                last_strength_date TEXT DEFAULT '',
                last_cardio_date TEXT DEFAULT '',
                cardio_count_today INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        self.cursor.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT, slot TEXT, price INTEGER, description TEXT, icon TEXT, bonus TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item_id INTEGER, quantity INTEGER, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(item_id) REFERENCES items(id))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS exercises (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, target TEXT, category TEXT, icon TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS routines (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, FOREIGN KEY(user_id) REFERENCES users(id))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS routine_exercises (id INTEGER PRIMARY KEY AUTOINCREMENT, routine_id INTEGER, exercise_id INTEGER, FOREIGN KEY(routine_id) REFERENCES routines(id), FOREIGN KEY(exercise_id) REFERENCES exercises(id))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS workout_log (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, exercise_id INTEGER, weight REAL, reps REAL, date TEXT, used_in_battle INTEGER DEFAULT 0, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(exercise_id) REFERENCES exercises(id))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS unlocked_achievements (user_id INTEGER, achievement_id TEXT, PRIMARY KEY(user_id, achievement_id))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS boss_progress (user_id INTEGER PRIMARY KEY, boss_level INTEGER, current_hp REAL)")
        self.conn.commit()

    def populate_data(self):
        self.cursor.execute("DELETE FROM items") 
        for i in SHOP_ITEMS:
            self.cursor.execute("INSERT INTO items (name, type, slot, price, description, icon, bonus) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                                (i['name'], i['type'], i['slot'], i['price'], i['desc'], i['icon'], i.get('bonus', '')))
        
        self.cursor.execute("DELETE FROM exercises") 
        for ex in DEFAULT_EXERCISES:
            self.cursor.execute("INSERT INTO exercises (name, target, category, icon) VALUES (?, ?, ?, ?)", 
                                (ex['name'], ex['target'], ex['category'], ex['icon']))
        self.conn.commit()

    # --- LÓGICA DO BOSS ---
    def get_boss_status(self, user_id):
        self.cursor.execute("SELECT boss_level, current_hp FROM boss_progress WHERE user_id=?", (user_id,))
        res = self.cursor.fetchone()
        
        if not res:
            lvl = 1; boss_data = next(b for b in BOSS_LADDER if b['lvl'] == lvl); hp = boss_data['hp']
            self.cursor.execute("INSERT INTO boss_progress VALUES (?, ?, ?)", (user_id, lvl, hp)); self.conn.commit()
            return boss_data, hp
        else:
            lvl, hp = res
            boss_data = next((b for b in BOSS_LADDER if b['lvl'] == lvl), None)
            if not boss_data: 
                lvl = 1; boss_data = BOSS_LADDER[0]; hp = boss_data['hp']
                self.cursor.execute("UPDATE boss_progress SET boss_level=?, current_hp=? WHERE user_id=?", (lvl, hp, user_id)); self.conn.commit()
            return boss_data, hp

    def attack_boss(self, user_id):
        self.cursor.execute("""
            SELECT w.id, w.weight, w.reps, e.target 
            FROM workout_log w
            JOIN exercises e ON w.exercise_id = e.id
            WHERE w.user_id=? AND w.used_in_battle=0
        """, (user_id,))
        logs = self.cursor.fetchall()
        
        if not logs: return 0, "Sem treinos novos para atacar!"

        total_dmg = 0; log_ids = []
        for l in logs:
            lid, weight, reps, target = l
            dmg = reps * 100 if target == 'stamina' else weight * reps
            total_dmg += dmg
            log_ids.append(lid)
        
        boss_data, current_hp = self.get_boss_status(user_id)
        new_hp = current_hp - total_dmg
        boss_died = False
        
        if new_hp <= 0: boss_died = True; new_hp = 0
            
        for lid in log_ids: self.cursor.execute("UPDATE workout_log SET used_in_battle=1 WHERE id=?", (lid,))
        
        msg = ""
        if boss_died:
            next_lvl = boss_data['lvl'] + 1
            next_boss = next((b for b in BOSS_LADDER if b['lvl'] == next_lvl), None)
            
            if next_boss:
                self.cursor.execute("UPDATE boss_progress SET boss_level=?, current_hp=? WHERE user_id=?", (next_lvl, next_boss['hp'], user_id))
                msg = f"VITÓRIA! Dano: {int(total_dmg)}. Novo Boss: {next_boss['name']}"
                hero = self.carregar_heroi(user_id); hero['gold'] += 500 * boss_data['lvl']; self.salvar_progresso(user_id, hero)
            else:
                self.cursor.execute("UPDATE boss_progress SET current_hp=0 WHERE user_id=?", (user_id,))
                msg = f"LENDÁRIO! Torre Limpa! Dano: {int(total_dmg)}"
        else:
            self.cursor.execute("UPDATE boss_progress SET current_hp=? WHERE user_id=?", (new_hp, user_id))
            msg = f"Ataque! Dano: {int(total_dmg)}. Boss HP: {int(new_hp)}"

        self.conn.commit()
        return total_dmg, msg

    # --- CHECK DE LIMITES (ANTI-CHEAT) ---
    # --- SUBSTITUA ESSES DOIS MÉTODOS DENTRO DE DatabaseManager ---
    
    def check_training_limit(self, user_id, is_strength):
        hero = self.carregar_heroi(user_id)
        today = str(datetime.now().date()) # Formato YYYY-MM-DD
        
        if is_strength:
            # Se a data do último treino de força for igual a hoje, bloqueia
            if hero['last_strength'] == today: 
                return False, "Você já treinou Força hoje! Descanse ou faça Cardio."
            return True, "OK"
        else:
            # Lógica do Cardio
            if hero['last_cardio'] != today:
                # Se é um dia novo, reseta o contador
                self.cursor.execute("UPDATE heroes SET cardio_count_today=0, last_cardio_date=? WHERE user_id=?", (today, user_id))
                self.conn.commit()
                return True, "OK"
            
            # Se for hoje, verifica se já bateu 2 cardios
            if hero['cardio_count'] >= 2: 
                return False, "Limite de 2 Cardios diários atingido!"
            return True, "OK"

    def update_training_limit(self, user_id, is_strength):
        today = str(datetime.now().date())
        if is_strength: 
            self.cursor.execute("UPDATE heroes SET last_strength_date=? WHERE user_id=?", (today, user_id))
        else: 
            self.cursor.execute("UPDATE heroes SET last_cardio_date=?, cardio_count_today=cardio_count_today+1 WHERE user_id=?", (today, user_id))
        self.conn.commit()

    # --- DAILY STATUS ---
    def get_daily_status(self, user_id):
        hero = self.carregar_heroi(user_id)
        last_claim = hero['last_claim']
        streak = hero['streak']
        today = datetime.now().date()
        can_claim = False; display_streak = streak
        if not last_claim: can_claim = True; display_streak = 1
        else:
            try:
                last_date = datetime.strptime(last_claim, "%Y-%m-%d").date()
                if last_date == today: can_claim = False
                elif last_date == today - timedelta(days=1): can_claim = True
                else: can_claim = True; display_streak = 1
            except: can_claim = True; display_streak = 1
        return display_streak, can_claim

    def claim_daily_reward(self, user_id):
        hero = self.carregar_heroi(user_id)
        last_claim = hero['last_claim']; streak = hero['streak']; today = datetime.now().date(); new_streak = 1
        if last_claim:
            try:
                last_date = datetime.strptime(last_claim, "%Y-%m-%d").date()
                if last_date == today - timedelta(days=1): new_streak = streak + 1
            except: pass
        cycle_day = new_streak if new_streak <= 7 else 1
        if new_streak > 7: new_streak = 1
        reward = next((r for r in DAILY_REWARDS_CONFIG if r['day'] == cycle_day), None)
        if reward:
            hero['gold'] += reward['gold']; hero['xp'] += reward['xp']
            if reward['item']:
                self.cursor.execute("SELECT id FROM items WHERE name=?", (reward['item'],))
                item_res = self.cursor.fetchone()
                if item_res: self.cursor.execute("INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, 1)", (user_id, item_res[0]))
            self.cursor.execute("UPDATE heroes SET current_streak=?, last_claim_date=?, gold=?, xp_atual=? WHERE user_id=?", (new_streak, str(today), hero['gold'], hero['xp'], user_id))
            self.conn.commit()
            return reward, new_streak
        return None, new_streak


    def check_and_unlock_achievements(self, user_id):
        hero = self.carregar_heroi(user_id)
        total_w, total_dist = self.get_lifetime_stats(user_id)
        unlocked_now = []
        
        for ach in ACHIEVEMENTS_DATA:
            is_met = False
            # Verifica cada tipo de conquista
            if ach['type'] == 'level' and hero['level'] >= ach['value']: is_met = True
            elif ach['type'] == 'gold' and hero['gold'] >= ach['value']: is_met = True
            elif ach['type'] == 'volume' and total_w >= ach['value']: is_met = True
            elif ach['type'] == 'distance' and total_dist >= ach['value']: is_met = True
            elif ach['type'] == 'streak' and hero['streak'] >= ach['value']: is_met = True
            
            if is_met:
                # Verifica se já pegou essa conquista antes
                self.cursor.execute("SELECT 1 FROM unlocked_achievements WHERE user_id=? AND achievement_id=?", (user_id, ach['id']))
                if not self.cursor.fetchone():
                    self.cursor.execute("INSERT INTO unlocked_achievements VALUES (?, ?)", (user_id, ach['id']))
                    hero['xp'] += ach['xp']
                    hero['gold'] += ach['gold']
                    unlocked_now.append(ach)
                    
        if unlocked_now: 
            self.salvar_progresso(user_id, hero)
            
        self.conn.commit()
        return unlocked_now

    def get_unlocked_titles(self, user_id):
        self.cursor.execute("SELECT achievement_id FROM unlocked_achievements WHERE user_id=?", (user_id,))
        ids = [r[0] for r in self.cursor.fetchall()]
        titles = ["Aventureiro"]
        for ach in ACHIEVEMENTS_DATA:
            if ach['id'] in ids: titles.append(ach['reward_title'])
        return titles
    def set_title(self, user_id, title): self.cursor.execute("UPDATE heroes SET current_title = ? WHERE user_id = ?", (title, user_id)); self.conn.commit()
    def get_lifetime_stats(self, user_id):
        self.cursor.execute("SELECT SUM(w.weight * w.reps) FROM workout_log w JOIN exercises e ON w.exercise_id = e.id WHERE w.user_id = ? AND e.target != 'stamina'", (user_id,))
        total_weight = self.cursor.fetchone()[0] or 0
        self.cursor.execute("SELECT SUM(w.reps) FROM workout_log w JOIN exercises e ON w.exercise_id = e.id WHERE w.user_id = ? AND e.target = 'stamina'", (user_id,))
        total_km = self.cursor.fetchone()[0] or 0
        return total_weight, total_km
    def get_exercise_history(self, user_id, exercise_id):
        self.cursor.execute("SELECT date, weight, reps FROM workout_log WHERE user_id = ? AND exercise_id = ? ORDER BY id DESC LIMIT 10", (user_id, exercise_id))
        return [{"date": r[0], "weight": r[1], "reps": r[2]} for r in self.cursor.fetchall()]
    def get_all_exercises(self): self.cursor.execute("SELECT * FROM exercises ORDER BY category, name"); return [{"id": r[0], "name": r[1], "target": r[2], "category": r[3], "icon": r[4]} for r in self.cursor.fetchall()]
    def import_premade_routine(self, user_id, routine_name):
        exercises = PREMADE_WORKOUTS.get(routine_name, [])
        if not exercises: return False
        self.cursor.execute("INSERT INTO routines (user_id, name) VALUES (?, ?)", (user_id, routine_name))
        rid = self.cursor.lastrowid
        for ex_name in exercises:
            self.cursor.execute("SELECT id FROM exercises WHERE name = ?", (ex_name,))
            res = self.cursor.fetchone()
            if not res:
                self.cursor.execute("SELECT id FROM exercises WHERE name LIKE ?", (f"{ex_name}%",))
                res = self.cursor.fetchone()
            if res: self.cursor.execute("INSERT INTO routine_exercises (routine_id, exercise_id) VALUES (?, ?)", (rid, res[0]))
        self.conn.commit()
        return True
    def create_routine(self, user_id, name, exercise_ids):
        self.cursor.execute("INSERT INTO routines (user_id, name) VALUES (?, ?)", (user_id, name))
        rid = self.cursor.lastrowid
        for ex in exercise_ids: self.cursor.execute("INSERT INTO routine_exercises (routine_id, exercise_id) VALUES (?, ?)", (rid, ex))
        self.conn.commit()
    def delete_routine(self, rid): self.cursor.execute("DELETE FROM routine_exercises WHERE routine_id=?", (rid,)); self.cursor.execute("DELETE FROM routines WHERE id=?", (rid,)); self.conn.commit()
    def get_user_routines(self, user_id):
        self.cursor.execute("SELECT id, name FROM routines WHERE user_id = ?", (user_id,))
        routines = []
        for r in self.cursor.fetchall():
            self.cursor.execute("SELECT ex.id, ex.name, ex.target, ex.category, ex.icon FROM routine_exercises re JOIN exercises ex ON re.exercise_id = ex.id WHERE re.routine_id = ?", (r[0],))
            exs = [{"id": x[0], "name": x[1], "target": x[2], "category": x[3], "icon": x[4]} for x in self.cursor.fetchall()]
            routines.append({"id": r[0], "name": r[1], "exercises": exs})
        return routines
    def log_set(self, user_id, exercise_id, weight, reps):
        self.cursor.execute("INSERT INTO workout_log (user_id, exercise_id, weight, reps, date, used_in_battle) VALUES (?, ?, ?, ?, datetime('now', 'localtime'), 0)", (user_id, exercise_id, weight, reps))
        self.cursor.execute("SELECT target FROM exercises WHERE id = ?", (exercise_id,))
        res = self.cursor.fetchone(); target_skill = res[0] if res else "upper"
        xp_gained = int(10 + (weight * 0.1)); gold_gained = 2
        hero = self.carregar_heroi(user_id); hero['xp'] += xp_gained; hero['gold'] += gold_gained
        return xp_gained, gold_gained, target_skill
    def get_shop_items(self): self.cursor.execute("SELECT * FROM items"); return [{"id": r[0], "name": r[1], "type": r[2], "slot": r[3], "price": r[4], "desc": r[5], "icon": r[6], "bonus": r[7]} for r in self.cursor.fetchall()]
    def get_inventory(self, user_id): self.cursor.execute("SELECT inv.id, inv.item_id, inv.quantity, it.name, it.type, it.slot, it.icon, it.description, it.bonus FROM inventory inv JOIN items it ON inv.item_id = it.id WHERE inv.user_id = ?", (user_id,)); return [{"inv_id": r[0], "item_id": r[1], "qtd": r[2], "name": r[3], "type": r[4], "slot": r[5], "icon": r[6], "desc": r[7], "bonus": r[8]} for r in self.cursor.fetchall()]
    def buy_item(self, user_id, item_id, price):
        hero = self.carregar_heroi(user_id)
        if hero['gold'] >= price:
            self.cursor.execute("UPDATE heroes SET gold = ? WHERE user_id = ?", (hero['gold'] - price, user_id))
            self.cursor.execute("INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, 1)", (user_id, item_id))
            self.conn.commit(); return True, hero['gold'] - price
        return False, hero['gold']
    def equip_item(self, user_id, item_id, slot_type):
        slot_map = {"head": "equip_head", "chest": "equip_chest", "legs": "equip_legs", "feet": "equip_feet", "main_hand": "equip_main_hand", "off_hand": "equip_off_hand", "mount": "equip_mount", "accessory": "equip_acc1"}
        db_col = slot_map.get(slot_type)
        if db_col: self.cursor.execute(f"UPDATE heroes SET {db_col} = ? WHERE user_id = ?", (item_id, user_id)); self.conn.commit(); return True
        return False
    def unequip_item(self, user_id, slot_type):
        slot_map = {"head": "equip_head", "chest": "equip_chest", "legs": "equip_legs", "feet": "equip_feet", "main_hand": "equip_main_hand", "off_hand": "equip_off_hand", "mount": "equip_mount", "accessory": "equip_acc1"}
        db_col = slot_map.get(slot_type)
        if db_col: self.cursor.execute(f"UPDATE heroes SET {db_col} = 0 WHERE user_id = ?", (user_id,)); self.conn.commit(); return True
        return False
    def use_consumable(self, user_id, inv_id, bonus_type):
        self.cursor.execute("DELETE FROM inventory WHERE id = ?", (inv_id,)); self.conn.commit(); return True
    def registrar_usuario(self, user, pwd):
        try: self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd)); self.conn.commit(); return self.cursor.lastrowid
        except: return None
    def login_usuario(self, user, pwd): self.cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (user, pwd)); res = self.cursor.fetchone(); return res[0] if res else None
    
    def criar_heroi(self, uid, name, gender, cls, align):
        self.cursor.execute("""
            INSERT INTO heroes VALUES (
                ?, ?, ?, ?, ?, 
                1, 0, 100, 500, 100, 100, 
                10, 0, 10, 0, 10, 0, 10, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 
                'Aventureiro', 1, '', '', '', 0
            )
        """, (uid, name, gender, cls, align)); self.conn.commit()
    
    def carregar_heroi(self, uid):
        self.cursor.execute("SELECT * FROM heroes WHERE user_id = ?", (uid,))
        r = self.cursor.fetchone()
        if r:
            return {
                "name": r[1], "gender": r[2], "class": r[3], "alignment": r[4],
                "level": r[5], "xp": r[6], "xp_max": r[7], "gold": r[8], "hp": r[9], "hp_max": r[10],
                "upper": {"lvl": r[11], "prog": r[12]}, "lower": {"lvl": r[13], "prog": r[14]}, 
                "stamina": {"lvl": r[15], "prog": r[16]}, "focus": {"lvl": r[17], "prog": r[18]},
                "equip": {"head": r[19], "chest": r[20], "legs": r[21], "feet": r[22], 
                          "main": r[23], "off": r[24], "acc1": r[25], "acc2": r[26], "mount": r[27]},
                "title": r[28],
                "streak": r[29], "last_claim": r[30],
                "last_strength": r[31], "last_cardio": r[32], "cardio_count": r[33]
            }
        return None
    
    def salvar_progresso(self, uid, h):
        self.cursor.execute("""
            UPDATE heroes SET level=?, xp_atual=?, xp_max=?, gold=?, hp_atual=?, hp_max=?,
            skill_upper=?, prog_upper=?, skill_lower=?, prog_lower=?,
            skill_stamina=?, prog_stamina=?, skill_focus=?, prog_focus=? WHERE user_id=?
        """, (h['level'], h['xp'], h['xp_max'], h['gold'], h['hp'], h['hp_max'], h['upper']['lvl'], h['upper']['prog'], h['lower']['lvl'], h['lower']['prog'], h['stamina']['lvl'], h['stamina']['prog'], h['focus']['lvl'], h['focus']['prog'], uid))
        self.conn.commit()

# ==============================================================================
# 3. INTERFACE GRÁFICA
# ==============================================================================
def main(page: ft.Page):
    print(f"DEBUG: Executando em {os.getcwd()}") 
    page.title = "Iron RPG"; page.theme_mode = "dark"; page.bgcolor = THEME["bg"]
    page.window_width = 400; page.window_height = 800; page.scroll = None
    page.fonts = {"RPG": "/rpg_font.ttf"}; page.theme = ft.Theme(font_family="RPG") 
    db = DatabaseManager(); session = {"user_id": None, "hero": None, "daily_msg": None}
    
    # --- ÁUDIO DESATIVADO TEMPORARIAMENTE (Evita erro no Android) ---
    def play_sound(type):
        pass # Não faz nada, apenas evita erro no código
    
    def show_snack(msg, color="green"): page.snack_bar = ft.SnackBar(ft.Text(msg, font_family="RPG"), bgcolor=color); page.snack_bar.open = True; page.update()
    
    def get_asset_image(image_name, size=30):
        # Caminho absoluto para garantir carregamento
        return ft.Image(src=f"/{image_name}", width=size, height=size, fit=ft.ImageFit.CONTAIN,
                        error_content=ft.Icon(name="broken_image", size=size, color="grey"))
    
    def resolve_char_image_path(cls_raw, gen_raw, align_raw):
        def normalize(txt): return ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn').lower()
        cls = normalize(cls_raw); gen = normalize(gen_raw); align = normalize(align_raw)
        return f"char_{cls}_{gen}_{align}.png"
        
    def rpg_container(content, padding=10, bgcolor=THEME["card_bg"]):
        return ft.Container(content=content, padding=padding, bgcolor=bgcolor, border=ft.border.all(1, THEME["primary"]), border_radius=ft.border_radius.all(8), shadow=ft.BoxShadow(blur_radius=5, color="black"))
    def calculate_effective_stats(hero):
        effective = {"upper": hero["upper"]["lvl"], "lower": hero["lower"]["lvl"], "stamina": hero["stamina"]["lvl"], "focus": hero["focus"]["lvl"]}
        inventory = db.get_inventory(session["user_id"]); equipped_slots = hero['equip']
        for item in inventory:
            is_equipped = False
            for slot_name, item_id in equipped_slots.items():
                if item_id == item['item_id']: is_equipped = True; break
            if is_equipped and item['bonus']:
                parts = item['bonus'].split('_')
                if len(parts) == 2:
                    stat, val = parts[0], int(parts[1])
                    if stat in effective: effective[stat] += val
        return effective

    # --- TELAS ---
    def view_login():
        page.vertical_alignment = "center"; page.horizontal_alignment = "center"
        user = ft.TextField(label="Usuário", border_color=THEME["primary"], text_style=ft.TextStyle(font_family="RPG")); pwd = ft.TextField(label="Senha", password=True, border_color=THEME["primary"], text_style=ft.TextStyle(font_family="RPG"))
        def log(e):
            play_sound("click")
            uid = db.login_usuario(user.value, pwd.value)
            if uid: 
                session["user_id"] = uid; session["hero"] = db.carregar_heroi(uid)
                page.go("/game" if session["hero"] else "/create_char")
            else: show_snack("Erro no login", "red")
        return ft.View("/", [ft.Stack([ft.Image(src="/background.png", fit=ft.ImageFit.COVER, expand=True), ft.Container(bgcolor=THEME["bg_overlay"], expand=True), ft.Container(alignment=ft.alignment.center, content=rpg_container(ft.Column([ft.Icon("shield", size=60, color=THEME["primary"]), ft.Text("IRON RPG", size=40, weight="bold", color=THEME["accent"], font_family="RPG"), user, pwd, ft.ElevatedButton("ENTRAR", on_click=log, style=ft.ButtonStyle(bgcolor=THEME["primary"], color="white")), ft.TextButton("Criar Conta", on_click=lambda e: page.go("/register"))], horizontal_alignment="center", spacing=15), padding=30))])], padding=0)

    def view_register():
        page.vertical_alignment = "center"; page.horizontal_alignment = "center"
        user = ft.TextField(label="Novo Usuário", border_color=THEME["accent"]); pwd = ft.TextField(label="Nova Senha", password=True, border_color=THEME["accent"])
        def reg(e):
            play_sound("click"); uid = db.registrar_usuario(user.value, pwd.value)
            if uid: session["user_id"] = uid; show_snack("Criado!"); time.sleep(0.5); page.go("/create_char")
            else: show_snack("Existe", "red")
        return ft.View("/register", [ft.Stack([ft.Image(src="/background.png", fit=ft.ImageFit.COVER, expand=True), ft.Container(bgcolor=THEME["bg_overlay"], expand=True), ft.Container(alignment=ft.alignment.center, content=rpg_container(ft.Column([ft.Text("REGISTRO", color=THEME["accent"], size=30, weight="bold", font_family="RPG"), user, pwd, ft.ElevatedButton("CONFIRMAR", on_click=reg, style=ft.ButtonStyle(bgcolor=THEME["accent"], color="black")), ft.TextButton("Voltar", on_click=lambda e: page.go("/"))], horizontal_alignment="center", spacing=15), padding=30))])], padding=0)

    def view_create_char():
        page.vertical_alignment = "start"; page.horizontal_alignment = "center"
        name = ft.TextField(label="Nome", border_color=THEME["accent"])
        gender_dropdown = ft.Dropdown(label="Gênero", border_color=THEME["accent"], options=[ft.dropdown.Option("Masculino"), ft.dropdown.Option("Feminino"), ft.dropdown.Option("Outro")])
        gender_dropdown.value = "Masculino"; align_group = ft.RadioGroup(content=ft.Row([ft.Radio(value="good", label="Bondoso"), ft.Radio(value="evil", label="Maligno")]), on_change=lambda e: update_class_list()); align_group.value = "good"
        sel_class = ft.Ref[str](); cards_column = ft.Column(spacing=10, scroll="auto")
        
        def update_class_list(e=None):
            cards_column.controls.clear(); gen = gender_dropdown.value or "Masculino"; align = align_group.value or "good"
            for k, v in CLASSES_RPG.items():
                img_path = resolve_char_image_path(k, gen, align)
                # Verifica visualmente se a imagem carrega, senão usa ícone
                visual = get_asset_image(img_path, size=50)
                
                card = ft.Container(data=k, on_click=lambda e: [setattr(sel_class, 'current', e.control.data), update_class_list()], padding=10, bgcolor=THEME["card_bg"], border_radius=10, border=ft.border.all(1, "grey"), content=ft.Row([ft.Container(content=visual, padding=5, bgcolor="#222", border_radius=10), ft.Column([ft.Text(v["titulo"], weight="bold", size=18, color=THEME["accent"]), ft.Text(v["subtitulo"], size=12, italic=True), ft.Text(v["estilo"], size=12)])]))
                if sel_class.current == k: card.border = ft.border.all(2, THEME["accent"]); card.bgcolor = "#333"
                cards_column.controls.append(card)
            page.update()
        
        gender_dropdown.on_change = update_class_list; align_group.on_change = update_class_list
        def create(e):
            if not name.value or not gender_dropdown.value or not sel_class.current: show_snack("Preencha tudo!", "red"); return
            play_sound("lvl")
            db.criar_heroi(session["user_id"], name.value, gender_dropdown.value, sel_class.current, align_group.value)
            session["hero"] = db.carregar_heroi(session["user_id"]); page.go("/game")
        update_class_list()
        
        return ft.View("/create_char", [
            ft.Stack([
                ft.Image(src="/background.png", fit=ft.ImageFit.COVER, expand=True),
                ft.Container(bgcolor=THEME["bg_overlay"], expand=True),
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text("CRIE SEU HERÓI", size=30, weight="bold", color=THEME["accent"], font_family="RPG"), 
                        rpg_container(ft.Column([name, gender_dropdown, align_group])), 
                        ft.Container(content=cards_column, expand=True), 
                        ft.ElevatedButton("INICIAR", on_click=create, style=ft.ButtonStyle(bgcolor=THEME["primary"], color="white"))
                    ], expand=True) 
                )
            ], expand=True)
        ], padding=0)

    # --- TELA JOGO ---
    def view_game():
        page.vertical_alignment = "start"; page.horizontal_alignment = "center"
        hero = session["hero"]; rpg_data = CLASSES_RPG.get(hero["class"], CLASSES_RPG["Berserker"])
        active_workout = {"on": False, "routine": None, "exercises": [], "current_index": 0, "session_logs": []}
        body_content = ft.Container(expand=True)

        def get_profile_page(current_hero):
            eff_stats = calculate_effective_stats(current_hero)
            def change_title(e):
                titles = db.get_unlocked_titles(session["user_id"])
                def select_t(e, t_val): db.set_title(session["user_id"], t_val); show_snack(f"Título: {t_val}", "green"); page.close(dlg_t); update_ui(0)
                title_list = ft.Column(spacing=5)
                for t in titles: bg = THEME["accent"] if t == current_hero['title'] else "#333"; title_list.controls.append(ft.Container(content=ft.Text(t, color="black" if t == current_hero['title'] else "white", font_family="RPG"), bgcolor=bg, padding=10, border_radius=5, data=t, on_click=lambda e: select_t(e, e.control.data)))
                dlg_t = ft.AlertDialog(title=ft.Text("Escolha um Título", font_family="RPG"), content=title_list); page.open(dlg_t)

            def slot_box(label, icon, equipped_id):
                color = THEME["accent"] if equipped_id > 0 else "grey"
                return ft.Container(content=ft.Column([ft.Icon(icon, color=color, size=20), ft.Text(label, size=8, color=color, font_family="RPG")], alignment="center", spacing=2), width=60, height=60, bgcolor="#222", border_radius=5, border=ft.border.all(1, color), tooltip="Equipado" if equipped_id > 0 else "Vazio")
            
            img_file = resolve_char_image_path(current_hero['class'], current_hero['gender'], current_hero['alignment'])
            avatar_widget = get_asset_image(img_file, size=100)
            
            equip_grid = ft.Row([ft.Column([slot_box("Head", "headphones", current_hero['equip']['head']), slot_box("Body", "accessibility", current_hero['equip']['chest']), slot_box("Legs", "directions_walk", current_hero['equip']['legs']), slot_box("Feet", "hiking", current_hero['equip']['feet'])], spacing=5), ft.Container(content=ft.Column([avatar_widget, ft.Text(f"LVL {current_hero['level']}", size=24, weight="bold", color=THEME["accent"], font_family="RPG"), ft.Container(content=ft.Text(current_hero.get('title', 'Novato'), size=10, color="black", font_family="RPG"), bgcolor=THEME["accent"], padding=3, border_radius=5, on_click=change_title)], horizontal_alignment="center", spacing=2), padding=10, shadow=ft.BoxShadow(blur_radius=10, color="red")), ft.Column([slot_box("Main", "colorize", current_hero['equip']['main']), slot_box("Off", "shield", current_hero['equip']['off']), slot_box("Acc", "circle", current_hero['equip']['acc1']), slot_box("Mount", "pets", current_hero['equip']['mount'])], spacing=5)], alignment="center", spacing=10)
            inv_list = ft.Column(spacing=5); inventory = db.get_inventory(session["user_id"]); equipped_ids = current_hero['equip'].values()
            for item in inventory:
                is_equipped = item['item_id'] in equipped_ids 
                def action_click(e, i=item, eq=is_equipped):
                    play_sound("click")
                    if i['type'] == 'equip':
                        if eq: db.unequip_item(session["user_id"], i['slot']); show_snack(f"Desequipou {i['name']}", "orange")
                        else: db.equip_item(session["user_id"], i['item_id'], i['slot']); show_snack(f"Equipou {i['name']}!", "cyan")
                    elif i['type'] == 'consumable':
                        db.use_consumable(session["user_id"], i['inv_id'], i['bonus'])
                        if "xp" in i['bonus']: 
                            amount = int(i['bonus'].split("_")[1]); current_hero['xp'] += amount; show_snack(f"Usou {i['name']}: +{amount} XP!", "green"); 
                            while current_hero['xp'] >= current_hero['xp_max']: current_hero['xp'] -= current_hero['xp_max']; current_hero['level'] += 1; current_hero['xp_max'] = int(current_hero['xp_max'] * 1.2); show_snack(f"LEVEL UP! {current_hero['level']}", "cyan"); play_sound("lvl")
                            db.salvar_progresso(session["user_id"], current_hero)
                        new_achs = db.check_and_unlock_achievements(session["user_id"])
                        for ach in new_achs: show_snack(f"🏆 {ach['name']} Desbloqueado!", "yellow"); play_sound("lvl")
                    update_ui(0)
                inv_list.controls.append(ft.Container(content=ft.Row([get_asset_image(item['icon'], size=30), ft.Column([ft.Text(f"{item['name']} (x{item['qtd']})", weight="bold", font_family="RPG"), ft.Text(item['desc'], size=10, color="grey")], expand=True), ft.ElevatedButton("DESEQUIPAR" if is_equipped else "EQUIPAR" if item['type']=='equip' else "USAR", on_click=action_click, bgcolor="#333", color="red" if is_equipped else "blue" if item['type']=='equip' else "green", height=30)]), bgcolor="#222", padding=5, border_radius=5))
            skills = ft.Column(spacing=5); map_skills = [("UPP", "upper", "red"), ("LOW", "lower", "blue"), ("STM", "stamina", "green"), ("FOC", "focus", "purple")]
            for l, k, c in map_skills: val_base = current_hero[k]['lvl']; val_eff = eff_stats.get(k, val_base); txt = f"Lvl {val_base} +{val_eff - val_base}" if val_eff > val_base else f"Lvl {val_base}"; skills.controls.append(ft.Row([ft.Text(l, weight="bold", color="grey", font_family="RPG"), ft.ProgressBar(value=current_hero[k]['prog']/100, color=c, expand=True), ft.Text(txt, color=c, font_family="RPG")]))
            def open_achievements(e):
                unlocked = db.get_unlocked_titles(session["user_id"]); ach_list_ui = ft.Column(scroll="auto", height=300)
                for ach in ACHIEVEMENTS_DATA:
                    is_unlocked = ach['reward_title'] in unlocked; icon = "check_circle" if is_unlocked else "lock"; color = "green" if is_unlocked else "grey"
                    ach_list_ui.controls.append(ft.Container(content=ft.Row([ft.Icon(icon, color=color), ft.Column([ft.Text(ach['name'], weight="bold", color="white", font_family="RPG"), ft.Text(ach['desc'], size=12, color="grey")], expand=True), ft.Column([ft.Text(f"Título: {ach['reward_title']}", size=10, color="yellow"), ft.Text(f"+{ach['xp']} XP", size=10, color="cyan")])]), opacity=1.0 if is_unlocked else 0.5, bgcolor="#222", padding=10, border_radius=5))
                dlg_ach = ft.AlertDialog(title=ft.Text("CONQUISTAS", font_family="RPG"), content=ach_list_ui); page.open(dlg_ach)
            def open_daily(e):
                streak, can_claim = db.get_daily_status(session["user_id"]); days_row = ft.Row(scroll="auto")
                for d in DAILY_REWARDS_CONFIG:
                    bg = "#444" if d['day'] == streak else "#222" if d['day'] < streak else "#333"; ic = "check_circle" if d['day'] < streak else "radio_button_unchecked" if d['day'] == streak and can_claim else "lock"
                    days_row.controls.append(ft.Container(content=ft.Column([ft.Text(f"Dia {d['day']}", size=10), ft.Icon(ic, size=16), ft.Text(f"{d['gold']}G", size=10, color="yellow")], alignment="center"), bgcolor=bg, padding=10, border_radius=5))
                def claim(e):
                    rew, ns = db.claim_daily_reward(session["user_id"])
                    if rew: play_sound("lvl"); show_snack(f"Ganhou {rew['gold']}G!", "green"); page.close(dlg_d); update_ui(0)
                btn = ft.ElevatedButton("COLETAR" if can_claim else "JÁ PEGOU", on_click=claim, disabled=not can_claim)
                dlg_d = ft.AlertDialog(title=ft.Text("RECOMPENSA DIÁRIA"), content=ft.Column([days_row, btn], height=150)); page.open(dlg_d)

            header = rpg_container(ft.Column([ft.Row([ft.Icon(rpg_data["icon"], color=THEME["accent"]), ft.Text(current_hero['name'], size=24, weight="bold", color=THEME["text"], font_family="RPG"), ft.Container(expand=True), ft.Text(f"{current_hero['gold']} G", color="yellow", weight="bold", font_family="RPG"), ft.Row([ft.Icon("local_fire_department", color="orange"), ft.Text(f"{current_hero.get('streak', 0)}", color="orange", font_family="RPG")])]), ft.Row([ft.ElevatedButton("🏆 CONQUISTAS", on_click=open_achievements, width=140), ft.ElevatedButton("📅 BÔNUS DIÁRIO", on_click=open_daily, width=140)], alignment="center")]), padding=15)
            return ft.Column([header, equip_grid, ft.Divider(), ft.Text("MOCHILA", weight="bold", color="grey", font_family="RPG"), ft.Container(content=inv_list, height=150, padding=5, border=ft.border.all(1, "#333"), border_radius=5), ft.Divider(), ft.Text("SKILLS", weight="bold", color="grey", font_family="RPG"), skills], spacing=10, scroll="auto", expand=True)

        def get_shop_page(current_hero):
            lst = ft.Column(spacing=10, scroll="auto", expand=True)
            for item in db.get_shop_items():
                def buy(e, i=item):
                    ok, bal = db.buy_item(session["user_id"], i['id'], i['price'])
                    if ok: play_sound("coin"); show_snack(f"Comprou {i['name']}", "green"); update_ui(3)
                    else: show_snack("Sem Ouro!", "red")
                lst.controls.append(rpg_container(ft.Row([get_asset_image(item['icon'], size=40), ft.Column([ft.Text(item['name'], weight="bold", size=16), ft.Text(item['desc'], size=12, color="grey")], expand=True), ft.ElevatedButton(f"{item['price']} G", on_click=buy, bgcolor="#222", color="yellow")])))
            return ft.Column([rpg_container(ft.Row([ft.Text("MERCADOR", size=24, weight="bold"), ft.Container(expand=True), ft.Icon("circle", size=12, color="yellow"), ft.Text(f"{current_hero['gold']} G", color="yellow", size=18)])), lst], spacing=10, expand=True)

        def get_training_page():
            routines = db.get_user_routines(session["user_id"]); lst = ft.Column(spacing=10, scroll="auto", expand=True)
            def open_builder(e): 
                name_tf = ft.TextField(label="Nome"); all_exs = db.get_all_exercises(); selected_ids = []
                tabs = ft.Tabs(selected_index=0, expand=True); cats = ["Peito", "Costas", "Ombro", "Braço", "Perna", "Cardio", "Outros"]
                for c in cats:
                    cl = ft.Column(scroll="auto", expand=True)
                    for ex in all_exs: 
                        if ex['category']==c: 
                            cl.controls.append(ft.Checkbox(label=ex['name'], on_change=lambda e, x=ex['id']: selected_ids.append(x) if e.control.value else selected_ids.remove(x)))
                    tabs.tabs.append(ft.Tab(text=c, content=ft.Container(content=cl, padding=10)))
                def save(e): db.create_routine(session["user_id"], name_tf.value, selected_ids); page.close(dlg); update_ui(1)
                content_ui = ft.Container(content=ft.Column([name_tf, tabs], expand=True), height=400, width=300)
                dlg = ft.AlertDialog(title=ft.Text("Nova Ficha"), content=content_ui, actions=[ft.ElevatedButton("SALVAR", on_click=save)]); page.open(dlg)
            
            def open_premade(e):
                def sel(n): db.import_premade_routine(session["user_id"], n); page.close(dp); update_ui(1)
                col = ft.Column(scroll="auto", expand=True); 
                for k in PREMADE_WORKOUTS: col.controls.append(ft.Container(content=ft.Text(k), padding=10, bgcolor="#333", on_click=lambda e, x=k: sel(x)))
                dp = ft.AlertDialog(title=ft.Text("Fichas Prontas"), content=ft.Container(content=col, height=300, width=300)); page.open(dp)

            lst.controls.append(ft.Row([ft.ElevatedButton("CRIAR", on_click=lambda _: page.go("/builder"), expand=True), ft.ElevatedButton("IMPORTAR", on_click=open_premade, expand=True)]))

            for r in routines:
                def run(e, rt=r): active_workout["on"]=True; active_workout["routine"]=rt; active_workout["exercises"]=rt['exercises']; active_workout["accumulated_xp"]=0; active_workout["accumulated_gold"]=0; active_workout["session_logs"]=[]; update_ui(True)
                def dele(e, rid=r['id']): db.delete_routine(rid); update_ui(1)
                lst.controls.append(ft.Container(content=ft.ListTile(title=ft.Text(r['name'], font_family="RPG"), trailing=ft.Row([ft.IconButton("delete", on_click=dele), ft.Icon("play_arrow")], width=100), on_click=run), bgcolor=THEME["card_bg"]))
            return ft.Column([ft.Text("MEUS TREINOS", size=24, weight="bold", font_family="RPG"), lst], spacing=10, expand=True)

        # --- SUBSTITUA A FUNÇÃO render_workout_view POR ESTA ---
        # --- VERSÃO COM BOTTOM SHEET (CORRIGE O ERRO DE DIGITAÇÃO) ---
        # --- VERSÃO INFALÍVEL (Sem janelas, abre na própria lista) ---
        # --- VERSÃO FINAL: Inline + Histórico com Rolagem (Scroll) ---
        def render_workout_view():
            routine = active_workout["routine"]
            
            # --- 1. ÁREA DE HISTÓRICO (COM SCROLL LIMITADO) ---
            # Criamos uma coluna que permite rolagem
            logs_scroll_col = ft.Column(scroll="auto", expand=True, spacing=2)
            
            # Se tiver logs, popula a lista
            has_logs = False
            if active_workout.get("session_logs"):
                has_logs = True
                for log in reversed(active_workout["session_logs"]): # Mostra o mais recente no topo
                    logs_scroll_col.controls.append(ft.Text(f"✅ {log}", size=12, color="green", font_family="RPG"))
            else:
                logs_scroll_col.controls.append(ft.Text("Nenhuma série registrada ainda.", size=12, italic=True, color="grey"))

            # Container que limita o tamanho (O "Cercadinho")
            logs_container = ft.Container(
                content=ft.Column([
                    ft.Text("Histórico da Sessão:", size=12, color="white", weight="bold"),
                    ft.Container(content=logs_scroll_col, expand=True) # O conteúdo rola aqui dentro
                ]),
                height=120, # <--- AQUI ESTÁ A MÁGICA: Altura fixa!
                bgcolor="#1a1a1a",
                border=ft.border.all(1, "#333"),
                border_radius=5,
                padding=10,
                visible=has_logs # Só aparece se tiver logs (opcional, deixei True se quiser ver o título)
            )
            # Se quiser que apareça sempre (mesmo vazio), mude visible=has_logs para visible=True acima.

            # --- 2. LISTA DE EXERCÍCIOS ---
            ex_list_ui = ft.Column(scroll="auto", expand=True)

            for ex in active_workout["exercises"]:
                # Variáveis de apoio
                is_cardio = (x_target := ex['target']) == 'stamina'
                lbl1 = "Tempo (min)" if is_cardio else "Carga (kg)"
                lbl2 = "Dist (km)" if is_cardio else "Reps"

                # Campos de Input
                t_load = ft.TextField(label=lbl1, width=100, height=40, text_size=12, content_padding=10, text_align=ft.TextAlign.CENTER)
                t_reps = ft.TextField(label=lbl2, width=100, height=40, text_size=12, content_padding=10, text_align=ft.TextAlign.CENTER)
                
                # Área de Input (Inline)
                input_area = ft.Container(
                    visible=False, 
                    bgcolor="#222",
                    padding=10,
                    border_radius=5,
                    content=ft.Column([
                        ft.Row([t_load, t_reps], alignment="center"),
                        ft.ElevatedButton("SALVAR", bgcolor="green", color="white", width=200, height=30, 
                                          on_click=lambda e, x=ex, tl=t_load, tr=t_reps, ia=None: confirm_log(x, tl, tr, e.control.parent.parent)) 
                    ], horizontal_alignment="center")
                )
                
                def toggle_input(e, area=input_area):
                    area.visible = not area.visible
                    page.update()

                def confirm_log(x, v1_txt, v2_txt, area_ref):
                    if not v1_txt.value or not v2_txt.value:
                        show_snack("Preencha tudo!", "red"); return
                    try:
                        val1 = float(v1_txt.value.replace(",", "."))
                        val2 = float(v2_txt.value.replace(",", "."))
                        
                        xp, gold, skill = db.log_set(session["user_id"], x['id'], val1, val2)
                        
                        # Atualiza Log
                        log_str = f"{x['name']}: {val1} x {val2}"
                        if "session_logs" not in active_workout: active_workout["session_logs"] = []
                        active_workout["session_logs"].append(log_str)
                        
                        # Atualiza Hero
                        bonus = rpg_data['learning_rate'].get(skill, 1.0)
                        gain = int(10 * bonus)
                        hero = session["hero"]; hero[skill]['prog'] += gain
                        
                        if hero[skill]['prog'] >= 100: 
                            hero[skill]['prog']-=100; hero[skill]['lvl']+=1; 
                            show_snack(f"{skill.upper()} UP!", "purple"); play_sound("lvl")
                        
                        active_workout["accumulated_xp"] = active_workout.get("accumulated_xp", 0) + xp
                        active_workout["accumulated_gold"] = active_workout.get("accumulated_gold", 0) + gold
                        
                        db.salvar_progresso(session["user_id"], hero)
                        
                        # Limpa input e esconde
                        v1_txt.value = ""; v2_txt.value = ""
                        area_ref.visible = False 
                        
                        show_snack(f"Boa! +{gain}% {skill}", "green")
                        play_sound("coin")
                        
                        # Recarrega a tela (vai atualizar a lista de histórico lá em cima)
                        update_ui(force_workout_view=True)
                    except: show_snack("Erro! Use números.", "red")

                # Botão de histórico do exercício (antigo)
                def open_hist(e, xid=ex['id'], xname=ex['name']):
                    hist = db.get_exercise_history(session["user_id"], xid)
                    if not hist: show_snack("Sem dados.", "grey"); return
                    rows = ft.Column(scroll="auto", height=300)
                    for h in hist: rows.controls.append(ft.Text(f"{h['date'].split(' ')[0]}: {h['weight']}kg - {int(h['reps'])}reps", size=12))
                    # Usando Dialog seguro
                    dlg = ft.AlertDialog(title=ft.Text(xname), content=rows)
                    page.dialog = dlg; dlg.open=True; page.update()

                ex_list_ui.controls.append(ft.Column([
                    ft.ListTile(
                        title=ft.Text(ex['name']), 
                        leading=ft.Icon(ex['icon']),
                        trailing=ft.Row([
                            ft.IconButton("history", on_click=lambda e, eid=ex['id'], en=ex['name']: open_hist(e, eid, en)),
                            ft.IconButton("add_circle", icon_color=THEME["accent"], on_click=toggle_input)
                        ], width=100)
                    ),
                    input_area
                ], spacing=0))

            def finish_workout(e):
                hero = session["hero"]
                has_strength = any(ex['target'] in ['upper', 'lower'] for ex in active_workout["exercises"])
                allowed, reason = db.check_training_limit(session["user_id"], has_strength)
                if not allowed: show_snack(reason, "red"); active_workout["on"] = False; update_ui(0); return
                db.update_training_limit(session["user_id"], has_strength)
                
                total_xp = active_workout.get("accumulated_xp", 0) + 100
                total_gold = active_workout.get("accumulated_gold", 0) + 50
                hero['xp'] += total_xp; hero['gold'] += total_gold
                while hero['xp'] >= hero['xp_max']: hero['xp']-=hero['xp_max']; hero['level']+=1; hero['xp_max']=int(hero['xp_max']*1.2); show_snack("LEVEL UP!", "cyan"); play_sound("lvl")
                
                db.salvar_progresso(session["user_id"], hero)
                active_workout["on"] = False
                show_snack("Treino Finalizado!", "green"); update_ui(0)

            # Layout Principal da Tela de Treino
            return ft.Container(content=ft.Column([
                ft.Text(f"Treinando: {routine['name']}", size=24, weight="bold", color="red", font_family="RPG"),
                # Se tiver logs, mostra o container com altura fixa. Se não, mostra um divider simples.
                logs_container if active_workout.get("session_logs") else ft.Container(), 
                ft.Divider(),
                ex_list_ui, # Essa lista ocupa o resto da tela
                ft.ElevatedButton("FINALIZAR TREINO", bgcolor="green", color="white", width=300, on_click=finish_workout)
            ]), padding=20)

        def get_tower_page():
            try:
                boss, current_hp = db.get_boss_status(session["user_id"]); hp_percent = current_hp / boss['hp']; hp_color = "green" if hp_percent > 0.5 else "orange" if hp_percent > 0.2 else "red"
                def attack_click(e):
                    dmg, msg = db.attack_boss(session["user_id"])
                    if dmg > 0: play_sound("lvl"); show_snack(msg, "cyan")
                    else: show_snack("Treine mais para dar dano!", "red")
                    update_ui(2)
                boss_img_widget = get_asset_image(boss['img'], size=200)
                return ft.Column([ft.Text(f"TORRE DE FERRO - ANDAR {boss['lvl']}", size=24, weight="bold", font_family="RPG", color="red"), rpg_container(ft.Column([boss_img_widget, ft.Text(boss['name'], size=20, weight="bold", font_family="RPG"), ft.Text(boss['desc'], italic=True, size=12, color="grey"), ft.ProgressBar(value=hp_percent, color=hp_color, height=20), ft.Text(f"{int(current_hp)} / {boss['hp']} HP", size=14, weight="bold"), ft.ElevatedButton("ATACAR (USAR TREINO HOJE)", on_click=attack_click, bgcolor="red", color="white", width=250)], horizontal_alignment="center"), padding=20)], horizontal_alignment="center", spacing=20, expand=True)
            except Exception as e: print(f"ERRO TORRE: {e}"); return ft.Text(f"Erro ao carregar Torre: {e}", color="red")

        def get_grimoire_page():
            total_w, total_km = db.get_lifetime_stats(session["user_id"]); history_list = ft.Column(spacing=5, scroll="auto", expand=True); all_exs = db.get_all_exercises()
            for ex in all_exs:
                def open_hist(e, xid=ex['id'], xname=ex['name']):
                    hist = db.get_exercise_history(session["user_id"], xid)
                    if not hist: show_snack("Sem dados.", "grey"); return
                    rows = ft.Column(scroll="auto", height=300)
                    for h in hist: rows.controls.append(ft.Text(f"{h['date'].split(' ')[0]}: {h['weight']}kg x {h['reps']}", size=12))
                    dlg_h = ft.AlertDialog(title=ft.Text(f"Histórico: {xname}"), content=rows); page.dialog=dlg_h; dlg_h.open=True; page.update()
                history_list.controls.append(ft.Container(content=ft.Row([ft.Icon(ex['icon'], size=16, color="grey"), ft.Text(ex['name'], expand=True), ft.Icon("history", size=16, color=THEME["accent"])]), padding=10, bgcolor=THEME["card_bg"], border_radius=5, on_click=lambda e, eid=ex['id'], en=ex['name']: open_hist(e, eid, en)))
            return ft.Column([ft.Text("GRIMÓRIO DE FORÇA", size=24, weight="bold"), ft.Row([rpg_container(ft.Column([ft.Text(f"{int(total_w)} kg", size=24, color="cyan", weight="bold", font_family="RPG"), ft.Text("VOLUME TOTAL", size=10)], horizontal_alignment="center"), padding=15), rpg_container(ft.Column([ft.Text(f"{int(total_km)} km", size=24, color="green", weight="bold", font_family="RPG"), ft.Text("DISTÂNCIA", size=10)], horizontal_alignment="center"), padding=15)], alignment="center"), ft.Divider(), ft.Text("REGISTROS:", size=12, color="grey"), ft.Container(content=history_list, expand=True)], spacing=10, expand=True)

        def update_ui(target_index=None, force_workout_view=False):
            if session["user_id"]: session["hero"] = db.carregar_heroi(session["user_id"])
            hero_atual = session["hero"]
            if active_workout["on"] or force_workout_view: body_content.content = ft.Stack([ft.Image(src="/background.png", fit=ft.ImageFit.COVER, expand=True), ft.Container(bgcolor=THEME["bg_overlay"], expand=True), ft.Container(content=render_workout_view(), padding=10)], expand=True); nav.visible = False
            else:
                nav.visible = True; idx = target_index if target_index is not None else nav.selected_index
                content_widget = None
                try:
                    if idx == 0: content_widget = get_profile_page(hero_atual)
                    elif idx == 1: content_widget = get_training_page()
                    elif idx == 2: content_widget = get_tower_page()
                    elif idx == 3: content_widget = get_grimoire_page()
                    elif idx == 4: content_widget = get_shop_page(hero_atual)
                except Exception as ex: content_widget = ft.Text(f"Erro na aba {idx}: {ex}", color="red")
                body_content.content = ft.Stack([ft.Image(src="/background.png", fit=ft.ImageFit.COVER, expand=True), ft.Container(bgcolor=THEME["bg_overlay"], expand=True), ft.Container(content=content_widget, padding=10)], expand=True)
                nav.selected_index = idx
            page.update()

        nav = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon="person", label="Perfil"), 
                ft.NavigationBarDestination(icon="fitness_center", label="Treinar"), 
                ft.NavigationBarDestination(icon="castle", label="Torre"), 
                ft.NavigationBarDestination(icon="menu_book", label="Grimório"), 
                ft.NavigationBarDestination(icon="shopping_bag", label="Loja")
            ], 
            on_change=lambda e: update_ui(), 
            bgcolor="#111", 
            indicator_color=THEME["primary"]
        )
        update_ui(0)
        return ft.View("/game", [ft.AppBar(title=ft.Text("Iron RPG", font_family="RPG", size=24), bgcolor="#111", actions=[ft.IconButton("logout", on_click=lambda e: page.go("/"))]), body_content, nav], padding=0)

    # --- TELA DE CRIAÇÃO DE FICHA (Rota Dedicada) ---
    def view_builder():
        name_tf = ft.TextField(label="Nome da Ficha", border_color="#FFD700")
        selected_ids = []
        tabs = ft.Tabs(selected_index=0, expand=True); cats = ["Peito", "Costas", "Ombro", "Braço", "Perna", "Cardio", "Outros"]
        all_exs = db.get_all_exercises()
        for c in cats:
            cl = ft.Column(scroll="auto", spacing=5)
            for ex in all_exs:
                if ex['category'] == c:
                    chk = ft.Checkbox(label=ex['name'], on_change=lambda e, x=ex['id']: selected_ids.append(x) if e.control.value else selected_ids.remove(x))
                    cl.controls.append(chk)
            tabs.tabs.append(ft.Tab(text=c, content=ft.Container(content=cl, padding=10, alignment=ft.alignment.top_left)))
        def save_routine(e):
            if not name_tf.value: show_snack("Dê um nome para a ficha!", "red"); return
            if not selected_ids: show_snack("Selecione pelo menos 1 exercício!", "red"); return
            db.create_routine(session["user_id"], name_tf.value, selected_ids)
            show_snack("Ficha Criada!", "green"); page.go("/game")
        return ft.View("/builder", [ft.AppBar(title=ft.Text("Montar Nova Ficha"), bgcolor="#111"), ft.Container(content=ft.Column([ft.Text("1. Escolha o Nome", color="grey"), name_tf, ft.Divider(), ft.Text("2. Selecione os Exercícios", color="grey"), ft.Container(content=tabs, expand=True), ft.ElevatedButton("SALVAR FICHA", on_click=save_routine, bgcolor="#8a0303", color="white", width=200)], expand=True), padding=20, expand=True)], bgcolor="#121212", padding=0)

    def route_change(route):
        page.views.clear()
        if page.route == "/": page.views.append(view_login())
        elif page.route == "/register": page.views.append(view_register())
        elif page.route == "/create_char": page.views.append(view_create_char())
        elif page.route == "/builder": page.views.append(view_builder())
        elif page.route == "/game": 
            if session["hero"]: page.views.append(view_game())
            else: page.go("/")
        page.update()

    page.on_route_change = route_change
    page.go("/")

ft.app(target=main, assets_dir="assets")