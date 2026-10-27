class CoreWarsArena:

  def __init__(self, size=10):
    self.size = size
    self.memory = [["DAT", 0, 0] for _ in range(size)]
    self.processes = []  

  def add_program(self, player_id, start_address, program):
    """Wgrywa program do pamięci i rejestruje jego pierwszy proces."""
    for i, instruction in enumerate(program):
      addr = (start_address + i) % self.size
      self.memory[addr] = list(instruction)
    # Każdy proces to słownik zawierający ID gracza oraz jego wskaźnik IP
    self.processes.append({"player_id": player_id, "ip": start_address})

  def step(self):
    surviving_processes = []
    new_processes = []

    for proc in self.processes:
      player_id = proc["player_id"]
      ip = proc["ip"]
      op, a, b = self.memory[ip]

      # Warunek śmierci: wejście na DAT kończy dany proces
      if op == "DAT":
        print(f"\n💥 Proces gracza '{player_id}' (IP: {ip}) wszedł na DAT i zginął!")
        continue  # Proces ginie i nie trafia do żywych

      next_ip = (ip + 1) % self.size

      if op == "MOV":
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

      elif op == "JMP":
        next_ip = (ip + a) % self.size

      elif op == "JMZ":
        target_addr = (ip + b) % self.size
        # Skacz, jeśli trzeci element (b-pole) komórki docelowej wynosi 0
        if self.memory[target_addr][2] == 0:
          next_ip = (ip + a) % self.size

      elif op == "DJN":
        target_addr = (ip + b) % self.size
        # Zmniejsz wartość w komórce docelowej o 1, a jeśli nie jest zerem, skacz
        self.memory[target_addr][2] = (
            self.memory[target_addr][2] - 1
        ) % self.size
        if self.memory[target_addr][2] != 0:
          next_ip = (ip + a) % self.size

      elif op == "SPL":
        # Rozgałęzienie: tworzy nowy proces pod adresem (ip + a)
        spawn_addr = (ip + a) % self.size
        new_processes.append({"player_id": player_id, "ip": spawn_addr})

      # Aktualizujemy pozycję bieżącego procesu i zapisujemy do listy żywych
      proc["ip"] = next_ip
      surviving_processes.append(proc)

    # Łączymy istniejące żywe procesy z nowo utworzonymi przez SPL
    self.processes = surviving_processes + new_processes

  def dump(self):
    for idx, cell in enumerate(self.memory):
      # Zbieramy wszystkie IP, które aktualnie wskazują na tę komórkę
      active_ips = [
          p["player_id"] for p in self.processes if p["ip"] == idx
      ]
      pointer_str = f" <-- IP: {', '.join(active_ips)}" if active_ips else ""
      print(f"[{idx:2d}] {cell}{pointer_str}")
    print("-" * 60)


# =====================================================================
# 1. SEKCJA DEFINICJI PROGRAMÓW (Tutaj tworzysz własny kod)
# =====================================================================

# Przykładowy program 1: Bombowiec
program_1 = [["MOV", 3, 5], ["ADD", 1, -1], ["JMP", -2, 0], ["DAT", 0, 0]]

# Przykładowy program 2: IMP
program_2 = [["MOV", 0, -1]]

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
    ["JMZ", 4, 8],   # 0: Radar (ip = 0). Cel: 0 + 8 = adres 8
    ["MOV", 6, 7],   # 1: Atak (ip = 1). Źródło: 1 + 5 = 6. Cel: 1 + 6 = adres 7!
    ["ADD", 1, -1],  # 2: Zwiększ pole B w linii 1
    ["JMP", -2, 0],  # 3: Wróć do linii 0 (3 + (-2) = 1) 
    ["ADD", 1, -4],  # 4: Zwiększ dystans radaru w linii 0
    ["ADD", 1, -4],  # 5: Zwiększ dystans ataku w linii 1
    ["JMP", -6,0],  # 6: Powrót na początek pętli
    ["DAT", 0, 0]    # 7: Magazyn amunicji (źródło bomby)
]

# =====================================================================
# 2. SEKCJA IMPLEMENTACJI DO GŁÓWNEJ FUNKCJI (Wczytywanie na arenę)
# =====================================================================

sim = CoreWarsArena(size=30)

# Wgrywamy program 1 pod adresem 10
# sim.add_program("BOMBER 1", start_address=10, program=program_1)

# Wgrywamy program 2 pod adresem 10
# sim.add_program("IMP", start_address=10, program=program_2)

# Wgrywamy program 3 pod adresem 20
# sim.add_program("BOMBER 2", start_address=20, program=program_3)

# Wgrywamy program 4 pod adresem 10
sim.add_program("SCANNER", start_address=10, program=program_4)

# Wgrywamy program 5 pod adresem 0
sim.add_program("SCA_BOMB", start_address=0, program=program_5)

# =====================================================================
# 3. URUCHOMIENIE SYMULACJI
# =====================================================================

print("Stan początkowy:")
sim.dump()

# Symulacja krok po kroku
for krok in range(1, 100):
  print(f"Krok {krok}:")
  input("Naciśniej ENTER aby kontynuować !!!" + "\n")
  sim.step()
  sim.dump()
  
  # Sprawdzamy, jacy gracze nadal mają aktywne procesy w grze
  active_players = set(p["player_id"] for p in sim.processes)
  if len(active_players) <= 1:
    break

active_players = set(p["player_id"] for p in sim.processes)
if len(active_players) == 1:
  zwycięzca = list(active_players)[0]
  print(f"🏆 KONIEC GRY! Zwyciężył: {zwycięzca}")
else:
  print("🤝 Symulacja zakończona po wyznaczonej liczbie kroków.")
