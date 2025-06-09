# Exemple de Réponse JSON Attendue

Après les modifications apportées au système, l'IA devrait maintenant répondre au format JSON spécifié dans le guide de structure.

## Avant (Format Texte)

**Question :** "Montre-moi la liste des produits disponibles"

**Ancienne réponse :**
```
Voici la liste des produits disponibles dans notre catalogue :

## Smartphones
- iPhone 15 Pro - 1199€
- Samsung Galaxy S24 - 899€

## Ordinateurs
- MacBook Pro M3 - 2499€
- Dell XPS 13 - 1299€

Tous ces produits sont disponibles avec livraison gratuite.
```

## Après (Format JSON)

**Question :** "Montre-moi la liste des produits disponibles"

**Nouvelle réponse attendue :**
```json
{
  "template": "centered",
  "components": [
    {
      "type": "Heading",
      "props": {
        "level": 1,
        "children": "Nos Produits Disponibles",
        "className": "text-center mb-8 text-3xl font-bold"
      }
    },
    {
      "type": "Grid",
      "props": {
        "cols": 2,
        "gap": 6,
        "className": "mt-8",
        "children": [
          {
            "type": "ProductCard",
            "props": {
              "title": "iPhone 15 Pro",
              "price": "1199€",
              "description": "Le dernier smartphone Apple avec puce A17 Pro",
              "image": "/images/iphone15pro.jpg",
              "category": "Smartphones"
            }
          },
          {
            "type": "ProductCard",
            "props": {
              "title": "Samsung Galaxy S24",
              "price": "899€",
              "description": "Smartphone Android haut de gamme",
              "image": "/images/galaxys24.jpg",
              "category": "Smartphones"
            }
          },
          {
            "type": "ProductCard",
            "props": {
              "title": "MacBook Pro M3",
              "price": "2499€",
              "description": "Ordinateur portable professionnel Apple",
              "image": "/images/macbookpro.jpg",
              "category": "Ordinateurs"
            }
          },
          {
            "type": "ProductCard",
            "props": {
              "title": "Dell XPS 13",
              "price": "1299€",
              "description": "Ultrabook Windows premium",
              "image": "/images/dellxps13.jpg",
              "category": "Ordinateurs"
            }
          }
        ]
      }
    },
    {
      "type": "Text",
      "props": {
        "children": "Livraison gratuite sur tous nos produits",
        "className": "text-center mt-6 text-green-600 font-semibold"
      }
    }
  ],
  "templateProps": {
    "maxWidth": "lg",
    "backgroundColor": "bg-gray-50",
    "className": "py-8"
  }
}
```

## Avantages du Nouveau Format

1. **Structure Standardisée** : Toutes les réponses suivent le même format JSON
2. **Rendu Dynamique** : Le JSON peut être directement utilisé pour générer l'interface
3. **Composants Réutilisables** : Utilisation de composants prédéfinis (ProductCard, Grid, etc.)
4. **Styling Cohérent** : Classes Tailwind CSS pour un design uniforme
5. **Flexibilité** : Différents templates selon le type de contenu

## Types de Réponses Possibles

### Page Simple
- Template : `"centered"`
- Composants : `Heading`, `Text`, `Button`

### Liste de Produits
- Template : `"centered"` ou `"grid"`
- Composants : `Grid`, `ProductCard`

### Tableau de Bord
- Template : `"dashboard"`
- Composants : `Navigation`, `Card`, `Chart`

### Page d'Atterrissage
- Template : `"landing"`
- Sections : `navbar`, `hero`, `features`, `footer`