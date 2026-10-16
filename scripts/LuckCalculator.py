### CREDITS TO https://github.com/vexsyx/OysterDetector/blob/main/data/aura-data.json FOR THE AURA DATA USED IN THIS PROJECT ###

import json
import math
import random

# basic is 1-999, epic is 1000-9999 etc
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
        self.biome_whitelist = [biome.lower() for biome in properties.get("biome_whitelist", [])]
        self.biome_blacklist = [biome.lower() for biome in properties.get("biome_blacklist", [])]

    def __str__(self) -> str:
        return f"{self.name} [1 in {self.base_chance}]"

auras = [Aura(aura) for aura in auras_dict]

BIOMES = {'graveyard', 'dreamspace', 'hell', 'null', 'heaven', 
          'corruption', 'night', 'glitched', 'sand storm', 'windy', 
          'rainy', 'starfall', 'pumpkin moon', 'blazing sun', 'cyberspace', 
          'day', 'singularity', 'snowy', 'blood rain', 'none'}
RARE_BIOMES = {'graveyard', 'dreamspace', 'glitched', 'pumpkin moon', 'blazing sun',
               'singularity', 'blood rain'}
RUNE_BIOMES = {'hell', 'null', 'heaven', 'corruption', 'sand storm',
               'snowy', 'rainy', 'starfall'}

def _get_biome_amplifier(aura: Aura, biome: str, ROE: bool) -> int:
    if ROE:
        return max(
            (amplifier for name, amplifier in aura.biome_amplifiers.items()
             if name in RUNE_BIOMES),
            default=1
        )
    return aura.biome_amplifiers.get(biome, 1)

def _prepare_auras(biome: str, ROE: bool) -> list[Aura]:
    auras_copy = auras.copy()

    # sort by luck
    auras_copy.sort(
        key=lambda a:
        # include biome multiplier
        a.base_chance / _get_biome_amplifier(a, biome, ROE),
        reverse=True
    )

    # remove auras that do not pass the biome whitelist or blacklist
    return [
        aura for aura in auras_copy
        if (
            not aura.biome_whitelist
            or biome in aura.biome_whitelist
        )
        and (biome not in aura.biome_blacklist)
    ]

def _get_rarity(aura: Aura, luck: float, biome: str, ROE: bool) -> int:
    rarity = aura.base_chance / _get_biome_amplifier(aura, biome, ROE)
    return math.ceil(rarity / luck)

def simulate_roll(auras: list[Aura], luck: float, biome: str, ROE: bool) -> Aura:
    """
    Simulates a roll according to the Sols RNG algorithm.

    Returns the aura rolled.
    """

    for aura in auras:

        if random.randint(1, _get_rarity(aura, luck, biome, ROE)) == 1:
            return aura

    return auras[-1]

def get_rank_odds(auras: list[Aura], luck: float, biome: str, ROE: bool) -> dict[str, float]:
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
                aura_probability = 1 / _get_rarity(auras[index], luck, biome, ROE)
                aura_failure_probability = 1 - aura_probability

            rank_failure_probability *= aura_failure_probability
            index += 1

        rank_odds[rank] += remaining_probability * (1 - rank_failure_probability)
        remaining_probability *= rank_failure_probability

    return rank_odds

def main():

    luck = float(input("Enter your luck :  "))
    ROE = input("Rune of Everything? (y/n) ").lower() == 'y'

    while (biome := input("Enter your biome : ").lower()) not in BIOMES:
        print(f"'{biome}' is not a biome. Choose from : {", ".join(BIOMES)}.")

    prepared_auras = _prepare_auras(biome, ROE)

    rank_odds = get_rank_odds(prepared_auras, luck, biome, ROE)
    for rank, probability in sorted(rank_odds.items(), key=lambda x: x[1], reverse=True):
        print(f"{rank.capitalize().ljust(20)} {probability:.8%} (every {round(1 / probability, 1) if probability != 0 else 'NaN'} rolls)")

if __name__ == '__main__':
    main()