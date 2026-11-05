# program zapisuje wyniku turnieju do  pliku csv
# TODO losowanie adresu rozpoczęcia gry
# TODO podliczenie wyników turnieju

import  pandas as pd

class CoreWarsArena:

  def __init__(self, size=8000):
    self.size = size
    self.memory = [["DAT", 0, 0] for _ in range(size)]
    self.processes = []

  def add_program(self, player_id, start_address, program):
    """Wgrywa program do pamięci i rejestruje jego pierwszy proces."""
    for i, instruction in enumerate(program):
      addr = (start_address + i) % self.size
      self.memory[addr] = list(instruction)
    self.processes.append({"player_id": player_id, "ip": start_address})

  def step(self):
    surviving_processes = []
    new_processes = []

    for proc in self.processes:
      player_id = proc["player_id"]
      ip = proc["ip"]
      op, a, b = self.memory[ip]

      # Warunek śmierci: wejście na DAT kończy dany proces
      if op == "DAT":
        # W dużych symulacjach z 8000 komórek można odkomentować poniższy print,
        # żeby widzieć każdy zgon, ale przy 6 graczach może spamować w konsoli:
        # print(f"\n💥 Proces gracza '{player_id}' (IP: {ip}) wszedł na DAT i zginął!")
        continue  # Proces ginie i nie trafia do żywych

      next_ip = (ip + 1) % self.size

      if op == "NOP":
        pass

      elif op == "MOV":
        src = (ip + a) % self.size
        dst = (ip + b) % self.size
        self.memory[dst] = list(self.memory[src])

      elif op == "ADD":
        target_addr = (ip + b) % self.size
        self.memory[target_addr][2] = (
            self.memory[target_addr][2] + a
        ) % self.size

      elif op == "SUB":
        target_addr = (ip + b) % self.size
        self.memory[target_addr][2] = (
            self.memory[target_addr][2] - a
        ) % self.size

      elif op == "MUL":
        target_addr = (ip + b) % self.size
        self.memory[target_addr][2] = (
            self.memory[target_addr][2] * a
        ) % self.size

      elif op == "DIV":
        target_addr = (ip + b) % self.size
        if a == 0:
          continue
        self.memory[target_addr][2] = (
            self.memory[target_addr][2] // a
        ) % self.size

      elif op == "MOD":
        target_addr = (ip + b) % self.size
        if a == 0:
          continue
        self.memory[target_addr][2] = (
            self.memory[target_addr][2] % a
        ) % self.size

      elif op == "JMP":
        next_ip = (ip + a) % self.size

      elif op == "JMZ":
        target_addr = (ip + b) % self.size
        if self.memory[target_addr][2] == 0:
          next_ip = (ip + a) % self.size
          
      elif op == "JMN":
        target_addr = (ip + b) % self.size
        if self.memory[target_addr][2] != 0:
          next_ip = (ip + a) % self.size

      elif op == "DJN":
        target_addr = (ip + b) % self.size
        self.memory[target_addr][2] = (
            self.memory[target_addr][2] - 1
        ) % self.size
        if self.memory[target_addr][2] != 0:
          next_ip = (ip + a) % self.size

      elif op == "SPL":
        spawn_addr = (ip + a) % self.size
        new_processes.append({"player_id": player_id, "ip": spawn_addr})
        
      elif op == "SEQ" or op == "CMP":
        src_addr = (ip + a) % self.size
        target_addr = (ip + b) % self.size
        if self.memory[src_addr] == self.memory[target_addr]:
          next_ip = (ip + 2) % self.size

      elif op == "SNE" or op == "CPN":
        src_addr = (ip + a) % self.size
        target_addr = (ip + b) % self.size
        if self.memory[src_addr] != self.memory[target_addr]:
          next_ip = (ip + 2) % self.size

      elif op == "SLT":
        target_addr = (ip + b) % self.size
        if a < self.memory[target_addr][2]:
          next_ip = (ip + 2) % self.size

      proc["ip"] = next_ip
      surviving_processes.append(proc)

    self.processes = surviving_processes + new_processes

# =====================================================================
# 1. SEKCJA DEFINICJI PROGRAMÓW
# =====================================================================

# Przykładowy program 1: Bombowiec
program_1 = [["MOV", 3, 1750], ["ADD", 1, -1], ["JMP", -2, 0], ["DAT", 0, 0]]

# Przykładowy program 2: IMP
program_2 = [["MOV", 0, 1]]

# Przykładowy program 3: Bombowiec
program_3 = [["MOV", 3, -2], ["SUB", 1, -1], ["JMP", -2, 0], ["DAT", 0, 0]]

# Przykładowy program 4: scanner
program_4 = [
    ["JMZ", 2, 8],   # 0: Radar (ip = 0). Cel: 0 + 6 = adres 6
    ["MOV", 4, 2200],   # 1: Atak (ip = 1). Źródło: 1 + 4 = 5. Cel: 1 + 5 = adres 6!
    ["ADD", 1, -2],  # 2: Zwiększ dystans radaru w linii 0
    ["ADD", 1, -2],  # 3: Zwiększ dystans ataku w linii 1
    ["JMP", -4, 0],  # 4: Powrót na początek pętli
    ["DAT", 0, 0]    # 5: Magazyn amunicji (źródło bomby)
]

# Przykładowy program 5: scanner bomber
program_5 = [
    ["JMZ", 4, 10],   # 0: Radar (ip = 0). Cel: 0 + 8 = adres 8
    ["MOV", 6, 3000],   # 1: Atak (ip = 1). Źródło: 1 + 5 = 6. Cel: 1 + 6 = adres 7!
    ["ADD", 10, -1],  # 2: Zwiększ pole B w linii 1
    ["JMP", -2, 0],  # 3: Wróć do linii 0 (3 + (-2) = 1) 
    ["ADD", 1, -4],  # 4: Zwiększ dystans radaru w linii 0
    ["ADD", 1, -4],  # 5: Zwiększ dystans ataku w linii 1
    ["JMP", -6,0],  # 6: Powrót na początek pętli
    ["DAT", 0, 0]    # 7: Magazyn amunicji (źródło bomby)
]

# Przykładowy program 6: spl
program_6 = [
    ["SPL", 3, 0],   # 0: Stwórz nowy proces pod adresem (ip + 3) i biegnij dalej
    ["MOV", 2, 5500],   # 1: Kopiuj kod w bezpieczne miejsce w pamięci
    ["JMP", -2, 0],  # 2: Wróć do góry i powtórz
    ["DAT", 0, 0]    # 3: Obszar danych / cel replikacji
]

# Przykładowy program 7: spl_2
program_7 = [
    ["SPL", 3, 0],   # 0: Tworzy nowy wątek (skierowany na linię 3)
    ["ADD", 1, 2],   # 1: Wątek A: modyfikuje komórkę danych
    ["JMP", -2, 0],  # 2: Wątek A: wraca do linii 1
    ["MOV", 2, 2000],   # 3: Wątek B: wykonuje akcję kopiowania
    ["JMP", -1, 0],
    ["DAT", 0, 0]
]

# Przykładowy program 8: spl_3
program_8 = [
    ["SPL", 4, 0],
    ["MOV", 10, 1000],
    ["ADD", 1, -1],
    ["JMP", -2, 0],
    ["SPL", 4, 0],
    ["MOV", 6, 3000],
    ["ADD", 1, -1],
    ["JMP", -2, 0],
    ["MOV", 3, 5000],
    ["ADD", 1, -1],
    ["JMP", -2, 0],
    ["DAT", 0, 0],
]

# =====================================================================
# 2. SEKCJA WCZYTYWANIA PROGRAMÓW NA ARENĘ i URUCHOMIENIA TURNIEJU
# =====================================================================

rezultat_turnieju = []
rundy = int(input(f"Symulacja turnieju uruchomiona !!! Wpisz liczbę rund do  rozegrania: "))
for runda in range(rundy):
  arena_size = 8000
  sim = CoreWarsArena(size=arena_size)

  # Wgrywamy program 1
  sim.add_program("BOMBER 1", start_address=600, program=program_1)

  # Wgrywamy program 2
  # sim.add_program("IMP", start_address=60, program=program_2)

  # Wgrywamy program 3
  sim.add_program("BOMBER 2", start_address=500, program=program_3)

  # Wgrywamy program 4
  sim.add_program("SCANNER", start_address=2000, program=program_4)

  # Wgrywamy program 5
  sim.add_program("SCA_BOMB", start_address=4780, program=program_5)

  # Wgrywamy program 6
  sim.add_program("SPL", start_address=400, program=program_6)

  # Wgrywamy program 7
  sim.add_program("SPL_2", start_address=5500, program=program_7)

  # Wgrywamy program 8
  sim.add_program("SPL_3", start_address=7300, program=program_8)

# =====================================================================
# 3. URUCHOMIENIE SYMULACJI
# =====================================================================
  print(f"Runda {runda + 1} symulacji turnieju uruchomiona na arenie o rozmiarze {arena_size} komórek dla {len(sim.processes)} graczy.\n")
  max_steps = 20000
  winning_step = max_steps  # Domyślnie ustawiamy na max, jeśli nikt nie wyeliminuje rywali przed czasem

  for krok in range(1, max_steps + 1):
    sim.step()
  
    active_players = set(p["player_id"] for p in sim.processes)
    if len(active_players) <= 1:
      winning_step = krok
      break
  
    if krok % 1000 == 0:
      print(f"Krok {krok}: W grze pozostaje {len(active_players)} graczy: {list(active_players)}")

# --- PODSUMOWANIE KOŃCOWE ---
  active_processes_final = sim.processes
  surviving_players = list(set(p["player_id"] for p in active_processes_final))

  print("\n" + "="*50)
  if len(surviving_players) == 1:
    print(f"🏆 KONIEC GRY w kroku {winning_step}! Zwyciężył jedyny ocalały: {surviving_players[0]}")
    rezultat_turnieju.append({
      "runda": runda + 1,
      "wygrany": surviving_players[0],
      "krok": krok,
      "status": "zwycięstwo",
      "punkty": 3
    })
  elif len(surviving_players) > 1:
    print(f"🤝 Symulacja zakończona po osiągnięciu limitu kroków ({max_steps}) w kroku {winning_step}.")
    print(f"👑 Ocalałe programy, które dotrwały do końca ({len(surviving_players)}):")
    for player in surviving_players:
       proc_count = sum(1 for p in active_processes_final if p["player_id"] == player)
       print(f"   - {player} (aktywne procesy: {proc_count})")
  else:
    print(f"💀 Wszyscy zginęli w kroku {winning_step}! Remis (brak żywych procesów).")
  print("="*50)
  # print(rezultat_turnieju)
for wynik_meczu in rezultat_turnieju:
  print(wynik_meczu)

# --- Tworzenie DataFrame---
ostateczny_rezultat = pd.DataFrame(rezultat_turnieju)
print(ostateczny_rezultat)

# --- Zapis rezultatu turnieju na dysk ---
ostateczny_rezultat.to_csv("ostateczny_rezultat.csv", index=False, encoding="utf-8")
