# Trourte
Documentation du Langage "Tourte"

Cette documentation couvre les fonctionnalités principales du langage. Toute précision non mentionnée est soit implicitement logique, soit mènera à une erreur lors de l'exécution.

La gestion des erreurs inclut l'indication de la ligne, du type d'erreur et de la valeur en cause.
1. Les Fondamentaux

    STR : ""

        Description : Représente une chaîne de caractères (texte).

        Exemple : print("Bonjour le monde"); -> "Bonjour le monde"

    int : 1, 2, 3, 0...

        Description : Représente un nombre entier.

        Exemple : print(42); -> 42

    float : 1.2, 3.14, 0.5...

        Description : Représente un nombre décimal (à virgule).

        Exemple : print(3.14); -> 3.14

    Affectation : =

        Description : Permet d'attribuer une valeur à une variable.

        Exemple : maVariable = 10; monTexte = "Salut";

    Print : print()

        Description : Affiche le contenu passé en argument à l'écran.

        Exemple : print("Ceci est un test"); -> "Ceci est un test"

    Liste : []

        Description : Crée une collection ordonnée de valeurs, accessibles par leur index (commençant à 0).

        Exemple : maListe = ["pomme", 123, 4.5]; print(maListe[0]); -> "pomme"

    Virgule : ,

        Description : Utilisée pour séparer des éléments (par exemple, des arguments dans print, ou des éléments dans une liste).

        Exemple : print("Un", "Deux", "Trois"); -> "Un Deux Trois"

    Point-virgule : ;

        Description : Indique la fin d'une instruction.

        Exemple : a = 1; b = 2; print(a + b);

    Dictionnaire : ||clé:valeur||

        Description : Collection de paires clé-valeur, où chaque clé est unique.

        Exemple : monDico = ||"nom":"Alice", "age":30||; print(monDico["nom"]); -> "Alice"

    Input : input()

        Description : Permet de demander une saisie à l'utilisateur. La valeur retournée est toujours une STR.

        Exemple : reponse = input("Entrez votre nom : "); nombre = int(input("Entrez un nombre : "));

    Commentaire : #

        Description : Tout ce qui suit # sur la même ligne est ignoré par l'interpréteur.

        Exemple : # Ceci est un commentaire utile

    Fonction : func nom_fonction(param1, param2) { ... };

        Description : Définit un bloc de code réutilisable qui peut prendre des paramètres.

        Exemple : func addition(a, b) { print(a + b); }; addition(5, 3); -> 8

    Portée des Variables :

        Les variables déclarées à l'intérieur des blocs if et while sont accessibles depuis l'extérieur de ces blocs.

    Variables non définies :

        Si une variable est utilisée sans avoir été préalablement définie, sa valeur sera none.

        Exemple : while (maVariableNonDefinie != 0) { print(maVariableNonDefinie); }; -> maVariableNonDefinie sera none lors de la première évaluation.

        Comparaison avec none : Les comparaisons d'égalité (==) et d'inégalité (!=) avec none fonctionnent normalement (ex: none == 0 est False). Cependant, l'utilisation d'opérateurs d'inégalité (>, <, >=, <=) avec none entraînera une erreur.

    Import de Fichier : import "nom du fichier"

        Description : Permet d'inclure et d'utiliser du code défini dans d'autres fichiers, rendant les fonctions définies à l'intérieur accessibles.

        Exemple : import "bibliotheque_math";

        Note : Les programmes "Tourte" compilés incluent toutes leurs dépendances dans un seul fichier exécutable.

2. Opérations Arithmétiques Simples

    Addition : +

        STR + STR : Concaténation (jointure de chaînes).

            Exemple : "Bonjour" + "Monde" -> "BonjourMonde"

        int/float + int/float : Addition numérique.

            Exemple : 1 + 2.5 -> 3.5

    Soustraction : -

        int/float - int/float : Soustraction numérique.

            Exemple : 10 - 3.0 -> 7.0

3. Opérations Arithmétiques Fortes

    Multiplication : *

        STR * int : Répétition de la chaîne.

            Exemple : "abc" * 3 -> "abcabcabc"

        int/float * int/float : Multiplication numérique.

            Exemple : 2.5 * 4 -> 10.0

    Puissance : **

        Description : Élève un nombre à une certaine puissance (base ** exposant).

        Exemple : 3 ** 2 (3 au carré) -> 9

    Division : /

        Description : Division numérique. Le résultat est toujours un float.

        Exemple : 7 / 2 -> 3.5

    Division Euclidienne : //

        Description : Division entière. Retourne la partie entière du quotient.

        Exemple : 7 // 2 -> 3

    Racine n-ième : ///

        Description : Calcule la racine n-ième d'un nombre (nombre /// n).

        Exemple : 27 /// 3 (racine cubique de 27) -> 3.0

        Exemple : 16 /// 2 (racine carrée de 16) -> 4.0

4. Tests Conditionnels et Boucles

    Opérateurs de Comparaison :

        == (égal à), != (différent de)

        > (supérieur à), < (inférieur à)

        >= (supérieur ou égal à), <= (inférieur ou égal à)

        and (ET logique), or (OU logique), not (NON logique)

        in (appartient à), not in (n'appartient pas à)

        Exemple : (age > 18) and (ville == "Paris")

    Condition IF : if (condition) { ... };

        Description : Exécute le bloc de code si la condition est True.

        Exemple : if (temperature > 25) { print("Il fait chaud"); };

    Condition ELIF : elif (condition) { ... };

        Description : Exécute le bloc de code si la condition if précédente était False ET cette condition est True.

        Exemple : elif (temperature > 15) { print("Il fait doux"); };

    Condition ELSE : else { ... };

        Description : Exécute le bloc de code si aucune des conditions if/elif précédentes n'était True.

        Exemple : else { print("Il fait froid"); };

    Boucle WHILE : while (condition) { ... };

        Description : Répète le bloc de code tant que la condition reste True.

        Exemple : compteur = 0; while (compteur < 5) { print(compteur); compteur = compteur + 1; }; -> 0;1;2;3;4

5. Exemple de Code Complet

# Définition d'une fonction pour saluer
func saluer(nom) {
    print("Bonjour, " + nom + " !");
};

# Demander le nom de l'utilisateur
nom_utilisateur = input("Quel est votre nom ? ");

# Appel de la fonction saluer
saluer(nom_utilisateur);

# Demander un nombre et effectuer des opérations
nombre_str = input("Entrez un nombre entier : ");
nombre = int(nombre_str); # Conversion en entier

print("Votre nombre est :", nombre);

# Opérations arithmétiques
resultat_addition = nombre + 10;
resultat_multiplication = nombre * 2;
resultat_puissance = nombre ** 3;
resultat_racine_carree = nombre /// 2; # Racine carrée

print("Nombre + 10 :", resultat_addition);
print("Nombre * 2 :", resultat_multiplication);
print("Nombre puissance 3 :", resultat_puissance);
print("Racine carrée du nombre :", resultat_racine_carree);

# Utilisation d'une liste
ma_liste_de_nombres = [10, 20, 30, 40, 50];
print("Premier élément de la liste :", ma_liste_de_nombres[0]);

# Vérifier si le nombre est dans la liste
if (nombre in ma_liste_de_nombres) {
    print("Votre nombre est dans la liste !");
} elif (nombre > 50) {
    print("Votre nombre est grand, mais pas dans la liste.");
} else {
    print("Votre nombre n'est pas dans la liste.");
};

# Utilisation d'un dictionnaire
informations_utilisateur = ||"nom":nom_utilisateur, "age":nombre||;
print("Informations via dictionnaire : Nom =", informations_utilisateur["nom"], ", Âge =", informations_utilisateur["age"]);

# Boucle while pour compter jusqu'au nombre entré
compteur_boucle = 0;
print("Comptage jusqu'à votre nombre :");
while (compteur_boucle <= nombre) {
    print(compteur_boucle);
    compteur_boucle = compteur_boucle + 1;
};

print("Fin du programme.");

