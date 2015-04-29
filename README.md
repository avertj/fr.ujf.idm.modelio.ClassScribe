# fr.ujf.idm.modelio.ClassScribe

Ce projet tente de répondre au sujet présenté [ici](http://modelioscribes.readthedocs.org/en/latest/ClassScribe.html).

# Collaborateurs

Groupe 235

* Julien AVERT (JAT)
* Mohammed MENBER (MMR)

# Travail effectué

## Export

Toutes les fonctions d'export qui sont présentes dans les specifications fonctionnent

Néanmoins, l'export de certaines choses peut faire planter le script.
* les classes d'association (leur représentation n'est pas specifiée dans le sujet)
* les association Naire  (leur représentation n'est pas specifiée dans le sujet)

De plus, les roles n'ayant pas de nom s'en voient un attribué par défaut : "unnamed"

Une remarque : Le type de retour des operations n'apparait nul part dans les specs je l'ai donc ajouté de la manière suivante :

```
<DefineOperation> ::= <Stereotype>* <Abstract?> <Derived>? <Visibility>? <Name> "() : " <TypeName>
```

Exemple de sortie :

```
e EnumerationE
    el1
    el2
    el3

ClassA < ClassD
    + someBs : ClassB [*] inv someAs [*]
    + theC : ClassC  inv theA [0..1]

ClassB
    + someAs : ClassA [*] inv someBs [*]

ClassC
    + theA : ClassA [0..1] inv theC 
    + classC : ClassC [0..1]

ClassD
    + attEnumeration : EnumerationE
```
```
ClassA
    S: The ClassA is just a fake Class.
    D: This is the description of the ClassA. By contrast to the summary, which is
    D: usually short (typically a one or very few sentences), the description can be a
    D: longer piece of text. By contrast to "rich notes" that are supported by Modelio,
    D: "standard" notes can only contains text with no formatting.
    + a : string 
    + op()
        p1 : string
        p2 : string
```
## Import

Pour l'instant aucun import n'est possible

Le dialogue de selection de fichier s'ouvre et il est possible de choisir un fichier mais cliquer sur ok provoquera une erreur que je n'ai pas su résoudre

```
TypeError: self invalid - must be a Java subclass [self=<TextualTree object at 0x1d>] in <script> at line number 90
Traceback (most recent call last):
  File "<script>", line 90, in <module>
  File "<script>", line 16, in import_tree
  File "<script>", line 298, in getTextualTree
  File "<script>", line 165, in __init__
TypeError: self invalid - must be a Java subclass [self=<TextualTree object at 0x1d>]
```

Nous avions commencé l'import (enums dans un premier temps) et il fonctionnait correctement mais cette erreur s'est déclarée du jour au lendemain sans raison apparente (nous n'avions touché à aucun code evoqué dans l'erreur) et sans que nous puissions la résoudre (malgré de longues heures de recherche)...
