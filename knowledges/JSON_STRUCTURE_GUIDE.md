# Guide de Structure JSON pour le Système de Rendu de Composants

## Vue d'ensemble

Ce document décrit la structure JSON requise pour générer des interfaces utilisateur dynamiques avec notre système de rendu de composants. Le JSON définit quels composants utiliser, leurs propriétés, et comment ils sont organisés dans un template.

## Structure de Base

```json
{
  "template": "nom_du_template",
  "components": [
    {
      "type": "TypeDeComposant",
      "props": {
        "propriété1": "valeur1",
        "propriété2": "valeur2",
        "children": [...]
      }
    }
  ],
  "templateProps": {
    "maxWidth": "lg",
    "backgroundColor": "bg-white",
    "className": "classes-css-additionnelles"
  }
}
```

## Propriétés Principales

### 1. `template` (obligatoire)
Définit le layout principal de la page.

**Valeurs possibles :**
- `"base"` - Template de base simple
- `"centered"` - Template centré avec largeur maximale
- `"grid"` - Template en grille
- `"dashboard"` - Template pour tableaux de bord
- `"landing"` - Template pour pages d'atterrissage

### 2. `components` (obligatoire)
Tableau contenant tous les composants à rendre.

**Structure d'un composant :**
```json
{
  "type": "NomDuComposant",
  "props": {
    // Propriétés spécifiques au composant
  }
}
```

### 3. `templateProps` (optionnel)
Propriétés appliquées au template principal.

**Propriétés communes :**
- `maxWidth`: `"sm"`, `"md"`, `"lg"`, `"xl"`, `"2xl"`, `"4xl"`, `"6xl"`, `"full"`
- `backgroundColor`: Classes Tailwind CSS (ex: `"bg-white"`, `"bg-gray-50"`)
- `className`: Classes CSS additionnelles

## Gestion des Enfants (Children)

Les composants peuvent contenir d'autres composants via la propriété `children`.

### Types de children supportés :

1. **Texte simple :**
```json
{
  "type": "Button",
  "props": {
    "children": "Cliquez ici"
  }
}
```

2. **Composant unique :**
```json
{
  "type": "Card",
  "props": {
    "children": {
      "type": "Text",
      "props": {
        "children": "Contenu de la carte"
      }
    }
  }
}
```

3. **Tableau de composants :**
```json
{
  "type": "Grid",
  "props": {
    "cols": 3,
    "children": [
      {
        "type": "Card",
        "props": { "children": "Carte 1" }
      },
      {
        "type": "Card",
        "props": { "children": "Carte 2" }
      }
    ]
  }
}
```

## Sections de Template

Certains templates supportent des sections spécifiques. Utilisez la propriété `section` pour organiser les composants :

```json
{
  "type": "Navigation",
  "props": {
    "items": ["Accueil", "Services", "Contact"],
    "section": "navbar"
  }
}
```

**Sections disponibles selon le template :**

### Template `landing` :
- `navbar` - Barre de navigation
- `hero` - Section héro
- `features` - Section des fonctionnalités
- `footer` - Pied de page

### Template `dashboard` :
- `sidebar` - Barre latérale
- `header` - En-tête
- `main` - Contenu principal
- `footer` - Pied de page

## Classes CSS et Styling

Utilisez Tailwind CSS pour le styling :

```json
{
  "type": "Button",
  "props": {
    "children": "Mon Bouton",
    "className": "bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg"
  }
}
```

## Exemples Complets

### Exemple Simple (Page Centrée)
```json
{
  "template": "centered",
  "components": [
    {
      "type": "Heading",
      "props": {
        "level": 1,
        "children": "Bienvenue",
        "className": "text-center mb-8"
      }
    },
    {
      "type": "Text",
      "props": {
        "children": "Ceci est un exemple de page simple.",
        "className": "text-center text-gray-600"
      }
    }
  ],
  "templateProps": {
    "maxWidth": "lg",
    "backgroundColor": "bg-white"
  }
}
```

### Exemple E-commerce
```json
{
  "template": "centered",
  "components": [
    {
      "type": "Heading",
      "props": {
        "level": 1,
        "children": "Notre Boutique"
      }
    },
    {
      "type": "Grid",
      "props": {
        "cols": 3,
        "gap": 6,
        "children": [
          {
            "type": "ProductCard",
            "props": {
              "title": "Produit 1",
              "price": "29,99 €",
              "description": "Description du produit",
              "image": "/images/produit1.jpg"
            }
          }
        ]
      }
    }
  ]
}
```

## Bonnes Pratiques

### 1. Organisation Hiérarchique
- Utilisez des conteneurs (`Container`, `Grid`, `Flex`) pour organiser le layout
- Groupez les éléments liés dans des `Card` ou `Container`

### 2. Responsive Design
- Utilisez les classes Tailwind responsive (`md:`, `lg:`, etc.)
- Testez sur différentes tailles d'écran

### 3. Accessibilité
- Utilisez des `Heading` avec des niveaux appropriés (h1, h2, h3...)
- Ajoutez des `alt` aux images
- Utilisez des couleurs contrastées

### 4. Performance
- Évitez l'imbrication excessive de composants
- Utilisez des `key` uniques pour les listes

### 5. Cohérence
- Utilisez un système de couleurs cohérent
- Respectez les espacements (margin, padding)
- Maintenez une hiérarchie typographique claire

## Validation

Le système valide automatiquement :
- La présence des propriétés obligatoires (`template`, `components`)
- L'existence des types de composants
- La structure des propriétés

En cas d'erreur, un message d'erreur détaillé sera affiché avec des suggestions de correction.