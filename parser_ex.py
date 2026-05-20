import re

# 1. Regex de structure globale
# ^connection:\s* -> Début de ligne + espace(s) optionnel(s)
# ([^\s\-]+)         -> Groupe 1 (Zone 1) : tout sauf un espace ou un tiret
# -                  -> Le tiret séparateur
# ([^\s\-]+)         -> Groupe 2 (Zone 2) : tout sauf un espace ou un tiret
# (?:\s+\[(.*?)\])?  -> Groupe 3 (Métadonnées) : Optionnel (?), cherche "[...]" et capture le contenu (.*?)
# \s*$               -> Fin de ligne (ignore les espaces finaux)
CONNECTION_PATTERN = re.compile(r"^connection:\s*([^\s\-]+)-([^\s\-]+)(?:\s+\[(.*?)\])?\s*$")

# 2. Regex d'extraction des métadonnées
# ([a-zA-Z_]+)       -> Clé : lettres et underscores
# =                  -> Séparateur
# ([a-zA-Z0-9_]+)    -> Valeur : alphanumérique et underscores
METADATA_PATTERN = re.compile(r"([a-zA-Z_]+)=([a-zA-Z0-9_]+)")

def parse_connection(line: str) -> dict:
    """
    Extrait les informations d'une ligne de connexion.
    Ex: 'connection: hub-roof1 [max_link_capacity=2 color=red]'
    """
    # On supprime les commentaires éventuels avant l'analyse
    clean_line = line.split('#')[0].strip()

    if not clean_line:
        return {} # Ligne vide ou juste un commentaire

    match = CONNECTION_PATTERN.match(clean_line)

    # Validation stricte : si ça ne matche pas, la syntaxe est invalide
    if not match:
        raise ValueError(f"Erreur de syntaxe : impossible de parser la ligne '{clean_line}'")

    zone1, zone2, meta_str = match.groups()

    # Construction du dictionnaire de base
    result = {
        "zone1": zone1,
        "zone2": zone2,
        "max_link_capacity": 1, # Valeur par défaut imposée par le sujet
        "color": None
    }

    # S'il y a un bloc [...] capturé, on l'analyse
    if meta_str:
        # findall retourne une liste de tuples : [('max_link_capacity', '2'), ('color', 'red')]
        tags = METADATA_PATTERN.findall(meta_str)

        for key, value in tags:
            # On injecte les valeurs brutes.
            # Note : on laisse Pydantic se charger de transformer le "2" en entier plus tard !
            result[key] = value

    return result
