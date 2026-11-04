class CoreWarsArena:

  def __init__(self, size=37):
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
        print(f"\n💥 Proces gracza '{player_id}' (IP: {ip}) wszedł na DAT i zginął!")
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
          print(f"\n💥 Proces gracza '{player_id}' (IP: {ip}) wykonał DZIELENIE PRZEZ ZERO i zginął!")
          continue
        self.memory[target_addr][2] = (
            self.memory[target_addr][2] // a
        ) % self.size

      elif op == "MOD":
        target_addr = (ip + b) % self.size
        if a == 0:
          print(f"\n💥 Proces gracza '{player_id}' (IP: {ip}) wykonał MODULO PRZEZ ZERO i zginął!")
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

      elif op == "SPL" or op == "PIN":
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

  def dump(self):
    for idx, cell in enumerate(self.memory):
      active_ips = [
          p["player_id"] for p in self.processes if p["ip"] == idx
      ]
      pointer_str = f" <-- IP: {', '.join(active_ips)}" if active_ips else ""
      # print(f"[{idx:2d}] {cell}{pointer_str}")
    # print("-" * 60)


# =====================================================================
# 1. SEKCJA DEFINICJI PROGRAMÓW
# =====================================================================

# Przykładowy program 1: Bombowiec
program_1 = [["MOV", 3, 5], ["ADD", 1, -1], ["JMP", -2, 0], ["DAT", 0, 0]]

# Przykładowy program 2: IMP
program_2 = [["MOV", 0, 1]]

# Przykładowy program 3: Bombowiec
program_3 = [["MOV", 3, -2], ["SUB", 1, -1], ["JMP", -2, 0], ["DAT", 0, 0]]

# Przykładowy program 4: scanner
program_4 = [
    ["JMZ", 2, 8],   # 0: Radar (ip = 0). Cel: 0 + 6 = adres 6
    ["MOV", 4, 7],   # 1: Atak (ip = 1). Źródło: 1 + 4 = 5. Cel: 1 + 5 = adres 6!
    ["ADD", 1, -2],  # 2: Zwiększ dystans radaru w linii 0
    ["ADD", 1, -2],  # 3: Zwiększ dystans ataku w linii 1
    ["JMP", -4, 0],  # 4: Powrót na początek pętli
    ["DAT", 0, 0]    # 5: Magazyn amunicji (źródło bomby)
]

# Przykładowy program 5: scanner bomber
program_5 = [
    ["JMZ", 4, 10],   # 0: Radar (ip = 0). Cel: 0 + 8 = adres 8
    ["MOV", 6, 9],   # 1: Atak (ip = 1). Źródło: 1 + 5 = 6. Cel: 1 + 6 = adres 7!
    ["ADD", 1, -1],  # 2: Zwiększ pole B w linii 1
    ["JMP", -2, 0],  # 3: Wróć do linii 0 (3 + (-2) = 1) 
    ["ADD", 1, -4],  # 4: Zwiększ dystans radaru w linii 0
    ["ADD", 1, -4],  # 5: Zwiększ dystans ataku w linii 1
    ["JMP", -6,0],  # 6: Powrót na początek pętli
    ["DAT", 0, 0]    # 7: Magazyn amunicji (źródło bomby)
]

# Przykładowy program 6: spl
program_6 = [
    ["SPL", 3, 0],   # 0: Stwórz nowy proces pod adresem (ip + 3) i biegnij dalej
    ["MOV", 2, 5],   # 1: Kopiuj kod w bezpieczne miejsce w pamięci
    ["JMP", -2, 0],  # 2: Wróć do góry i powtórz
    ["DAT", 0, 0]    # 3: Obszar danych / cel replikacji
]

# Przykładowy program 7: spl_2
program_7 = [
    ["SPL", 3, 0],   # 0: Tworzy nowy wątek (skierowany na linię 3)
    ["ADD", 1, 2],   # 1: Wątek A: modyfikuje komórkę danych
    ["JMP", -2, 0],  # 2: Wątek A: wraca do linii 1
    ["MOV", 2, 3],   # 3: Wątek B: wykonuje akcję kopiowania
    ["JMP", -1, 0],  # 4: Wątek B: wraca do linii 3
    ["DAT", 0, 0]    # 5: Magazyn danych / komórka robocza
]

# Przykładowy program 8: spl_3
program_8 = [
    ["SPL", 4, 0],
    ["MOV", 10, 12],
    ["ADD", 1, -1],
    ["JMP", -2, 0],
    ["SPL", 4, 0],
    ["MOV", 6, 18],
    ["ADD", 1, -1],
    ["JMP", -2, 0],
    ["MOV", 3, 24],
    ["ADD", 1, -1],
    ["JMP", -2, 0],
    ["DAT", 0, 0],
]

# =====================================================================
# 2. SEKCJA WCZYTYWANIA PROGRAMÓW NA ARENĘ
# =====================================================================

sim = CoreWarsArena(size=8000)

# Wgrywamy program 1 pod adresem 9
sim.add_program("BOMBER 1", start_address=0, program=program_1)

# Wgrywamy program 2 pod adresem 7
# sim.add_program("IMP", start_address=60, program=program_2)

# Wgrywamy program 3 pod adresem 25
# sim.add_program("BOMBER 2", start_address=160, program=program_3)

# Wgrywamy program 4 pod adresem 0
sim.add_program("SCANNER", start_address=2000, program=program_4)

# Wgrywamy program 5 pod adresem 0
sim.add_program("SCA_BOMB", start_address=3500, program=program_5)

# Wgrywamy program 6 pod adresem 0
sim.add_program("SPL", start_address=4250, program=program_6)

# Wgrywamy program 7 pod adresem 0
sim.add_program("SPL_2", start_address=5500, program=program_7)

# Wgrywamy program 8 pod adresem 0
sim.add_program("SPL_3", start_address=7000, program=program_8)

# Wgrywamy program 2 pod adresem 7
# sim.add_program("IMP_2", start_address=14, program=program_2)


# =====================================================================
# 3. URUCHOMIENIE SYMULACJI
# =====================================================================

print("Stan początkowy:")
sim.dump()

# Symulacja krok po kroku
for krok in range(1, 100):
  # input("Naciśnij ENTER aby kontynuować !!!")
  # print(f"Krok {krok}:")
  sim.step()
  sim.dump()
  
  # Sprawdzamy, jacy gracze nadal mają aktywne procesy w grze
  active_players = set(p["player_id"] for p in sim.processes)
  if len(active_players) <= 1:
    break

active_players = set(p["player_id"] for p in sim.processes)
if len(active_players) == 1:
  zwycięzca = list(active_players)[0]
  print(f"🏆 KONIEC GRY! Zwyciężył: {zwycięzca}")
else:
  print("🤝 Symulacja zakończona po wyznaczonej liczbie kroków.")