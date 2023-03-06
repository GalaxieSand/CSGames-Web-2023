# CS Games 2020 Compétition Web 

## Mise en contexte

Avec les riches qui fuient la planète à la hâte et notre empressement à déménager vers les villes sous-marines, nous voulons ramasser et enregistrer tout le code que nous pouvons. Nous ne pouvons pas nous permettre de perdre toutes ces connaissances et ces progrès. Nous voulons que vous créiez un site Web sur lequel n'importe qui peut partager du code de manière anonyme étant donné qu'une partie pourrait être "empruntée" à ceux qui ont ruiné notre planète pour leur propre profit.

## État du projet

Le travail derrière ce site Web a déjà été entamé par une équipe au Mexique. Mais avec des conditions météorologiques extrêmes dans leur région, ils n'ont pas le temps de le terminer.

Une architecture microservice a été choisie par cette équipe. Ils ont choisi de transiter un `JSON Web Token` afin de valider l'identité d'un utilisateur à l'intérieur du système. Ce jeton doit être ajouté dans chaque requête vers les microservices, on doit ajouter l'en-tête `Authorization`. Ensuite, la valeur de l'en-tête est `Bearer $JSONWebToken`.

L'équipe a développé le service d'identité et de dépôt, vous devez développer le service de snippet ainsi qu'une interface web pour consulter les services.

### JSON Web Token

Le JWT est un ensemble de trois chaînes de caractères encodé en Base64, séparé par un `.`.

Le premier élément est l'en-tête du jeton. Cet en-tête contient l'identifiant de la clé publique de l'émetteur et l'algorithme utilisé pour la signature digitale du jeton.
Le second élément est les données du jeton.
Le troisième élément est la signature digitale du jeton.

Quand on utilise le mot **subject**, on fait référence au claim **sub** dans le Json Web Token. Ce qui représente l'identifiant unique de l'utilisateur auprès du serveur d'identité.

### Services fournis

Ils ont déjà implémenté deux pièces maîtresses pour le `back-end` du site web. Ces deux services sont le serveur d'identité (Identity Server) et le service de dépôt (Repository Service). Ils ont aussi offert un fichier de spécification OpenAPI 3.0 pour documenter la consommation des services. Ils ont aussi ajouté un SwaggerUI qui va vous permettre de tester la consommation du service à partir d'un fureteur web.

Afin d'assurer que les dépôts ne soient pas visibles publiquement, on doit obligatoirement être authentifié pour consulter le service de dépôt.

#### Id Server

Ce service s'occupe de la gestion des identités des utilisateurs. Il rend publique sa clé afin que vous puissiez valider la signature digitale du jeton afin de vérifier qu'il est bien l'émetteur de ce jeton.

${IDSERVER_ENDPOINT}
* Appels importants :
    * GET /.well-known/openid-configuration
      * Retourne la configuration OpenId Connect du serveur
    * GET /.well-known/openid-configuration/jwks
      * Retourne la liste des clés publiques du serveur
    * POST /connect/token
      * En utilisant `grant_type=client_credentials`, on obtient un JWT de compte de service.
      * Avec `grant_type=password` et en ajoutant `username` et `password`, on obtient un JWT d'utilisateur.
    * POST /user/create
      * Créer un nouvel utilisateur

[Voir Swagger UI](${IDSERVER_ENDPOINT}/swagger)

#### Repository Service

Ce service permet de consulter les dépôts de code. Ce service nécessite l'utilisation d'un JWT émis par Id Server afin de consommer les données.

${REPOAPI_ENDPOINT}
* Appels importants :
    * GET /repositories
      * Liste des dépôts
    * GET /repositories/{id}
      * Information d'un dépôt
    * GET /repositories/{id}/commits
      * Historique d'un dépôt
    * GET /repositories/{id}/blob/commits
      * Historique d'un fichier
    * GET /repositories/{id}/tree
      * Arborescence du dépôt
    * GET /repositories/{id}/blob
      * Récupérer un fichier du dépôt

[Voir Swagger UI](${REPOAPI_ENDPOINT}/swagger)

### Service à implémenter

#### Snippet Service

Les spécifications de ce service ont déjà été rédigées avec un swagger OpenAPI 3.0. 
Vous devez implémenter les appels à partir du swagger.

* Fichier YAML : [Snippet Service Swagger YAML](/snippets_service.yaml)

* Interface graphique présentant le YAML : [Snippet Service Swagger](/snippetsspec.html)

### Contrainte(s)

#### Technologie

Vous pouvez utiliser le langage que vous voulez. La seule contrainte est que votre application soit multiplateforme. Votre application doit être compatible avec Linux.

#### Architecture

Vous devez implémenté un front-end ainsi qu'un service back-end. Vous pouvez combiner le front-end avec le snippet service afin qu'ils vivent ensemble.

### Tâches à accomplir

#### Front-End

 * Authentification [Id Server]
    - Implémenter un formulaire pour s'authentifier. Ensuite, récupération d'un JWT avec l'appel POST /connect/token. Ce JWT pourra être utilisé pour consommer les autres services. [20 pts]
    - Gérer les erreurs d'authentification. (Bad Request de l'appel) [10 pt]
    - Implémenter un formulaire pour la création d'un nouveau compte, en utilisant l'appel POST /user/create. [20 pts]
    - Gérer les erreurs de création d'un compte. (Bad Request de l'appel) [10 pt]
    - Déconnexion de la session [20 pt]

    * Ne vous préoccupez pas de l'expiration du JWT, ils ont une durée de vie de 3 heures.

 * Liste des dépôts [Repository Service]
    - Afficher la liste des dépôts de code. Afficher le nom du projet, la licence et la description. (GET /repositories) [20 pts]
    - Implémenter la pagination pour parcourir les résultats. (paramètres skip et limit de GET /repositories et le champ totalMatches de la réponse) [20 pts]
    - Offrir la possibilité de filtrer les dépôts par nom. (paramètres filter de GET /repositories) [20 pts]

 * Page d'un projet [Repository Service]
    - En cliquant sur un dépot de liste, afficher la page du projet. (GET /repositories/<repository_id>) [20 pts]
    - Afficher les topics, langages, description et licence du projet. [20 pts]
    - Afficher le dernier commit sur master, incluant l'auteur et le message du commit. (GET /repositories/<repository_id>/commits?limit=1) [20 pts]
    - Afficher l'arborescence git du projet. (GET /repositories/<repository_id>/tree) [30 pts]
    - Afficher un dropdown avec la listes des branches et tags du dépôts. [20 pts]
    - Appliquer la sélection de la branche ou tag sur l'arborescence git du projet. (paramètre branch de GET /repositories/<repository_id>/tree) [20 pts]
    - Appliquer la sélection de la branche ou tag sur l'affichage du dernier commit. (GET /repositories/<repository_id>/commits) [20 pts]
    - En cliquant sur un ficher dans l'arborescence, afficher une section qui montre des informations sur ce fichier.
      - Les 25 derniers commits qui modifient ce fichier (paramètre filepath de GET /repositories/<repository_id>/blob/commits). [20 pts]
      - Permettre à l'utilisateur de télécharger le fichier sur son poste (paramètre filepath de GET /repositories/<repository_id>/blob). [20 pts]
      - Supporter la sélection de la branche ou du tag sur fichier (paramètre branch sur les deux appels précédents) [20 pts]

 * Historique des commits d'un projet [Repository Service]
    - Créer une page ou une section pour consulter les 25 derniers commits d'un projet, sur master (GET /repositories/<repository_id>/commits) [20 pts]
    - Supporter la pagination pour aller au-delà des 25 derniers commits. [20 pts]
    - Permettre à l'utilisateur de consulter l'historique d'une branche spécifique. [20 pts]

 * Liste des auteurs [Repository Service]
    - Afficher la liste des auteurs (GET /authors) [20 pts]
    - Supporter la pagination pour parcourir les auteurs [20 pts]
    - Quand on clique sur un auteur, afficher une section avec la liste de ses dépôts (GET /authors/<author_id>/repositories) [20 pts]
    - Quand on clique sur un dépôt, rediriger vers la page du projet [10 pt]
   
 * Publier un snippet [Snippets Service]
    - Permettre de publier un snippet de code. (POST /snippets) [20 pts]
    - Afficher un message d'erreur si la publication n'a pas fonctionné. [10 pt]
 
 * Parcourir les snippets [Snippets Service]
    - Afficher les derniers snippets. (GET /snippets) [20 pts]
    - Afficher le contenu du snippet quand on clique dessus [20 pt]
        - Appliquer la coloration syntaxique [70 pts]
    - Supporter la pagination. (GET /snippets?limit=x&skip=y) [20 pts]
    - Filtrer par mot-clé. (GET /snippets?keywords=x;y;..n) [20 pts]
        - Suggérer les mots-clés. (GET /keywords) [50 pts]
    - Afficher seulement mes snippets (GET /snippets?mine=true) [20 pts]
    - Permettre de supprimer un de ses snippets. (DELETE /snippets/<snippet_id>) [20 pts]
  
 * Style
   - Appliquer des feuilles de style sur l'ensemble du front-end , est-ce que c'est beau ?! [70 pts]

#### Back-End

  ##### Snippets Service

  * Protection par Json Web Token
    - Tous les appels de ce service doivent être protégés.
    - Le code de retour doit être 401 pour un appel sans JWT.

  * Poster un snippet, POST /snippets/create
    - Retourner une 401 si aucun JWT n’est présent dans la requête. [10 pt]
    - Un JWT d'utilisateur doit être utilisé (role=User), sinon retourner une erreur 403. [10 pt]
    - Retourner le code 201 (Created) avec l'identifiant du nouveau snippet créé. [20 pts]
    - Retourner une 400, si le champ title et/ou content sont manquants. [20 pt]
    - Supporter la sauvegarde des keywords fournis lors de la création. [20 pts]

  * Parcourir les snippets, GET /snippets
    - Retourner une 401 si aucun JWT est présent dans la requête. [10 pt]
    - Respecter le format de retour. [20 pts]
    - Supporter le paramètre title, pour filtrer par titre si la chaîne est contenue dans le titre. [20 pts]
    - Supporter le paramètre keywords, pour filtrer selon les mots clés associés. [20 pts]
        - Supporter plusieurs mots clés, séparé par ';'. [20 pts]
    - Implémenter la pagination avec les paramètres skip et limit. [20 pts]
    - Implémenter le paramètre mine, qui liste seulement les snippets de l'utilisateur courant, selon le **subject** qui est présent dans le JWT. [20 pts]
    - Ordonner les snippets par ordre décroissant sur le champ `created`. [10 pt]

  * Récupérer un snippet par identifiant, GET /snippets/<snippet_id>
    - Retourner une 401 si aucun JWT est présent dans la requête. [10 pt]
    - Respecter le format de retour. [20 pts]
    - Retourner une 404 si le snippet n'existe pas. [20 pts]

  * Supprimer un snippet, DELETE /snippets/<snippet_id>
    - Retourner une 401 si aucun JWT n’est présent dans la requête. [10 pt]
    - Retourner une 204 si l'appel a bien fonctionné. [10 pt]
    - Les snippets qui peuvent être supprimés sont seulement ceux postés par le même utilisateur. En utilisant le champ **subject** dans le JWT. [20 pt]
    - Si l'appel n'est pas valide, retourner une 400. [10 pt]

  * Les keywords existant, GET /keywords
    - Retourner une 401 si aucun JWT n’est présent dans la requête. [10 pt]
    - Retourner la liste des keywords disponible. [10 pts]

#### Artéfact
  * Fournir un run<i></i>.sh ou Dockerfile [20 pts]
  * Fournir un readme avec les informations nécessaires pour rouler la solution. [20 pts]

### Lien(s) utile(s)
* [OpenAPI 3.0 Specs](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md)

* [JWT Decoding](https://jwt.ms)

* [Json Web Token RFC](https://tools.ietf.org/html/rfc7519)
