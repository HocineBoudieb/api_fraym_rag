# Guide des Scénarios de Réponse et Formats Adaptés

Ce document définit les différents scénarios d'interaction et leurs formats de réponse JSON correspondants pour optimiser l'expérience utilisateur selon le contexte.

## Vue d'ensemble

Au lieu d'utiliser une structure rigide de 6 composants pour toutes les réponses, le système doit adapter le format selon :
- Le type de requête utilisateur
- Le contexte métier (e-commerce, restaurant, service client)
- L'intention détectée
- Les données disponibles

## Scénarios de Réponse

### 1. Affichage de Produit Unique

**Déclencheurs :**
- Mots-clés : "détails", "spécifications", "caractéristiques", "fiche produit", "plus d'infos"
- Tags détectés : `product`, `ecommerce`
- Contexte : Un seul produit trouvé (len(found_docs) == 1)

**Format de réponse :**
```json
{
  "template": "centered",
  "components": [
    {
      "type": "Heading",
      "props": {
        "level": 1,
        "children": "[Nom du Produit]",
        "className": "text-center mb-6"
      }
    },
    {
      "type": "ProductCard",
      "props": {
        "name": "Nom du Produit",
        "price": "€XX.XX",
        "description": "Description détaillée avec spécifications",
        "image": "product-image.jpg",
        "features": ["Caractéristique 1", "Caractéristique 2"],
        "availability": "En stock",
        "shipping": "Livraison gratuite"
      }
    },
    {
      "type": "Text",
      "props": {
        "children": "Informations sur garantie et support.",
        "className": "text-center mb-4"
      }
    },
    {
      "type": "Button",
      "props": {
        "children": "Ajouter au panier",
        "color": "blue",
        "size": "lg",
        "className": "mx-auto block"
      }
    }
  ]
}
```

### 2. Affichage de Produits E-commerce (Multiples)

**Déclencheurs :**
- Mots-clés : "produit", "acheter", "prix", "catalogue", "recommandation"
- Tags détectés : `product`, `ecommerce`
- Contexte : Plusieurs produits trouvés

**Format de réponse :**
```json
{
  "template": "grid",
  "components": [
    {
      "type": "Heading",
      "props": {
        "level": 1,
        "children": "[Titre contextuel]",
        "className": "text-center mb-6"
      }
    },
    {
      "type": "Text",
      "props": {
        "children": "[Description ou question]",
        "className": "text-center text-gray-600 mb-8"
      }
    },
    {
      "type": "Grid",
      "props": {
        "cols": 3,
        "gap": 6,
        "className": "mb-8",
        "children": [
          // ProductCard components
        ]
      }
    },
    {
      "type": "Text",
      "props": {
        "children": "[Question de suivi ou CTA]",
        "className": "text-center"
      }
    }
  ],
  "templateProps": {
    "maxWidth": "6xl",
    "className": "py-8"
  }
}
```

### 3. Menu Restaurant

**Déclencheurs :**
- Mots-clés : "menu", "plat", "restaurant", "réserver", "carte"
- Tags détectés : `restaurant`, `menu`
- Contexte : Données restaurant disponibles

**Format de réponse :**
```json
{
  "template": "centered",
  "components": [
    {
      "type": "Heading",
      "props": {
        "level": 1,
        "children": "Notre Menu",
        "className": "text-center mb-6"
      }
    },
    {
      "type": "Grid",
      "props": {
        "cols": 2,
        "gap": 6,
        "children": [
          // Menu items as Cards
        ]
      }
    },
    {
      "type": "Button",
      "props": {
        "children": "Réserver une table",
        "color": "blue",
        "size": "lg",
        "className": "mt-8 mx-auto block"
      }
    }
  ]
}
```

### 4. Service Client / FAQ

**Déclencheurs :**
- Mots-clés : "aide", "problème", "retour", "livraison", "garantie"
- Tags détectés : `support`, `faq`
- Contexte : Questions de support

**Format de réponse :**
```json
{
  "template": "centered",
  "components": [
    {
      "type": "Heading",
      "props": {
        "level": 2,
        "children": "[Titre de la réponse]",
        "className": "mb-4"
      }
    },
    {
      "type": "Card",
      "props": {
        "className": "p-6 mb-6",
        "children": {
          "type": "Text",
          "props": {
            "children": "[Réponse détaillée]"
          }
        }
      }
    },
    {
      "type": "Text",
      "props": {
        "children": "Besoin d'aide supplémentaire ?",
        "className": "text-center mb-4"
      }
    },
    {
      "type": "Button",
      "props": {
        "children": "Contacter le support",
        "color": "green",
        "className": "mx-auto block"
      }
    }
  ]
}
```

### 5. Réponse Informative Simple

**Déclencheurs :**
- Questions générales
- Demandes d'information
- Pas de produits/services spécifiques

**Format de réponse :**
```json
{
  "template": "centered",
  "components": [
    {
      "type": "Heading",
      "props": {
        "level": 2,
        "children": "[Titre de la réponse]",
        "className": "mb-4"
      }
    },
    {
      "type": "Text",
      "props": {
        "children": "[Contenu de la réponse]",
        "className": "mb-6"
      }
    }
  ]
}
```

### 6. Page d'Accueil / Landing

**Déclencheurs :**
- Première visite
- Salutations générales
- Demandes d'orientation

**Format de réponse :**
```json
{
  "template": "landing",
  "components": [
    {
      "type": "Heading",
      "props": {
        "level": 1,
        "children": "Bienvenue !",
        "className": "text-center text-4xl mb-6"
      }
    },
    {
      "type": "Text",
      "props": {
        "children": "Comment puis-je vous aider aujourd'hui ?",
        "className": "text-center text-xl mb-8"
      }
    },
    {
      "type": "Grid",
      "props": {
        "cols": 3,
        "gap": 6,
        "children": [
          // Action cards
        ]
      }
    }
  ]
}
```

### 7. Comparaison de Produits

**Déclencheurs :**
- Mots-clés : "comparer", "différence", "vs", "mieux"
- Plusieurs produits mentionnés

**Format de réponse :**
```json
{
  "template": "grid",
  "components": [
    {
      "type": "Heading",
      "props": {
        "level": 2,
        "children": "Comparaison de produits",
        "className": "text-center mb-6"
      }
    },
    {
      "type": "Grid",
      "props": {
        "cols": 2,
        "gap": 6,
        "children": [
          // Comparison cards
        ]
      }
    },
    {
      "type": "Text",
      "props": {
        "children": "[Recommandation basée sur la comparaison]",
        "className": "text-center mt-6"
      }
    }
  ]
}
```

## Logique de Sélection des Scénarios

### Algorithme de Détection

1. **Analyse des mots-clés** dans la requête utilisateur
2. **Vérification des tags** dans les documents trouvés
3. **Évaluation du contexte** (historique de conversation)
4. **Nombre et type de résultats** trouvés
5. **Intention utilisateur** détectée

### Priorités de Sélection

1. **Produits E-commerce** : Si tags `product` ET mots-clés commerce
2. **Restaurant** : Si tags `restaurant` OU mots-clés restauration
3. **Support** : Si mots-clés d'aide OU tags `support`
4. **Comparaison** : Si mots-clés de comparaison ET plusieurs produits
5. **Landing** : Si salutation OU première interaction
6. **Informatif** : Par défaut

### Règles de Fallback

- Si aucun scénario spécifique détecté → Format informatif simple
- Si erreur dans la génération → Format minimal sécurisé
- Si pas de données → Message d'orientation vers les bonnes ressources

## Personnalisation par Contexte

### E-commerce
- Accent sur les produits et l'achat
- CTAs vers le panier/commande
- Informations prix et disponibilité

### Restaurant
- Accent sur l'expérience et la réservation
- Informations horaires et contact
- Mise en avant des spécialités

### Service Client
- Accent sur la résolution de problèmes
- Informations de contact prioritaires
- Guides étape par étape

## Métriques et Optimisation

### Indicateurs à Suivre
- Taux de satisfaction par scénario
- Temps de résolution des requêtes
- Taux de conversion (achat, réservation, etc.)
- Taux de rebond par format

### Tests A/B Recommandés
- Nombre optimal de composants par scénario
- Ordre des éléments
- Formulations des CTAs
- Couleurs et styles visuels