### CREDITS TO https://github.com/vexsyx/OysterDetector/blob/main/data/aura-data.json FOR THE AURA DATA USED IN THIS PROJECT ###

import json
import math
import random

# basic is 1-999, epic is 1000-9999 etc
# reverse the rank order so higher tiers are evaluated before lower tiers
RANK_BOUNDARIES = {
    "basic"         : 999,
    "epic"          : 9999,
    "unique"        : 99998,
    "legendary"     : 999998,
    "mythic"        : 9999999,
    "exalted"       : 99999998,
    "glorious"      : 999999998,
    "transcendent"  : 7500000000,
    "dimensional"   : 12500000000
}

# load auras
with open("macro/src/core/auras.json", "r", encoding="utf-8") as f:
    auras_dict = json.load(f)

# filter out all unobtainable auras
auras_dict = [
    aura for aura in auras_dict
    if aura["properties"].get("rank") != "unobtainable"
    and aura["properties"].get("unobtainable") is None
    and aura["properties"].get("event_override") is None
    and aura["properties"].get("rarity_override") is None
]

class Aura:

    def __init__(self, aura_dict: dict):

        properties: dict = aura_dict["properties"]

        self.id: str = aura_dict["identifier"]
        self.name: str = properties["name"]
        self.base_chance: int = properties["base_chance"]
        self.unobtainable: bool = properties.get("unobtainable", False)

        if properties.get("rank") is not None:
            self.rank = properties["rank"]
        else:
            for rank, rarity in RANK_BOUNDARIES.items():
                if self.base_chance < rarity:
                    self.rank = rank
                    break

        self.biome_amplifiers: dict[str, int] = {k.lower() : v for k, v in properties["biome_amplifiers"].items()}
        self.biome_whitelist = properties.get("biome_whitelist", [])

    def __str__(self) -> str:
        return f"{self.name} [1 in {self.base_chance}]"

auras = [Aura(aura) for aura in auras_dict]

BIOMES = {'graveyard', 'dreamspace', 'hell', 'null', 'heaven', 
          'corruption', 'night', 'glitched', 'sand storm', 'windy', 
          'rainy', 'starfall', 'pumpkin moon', 'blazing sun', 'cyberspace', 
          'day', 'singularity', 'snowy', 'blood rain', 'none'}
RARE_BIOMES = {'graveyard', 'dreamspace', 'glitched', 'pumpkin moon', 'blazing sun',
               'singularity', 'blood rain'}

def _prepare_auras(biome: str) -> list[Aura]:
    auras_copy = auras.copy()

    # sort by luck
    auras_copy.sort(key=lambda a: 
               a.base_chance * a.biome_amplifiers.get(biome, 1),
               reverse=True)

    return [a for a in auras_copy if not (a.biome_whitelist and biome not in a.biome_whitelist)]

def _get_rarity(aura: Aura, luck: float, biome: str) -> int:
    rarity = aura.base_chance * aura.biome_amplifiers.get(biome, 1)
    return math.ceil(rarity / luck)

def simulate_roll(auras: list[Aura], luck: float, biome: str) -> Aura:
    """
    Simulates a roll according to the Sols RNG algorithm.

    Returns the aura rolled.
    """

    for aura in auras:

        if random.randint(1, _get_rarity(aura, luck, biome)) == 1:
            return aura

    return auras[-1]

def get_rank_odds(auras: list[Aura], luck: float, biome: str) -> dict[str, float]:
    """
    Determines the probability of rolling each rank in the supplied aura order.
    """

    if not auras:
        raise ValueError("At least one aura is required to calculate rank odds.")
    if not math.isfinite(luck) or luck <= 0:
        raise ValueError("Luck must be a finite number greater than zero.")

    rank_odds = dict.fromkeys(dict.fromkeys(aura.rank for aura in auras), 0.0)
    remaining_probability = 1.0
    index = 0

    while index < len(auras):
        rank = auras[index].rank
        rank_failure_probability = 1.0

        while index < len(auras) and auras[index].rank == rank:
            if index == len(auras) - 1:
                # simulate_roll returns the final aura if all checks fail.
                aura_failure_probability = 0.0
            else:
                aura_probability = 1 / _get_rarity(auras[index], luck, biome)
                aura_failure_probability = 1 - aura_probability

            rank_failure_probability *= aura_failure_probability
            index += 1

        rank_odds[rank] += remaining_probability * (1 - rank_failure_probability)
        remaining_probability *= rank_failure_probability

    return rank_odds

def main():

    luck = float(input("Enter your luck : "))

    while (biome := input("Enter your biome : ").lower()) not in BIOMES:
        print(f"'{biome}' is not a biome. Choose from : {", ".join(BIOMES)}.")

    prepared_auras = _prepare_auras(biome)

    print("Rank odds:")
    for rank, probability in get_rank_odds(prepared_auras, luck, biome).items():
        print(f"{rank}: {probability:.8%}")

if __name__ == '__main__':
    main()